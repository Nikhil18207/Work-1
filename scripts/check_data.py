import pandas as pd

print("=" * 80)
print("CHECKING SPEND DATA")
print("=" * 80)

# Load spend data
df = pd.read_csv('data/structured/spend_data.csv')

print(f"\nTotal rows in spend_data.csv: {len(df)}")
print(f"\nColumns: {list(df.columns)}")

print("\n" + "=" * 80)
print("UNIQUE VALUES")
print("=" * 80)

print(f"\nUnique Clients: {df['Client_ID'].unique()}")
print(f"\nUnique Categories: {df['Category'].unique()}")

print("\n" + "=" * 80)
print("CLIENT_001 DATA")
print("=" * 80)

client_data = df[df['Client_ID'] == 'CLIENT_001']
print(f"\nRows for CLIENT_001: {len(client_data)}")

if len(client_data) > 0:
    print(f"Categories: {client_data['Category'].unique()}")
    print(f"Total Spend: ${client_data['Spend_USD'].sum():,.2f}")
    print(f"\nBreakdown by Category:")
    category_spend = client_data.groupby('Category')['Spend_USD'].sum().sort_values(ascending=False)
    for cat, spend in category_spend.items():
        print(f"  - {cat}: ${spend:,.2f}")
else:
    print("❌ No data found for CLIENT_001")

print("\n" + "=" * 80)
print("RICE BRAN OIL DATA")
print("=" * 80)

rbo_data = df[df['Category'] == 'Rice Bran Oil']
print(f"\nRows for Rice Bran Oil: {len(rbo_data)}")

if len(rbo_data) > 0:
    print(f"Clients with Rice Bran Oil: {rbo_data['Client_ID'].unique()}")
    print(f"Total Spend: ${rbo_data['Spend_USD'].sum():,.2f}")
    print(f"\nBreakdown by Client:")
    client_spend = rbo_data.groupby('Client_ID')['Spend_USD'].sum().sort_values(ascending=False)
    for client, spend in client_spend.items():
        print(f"  - {client}: ${spend:,.2f}")
else:
    print("❌ No data found for Rice Bran Oil category")

print("\n" + "=" * 80)
print("SAMPLE DATA (First 5 rows)")
print("=" * 80)
print(df.head())
