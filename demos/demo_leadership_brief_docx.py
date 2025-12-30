"""
Demo: Leadership Brief Generation with DOCX Export
Shows how to generate professional leadership briefs and export them as DOCX files
"""

import sys
from pathlib import Path

root_path = Path(__file__).parent.parent
if str(root_path) not in sys.path:
    sys.path.insert(0, str(root_path))

from backend.engines.leadership_brief_generator import LeadershipBriefGenerator
from backend.engines.docx_exporter import DOCXExporter


def demo_brief_generation_and_export():
    """Demonstrate brief generation and DOCX export"""
    
    print("\n" + "=" * 80)
    print("LEADERSHIP BRIEF GENERATION & DOCX EXPORT DEMO")
    print("=" * 80)
    
    # Initialize generators
    brief_generator = LeadershipBriefGenerator()
    docx_exporter = DOCXExporter()
    
    # Test with different categories
    test_cases = [
        ('C001', 'Rice Bran Oil'),
        ('C002', 'IT Hardware'),
        ('C003', 'Cloud Services'),
    ]
    
    results = []
    
    for client_id, category in test_cases:
        print(f"\n{'─' * 80}")
        print(f"Processing: {category} (Client: {client_id})")
        print('─' * 80)
        
        try:
            # Step 1: Generate briefs
            print(f"\n📋 Generating briefs for {category}...")
            briefs = brief_generator.generate_both_briefs(
                client_id=client_id,
                category=category
            )
            
            # Extract key metrics
            incumbent_brief = briefs['incumbent_concentration_brief']
            regional_brief = briefs['regional_concentration_brief']
            
            print(f"   ✅ Incumbent Concentration Brief Generated")
            print(f"      - Total Spend: USD {incumbent_brief['total_spend']:,.0f}")
            print(f"      - Dominant Supplier: {incumbent_brief.get('dominant_supplier', 'N/A')}")
            print(f"      - Concentration: {incumbent_brief.get('dominant_supplier_pct', 0):.0f}%")
            
            print(f"   ✅ Regional Concentration Brief Generated")
            print(f"      - Total Spend: USD {regional_brief['total_spend']:,.0f}")
            print(f"      - Top Regions: {len(regional_brief.get('original_concentration', []))} regions")
            
            # Step 2: Export to DOCX
            print(f"\n📝 Exporting to DOCX format...")
            docx_files = docx_exporter.export_both_briefs(briefs)
            
            print(f"   ✅ DOCX Files Generated Successfully:")
            for brief_type, filepath in docx_files.items():
                filename = Path(filepath).name
                print(f"      • {brief_type}: {filename}")
            
            results.append({
                'category': category,
                'client_id': client_id,
                'status': 'SUCCESS',
                'files': docx_files,
                'spend': incumbent_brief['total_spend']
            })
            
        except Exception as e:
            print(f"   ❌ ERROR: {str(e)}")
            import traceback
            traceback.print_exc()
            results.append({
                'category': category,
                'client_id': client_id,
                'status': 'FAILED',
                'error': str(e)
            })
    
    # Summary
    print(f"\n{'=' * 80}")
    print("SUMMARY")
    print('=' * 80)
    
    successful = sum(1 for r in results if r['status'] == 'SUCCESS')
    failed = sum(1 for r in results if r['status'] == 'FAILED')
    total_spend = sum(r.get('spend', 0) for r in results if r['status'] == 'SUCCESS')
    
    print(f"\n✅ Successful: {successful}/{len(results)}")
    print(f"❌ Failed: {failed}/{len(results)}")
    print(f"💰 Total Spend Analyzed: USD {total_spend:,.0f}")
    
    print(f"\n📊 Results:")
    print(f"{'Category':<20} {'Client':<10} {'Status':<12} {'Total Spend':<15}")
    print("─" * 60)
    
    for result in results:
        status_icon = "✅" if result['status'] == 'SUCCESS' else "❌"
        spend_str = f"USD {result.get('spend', 0):,.0f}" if result['status'] == 'SUCCESS' else "N/A"
        print(f"{result['category']:<20} {result['client_id']:<10} {status_icon} {result['status']:<10} {spend_str:<15}")
    
    print(f"\n📁 All DOCX files saved to: outputs/briefs/")
    
    print(f"\n{'=' * 80}")
    print("✅ DEMO COMPLETE!")
    print("You can now use the generated DOCX files as templates for your reports.")
    print('=' * 80 + "\n")


if __name__ == "__main__":
    demo_brief_generation_and_export()
