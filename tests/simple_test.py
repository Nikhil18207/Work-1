import sys
from pathlib import Path

root_path = Path(__file__).parent.parent
sys.path.insert(0, str(root_path))

from backend.engines.rule_evaluation_engine import RuleEvaluationEngine

engine = RuleEvaluationEngine()
results = engine.evaluate_all_rules('C001', 'Rice Bran Oil')

print("RULE EVALUATION RESULTS")
print("=" * 60)
print(f"Total Spend: ${results['total_spend']:,.2f}")
print(f"Suppliers: {results['supplier_count']}")
print(f"Status: {results['summary']['overall_status']}")
print(f"\nViolations: {results['summary']['violations_count']}")
print(f"Warnings: {results['summary']['warnings_count']}")
print(f"Compliant: {results['summary']['compliant_count']}")

print("\n" + "=" * 60)
print("VIOLATED RULES:")
print("=" * 60)
for v in results['violations']:
    print(f"{v['rule_id']}: {v['rule_name']}")
    print(f"  Current: {v['current_value']} | Threshold: {v['threshold']}")

print("\n" + "=" * 60)
print("COMPLIANT RULES:")
print("=" * 60)
for c in results['compliant']:
    print(f"{c['rule_id']}: {c['rule_name']}")
    print(f"  Current: {c['current_value']} | Threshold: {c['threshold']}")
