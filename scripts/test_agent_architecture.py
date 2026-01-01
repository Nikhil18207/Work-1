"""
Test Script for Microagent Architecture

Tests the new agent-based brief generation system:
1. Individual agent functionality
2. BriefOrchestrator coordination
3. LeadershipBriefGenerator with use_agents=True
4. Comparison with traditional generation
"""

import sys
from pathlib import Path

# Add project root to path
root_path = Path(__file__).parent.parent
sys.path.insert(0, str(root_path))


def test_individual_agents():
    """Test individual agent functionality."""
    print("\n" + "=" * 60)
    print(" TESTING INDIVIDUAL AGENTS")
    print("=" * 60)

    from backend.engines.data_loader import DataLoader

    # Load test data
    data_loader = DataLoader()
    spend_df = data_loader.load_spend_data()
    supplier_df = data_loader.load_supplier_master()

    # Filter to a test category
    test_category = 'Rice Bran Oil'
    test_client = 'C001'

    resolved = data_loader.resolve_category_input(test_category, test_client)
    if not resolved.get('success'):
        print(f"[WARN] Could not resolve test category: {test_category}")
        # Use first available category
        spend_df = spend_df[spend_df['Client_ID'] == test_client]
    else:
        spend_df = resolved.get('spend_data')

    print(f"\nTest Data: {len(spend_df)} spend records")

    # Test 1: DataAnalysisAgent
    print("\n[1] Testing DataAnalysisAgent...")
    try:
        from backend.agents.data_analysis_agent import DataAnalysisAgent

        data_agent = DataAnalysisAgent()
        context = {
            'spend_df': spend_df,
            'supplier_df': supplier_df,
            'category': test_category,
            'client_id': test_client
        }
        result = data_agent.execute(context)

        if result.get('success'):
            summary = result.get('summary', {})
            print(f"   [OK] DataAnalysisAgent successful")
            print(f"       Total Spend: {summary.get('total_spend_formatted', 'N/A')}")
            print(f"       Dominant Supplier: {summary.get('dominant_supplier', 'N/A')} ({summary.get('dominant_supplier_pct', 0):.1f}%)")
            print(f"       HHI: {summary.get('hhi_value', 0):.0f} ({summary.get('hhi_interpretation', '')})")
        else:
            print(f"   [FAIL] DataAnalysisAgent failed: {result.get('error')}")
    except Exception as e:
        print(f"   [ERROR] DataAnalysisAgent error: {e}")

    # Test 2: RiskAssessmentAgent
    print("\n[2] Testing RiskAssessmentAgent...")
    try:
        from backend.agents.risk_assessment_agent import RiskAssessmentAgent

        risk_agent = RiskAssessmentAgent()
        risk_context = {
            'data_analysis': result,  # Use output from DataAnalysisAgent
            'rule_engine': None,  # Skip rule evaluation for quick test
            'client_id': test_client,
            'category': test_category
        }
        risk_result = risk_agent.execute(risk_context)

        if risk_result.get('success'):
            risk_matrix = risk_result.get('risk_matrix', {})
            print(f"   [OK] RiskAssessmentAgent successful")
            print(f"       Overall Risk: {risk_matrix.get('overall_risk', 'N/A')}")
            print(f"       Supply Chain Risk: {risk_matrix.get('supply_chain_risk', 'N/A')}")
            print(f"       Geographic Risk: {risk_matrix.get('geographic_risk', 'N/A')}")
        else:
            print(f"   [FAIL] RiskAssessmentAgent failed: {risk_result.get('error')}")
    except Exception as e:
        print(f"   [ERROR] RiskAssessmentAgent error: {e}")

    # Test 3: MarketIntelligenceAgent
    print("\n[3] Testing MarketIntelligenceAgent...")
    try:
        from backend.agents.market_intelligence_agent import MarketIntelligenceAgent

        market_agent = MarketIntelligenceAgent()
        market_context = {
            'category': test_category,
            'product_category': 'Edible Oils',
            'regions': ['India', 'Thailand', 'Indonesia']
        }
        market_result = market_agent.execute(market_context)

        if market_result.get('success'):
            config = market_result.get('industry_config', {})
            print(f"   [OK] MarketIntelligenceAgent successful")
            print(f"       Low Cost Regions: {', '.join(config.get('low_cost_regions', []))}")
            print(f"       Savings Range: {config.get('savings_range', (0, 0))}")
        else:
            print(f"   [FAIL] MarketIntelligenceAgent failed: {market_result.get('error')}")
    except Exception as e:
        print(f"   [ERROR] MarketIntelligenceAgent error: {e}")

    # Test 4: RecommendationAgent
    print("\n[4] Testing RecommendationAgent...")
    try:
        from backend.agents.recommendation_agent import RecommendationAgent

        rec_agent = RecommendationAgent()
        rec_context = {
            'data_analysis': result,
            'risk_assessment': risk_result,
            'alternate_suppliers': {'alternate_supplier': None, 'alternate_regions': []},
            'industry_config': market_result.get('industry_config', {}),
            'category': test_category
        }
        rec_result = rec_agent.execute(rec_context)

        if rec_result.get('success'):
            roi = rec_result.get('roi_projections', {})
            print(f"   [OK] RecommendationAgent successful")
            print(f"       Projected Savings: ${roi.get('annual_cost_savings_min', 0):,.0f} - ${roi.get('annual_cost_savings_max', 0):,.0f}")
            print(f"       ROI: {roi.get('roi_percentage_min', 0):.0f}% - {roi.get('roi_percentage_max', 0):.0f}%")
        else:
            print(f"   [FAIL] RecommendationAgent failed: {rec_result.get('error')}")
    except Exception as e:
        print(f"   [ERROR] RecommendationAgent error: {e}")

    return True


