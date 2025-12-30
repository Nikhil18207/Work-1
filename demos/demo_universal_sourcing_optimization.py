"""
Demo: Universal Sourcing Optimization System

Demonstrates how the system handles ANY of the 35 procurement rules,
not just R001.
"""

import sys
sys.path.append('.')

from backend.engines.sourcing_optimization_engine import SourcingOptimizationEngine
from backend.engines.data_loader import DataLoader
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def demo_r001_regional_concentration():
    """Demo: R001 - Regional Concentration"""
    print("\n" + "="*80)
    print("DEMO 1: R001 - Regional Concentration (Geographic Risk)")
    print("="*80)
    
    # Initialize engine
    data_loader = DataLoader()
    engine = SourcingOptimizationEngine(data_loader)
    
    # Current state: Malaysia 85% (VIOLATION)
    current_metrics = {
        'regional_concentration': 85.0,  # >40% threshold
        'allocation': {
            'Malaysia': 85,
            'India': 10,
            'Thailand': 5
        }
    }
    
    # Run optimization
    result = engine.optimize('R001', current_metrics)
    
    # Display results
    print(f"\n✅ Rule: {result.rule_name}")
    print(f"📊 Recommendations: {len(result.recommendations)}")
    print(f"💰 Cost Impact: {result.cost_impact:+.1f}%")
    print(f"⚠️  Risk Reduction: {result.risk_reduction:.1f}%")
    print(f"📅 Timeline: {result.implementation_timeline} days")
    print(f"✅ All Rules Compliant: {result.all_rules_compliant}")
    
    print("\n🥇 Top Recommendation:")
    if result.recommendations:
        top_rec = result.recommendations[0]
        print(f"   Strategy: {top_rec['strategy']}")
        print(f"   Score: {top_rec['score']}/100")
        print(f"   Details: {top_rec['description']}")


def demo_r003_single_supplier_dependency():
    """Demo: R003 - Single Supplier Dependency"""
    print("\n" + "="*80)
    print("DEMO 2: R003 - Single Supplier Dependency (Supply Chain Risk)")
    print("="*80)
    
    # Initialize engine
    data_loader = DataLoader()
    engine = SourcingOptimizationEngine(data_loader)
    
    # Current state: Supplier A 75% (VIOLATION)
    current_metrics = {
        'single_supplier_percentage': 75.0,  # >60% threshold
        'allocation': {
            'Supplier A': 75,
            'Supplier B': 25
        }
    }
    
    # Run optimization
    result = engine.optimize('R003', current_metrics)
    
    # Display results
    print(f"\n✅ Rule: {result.rule_name}")
    print(f"📊 Recommendations: {len(result.recommendations)}")
    print(f"💰 Cost Impact: {result.cost_impact:+.1f}%")
    print(f"⚠️  Risk Reduction: {result.risk_reduction:.1f}%")
    print(f"📅 Timeline: {result.implementation_timeline} days")
    print(f"✅ All Rules Compliant: {result.all_rules_compliant}")


def demo_r007_quality_rejection_rate():
    """Demo: R007 - Quality Rejection Rate"""
    print("\n" + "="*80)
    print("DEMO 3: R007 - Quality Rejection Rate (Quality Assurance)")
    print("="*80)
    
    # Initialize engine
    data_loader = DataLoader()
    engine = SourcingOptimizationEngine(data_loader)
    
    # Current state: 8% rejection rate (VIOLATION)
    current_metrics = {
        'quality_rejection_rate': 8.0,  # >5% threshold
        'defect_rate': 8.0
    }
    
    # Run optimization
    result = engine.optimize('R007', current_metrics)
    
    # Display results
    print(f"\n✅ Rule: {result.rule_name}")
    print(f"📊 Recommendations: {len(result.recommendations)}")
    print(f"💰 Cost Impact: {result.cost_impact:+.1f}%")
    print(f"⚠️  Risk Reduction: {result.risk_reduction:.1f}%")
    print(f"📅 Timeline: {result.implementation_timeline} days")
    print(f"✅ All Rules Compliant: {result.all_rules_compliant}")


