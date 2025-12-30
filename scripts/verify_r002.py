import pandas as pd

print("=" * 80)
print("VERIFYING R002 RULE DATA FOR C001")
print("=" * 80)

# Load spend data
df = pd.read_csv('data/structured/spend_data.csv')

# Filter for C001
c001_data = df[df['Client_ID'] == 'C001']

print("\n=== CLIENT C001 - ALL CATEGORIES ===")
print(f"Total Spend: ${c001_data['Spend_USD'].sum():,.2f}")
print(f"Total Transactions: {len(c001_data)}")

# Category breakdown
print("\n=== CATEGORY BREAKDOWN ===")
category_breakdown = c001_data.groupby('Category').agg({
    'Spend_USD': ['sum', 'count']
}).reset_index()
category_breakdown.columns = ['Category', 'Total_Spend', 'Transaction_Count']
category_breakdown['Percentage'] = (category_breakdown['Total_Spend'] / c001_data['Spend_USD'].sum() * 100).round(2)
category_breakdown = category_breakdown.sort_values('Total_Spend', ascending=False)

for _, row in category_breakdown.iterrows():
    print(f"\n{row['Category']}:")
    print(f"  Spend: ${row['Total_Spend']:,.2f}")
    print(f"  Percentage: {row['Percentage']:.2f}%")
    print(f"  Transactions: {row['Transaction_Count']}")

# Load rule book
print("\n" + "=" * 80)
print("R002 RULE DEFINITION")
print("=" * 80)

try:
    rules_df = pd.read_csv('data/structured/rule_book.csv')
    r002 = rules_df[rules_df['Rule_ID'] == 'R002']
    if not r002.empty:
        print(f"\nRule ID: {r002.iloc[0]['Rule_ID']}")
        print(f"Rule Name: {r002.iloc[0]['Rule_Name']}")
        print(f"Threshold: {r002.iloc[0]['Threshold_Value']}")
        if 'Description' in r002.columns:
            print(f"Description: {r002.iloc[0]['Description']}")
        
        # Check if rule is triggered
        threshold = float(r002.iloc[0]['Threshold_Value'])
        print(f"\n=== R002 RULE CHECK ===")
        print(f"Threshold: {threshold}%")
        
        # Calculate tail spend (categories < threshold%)
        tail_categories = category_breakdown[category_breakdown['Percentage'] < threshold]
        tail_spend = tail_categories['Total_Spend'].sum()
        tail_percentage = (tail_spend / c001_data['Spend_USD'].sum() * 100)
        
        print(f"\nTail Spend Categories (< {threshold}%):")
        print(f"  Number of categories: {len(tail_categories)}")
        print(f"  Total tail spend: ${tail_spend:,.2f}")
        print(f"  Tail spend percentage: {tail_percentage:.2f}%")
        
        if len(tail_categories) > 0:
            print(f"\n  Tail Categories:")
            for _, cat in tail_categories.iterrows():
                print(f"    - {cat['Category']}: {cat['Percentage']:.2f}% (${cat['Total_Spend']:,.2f})")
        
        # Determine status
        if tail_percentage > threshold:
            print(f"\n  Status: ❌ TRIGGERED (Tail spend {tail_percentage:.2f}% > {threshold}%)")
        else:
            print(f"\n  Status: ✓ PASSED (Tail spend {tail_percentage:.2f}% <= {threshold}%)")
            
except FileNotFoundError:
    print("Rule book file not found")
except Exception as e:
    print(f"Error loading rule book: {e}")

# Also check procurement rulebook
print("\n" + "=" * 80)
print("CHECKING PROCUREMENT RULEBOOK")
print("=" * 80)

try:
    proc_rules = pd.read_csv('data/structured/procurement_rulebook.csv')
    r002_proc = proc_rules[proc_rules['rule_id'] == 'R002']
    if not r002_proc.empty:
        print(f"\nRule ID: {r002_proc.iloc[0]['rule_id']}")
        print(f"Rule Name: {r002_proc.iloc[0]['rule_name']}")
        print(f"Threshold: {r002_proc.iloc[0]['threshold_value']}")
        print(f"Metric Type: {r002_proc.iloc[0]['metric_type']}")
        if 'description' in r002_proc.columns:
            print(f"Description: {r002_proc.iloc[0]['description']}")
except Exception as e:
    print(f"Could not load procurement rulebook: {e}")

print("\n" + "=" * 80)
print("VERIFICATION COMPLETE")
print("=" * 80)
