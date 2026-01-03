"""
Script to regenerate all calculated data files from the enhanced spend_data.csv
Run this after updating spend_data.csv to refresh all derived metrics.
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
import os

# Set paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STRUCTURED_DIR = os.path.join(BASE_DIR, 'data', 'structured')
CALCULATED_DIR = os.path.join(BASE_DIR, 'data', 'calculated')

# Ensure calculated directory exists
os.makedirs(CALCULATED_DIR, exist_ok=True)

# Set seed for reproducibility
random.seed(42)
np.random.seed(42)

print("="*60)
print("REGENERATING ALL CALCULATED DATA FILES")
print("="*60)

# Load source data
print("\nLoading source data...")
spend_df = pd.read_csv(os.path.join(STRUCTURED_DIR, 'spend_data.csv'))
supplier_master = pd.read_csv(os.path.join(STRUCTURED_DIR, 'supplier_master.csv'))
contracts_df = pd.read_csv(os.path.join(STRUCTURED_DIR, 'supplier_contracts.csv'))

print(f"  Spend data: {len(spend_df)} rows")
print(f"  Suppliers: {len(supplier_master)} records")
print(f"  Contracts: {len(contracts_df)} records")

calculation_date = datetime.now().strftime('%Y-%m-%d')

# ============================================================
# 1. CALCULATED METRICS
# ============================================================
print("\n[1/10] Generating calculated_metrics.csv...")

metrics_rows = []
subcategories = spend_df.groupby(['Sector', 'Category', 'SubCategory'])

for (sector, category, subcategory), group in subcategories:
    total_spend = group['Spend_USD'].sum()
    num_suppliers = group['Supplier_ID'].nunique()
    num_transactions = len(group)

    # Region concentration
    region_spend = group.groupby('Supplier_Region')['Spend_USD'].sum()
    top_region = region_spend.idxmax()
    top_region_pct = (region_spend.max() / total_spend * 100)

    # Supplier concentration
    supplier_spend = group.groupby('Supplier_ID')['Spend_USD'].sum().sort_values(ascending=False)
    top_supplier_pct = (supplier_spend.iloc[0] / total_spend * 100) if len(supplier_spend) > 0 else 0
    top3_supplier_pct = (supplier_spend.head(3).sum() / total_spend * 100) if len(supplier_spend) > 0 else 0

    # Ratings
    avg_quality = group['Quality_Rating'].mean() if 'Quality_Rating' in group.columns else 4.0
    avg_delivery = group['Delivery_Rating'].mean() if 'Delivery_Rating' in group.columns else 4.0

    # Risk scores
    regional_risk = min(100, top_region_pct * 1.2)
    supplier_risk = min(100, top_supplier_pct * 1.2)
    overall_risk = regional_risk * 0.4 + supplier_risk * 0.4 + 20 * 0.2

    base_row = {'Sector': sector, 'Category': category, 'SubCategory': subcategory}

    metrics_rows.extend([
        {**base_row, 'Metric': 'Total_Spend_USD', 'Calculated_Value': round(total_spend, 2),
         'Calculation_Method': 'SUM(Spend_USD)', 'Data_Sources': 'spend_data.csv',
         'Calculation_Date': calculation_date, 'Confidence_Level': 'HIGH'},
        {**base_row, 'Metric': 'Number_of_Suppliers', 'Calculated_Value': float(num_suppliers),
         'Calculation_Method': 'COUNT(DISTINCT Supplier_ID)', 'Data_Sources': 'spend_data.csv',
         'Calculation_Date': calculation_date, 'Confidence_Level': 'HIGH'},
        {**base_row, 'Metric': 'Number_of_Transactions', 'Calculated_Value': float(num_transactions),
         'Calculation_Method': 'COUNT(*)', 'Data_Sources': 'spend_data.csv',
         'Calculation_Date': calculation_date, 'Confidence_Level': 'HIGH'},
        {**base_row, 'Metric': 'Top_Region_Concentration_Pct', 'Calculated_Value': round(top_region_pct, 2),
         'Calculation_Method': f'MAX(Region_Spend)/Total_Spend*100 [{top_region}]', 'Data_Sources': 'spend_data.csv',
         'Calculation_Date': calculation_date, 'Confidence_Level': 'HIGH'},
        {**base_row, 'Metric': 'Top_Supplier_Concentration_Pct', 'Calculated_Value': round(top_supplier_pct, 2),
         'Calculation_Method': 'MAX(Supplier_Spend)/Total_Spend*100', 'Data_Sources': 'spend_data.csv',
         'Calculation_Date': calculation_date, 'Confidence_Level': 'HIGH'},
        {**base_row, 'Metric': 'Top3_Supplier_Concentration_Pct', 'Calculated_Value': round(top3_supplier_pct, 2),
         'Calculation_Method': 'SUM(Top3_Supplier_Spend)/Total_Spend*100', 'Data_Sources': 'spend_data.csv',
         'Calculation_Date': calculation_date, 'Confidence_Level': 'HIGH'},
        {**base_row, 'Metric': 'Avg_Quality_Rating', 'Calculated_Value': round(avg_quality, 2),
         'Calculation_Method': 'AVG(Quality_Rating)', 'Data_Sources': 'spend_data.csv',
         'Calculation_Date': calculation_date, 'Confidence_Level': 'MEDIUM'},
        {**base_row, 'Metric': 'Avg_Delivery_Rating', 'Calculated_Value': round(avg_delivery, 2),
         'Calculation_Method': 'AVG(Delivery_Rating)', 'Data_Sources': 'spend_data.csv',
         'Calculation_Date': calculation_date, 'Confidence_Level': 'MEDIUM'},
        {**base_row, 'Metric': 'Regional_Risk_Score', 'Calculated_Value': round(regional_risk, 1),
         'Calculation_Method': 'Concentration_Based_Risk_Calculation', 'Data_Sources': 'spend_data.csv',
         'Calculation_Date': calculation_date, 'Confidence_Level': 'HIGH'},
        {**base_row, 'Metric': 'Supplier_Risk_Score', 'Calculated_Value': round(supplier_risk, 1),
         'Calculation_Method': 'Concentration_Based_Risk_Calculation', 'Data_Sources': 'spend_data.csv',
         'Calculation_Date': calculation_date, 'Confidence_Level': 'HIGH'},
        {**base_row, 'Metric': 'Overall_Risk_Score', 'Calculated_Value': round(overall_risk, 1),
         'Calculation_Method': 'WEIGHTED_AVG(Regional*0.4 + Supplier*0.4 + DataRisk*0.2)', 'Data_Sources': 'spend_data.csv',
         'Calculation_Date': calculation_date, 'Confidence_Level': 'HIGH'},
    ])

metrics_df = pd.DataFrame(metrics_rows)
metrics_df.to_csv(os.path.join(CALCULATED_DIR, 'calculated_metrics.csv'), index=False)
print(f"  Generated {len(metrics_df)} metric rows")

# ============================================================
# 2. ACTION PLAN
# ============================================================
print("\n[2/10] Generating action_plan.csv...")

action_templates = [
    ('Diversify supplier base', 'Supplier Concentration', 'HIGH', 'Add 2-3 alternative suppliers to reduce dependency'),
    ('Expand regional sourcing', 'Regional Concentration', 'CRITICAL', 'Identify suppliers in {region} to reduce geographic risk'),
    ('Negotiate volume discounts', 'Cost Optimization', 'MEDIUM', 'Leverage spend volume for 5-10% cost reduction'),
    ('Improve delivery performance', 'Performance Improvement', 'HIGH', 'Implement SLA monitoring and escalation process'),
    ('Conduct supplier audit', 'Risk Mitigation', 'MEDIUM', 'Annual quality and compliance audit'),
    ('Develop backup suppliers', 'Business Continuity', 'HIGH', 'Qualify backup suppliers in alternative regions'),
]

action_rows = []
for (sector, category, subcategory), group in subcategories:
    total_spend = group['Spend_USD'].sum()
    supplier_spend = group.groupby('Supplier_ID')['Spend_USD'].sum()
    top_supplier_pct = (supplier_spend.max() / total_spend * 100) if len(supplier_spend) > 0 else 0

    region_spend = group.groupby('Supplier_Region')['Spend_USD'].sum()
    regions_used = list(region_spend.index)
    all_regions = ['Americas', 'Europe', 'APAC', 'Middle East', 'Africa']
    missing_regions = [r for r in all_regions if r not in regions_used]

    # Select actions based on concentration
    selected_actions = []
    if top_supplier_pct > 50:
        selected_actions.append(action_templates[0])
        selected_actions.append(action_templates[5])
    if region_spend.max() / total_spend > 0.6:
        target_region = missing_regions[0] if missing_regions else 'alternative region'
        action = list(action_templates[1])
        action[3] = action[3].format(region=target_region)
        selected_actions.append(tuple(action))
    selected_actions.append(action_templates[2])
    selected_actions.append(action_templates[4])

    for i, (action, category_type, priority, description) in enumerate(selected_actions[:4], 1):
        action_rows.append({
            'Sector': sector,
            'Category': category,
            'SubCategory': subcategory,
            'Action_ID': f'A{i:03d}',
            'Action_Name': action,
            'Action_Category': category_type,
            'Priority': priority,
            'Description': description,
            'Target_Date': (datetime.now() + timedelta(days=90*i)).strftime('%Y-%m-%d'),
            'Status': 'Pending',
            'Estimated_Savings_Pct': round(random.uniform(3, 15), 1)
        })

action_df = pd.DataFrame(action_rows)
action_df.to_csv(os.path.join(CALCULATED_DIR, 'action_plan.csv'), index=False)
print(f"  Generated {len(action_df)} action items")

# ============================================================
# 3. RISK REGISTER (Multi-Industry)
# ============================================================
print("\n[3/10] Generating risk_register_multi_industry.csv...")

risk_rows = []
risk_types = [
    ('Supply Chain Disruption', 'OPERATIONAL'),
    ('Price Volatility', 'FINANCIAL'),
    ('Quality Issues', 'OPERATIONAL'),
    ('Geopolitical Risk', 'STRATEGIC'),
    ('Supplier Financial Stability', 'FINANCIAL'),
    ('Regulatory Compliance', 'COMPLIANCE'),
    ('ESG/Sustainability', 'COMPLIANCE'),
]

for (sector, category, subcategory), group in subcategories:
    total_spend = group['Spend_USD'].sum()
    supplier_spend = group.groupby('Supplier_ID')['Spend_USD'].sum()
    top_supplier_pct = supplier_spend.max() / total_spend * 100 if total_spend > 0 else 0

    region_spend = group.groupby('Supplier_Region')['Spend_USD'].sum()
    top_region_pct = region_spend.max() / total_spend * 100 if total_spend > 0 else 0

    # High risk regions
    high_risk_regions = ['Middle East', 'Africa']
    high_risk_spend = region_spend[region_spend.index.isin(high_risk_regions)].sum()
    high_risk_pct = high_risk_spend / total_spend * 100 if total_spend > 0 else 0

    for risk_name, risk_type in risk_types:
        # Calculate likelihood and impact based on metrics
        if risk_name == 'Supply Chain Disruption':
            likelihood = min(5, int(top_supplier_pct / 20) + 1)
            impact = 4 if top_supplier_pct > 50 else 3
        elif risk_name == 'Geopolitical Risk':
            likelihood = min(5, int(high_risk_pct / 15) + 1)
            impact = 4 if high_risk_pct > 30 else 3
        elif risk_name == 'Price Volatility':
            likelihood = random.randint(2, 4)
            impact = 3
        else:
            likelihood = random.randint(1, 4)
            impact = random.randint(2, 4)

        risk_score = likelihood * impact
        risk_level = 'CRITICAL' if risk_score >= 16 else 'HIGH' if risk_score >= 9 else 'MEDIUM' if risk_score >= 4 else 'LOW'

        risk_rows.append({
            'Sector': sector,
            'Category': category,
            'SubCategory': subcategory,
            'Risk_ID': f'R{len(risk_rows)+1:04d}',
            'Risk_Name': risk_name,
            'Risk_Type': risk_type,
            'Likelihood': likelihood,
            'Impact': impact,
            'Risk_Score': risk_score,
            'Risk_Level': risk_level,
            'Mitigation_Strategy': f'Implement controls for {risk_name.lower()}',
            'Owner': 'Procurement Team',
            'Review_Date': (datetime.now() + timedelta(days=90)).strftime('%Y-%m-%d')
        })

risk_df = pd.DataFrame(risk_rows)
risk_df.to_csv(os.path.join(CALCULATED_DIR, 'risk_register_multi_industry.csv'), index=False)
risk_df.to_csv(os.path.join(CALCULATED_DIR, 'risk_register.csv'), index=False)  # Also save as risk_register.csv
print(f"  Generated {len(risk_df)} risk entries")

# ============================================================
# 4. SUPPLIER PERFORMANCE (Multi-Industry)
# ============================================================
print("\n[4/10] Generating supplier_performance_multi_industry.csv...")

perf_rows = []
for _, supplier in supplier_master.iterrows():
    supplier_spend = spend_df[spend_df['Supplier_ID'] == supplier['supplier_id']]

    if len(supplier_spend) > 0:
        total_spend = supplier_spend['Spend_USD'].sum()
        avg_quality = supplier_spend['Quality_Rating'].mean() if 'Quality_Rating' in supplier_spend.columns else 4.0
        avg_delivery = supplier_spend['Delivery_Rating'].mean() if 'Delivery_Rating' in supplier_spend.columns else 4.0
        transaction_count = len(supplier_spend)
    else:
        total_spend = 0
        avg_quality = supplier['quality_rating']
        avg_delivery = random.uniform(3.5, 4.8)
        transaction_count = 0

    # Performance score
    performance_score = (avg_quality * 0.4 + avg_delivery * 0.4 + random.uniform(3.5, 4.5) * 0.2) * 20

    perf_rows.append({
        'Supplier_ID': supplier['supplier_id'],
        'Supplier_Name': supplier['supplier_name'],
        'Region': supplier['region'],
        'Country': supplier['country'],
        'Sector': supplier['sector'],
        'Category': supplier['product_category'],
        'SubCategory': supplier['subcategory'],
        'Total_Spend_USD': round(total_spend, 2),
        'Transaction_Count': transaction_count,
        'Avg_Quality_Rating': round(avg_quality, 2),
        'Avg_Delivery_Rating': round(avg_delivery, 2),
        'Performance_Score': round(performance_score, 1),
        'Performance_Tier': 'Gold' if performance_score >= 85 else 'Silver' if performance_score >= 70 else 'Bronze',
        'Sustainability_Score': supplier.get('sustainability_score', random.uniform(6, 9)),
        'Last_Review_Date': calculation_date
    })

perf_df = pd.DataFrame(perf_rows)
perf_df.to_csv(os.path.join(CALCULATED_DIR, 'supplier_performance_multi_industry.csv'), index=False)
print(f"  Generated {len(perf_df)} supplier performance records")

# ============================================================
# 5. PRICING BENCHMARKS (Multi-Industry)
# ============================================================
print("\n[5/10] Generating pricing_benchmarks_multi_industry.csv...")

benchmark_rows = []
for (sector, category, subcategory), group in subcategories:
    avg_spend_per_transaction = group['Spend_USD'].mean()
    min_spend = group['Spend_USD'].min()
    max_spend = group['Spend_USD'].max()

    # Regional benchmarks
    region_avg = group.groupby('Supplier_Region')['Spend_USD'].mean()

    benchmark_rows.append({
        'Sector': sector,
        'Category': category,
        'SubCategory': subcategory,
        'Avg_Transaction_Value': round(avg_spend_per_transaction, 2),
        'Min_Transaction_Value': round(min_spend, 2),
        'Max_Transaction_Value': round(max_spend, 2),
        'Std_Dev': round(group['Spend_USD'].std(), 2) if len(group) > 1 else 0,
        'Americas_Avg': round(region_avg.get('Americas', 0), 2),
        'Europe_Avg': round(region_avg.get('Europe', 0), 2),
        'APAC_Avg': round(region_avg.get('APAC', 0), 2),
        'Middle_East_Avg': round(region_avg.get('Middle East', 0), 2),
        'Africa_Avg': round(region_avg.get('Africa', 0), 2),
        'Benchmark_Date': calculation_date,
        'Data_Points': len(group)
    })

benchmark_df = pd.DataFrame(benchmark_rows)
benchmark_df.to_csv(os.path.join(CALCULATED_DIR, 'pricing_benchmarks_multi_industry.csv'), index=False)
print(f"  Generated {len(benchmark_df)} pricing benchmarks")

# ============================================================
# 6. FORECASTS & PROJECTIONS
# ============================================================
print("\n[6/10] Generating forecasts_projections.csv...")

forecast_rows = []
for (sector, category, subcategory), group in subcategories:
    current_spend = group['Spend_USD'].sum()

    # Generate 4 quarters of projections
    for q in range(1, 5):
        growth_rate = random.uniform(0.02, 0.08)  # 2-8% quarterly growth
        projected_spend = current_spend * (1 + growth_rate) ** q

        forecast_rows.append({
            'Sector': sector,
            'Category': category,
            'SubCategory': subcategory,
            'Forecast_Period': f'Q{q} 2026',
            'Projected_Spend_USD': round(projected_spend, 2),
            'Growth_Rate_Pct': round(growth_rate * 100, 2),
            'Confidence_Interval_Lower': round(projected_spend * 0.9, 2),
            'Confidence_Interval_Upper': round(projected_spend * 1.1, 2),
            'Forecast_Model': 'Time_Series_Extrapolation',
            'Generated_Date': calculation_date
        })

forecast_df = pd.DataFrame(forecast_rows)
forecast_df.to_csv(os.path.join(CALCULATED_DIR, 'forecasts_projections.csv'), index=False)
print(f"  Generated {len(forecast_df)} forecast entries")

# ============================================================
# 7. HISTORICAL QUARTERLY TRENDS
# ============================================================
print("\n[7/10] Generating historical_quarterly_trends.csv...")

# Parse transaction dates
spend_df['Transaction_Date'] = pd.to_datetime(spend_df['Transaction_Date'])
spend_df['Quarter'] = spend_df['Transaction_Date'].dt.to_period('Q')

trend_rows = []
for (sector, category, subcategory), group in subcategories:
    quarterly = group.groupby('Quarter').agg({
        'Spend_USD': 'sum',
        'Supplier_ID': 'nunique',
        'Quality_Rating': 'mean',
        'Delivery_Rating': 'mean'
    }).reset_index()

    for _, row in quarterly.iterrows():
        trend_rows.append({
            'Sector': sector,
            'Category': category,
            'SubCategory': subcategory,
            'Quarter': str(row['Quarter']),
            'Total_Spend_USD': round(row['Spend_USD'], 2),
            'Active_Suppliers': int(row['Supplier_ID']),
            'Avg_Quality_Rating': round(row['Quality_Rating'], 2),
            'Avg_Delivery_Rating': round(row['Delivery_Rating'], 2)
        })

trend_df = pd.DataFrame(trend_rows)
trend_df.to_csv(os.path.join(CALCULATED_DIR, 'historical_quarterly_trends.csv'), index=False)
print(f"  Generated {len(trend_df)} trend entries")

# ============================================================
# 8. SCENARIO PLANNING
# ============================================================
print("\n[8/10] Generating scenario_planning.csv...")

scenarios = [
    ('Aggressive Diversification', 'Reduce top supplier share to <30%', 15, 25),
    ('Moderate Diversification', 'Reduce top supplier share to <40%', 10, 15),
    ('Regional Expansion', 'Add Africa/Middle East suppliers', 12, 20),
    ('Cost Optimization', 'Shift 20% spend to low-cost regions', 8, 12),
    ('Risk Mitigation', 'Dual-source all critical categories', 5, 18),
]

scenario_rows = []
for (sector, category, subcategory), group in subcategories:
    current_spend = group['Spend_USD'].sum()

    for scenario_name, description, savings_pct, risk_reduction in scenarios:
        scenario_rows.append({
            'Sector': sector,
            'Category': category,
            'SubCategory': subcategory,
            'Scenario_Name': scenario_name,
            'Description': description,
            'Current_Spend_USD': round(current_spend, 2),
            'Projected_Savings_Pct': savings_pct,
            'Projected_Savings_USD': round(current_spend * savings_pct / 100, 2),
            'Risk_Reduction_Pct': risk_reduction,
            'Implementation_Complexity': random.choice(['Low', 'Medium', 'High']),
            'Timeline_Months': random.randint(3, 12)
        })

scenario_df = pd.DataFrame(scenario_rows)
scenario_df.to_csv(os.path.join(CALCULATED_DIR, 'scenario_planning.csv'), index=False)
print(f"  Generated {len(scenario_df)} scenario entries")

# ============================================================
# 9. SUPPLIER PERFORMANCE HISTORY
# ============================================================
print("\n[9/10] Generating supplier_performance_history.csv...")

history_rows = []
# Sample top suppliers
top_suppliers = spend_df.groupby('Supplier_ID')['Spend_USD'].sum().nlargest(50).index.tolist()

for supplier_id in top_suppliers:
    supplier_data = spend_df[spend_df['Supplier_ID'] == supplier_id].iloc[0]

    # Generate 4 quarters of history
    for q in range(4, 0, -1):
        period = f'Q{5-q} 2025'
        history_rows.append({
            'Supplier_ID': supplier_id,
            'Supplier_Name': supplier_data['Supplier_Name'],
            'Period': period,
            'Quality_Score': round(random.uniform(3.8, 5.0), 2),
            'Delivery_Score': round(random.uniform(3.5, 5.0), 2),
            'Cost_Competitiveness': round(random.uniform(3.5, 4.8), 2),
            'Responsiveness': round(random.uniform(3.5, 4.9), 2),
            'Overall_Score': round(random.uniform(3.8, 4.8), 2),
            'Trend': random.choice(['Improving', 'Stable', 'Declining'])
        })

history_df = pd.DataFrame(history_rows)
history_df.to_csv(os.path.join(CALCULATED_DIR, 'supplier_performance_history.csv'), index=False)
print(f"  Generated {len(history_df)} history entries")

# ============================================================
# 10. SUMMARY
# ============================================================
print("\n" + "="*60)
print("REGENERATION COMPLETE!")
print("="*60)

print("\nFiles generated in data/calculated/:")
for f in os.listdir(CALCULATED_DIR):
    if f.endswith('.csv'):
        size = os.path.getsize(os.path.join(CALCULATED_DIR, f))
        print(f"  - {f} ({size:,} bytes)")

print(f"\nTotal spend in dataset: ${spend_df['Spend_USD'].sum():,.0f}")
print(f"Total suppliers: {spend_df['Supplier_ID'].nunique()}")
print(f"Total transactions: {len(spend_df)}")
print(f"Regions covered: {spend_df['Supplier_Region'].nunique()}")
