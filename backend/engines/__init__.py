"""
Engines package
Contains processing engines for the recommendation system
"""

# Core engines
from .data_loader import DataLoader
from .enhanced_rule_engine import EnhancedRuleEngine
from .enhanced_rule_engine import EnhancedRuleEngine as RuleEngine  # Alias for backward compatibility
from .scenario_detector import ScenarioDetector
from .recommendation_generator import RecommendationGenerator
from .llm_engine import LLMEngine
from .rag_engine import RAGEngine
from .vector_store_manager import VectorStoreManager
from .intelligent_search_engine import IntelligentSearchEngine
from .semantic_query_analyzer import SemanticQueryAnalyzer
from .web_search_engine import WebSearchEngine

# Main AI systems (moved from backend root)
from .conversational_ai import ConversationalAI
from .conversation_memory import ConversationMemory
from .llm_recommendation_system import LLMRecommendationSystem
from .semantic_use_case_matcher import SemanticUseCaseMatcher

# Document and export engines
from .leadership_brief_generator import LeadershipBriefGenerator
from .docx_exporter import DOCXExporter
from .document_processor import DocumentProcessor

# Workflow engines
from .r001_optimization_workflow import R001OptimizationWorkflow

__all__ = [
    # Core
    'DataLoader',
    'EnhancedRuleEngine',
    'RuleEngine',
    'ScenarioDetector',
    'RecommendationGenerator',
    'LLMEngine',
    'RAGEngine',
    'VectorStoreManager',
    'IntelligentSearchEngine',
    'SemanticQueryAnalyzer',
    'WebSearchEngine',
    # AI Systems
    'ConversationalAI',
    'ConversationMemory',
    'LLMRecommendationSystem',
    'SemanticUseCaseMatcher',
    # Document/Export
    'LeadershipBriefGenerator',
    'DOCXExporter',
    'DocumentProcessor',
    # Workflows
    'R001OptimizationWorkflow',
]
