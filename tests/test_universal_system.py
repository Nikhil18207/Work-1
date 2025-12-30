"""
Test Universal System - Works for ANY Category
"""

import sys
from pathlib import Path

root_path = Path(__file__).parent.parent
if str(root_path) not in sys.path:
    sys.path.insert(0, str(root_path))

from backend.engines.leadership_brief_generator import LeadershipBriefGenerator
from backend.engines.docx_exporter import DOCXExporter


def test_category(client_id, category):
    """Test brief generation for any category and export to DOCX"""
    
    print("\n" + "=" * 80)
    print(f"TESTING: {category.upper()}")
    print("=" * 80)
    
    generator = LeadershipBriefGenerator()
    exporter = DOCXExporter()
    
    try:
        # Generate briefs
        briefs = generator.generate_both_briefs(
            client_id=client_id,
            category=category
        )
        
        print(f"\n✅ SUCCESS! Generated briefs for {category}")
        print(f"   Total Spend: USD {briefs['incumbent_concentration_brief']['total_spend']:,.0f}")
        print(f"   Suppliers: {briefs['incumbent_concentration_brief']['num_current_suppliers']}")
        
        # Show regional allocation
        regional = briefs['regional_concentration_brief']
        print(f"\n📊 Regional Allocation:")
        for country, data in list(regional['target_allocation'].items())[:3]:
            print(f"   {country}: {data['pct']}%")
        
        # Export to DOCX
        print(f"\n📝 Exporting to DOCX format...")
        docx_files = exporter.export_both_briefs(briefs)
        
        print(f"\n✅ DOCX Files Generated:")
        for brief_type, filepath in docx_files.items():
            print(f"   {brief_type}: {filepath}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    print("\n" + "=" * 80)
    print("UNIVERSAL SYSTEM TEST - WORKS FOR ANY CATEGORY!")
    print("=" * 80)
    
    # Test multiple categories
    test_cases = [
        ('C001', 'Rice Bran Oil'),
        ('C001', 'Sunflower Oil'),
        ('C001', 'Palm Oil'),
        ('C001', 'Olive Oil'),
    ]
    
    results = []
    for client_id, category in test_cases:
        success = test_category(client_id, category)
        results.append((category, success))
    
    # Summary
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    
    for category, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} - {category}")
    
    total = len(results)
    passed = sum(1 for _, s in results if s)
    
    print(f"\n📊 Results: {passed}/{total} categories passed")
    
    if passed == total:
        print("\n🎉 PERFECT! System works for ALL categories!")
    else:
        print(f"\n⚠️  {total - passed} categories failed")


if __name__ == "__main__":
    main()
