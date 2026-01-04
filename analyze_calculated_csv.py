import pandas as pd
import os

# Define the calculated CSV files to analyze
csv_files = [
    'data/calculated/calculated_metrics.csv',
    'data/calculated/action_plan.csv',
    'data/calculated/risk_register.csv',
    'data/calculated/forecasts_projections.csv',
    'data/calculated/supplier_performance_history.csv',
    'data/calculated/historical_quarterly_trends.csv',
    'data/calculated/scenario_planning.csv',
    'data/calculated/pricing_benchmarks_multi_industry.csv',
    'data/calculated/risk_register_multi_industry.csv',
    'data/calculated/supplier_performance_multi_industry.csv'
]

print("="*80)
print("CALCULATED CSV FILES ANALYSIS")
print("="*80)

for csv_file in csv_files:
    if os.path.exists(csv_file):
        print(f"\n{'='*80}")
        print(f"FILE: {csv_file}")
        print(f"{'='*80}")
        
        try:
            df = pd.read_csv(csv_file)
            
            print(f"\n📊 BASIC INFO:")
            print(f"   Total Rows: {len(df):,}")
            print(f"   Total Columns: {len(df.columns)}")
            
            print(f"\n📋 COLUMNS:")
            for i, col in enumerate(df.columns, 1):
                print(f"   {i}. {col}")
            
            print(f"\n🔍 DATA PREVIEW (First 5 rows):")
            print(df.head(5).to_string(index=False))
            
            # Check for any null values
            null_counts = df.isnull().sum()
            if null_counts.sum() > 0:
                print(f"\n⚠️  NULL VALUES DETECTED:")
                for col, count in null_counts[null_counts > 0].items():
                    print(f"   {col}: {count} nulls")
            else:
                print(f"\n✅ NO NULL VALUES")
            
            # Show unique value counts for key columns
            if 'Sector' in df.columns:
                print(f"\n📈 UNIQUE VALUES:")
                print(f"   Sectors: {df['Sector'].nunique()}")
                if 'Category' in df.columns:
                    print(f"   Categories: {df['Category'].nunique()}")
                if 'SubCategory' in df.columns:
                    print(f"   SubCategories: {df['SubCategory'].nunique()}")
            
        except Exception as e:
            print(f"\n❌ ERROR reading file: {str(e)}")
    else:
        print(f"\n⚠️  FILE NOT FOUND: {csv_file}")

print(f"\n{'='*80}")
print("ANALYSIS COMPLETE")
print(f"{'='*80}")
