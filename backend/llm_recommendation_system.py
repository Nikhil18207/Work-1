"""
LLM-Enhanced Recommendation System
Complete system with LLM integration for natural language explanations
"""

import os
from typing import Dict, Any, Optional
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add parent directory to path
# Add workspace root to path
root_path = Path(__file__).parent.parent
if str(root_path) not in sys.path:
    sys.path.insert(0, str(root_path))

from backend.engines.data_loader import DataLoader
from backend.engines.rule_engine import RuleEngine
from backend.engines.scenario_detector import ScenarioDetector
from backend.engines.recommendation_generator import RecommendationGenerator
from backend.engines.llm_engine import LLMEngine, LLMProvider
from backend.engines.web_search_engine import WebSearchEngine
from backend.engines.rag_engine import RAGEngine
from backend.engines.vector_store_manager import VectorStoreManager


class LLMRecommendationSystem:
    """
    LLM-Enhanced Supply Chain Recommendation System
    Combines rule-based logic with LLM natural language reasoning
    """

    def __init__(
        self,
        llm_provider: str = "openai",
        api_key: Optional[str] = None,
        enable_llm: bool = True,
        enable_web_search: bool = True,
        enable_rag: bool = True
    ):
        """
        Initialize LLM-enhanced system
        
        Args:
            llm_provider: "openai" or "gemini"
            api_key: API key (if None, reads from environment)
            enable_llm: Whether to enable LLM features
            enable_web_search: Whether to enable real-time web search
            enable_rag: Whether to enable RAG (Retrieval Augmented Generation)
        """
        # Initialize core engines
        self.data_loader = DataLoader()
        self.rule_engine = RuleEngine()
        self.scenario_detector = ScenarioDetector()
        self.recommendation_generator = RecommendationGenerator()
        
        # Initialize LLM engine
        self.enable_llm = enable_llm
        if self.enable_llm:
            provider = LLMProvider.OPENAI if llm_provider.lower() == "openai" else LLMProvider.GEMINI
            self.llm_engine = LLMEngine(provider=provider, api_key=api_key)
        else:
            self.llm_engine = None
        
        # Initialize web search engine
        self.enable_web_search = enable_web_search
        if self.enable_web_search:
            self.web_search_engine = WebSearchEngine()
        else:
            self.web_search_engine = None
        
        # Initialize RAG engine
        self.enable_rag = enable_rag
        if self.enable_rag:
            try:
                # Use provider-specific directories and collection names
                if llm_provider.lower() == "google" or llm_provider.lower() == "gemini":
                    persist_dir = "./data/vector_db_gemini"
                    collection = "procurement_docs_gemini"
                    provider = "google"
                else:
                    persist_dir = "./data/vector_db"
                    collection = "procurement_docs"
                    provider = "openai"
                
                # Load vector store
                self.vector_store = VectorStoreManager(
                    persist_directory=persist_dir,
                    collection_name=collection,
                    provider=provider
                )
                
                # Try to load existing collection
                if self.vector_store.load_collection():
                    self.rag_engine = RAGEngine(
                        vector_store_manager=self.vector_store,
                        provider=provider,
                        api_key=api_key
                    )
                    print(f"✓ RAG engine initialized ({provider})")
                else:
                    print(f"⚠️  RAG: Vector store not found for {provider}")
                    self.rag_engine = None
            except Exception as e:
                print(f"⚠️  RAG initialization failed: {e}")
                self.rag_engine = None
        else:
            self.rag_engine = None

    def get_recommendation(
        self,
        category: str = "Rice Bran Oil",
        client_id: Optional[str] = None,
        include_llm_explanation: bool = True
    ) -> Dict[str, Any]:
        """
        Get complete LLM-enhanced recommendation
        
        Args:
            category: Product category to analyze
            client_id: Optional client ID
            include_llm_explanation: Whether to generate LLM explanation
            
        Returns:
            Complete recommendation with LLM insights
        """
        # Step 1: Load data
        spend_data = self.data_loader.load_spend_data()
        
        # Filter by category
        if category:
            spend_data = spend_data[spend_data['Category'] == category]
        
        # Filter by client if specified
        if client_id:
            spend_data = spend_data[spend_data['Client_ID'] == client_id]
        
        # Step 2: Evaluate rules
        rule_results = self.rule_engine.evaluate_all_rules(spend_data)
        
        # Step 3: Detect scenario
        scenario = self.scenario_detector.detect_scenario(category, spend_data)
        
        # Step 4: Generate recommendation
        recommendation = self.recommendation_generator.generate_recommendation(scenario)
        
        # Step 5: Format base output
        formatted_text = self.recommendation_generator.format_recommendation(recommendation)
        
        # Step 6: LLM Enhancement
        llm_explanation = None
        confidence_score = None
        
        if self.enable_llm and include_llm_explanation and self.llm_engine:
            try:
                # Generate natural language explanation
                llm_explanation = self.llm_engine.generate_explanation(
                    scenario,
                    recommendation,
                    {"spend_data": spend_data.to_dict('records')}
                )
                
                # Generate confidence score
                confidence_score = self.llm_engine.generate_confidence_score(
                    scenario,
                    recommendation
                )
            except Exception as e:
                print(f"⚠️ LLM enhancement failed: {e}")
        
        return {
            "category": category,
            "client_id": client_id,
            "scenario": scenario.to_dict(),
            "rules_evaluated": [r.to_dict() for r in rule_results],
            "recommendation": recommendation.to_dict(),
            "formatted_output": formatted_text,
            "llm_explanation": llm_explanation,
            "confidence_score": confidence_score,
            "llm_enabled": self.enable_llm
        }

    def ask_question(
        self,
        category: str,
        question: str
    ) -> str:
        """
        Ask a question about a category's recommendation
        
        Args:
            category: Product category
            question: User question
            
        Returns:
            LLM-generated answer
        """
        if not self.enable_llm or not self.llm_engine:
            return "LLM is not enabled. Please configure API key."
        
        # Get recommendation first
        result = self.get_recommendation(category, include_llm_explanation=False)
        scenario = self.scenario_detector.detect_scenario(category)
        recommendation = self.recommendation_generator.generate_recommendation(scenario)
        
        # Ask LLM
        return self.llm_engine.generate_interactive_qa(scenario, recommendation, question)

    def analyze_category(self, category: str) -> Dict[str, Any]:
        """Quick category analysis"""
        return self.data_loader.get_category_summary(category)

    def analyze_supplier(self, supplier_id: str) -> Dict[str, Any]:
        """Quick supplier analysis"""
        return self.data_loader.get_supplier_summary(supplier_id)

    def get_regional_analysis(self) -> Dict[str, Any]:
        """Get regional spend distribution"""
        return self.data_loader.get_regional_summary()


