"""
Generate Multi-Industry Calculated Data
Calculates metrics FROM structured data (spend_data_multi_industry.csv, etc.)
"""

import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime

def generate_multi_industry_risk_register():
    """Generate risk register from multi-industry spend data"""
    
    print("\n" + "="*80)
    print("📊 GENERATING MULTI-INDUSTRY CALCULATED DATA")
    print("="*80 + "\n")
    
    # Load structured data
    print("📂 Loading structured data...")
    spend_data = pd.read_csv('data/structured/spend_data_multi_industry.csv')
    supplier_data = pd.read_csv('data/structured/supplier_master_multi_industry.csv')
    client_data = pd.read_csv('data/structured/client_master_multi_industry.csv')
    
    print(f"✅ Loaded {len(spend_data)} transactions")
    print(f"✅ Loaded {len(supplier_data)} suppliers")
    print(f"✅ Loaded {len(client_data)} clients\n")
    
    # Calculate risks by analyzing actual data
    risks = []
    
    # 1. Regional Concentration Risk (from spend data)
    print("🔍 Analyzing regional concentration...")
    regional_spend = spend_data.groupby('Supplier_Region')['Spend_USD'].sum()
    total_spend = regional_spend.sum()
    
    for region, spend in regional_spend.items():
        concentration_pct = (spend / total_spend) * 100
        if concentration_pct > 60:
            risk_level = "HIGH"
            severity = 9
        elif concentration_pct > 40:
            risk_level = "MEDIUM"
            severity = 6
        else:
            risk_level = "LOW"
            severity = 3
        
        risks.append({
            'Risk_ID': f'R{len(risks)+1:03d}',
            'Category': 'Regional Concentration',
            'Industry': 'All',
            'Risk_Description': f'{concentration_pct:.1f}% of spend concentrated in {region}',
            'Risk_Level': risk_level,
            'Severity_Score': severity,
            'Likelihood_Score': 7 if concentration_pct > 50 else 5,
            'Impact_Area': 'Supply Chain',
            'Current_Mitigation': 'Diversification strategy' if concentration_pct > 40 else 'Monitoring',
            'Recommended_Action': f'Reduce {region} dependency to <40%' if concentration_pct > 40 else 'Continue monitoring',
            'Owner': 'CPO',
            'Status': 'Active',
            'Last_Updated': datetime.now().strftime('%Y-%m-%d')
        })
    
    # 2. Supplier Concentration Risk (from spend data)
    print("🔍 Analyzing supplier concentration...")
    supplier_spend = spend_data.groupby('Supplier_Name')['Spend_USD'].sum().sort_values(ascending=False)
    
    for supplier, spend in supplier_spend.head(10).items():
        concentration_pct = (spend / total_spend) * 100
        if concentration_pct > 15:
            risks.append({
                'Risk_ID': f'R{len(risks)+1:03d}',
                'Category': 'Supplier Dependency',
                'Industry': spend_data[spend_data['Supplier_Name']==supplier]['Category'].iloc[0],
                'Risk_Description': f'{concentration_pct:.1f}% spend with single supplier ({supplier})',
                'Risk_Level': 'HIGH' if concentration_pct > 20 else 'MEDIUM',
                'Severity_Score': 8 if concentration_pct > 20 else 6,
                'Likelihood_Score': 6,
                'Impact_Area': 'Business Continuity',
                'Current_Mitigation': 'Dual sourcing evaluation',
                'Recommended_Action': f'Identify alternative suppliers for {supplier}',
                'Owner': 'Category Manager',
                'Status': 'Active',
                'Last_Updated': datetime.now().strftime('%Y-%m-%d')
            })
    
    # 3. Category-Specific Risks (from spend and supplier data)
    print("🔍 Analyzing category-specific risks...")
    category_spend = spend_data.groupby('Category')['Spend_USD'].sum()
    
    for category in category_spend.index:
        category_suppliers = spend_data[spend_data['Category']==category]['Supplier_Name'].nunique()
        category_total = category_spend[category]
        
        # Low supplier diversity risk
        if category_suppliers < 3:
            risks.append({
                'Risk_ID': f'R{len(risks)+1:03d}',
                'Category': 'Supplier Diversity',
                'Industry': category,
                'Risk_Description': f'Only {category_suppliers} suppliers for {category}',
                'Risk_Level': 'MEDIUM',
                'Severity_Score': 6,
                'Likelihood_Score': 5,
                'Impact_Area': 'Supply Chain',
                'Current_Mitigation': 'Supplier qualification in progress',
                'Recommended_Action': f'Qualify 2-3 additional suppliers for {category}',
                'Owner': 'Category Manager',
                'Status': 'Active',
                'Last_Updated': datetime.now().strftime('%Y-%m-%d')
            })
    
    # 4. Quality Risks (from supplier data)
    print("🔍 Analyzing quality risks...")
    low_quality_suppliers = supplier_data[supplier_data['quality_rating'] < 4.5]
    
    for _, supplier in low_quality_suppliers.iterrows():
        risks.append({
            'Risk_ID': f'R{len(risks)+1:03d}',
            'Category': 'Quality Risk',
            'Industry': supplier['product_category'],
            'Risk_Description': f'{supplier["supplier_name"]} quality rating: {supplier["quality_rating"]}/5.0',
            'Risk_Level': 'MEDIUM' if supplier['quality_rating'] >= 4.0 else 'HIGH',
            'Severity_Score': 7 if supplier['quality_rating'] < 4.0 else 5,
            'Likelihood_Score': 6,
            'Impact_Area': 'Product Quality',
            'Current_Mitigation': 'Enhanced inspection protocols',
            'Recommended_Action': f'Quality improvement plan for {supplier["supplier_name"]}',
            'Owner': 'Quality Manager',
            'Status': 'Active',
            'Last_Updated': datetime.now().strftime('%Y-%m-%d')
        })
    
    # 5. Delivery Reliability Risks
    print("🔍 Analyzing delivery risks...")
    low_reliability_suppliers = supplier_data[supplier_data['delivery_reliability_pct'] < 92]
    
    for _, supplier in low_reliability_suppliers.iterrows():
        risks.append({
            'Risk_ID': f'R{len(risks)+1:03d}',
            'Category': 'Delivery Risk',
            'Industry': supplier['product_category'],
            'Risk_Description': f'{supplier["supplier_name"]} delivery reliability: {supplier["delivery_reliability_pct"]}%',
            'Risk_Level': 'MEDIUM',
            'Severity_Score': 6,
            'Likelihood_Score': 7,
            'Impact_Area': 'Operations',
            'Current_Mitigation': 'Safety stock increase',
            'Recommended_Action': f'Performance improvement plan for {supplier["supplier_name"]}',
            'Owner': 'Supply Chain Manager',
            'Status': 'Active',
            'Last_Updated': datetime.now().strftime('%Y-%m-%d')
        })
    
    # 6. Sustainability Risks
    print("🔍 Analyzing sustainability risks...")
    low_esg_suppliers = supplier_data[supplier_data['sustainability_score'] < 8.0]
    
    for _, supplier in low_esg_suppliers.iterrows():
        risks.append({
            'Risk_ID': f'R{len(risks)+1:03d}',
            'Category': 'ESG Risk',
            'Industry': supplier['product_category'],
            'Risk_Description': f'{supplier["supplier_name"]} ESG score: {supplier["sustainability_score"]}/10',
            'Risk_Level': 'LOW' if supplier['sustainability_score'] >= 7.5 else 'MEDIUM',
            'Severity_Score': 4,
            'Likelihood_Score': 5,
            'Impact_Area': 'Reputation',
            'Current_Mitigation': 'ESG improvement program',
            'Recommended_Action': f'ESG audit and improvement plan for {supplier["supplier_name"]}',
            'Owner': 'Sustainability Manager',
            'Status': 'Active',
            'Last_Updated': datetime.now().strftime('%Y-%m-%d')
        })
    
    # Create DataFrame
    risk_df = pd.DataFrame(risks)
    
    # Calculate risk score
    risk_df['Risk_Score'] = risk_df['Severity_Score'] * risk_df['Likelihood_Score']
    
    # Save to CSV
    output_path = 'data/calculated/risk_register_multi_industry.csv'
    risk_df.to_csv(output_path, index=False)
    
    print(f"\n✅ Generated {len(risk_df)} risks")
    print(f"✅ Saved to: {output_path}\n")
    
    # Summary
    print("📊 RISK SUMMARY:")
    print("="*80)
    print(f"Total Risks: {len(risk_df)}")
    print(f"\nBy Risk Level:")
    print(risk_df['Risk_Level'].value_counts())
    print(f"\nBy Category:")
    print(risk_df['Category'].value_counts())
    print(f"\nBy Industry:")
    print(risk_df['Industry'].value_counts().head(10))
    
    return risk_df


