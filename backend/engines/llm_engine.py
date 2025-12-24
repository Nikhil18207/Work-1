"""
LLM Engine
Integrates Large Language Models for natural language reasoning and explanations
Supports OpenAI GPT-4 and Google Gemini
"""

import os
from typing import Dict, List, Any, Optional
from enum import Enum
import json

try:
    from .scenario_detector import Scenario
    from .recommendation_generator import Recommendation
except ImportError:
    from scenario_detector import Scenario
    from recommendation_generator import Recommendation


class LLMProvider(Enum):
    """Supported LLM providers"""
    OPENAI = "openai"
    GEMINI = "gemini"


class LLMEngine:
    """
    LLM Engine for natural language reasoning and explanations
    Implements context-aware recommendations with explainability
    """

    def __init__(
        self,
        provider: LLMProvider = LLMProvider.OPENAI,
        api_key: Optional[str] = None,
        model: Optional[str] = None
    ):
        """
        Initialize LLM Engine
        
        Args:
            provider: LLM provider (OpenAI or Gemini)
            api_key: API key (if None, reads from environment)
            model: Model name (if None, uses default)
        """
        self.provider = provider
        self.api_key = api_key or self._get_api_key()
        self.model = model or self._get_default_model()
        self.client = self._initialize_client()

    def _get_api_key(self) -> str:
        """Get API key from environment"""
        if self.provider == LLMProvider.OPENAI:
            return os.getenv('OPENAI_API_KEY', '')
        elif self.provider == LLMProvider.GEMINI:
            return os.getenv('GEMINI_API_KEY', '')
        return ''

    def _get_default_model(self) -> str:
        """Get default model for provider"""
        if self.provider == LLMProvider.OPENAI:
            return "gpt-4"
        elif self.provider == LLMProvider.GEMINI:
            return "gemini-pro"
        return ""

    def _initialize_client(self):
        """Initialize LLM client"""
        if self.provider == LLMProvider.OPENAI:
            try:
                from openai import OpenAI
                return OpenAI(api_key=self.api_key)
            except ImportError:
                print("⚠️ OpenAI not installed. Run: pip install openai")
                return None
        elif self.provider == LLMProvider.GEMINI:
            try:
                import google.generativeai as genai
                genai.configure(api_key=self.api_key)
                return genai.GenerativeModel(self.model)
            except ImportError:
                print("⚠️ Google Generative AI not installed. Run: pip install google-generativeai")
                return None
        return None

    def generate_explanation(
        self,
        scenario: Scenario,
        recommendation: Recommendation,
        context: Dict[str, Any]
    ) -> str:
        """
        Generate natural language explanation for recommendation
        
        Args:
            scenario: Detected scenario
            recommendation: Generated recommendation
            context: Additional context (spend data, suppliers, etc.)
            
        Returns:
            Natural language explanation
        """
        # Build prompt
        prompt = self._build_explanation_prompt(scenario, recommendation, context)
        
        # Generate with LLM
        if self.client is None:
            return self._generate_fallback_explanation(scenario, recommendation)
        
        try:
            if self.provider == LLMProvider.OPENAI:
                return self._generate_openai(prompt)
            elif self.provider == LLMProvider.GEMINI:
                return self._generate_gemini(prompt)
        except Exception as e:
            print(f"⚠️ LLM generation failed: {e}")
            return self._generate_fallback_explanation(scenario, recommendation)

    def _build_explanation_prompt(
        self,
        scenario: Scenario,
        recommendation: Recommendation,
        context: Dict[str, Any]
    ) -> str:
        """Build prompt for LLM explanation"""
        
        prompt = f"""You are a procurement expert AI assistant analyzing supply chain data.

SCENARIO ANALYSIS:
- Category: {scenario.category}
- Pattern: {scenario.details.get('pattern', 'N/A')}
- Risk Level: {scenario.risk_level.value}
- Description: {scenario.details.get('description', 'N/A')}

TRIGGERED RULES:
"""
        for rule in scenario.triggered_rules:
            prompt += f"- {rule.rule_id}: {rule.rule_name}\n"
            prompt += f"  Actual: {rule.actual_value:.2f} | Threshold: {rule.threshold_value}\n"

        prompt += f"""
RECOMMENDATION STRATEGY: {recommendation.strategy.value}
Priority: {recommendation.priority}
Timeline: {recommendation.timeline}

RECOMMENDED ACTIONS:
"""
        for i, action in enumerate(recommendation.actions[:3], 1):
            prompt += f"{i}. {action['type']}\n"
            for key, value in action.items():
                if key not in ['action_id', 'type', 'specific'] and not isinstance(value, (list, dict)):
                    prompt += f"   - {key}: {value}\n"

        prompt += f"""
EXPECTED OUTCOMES:
"""
        for key, value in recommendation.expected_outcomes.items():
            prompt += f"- {key.replace('_', ' ').title()}: {value}\n"

        prompt += """
TASK:
Generate a clear, professional explanation of this procurement recommendation in 3-4 paragraphs:

1. **Current Situation**: Explain the current state and why it's problematic
2. **Risk Analysis**: Explain the specific risks and rule violations
3. **Recommended Solution**: Explain the strategy and specific actions
4. **Expected Impact**: Explain the expected outcomes and benefits

Be specific, use exact numbers, name suppliers, and explain the business rationale.
Write in a professional but conversational tone suitable for procurement executives.
"""
        
        return prompt

    def _load_system_prompt(self) -> str:
        """Load enterprise system prompt"""
        try:
            from pathlib import Path
            prompt_file = Path(__file__).parent.parent.parent / 'config' / 'prompts' / 'system_prompt.py'
            if prompt_file.exists():
                with open(prompt_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    # Extract SYSTEM_PROMPT variable
                    if 'SYSTEM_PROMPT = """' in content:
                        start = content.find('SYSTEM_PROMPT = """') + len('SYSTEM_PROMPT = """')
                        end = content.find('"""', start)
                        return content[start:end].strip()
            return self._get_default_system_prompt()
        except Exception as e:
            print(f"⚠️ Could not load system prompt: {e}")
            return self._get_default_system_prompt()
    
    def _get_default_system_prompt(self) -> str:
        """Get default system prompt if file not found"""
        return """You are the Beroe Inc Supply Chain Recommendation AI, an enterprise-grade procurement intelligence system.

CRITICAL RULES:
1. ZERO HALLUCINATION: Never invent data, suppliers, or numbers
2. TRACEABILITY: Cite source file + column for every claim
3. ACCURACY: Show calculations with formulas
4. SPECIFICITY: Use exact numbers, not ranges
5. DATA-DRIVEN: Only use provided data

RESPONSE FORMAT:
- State data source (spend_data.csv, supplier_contracts.csv, rule_book.csv)
- Show calculations (e.g., "93.55% = $13.85M / $14.80M")
- Cite rules (R001: Regional Concentration, threshold 40%)
- Provide specific recommendations with named suppliers
- Include confidence level and limitations

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
        """Generate with OpenAI using enterprise system prompt"""
        system_prompt = self._load_system_prompt()
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": system_prompt
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.3,  # Lower temperature for more factual responses
            max_tokens=2000
        )
        return response.choices[0].message.content

    def _generate_gemini(self, prompt: str) -> str:
        """Generate with Gemini"""
        response = self.client.generate_content(prompt)
        return response.text

    def _generate_fallback_explanation(
        self,
        scenario: Scenario,
        recommendation: Recommendation
    ) -> str:
        """Generate fallback explanation without LLM"""
        
        explanation = f"""
PROCUREMENT RECOMMENDATION ANALYSIS

Current Situation:
Your {scenario.category} procurement shows a {scenario.details.get('pattern', 'concerning pattern')}. 
The spend analysis reveals {scenario.details.get('description', 'concentration issues')}, 
which has been flagged as {scenario.risk_level.value} risk.

Risk Analysis:
"""
        for rule in scenario.triggered_rules:
            explanation += f"Rule {rule.rule_id} ({rule.rule_name}) has been triggered with an actual value of {rule.actual_value:.2f}, "
            explanation += f"exceeding the threshold of {rule.threshold_value}. {rule.action_recommendation}\n"

        explanation += f"""
Recommended Solution:
We recommend a {recommendation.strategy.value.replace('_', ' ').title()} strategy with {recommendation.priority} priority. 
This should be implemented over a {recommendation.timeline} timeframe.

Key actions include:
"""
        for i, action in enumerate(recommendation.actions[:3], 1):
            explanation += f"{i}. {action['type']}"
            if 'supplier_name' in action:
                explanation += f" - {action['supplier_name']} ({action.get('region', 'N/A')})"
            explanation += "\n"

        explanation += f"""
Expected Impact:
"""
        for key, value in recommendation.expected_outcomes.items():
            explanation += f"- {key.replace('_', ' ').title()}: {value}\n"

        return explanation.strip()

    def generate_confidence_score(
        self,
        scenario: Scenario,
        recommendation: Recommendation,
        data_completeness: float = 1.0
    ) -> Dict[str, Any]:
        """
        Generate confidence score for recommendation
        
        Args:
            scenario: Detected scenario
            recommendation: Generated recommendation
            data_completeness: Data completeness ratio (0-1)
            
        Returns:
            Confidence score with explanation
        """
        # Base confidence from rule triggers
        base_confidence = 60.0
        
        # Add confidence for triggered rules
        if len(scenario.triggered_rules) > 0:
            base_confidence += 20.0
        
        # Add confidence for data completeness
        base_confidence += (data_completeness * 15.0)
        
        # Add confidence for specific recommendations
        if len(recommendation.actions) >= 3:
            base_confidence += 5.0
        
        # Cap at 100
        confidence = min(base_confidence, 100.0)
        
        # Determine confidence level
        if confidence >= 90:
            level = "VERY HIGH"
            explanation = "Strong data support, clear rule violations, specific recommendations"
        elif confidence >= 75:
            level = "HIGH"
            explanation = "Good data support, rule violations detected, actionable recommendations"
        elif confidence >= 60:
            level = "MEDIUM"
            explanation = "Adequate data support, some patterns detected"
        else:
            level = "LOW"
            explanation = "Limited data, unclear patterns"
        
        return {
            "confidence_score": round(confidence, 2),
            "confidence_level": level,
            "explanation": explanation,
            "data_completeness": round(data_completeness * 100, 2),
            "rules_triggered": len(scenario.triggered_rules),
            "actions_recommended": len(recommendation.actions)
        }

    def generate_interactive_qa(
        self,
        scenario: Scenario,
        recommendation: Recommendation,
        question: str
    ) -> str:
        """
        Answer questions about the recommendation
        
        Args:
            scenario: Detected scenario
            recommendation: Generated recommendation
            question: User question
            
        Returns:
            Answer to the question
        """
        if self.client is None:
            return "LLM not available. Please configure API key."
        
        # Build context
        context = f"""
Scenario: {scenario.details.get('pattern', 'N/A')}
Risk Level: {scenario.risk_level.value}
Strategy: {recommendation.strategy.value}
Actions: {len(recommendation.actions)} recommended
        """
        
        prompt = f"""Based on this procurement recommendation:

{context}

User Question: {question}

Provide a clear, specific answer based on the recommendation data.
"""
        
        try:
            if self.provider == LLMProvider.OPENAI:
                return self._generate_openai(prompt)
            elif self.provider == LLMProvider.GEMINI:
                return self._generate_gemini(prompt)
        except Exception as e:
            return f"Unable to answer: {e}"


# Example usage
if __name__ == "__main__":
    from scenario_detector import ScenarioDetector
    from recommendation_generator import RecommendationGenerator
    
    # Detect scenario
    detector = ScenarioDetector()
    scenario = detector.detect_scenario("Rice Bran Oil")
    
    # Generate recommendation
    generator = RecommendationGenerator()
    recommendation = generator.generate_recommendation(scenario)
    
    # Initialize LLM engine (will use fallback if no API key)
    llm = LLMEngine(provider=LLMProvider.OPENAI)
    
    print("=" * 80)
    print("LLM-ENHANCED RECOMMENDATION")
    print("=" * 80)
    
    # Generate explanation
    explanation = llm.generate_explanation(scenario, recommendation, {})
    print("\n📝 EXPLANATION:")
    print(explanation)
    
    # Generate confidence score
    confidence = llm.generate_confidence_score(scenario, recommendation)
    print("\n" + "=" * 80)
    print("📊 CONFIDENCE SCORE")
    print("=" * 80)
    print(f"Score: {confidence['confidence_score']}%")
    print(f"Level: {confidence['confidence_level']}")
    print(f"Explanation: {confidence['explanation']}")
    print(f"Data Completeness: {confidence['data_completeness']}%")
    print(f"Rules Triggered: {confidence['rules_triggered']}")
    print(f"Actions Recommended: {confidence['actions_recommended']}")
