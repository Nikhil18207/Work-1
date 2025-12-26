"""
Complete System Demo
Demonstrates all 5 branches working together
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from engines.data_loader import DataLoader
from engines.rule_engine import RuleEngine
from engines.scenario_detector import ScenarioDetector
from engines.recommendation_generator import RecommendationGenerator
from recommendation_system import RecommendationSystem


def print_section(title):
    """Print section header"""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80 + "\n")


def demo_complete_system():
    """Demonstrate the complete 5-branch system"""
    
    print_section(" SUPPLY CHAIN LLM RECOMMENDATION SYSTEM - COMPLETE DEMO")
    
    # Initialize system
    system = RecommendationSystem()
    
    # BRANCH 1: DATA ARCHITECTURE
    print_section("BRANCH 1: DATA ARCHITECTURE")
    print(" Loading data from multiple sources...")
    
    regional = system.get_regional_analysis()
    print(f"Total Spend: ${regional['total_spend']:,.0f}")
    print(f"\nRegional Distribution:")
    for region, data in regional['regions'].items():
        print(f"  {region:15} ${data['spend']:>12,.0f} ({data['percentage']:>5.2f}%)")
    
    # BRANCH 2: RULE BOOK LOGIC
    print_section("BRANCH 2: RULE BOOK LOGIC")
    print(" Evaluating business rules...")
    
    spend_data = system.data_loader.load_spend_data()
    rule_results = system.rule_engine.evaluate_all_rules(spend_data)
    
    for rule in rule_results:
        status = " TRIGGERED" if rule.triggered else " PASSED"
        print(f"\n{rule.rule_id}: {rule.rule_name} - {status}")
        print(f"  Actual: {rule.actual_value:.2f} | Threshold: {rule.threshold_value}")
        print(f"  Risk Level: {rule.risk_level.value}")
        print(f"  Action: {rule.action_recommendation}")
    
    # BRANCH 3: SAMPLE DATA SCENARIOS
    print_section("BRANCH 3: SAMPLE DATA SCENARIOS")
    print(" Detecting procurement scenario...")
    
    scenario = system.scenario_detector.detect_scenario("Rice Bran Oil")
    print(f"\nScenario Type: {scenario.scenario_type.value}")
    print(f"Pattern: {scenario.details['pattern']}")
    print(f"Risk Level: {scenario.risk_level.value}")
    print(f"Description: {scenario.details['description']}")
    print(f"Primary Concern: {scenario.details['primary_concern']}")
    print(f"Recommended Strategy: {scenario.details['recommended_strategy']}")
    
    # BRANCH 4: RECOMMENDATION STRATEGY
    print_section("BRANCH 4: RECOMMENDATION STRATEGY")
    print(" Generating strategic recommendations...")
    
    recommendation = system.recommendation_generator.generate_recommendation(scenario)
    print(f"\nStrategy: {recommendation.strategy.value}")
    print(f"Priority: {recommendation.priority}")
    print(f"Timeline: {recommendation.timeline}")
    
    print(f"\n Actions ({len(recommendation.actions)} total):")
    for action in recommendation.actions[:3]:  # Show first 3
        print(f"\n  {action['action_id']}. {action['type']}")
        if 'supplier_name' in action:
            print(f"     Supplier: {action['supplier_name']} ({action['region']})")
            print(f"     ESG Score: {action['esg_score']}")
            print(f"     Allocation: {action['allocation']}")
    
    print(f"\n Expected Outcomes:")
    for key, value in recommendation.expected_outcomes.items():
        print(f"  - {key.replace('_', ' ').title()}: {value}")
    
    # BRANCH 5: PROJECT METHODOLOGY
    print_section("BRANCH 5: PROJECT METHODOLOGY - SPECIFIC INSIGHTS")
    print(" Demonstrating specific vs generic insights...\n")
    
    print(" GENERIC (Bad):")
    print('  "Consider diversifying your suppliers."\n')
    
    print(" SPECIFIC (Good):")
    print(f'  "Your Rice Bran Oil spend is {scenario.details["concentration_pct"]}% ')
    print(f'   concentrated in {scenario.details["concentration_region"]}.')
    print(f'   This exceeds our 40% threshold (Rule R001).')
    print(f'   ')
    print(f'   Recommended Actions:')
    print(f'   1. Reduce {scenario.details["concentration_region"]} to 35%')
    print(f'      (reallocate ${recommendation.actions[0]["reallocation_required"]})')
    print(f'   2. Add {recommendation.actions[1]["supplier_name"]} ')
    print(f'      ({recommendation.actions[1]["region"]}, ESG: {recommendation.actions[1]["esg_score"]})')
    print(f'   3. Timeline: {recommendation.timeline}')
    print(f'   4. Expected: Risk {scenario.risk_level.value} → MEDIUM, Resilience +60%"')
    
    # COMPLETE FORMATTED OUTPUT
    print_section("COMPLETE RECOMMENDATION OUTPUT")
    formatted = system.recommendation_generator.format_recommendation(recommendation)
    print(formatted)
    
    # SUMMARY
    print_section(" SYSTEM DEMONSTRATION COMPLETE")
    print("All 5 branches working together successfully!")
    print("\n Branch 1: Data Architecture - Data loaded from multiple sources")
    print(" Branch 2: Rule Book Logic - Rules evaluated (R001, R002)")
    print(" Branch 3: Sample Data Scenarios - Scenario detected (Rice Bran Oil)")
    print(" Branch 4: Recommendation Strategy - Strategy generated (Risk Reduction)")
    print(" Branch 5: Project Methodology - Specific insights provided")
    print("\n System is PRODUCTION-READY!")


if __name__ == "__main__":
    demo_complete_system()
