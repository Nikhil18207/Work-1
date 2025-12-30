import pandas as pd

print("=" * 80)
print("VERIFYING R001 RULE DATA FOR C001 - Rice Bran Oil")
print("=" * 80)

# Load spend data
df = pd.read_csv('data/structured/spend_data.csv')

# Filter for C001 and Rice Bran Oil
c001_rbo = df[(df['Client_ID'] == 'C001') & (df['Category'] == 'Rice Bran Oil')]

print("\n=== RAW DATA ===")
print(c001_rbo[['Client_ID', 'Category', 'Supplier_Name', 'Supplier_Region', 'Spend_USD']])

print("\n=== TOTAL SPEND ===")
total_spend = c001_rbo['Spend_USD'].sum()
print(f"Total Spend: ${total_spend:,.2f}")

print("\n=== SUPPLIER CONCENTRATION ===")
supplier_breakdown = c001_rbo.groupby('Supplier_Name')['Spend_USD'].sum().sort_values(ascending=False)

for supplier, spend in supplier_breakdown.items():
    pct = (spend / total_spend * 100)
    status = "✓ OK" if pct <= 30 else "❌ VIOLATION"
    print(f"{supplier}:")
    print(f"  Spend: ${spend:,.2f}")
    print(f"  Percentage: {pct:.1f}%")
    print(f"  Status: {status} (30% threshold)")
    if pct > 30:
        excess = pct - 30
        excess_amount = (excess / 100) * total_spend
        print(f"  Excess: {excess:.1f}% (${excess_amount:,.2f})")
    print()

print("=" * 80)
print("R001 RULE: Regional Concentration")
print("=" * 80)

# Load rule book
try:
    rules_df = pd.read_csv('data/structured/rule_book.csv')
    r001 = rules_df[rules_df['Rule_ID'] == 'R001']
    if not r001.empty:
        print("\nRule Definition:")
        print(f"  Rule ID: {r001.iloc[0]['Rule_ID']}")
        print(f"  Rule Name: {r001.iloc[0]['Rule_Name']}")
        print(f"  Threshold: {r001.iloc[0]['Threshold_Value']}")
        print(f"  Description: {r001.iloc[0].get('Description', 'N/A')}")
except Exception as e:
    print(f"Could not load rule book: {e}")

print("\n=== REGIONAL CONCENTRATION ===")
region_breakdown = c001_rbo.groupby('Supplier_Region')['Spend_USD'].sum().sort_values(ascending=False)

for region, spend in region_breakdown.items():
    pct = (spend / total_spend * 100)
    print(f"{region}:")
    print(f"  Spend: ${spend:,.2f}")
    print(f"  Percentage: {pct:.1f}%")
    print()

print("=" * 80)
print("VERIFICATION COMPLETE")
print("=" * 80)
