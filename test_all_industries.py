"""Test rule violations across ALL industries"""

from backend.engines.leadership_brief_generator import LeadershipBriefGenerator
from backend.engines.docx_exporter import DOCXExporter

g = LeadershipBriefGenerator()
e = DOCXExporter()

industries = [
    ('C001', 'Rice Bran Oil'),
    ('C002', 'IT Hardware'),
    ('C005', 'Raw Materials - Steel'),
    ('C007', 'Pharmaceuticals'),
    ('C009', 'Marketing Services'),
    ('C012', 'Logistics Services'),
]

print('='*70)
print('RULE VIOLATIONS CHECK - ALL INDUSTRIES')
print('='*70)

for client, category in industries:
    b = g.generate_incumbent_concentration_brief(client, category)
    rv = b.get('rule_violations', {})
    
    violations = rv.get('total_violations', 0)
    warnings = rv.get('total_warnings', 0)
    compliance = rv.get('compliance_rate', 0)
    status = rv.get('overall_status', 'N/A')
    
    print(f"\n{category} ({client}):")
    print(f"  Total Spend: ${b.get('total_spend', 0):,.0f}")
    print(f"  Violations: {violations}")
    print(f"  Warnings: {warnings}")
    print(f"  Compliance Rate: {compliance}%")
    print(f"  Status: {status}")
    
    violation_list = rv.get('violations', [])
    if violation_list:
        print("  Rule Violations:")
        for v in violation_list[:3]:
            if isinstance(v, dict):
                print(f"    - {v.get('rule_id')}: {v.get('rule_name')}")

print("\n" + "="*70)
print("GENERATING BRIEFS FOR ALL INDUSTRIES...")
print("="*70)

for client, category in industries:
    briefs = g.generate_both_briefs(client, category)
    results = e.export_both_briefs(briefs)
    print(f"\n{category}: Generated")
    for k, v in results.items():
        print(f"  {k}: {v}")

print("\nDONE!")
