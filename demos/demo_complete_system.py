"""
COMPLETE DEMO: All 13 Agents in Action
Shows the full 5-branch architecture
"""

import sys
from pathlib import Path

root_path = Path(__file__).parent.parent
sys.path.insert(0, str(root_path))

from backend.agents.orchestrator import AgentOrchestrator


def print_header(title: str):
    """Print section header"""
    print(f"\n{'='*100}")
    print(f"  {title}")
    print(f"{'='*100}\n")


def demo_all_agents():
    """Demo all 13 agents"""
    
    print_header("🚀 COMPLETE MULTI-AGENT SYSTEM DEMO - ALL 13 AGENTS")
    
    orchestrator = AgentOrchestrator()
    
    print(f"\n✅ System initialized with {len(orchestrator.agents)} agents:\n")
    for i, (name, agent) in enumerate(orchestrator.agents.items(), 1):
        print(f"   {i:2d}. {agent.name:30s} - {agent.description}")
    
    # Demo 1: Incumbent Supplier Capability Screening
    print_header("DEMO 1: INCUMBENT SUPPLIER CAPABILITY SCREENING")
    print("Question: Can our current Rice Bran Oil suppliers also provide Sunflower Oil?\n")
    
    capability_result = orchestrator.agents['capability_screener'].execute({
        'client_id': 'C001',
        'current_category': 'Rice Bran Oil',
        'target_category': 'Sunflower Oil'
    })
    
    if capability_result['success']:
        data = capability_result['data']
        print(f"✅ Found {data['capable_suppliers_count']}/{data['current_suppliers_count']} suppliers who can provide Sunflower Oil\n")
        
        if data['capable_suppliers']:
            print("CAPABLE SUPPLIERS:")
            for supplier in data['capable_suppliers']:
                print(f"   • {supplier['supplier_name']} ({supplier['country']})")
                print(f"     Current Spend: ${supplier['current_spend']:,.2f}")
                print(f"     Quality: {supplier['quality_rating']}/5.0")
                print(f"     Expansion Potential: {supplier['expansion_potential']['potential_spend_formatted']}\n")
        
        print(f"RECOMMENDATION:\n{data['recommendation']}")
    
    # Demo 2: Region Identification
    print_header("DEMO 2: ALTERNATIVE REGION IDENTIFICATION")
    print("Question: What are alternatives to Malaysia for Rice Bran Oil?\n")
    
    region_result = orchestrator.agents['region_identifier'].execute({
        'current_region': 'APAC',
        'product_category': 'Rice Bran Oil'
    })
    
    if region_result['success']:
        data = region_result['data']
        print(f"✅ Found {data['alternative_count']} alternative regions\n")
        
        print("TOP 3 ALTERNATIVES:")
        for alt in data['alternative_regions'][:3]:
            print(f"\n   {alt['region']} (Score: {alt['recommendation_score']:.1f}/100)")
            print(f"   • Suppliers: {alt['supplier_count']}")
            print(f"   • Quality: {alt['avg_quality_rating']}/5.0")
            print(f"   • Countries: {', '.join(alt['countries'][:3])}")
            print(f"   • Strengths: {', '.join(alt['strengths'][:2])}")
    
    # Demo 3: Supplier Ranking
    print_header("DEMO 3: SUPPLIER RANKING & EVALUATION")
    print("Question: Rank all Edible Oils suppliers by quality and criteria\n")
    
    ranking_result = orchestrator.agents['supplier_ranking'].execute({
        'product_category': 'Edible Oils',
        'client_criteria': {
            'min_quality': 4.5,
            'max_lead_time': 15,
            'required_certifications': ['ISO 22000']
        },
        'top_n': 5
    })
    
    if ranking_result['success']:
        data = ranking_result['data']
        print(f"✅ Evaluated {data['total_suppliers_evaluated']} suppliers\n")
        
        print(f"TOP {data['top_n']} SUPPLIERS:")
        for supplier in data['ranked_suppliers']:
            print(f"\n   #{supplier['rank']}. {supplier['supplier_name']} - Score: {supplier['overall_score']:.1f}/100")
            print(f"       Country: {supplier['country']}")
            print(f"       Quality: {supplier['quality_rating']}/5.0 | Delivery: {supplier['delivery_reliability']}%")
            print(f"       Meets Criteria: {'✅ YES' if supplier['meets_all_criteria'] else '❌ NO'}")
            print(f"       Strengths: {', '.join(supplier['strengths'][:2])}")
        
        print(f"\n💡 RECOMMENDATIONS:")
        for rec in data['recommendations']:
            print(f"   {rec}")
    
    # Demo 4: Complete Comprehensive Analysis
    print_header("DEMO 4: COMPREHENSIVE ANALYSIS (All Data Analysis Agents)")
    
    comp_result = orchestrator.execute_workflow(
        workflow_type='comprehensive_analysis',
        input_data={
            'client_id': 'C001',
            'category': 'Rice Bran Oil'
        }
    )
    
    if comp_result['success']:
        print(comp_result['results']['summary'])
    
    # Demo 5: Savings Opportunity with Action Plan
    print_header("DEMO 5: SAVINGS OPPORTUNITY ANALYSIS")
    
    savings_result = orchestrator.execute_workflow(
        workflow_type='savings_opportunity',
        input_data={
            'client_id': 'C001',
            'category': 'Rice Bran Oil',
            'scenario': 'price_negotiation',
            'target_price': 1180
        }
    )
    
    if savings_result['success'] and savings_result['results'].get('savings_calculation'):
        savings = savings_result['results']['savings_calculation']
        print(f"\n💰 SAVINGS OPPORTUNITY:")
        print(f"   Current Spend: {savings['current_spend_formatted']}")
        print(f"   Potential Savings: {savings['potential_savings_formatted']} ({savings['savings_percentage']:.1f}%)")
        print(f"   Timeline: {savings['implementation_timeline']}")
        print(f"   Confidence: {savings['confidence']}")
        
        if savings_result['results'].get('action_plan'):
            plan = savings_result['results']['action_plan']
            print(f"\n📝 ACTION PLAN ({plan['total_steps']} steps):")
            for step in plan['steps'][:3]:
                print(f"   {step['step']}. {step['action']} ({step['timeline']})")
    
    # Summary
    print_header("✅ DEMO COMPLETE - ALL 13 AGENTS DEMONSTRATED")
    
    print("\n📊 AGENT CATEGORIES:")
    print("\n1️⃣  DATA ANALYSIS (4 agents):")
    print("   ✅ SpendAnalyzer - Spend breakdowns")
    print("   ✅ RegionalConcentration - Regional risk analysis")
    print("   ✅ PatternDetector - Trends and anomalies")
    print("   ✅ ThresholdTracker - Rule compliance")
    
    print("\n2️⃣  INTELLIGENCE (4 agents):")
    print("   ✅ WebIntelligence - Real-time market data")
    print("   ✅ RiskScoring - Comprehensive risk scores")
    print("   ✅ RuleEngine - Rule evaluation")
    print("   ✅ BestPractice - Industry best practices")
    
    print("\n3️⃣  RECOMMENDATIONS (2 agents):")
    print("   ✅ SavingsCalculator - Exact savings calculations")
    print("   ✅ ActionPlanGenerator - Step-by-step plans")
    
    print("\n4️⃣  INCUMBENT STRATEGY (1 agent):")
    print("   ✅ SupplierCapabilityScreener - Expansion opportunities")
    
    print("\n5️⃣  REGION SOURCING (2 agents):")
    print("   ✅ RegionIdentifier - Alternative regions")
    print("   ✅ SupplierRanking - Supplier evaluation")
    
    print("\n" + "="*100)
    print("  🎯 COMPLETE 5-BRANCH ARCHITECTURE IMPLEMENTED!")
    print("="*100 + "\n")


if __name__ == "__main__":
    demo_all_agents()
