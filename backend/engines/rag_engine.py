"""
RAG Engine - Retrieval Augmented Generation
Combines vector search with LLM for context-aware recommendations
"""

import os
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime

# Import engines
from backend.engines.vector_store_manager import VectorStoreManager
from backend.engines.document_processor import DocumentProcessor

# LLM
try:
    from openai import OpenAI
except ImportError:
    OpenAI = None

# Gemini support disabled - using OpenAI only
# try:
#     import google.generativeai as genai
# except ImportError:
#     genai = None
genai = None


class RAGEngine:
    """
    RAG Engine for context-aware procurement recommendations
    
    Combines:
    - Vector database semantic search
    - LLM reasoning and generation
    - Procurement domain knowledge
    """
    
    def __init__(
        self,
        vector_store_manager: Optional[VectorStoreManager] = None,
        provider: str = "openai",
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        temperature: float = 0.7
    ):
        """
        Initialize RAG engine
        
        Args:
            vector_store_manager: Vector store instance
            provider: 'openai' or 'google'
            api_key: API key
            model: LLM model to use
            temperature: LLM temperature
        """
        # Vector store
        self.vector_store = vector_store_manager
        self.provider = provider.lower()
        self.temperature = temperature
        
        # LLM client setup
        if self.provider == "google":
            self.api_key = api_key or os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
            if not self.api_key:
                raise ValueError("Google API key required")
            
            if genai:
                genai.configure(api_key=self.api_key)
                self.model_name = model or "gemini-pro"
                self.client = genai.GenerativeModel(self.model_name)
            else:
                self.client = None
                print("Warning: google-generativeai not installed")
        else:
            self.api_key = api_key or os.getenv("OPENAI_API_KEY")
            if not self.api_key:
                raise ValueError("OpenAI API key required")
            
            if OpenAI:
                self.client = OpenAI(api_key=self.api_key)
                self.model_name = model or "gpt-4"
            else:
                self.client = None
                print("Warning: openai not installed")
        
        print(f" RAG Engine initialized")
        print(f"  Provider: {self.provider}")
        print(f"  Model: {self.model_name}")
        print(f"  Vector Store: {'Connected' if vector_store_manager else 'Not connected'}")
    
    def query(
        self,
        question: str,
        k: int = 5,
        category: Optional[str] = None,
        include_sources: bool = True,
        verbose: bool = False
    ) -> Dict[str, Any]:
        """
        Query RAG system with a question
        
        Args:
            question: User question
            k: Number of context documents to retrieve
            category: Filter by document category
            include_sources: Include source citations
            verbose: Print detailed process
            
        Returns:
            Response dictionary with answer and metadata
        """
        if not self.vector_store:
            return {
                'answer': "RAG system not initialized. Vector store not connected.",
                'sources': [],
                'error': 'no_vector_store'
            }
        
        if verbose:
            print(f"\n{'='*60}")
            print(f" RAG QUERY")
            print(f"{'='*60}")
            print(f"Question: {question}")
            print(f"Retrieving top {k} relevant documents...")
        
        # Step 1: Retrieve relevant context
        try:
            search_results = self.vector_store.semantic_search(
                query=question,
                k=k,
                category=category,
                verbose=verbose
            )
            
            if not search_results:
                return {
                    'answer': "I couldn't find relevant information in the knowledge base to answer this question.",
                    'sources': [],
                    'context_found': False
                }
            
            # Format context
            context = self._format_context(search_results)
            
            if verbose:
                print(f"\n Retrieved {len(search_results)} relevant documents")
                print(f"\n Context length: {len(context)} characters")
            
        except Exception as e:
            return {
                'answer': f"Error retrieving context: {str(e)}",
                'sources': [],
                'error': 'retrieval_error'
            }
        
        # Step 2: Generate answer with LLM
        try:
            if verbose:
                print(f"\n Generating answer with {self.model_name}...")
            
            answer = self._generate_answer(question, context, verbose=verbose)
            
            # Prepare response
            response = {
                'answer': answer,
                'question': question,
                'context_found': True,
                'num_sources': len(search_results),
                'model': self.model_name,
                'timestamp': datetime.now().isoformat()
            }
            
            # Add sources if requested
            if include_sources:
                response['sources'] = [
                    {
                        'rank': r['rank'],
                        'source': r['metadata'].get('file_name', 'unknown'),
                        'category': r['category'],
                        'score': r['score'],
                        'excerpt': r['content'][:200] + "..."
                    }
                    for r in search_results
                ]
            
            if verbose:
                print(f"\n Answer generated successfully")
                print(f"{'='*60}\n")
            
            return response
            
        except Exception as e:
            return {
                'answer': f"Error generating answer: {str(e)}",
                'sources': [],
                'error': 'generation_error'
            }
    
    def get_procurement_recommendation(
        self,
        scenario: str,
        context_data: Dict[str, Any],
        k: int = 5
    ) -> Dict[str, Any]:
        """
        Get procurement recommendation using RAG
        
        Args:
            scenario: Procurement scenario description
            context_data: Additional context (spend data, rules, etc.)
            k: Number of context documents
            
        Returns:
            Recommendation with sources
        """
        # Build comprehensive query
        query = self._build_procurement_query(scenario, context_data)
        
        # Retrieve context
        search_results = self.vector_store.semantic_search(
            query=query,
            k=k
        )
        
        if not search_results:
            return {
                'recommendation': "Insufficient data for recommendation",
                'confidence': 0.0,
                'sources': []
            }
        
        # Format context
        context = self._format_context(search_results)
        
        # Generate recommendation
        recommendation = self._generate_procurement_recommendation(
            scenario=scenario,
            context_data=context_data,
            retrieved_context=context
        )
        
        return {
            'recommendation': recommendation,
            'sources': [
                {
                    'source': r['metadata'].get('file_name', 'unknown'),
                    'category': r['category'],
                    'relevance_score': r['score']
                }
                for r in search_results
            ],
            'num_sources': len(search_results),
            'timestamp': datetime.now().isoformat()
        }
    
    def _format_context(self, search_results: List[Dict[str, Any]]) -> str:
        """Format search results into context string"""
        context_parts = []
        
        for result in search_results:
            source = result['metadata'].get('file_name', 'unknown')
            category = result['category']
            content = result['content']
            
            context_parts.append(
                f"[Source: {source} | Category: {category}]\n{content}"
            )
        
        return "\n\n---\n\n".join(context_parts)
    
    def _generate_answer(
        self,
        question: str,
        context: str,
        verbose: bool = False
    ) -> str:
        """Generate answer using LLM with retrieved context"""
        
        system_prompt = """You are an expert procurement analyst with deep knowledge of supply chain management, 
supplier selection, risk management, and procurement best practices.

Your role is to provide accurate, actionable answers based on the provided context from procurement documents, 
policies, contracts, and industry best practices.

Guidelines:
- Answer based ONLY on the provided context
- If the context doesn't contain enough information, say so clearly
- Provide specific, actionable insights
- Cite relevant policies or rules when applicable
- Be concise but comprehensive
- Use professional procurement terminology"""

        user_prompt = f"""Context from procurement knowledge base:

{context}

---

Question: {question}

Please provide a detailed, accurate answer based on the context above."""

        try:
            if self.provider == "google":
                # For Google Gemini
                combined_prompt = f"{system_prompt}\n\n{user_prompt}"
                response = self.client.generate_content(
                    combined_prompt,
                    generation_config={
                        "temperature": self.temperature,
                        "max_output_tokens": 1000,
                    }
                )
                answer = response.text
            else:
                # For OpenAI
                response = self.client.chat.completions.create(
                    model=self.model_name,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    temperature=self.temperature,
                    max_tokens=1000
                    )
                answer = response.choices[0].message.content
            
            if verbose:
                print(f"\n LLM Response:")
                print(f"{answer[:200]}...")
            
            return answer
            
        except Exception as e:
            return f"Error generating answer: {str(e)}"
            return f"Error generating answer: {str(e)}"
    
    def _generate_procurement_recommendation(
        self,
        scenario: str,
        context_data: Dict[str, Any],
        retrieved_context: str
    ) -> str:
        """Generate procurement recommendation with RAG"""
        
        system_prompt = """You are a senior procurement strategist providing data-driven recommendations.

Use the retrieved context from procurement policies, best practices, and historical data to generate 
specific, actionable recommendations."""

        # Format context data
        context_summary = "\n".join([f"{k}: {v}" for k, v in context_data.items()])
        
        user_prompt = f"""Procurement Scenario:
{scenario}

Current Context:
{context_summary}

Relevant Procurement Knowledge:
{retrieved_context}

---

Based on the above information, provide a comprehensive procurement recommendation including:
1. Recommended action
2. Rationale based on policies and best practices
3. Expected outcomes
4. Risk considerations
5. Implementation steps"""

        try:
            if self.provider == "google":
                combined_prompt = f"{system_prompt}\n\n{user_prompt}"
                response = self.client.generate_content(
                    combined_prompt,
                    generation_config={
                        "temperature": self.temperature,
                        "max_output_tokens": 1500,
                    }
                )
                return response.text
            else:
                response = self.client.chat.completions.create(
                    model=self.model_name,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    temperature=self.temperature,
                    max_tokens=1500
                )
                return response.choices[0].message.content
            
        except Exception as e:
            return f"Error generating recommendation: {str(e)}"
    
    def _build_procurement_query(
        self,
        scenario: str,
        context_data: Dict[str, Any]
    ) -> str:
        """Build optimized query for procurement scenario"""
        
        # Extract key elements
        product = context_data.get('product', '')
        region = context_data.get('region', '')
        issue = context_data.get('issue', '')
        
        # Build query
        query_parts = [scenario]
        
        if product:
            query_parts.append(f"procurement of {product}")
        if region:
            query_parts.append(f"in {region}")
        if issue:
            query_parts.append(f"addressing {issue}")
        
        return " ".join(query_parts)


if __name__ == "__main__":
    # Demo usage
    print("\n RAG ENGINE DEMO\n")
    
    # Initialize vector store
    vector_store = VectorStoreManager(
        persist_directory="./data/vector_db",
        collection_name="procurement_docs"
    )
    
    # Load existing collection
    if vector_store.load_collection():
        # Initialize RAG engine
        rag = RAGEngine(
            vector_store_manager=vector_store,
            model="gpt-4"
        )
        
        # Test queries
        test_questions = [
            "What are the key criteria for supplier selection?",
            "How should we handle regional concentration risk?",
            "What are the ESG requirements for suppliers?",
            "How do we manage tail spend fragmentation?"
        ]
        
        for question in test_questions:
            print(f"\n{'='*60}")
            print(f"Q: {question}")
            print(f"{'='*60}")
            
            response = rag.query(
                question=question,
                k=3,
                verbose=False
            )
            
            print(f"\nA: {response['answer']}")
            
            if response.get('sources'):
                print(f"\n Sources ({len(response['sources'])}):")
                for source in response['sources']:
                    print(f"  - {source['source']} (score: {source['score']:.3f})")
    else:
        print(" No vector store found. Run document_processor.py first to create one.")
