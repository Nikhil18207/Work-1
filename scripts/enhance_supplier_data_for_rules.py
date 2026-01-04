"""
Enhance supplier data to support all 35 procurement rules
This script adds missing fields to supplier_master.csv and supplier_contracts.csv
"""

import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime, timedelta
import random

# Set seed for reproducibility
np.random.seed(42)
random.seed(42)

# Paths
DATA_DIR = Path(__file__).parent.parent / 'data' / 'structured'

def enhance_supplier_master():
    """Add missing fields to supplier_master.csv for rules evaluation"""

    print("Loading supplier_master.csv...")
    df = pd.read_csv(DATA_DIR / 'supplier_master.csv')
    print(f"Loaded {len(df)} suppliers")

    # Current columns:
    # supplier_id, supplier_name, region, country, sector, product_category, subcategory,
    # quality_rating, certifications, sustainability_score, delivery_reliability_pct,
    # lead_time_days, min_order_quantity, payment_terms_offered, years_in_business, annual_capacity_tons

    # === NEW FIELDS NEEDED FOR RULES ===

    # R010: Supplier Financial Risk - debt_to_equity_ratio (threshold: 2.5)
    # Most suppliers should be healthy (< 2.5), some at risk
    df['debt_to_equity_ratio'] = np.random.choice(
        [np.random.uniform(0.5, 1.5), np.random.uniform(1.5, 2.3), np.random.uniform(2.5, 4.0)],
        size=len(df),
        p=[0.6, 0.3, 0.1]  # 60% healthy, 30% moderate, 10% high risk
    )
    df['debt_to_equity_ratio'] = df['debt_to_equity_ratio'].round(2)

    # R011: Capacity Utilization Risk (threshold: 90%)
    df['capacity_utilization_pct'] = np.random.choice(
        [np.random.uniform(50, 75), np.random.uniform(75, 88), np.random.uniform(90, 98)],
        size=len(df),
        p=[0.4, 0.45, 0.15]  # 40% low, 45% moderate, 15% high
    )
    df['capacity_utilization_pct'] = df['capacity_utilization_pct'].round(1)

    # R013: Lead Time Variance (threshold: 30%)
    df['lead_time_variance_pct'] = np.random.choice(
        [np.random.uniform(5, 15), np.random.uniform(15, 28), np.random.uniform(30, 50)],
        size=len(df),
        p=[0.5, 0.35, 0.15]
    )
    df['lead_time_variance_pct'] = df['lead_time_variance_pct'].round(1)

    # R016: Innovation Score (threshold: 60 for strategic)
    df['innovation_score'] = np.random.choice(
        [np.random.uniform(30, 55), np.random.uniform(55, 70), np.random.uniform(70, 95)],
        size=len(df),
        p=[0.2, 0.5, 0.3]
    )
    df['innovation_score'] = df['innovation_score'].round(0).astype(int)

    # R020: Supplier Responsiveness - response_time_hours (threshold: 48)
    df['response_time_hours'] = np.random.choice(
        [np.random.uniform(4, 24), np.random.uniform(24, 46), np.random.uniform(48, 96)],
        size=len(df),
        p=[0.5, 0.35, 0.15]
    )
    df['response_time_hours'] = df['response_time_hours'].round(0).astype(int)

    # R025: Cybersecurity Rating (A, B, C, D, F) - threshold: B
    cyber_ratings = ['A', 'A', 'A', 'B', 'B', 'B', 'B', 'C', 'C', 'D']  # Most are B or better
    df['cybersecurity_rating'] = [random.choice(cyber_ratings) for _ in range(len(df))]

    # R030: Supplier Innovation Score (already added above as innovation_score)

    # R031: Carbon Footprint kg CO2/unit (threshold: 1000)
    df['carbon_footprint_kg_co2'] = np.random.choice(
        [np.random.uniform(200, 600), np.random.uniform(600, 950), np.random.uniform(1000, 2000)],
        size=len(df),
        p=[0.4, 0.45, 0.15]
    )
    df['carbon_footprint_kg_co2'] = df['carbon_footprint_kg_co2'].round(0).astype(int)

    # R035: Supplier Performance Score (composite) - threshold: 75
    # Calculate from quality, delivery, sustainability
    df['performance_score'] = (
        df['quality_rating'] * 15 +  # Max 75 points from quality (5*15)
        df['delivery_reliability_pct'] * 0.15 +  # Max 15 points from delivery
        df['sustainability_score']  # Max 10 points from sustainability
    ).round(0).astype(int)

    # R015: Diverse Supplier flag (minority/women-owned)
    df['is_diverse_supplier'] = np.random.choice([True, False], size=len(df), p=[0.18, 0.82])

    # R016: Innovation Supplier flag
    df['is_innovation_supplier'] = df['innovation_score'] >= 70

    # R017: Local Content flag (for local content requirements)
    df['is_local_supplier'] = df['country'].isin(['USA', 'UK', 'Germany', 'France'])

    # R026: Certification compliance - has required certifications
    df['has_required_certifications'] = df['certifications'].apply(
        lambda x: 'ISO' in str(x) if pd.notna(x) else False
    )

    # R027: Last Audit Date
    base_date = datetime(2025, 1, 1)
    df['last_audit_date'] = [
        (base_date - timedelta(days=random.choice([30, 60, 90, 180, 270, 400]))).strftime('%Y-%m-%d')
        for _ in range(len(df))
    ]

    # R032: Ethical Sourcing Certification
    ethical_certs = ['SA8000', 'Fair Trade', 'Rainforest Alliance', 'None', 'None']
    df['ethical_certification'] = [random.choice(ethical_certs) for _ in range(len(df))]
    df['has_ethical_certification'] = df['ethical_certification'] != 'None'

    print(f"Added {len(df.columns) - 16} new columns to supplier_master.csv")

    # Save enhanced file
    df.to_csv(DATA_DIR / 'supplier_master.csv', index=False)
    print("Saved enhanced supplier_master.csv")

    return df


