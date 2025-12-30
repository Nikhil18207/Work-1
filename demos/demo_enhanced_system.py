"""
COMPREHENSIVE DEMO: Enhanced Supplier Coaching System
Showcases all new features and refinements
"""

import sys
from pathlib import Path
from datetime import datetime
import json

root_path = Path(__file__).parent.parent
if str(root_path) not in sys.path:
    sys.path.insert(0, str(root_path))

from backend.agents.enhanced_supplier_coaching_orchestrator import EnhancedSupplierCoachingOrchestrator
from backend.agents.intelligence.tariff_calculator import TariffCalculatorAgent
from backend.agents.intelligence.leading_questions import LeadingQuestionsModule
from backend.agents.intelligence.cost_risk_loop_engine import CostAndRiskLoopEngine
from backend.agents.intelligence.client_criteria_matching import ClientCriteriaMatchingEngine
from backend.engines.visual_workflow_generator import VisualWorkflowDiagramGenerator


def print_header(title: str, char: str = "="):
    """Print formatted header"""
    print(f"\n{char * 100}")
    print(f"  {title}")
    print(f"{char * 100}\n")


def print_section(title: str):
    """Print formatted section"""
    print(f"\n{'─' * 100}")
    print(f"  {title}")
    print(f"{'─' * 100}\n")


def demo_leading_questions():
    """Demo 1: Leading Questions Module"""
    print_header("🎯 DEMO 1: LEADING QUESTIONS MODULE")
    print("This module intelligently gathers critical information through targeted questions\n")
    
    module = LeadingQuestionsModule()
    
    result = module.execute({
        'existing_data': {},
        'analysis_type': 'tariff_analysis',
        'skip_optional': False
    })
    
    if result['success']:
        data = result['data']
        print(f"✅ Questions Generated: {data['total_questions']}")
        print(f"   Estimated Time: {data['estimated_time_minutes']} minutes\n")
        
        print("Questions by Priority:")
        for priority, questions in data['by_priority'].items():
            if questions:
                print(f"\n  {priority} ({len(questions)} questions):")
                for q in questions[:2]:
                    print(f"    • {q['text']}")
                if len(questions) > 2:
                    print(f"    ... and {len(questions) - 2} more")
    
    print("\n✨ The system adapts questions based on:")
    print("   • Analysis type (tariff, cost comparison, regional sourcing, etc.)")
    print("   • Existing data (skips already-known information)")
    print("   • User preferences (can skip optional questions)")
    print("   • Dependencies (follow-up questions based on answers)")


def demo_tariff_calculator():
    """Demo 2: Tariff Calculator"""
    print_header("💰 DEMO 2: TARIFF CALCULATOR WITH REAL DATA")
    print("Calculates tariff impacts and trade costs for cross-border sourcing\n")
    
    calculator = TariffCalculatorAgent()
    
    result = calculator.execute({
        'from_region': 'Malaysia',
        'to_region': 'India',
        'destination_country': 'USA',
        'product': 'rice_bran_oil',
        'current_price_per_mt': 1000,
        'volume_mt': 1000
    })
    
    if result['success']:
        data = result['data']
        
        print("📊 COST IMPACT ANALYSIS")
        current = data['current_route_impact']
        proposed = data['proposed_route_impact']
        impact = data['cost_impact_analysis']
        
        print(f"\n  Current Route: Malaysia → USA")
        print(f"    Tariff Rate: {current['tariff_rate']}%")
        print(f"    Total Cost: ${current['total_cost']:,.2f}")
        print(f"    Lead Time: {current['lead_time_days']} days")
        
        print(f"\n  Proposed Route: India → USA")
        print(f"    Tariff Rate: {proposed['tariff_rate']}%")
        print(f"    Total Cost: ${proposed['total_cost']:,.2f}")
        print(f"    Lead Time: {proposed['lead_time_days']} days")
        
        print(f"\n  Impact Analysis:")
        print(f"    Cost Delta: ${impact['total_delta']:,.2f} ({impact['total_delta_pct']:+.2f}%)")
        print(f"    Direction: {impact['impact_direction']}")
        
        print(f"\n  3-Year Projection:")
        for proj in data['3year_projection']['projections'][:3]:
            print(f"    Year {proj['year']}: Projected tariff rate {proj['projected_tariff_rate']}% " +
                  f"(${proj['projected_cost_increase']:,.0f} increase)")
        
        print(f"\n  Risk Assessment:")
        print(f"    Risk Score: {data['risk_assessment']['overall_risk_score']}/100")
        print(f"    Risk Level: {data['risk_assessment']['risk_level']}")
        if data['risk_assessment']['identified_risks']:
            print(f"    Identified Risks:")
            for risk in data['risk_assessment']['identified_risks'][:2]:
                print(f"      • {risk['severity']}: {risk['description']}")
        
        print(f"\n  Recommendation: {data['recommendation']}")


