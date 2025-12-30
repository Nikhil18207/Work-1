"""
Leading Questions Generator

Dynamically generates targeted questions to gather missing data
based on the specific optimization scenario and rule violations.

Features:
- Context-aware question generation
- Priority-based questioning (ask critical data first)
- Interactive data collection
- Validation of user responses
- Smart follow-up questions
"""

from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum


class QuestionPriority(Enum):
    """Priority levels for questions"""
    CRITICAL = "CRITICAL"  # Must have to proceed
    HIGH = "HIGH"  # Strongly recommended
    MEDIUM = "MEDIUM"  # Nice to have
    LOW = "LOW"  # Optional


class QuestionType(Enum):
    """Types of questions"""
    YES_NO = "yes_no"
    NUMERIC = "numeric"
    TEXT = "text"
    CHOICE = "choice"
    MULTIPLE_CHOICE = "multiple_choice"


@dataclass
class Question:
    """Represents a single question"""
    question_id: str
    question_text: str
    question_type: QuestionType
    priority: QuestionPriority
    context: str
    why_it_matters: str
    choices: Optional[List[str]] = None
    validation_rule: Optional[str] = None
    follow_up_questions: Optional[List[str]] = None


@dataclass
class QuestionResponse:
    """User's response to a question"""
    question_id: str
    response: Any
    confidence: float  # How confident is the user in this answer (0-100)
    notes: Optional[str] = None


