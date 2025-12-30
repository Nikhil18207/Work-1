"""
Complete R001 Optimization Demo

Demonstrates the full workflow with all components integrated:
1. Tariff Calculator
2. Leading Questions Generator
3. Enhanced Supplier Ranking
4. Constraint Validation Agent
5. R001 Optimization Workflow

This is the complete end-to-end system.
"""

import sys
from pathlib import Path

root_path = Path(__file__).parent.parent
if str(root_path) not in sys.path:
    sys.path.insert(0, str(root_path))

from backend.engines.r001_optimization_workflow import R001OptimizationWorkflow
from backend.engines.tariff_calculator import TariffCalculator
from backend.engines.leading_questions_generator import LeadingQuestionsGenerator
from backend.engines.data_loader import DataLoader


def print_header(title):
    """Print formatted header"""
    print("\n" + "="*80)
    print(f" {title}")
    print("="*80)


def demo_complete_workflow():
    """Run complete R001 optimization workflow"""
    
    print_header("🚀 COMPLETE R001 OPTIMIZATION WORKFLOW DEMO")
    
    # Initialize workflow
    print("\n📋 Initializing workflow components...")
    workflow = R001OptimizationWorkflow()
    tariff_calc = TariffCalculator()
    questions_gen = LeadingQuestionsGenerator()
    
    print("✅ All components initialized")
    
    # Step 1: Run R001 optimization
    print_header("STEP 1: R001 OPTIMIZATION WORKFLOW")
    
    result = workflow.execute(
        client_id='C001',
        category='Rice Bran Oil',
        interactive_mode=False  # Non-interactive for demo
    )
    
    # Step 2: Show tariff calculations
    print_header("STEP 2: TARIFF CALCULATIONS")
    
    if result.branch_a_regions:
        print("\n💰 Tariff Analysis for Top 3 Regions:")
        for i, region_option in enumerate(result.branch_a_regions[:3], 1):
            print(f"\n{i}. {region_option.region}")
            
            tariff_result = tariff_calc.calculate_tariff(
                from_country=region_option.region,
                to_country='USA',
                product_category='Rice Bran Oil',
                base_price=1000.0
            )
            
            print(f"   Base Price: $1,000")
            print(f"   Tariff Rate: {tariff_result.tariff_rate_pct}%")
            print(f"   Tariff Amount: ${tariff_result.tariff_amount:,.2f}")
            print(f"   Landed Cost: ${tariff_result.landed_cost:,.2f}")
            print(f"   Total Impact: +{tariff_result.total_cost_impact_pct}%")
            if tariff_result.trade_agreement_applied:
                print(f"   ✅ Trade Agreement: {tariff_result.trade_agreement_applied}")
    
    # Step 3: Show leading questions
    print_header("STEP 3: DATA COLLECTION QUESTIONS")
    
    if result.missing_data:
        print("\n❓ Missing Data Identified:")
        for item in result.missing_data:
            print(f"   • {item}")
        
        print("\n📋 Generating targeted questions...")
        questions = questions_gen.generate_questions(
            rule_id='R001',
            client_id='C001',
            category='Rice Bran Oil',
            current_data={},
            optimization_strategy='alternate_region_identification'
        )
        
        print(f"\n✅ Generated {len(questions)} questions")
        print("\nSample Questions:")
        for q in questions[:3]:
            print(f"\n   [{q.priority.value}] {q.question_text}")
            print(f"   💡 {q.why_it_matters}")
    
    # Step 4: Show final recommendations
    print_header("STEP 4: FINAL RECOMMENDATIONS")
    
    if result.top_3_recommendations:
        for rec in result.top_3_recommendations:
            print(f"\n{'='*74}")
            print(f"RECOMMENDATION #{rec['rank']}: {rec['strategy']}")
            print(f"{'='*74}")
            print(f"Description: {rec['description']}")
            print(f"Timeline: {rec.get('timeline', 'N/A')}")
            print(f"Risk Reduction: {rec.get('risk_reduction', 'N/A')}")
    
    # Step 5: Show briefs
    print_header("STEP 5: LEADERSHIP BRIEF GENERATION")
    
    if result.regional_brief:
        print("\n📄 REGIONAL CONCENTRATION BRIEF")
        print(f"   Title: {result.regional_brief.get('title', 'N/A')}")
        print(f"   Category: {result.regional_brief.get('category', 'N/A')}")
        
        if 'regional_dependency' in result.regional_brief:
            rd = result.regional_brief['regional_dependency']
            print("\n   Regional Dependency:")
            print(f"      Original SEA %: {rd.get('original_sea_pct', 'N/A')}%")
            print(f"      Target %: {rd.get('new_target_pct', 'N/A')}")
            print(f"      Reduction: {rd.get('reduction_pct', 'N/A')}")
            
        if 'strategic_outcome' in result.regional_brief:
            print("\n   Strategic Outcome:")
            for outcome in result.regional_brief['strategic_outcome'][:3]:
                print(f"      - {outcome}")

    if result.incumbent_brief:
        print("\n📄 INCUMBENT CONCENTRATION BRIEF")
        print(f"   Title: {result.incumbent_brief.get('title', 'N/A')}")
        
        if 'current_state' in result.incumbent_brief:
            cs = result.incumbent_brief['current_state']
            print(f"   Current Risk: {cs.get('key_risk', 'N/A')}")
            
        if 'supplier_reduction' in result.incumbent_brief:
            sr = result.incumbent_brief['supplier_reduction']
            dom = sr.get('dominant_supplier', {})
            print("\n   Supplier Reduction:")
            print(f"      Dominant Supplier Target: {dom.get('new_target_cap_pct', 'N/A')}% (from {dom.get('original_share_pct', 'N/A')}%)")
            
        if 'total_cost_advantage' in result.incumbent_brief:
            tca = result.incumbent_brief['total_cost_advantage']
            print(f"\n   Est. Annual Benefit: USD {tca.get('min_usd', 0):,} - {tca.get('max_usd', 0):,}")
    
    # Summary
    print_header("📊 WORKFLOW SUMMARY")
    
    print(f"\n✅ Violation Detected: {result.violation_detected}")
    print(f"✅ All Rules Compliant: {result.all_rules_compliant}")
    print(f"✅ Regions Identified: {len(result.branch_a_regions)}")
    print(f"✅ Suppliers Identified: {len(result.branch_b_suppliers)}")
    print(f"✅ Recommendations Generated: {len(result.top_3_recommendations)}")
    
    if result.final_allocation:
        print(f"\n📊 Final Allocation:")
        for region, pct in result.final_allocation.items():
            print(f"   {region}: {pct}%")
    
    print("\n" + "="*80)
    print("✅ COMPLETE WORKFLOW DEMO FINISHED")
    print("="*80)


