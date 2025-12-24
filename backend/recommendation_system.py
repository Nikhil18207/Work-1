"""
Main Recommendation API
Orchestrates all engines to generate procurement recommendations
"""

from typing import Dict, Any, Optional
import pandas as pd
import sys
from pathlib import Path

# Add workspace root to path
root_path = Path(__file__).parent.parent
if str(root_path) not in sys.path:
    sys.path.insert(0, str(root_path))

from backend.engines.data_loader import DataLoader
from backend.engines.rule_engine import RuleEngine
from backend.engines.scenario_detector import ScenarioDetector
from backend.engines.recommendation_generator import RecommendationGenerator


class RecommendationSystem:
    """
    Main orchestrator for the Supply Chain LLM Recommendation System
    Implements the complete 5-branch architecture
    """

    def __init__(self):
        """Initialize all engines"""
        self.data_loader = DataLoader()
        self.rule_engine = RuleEngine()
        self.scenario_detector = ScenarioDetector()
        self.recommendation_generator = RecommendationGenerator()

    def get_recommendation(
        self,
        category: str = "Rice Bran Oil",
        client_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get complete recommendation for a category
        
        Args:
            category: Product category to analyze
            client_id: Optional client ID for client-specific analysis
            
        Returns:
            Complete recommendation with all details
        """
        # Step 1: Load data (Branch 1: Data Architecture)
        spend_data = self.data_loader.load_spend_data()
        
        # Filter by category
        if category:
            spend_data = spend_data[spend_data['Category'] == category]
        
        # Filter by client if specified
        if client_id:
            spend_data = spend_data[spend_data['Client_ID'] == client_id]
        
        # Step 2: Evaluate rules (Branch 2: Rule Book Logic)
        rule_results = self.rule_engine.evaluate_all_rules(spend_data)
        
        # Step 3: Detect scenario (Branch 3: Sample Data Scenarios)
        scenario = self.scenario_detector.detect_scenario(category, spend_data)
        
        # Step 4: Generate recommendation (Branch 4: Recommendation Strategy)
        recommendation = self.recommendation_generator.generate_recommendation(scenario)
        
        # Step 5: Format output (Branch 5: Project Methodology - Specific Insights)
        formatted_text = self.recommendation_generator.format_recommendation(recommendation)
        
        return {
            "category": category,
            "client_id": client_id,
            "scenario": scenario.to_dict(),
            "rules_evaluated": [r.to_dict() for r in rule_results],
            "recommendation": recommendation.to_dict(),
            "formatted_output": formatted_text
        }

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
    
    # Initialize system
    system = RecommendationSystem()
    
    print("=" * 80)
    print("🚀 SUPPLY CHAIN LLM RECOMMENDATION SYSTEM")
    print("=" * 80)
    
    # Get recommendation
    result = system.get_recommendation("Rice Bran Oil")
    
    # Print formatted output
    print("\n" + result['formatted_output'])
    
    # Print JSON summary
    print("\n" + "=" * 80)
    print("📊 COMPLETE ANALYSIS (JSON)")
    print("=" * 80)
    print(json.dumps({
        "category": result['category'],
        "scenario_type": result['scenario']['scenario_type'],
        "risk_level": result['scenario']['risk_level'],
        "strategy": result['recommendation']['strategy'],
        "priority": result['recommendation']['priority'],
        "timeline": result['recommendation']['timeline']
    }, indent=2))