class LeadingQuestionsGenerator:
    """
    Generates targeted questions to gather missing data
    
    Adapts questions based on:
    - Rule being optimized
    - Current data availability
    - Client context
    - Optimization strategy
    """
    
    def __init__(self):
        self.question_templates = self._initialize_question_templates()
    
    def generate_questions(
        self,
        rule_id: str,
        client_id: str,
        category: str,
        current_data: Dict[str, Any],
        optimization_strategy: str
    ) -> List[Question]:
        """
        Generate targeted questions based on context
        
        Args:
            rule_id: Rule being optimized (e.g., 'R001')
            client_id: Client identifier
            category: Product category
            current_data: Currently available data
            optimization_strategy: Strategy being used
            
        Returns:
            List of prioritized questions
        """
        questions = []
        
        # Get rule-specific questions
        rule_questions = self._get_rule_specific_questions(rule_id, current_data)
        questions.extend(rule_questions)
        
        # Get strategy-specific questions
        strategy_questions = self._get_strategy_specific_questions(
            optimization_strategy, current_data
        )
        questions.extend(strategy_questions)
        
        # Get category-specific questions
        category_questions = self._get_category_specific_questions(
            category, current_data
        )
        questions.extend(category_questions)
        
        # Sort by priority
        priority_order = {
            QuestionPriority.CRITICAL: 0,
            QuestionPriority.HIGH: 1,
            QuestionPriority.MEDIUM: 2,
            QuestionPriority.LOW: 3
        }
        questions.sort(key=lambda q: priority_order[q.priority])
        
        return questions
    
    def collect_responses(
        self,
        questions: List[Question],
        interactive: bool = True
    ) -> List[QuestionResponse]:
        """
        Collect responses to questions
        
        Args:
            questions: List of questions to ask
            interactive: If True, prompt user interactively
            
        Returns:
            List of responses
        """
        responses = []
        
        if not interactive:
            # Return empty responses for non-interactive mode
            return responses
        
        print("\n" + "="*80)
        print("📋 DATA COLLECTION - Please answer the following questions")
        print("="*80)
        
        for i, question in enumerate(questions, 1):
            print(f"\n[{i}/{len(questions)}] {question.priority.value} Priority")
            print(f"❓ {question.question_text}")
            print(f"💡 Why it matters: {question.why_it_matters}")
            
            # Get response based on question type
            response = self._get_user_response(question)
            
            if response is not None:
                responses.append(QuestionResponse(
                    question_id=question.question_id,
                    response=response,
                    confidence=80.0,  # Default confidence
                    notes=None
                ))
        
        return responses
    
    def _initialize_question_templates(self) -> Dict[str, List[Question]]:
        """Initialize question templates for different scenarios"""
        return {
            'R001_regional_concentration': [
                Question(
                    question_id='R001_Q1',
                    question_text='Which country is your primary destination for imports?',
                    question_type=QuestionType.CHOICE,
                    priority=QuestionPriority.CRITICAL,
                    context='Need to calculate accurate tariff rates',
                    why_it_matters='Tariff rates vary significantly by destination country. This affects total landed cost.',
                    choices=['USA', 'Europe', 'China', 'India', 'Other']
                ),
                Question(
                    question_id='R001_Q2',
                    question_text='Do you have any regional restrictions or preferences?',
                    question_type=QuestionType.TEXT,
                    priority=QuestionPriority.HIGH,
                    context='Some clients have geopolitical or regulatory constraints',
                    why_it_matters='Helps us avoid recommending regions that are not viable for your business.'
                ),
                Question(
                    question_id='R001_Q3',
                    question_text='What is your target timeline for diversification?',
                    question_type=QuestionType.CHOICE,
                    priority=QuestionPriority.HIGH,
                    context='Timeline affects supplier qualification process',
                    why_it_matters='Faster timelines may limit options to pre-qualified suppliers.',
                    choices=['30 days', '60 days', '90 days', '120+ days']
                ),
                Question(
                    question_id='R001_Q4',
                    question_text='What percentage of volume are you willing to allocate to new regions?',
                    question_type=QuestionType.NUMERIC,
                    priority=QuestionPriority.MEDIUM,
                    context='Helps size the diversification effort',
                    why_it_matters='Determines scale of supplier qualification and onboarding.',
                    validation_rule='0-100'
                ),
                Question(
                    question_id='R001_Q5',
                    question_text='Do you have existing trade agreements with any countries?',
                    question_type=QuestionType.TEXT,
                    priority=QuestionPriority.MEDIUM,
                    context='Trade agreements can reduce tariffs significantly',
                    why_it_matters='Can reduce landed costs by 50-100% through tariff elimination.'
                )
            ],
            'tariff_data': [
                Question(
                    question_id='TARIFF_Q1',
                    question_text='What are the current tariff rates for importing from your target regions?',
                    question_type=QuestionType.TEXT,
                    priority=QuestionPriority.CRITICAL,
                    context='Need accurate tariff data for cost calculations',
                    why_it_matters='Tariffs can add 3-15% to landed costs. Accurate rates are essential.'
                ),
                Question(
                    question_id='TARIFF_Q2',
                    question_text='Are there any upcoming tariff changes you are aware of?',
                    question_type=QuestionType.YES_NO,
                    priority=QuestionPriority.MEDIUM,
                    context='Tariff rates change frequently',
                    why_it_matters='Helps us factor in future cost changes in recommendations.'
                )
            ],
            'supplier_preferences': [
                Question(
                    question_id='SUPP_Q1',
                    question_text='What is your minimum acceptable quality rating for suppliers?',
                    question_type=QuestionType.NUMERIC,
                    priority=QuestionPriority.HIGH,
                    context='Quality standards vary by client',
                    why_it_matters='Ensures we only recommend suppliers meeting your quality standards.',
                    validation_rule='1-5'
                ),
                Question(
                    question_id='SUPP_Q2',
                    question_text='What certifications are mandatory for your suppliers?',
                    question_type=QuestionType.MULTIPLE_CHOICE,
                    priority=QuestionPriority.HIGH,
                    context='Certification requirements',
                    why_it_matters='Non-certified suppliers cannot be considered.',
                    choices=['ISO 22000', 'HACCP', 'Organic', 'RSPO', 'Fair Trade', 'None']
                ),
                Question(
                    question_id='SUPP_Q3',
                    question_text='What is your maximum acceptable lead time (in days)?',
                    question_type=QuestionType.NUMERIC,
                    priority=QuestionPriority.MEDIUM,
                    context='Lead time affects inventory planning',
                    why_it_matters='Longer lead times require higher safety stock.',
                    validation_rule='1-180'
                )
            ]
        }
    
    def _get_rule_specific_questions(
        self, rule_id: str, current_data: Dict[str, Any]
    ) -> List[Question]:
        """Get questions specific to the rule being optimized"""
        questions = []
        
        if rule_id == 'R001':
            # Regional concentration questions
            template_key = 'R001_regional_concentration'
            if template_key in self.question_templates:
                for q in self.question_templates[template_key]:
                    # Check if we already have this data
                    if not self._data_available(q.question_id, current_data):
                        questions.append(q)
        
        # Add more rule-specific questions as needed
        
        return questions
    
    def _get_strategy_specific_questions(
        self, strategy: str, current_data: Dict[str, Any]
    ) -> List[Question]:
        """Get questions specific to the optimization strategy"""
        questions = []
        
        if 'region' in strategy.lower():
            # Need tariff data
            if 'tariff_data' in self.question_templates:
                for q in self.question_templates['tariff_data']:
                    if not self._data_available(q.question_id, current_data):
                        questions.append(q)
        
        return questions
    
    def _get_category_specific_questions(
        self, category: str, current_data: Dict[str, Any]
    ) -> List[Question]:
        """Get questions specific to the product category"""
        questions = []
        
        # Supplier preference questions are generally applicable
        if 'supplier_preferences' in self.question_templates:
            for q in self.question_templates['supplier_preferences']:
                if not self._data_available(q.question_id, current_data):
                    questions.append(q)
        
        return questions
    
    def _data_available(self, question_id: str, current_data: Dict[str, Any]) -> bool:
        """Check if data for this question is already available"""
        # Map question IDs to data keys
        data_map = {
            'R001_Q1': 'destination_country',
            'R001_Q2': 'regional_restrictions',
            'R001_Q3': 'timeline',
            'R001_Q4': 'target_volume_pct',
            'R001_Q5': 'trade_agreements',
            'TARIFF_Q1': 'tariff_rates',
            'TARIFF_Q2': 'tariff_changes',
            'SUPP_Q1': 'min_quality_rating',
            'SUPP_Q2': 'required_certifications',
            'SUPP_Q3': 'max_lead_time'
        }
        
        data_key = data_map.get(question_id)
        if not data_key:
            return False
        
        return data_key in current_data and current_data[data_key] is not None
    
    def _get_user_response(self, question: Question) -> Any:
        """Get user response for a question (interactive mode)"""
        if question.question_type == QuestionType.YES_NO:
            while True:
                response = input("   Answer (yes/no): ").strip().lower()
                if response in ['yes', 'y', 'no', 'n']:
                    return response in ['yes', 'y']
                print("   ⚠️  Please answer 'yes' or 'no'")
        
        elif question.question_type == QuestionType.NUMERIC:
            while True:
                try:
                    response = input("   Answer (number): ").strip()
                    if not response:
                        return None
                    value = float(response)
                    
                    # Validate if rule exists
                    if question.validation_rule:
                        min_val, max_val = map(float, question.validation_rule.split('-'))
                        if min_val <= value <= max_val:
                            return value
                        print(f"   ⚠️  Please enter a number between {min_val} and {max_val}")
                    else:
                        return value
                except ValueError:
                    print("   ⚠️  Please enter a valid number")
        
        elif question.question_type == QuestionType.CHOICE:
            if question.choices:
                print("   Choices:")
                for i, choice in enumerate(question.choices, 1):
                    print(f"      {i}. {choice}")
                
                while True:
                    response = input(f"   Select (1-{len(question.choices)}): ").strip()
                    try:
                        idx = int(response) - 1
                        if 0 <= idx < len(question.choices):
                            return question.choices[idx]
                        print(f"   ⚠️  Please select a number between 1 and {len(question.choices)}")
                    except ValueError:
                        print("   ⚠️  Please enter a valid number")
        
        elif question.question_type == QuestionType.MULTIPLE_CHOICE:
            if question.choices:
                print("   Choices (select multiple, comma-separated):")
                for i, choice in enumerate(question.choices, 1):
                    print(f"      {i}. {choice}")
                
                response = input(f"   Select (e.g., 1,3,4): ").strip()
                if not response:
                    return []
                
                try:
                    indices = [int(x.strip()) - 1 for x in response.split(',')]
                    selected = [question.choices[i] for i in indices if 0 <= i < len(question.choices)]
                    return selected
                except (ValueError, IndexError):
                    print("   ⚠️  Invalid selection, skipping")
                    return []
        
        elif question.question_type == QuestionType.TEXT:
            response = input("   Answer: ").strip()
            return response if response else None
        
        return None
    
    def generate_summary(
        self, questions: List[Question], responses: List[QuestionResponse]
    ) -> Dict[str, Any]:
        """Generate summary of collected data"""
        response_map = {r.question_id: r.response for r in responses}
        
        summary = {
            'total_questions': len(questions),
            'answered': len(responses),
            'unanswered': len(questions) - len(responses),
            'critical_answered': sum(1 for q in questions if q.priority == QuestionPriority.CRITICAL 
                                    and q.question_id in response_map),
            'critical_total': sum(1 for q in questions if q.priority == QuestionPriority.CRITICAL),
            'responses': response_map,
            'data_completeness_pct': round(len(responses) / len(questions) * 100, 1) if questions else 100
        }
        
        return summary


# Example usage
if __name__ == "__main__":
    generator = LeadingQuestionsGenerator()
    
    print("="*80)
    print("LEADING QUESTIONS GENERATOR DEMO")
    print("="*80)
    
    # Generate questions for R001
    questions = generator.generate_questions(
        rule_id='R001',
        client_id='C001',
        category='Rice Bran Oil',
        current_data={},
        optimization_strategy='alternate_region_identification'
    )
    
    print(f"\n📋 Generated {len(questions)} questions for R001 optimization")
    print("\nQuestions by priority:")
    
    for priority in [QuestionPriority.CRITICAL, QuestionPriority.HIGH, 
                     QuestionPriority.MEDIUM, QuestionPriority.LOW]:
        priority_questions = [q for q in questions if q.priority == priority]
        if priority_questions:
            print(f"\n{priority.value} ({len(priority_questions)} questions):")
            for q in priority_questions:
                print(f"  • {q.question_text}")
                print(f"    💡 {q.why_it_matters}")
    
    # Simulate collecting responses (non-interactive)
    print("\n" + "="*80)
    print("In interactive mode, the system would now collect responses...")
    print("="*80)
