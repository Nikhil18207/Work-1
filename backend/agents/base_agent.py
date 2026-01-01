"""
Base Agent - Common functionality for all microagents

Provides:
- RAG context retrieval with confidence scoring
- LLM integration with strict grounding
- Data access utilities
- Standard prompt building
"""

import sys
from pathlib import Path
from typing import Dict, Any, List, Optional
from abc import ABC, abstractmethod

root_path = Path(__file__).parent.parent.parent
if str(root_path) not in sys.path:
    sys.path.insert(0, str(root_path))


class BaseAgent(ABC):
    """
    Abstract base class for all microagents.

    Provides common functionality:
    - RAG context retrieval with confidence scoring
    - LLM generation with strict grounding
    - Fallback to template-based output
    - Source citation tracking

    ZERO HALLUCINATION POLICY:
    - All agents must cite sources
    - Low confidence triggers template fallback
    - LLM only uses provided data + RAG context
    """

    # Minimum confidence threshold for using LLM (vs template fallback)
    DEFAULT_CONFIDENCE_THRESHOLD = 0.4

    def __init__(
        self,
        llm_engine=None,
        vector_store=None,
        enable_llm: bool = True,
        enable_rag: bool = True,
        confidence_threshold: float = None
    ):
        """
        Initialize base agent with optional LLM and RAG capabilities.

        Args:
            llm_engine: LLMEngine instance for generation
            vector_store: FAISSVectorStore instance for RAG
            enable_llm: Enable LLM-powered generation
            enable_rag: Enable RAG context retrieval
            confidence_threshold: Minimum RAG confidence for LLM use
        """
        self.llm_engine = llm_engine
        self.vector_store = vector_store
        self.enable_llm = enable_llm and llm_engine is not None
        self.enable_rag = enable_rag and vector_store is not None
        self.confidence_threshold = confidence_threshold or self.DEFAULT_CONFIDENCE_THRESHOLD

        # Track sources used in generation for traceability
        self._sources_used = []

    @property
    @abstractmethod
    def agent_name(self) -> str:
        """Return the agent's name for logging"""
        pass

    @abstractmethod
    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the agent's primary task.

        Args:
            context: Dictionary containing all data needed for the task

        Returns:
            Dictionary with agent output and metadata
        """
        pass

    def get_rag_context(
        self,
        query: str,
        category: Optional[str] = None,
        k: int = 5
    ) -> Dict[str, Any]:
        """
        Retrieve RAG context with full metadata for traceability.

        Returns:
            Dict with:
            - context: Formatted text for LLM prompt
            - sources: List of source documents
            - confidence: Score (0-1)
            - has_strong_context: Boolean for fallback decision
        """
        if not self.enable_rag or not self.vector_store:
            return {
                'context': '',
                'sources': [],
                'confidence': 0.0,
                'has_strong_context': False,
                'source_citations': ''
            }

        try:
            results = self.vector_store.search(query=query, k=k)

            if not results:
                return {
                    'context': '',
                    'sources': [],
                    'confidence': 0.0,
                    'has_strong_context': False,
                    'source_citations': ''
                }

            # Format context with numbered citations
            context_parts = []
            sources = []
            citations = []

            for i, result in enumerate(results, 1):
                metadata = result.get('metadata', {})
                source_file = metadata.get('file_name', metadata.get('source', 'knowledge_base'))
                source_category = result.get('category', metadata.get('category', 'general'))
                content = result.get('content', '')
                score = result.get('score', 0.5)

                citation_id = f"[SOURCE-{i}]"
                context_parts.append(f"{citation_id} ({source_file}):\n{content}")

                sources.append({
                    'citation_id': citation_id,
                    'file_name': source_file,
                    'category': source_category,
                    'relevance_score': score,
                    'excerpt': content[:200] + '...' if len(content) > 200 else content
                })

                citations.append(f"{citation_id}: {source_file}")

            # Calculate confidence score
            avg_score = sum(r.get('score', 0.5) for r in results) / len(results)
            confidence = max(0, min(1, avg_score))

            # Strong context: >= threshold confidence with >= 2 relevant docs
            has_strong_context = confidence >= self.confidence_threshold and len(results) >= 2

            # Track sources for this generation
            self._sources_used = sources

            return {
                'context': "\n\n".join(context_parts),
                'sources': sources,
                'confidence': round(confidence, 2),
                'has_strong_context': has_strong_context,
                'source_citations': "\n".join(citations)
            }

        except Exception as e:
            print(f"[WARN] {self.agent_name} RAG retrieval failed: {e}")
            return {
                'context': '',
                'sources': [],
                'confidence': 0.0,
                'has_strong_context': False,
                'source_citations': ''
            }

    def generate_with_llm(
        self,
        data_section: str,
        task_instruction: str,
        rag_query: Optional[str] = None,
        fallback_generator: callable = None
    ) -> Dict[str, Any]:
        """
        Generate content using LLM with strict grounding.

        Args:
            data_section: Primary data for the prompt
            task_instruction: What the LLM should generate
            rag_query: Optional query for RAG context
            fallback_generator: Function to call if LLM/RAG fails

        Returns:
            Dict with:
            - content: Generated text
            - method: 'llm' or 'template'
            - sources: List of sources used
            - confidence: RAG confidence score
        """
        # Attempt RAG retrieval if query provided
        rag_result = None
        if rag_query and self.enable_rag:
            rag_result = self.get_rag_context(rag_query)

        # Check if we should use LLM or fallback
        use_llm = (
            self.enable_llm and
            self.llm_engine is not None and
            (rag_result is None or rag_result.get('has_strong_context', False))
        )

        if not use_llm:
            # Use fallback template
            if fallback_generator:
                content = fallback_generator()
                return {
                    'content': content,
                    'method': 'template',
                    'sources': [],
                    'confidence': 0.0,
                    'reason': 'LLM disabled or low RAG confidence'
                }
            else:
                return {
                    'content': '',
                    'method': 'template',
                    'sources': [],
                    'confidence': 0.0,
                    'reason': 'No fallback provided'
                }

        try:
            # Build strictly grounded prompt
            prompt = self._build_grounded_prompt(data_section, rag_result, task_instruction)

            # Generate with LLM
            response = self.llm_engine._generate_openai(prompt)

            # Check for refusal
            if self._is_llm_refusal(response):
                if fallback_generator:
                    return {
                        'content': fallback_generator(),
                        'method': 'template',
                        'sources': [],
                        'confidence': 0.0,
                        'reason': 'LLM refused to generate'
                    }

            # Add sources footer
            sources = rag_result.get('sources', []) if rag_result else []
            if sources:
                sources_footer = "\n\n---\nSources: " + ", ".join(
                    s['file_name'] for s in sources[:3]
                )
                response += sources_footer

            return {
                'content': response,
                'method': 'llm',
                'sources': sources,
                'confidence': rag_result.get('confidence', 0.0) if rag_result else 0.0
            }

        except Exception as e:
            print(f"[WARN] {self.agent_name} LLM generation failed: {e}")
            if fallback_generator:
                return {
                    'content': fallback_generator(),
                    'method': 'template',
                    'sources': [],
                    'confidence': 0.0,
                    'reason': f'LLM error: {str(e)}'
                }
            return {
                'content': '',
                'method': 'error',
                'sources': [],
                'confidence': 0.0,
                'reason': f'LLM error: {str(e)}'
            }

    def _build_grounded_prompt(
        self,
        data_section: str,
        rag_result: Optional[Dict[str, Any]],
        task_instruction: str
    ) -> str:
        """Build a prompt with strict grounding rules."""
        grounding_rules = """
