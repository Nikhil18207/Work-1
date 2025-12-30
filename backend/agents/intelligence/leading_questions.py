"""
Leading Questions Module
Intelligently asks users critical questions to gather missing information
Required for accurate tariff, cost, and risk calculations
"""

import sys
from pathlib import Path
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from enum import Enum

root_path = Path(__file__).parent.parent.parent.parent
if str(root_path) not in sys.path:
    sys.path.insert(0, str(root_path))

from backend.agents.base_agent import BaseAgent


class QuestionPriority(Enum):
    """Question priority levels"""
    CRITICAL = "CRITICAL"      # Must answer to proceed
    HIGH = "HIGH"              # Strongly recommended
    MEDIUM = "MEDIUM"          # Nice to have
    OPTIONAL = "OPTIONAL"      # For optimization


class QuestionType(Enum):
    """Types of questions"""
    MULTIPLE_CHOICE = "multiple_choice"
    NUMERIC = "numeric"
    TEXT = "text"
    YES_NO = "yes_no"
    RANKING = "ranking"


@dataclass
class Question:
    """Represents a single question"""
    question_id: str
    category: str
    text: str
    type: QuestionType
    priority: QuestionPriority
    options: Optional[List[str]] = None
    default_value: Optional[Any] = None
    follow_up_questions: Optional[List[str]] = None
    context: Optional[str] = None