def generate_pricing_benchmarks():
    """Generate pricing benchmarks from spend data"""
    
    print("\n" + "="*80)
    print("📊 GENERATING PRICING BENCHMARKS")
    print("="*80 + "\n")
    
    spend_data = pd.read_csv('data/structured/spend_data_multi_industry.csv')
    
    # Calculate average prices by category
    benchmarks = spend_data.groupby('Category').agg({
        'Spend_USD': ['mean', 'median', 'min', 'max', 'std', 'count']
    }).round(2)
    
    benchmarks.columns = ['Average_Spend', 'Median_Spend', 'Min_Spend', 'Max_Spend', 'Std_Dev', 'Transaction_Count']
    benchmarks = benchmarks.reset_index()
    
    # Add market position
    benchmarks['Market_Position'] = benchmarks['Average_Spend'].apply(
        lambda x: 'Premium' if x > benchmarks['Average_Spend'].quantile(0.75) else
                  'Standard' if x > benchmarks['Average_Spend'].quantile(0.25) else
                  'Economy'
    )
    
    # Save
    output_path = 'data/calculated/pricing_benchmarks_multi_industry.csv'
    benchmarks.to_csv(output_path, index=False)
    
    print(f"✅ Generated pricing benchmarks for {len(benchmarks)} categories")
    print(f"✅ Saved to: {output_path}\n")
    
    return benchmarks