STRICT GROUNDING RULES (MUST FOLLOW):
1. You may ONLY use facts from the DATA SECTION and KNOWLEDGE BASE CONTEXT below
2. When using information from the knowledge base, cite it as [SOURCE-N]
3. NEVER invent or guess statistics, percentages, market trends, or industry facts
4. If specific information is not available, use phrases like "Based on the provided data..."
5. All numerical claims MUST come from the DATA SECTION
6. Do NOT make claims about market conditions unless explicitly stated in KNOWLEDGE BASE
7. Focus on ANALYSIS and SYNTHESIS of provided information, not new information
"""

        if rag_result and rag_result.get('has_strong_context'):
            knowledge_section = f"""
KNOWLEDGE BASE CONTEXT (cite as [SOURCE-N]):
{rag_result['context']}

AVAILABLE SOURCES:
{rag_result['source_citations']}
"""
        else:
            knowledge_section = """
KNOWLEDGE BASE CONTEXT:
[No highly relevant documents found in knowledge base]
Focus ONLY on analyzing the DATA SECTION below.
"""

        return f"""{grounding_rules}
{knowledge_section}

DATA SECTION (PRIMARY SOURCE - all numbers from here):
{data_section}

TASK:
{task_instruction}

REMEMBER: Cite sources. No hallucination. Only use provided information.
"""

    def _is_llm_refusal(self, response: str) -> bool:
        """Check if LLM refused to generate content."""
        if not response:
            return True

        refusal_indicators = [
            "i cannot",
            "i can't",
            "i'm unable",
            "i am unable",
            "i don't have enough information",
            "insufficient data",
            "cannot provide",
            "not enough context"
        ]

        response_lower = response.lower()[:200]
        return any(indicator in response_lower for indicator in refusal_indicators)

    def get_sources_used(self) -> List[Dict[str, Any]]:
        """Get list of sources used in last generation."""
        return self._sources_used

    def log(self, message: str, level: str = "INFO"):
        """Log a message with agent name prefix."""
        prefix = {
            "INFO": "[INFO]",
            "WARN": "[WARN]",
            "ERROR": "[ERROR]",
            "OK": "[OK]"
        }.get(level, "[INFO]")
        print(f"{prefix} {self.agent_name}: {message}")
