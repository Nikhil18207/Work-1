"""
Demo Script for Personalized Supplier Coaching System
Demonstrates all 5 branches working together
"""

import sys
from pathlib import Path
from datetime import datetime
import json

root_path = Path(__file__).parent.parent
if str(root_path) not in sys.path:
    sys.path.insert(0, str(root_path))

from backend.agents.supplier_coaching_orchestrator import SupplierCoachingOrchestrator


def print_section(title: str):
    """Print formatted section header"""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80 + "\n")


def print_subsection(title: str):
    """Print formatted subsection header"""
    print(f"\n--- {title} ---")


def demo_full_coaching_session():
    """Demonstrate full coaching session"""
    print_section("PERSONALIZED SUPPLIER COACHING SYSTEM - FULL DEMO")
    
    # Initialize orchestrator
    print("Initializing Supplier Coaching Orchestrator...")
    orchestrator = SupplierCoachingOrchestrator()
    print("✓ Orchestrator initialized with all 5 branches\n")
    
    # Prepare input
    coaching_input = {
        'client_id': 'CLIENT_001',
        'category': 'Rice Bran Oil',
        'coaching_mode': 'full',
        'expansion_volume': 500000,  # $500k additional spend
        'tuning_mode': 'balanced',
        'focus_areas': ['concentration', 'quality', 'diversification']
    }
    
    print("Coaching Request:")
    print(f"  Client: {coaching_input['client_id']}")
    print(f"  Category: {coaching_input['category']}")
    print(f"  Mode: {coaching_input['coaching_mode']}")
    print(f"  Expansion Volume: ${coaching_input['expansion_volume']:,}")
    print(f"  Tuning Mode: {coaching_input['tuning_mode']}")
    
    # Execute coaching
    print("\n🚀 Starting comprehensive coaching analysis...\n")
    result = orchestrator.execute(coaching_input)
    
    if not result['success']:
        print(f"❌ Error: {result['error']}")
        return
    
    data = result['data']
    
    # Display Executive Summary
    print_section("EXECUTIVE SUMMARY")
    exec_summary = data['executive_summary']
    
    print(f"Session ID: {exec_summary['session_id']}")
    print(f"Timestamp: {exec_summary['timestamp']}")
    print(f"Client: {exec_summary['client_id']}")
    print(f"Category: {exec_summary['category']}")
    
    print_subsection("Current State")
    current_state = exec_summary['current_state']
    print(f"  Total Spend: {current_state['total_spend_formatted']}")
    print(f"  Active Suppliers: {current_state['supplier_count']}")
    print(f"  Geographic Regions: {current_state['region_count']}")
    print(f"  Overall Risk Level: {current_state['risk_level']}")
    
    print_subsection("Key Issues")
    key_issues = exec_summary['key_issues']
    print(f"  Violations: {key_issues['violations']}")
    print(f"  Warnings: {key_issues['warnings']}")
    print(f"\n  Critical Areas:")
    for i, area in enumerate(key_issues['critical_areas'][:3], 1):
        print(f"    {i}. {area}")
    
    print_subsection("Opportunities Identified")
    opportunities = exec_summary['opportunities']
    print(f"  Incumbent Expansion Opportunities: {opportunities['incumbent_expansion']}")
    print(f"  New Regions Identified: {opportunities['new_regions']}")
    print(f"  Total Recommendations: {opportunities['total_recommendations']}")
    
    print_subsection("Market Intelligence")
    market_intel = exec_summary['market_intelligence']
    if market_intel.get('available'):
        print(f"  Key Insights: {market_intel['key_insights_count']}")
        print(f"  Opportunities: {market_intel['opportunities_count']}")
        print(f"  Threats: {market_intel['threats_count']}")
        print(f"\n  Top Insights:")
        for i, insight in enumerate(market_intel.get('top_insights', []), 1):
            print(f"    {i}. {insight}")
    else:
        print("  Market intelligence not available")
    
    print_subsection("Immediate Actions Required")
    for i, action in enumerate(exec_summary['immediate_actions'][:5], 1):
        print(f"\n  {i}. [{action['priority']}] {action['action']}")
        print(f"     Timeline: {action['timeline']}")
        print(f"     {action['description']}")
    
    # Display Branch Results
    print_section("BRANCH 1: DATA ANALYSIS & QUANTIFICATION")
    
    data_analysis = data['branches']['data_analysis']
    quant_summary = data_analysis['quantification_summary']
    
    print("Quantification Metrics:")
    print(f"  Total Spend: ${quant_summary['total_spend']:,.2f}")
    print(f"  Supplier Count: {quant_summary['supplier_count']}")
    print(f"  Region Count: {quant_summary['region_count']}")
    print(f"  Violations: {quant_summary['violation_count']}")
    print(f"  Warnings: {quant_summary['warning_count']}")
    print(f"  Risk Level: {quant_summary['risk_level']}")
    
    # Threshold Tracking Details
    threshold_data = data_analysis['components'].get('threshold_tracking', {})
    if threshold_data:
        print_subsection("Threshold Violations")
        for i, violation in enumerate(threshold_data.get('violations', [])[:3], 1):
            print(f"\n  {i}. {violation.get('rule', 'Unknown')}")
            print(f"     {violation.get('message', '')}")
            if violation.get('action_required'):
                print(f"     Action: {violation['action_required']}")
    
    # Regional Concentration
    regional_data = data_analysis['components'].get('regional_concentration', {})
    if regional_data:
        print_subsection("Regional Concentration")
        print(f"  Concentration Risk: {regional_data.get('concentration_risk', 'Unknown')}")
        for region in regional_data.get('regional_breakdown', [])[:3]:
            print(f"  • {region.get('region', 'Unknown')}: {region.get('percentage', 0):.1f}% ({region.get('supplier_count', 0)} suppliers)")
    
    # Display Branch 2: Personalized Recommendations
    print_section("BRANCH 2: PERSONALIZED RECOMMENDATIONS")
    
    recommendations_branch = data['branches']['personalized_recommendations']
    recommendations = recommendations_branch.get('personalized_recommendations', [])
    
    print(f"Total Recommendations: {len(recommendations)}\n")
    
    for i, rec in enumerate(recommendations[:5], 1):
        print(f"{i}. [{rec['priority']}] {rec['title']}")
        print(f"   Category: {rec['category']}")
        print(f"   Current: {rec['current_situation']}")
        print(f"   Target: {rec['target_state']}")
        print(f"   Expected Outcome: {rec['expected_outcome']}")
        
        if rec.get('specific_actions'):
            print(f"   Action Steps:")
            for step in rec['specific_actions'][:3]:
                print(f"     Step {step['step']}: {step['action']} ({step['timeline']})")
        print()
    
    # Implementation Roadmap
    roadmap = recommendations_branch.get('implementation_roadmap', {})
    if roadmap:
        print_subsection("Implementation Roadmap")
        for phase_name, phase_data in roadmap.items():
            if isinstance(phase_data, dict):
                print(f"\n  {phase_name.replace('_', ' ').title()}")
                print(f"    Timeline: {phase_data.get('timeline', 'N/A')}")
                print(f"    Focus: {phase_data.get('focus', 'N/A')}")
                print(f"    Recommendations: {len(phase_data.get('recommendations', []))}")
    
    # Display Branch 3: Incumbent Supplier Strategy
    print_section("BRANCH 3: INCUMBENT SUPPLIER STRATEGY")
    
    incumbent_branch = data['branches'].get('incumbent_strategy', {})
    if incumbent_branch:
        screening_summary = incumbent_branch.get('screening_summary', {})
        print("Screening Summary:")
        print(f"  Total Incumbents: {screening_summary.get('total_incumbents', 0)}")
        print(f"  Qualified for Expansion: {screening_summary.get('qualified_for_expansion', 0)}")
        print(f"  High Potential: {screening_summary.get('high_potential', 0)}")
        print(f"  Disqualified: {screening_summary.get('disqualified', 0)}")
        
        expansion_opps = incumbent_branch.get('expansion_opportunities', [])
        if expansion_opps:
            print_subsection("Top Expansion Opportunities")
            for i, opp in enumerate(expansion_opps[:3], 1):
                print(f"\n  {i}. {opp['supplier_name']} [{opp['priority']}]")
                print(f"     Current Spend: ${opp['current_relationship']['spend']:,.2f} ({opp['current_relationship']['percentage']:.1f}%)")
                print(f"     Recommended Additional: ${opp['expansion_potential']['recommended_additional_spend']:,.2f}")
                print(f"     Quality: {opp['current_relationship']['quality_rating']}/5.0")
                print(f"     Risk Level: {opp['risk_profile']['risk_level']}")
    
    # Display Branch 4: Additional Region Sourcing
    print_section("BRANCH 4: ADDITIONAL REGION SOURCING")
    
    region_branch = data['branches'].get('region_sourcing', {})
    if region_branch:
        new_regions = region_branch.get('new_regions', [])
        print(f"New Regions Identified: {len(new_regions)}\n")
        
        for i, region in enumerate(new_regions[:3], 1):
            print(f"{i}. {region['region']} [Score: {region['region_score']}/100]")
            print(f"   Suppliers: {region['supplier_count']}")
            print(f"   Capacity: {region['total_capacity_mt']:,.0f} MT")
            print(f"   Avg Quality: {region['avg_quality_rating']}/5.0")
            print(f"   Avg Price: ${region['avg_price_per_kg']:.2f}/kg")
            print(f"   Risk Level: {region['risk_assessment']['overall_risk']}")
            print(f"   Recommended: {'Yes' if region['recommended'] else 'No'}")
            print()
    
    # Display Branch 5: System Architecture
    print_section("BRANCH 5: SYSTEM ARCHITECTURE")
    
    system_arch = data['branches']['system_architecture']
    
    # Parameter Tuning
    tuning_data = system_arch['components'].get('parameter_tuning', {})
    if tuning_data:
        print_subsection("Parameter Tuning")
        print(f"  Tuning Mode: {tuning_data.get('tuning_mode', 'Unknown')}")
        
        tuned_params = tuning_data.get('tuned_parameters', {})
        default_params = tuning_data.get('default_parameters', {})
        
        print(f"\n  Key Parameter Adjustments:")
        for param, tuned_value in list(tuned_params.items())[:5]:
            default_value = default_params.get(param, 'N/A')
            if tuned_value != default_value:
                print(f"    • {param}: {default_value} → {tuned_value}")
    
    # Web Scraping Intelligence
    web_data = system_arch['components'].get('web_scraping', {})
    if web_data:
        print_subsection("Real-time Market Intelligence")
        
        pricing_data = web_data.get('pricing_data', {})
        if pricing_data:
            current_price = pricing_data.get('current_price', {})
            trend = pricing_data.get('price_trend', {})
            print(f"\n  Current Price: ${current_price.get('value', 0):.2f}/{current_price.get('unit', 'kg')}")
            print(f"  7-Day Change: {trend.get('7d_change_pct', 0):+.2f}%")
            print(f"  30-Day Change: {trend.get('30d_change_pct', 0):+.2f}%")
        
        news_data = web_data.get('news_data', {})
        if news_data:
            print(f"\n  Recent News Items: {news_data.get('news_count', 0)}")
            print(f"  High Relevance: {news_data.get('high_relevance_count', 0)}")
            
            sentiment = news_data.get('sentiment_summary', {})
            print(f"  Sentiment: {sentiment.get('overall_sentiment', 'Unknown')}")
            print(f"    Positive: {sentiment.get('positive', 0)}, Neutral: {sentiment.get('neutral', 0)}, Negative: {sentiment.get('negative', 0)}")
    
    # Display Overall Scores
    print_section("OVERALL PERFORMANCE SCORES")
    
    scoring = data['scoring']
    print(f"Current Health Score: {scoring['current_health_score']}/100")
    print(f"Projected Health Score: {scoring['projected_health_score']}/100")
    print(f"Improvement Potential: +{scoring['improvement_potential']} points")
    
    print("\nScore Breakdown:")
    for component, score in scoring['breakdown'].items():
        print(f"  • {component.replace('_', ' ').title()}: {score} points")
    
    # Action Plan Summary
    print_section("ACTION PLAN SUMMARY")
    
    action_plan = data['action_plan']
    print(f"Total Actions: {action_plan['total_actions']}")
    print(f"Estimated Duration: {action_plan['estimated_duration']}")
    
    print("\nPhased Approach:")
    for phase_name, phase_data in action_plan.get('phases', {}).items():
        if isinstance(phase_data, dict):
            print(f"\n  {phase_name.replace('_', ' ').title()}")
            print(f"    Timeline: {phase_data.get('timeline', 'N/A')}")
            print(f"    Focus: {phase_data.get('focus', 'N/A')}")
            milestones = phase_data.get('key_milestones', [])
            if milestones:
                print(f"    Key Milestones:")
                for milestone in milestones[:3]:
                    print(f"      - {milestone}")
    
    # Save results to file
    print_section("SAVING RESULTS")
    
    output_dir = Path(__file__).parent.parent / 'outputs'
    output_dir.mkdir(exist_ok=True)
    
    output_file = output_dir / f"coaching_session_{data['session_id']}.json"
    
    with open(output_file, 'w') as f:
        json.dump(data, f, indent=2, default=str)
    
    print(f"✓ Full results saved to: {output_file}")
    
    print_section("DEMO COMPLETE")
    print("✓ All 5 branches executed successfully")
    print("✓ Comprehensive coaching analysis complete")
    print("✓ Personalized recommendations generated")
    print("✓ Implementation roadmap created")
    print("\nThe Personalized Supplier Coaching System is ready for production use!")


if __name__ == "__main__":
    try:
        demo_full_coaching_session()
    except Exception as e:
        print(f"\n❌ Error during demo: {str(e)}")
        import traceback
        traceback.print_exc()
