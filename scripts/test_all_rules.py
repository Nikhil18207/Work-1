"""
Test script to verify all 35 rules are being evaluated with real data
"""
import sys
from pathlib import Path

# Add project root to path
root = Path(__file__).parent.parent
sys.path.insert(0, str(root))

from backend.engines.rule_evaluation_engine import RuleEvaluationEngine


def test_rules():
    engine = RuleEvaluationEngine()

    print("=" * 80)
    print("TESTING ALL 35 RULES WITH REAL DATA")
    print("=" * 80)

    # Test with Rice Bran Oil
    results = engine.evaluate_all_rules('C001', 'Rice Bran Oil')

    if not results.get('success', False):
        print(f"ERROR: {results.get('error', 'Unknown error')}")
        return

    print(f"\nCategory: Rice Bran Oil")
    print(f"Total Spend: ${results['total_spend']:,.2f}")
    print(f"Supplier Count: {results['supplier_count']}")
    print(f"\nOverall Status: {results['summary']['overall_status']}")
    print(f"Total Rules Evaluated: {results['summary']['total_rules_evaluated']}")
    print(f"  - Violations: {results['summary']['violations_count']}")
    print(f"  - Warnings: {results['summary']['warnings_count']}")
    print(f"  - Compliant: {results['summary']['compliant_count']}")

    # Show Violations
    if results['violations']:
        print("\n" + "=" * 80)
        print("VIOLATIONS:")
        print("=" * 80)
        for v in results['violations']:
            print(f"\n  [{v['rule_id']}] {v['rule_name']}")
            print(f"       Current: {v['current_value']} | Threshold: {v['threshold']}")
            print(f"       Risk Level: {v['risk_level']}")

    # Show Warnings
    if results['warnings']:
        print("\n" + "=" * 80)
        print("WARNINGS:")
        print("=" * 80)
        for w in results['warnings']:
            print(f"  [{w['rule_id']}] {w['rule_name']}: {w['current_value']}")

    # Show Compliant Rules
    if results['compliant']:
        print("\n" + "=" * 80)
        print(f"COMPLIANT RULES ({len(results['compliant'])}):")
        print("=" * 80)
        for c in results['compliant']:
            print(f"  [{c['rule_id']}] {c['rule_name']}: {c['current_value']}")

    # Verify all 35 rules were evaluated
    total = len(results['violations']) + len(results['warnings']) + len(results['compliant'])
    print("\n" + "=" * 80)
    print(f"SUMMARY: {total} out of 35 rules evaluated")
    print("=" * 80)

    if total < 35:
        print(f"\nWARNING: Only {total} rules were evaluated. Some rules may have missing data.")

        # Find which rules are missing
        all_rule_ids = set([f"R{str(i).zfill(3)}" for i in range(1, 36)])
        evaluated_ids = set()
        for r in results['violations'] + results['warnings'] + results['compliant']:
            evaluated_ids.add(r['rule_id'])

        missing = all_rule_ids - evaluated_ids
        if missing:
            print(f"Missing rules: {sorted(missing)}")


if __name__ == "__main__":
    test_rules()