def enhance_supplier_contracts():
    """Add missing fields to supplier_contracts.csv for rules evaluation"""

    print("\nLoading supplier_contracts.csv...")
    df = pd.read_csv(DATA_DIR / 'supplier_contracts.csv')
    print(f"Loaded {len(df)} contracts")

    # Current columns:
    # Supplier_ID, Supplier_Name, Region, Sector, Category, SubCategory,
    # Contract_Start, Contract_End, Payment_Terms_Days, ESG_Score, Contract_Status

    # === NEW FIELDS NEEDED FOR RULES ===

    # R004: Days to Contract Expiry (calculated field)
    today = datetime.now()
    df['Contract_End'] = pd.to_datetime(df['Contract_End'])
    df['days_to_expiry'] = (df['Contract_End'] - today).dt.days
    df['days_to_expiry'] = df['days_to_expiry'].clip(lower=0)  # No negative days

    # R006: Price Variance from historical (threshold: 15%)
    df['price_variance_pct'] = np.random.choice(
        [np.random.uniform(0, 8), np.random.uniform(8, 14), np.random.uniform(15, 30)],
        size=len(df),
        p=[0.6, 0.3, 0.1]
    )
    df['price_variance_pct'] = df['price_variance_pct'].round(1)

    # R019: Price Benchmark Deviation (threshold: 10%)
    df['price_benchmark_deviation_pct'] = np.random.choice(
        [np.random.uniform(-5, 5), np.random.uniform(5, 9), np.random.uniform(10, 25)],
        size=len(df),
        p=[0.5, 0.35, 0.15]
    )
    df['price_benchmark_deviation_pct'] = df['price_benchmark_deviation_pct'].round(1)

    # R021: Contract Compliance Rate (threshold: 90%)
    df['contract_compliance_pct'] = np.random.choice(
        [np.random.uniform(92, 100), np.random.uniform(85, 92), np.random.uniform(70, 85)],
        size=len(df),
        p=[0.7, 0.2, 0.1]
    )
    df['contract_compliance_pct'] = df['contract_compliance_pct'].round(1)

    # R028: Price Escalation Cap (threshold: 5% annual max)
    df['has_price_escalation_cap'] = np.random.choice([True, False], size=len(df), p=[0.75, 0.25])
    df['price_escalation_cap_pct'] = df['has_price_escalation_cap'].apply(
        lambda x: round(np.random.uniform(3, 7), 1) if x else None
    )

    # R034: Contract Duration in years (threshold: 3 years for strategic)
    df['Contract_Start'] = pd.to_datetime(df['Contract_Start'])
    df['contract_duration_years'] = ((df['Contract_End'] - df['Contract_Start']).dt.days / 365).round(1)

    # R029: Is Backup Supplier
    df['is_backup_supplier'] = np.random.choice([True, False], size=len(df), p=[0.3, 0.7])

    # Convert Contract_End back to string for CSV
    df['Contract_End'] = df['Contract_End'].dt.strftime('%Y-%m-%d')
    df['Contract_Start'] = df['Contract_Start'].dt.strftime('%Y-%m-%d')

    print(f"Added {len(df.columns) - 11} new columns to supplier_contracts.csv")

    # Save enhanced file
    df.to_csv(DATA_DIR / 'supplier_contracts.csv', index=False)
    print("Saved enhanced supplier_contracts.csv")

    return df