def demo_tariff_comparison():
    """Demo tariff comparison across regions"""
    
    print_header("💰 TARIFF COMPARISON DEMO")
    
    calculator = TariffCalculator()
    
    regions = ['Malaysia', 'India', 'Thailand', 'Vietnam', 'China']
    
    print("\nComparing tariffs for Rice Bran Oil from different regions to USA:")
    print(f"\n{'Region':<15} {'Tariff Rate':<12} {'Landed Cost':<15} {'Cost Impact':<12} {'Trade Agreement':<20}")
    print("-" * 80)
    
    comparisons = calculator.compare_tariffs(
        to_country='USA',
        product_category='Rice Bran Oil',
        base_price=1000.0,
        from_countries=regions
    )
    
    for comp in comparisons:
        agreement = comp.trade_agreement_applied or "None"
        print(f"{comp.from_country:<15} {comp.tariff_rate_pct}%{'':<10} ${comp.landed_cost:,.2f}{'':<6} +{comp.total_cost_impact_pct}%{'':<8} {agreement:<20}")
    
    print("\n💡 Insight: Thailand has the lowest landed cost due to favorable trade agreements!")


if __name__ == "__main__":
    # Run complete workflow demo
    demo_complete_workflow()
    
    # Run tariff comparison demo
    demo_tariff_comparison()
