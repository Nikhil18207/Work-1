"""
Quick Test Script for Personalized Supplier Coaching System
"""

import sys
from pathlib import Path

root_path = Path(__file__).parent.parent
if str(root_path) not in sys.path:
    sys.path.insert(0, str(root_path))

print("=" * 80)
print("PERSONALIZED SUPPLIER COACHING SYSTEM - QUICK TEST")
print("=" * 80)

try:
    # Test 1: Import all agents
    print("\n1. Testing imports...")
    from backend.agents.supplier_coaching_orchestrator import SupplierCoachingOrchestrator
    print("   ✓ Orchestrator imported")
    
    from backend.agents.recommendations.personalized_coach import PersonalizedCoachAgent
    print("   ✓ Personalized Coach imported")
    
    from backend.agents.incumbent_strategy.enhanced_incumbent_strategy import IncumbentStrategyAgent
    print("   ✓ Incumbent Strategy imported")
    
    from backend.agents.region_sourcing.enhanced_region_sourcing import EnhancedRegionSourcingAgent
    print("   ✓ Region Sourcing imported")
    
    from backend.agents.intelligence.web_scraping_agent import WebScrapingAgent
    print("   ✓ Web Scraping imported")
    
    from backend.engines.parameter_tuning_engine import ParameterTuningEngine
    print("   ✓ Parameter Tuning imported")
    
    # Test 2: Initialize orchestrator
    print("\n2. Initializing orchestrator...")
    orchestrator = SupplierCoachingOrchestrator()
    print("   ✓ Orchestrator initialized with all 5 branches")
    
    # Test 3: Test individual agents
    print("\n3. Testing individual agents...")
    
    # Test Personalized Coach
    coach = PersonalizedCoachAgent()
    print("   ✓ Personalized Coach agent created")
    
    # Test Incumbent Strategy
    incumbent = IncumbentStrategyAgent()
    print("   ✓ Incumbent Strategy agent created")
    
    # Test Region Sourcing
    region = EnhancedRegionSourcingAgent()
    print("   ✓ Region Sourcing agent created")
    
    # Test Web Scraping
    web = WebScrapingAgent()
    print("   ✓ Web Scraping agent created")
    
    # Test Parameter Tuning
    tuning = ParameterTuningEngine()
    print("   ✓ Parameter Tuning engine created")
    
    # Test 4: Verify agent info
    print("\n4. Verifying agent information...")
    agents = [
        orchestrator,
        coach,
        incumbent,
        region,
        web,
        tuning
    ]
    
    for agent in agents:
        info = agent.get_info()
        print(f"   • {info['name']}: {info['description']}")
    
    print("\n" + "=" * 80)
    print("✓ ALL TESTS PASSED")
    print("=" * 80)
    print("\nThe Personalized Supplier Coaching System is ready!")
    print("\nSystem Components:")
    print("  • Branch 1: Data Analysis & Quantification")
    print("  • Branch 2: Personalized Recommendations")
    print("  • Branch 3: Incumbent Supplier Strategy")
    print("  • Branch 4: Additional Region Sourcing")
    print("  • Branch 5: System Architecture (Web Scraping + Parameter Tuning)")
    print("\nTo run a full coaching session:")
    print("  python demos/demo_coaching_system.py")
    
except Exception as e:
    print(f"\n❌ ERROR: {str(e)}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
