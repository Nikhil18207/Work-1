"""Test script for Leadership Brief Generator - Multiple Industries"""

from backend.engines.leadership_brief_generator import LeadershipBriefGenerator
from backend.engines.docx_exporter import DOCXExporter

def test_industry(client_id: str, category: str):
    g = LeadershipBriefGenerator()
    e = DOCXExporter()
    
    print("=" * 70)
    print(f"TESTING: {category.upper()}")
    print("=" * 70)
    
    briefs = g.generate_both_briefs(client_id, category)
    
    ib = briefs['incumbent_concentration_brief']
    
    if 'error' in ib:
        print(f"Error: {ib['error']}")
        return
    
    print(f"Category: {ib['category']}")
    print(f"Total Spend: USD {ib['total_spend']:,.0f}")
    print(f"Dominant Supplier: {ib['current_state']['dominant_supplier']}")
    print(f"Supplier Concentration: {ib['current_state']['spend_share_pct']:.1f}%")
    print(f"Risk Level: {ib['risk_matrix']['overall_risk']} (Score: {ib['risk_matrix']['risk_score']})")
    print(f"Reduction: {ib['supplier_reduction']['dominant_supplier']['formatted_reduction']}")
    print()
    print("Cost Advantages:")
    for ca in ib.get('cost_advantages', [])[:4]:
        driver = ca['driver'][:60] + "..." if len(ca['driver']) > 60 else ca['driver']
        print(f"  {ca['region']}: {driver}")
        print(f"    Savings: USD {ca['min_usd']:,.0f} - {ca['max_usd']:,.0f}")
    
    print()
    print("ROI Projections:")
    roi = ib.get('roi_projections', {})
    print(f"  Annual Savings: USD {roi.get('annual_cost_savings_min', 0):,.0f} - {roi.get('annual_cost_savings_max', 0):,.0f}")
    print(f"  ROI: {roi.get('roi_percentage_min', 0):.0f}% - {roi.get('roi_percentage_max', 0):.0f}%")
    print(f"  3-Year Net Benefit: USD {roi.get('three_year_net_benefit_min', 0):,.0f} - {roi.get('three_year_net_benefit_max', 0):,.0f}")
    
    results = e.export_both_briefs(briefs, export_pdf=True)
    print()
    print("Generated files:")
    for k, v in results.items():
        print(f"  {k}: {v}")
    
    print()
    return results


if __name__ == "__main__":
    test_industry('C001', 'Rice Bran Oil')
    
    print("\n" + "=" * 70)
    print("Testing with Palm Oil...")
    print("=" * 70 + "\n")
    test_industry('C001', 'Palm Oil')
    
    print("\n" + "=" * 70)
    print("Testing with IT Hardware...")
    print("=" * 70 + "\n")
    test_industry('C002', 'IT Hardware')