# Example usage
if __name__ == "__main__":
    import json
    
    print("=" * 80)
    print("🚀 LLM-ENHANCED SUPPLY CHAIN RECOMMENDATION SYSTEM")
    print("=" * 80)
    
    # Initialize system (will use fallback if no API key)
    system = LLMRecommendationSystem(
        llm_provider="openai",
        enable_llm=True
    )
    
    # Get recommendation
    print("\n📊 Generating recommendation...")
    result = system.get_recommendation("Rice Bran Oil")
    
    # Print formatted output
    print("\n" + result['formatted_output'])
    
    # Print LLM explanation if available
    if result['llm_explanation']:
        print("\n" + "=" * 80)
        print("🤖 LLM EXPLANATION")
        print("=" * 80)
        print(result['llm_explanation'])
    
    # Print confidence score
    if result['confidence_score']:
        print("\n" + "=" * 80)
        print("📊 CONFIDENCE SCORE")
        print("=" * 80)
        conf = result['confidence_score']
        print(f"Score: {conf['confidence_score']}% ({conf['confidence_level']})")
        print(f"Explanation: {conf['explanation']}")
        print(f"Data Completeness: {conf['data_completeness']}%")
        print(f"Rules Triggered: {conf['rules_triggered']}")
        print(f"Actions Recommended: {conf['actions_recommended']}")
    
    # Demo Q&A
    print("\n" + "=" * 80)
    print("💬 INTERACTIVE Q&A DEMO")
    print("=" * 80)
    
    questions = [
        "Why is APAC concentration a problem?",
        "What are the benefits of adding EuroSeed GmbH?",
        "How long will this transition take?"
    ]
    
    for q in questions:
        print(f"\nQ: {q}")
        answer = system.ask_question("Rice Bran Oil", q)
        print(f"A: {answer[:200]}..." if len(answer) > 200 else f"A: {answer}")
    
    print("\n" + "=" * 80)
    print("✅ LLM INTEGRATION COMPLETE!")
    print("=" * 80)

    def search_supplier_news(self, supplier_name: str, region: Optional[str] = None) -> Dict[str, Any]:
        if not self.enable_web_search or not self.web_search_engine:
            return {'status': 'disabled', 'message': 'Web search not enabled'}
        results = self.web_search_engine.search_supplier_news(supplier_name, region)
        return {'status': 'success', 'results': results, 'formatted_output': self.web_search_engine.format_search_results(results, f'{supplier_name} news')}

    def search_market_intelligence(self, product_category: str, region: Optional[str] = None) -> Dict[str, Any]:
        if not self.enable_web_search or not self.web_search_engine:
            return {'status': 'disabled', 'message': 'Web search not enabled'}
        results = self.web_search_engine.search_market_intelligence(product_category, region)
        return {'status': 'success', 'results': results, 'formatted_output': self.web_search_engine.format_search_results(results, f'{product_category} market intelligence')}

    def search_top_suppliers(self, product_category: str, region: str) -> Dict[str, Any]:
        if not self.enable_web_search or not self.web_search_engine:
            return {'status': 'disabled', 'message': 'Web search not enabled'}
        results = self.web_search_engine.search_top_suppliers(product_category, region)
        return {'status': 'success', 'results': results, 'formatted_output': self.web_search_engine.format_search_results(results, f'Top {product_category} suppliers in {region}')}
    
    # ========== RAG Methods ==========
    
    def query_knowledge_base(
        self,
        question: str,
        k: int = 5,
        category: Optional[str] = None,
        include_sources: bool = True
    ) -> Dict[str, Any]:
        """
        Query the procurement knowledge base using RAG
        
        Args:
            question: User question
            k: Number of context documents to retrieve
            category: Filter by document category
            include_sources: Include source citations
            
        Returns:
            Answer with sources and metadata
        """
        if not self.enable_rag or not self.rag_engine:
            return {
                'status': 'disabled',
                'message': 'RAG not enabled or vector store not initialized',
                'answer': 'RAG system not available. Run scripts/setup_rag.py to initialize.'
            }
        
        try:
            response = self.rag_engine.query(
                question=question,
                k=k,
                category=category,
                include_sources=include_sources,
                verbose=False
            )
            response['status'] = 'success'
            return response
        except Exception as e:
            return {
                'status': 'error',
                'message': str(e),
                'answer': f'Error querying knowledge base: {str(e)}'
            }
    
    def get_rag_recommendation(
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
        if not self.enable_rag or not self.rag_engine:
            return {
                'status': 'disabled',
                'message': 'RAG not enabled',
                'recommendation': 'RAG system not available'
            }
        
        try:
            response = self.rag_engine.get_procurement_recommendation(
                scenario=scenario,
                context_data=context_data,
                k=k
            )
            response['status'] = 'success'
            return response
        except Exception as e:
            return {
                'status': 'error',
                'message': str(e),
                'recommendation': f'Error generating recommendation: {str(e)}'
            }
    
    def semantic_search(
        self,
        query: str,
        k: int = 5,
        category: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Perform semantic search on procurement documents
        
        Args:
            query: Search query
            k: Number of results
            category: Filter by category
            
        Returns:
            Search results with scores
        """
        if not self.enable_rag or not self.vector_store:
            return {
                'status': 'disabled',
                'message': 'RAG not enabled',
                'results': []
            }
        
        try:
            results = self.vector_store.semantic_search(
                query=query,
                k=k,
                category=category,
                verbose=False
            )
            return {
                'status': 'success',
                'query': query,
                'num_results': len(results),
                'results': results
            }
        except Exception as e:
            return {
                'status': 'error',
                'message': str(e),
                'results': []
            }

