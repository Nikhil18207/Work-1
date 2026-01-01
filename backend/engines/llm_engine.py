"""
LLM Engine - OpenAI GPT integration for brief generation
"""

import os
from typing import Optional


class LLMEngine:
    """
    LLM Engine for natural language generation
    Uses OpenAI GPT-4 for context-aware text generation
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None
    ):
        """
        Initialize LLM Engine with OpenAI

        Args:
            api_key: OpenAI API key (if None, reads from environment)
            model: Model name (if None, uses gpt-4o)
        """
        self.api_key = api_key or os.getenv('OPENAI_API_KEY', '')
        self.model = model or "gpt-4o"
        self.client = self._initialize_client()

    def _initialize_client(self):
        """Initialize OpenAI client"""
        if not self.api_key:
            print("[WARN] OPENAI_API_KEY not set")
            return None

        try:
            from openai import OpenAI
            return OpenAI(api_key=self.api_key)
        except ImportError:
            print("[WARN] OpenAI not installed. Run: pip install openai")
            return None

    def _load_system_prompt(self) -> str:
        """Load enterprise system prompt"""
        try:
            from pathlib import Path
            prompt_file = Path(__file__).parent.parent.parent / 'config' / 'prompts' / 'system_prompt.py'
            if prompt_file.exists():
                with open(prompt_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    if 'SYSTEM_PROMPT = """' in content:
                        start = content.find('SYSTEM_PROMPT = """') + len('SYSTEM_PROMPT = """')
                        end = content.find('"""', start)
                        return content[start:end].strip()
            return self._get_default_system_prompt()
        except Exception:
            return self._get_default_system_prompt()

    def _get_default_system_prompt(self) -> str:
        """Get default system prompt"""
        return """You are the Beroe Inc Supply Chain Recommendation AI, an enterprise-grade procurement intelligence system.

CRITICAL RULES:
1. ZERO HALLUCINATION: Never invent data, suppliers, or numbers
2. TRACEABILITY: Cite source for every claim
3. ACCURACY: Show calculations with formulas
4. SPECIFICITY: Use exact numbers, not ranges
5. DATA-DRIVEN: Only use provided data

NEVER:
- Invent supplier names or numbers
- Make assumptions without data
- Provide generic advice
- State opinions as facts

ALWAYS:
- Cite source for every number
- Show calculation formulas
- Reference specific rules
- Acknowledge data limitations
"""

    def _generate_openai(self, prompt: str) -> str:
        """
        Generate text with OpenAI

        Args:
            prompt: The prompt to send to OpenAI

        Returns:
            Generated text response
        """
        if self.client is None:
            return ""

        system_prompt = self._load_system_prompt()

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=2000
        )
        return response.choices[0].message.content
