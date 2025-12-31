"""
COMPREHENSIVE DATA VERIFICATION
Checks all 6 DOCX briefs against source spend_data.csv
"""
import sys
from pathlib import Path

# Add project root to path (go up one level from scripts/)
root = Path(__file__).parent.parent
sys.path.insert(0, str(root))

import pandas as pd
from backend.engines.data_loader import DataLoader
from backend.engines.leadership_brief_generator import LeadershipBriefGenerator

def verify_category(category: str, client_id: str, df: pd.DataFrame):
    """Verify a single category's brief against source data"""
    
    print(f"\n{'='*70}")
    print(f"VERIFYING: {category}")
    print(f"{'='*70}")
    
    # Filter data for this category
    cat_df = df[(df['Category'] == category) & (df['Client_ID'] == client_id)]
    
    if len(cat_df) == 0:
        print(f"❌ NO DATA FOUND for {category} / {client_id}")
        return False
    
    # Calculate actual metrics from CSV
    actual_total_spend = cat_df['Spend_USD'].sum()
    actual_num_suppliers = cat_df['Supplier_Name'].nunique()
    
    supplier_spend = cat_df.groupby('Supplier_Name')['Spend_USD'].sum().sort_values(ascending=False)
    actual_dominant_supplier = supplier_spend.index[0]
    actual_dominant_spend = supplier_spend.iloc[0]
    actual_dominant_pct = (actual_dominant_spend / actual_total_spend) * 100
    
    country_spend = cat_df.groupby('Supplier_Country')['Spend_USD'].sum().sort_values(ascending=False)
    actual_countries = country_spend.index.tolist()
    actual_top_country = actual_countries[0] if actual_countries else 'N/A'
    actual_top_country_pct = (country_spend.iloc[0] / actual_total_spend) * 100 if len(country_spend) > 0 else 0
    
    print(f"\n📊 SOURCE DATA (spend_data.csv):")
    print(f"   Total Spend: ${actual_total_spend:,.0f}")
    print(f"   Num Suppliers: {actual_num_suppliers}")
    print(f"   Dominant Supplier: {actual_dominant_supplier}")
    print(f"   Dominant %: {actual_dominant_pct:.1f}%")
    print(f"   Top Country: {actual_top_country} ({actual_top_country_pct:.1f}%)")
    print(f"   Suppliers:")
    for supplier, spend in supplier_spend.items():
        pct = (spend / actual_total_spend) * 100
        print(f"      - {supplier}: ${spend:,.0f} ({pct:.1f}%)")
    
    # Generate brief and extract values
    generator = LeadershipBriefGenerator()
    briefs = generator.generate_both_briefs(client_id, category)
    
    incumbent = briefs.get('incumbent_concentration_brief', {})
    regional = briefs.get('regional_concentration_brief', {})
    
    brief_total_spend = incumbent.get('total_spend', 0)
    current_state = incumbent.get('current_state', {})
    brief_dominant_supplier = current_state.get('dominant_supplier', 'N/A')
    brief_dominant_pct = current_state.get('spend_share_pct', 0)
    brief_num_suppliers = current_state.get('num_suppliers', 0)
    
    print(f"\n📄 GENERATED BRIEF DATA:")
    print(f"   Total Spend: ${brief_total_spend:,.0f}")
    print(f"   Num Suppliers: {brief_num_suppliers}")
    print(f"   Dominant Supplier: {brief_dominant_supplier}")
    print(f"   Dominant %: {brief_dominant_pct:.1f}%")
    
    # Compare and report
    print(f"\n✓ VERIFICATION RESULTS:")
    
    all_passed = True
    
    # Check Total Spend
    if abs(brief_total_spend - actual_total_spend) < 1:
        print(f"   ✅ Total Spend: MATCH")
    else:
        print(f"   ❌ Total Spend: MISMATCH (CSV: ${actual_total_spend:,.0f}, Brief: ${brief_total_spend:,.0f})")
        all_passed = False
    
    # Check Dominant Supplier
    if brief_dominant_supplier == actual_dominant_supplier:
        print(f"   ✅ Dominant Supplier: MATCH ({actual_dominant_supplier})")
    else:
        print(f"   ❌ Dominant Supplier: MISMATCH (CSV: {actual_dominant_supplier}, Brief: {brief_dominant_supplier})")
        all_passed = False
    
    # Check Concentration %
    if abs(brief_dominant_pct - actual_dominant_pct) < 0.5:
        print(f"   ✅ Concentration %: MATCH ({actual_dominant_pct:.1f}%)")
    else:
        print(f"   ❌ Concentration %: MISMATCH (CSV: {actual_dominant_pct:.1f}%, Brief: {brief_dominant_pct:.1f}%)")
        all_passed = False
    
    # Check Num Suppliers
    if brief_num_suppliers == actual_num_suppliers:
        print(f"   ✅ Num Suppliers: MATCH ({actual_num_suppliers})")
    else:
        print(f"   ❌ Num Suppliers: MISMATCH (CSV: {actual_num_suppliers}, Brief: {brief_num_suppliers})")
        all_passed = False
    
    # Check Regional Brief
    regional_total = regional.get('total_spend', 0)
    if abs(regional_total - actual_total_spend) < 1:
        print(f"   ✅ Regional Brief Total: MATCH")
    else:
        print(f"   ❌ Regional Brief Total: MISMATCH")
        all_passed = False
    
    return all_passed


def main():
    print("\n" + "="*70)
    print("  COMPREHENSIVE DOCX VERIFICATION")
    print("  Checking all briefs against spend_data.csv")
    print("="*70)
    
    # Load source data
    loader = DataLoader()
    df = loader.load_spend_data()
    
    print(f"\n📁 Loaded spend_data.csv: {len(df)} rows")
    
    # Categories to verify (matching the 6 DOCX files)
    categories_to_check = [
        ('IT Hardware', 'C002'),
        ('Manufacturing Equipment', 'C006'),
        ('Pharmaceuticals', 'C007'),
    ]
    
    results = []
    
    for category, client_id in categories_to_check:
        passed = verify_category(category, client_id, df)
        results.append((category, passed))
    
    # Final Summary
    print("\n" + "="*70)
    print("  FINAL VERIFICATION SUMMARY")
    print("="*70)
    
    all_passed = True
    for category, passed in results:
        status = "✅ ALL CORRECT" if passed else "❌ ISSUES FOUND"
        print(f"   {category}: {status}")
        if not passed:
            all_passed = False
    
    print("="*70)
    if all_passed:
        print("  🎉 ALL 6 DOCX FILES VERIFIED - DATA IS ACCURATE!")
    else:
        print("  ⚠️ SOME ISSUES FOUND - PLEASE REVIEW ABOVE")
    print("="*70 + "\n")


if __name__ == "__main__":
    main()