def demo_cost_risk_loop():
    """Demo 3: Cost & Risk Loop Optimization"""
    print_header("🔄 DEMO 3: COST & RISK LOOP OPTIMIZATION (Granular Iterations)")
    print("Iteratively refines allocations until constraints are satisfied (up to 50 iterations)\n")
    
    engine = CostAndRiskLoopEngine()
    
    result = engine.execute({
        'initial_allocation': {
            'Supplier_A': 35,
            'Supplier_B': 30,
            'Region_India': 20,
            'Region_Thailand': 15
        },
        'constraints': [
            {'type': 'max_supplier_pct', 'supplier': 'Supplier_A', 'value': 30},
            {'type': 'max_supplier_pct', 'supplier': 'Supplier_B', 'value': 30},
            {'type': 'max_region_pct', 'region': 'India', 'value': 40},
            {'type': 'min_suppliers', 'value': 3}
        ],
        'optimization_target': 'balanced',
        'available_options': [
            {'id': 'Supplier_A', 'cost_per_unit': 1000, 'risk_score': 30},
            {'id': 'Supplier_B', 'cost_per_unit': 950, 'risk_score': 45},
            {'id': 'Region_India', 'cost_per_unit': 980, 'risk_score': 50},
            {'id': 'Region_Thailand', 'cost_per_unit': 1020, 'risk_score': 35},
        ]
    })
    
    if result['success']:
        data = result['data']
        
        print(f"✅ Optimization Complete in {data['total_iterations']} iterations")
        print(f"   Feasible Solutions Found: {data['feasible_solutions_found']}")
        print(f"   Convergence Achieved: {data['convergence_achieved']}\n")
        
        print("📊 ITERATION PROGRESSION:")
        iterations = data['iterations_detail']
        sample_iterations = [iterations[0], iterations[len(iterations)//2], iterations[-1]]
        
        for it in sample_iterations:
            if it:
                print(f"\n  Iteration {it['iteration']}:")
                print(f"    Cost: ${it['cost']:,.0f}")
                print(f"    Risk: {it['risk_score']:.1f}")
                print(f"    Constraints Satisfied: {it['constraint_satisfaction']:.0f}%")
                print(f"    Feasible: {'✅' if it['feasible'] else '❌'}")
        
        print(f"\n📌 OPTIMAL SOLUTION:")
        optimal = data['optimal_solution']
        if optimal:
            print(f"   Allocation: {optimal['allocation']}")
            print(f"   Cost: ${optimal['cost']:,.0f}")
            print(f"   Risk Score: {optimal['risk_score']:.1f}")
            print(f"   Constraint Satisfaction: {optimal['constraint_satisfaction']:.0f}%")
        
        print(f"\n🎯 ALTERNATIVE SOLUTIONS: {len(data['alternative_solutions'])} options available")
        for i, alt in enumerate(data['alternative_solutions'][:2], 1):
            print(f"   Option {i}: Cost ${alt['cost']:,.0f}, Risk {alt['risk_score']:.1f}, " +
                  f"Satisfaction {alt['constraint_satisfaction']:.0f}%")


def demo_criteria_matching():
    """Demo 4: Client Criteria Matching"""
    print_header("🎯 DEMO 4: MULTI-DIMENSIONAL CLIENT CRITERIA MATCHING")
    print("Sophisticated supplier/region evaluation against detailed client criteria\n")
    
    matcher = ClientCriteriaMatchingEngine()
    
    suppliers = [
        {
            'id': 'SUP_001',
            'name': 'Global Rice Solutions',
            'quality_rating': 4.8,
            'delivery_reliability_pct': 96,
            'annual_capacity_mt': 5000,
            'list_price_per_kg': 1.25,
            'certifications': 'ISO 22000, HACCP'
        },
        {
            'id': 'SUP_002',
            'name': 'Asian Oil Trading Co',
            'quality_rating': 4.2,
            'delivery_reliability_pct': 88,
            'annual_capacity_mt': 3000,
            'list_price_per_kg': 1.15,
            'certifications': 'ISO 22000'
        },
        {
            'id': 'SUP_003',
            'name': 'Premium Imports Ltd',
            'quality_rating': 4.9,
            'delivery_reliability_pct': 98,
            'annual_capacity_mt': 8000,
            'list_price_per_kg': 1.45,
            'certifications': 'ISO 22000, HACCP, RSPO'
        }
    ]
    
    result = matcher.execute({
        'entities': suppliers,
        'entity_type': 'supplier',
        'client_criteria': matcher._get_default_criteria(),
        'comparison_mode': 'hybrid'
    })
    
    if result['success']:
        data = result['data']
        
        print(f"📊 EVALUATION RESULTS: {data['total_entities_evaluated']} suppliers evaluated\n")
        
        print("🏆 TOP 3 MATCHES:")
        for score in data['top_3_matches']:
            print(f"\n  #{score['rank']}: {score['entity_name']} - Score: {score['overall_score']}/100")
            print(f"     Strengths: {', '.join(score['strengths'])}")
            print(f"     Weaknesses: {', '.join(score['weaknesses'])}")
            print(f"     Dimension Scores:")
            for dim, score_val in score['dimension_scores'].items():
                print(f"       • {dim.title()}: {score_val}")
        
        print(f"\n📈 SCORING SUMMARY:")
        summary = data['scoring_summary']
        print(f"   Excellent Matches (>80): {summary['excellent_matches']}")
        print(f"   Good Matches (70-80): {summary['good_matches']}")
        print(f"   Average Score: {summary['average_score']}/100")
        
        print(f"\n💡 RECOMMENDATIONS:")
        for rec in data['recommendations'][:3]:
            print(f"   {rec}")


def demo_visual_diagrams():
    """Demo 5: Visual Workflow Diagrams"""
    print_header("📊 DEMO 5: VISUAL WORKFLOW DIAGRAM GENERATION")
    print("Generates visual representations in ASCII and Mermaid formats\n")
    
    generator = VisualWorkflowDiagramGenerator()
    
    result = generator.execute({
        'diagram_type': 'full_system',
        'format': 'ascii',
        'include_decisions': True
    })
    
    if result['success']:
        data = result['data']
        diagrams = data['diagrams']
        
        if 'full_system' in diagrams:
            print("🎨 FULL SYSTEM DIAGRAM (ASCII):")
            print(diagrams['full_system'].get('ascii', ''))
        
        print("\n📋 AVAILABLE DIAGRAM TYPES:")
        print("   • Full System - Complete flow of all 5 branches")
        print("   • Analysis Flow - Data processing pipeline")
        print("   • Decision Tree - Key decision points")
        print("   • Coaching Loop - Iterative optimization process")
        print("\n📁 EXPORT FORMATS:")
        print("   • ASCII - Terminal/document friendly")
        print("   • Mermaid - Online visualization (mermaid.live)")
        print("   • SVG/PNG - High-quality graphics")


def demo_full_coaching_session():
    """Demo 6: Full Enhanced Coaching Session"""
    print_header("🚀 DEMO 6: FULL ENHANCED COACHING SESSION")
    print("End-to-end demonstration with all 5 branches + 4 advanced modules\n")
    
    orchestrator = EnhancedSupplierCoachingOrchestrator()
    
    coaching_input = {
        'client_id': 'DEMO_CLIENT_001',
        'category': 'Rice Bran Oil',
        'coaching_mode': 'full',
        'expansion_volume': 500000,
        'tuning_mode': 'balanced',
        'include_questions': True,
        'include_tariff_analysis': True,
        'include_optimization_loop': True,
        'include_criteria_matching': True,
        'include_diagrams': True
    }
    
    print("⏳ Executing enhanced coaching session with all modules enabled...\n")
    
    result = orchestrator.execute(coaching_input)
    
    if result['success']:
        data = result['data']
        
        print(f"✅ SESSION COMPLETE: {data['session_id']}\n")
        
        print("📊 MODULES EXECUTED:")
        for module, status in data['modules_executed'].items():
            if isinstance(status, dict) and 'success' in status:
                symbol = "✅" if status['success'] else "❌"
                print(f"   {symbol} {module.replace('_', ' ').title()}")
            else:
                print(f"   • {module.replace('_', ' ').title()}")
        
        print(f"\n🌳 BRANCHES EXECUTED:")
        for branch, status in data['branches'].items():
            print(f"   • {branch.replace('_', ' ').title()}")
        
        print(f"\n📈 OVERALL SCORES:")
        scoring = data.get('scoring', {})
        print(f"   Optimization Score: {scoring.get('optimization_score', 'N/A')}/100")
        print(f"   Feasibility Score: {scoring.get('feasibility_score', 'N/A')}/100")
        print(f"   Overall Recommendation: {scoring.get('overall_recommendation_score', 'N/A')}/100")
        
        print(f"\n📋 EXECUTIVE SUMMARY:")
        exec_summary = data.get('executive_summary', {})
        print(f"   Modules Executed: {exec_summary.get('modules_executed', 0)}")
        print(f"   Branches Executed: {exec_summary.get('branches_executed', 0)}")
        for finding in exec_summary.get('key_findings', [])[:3]:
            print(f"   • {finding}")
        
        print(f"\n🎯 ACTION PLAN:")
        action_plan = data.get('action_plan', {})
        print(f"   Total Steps: {action_plan.get('total_steps', 0)}")
        print(f"   Est. Implementation: {action_plan.get('estimated_days_to_implement', 0)} days")
        for i, action in enumerate(action_plan.get('priority_actions', [])[:3], 1):
            print(f"   {i}. {action}")
        
        print(f"\n💾 EXPORT OPTIONS:")
        for format_type, url in data.get('export_formats', {}).items():
            print(f"   • {format_type.upper()}: {url}")


def main():
    """Run all demos"""
    print("\n" + "=" * 100)
    print("  🎯 ENHANCED PERSONALIZED SUPPLIER COACHING SYSTEM - COMPREHENSIVE DEMO")
    print("  All New Features & Refinements Showcased")
    print("=" * 100)
    
    demos = [
        demo_leading_questions,
        demo_tariff_calculator,
        demo_cost_risk_loop,
        demo_criteria_matching,
        demo_visual_diagrams,
        demo_full_coaching_session
    ]
    
    for i, demo_func in enumerate(demos, 1):
        try:
            demo_func()
        except Exception as e:
            print(f"\n❌ Error in demo {i}: {str(e)}")
        
        if i < len(demos):
            input("\n\n📌 Press Enter to continue to next demo...")
    
    print_header("✅ ALL DEMOS COMPLETE!", "=")
    print("""
    🎯 KEY TAKEAWAYS:
    
    1. LEADING QUESTIONS: Intelligently gathers critical information
       → Prioritizes by importance
       → Adapts based on analysis type
       → Identifies critical gaps
    
    2. TARIFF CALCULATOR: Real tariff data + trade analysis
       → Calculates cost impact of region migration
       → 3-year projection of tariff trends
       → Risk assessment for trade routes
    
    3. COST & RISK LOOP: Granular optimization (up to 50 iterations)
       → Finds feasible allocations within constraints
       → Multiple solution options (3-5 alternatives)
       → Convergence detection and fine-tuning
    
    4. CRITERIA MATCHING: Multi-dimensional evaluation
       → 6 evaluation dimensions (quality, cost, reliability, capacity, sustainability, innovation)
       → Comparative analysis across all options
       → Strength/weakness identification
    
    5. VISUAL DIAGRAMS: Multiple formats (ASCII, Mermaid, SVG)
       → Full system architecture visualization
       → Decision tree and workflow diagrams
       → Session-specific flow documentation
    
    6. FULL ORCHESTRATION: End-to-end coaching system
       → All 5 main branches + 4 advanced modules
       → Seamless integration and synthesis
       → Comprehensive reporting and export
    
    ✨ The system is production-ready and optimized for real-world supplier coaching!
    """)


if __name__ == "__main__":
    main()