def demo_strategy_selection():
    """Demo: Dynamic Strategy Selection for Different Rules"""
    print("\n" + "="*80)
    print("DEMO 4: Dynamic Strategy Selection (All Rule Categories)")
    print("="*80)
    
    # Initialize engine
    data_loader = DataLoader()
    engine = SourcingOptimizationEngine(data_loader)
    
    # Test different rule categories
    test_rules = [
        ('R001', 'Geographic Risk'),
        ('R003', 'Supply Chain Risk'),
        ('R006', 'Cost Management'),
        ('R007', 'Quality Assurance'),
        ('R005', 'Sustainability'),
        ('R004', 'Contract Management'),
        ('R002', 'Operational Efficiency'),
    ]
    
    print("\n📋 Strategy Selection for Different Rules:\n")
    
    for rule_id, expected_category in test_rules:
        rule_info = engine.rulebook[engine.rulebook['Rule_ID'] == rule_id].iloc[0]
        strategy = engine.select_optimization_strategy(rule_info['Category'])
        
        print(f"Rule {rule_id} ({rule_info['Rule_Name']}):")
        print(f"  Category: {rule_info['Category']}")
        print(f"  Branch A: {strategy.branch_a_strategy}")
        print(f"  Branch B: {strategy.branch_b_strategy}")
        print(f"  Tools: {', '.join(strategy.tools)}")
        print()


def demo_data_checklist_generation():
    """Demo: Dynamic Data Checklist Generation"""
    print("\n" + "="*80)
    print("DEMO 5: Dynamic Data Checklist Generation")
    print("="*80)
    
    # Initialize engine
    data_loader = DataLoader()
    engine = SourcingOptimizationEngine(data_loader)
    
    # Test checklist generation for different categories
    categories = [
        'Geographic Risk',
        'Supply Chain Risk',
        'Cost Management',
        'Quality Assurance',
        'Sustainability'
    ]
    
    print("\n📋 Data Requirements by Category:\n")
    
    for category in categories:
        checklist = engine.generate_data_checklist(category)
        print(f"{category}:")
        for item in checklist:
            print(f"  □ {item}")
        print()


def demo_validation_against_all_rules():
    """Demo: Validation Against All 35 Rules"""
    print("\n" + "="*80)
    print("DEMO 6: Validation Against All 35 Rules")
    print("="*80)
    
    # Initialize engine
    data_loader = DataLoader()
    engine = SourcingOptimizationEngine(data_loader)
    
    # Proposed state after optimization
    proposed_state = {
        'regional_concentration': 45.0,  # Reduced from 85%
        'single_supplier_percentage': 50.0,  # Reduced from 75%
        'quality_rejection_rate': 4.0,  # Improved from 8%
        'price_variance_percentage': 12.0,  # Within limits
    }
    
    print("\n🔍 Validating proposed state against all 35 rules...")
    
    is_compliant, violations = engine.validate_against_all_rules(proposed_state)
    
    print(f"\n✅ Validation Result: {'COMPLIANT' if is_compliant else 'VIOLATIONS FOUND'}")
    print(f"📊 Total Violations: {len(violations)}")
    
    if violations:
        print("\n⚠️  Violations Detected:")
        for v in violations:
            print(f"   - {v.rule_id}: {v.rule_name}")
            print(f"     Current: {v.current_value}, Threshold: {v.threshold}")


def main():
    """Run all demos"""
    print("\n" + "="*80)
    print("UNIVERSAL SOURCING OPTIMIZATION SYSTEM - DEMO")
    print("Handles ANY of the 35 Procurement Rules (R001-R035)")
    print("="*80)
    
    try:
        # Demo 1: R001 - Regional Concentration
        demo_r001_regional_concentration()
        
        # Demo 2: R003 - Single Supplier Dependency
        demo_r003_single_supplier_dependency()
        
        # Demo 3: R007 - Quality Rejection Rate
        demo_r007_quality_rejection_rate()
        
        # Demo 4: Dynamic Strategy Selection
        demo_strategy_selection()
        
        # Demo 5: Data Checklist Generation
        demo_data_checklist_generation()
        
        # Demo 6: Validation Against All Rules
        demo_validation_against_all_rules()
        
        print("\n" + "="*80)
        print("✅ ALL DEMOS COMPLETE")
        print("="*80)
        print("\nKey Takeaway:")
        print("  R001 was just an example - this system works for ALL 35 rules!")
        print("  The engine dynamically selects strategies based on rule category.")
        print("  Every solution is validated against ALL 35 rules.")
        print("="*80 + "\n")
        
    except Exception as e:
        logger.error(f"Error running demos: {e}", exc_info=True)


if __name__ == "__main__":
    main()