def create_inventory_data():
    """Create inventory metrics CSV for inventory-related rules"""

    print("\nCreating inventory_metrics.csv...")

    # Load spend data to get categories
    spend_df = pd.read_csv(DATA_DIR / 'spend_data.csv')
    categories = spend_df[['Sector', 'Category', 'SubCategory']].drop_duplicates()

    inventory_data = []
    for _, row in categories.iterrows():
        inventory_data.append({
            'sector': row['Sector'],
            'category': row['Category'],
            'subcategory': row['SubCategory'],
            # R012: MOQ Months of Demand (threshold: 6 months)
            'moq_months_of_demand': round(np.random.choice(
                [np.random.uniform(1, 4), np.random.uniform(4, 6), np.random.uniform(6, 12)],
                p=[0.5, 0.35, 0.15]
            ), 1),
            # R014: Foreign Currency Spend % (threshold: 50%)
            'foreign_currency_spend_pct': round(np.random.choice(
                [np.random.uniform(10, 35), np.random.uniform(35, 50), np.random.uniform(50, 80)],
                p=[0.4, 0.4, 0.2]
            ), 1),
            # R022: Inventory Turnover (threshold: 6)
            'inventory_turnover': round(np.random.choice(
                [np.random.uniform(7, 12), np.random.uniform(5, 7), np.random.uniform(2, 5)],
                p=[0.5, 0.35, 0.15]
            ), 1),
            # Safety stock days
            'safety_stock_days': random.randint(15, 60),
            # Average inventory value
            'avg_inventory_value_usd': random.randint(50000, 500000)
        })

    df = pd.DataFrame(inventory_data)
    df.to_csv(DATA_DIR / 'inventory_metrics.csv', index=False)
    print(f"Created inventory_metrics.csv with {len(df)} category records")

    return df


def create_category_metrics():
    """Create category-level metrics for aggregated rules"""

    print("\nCreating category_metrics.csv...")

    # Load spend data
    spend_df = pd.read_csv(DATA_DIR / 'spend_data.csv')
    supplier_master = pd.read_csv(DATA_DIR / 'supplier_master.csv')

    # Aggregate by category
    categories = spend_df.groupby(['Sector', 'Category', 'SubCategory']).agg({
        'Spend_USD': 'sum',
        'Supplier_ID': 'nunique'
    }).reset_index()
    categories.columns = ['sector', 'category', 'subcategory', 'total_spend', 'supplier_count']

    # Add category-level metrics
    category_data = []
    for _, row in categories.iterrows():
        # Get suppliers for this category
        cat_suppliers = supplier_master[
            (supplier_master['sector'] == row['sector']) &
            (supplier_master['product_category'] == row['category'])
        ]

        diverse_count = cat_suppliers['is_diverse_supplier'].sum() if 'is_diverse_supplier' in cat_suppliers.columns else 0
        innovation_count = cat_suppliers['is_innovation_supplier'].sum() if 'is_innovation_supplier' in cat_suppliers.columns else 0
        local_count = cat_suppliers['is_local_supplier'].sum() if 'is_local_supplier' in cat_suppliers.columns else 0
        certified_count = cat_suppliers['has_required_certifications'].sum() if 'has_required_certifications' in cat_suppliers.columns else 0
        ethical_count = cat_suppliers['has_ethical_certification'].sum() if 'has_ethical_certification' in cat_suppliers.columns else 0

        total_in_cat = len(cat_suppliers) if len(cat_suppliers) > 0 else 1

        category_data.append({
            'sector': row['sector'],
            'category': row['category'],
            'subcategory': row['subcategory'],
            'total_spend': row['total_spend'],
            'supplier_count': row['supplier_count'],
            # R015: Diverse Supplier Spend % (threshold: 15%)
            'diverse_supplier_pct': round((diverse_count / total_in_cat) * 100, 1),
            # R016: Innovation Supplier Spend % (threshold: 10%)
            'innovation_supplier_pct': round((innovation_count / total_in_cat) * 100, 1),
            # R017: Local Content % (threshold: 30%)
            'local_content_pct': round((local_count / total_in_cat) * 100, 1),
            # R018: Qualified Supplier Count (threshold: 3)
            'qualified_supplier_count': max(1, int(row['supplier_count'] * 0.8)),
            # R026: Certified Suppliers % (threshold: 100%)
            'certified_suppliers_pct': round((certified_count / total_in_cat) * 100, 1),
            # R029: Backup Supplier Count (threshold: 1)
            'backup_supplier_count': random.randint(0, 3),
            # R032: Ethical Certified Suppliers % (threshold: 100%)
            'ethical_certified_pct': round((ethical_count / total_in_cat) * 100, 1),
            # R033: Low Spend Supplier Count (threshold: 20)
            'low_spend_supplier_count': random.randint(2, 25)
        })

    df = pd.DataFrame(category_data)
    df.to_csv(DATA_DIR / 'category_metrics.csv', index=False)
    print(f"Created category_metrics.csv with {len(df)} category records")

    return df


if __name__ == "__main__":
    print("=" * 60)
    print("ENHANCING SUPPLIER DATA FOR ALL 35 RULES")
    print("=" * 60)

    # Enhance existing files
    enhance_supplier_master()
    enhance_supplier_contracts()

    # Create new metric files
    create_inventory_data()
    create_category_metrics()

    print("\n" + "=" * 60)
    print("DATA ENHANCEMENT COMPLETE")
    print("=" * 60)
    print("\nNew/Updated files:")
    print("  - supplier_master.csv (enhanced with 12+ new fields)")
    print("  - supplier_contracts.csv (enhanced with 8+ new fields)")
    print("  - inventory_metrics.csv (new)")
    print("  - category_metrics.csv (new)")