def generate_supplier_performance_metrics():
    """Generate supplier performance metrics"""
    
    print("\n" + "="*80)
    print("📊 GENERATING SUPPLIER PERFORMANCE METRICS")
    print("="*80 + "\n")
    
    spend_data = pd.read_csv('data/structured/spend_data_multi_industry.csv')
    supplier_data = pd.read_csv('data/structured/supplier_master_multi_industry.csv')
    
    # Merge data
    merged = spend_data.merge(supplier_data, left_on='Supplier_ID', right_on='supplier_id', how='left')
    
    # Calculate metrics by supplier
    metrics = merged.groupby('Supplier_Name').agg({
        'Spend_USD': ['sum', 'count', 'mean'],
        'quality_rating': 'first',
        'delivery_reliability_pct': 'first',
        'sustainability_score': 'first',
        'product_category': 'first'
    }).round(2)
    
    metrics.columns = ['Total_Spend', 'Transaction_Count', 'Avg_Transaction_Value', 
                       'Quality_Rating', 'Delivery_Reliability', 'Sustainability_Score', 'Category']
    metrics = metrics.reset_index()
    
    # Calculate performance score
    metrics['Performance_Score'] = (
        (metrics['Quality_Rating'] / 5.0 * 40) +
        (metrics['Delivery_Reliability'] / 100 * 30) +
        (metrics['Sustainability_Score'] / 10 * 30)
    ).round(2)
    
    # Rank suppliers
    metrics['Performance_Rank'] = metrics['Performance_Score'].rank(ascending=False, method='dense').astype(int)
    
    # Save
    output_path = 'data/calculated/supplier_performance_multi_industry.csv'
    metrics.to_csv(output_path, index=False)
    
    print(f"✅ Generated performance metrics for {len(metrics)} suppliers")
    print(f"✅ Saved to: {output_path}\n")
    
    return metrics


if __name__ == "__main__":
    print("\n" + "="*80)
    print("🚀 MULTI-INDUSTRY CALCULATED DATA GENERATION")
    print("="*80)
    
    # Generate all calculated data
    risk_df = generate_multi_industry_risk_register()
    pricing_df = generate_pricing_benchmarks()
    performance_df = generate_supplier_performance_metrics()
    
    print("\n" + "="*80)
    print("✅ ALL CALCULATED DATA GENERATED SUCCESSFULLY!")
    print("="*80)
    print("\nGenerated Files:")
    print("  1. data/calculated/risk_register_multi_industry.csv")
    print("  2. data/calculated/pricing_benchmarks_multi_industry.csv")
    print("  3. data/calculated/supplier_performance_multi_industry.csv")
    print("\n" + "="*80 + "\n")