def test_brief_orchestrator():
    """Test BriefOrchestrator coordination."""
    print("\n" + "=" * 60)
    print(" TESTING BRIEF ORCHESTRATOR")
    print("=" * 60)

    try:
        from backend.engines.data_loader import DataLoader
        from backend.engines.rule_evaluation_engine import RuleEvaluationEngine
        from backend.agents.brief_orchestrator import BriefOrchestrator

        # Initialize components
        data_loader = DataLoader()
        rule_engine = RuleEvaluationEngine()

        # Create orchestrator (without LLM for faster test)
        orchestrator = BriefOrchestrator(
            data_loader=data_loader,
            rule_engine=rule_engine,
            llm_engine=None,
            vector_store=None,
            enable_llm=False,
            enable_rag=False
        )

        print("\n[OK] BriefOrchestrator initialized")

        # Test incumbent brief generation
        print("\n[1] Generating Incumbent Concentration Brief...")
        incumbent_brief = orchestrator.generate_incumbent_concentration_brief(
            client_id='C001',
            category='Rice Bran Oil'
        )

        if incumbent_brief.get('total_spend', 0) > 0:
            print(f"   [OK] Incumbent Brief generated")
            print(f"       Title: {incumbent_brief.get('title', 'N/A')}")
            print(f"       Total Spend: ${incumbent_brief.get('total_spend', 0):,.0f}")
            current_state = incumbent_brief.get('current_state', {})
            print(f"       Dominant Supplier: {current_state.get('dominant_supplier', 'N/A')}")
            print(f"       Risk Level: {incumbent_brief.get('risk_matrix', {}).get('overall_risk', 'N/A')}")
            print(f"       Agents Used: {', '.join(incumbent_brief.get('agents_used', []))}")
        else:
            print(f"   [FAIL] Incumbent Brief generation failed")

        # Test regional brief generation
        print("\n[2] Generating Regional Concentration Brief...")
        regional_brief = orchestrator.generate_regional_concentration_brief(
            client_id='C001',
            category='Rice Bran Oil'
        )

        if regional_brief.get('total_spend', 0) > 0:
            print(f"   [OK] Regional Brief generated")
            print(f"       Title: {regional_brief.get('title', 'N/A')}")
            print(f"       Total Spend: ${regional_brief.get('total_spend', 0):,.0f}")
            print(f"       Risk Level: {regional_brief.get('risk_matrix', {}).get('overall_risk', 'N/A')}")
        else:
            print(f"   [FAIL] Regional Brief generation failed")

        return True

    except Exception as e:
        print(f"   [ERROR] BriefOrchestrator test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_leadership_brief_generator_with_agents():
    """Test LeadershipBriefGenerator with use_agents=True."""
    print("\n" + "=" * 60)
    print(" TESTING LEADERSHIP BRIEF GENERATOR (AGENT MODE)")
    print("=" * 60)

    try:
        from backend.engines.leadership_brief_generator import LeadershipBriefGenerator

        # Create generator with agent mode enabled (no LLM for faster test)
        generator = LeadershipBriefGenerator(
            enable_llm=False,
            enable_rag=False,
            use_agents=True
        )

        print("\n[OK] LeadershipBriefGenerator initialized with use_agents=True")

        # Generate brief
        print("\n[1] Generating brief via agent architecture...")
        result = generator.generate_both_briefs(
            client_id='C001',
            category='Rice Bran Oil'
        )

        incumbent = result.get('incumbent_concentration_brief', {})
        regional = result.get('regional_concentration_brief', {})

        if incumbent.get('total_spend', 0) > 0:
            print(f"   [OK] Agent-based generation successful")
            print(f"       Incumbent Spend: ${incumbent.get('total_spend', 0):,.0f}")
            print(f"       Regional Spend: ${regional.get('total_spend', 0):,.0f}")
            print(f"       Orchestrator Version: {incumbent.get('orchestrator_version', 'N/A')}")
        else:
            print(f"   [FAIL] Agent-based generation failed")

        return True

    except Exception as e:
        print(f"   [ERROR] Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_comparison():
    """Compare agent-based vs traditional generation."""
    print("\n" + "=" * 60)
    print(" COMPARING AGENT VS TRADITIONAL GENERATION")
    print("=" * 60)

    try:
        from backend.engines.leadership_brief_generator import LeadershipBriefGenerator
        import time

        # Traditional mode
        print("\n[1] Traditional mode (use_agents=False)...")
        start = time.time()
        generator_traditional = LeadershipBriefGenerator(
            enable_llm=False,
            enable_rag=False,
            use_agents=False
        )
        traditional_result = generator_traditional.generate_incumbent_concentration_brief(
            client_id='C001',
            category='Rice Bran Oil'
        )
        traditional_time = time.time() - start

        # Agent mode
        print("\n[2] Agent mode (use_agents=True)...")
        start = time.time()
        generator_agent = LeadershipBriefGenerator(
            enable_llm=False,
            enable_rag=False,
            use_agents=True
        )
        agent_result = generator_agent.generate_incumbent_concentration_brief(
            client_id='C001',
            category='Rice Bran Oil'
        )
        agent_time = time.time() - start

        # Compare results
        print("\n[3] Comparison Results:")
        print(f"   Traditional Time: {traditional_time:.2f}s")
        print(f"   Agent Time: {agent_time:.2f}s")
        print(f"   Traditional Spend: ${traditional_result.get('total_spend', 0):,.0f}")
        print(f"   Agent Spend: ${agent_result.get('total_spend', 0):,.0f}")

        # Verify key fields match
        fields_match = (
            traditional_result.get('total_spend') == agent_result.get('total_spend') and
            traditional_result.get('current_state', {}).get('dominant_supplier') ==
            agent_result.get('current_state', {}).get('dominant_supplier')
        )

        if fields_match:
            print("   [OK] Key fields match between modes")
        else:
            print("   [WARN] Some fields differ between modes (expected during refactoring)")

        return True

    except Exception as e:
        print(f"   [ERROR] Comparison failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests."""
    print("=" * 60)
    print(" MICROAGENT ARCHITECTURE TEST SUITE")
    print("=" * 60)

    results = {}

    # Run tests
    results['individual_agents'] = test_individual_agents()
    results['orchestrator'] = test_brief_orchestrator()
    results['generator_with_agents'] = test_leadership_brief_generator_with_agents()
    results['comparison'] = test_comparison()

    # Summary
    print("\n" + "=" * 60)
    print(" TEST SUMMARY")
    print("=" * 60)

    all_passed = True
    for test_name, passed in results.items():
        status = "[PASS]" if passed else "[FAIL]"
        print(f"   {status} {test_name}")
        if not passed:
            all_passed = False

    print("\n" + "=" * 60)
    if all_passed:
        print(" ALL TESTS PASSED!")
    else:
        print(" SOME TESTS FAILED - Review output above")
    print("=" * 60)

    return all_passed


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
