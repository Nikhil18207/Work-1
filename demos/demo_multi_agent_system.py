"""
Demo: Multi-Agent Procurement System
Shows the power of the agent-based architecture
"""

import sys
from pathlib import Path

root_path = Path(__file__).parent.parent
sys.path.insert(0, str(root_path))

from backend.agents.orchestrator import AgentOrchestrator
import json


def print_section(title: str):
    """Print section header"""
    print(f"\n{'='*100}")
    print(f"  {title}")
    print(f"{'='*100}\n")


def demo_comprehensive_analysis():
    """Demo: Comprehensive analysis for a client"""
    print_section("DEMO 1: COMPREHENSIVE ANALYSIS - Client C001, Rice Bran Oil")
    
    orchestrator = AgentOrchestrator()
    
    result = orchestrator.execute_workflow(
        workflow_type='comprehensive_analysis',
        input_data={
            'client_id': 'C001',
            'category': 'Rice Bran Oil'
        }
    )
    
    if result['success']:
        print("\n📊 RESULTS:\n")
        print(result['results']['summary'])
        
        # Show spend details
        if result['results'].get('spend_analysis'):
            spend = result['results']['spend_analysis']
            print("\n💰 SPEND BREAKDOWN BY SUPPLIER:")
            for supplier in spend['spend_by_supplier'][:3]:
                print(f"   • {supplier['Supplier_Name']}: ${supplier['total']:,.2f} ({supplier['percentage']:.1f}%)")
        
        # Show regional risk
        if result['results'].get('regional_analysis'):
            regional = result['results']['regional_analysis']
            print(f"\n🌍 REGIONAL RISK:")
            print(f"   {regional['risk_explanation']}")
            print(f"   Recommendation: {regional['diversification_recommendation']}")
        
        # Show threshold violations
        if result['results'].get('thresholds'):
            thresholds = result['results']['thresholds']
            if thresholds['violations']:
                print(f"\n⚠️  VIOLATIONS FOUND:")
                for v in thresholds['violations'][:2]:
                    print(f"   • {v['message']}")
                    print(f"     Action: {v['action_required']}")


def demo_rule_evaluation():
    """Demo: Evaluate specific rule"""
    print_section("DEMO 2: RULE EVALUATION - HC001 (Food Safety Certification)")
    
    orchestrator = AgentOrchestrator()
    
    result = orchestrator.execute_workflow(
        workflow_type='rule_evaluation',
        input_data={
            'rule_id': 'HC001',
            'client_id': 'C001',
            'category': 'Rice Bran Oil'
        }
    )
    
    if result['success']:
        rule_eval = result['results']['rule_evaluation']
        
        print(f"\n📋 RULE: {rule_eval['rule_name']}")
        print(f"   Status: {rule_eval['status']}")
        print(f"   Violations: {rule_eval['violation_count']}")
        print(f"   Compliant Suppliers: {rule_eval['compliant_count']}")
        
        if rule_eval['violations']:
            print(f"\n⚠️  VIOLATIONS:")
            for v in rule_eval['violations']:
                print(f"   • {v['supplier_name']}: {v['issue']}")
                print(f"     Spend at risk: ${v['spend']:,.2f}")
        
        print(f"\n💡 RECOMMENDATION:")
        print(f"   {rule_eval['recommendation']}")
        
        # Show action plan if available
        if result['results'].get('action_plan'):
            action_plan = result['results']['action_plan']
            print(f"\n📝 ACTION PLAN ({action_plan['total_steps']} steps):")
            for step in action_plan['steps'][:3]:
                print(f"   {step['step']}. {step['action']}")


def demo_savings_opportunity():
    """Demo: Calculate savings opportunity"""
    print_section("DEMO 3: SAVINGS OPPORTUNITY - Price Negotiation for Rice Bran Oil")
    
    orchestrator = AgentOrchestrator()
    
    result = orchestrator.execute_workflow(
        workflow_type='savings_opportunity',
        input_data={
            'client_id': 'C001',
            'category': 'Rice Bran Oil',
            'scenario': 'price_negotiation',
            'target_price': 1180  # Target price per ton
        }
    )
    
    if result['success']:
        savings = result['results']['savings_calculation']
        
        print(f"\n💰 SAVINGS ANALYSIS:")
        print(f"   Current Spend: {savings['current_spend_formatted']}")
        print(f"   Potential Savings: {savings['potential_savings_formatted']}")
        print(f"   Savings %: {savings['savings_percentage']:.1f}%")
        print(f"   Timeline: {savings['implementation_timeline']}")
        print(f"   Confidence: {savings['confidence']}")
        
        if savings.get('current_price'):
            print(f"\n📊 PRICE COMPARISON:")
            print(f"   Current Price: ${savings['current_price']:,.2f}/ton")
            print(f"   Market Price: ${savings['market_price']:,.2f}/ton")
            print(f"   Target Price: ${savings['target_price']:,.2f}/ton")
            print(f"   Gap: ${savings['price_gap']:,.2f}/ton")
        
        # Show action plan
        if result['results'].get('action_plan'):
            action_plan = result['results']['action_plan']
            print(f"\n📝 ACTION PLAN:")
            for step in action_plan['steps'][:4]:
                print(f"   {step['step']}. {step['action']} ({step['timeline']})")
                print(f"      Owner: {step['owner']}")