class LeadingQuestionsModule(BaseAgent):
    """
    Intelligently gathers missing information through targeted questions
    Optimizes question flow based on dependencies
    """
    
    def __init__(self):
        super().__init__(
            name="LeadingQuestionsModule",
            description="Intelligently gathers critical information through guided questions"
        )
        self.questions_db = self._initialize_questions_db()
        self.user_responses = {}
    
    def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute question gathering workflow
        
        Input:
            - existing_data: Dict - data already available
            - analysis_type: str - type of analysis being run
            - required_fields: List[str] - fields that MUST be filled
            - skip_optional: bool - skip optional questions
        """
        try:
            existing_data = input_data.get('existing_data', {})
            analysis_type = input_data.get('analysis_type', 'general')
            required_fields = input_data.get('required_fields', [])
            skip_optional = input_data.get('skip_optional', False)
            
            # Determine which questions to ask
            questions_to_ask = self._determine_questions(
                analysis_type, existing_data, required_fields, skip_optional
            )
            
            # Sort by priority and dependencies
            sorted_questions = self._sort_by_priority_and_dependency(questions_to_ask)
            
            result = {
                'questions_to_ask': [self._question_to_dict(q) for q in sorted_questions],
                'total_questions': len(sorted_questions),
                'by_priority': self._group_by_priority(sorted_questions),
                'estimated_time_minutes': len(sorted_questions) * 2,
                'analysis_type': analysis_type,
                'metadata': {
                    'existing_data_fields': len(existing_data),
                    'critical_gaps': self._identify_critical_gaps(analysis_type, existing_data),
                    'can_proceed_without_all_answers': len([q for q in sorted_questions if q.priority == QuestionPriority.CRITICAL]) == 0
                }
            }
            
            self._log(f"Generated {len(sorted_questions)} questions for {analysis_type} analysis")
            
            return self._create_response(
                success=True,
                data=result
            )
            
        except Exception as e:
            self._log(f"Error in question generation: {str(e)}", "ERROR")
            return self._create_response(
                success=False,
                error=str(e)
            )
    
    def process_answers(self, answers: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process user responses to questions
        
        Input:
            - answers: Dict mapping question_id to user response
        
        Returns:
            - Processed data ready for analysis
            - Validation results
            - Follow-up questions if needed
        """
        try:
            processed_data = {}
            validation_errors = []
            follow_ups = []
            
            for question_id, answer in answers.items():
                question = self._get_question(question_id)
                if not question:
                    continue
                
                # Validate answer
                is_valid, error = self._validate_answer(question, answer)
                if not is_valid:
                    validation_errors.append({
                        'question_id': question_id,
                        'question': question.text,
                        'error': error
                    })
                    continue
                
                # Process answer
                processed_value = self._process_answer_value(question, answer)
                processed_data[question.category] = processed_value
                
                # Check for follow-ups
                if question.follow_up_questions and answer in question.options:
                    follow_ups.extend(question.follow_up_questions)
            
            return {
                'success': len(validation_errors) == 0,
                'processed_data': processed_data,
                'validation_errors': validation_errors,
                'follow_up_questions': follow_ups,
                'data_completeness': self._calculate_data_completeness(processed_data)
            }
            
        except Exception as e:
            self._log(f"Error processing answers: {str(e)}", "ERROR")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _initialize_questions_db(self) -> Dict[str, Question]:
        """Initialize the database of all possible questions"""
        
        questions = {
            # CRITICAL: Source Country Questions
            'Q_SOURCE_COUNTRY': Question(
                question_id='Q_SOURCE_COUNTRY',
                category='sourcing_geography',
                text='Which country is your current primary source for this product?',
                type=QuestionType.MULTIPLE_CHOICE,
                priority=QuestionPriority.CRITICAL,
                options=['Malaysia', 'India', 'Thailand', 'Vietnam', 'Indonesia', 'Brazil', 'Argentina', 'China', 'USA', 'Other'],
                context='Critical for tariff and logistics calculations'
            ),
            
            'Q_TARGET_COUNTRY': Question(
                question_id='Q_TARGET_COUNTRY',
                category='sourcing_geography',
                text='Which country are you importing to?',
                type=QuestionType.MULTIPLE_CHOICE,
                priority=QuestionPriority.CRITICAL,
                options=['USA', 'EU', 'India', 'China', 'Japan', 'UAE', 'Other'],
                context='Determines applicable tariff rates'
            ),
            
            'Q_ALTERNATE_SOURCES': Question(
                question_id='Q_ALTERNATE_SOURCES',
                category='sourcing_geography',
                text='What are your preferred alternate source countries? (Rank top 3)',
                type=QuestionType.RANKING,
                priority=QuestionPriority.HIGH,
                options=['Malaysia', 'India', 'Thailand', 'Vietnam', 'Indonesia', 'Brazil', 'Argentina'],
                context='For region comparison analysis'
            ),
            
            # CRITICAL: Product and Volume Questions
            'Q_PRODUCT_TYPE': Question(
                question_id='Q_PRODUCT_TYPE',
                category='product_info',
                text='What is the product category?',
                type=QuestionType.MULTIPLE_CHOICE,
                priority=QuestionPriority.CRITICAL,
                options=['Rice Bran Oil', 'Palm Oil', 'Coconut Oil', 'Soybean Oil', 'Sunflower Oil', 'Other'],
                context='Determines applicable rules and tariffs'
            ),
            
            'Q_ANNUAL_VOLUME': Question(
                question_id='Q_ANNUAL_VOLUME',
                category='volume_metrics',
                text='What is your annual volume for this product (in MT)?',
                type=QuestionType.NUMERIC,
                priority=QuestionPriority.CRITICAL,
                context='For cost and capacity calculations'
            ),
            
            'Q_EXPANSION_VOLUME': Question(
                question_id='Q_EXPANSION_VOLUME',
                category='volume_metrics',
                text='Do you plan to increase volume? If yes, by how much (MT or %)?',
                type=QuestionType.TEXT,
                priority=QuestionPriority.HIGH,
                default_value='No expansion planned',
                context='For opportunity sizing'
            ),
            
            # HIGH: Quality and Compliance Questions
            'Q_QUALITY_REQUIREMENTS': Question(
                question_id='Q_QUALITY_REQUIREMENTS',
                category='quality_compliance',
                text='What quality certifications are required?',
                type=QuestionType.MULTIPLE_CHOICE,
                priority=QuestionPriority.HIGH,
                options=['ISO 22000', 'HACCP', 'RSPO', 'None', 'Other'],
                context='For supplier screening'
            ),
            
            'Q_QUALITY_PRIORITY': Question(
                question_id='Q_QUALITY_PRIORITY',
                category='quality_compliance',
                text='How would you rate quality importance (1-5)?',
                type=QuestionType.NUMERIC,
                priority=QuestionPriority.MEDIUM,
                context='For criteria matching'
            ),
            
            'Q_SUSTAINABILITY': Question(
                question_id='Q_SUSTAINABILITY',
                category='quality_compliance',
                text='Is sustainability certification required?',
                type=QuestionType.YES_NO,
                priority=QuestionPriority.MEDIUM,
                context='For ESG compliance'
            ),
            
            # MEDIUM: Cost and Risk Preferences
            'Q_PRICE_TOLERANCE': Question(
                question_id='Q_PRICE_TOLERANCE',
                category='cost_preferences',
                text='What is your acceptable price variance from benchmark (%)?',
                type=QuestionType.NUMERIC,
                priority=QuestionPriority.MEDIUM,
                default_value=15,
                context='For cost analysis'
            ),
            
            'Q_RISK_APPETITE': Question(
                question_id='Q_RISK_APPETITE',
                category='risk_preferences',
                text='What is your risk tolerance?',
                type=QuestionType.MULTIPLE_CHOICE,
                priority=QuestionPriority.HIGH,
                options=['Conservative (Low Risk)', 'Balanced (Medium Risk)', 'Aggressive (High Risk)'],
                context='Affects region and supplier selection'
            ),
            
            'Q_SUPPLY_CHAIN_RESILIENCE': Question(
                question_id='Q_SUPPLY_CHAIN_RESILIENCE',
                category='risk_preferences',
                text='How important is supply chain resilience/diversification?',
                type=QuestionType.MULTIPLE_CHOICE,
                priority=QuestionPriority.MEDIUM,
                options=['Critical', 'Important', 'Moderate', 'Low Priority'],
                context='For diversification recommendations'
            ),
            
            # MEDIUM: Incumbent Supplier Relationship
            'Q_CURRENT_SUPPLIERS': Question(
                question_id='Q_CURRENT_SUPPLIERS',
                category='incumbent_info',
                text='Are you satisfied with current suppliers?',
                type=QuestionType.MULTIPLE_CHOICE,
                priority=QuestionPriority.MEDIUM,
                options=['Very Satisfied', 'Somewhat Satisfied', 'Neutral', 'Unsatisfied'],
                context='For incumbent expansion strategy'
            ),
            
            'Q_EXPANSION_READINESS': Question(
                question_id='Q_EXPANSION_READINESS',
                category='incumbent_info',
                text='Are current suppliers capable of expanding?',
                type=QuestionType.YES_NO,
                priority=QuestionPriority.MEDIUM,
                context='For incumbent screening'
            ),
            
            # OPTIONAL: Business Context
            'Q_BUSINESS_PRIORITY': Question(
                question_id='Q_BUSINESS_PRIORITY',
                category='business_context',
                text='What is your primary business priority?',
                type=QuestionType.MULTIPLE_CHOICE,
                priority=QuestionPriority.OPTIONAL,
                options=['Cost Reduction', 'Risk Mitigation', 'Quality Improvement', 'Market Expansion', 'Sustainability'],
                context='For prioritizing recommendations'
            ),
            
            'Q_TIMELINE': Question(
                question_id='Q_TIMELINE',
                category='business_context',
                text='What is your implementation timeline?',
                type=QuestionType.MULTIPLE_CHOICE,
                priority=QuestionPriority.OPTIONAL,
                options=['Immediate (< 1 month)', 'Short-term (1-3 months)', 'Medium-term (3-6 months)', 'Long-term (6+ months)'],
                context='Affects feasibility assessment'
            ),
        }
        
        return questions
    
    def _determine_questions(
        self, analysis_type: str, existing_data: Dict, required_fields: List[str], skip_optional: bool
    ) -> List[Question]:
        """Determine which questions need to be asked"""
        
        questions_to_ask = []
        
        # Always include CRITICAL questions that don't have data
        for q_id, question in self.questions_db.items():
            if question.priority == QuestionPriority.CRITICAL:
                # Check if data already exists
                if question.category not in existing_data:
                    questions_to_ask.append(question)
        
        # Add HIGH priority questions
        for q_id, question in self.questions_db.items():
            if question.priority == QuestionPriority.HIGH:
                if question.category not in existing_data:
                    questions_to_ask.append(question)
        
        # Add MEDIUM priority for specific analysis types
        if analysis_type in ['tariff_analysis', 'cost_comparison', 'regional_sourcing']:
            for q_id, question in self.questions_db.items():
                if question.priority == QuestionPriority.MEDIUM:
                    if question.category not in existing_data:
                        questions_to_ask.append(question)
        
        # Add OPTIONAL if not skipped
        if not skip_optional:
            for q_id, question in self.questions_db.items():
                if question.priority == QuestionPriority.OPTIONAL:
                    if question.category not in existing_data:
                        questions_to_ask.append(question)
        
        return questions_to_ask
    
    def _sort_by_priority_and_dependency(self, questions: List[Question]) -> List[Question]:
        """Sort questions by priority and dependencies"""
        
        priority_order = {
            QuestionPriority.CRITICAL: 0,
            QuestionPriority.HIGH: 1,
            QuestionPriority.MEDIUM: 2,
            QuestionPriority.OPTIONAL: 3,
        }
        
        return sorted(questions, key=lambda q: priority_order[q.priority])
    
    def _group_by_priority(self, questions: List[Question]) -> Dict:
        """Group questions by priority level"""
        
        grouped = {
            'CRITICAL': [],
            'HIGH': [],
            'MEDIUM': [],
            'OPTIONAL': []
        }
        
        for q in questions:
            grouped[q.priority.value].append({
                'id': q.question_id,
                'text': q.text,
                'type': q.type.value,
                'options': q.options
            })
        
        return grouped
    
    def _identify_critical_gaps(self, analysis_type: str, existing_data: Dict) -> List[str]:
        """Identify critical information gaps"""
        
        gaps = []
        
        critical_fields = {
            'tariff_analysis': ['sourcing_geography', 'product_info', 'volume_metrics'],
            'cost_comparison': ['sourcing_geography', 'volume_metrics', 'cost_preferences'],
            'regional_sourcing': ['sourcing_geography', 'risk_preferences', 'quality_compliance'],
            'incumbent_strategy': ['incumbent_info', 'volume_metrics', 'expansion_readiness'],
        }
        
        required_for_type = critical_fields.get(analysis_type, [])
        
        for field in required_for_type:
            if field not in existing_data:
                gaps.append(field)
        
        return gaps
    
    def _question_to_dict(self, q: Question) -> Dict:
        """Convert question object to dictionary"""
        return {
            'id': q.question_id,
            'category': q.category,
            'text': q.text,
            'type': q.type.value,
            'priority': q.priority.value,
            'options': q.options,
            'default': q.default_value,
            'context': q.context
        }
    
    def _get_question(self, question_id: str) -> Optional[Question]:
        """Get question by ID"""
        return self.questions_db.get(question_id)
    
    def _validate_answer(self, question: Question, answer: Any) -> tuple:
        """Validate user answer"""
        
        if question.type == QuestionType.MULTIPLE_CHOICE:
            if question.options and answer not in question.options:
                return False, f"Answer must be one of: {', '.join(question.options)}"
        
        elif question.type == QuestionType.NUMERIC:
            try:
                float(answer)
            except (ValueError, TypeError):
                return False, "Answer must be a number"
        
        elif question.type == QuestionType.YES_NO:
            if answer.lower() not in ['yes', 'no', 'true', 'false', '1', '0']:
                return False, "Answer must be Yes or No"
        
        return True, None
    
    def _process_answer_value(self, question: Question, answer: Any) -> Any:
        """Process and normalize answer value"""
        
        if question.type == QuestionType.NUMERIC:
            return float(answer)
        elif question.type == QuestionType.YES_NO:
            return answer.lower() in ['yes', 'true', '1']
        else:
            return answer
    
    def _calculate_data_completeness(self, processed_data: Dict) -> Dict:
        """Calculate how complete the data is"""
        
        total_categories = len(self.questions_db)
        filled_categories = len(processed_data)
        
        return {
            'percentage': round((filled_categories / total_categories) * 100, 1),
            'filled_categories': filled_categories,
            'total_categories': total_categories,
            'completeness_level': 'COMPLETE' if filled_categories > 0.8 * total_categories else 'GOOD' if filled_categories > 0.6 * total_categories else 'PARTIAL'
        }
