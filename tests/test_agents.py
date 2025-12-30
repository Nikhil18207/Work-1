"""
Simple Test: Test individual agents
"""

import sys
from pathlib import Path

root_path = Path(__file__).parent.parent
sys.path.insert(0, str(root_path))

print("="*80)
print("TESTING INDIVIDUAL AGENTS")
print("="*80)

# Test 1: Spend Analyzer
print("\n1. Testing Spend Analyzer...")
from backend.agents.data_analysis.spend_analyzer import SpendAnalyzerAgent

spend_agent = SpendAnalyzerAgent()
result = spend_agent.execute({
    'client_id': 'C001',
    'category': 'Rice Bran Oil'
})

if result['success']:
    print(f"✅ Success!")
    print(f"   Total Spend: {result['data']['total_spend_formatted']}")
    print(f"   Transactions: {result['data']['transaction_count']}")
else:
    print(f"❌ Failed: {result['error']}")

# Test 2: Regional Concentration
print("\n2. Testing Regional Concentration...")
from backend.agents.data_analysis.regional_concentration import RegionalConcentrationAgent

regional_agent = RegionalConcentrationAgent()
result = regional_agent.execute({
    'client_id': 'C001',
    'category': 'Rice Bran Oil'
})

if result['success']:
    print(f"✅ Success!")
    print(f"   Risk Level: {result['data']['risk_level']}")
    print(f"   HHI: {result['data']['herfindahl_index']}")
else:
    print(f"❌ Failed: {result['error']}")

# Test 3: Risk Scoring
print("\n3. Testing Risk Scoring...")
from backend.agents.intelligence.risk_scoring import RiskScoringAgent

risk_agent = RiskScoringAgent()
result = risk_agent.execute({
    'supplier_id': 'S001'
})

if result['success']:
    print(f"✅ Success!")
    print(f"   Supplier: {result['data']['supplier_name']}")
    print(f"   Risk Score: {result['data']['overall_risk_score']:.1f}/100")
    print(f"   Risk Level: {result['data']['risk_level']}")
else:
    print(f"❌ Failed: {result['error']}")

# Test 4: Rule Engine
print("\n4. Testing Rule Engine...")
from backend.agents.intelligence.rule_engine import RuleEngineAgent

rule_agent = RuleEngineAgent()
result = rule_agent.execute({
    'rule_id': 'HC001',
    'client_id': 'C001',
    'category': 'Rice Bran Oil'
})

if result['success']:
    print(f"✅ Success!")
    print(f"   Rule: {result['data']['rule_name']}")
    print(f"   Status: {result['data']['status']}")
    print(f"   Violations: {result['data']['violation_count']}")
else:
    print(f"❌ Failed: {result['error']}")

# Test 5: Savings Calculator
print("\n5. Testing Savings Calculator...")
from backend.agents.recommendations.savings_calculator import SavingsCalculatorAgent

savings_agent = SavingsCalculatorAgent()
result = savings_agent.execute({
    'client_id': 'C001',
    'category': 'Rice Bran Oil',
    'scenario': 'price_negotiation',
    'target_price': 1180
})

if result['success']:
    print(f"✅ Success!")
    print(f"   Current Spend: {result['data']['current_spend_formatted']}")
    print(f"   Potential Savings: {result['data']['potential_savings_formatted']}")
    print(f"   Savings %: {result['data']['savings_percentage']:.1f}%")
else:
    print(f"❌ Failed: {result['error']}")

# Test 6: Orchestrator
print("\n6. Testing Orchestrator...")
from backend.agents.orchestrator import AgentOrchestrator

orchestrator = AgentOrchestrator()
print(f"✅ Orchestrator initialized with {len(orchestrator.agents)} agents")

print("\n" + "="*80)
print("ALL TESTS COMPLETED")
print("="*80)