def demo_risk_assessment():
    """Demo: Risk assessment for a supplier"""
    print_section("DEMO 4: RISK ASSESSMENT - Supplier S001 (Malaya Agri Oils)")
    
    orchestrator = AgentOrchestrator()
    
    result = orchestrator.execute_workflow(
        workflow_type='risk_assessment',
        input_data={
            'supplier_id': 'S001'
        }
    )
    
    if result['success']:
        risk = result['results']['risk_score']
        
        print(f"\n⚠️  RISK ASSESSMENT:")
        print(f"   Supplier: {risk['supplier_name']}")
        print(f"   Country: {risk['country']}")
        print(f"   Overall Risk Score: {risk['overall_risk_score']:.1f}/100")
        print(f"   Risk Level: {risk['risk_level']}")
        print(f"   {risk['risk_level_description']}")
        
        print(f"\n📊 RISK BREAKDOWN:")
        breakdown = risk['risk_breakdown']
        print(f"   Quality Risk: {breakdown['quality_risk']:.1f}")
        print(f"   Delivery Risk: {breakdown['delivery_risk']:.1f}")
        print(f"   Geopolitical Risk: {breakdown['geopolitical_risk']:.1f}")
        print(f"   Sustainability Risk: {breakdown['sustainability_risk']:.1f}")
        print(f"   Lead Time Risk: {breakdown['lead_time_risk']:.1f}")
        
        if risk['risk_factors']:
            print(f"\n🔍 KEY RISK FACTORS ({len(risk['risk_factors'])}):")
            for factor in risk['risk_factors'][:3]:
                print(f"   • [{factor['severity']}] {factor['description']}")
                print(f"     Impact: {factor['impact']}")


def demo_supplier_comparison():
    """Demo: Compare two suppliers"""
    print_section("DEMO 5: SUPPLIER COMPARISON - S001 vs S002")
    
    orchestrator = AgentOrchestrator()
    
    result = orchestrator.execute_workflow(
        workflow_type='supplier_comparison',
        input_data={
            'supplier_id_1': 'S001',
            'supplier_id_2': 'S002'
        }
    )
    
    if result['success']:
        comparison = result['results']['risk_comparison']
        
        print(f"\n🔄 SUPPLIER COMPARISON:")
        print(f"\n   Supplier 1: {comparison['supplier_1']['name']}")
        print(f"   Risk Score: {comparison['supplier_1']['risk_score']:.1f} ({comparison['supplier_1']['risk_level']})")
        
        print(f"\n   Supplier 2: {comparison['supplier_2']['name']}")
        print(f"   Risk Score: {comparison['supplier_2']['risk_score']:.1f} ({comparison['supplier_2']['risk_level']})")
        
        print(f"\n   Risk Delta: {comparison['risk_delta']:+.1f} points ({comparison['risk_delta_percentage']:+.1f}%)")
        print(f"\n💡 RECOMMENDATION:")
        print(f"   {comparison['recommendation']}")


def main():
    """Run all demos"""
    print("\n" + "="*100)
    print("  🚀 MULTI-AGENT PROCUREMENT INTELLIGENCE SYSTEM - DEMO")
    print("="*100)
    
    try:
        # Demo 1: Comprehensive Analysis
        demo_comprehensive_analysis()
        
        # Demo 2: Rule Evaluation
        demo_rule_evaluation()
        
        # Demo 3: Savings Opportunity
        demo_savings_opportunity()
        
        # Demo 4: Risk Assessment
        demo_risk_assessment()
        
        # Demo 5: Supplier Comparison
        demo_supplier_comparison()
        
        print("\n" + "="*100)
        print("  ✅ ALL DEMOS COMPLETED SUCCESSFULLY")
        print("="*100 + "\n")
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
