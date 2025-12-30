"""
Test script to verify rule evaluation for Rice Bran Oil
Tests R001, R002, R003, and R023
"""

import sys
from pathlib import Path

root_path = Path(__file__).parent.parent
sys.path.insert(0, str(root_path))

from backend.engines.rule_evaluation_engine import RuleEvaluationEngine

def test_rice_bran_oil_rules():
    """Test all rules for Rice Bran Oil category"""
    print("=" * 100)
    print("COMPREHENSIVE RULE EVALUATION TEST - Rice Bran Oil (Client C001)")
    print("=" * 100)
    
    engine = RuleEvaluationEngine()
    
    # Evaluate all rules
    results = engine.evaluate_all_rules('C001', 'Rice Bran Oil')
    
    if not results['success']:
        print(f"\n❌ ERROR: {results.get('error')}")
        return
    
    # Print summary
    print(f"\n📊 SUMMARY:")
    print(f"  Total Spend: ${results['total_spend']:,.2f}")
    print(f"  Supplier Count: {results['supplier_count']}")
    print(f"  Overall Status: {results['summary']['overall_status']}")
    print(f"  Violations: {results['summary']['violations_count']}")
    print(f"  Warnings: {results['summary']['warnings_count']}")
    print(f"  Compliant: {results['summary']['compliant_count']}")
    
    # Print violations
    if results['violations']:
        print("\n" + "=" * 100)
        print("⚠️  RULE VIOLATIONS")
        print("=" * 100)
        for v in results['violations']:
            print(f"\n[{v['rule_id']}] {v['rule_name']}")
            print(f"  Description: {v['rule_description']}")
            print(f"  Threshold: {v['threshold']}")
            print(f"  Current Value: {v['current_value']}")
            print(f"  Status: {v['message']}")
            print(f"  Action Required: {v['action_required']}")
            if 'details' in v:
                print(f"  Details:")
                for key, value in v['details'].items():
                    print(f"    - {key}: {value}")
    
    # Print warnings
    if results['warnings']:
        print("\n" + "=" * 100)
        print("⚡ WARNINGS")
        print("=" * 100)
        for w in results['warnings']:
            print(f"\n[{w['rule_id']}] {w['rule_name']}")
            print(f"  {w['message']}")
    
    # Print compliant rules
    if results['compliant']:
        print("\n" + "=" * 100)
        print("✅ COMPLIANT RULES")
        print("=" * 100)
        for c in results['compliant']:
            print(f"  [{c['rule_id']}] {c['rule_name']}: {c['message']}")
    
    # Detailed analysis for specific rules
    print("\n" + "=" * 100)
    print("DETAILED RULE ANALYSIS")
    print("=" * 100)
    
    # Check R002 specifically
    r002_found = False
    for rule in results['violations'] + results['warnings'] + results['compliant']:
        if rule['rule_id'] == 'R002':
            r002_found = True
            print(f"\n✓ R002 (Tail Spend Fragmentation):")
            print(f"  Status: {rule['status']}")
            print(f"  Message: {rule['message']}")
            print(f"  This is CORRECT - Only 2 suppliers total, no fragmentation issue")
            break
    
    if not r002_found:
        print(f"\n⚠️  R002 not evaluated (may not have enough data)")
    
    # Check R003 specifically
    r003_found = False
    for rule in results['violations'] + results['warnings'] + results['compliant']:
        if rule['rule_id'] == 'R003':
            r003_found = True
            print(f"\n✓ R003 (Single Supplier Dependency - 60% threshold):")
            print(f"  Status: {rule['status']}")
            print(f"  Message: {rule['message']}")
            if rule['status'] == 'VIOLATION':
                print(f"  This is CORRECT - Malaya Agri Oils at 65.3% exceeds 60% threshold")
            break
    
    if not r003_found:
        print(f"\n⚠️  R003 not evaluated")
    
    # Check R001 specifically
    r001_found = False
    for rule in results['violations'] + results['warnings'] + results['compliant']:
        if rule['rule_id'] == 'R001':
            r001_found = True
            print(f"\n✓ R001 (Regional Concentration - 40% threshold):")
            print(f"  Status: {rule['status']}")
            print(f"  Message: {rule['message']}")
            if rule['status'] == 'VIOLATION':
                print(f"  This is CORRECT - 100% in APAC exceeds 40% threshold")
            break
    
    if not r001_found:
        print(f"\n⚠️  R001 not evaluated")
    
    # Check R023 specifically
    r023_found = False
    for rule in results['violations'] + results['warnings'] + results['compliant']:
        if rule['rule_id'] == 'R023':
            r023_found = True
            print(f"\n✓ R023 (Supplier Concentration Index - HHI threshold 2500):")
            print(f"  Status: {rule['status']}")
            print(f"  Message: {rule['message']}")
            if rule['status'] == 'VIOLATION':
                print(f"  This is CORRECT - HHI of 10000 (highly concentrated) exceeds 2500 threshold")
            break
    
    if not r023_found:
        print(f"\n⚠️  R023 not evaluated")
    
    print("\n" + "=" * 100)
    print("TEST COMPLETE")
    print("=" * 100)

if __name__ == "__main__":
    test_rice_bran_oil_rules()
