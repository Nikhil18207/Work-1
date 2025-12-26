"""
Data Loader
Loads and manages all data sources for the recommendation system
"""

import pandas as pd
import os
from typing import Dict, Any
from pathlib import Path


class DataLoader:
    """
    Loads and caches data from all sources:
    - Structured data (CSV files)
    - Supplier contracts
    - Rule book
    """

    def __init__(self, data_dir: str = None):
        """
        Initialize data loader
        
        Args:
            data_dir: Path to data directory (defaults to project data dir)
        """
        if data_dir is None:
            # Get project root
            current_file = Path(__file__)
            project_root = current_file.parent.parent.parent
            data_dir = project_root / 'data' / 'structured'
        
        self.data_dir = Path(data_dir)
        self._cache = {}

    def load_spend_data(self, force_reload: bool = False) -> pd.DataFrame:
        """
        Load spend data (Rice Bran Oil transactions)
        
        Returns:
            DataFrame with columns: Client_ID, Category, Supplier_ID, Supplier_Name,
                                   Supplier_Country, Supplier_Region, Transaction_Date, Spend_USD
        """
        if 'spend_data' not in self._cache or force_reload:
            file_path = self.data_dir / 'spend_data.csv'
            self._cache['spend_data'] = pd.read_csv(file_path)
            # Convert date column
            self._cache['spend_data']['Transaction_Date'] = pd.to_datetime(
                self._cache['spend_data']['Transaction_Date']
            )
        
        return self._cache['spend_data'].copy()

    def load_supplier_contracts(self, force_reload: bool = False) -> pd.DataFrame:
        """
        Load supplier contract data
        
        Returns:
            DataFrame with columns: Supplier_ID, Supplier_Name, Region, Product_Type,
                                   Contract_Start, Contract_End, Payment_Terms_Days, ESG_Score
        """
        if 'supplier_contracts' not in self._cache or force_reload:
            file_path = self.data_dir / 'supplier_contracts.csv'
            self._cache['supplier_contracts'] = pd.read_csv(file_path)
            # Convert date columns
            self._cache['supplier_contracts']['Contract_Start'] = pd.to_datetime(
                self._cache['supplier_contracts']['Contract_Start']
            )
            self._cache['supplier_contracts']['Contract_End'] = pd.to_datetime(
                self._cache['supplier_contracts']['Contract_End']
            )
        
        return self._cache['supplier_contracts'].copy()

    def load_rule_book(self, force_reload: bool = False) -> pd.DataFrame:
        """
        Load rule book
        
        Returns:
            DataFrame with columns: Rule_ID, Rule_Name, Rule_Description,
                                   Threshold_Value, Comparison_Logic, Risk_Level, Action_Recommendation
        """
        if 'rule_book' not in self._cache or force_reload:
            file_path = self.data_dir / 'rule_book.csv'
            self._cache['rule_book'] = pd.read_csv(file_path)
        
        return self._cache['rule_book'].copy()

    def load_client_master(self, force_reload: bool = False) -> pd.DataFrame:
        """Load client master data"""
        if 'client_master' not in self._cache or force_reload:
            file_path = self.data_dir / 'client_master.csv'
            self._cache['client_master'] = pd.read_csv(file_path)
        
        return self._cache['client_master'].copy()

    def load_supplier_master(self, force_reload: bool = False) -> pd.DataFrame:
        """Load supplier master data"""
        if 'supplier_master' not in self._cache or force_reload:
            file_path = self.data_dir / 'supplier_master.csv'
            self._cache['supplier_master'] = pd.read_csv(file_path)
        
        return self._cache['supplier_master'].copy()

    def load_pricing_benchmarks(self, force_reload: bool = False) -> pd.DataFrame:
        """Load pricing benchmarks"""
        if 'pricing_benchmarks' not in self._cache or force_reload:
            file_path = self.data_dir / 'pricing_benchmarks.csv'
            self._cache['pricing_benchmarks'] = pd.read_csv(file_path)
        
        return self._cache['pricing_benchmarks'].copy()

    def load_industry_benchmarks(self, force_reload: bool = False) -> pd.DataFrame:
        """
        Load industry benchmarks
        
        Returns:
            DataFrame with columns: Category, Metric, Industry_Benchmark, Our_Performance,
                                   Gap, Unit, Benchmark_Source, Last_Updated
        """
        if 'industry_benchmarks' not in self._cache or force_reload:
            file_path = self.data_dir / 'industry_benchmarks.csv'
            self._cache['industry_benchmarks'] = pd.read_csv(file_path)
            # Convert date column
            self._cache['industry_benchmarks']['Last_Updated'] = pd.to_datetime(
                self._cache['industry_benchmarks']['Last_Updated']
            )
        
        return self._cache['industry_benchmarks'].copy()
    
    def get_benchmark_analysis(self, category: str = None) -> Dict[str, Any]:
        """
        Get industry benchmark comparison for a category
        
        Args:
            category: Product category (e.g., 'Rice Bran Oil')
            
        Returns:
            Dictionary with benchmark analysis
        """
        benchmarks = self.load_industry_benchmarks()
        
        if category:
            benchmarks = benchmarks[benchmarks['Category'] == category]
        
        if len(benchmarks) == 0:
            return {
                "error": f"No benchmarks found for category: {category}",
                "category": category
            }
        
        # Group by category
        analysis = {
            "category": category or "All Categories",
            "metrics": []
        }
        
        for _, row in benchmarks.iterrows():
            metric_data = {
                "metric": row['Metric'],
                "industry_benchmark": row['Industry_Benchmark'],
                "our_performance": row['Our_Performance'],
                "gap": row['Gap'],
                "unit": row['Unit'],
                "source": row['Benchmark_Source'],
                "last_updated": str(row['Last_Updated'].date())
            }
            
            # Determine performance status
            if pd.notna(row['Gap']):
                if isinstance(row['Gap'], (int, float)):
                    if row['Gap'] > 0:
                        metric_data['status'] = 'Above Benchmark' if 'Cost' not in row['Metric'] else 'Below Industry'
                    elif row['Gap'] < 0:
                        metric_data['status'] = 'Below Benchmark' if 'Cost' not in row['Metric'] else 'Better than Industry'
                    else:
                        metric_data['status'] = 'At Benchmark'
                else:
                    metric_data['status'] = str(row['Gap'])
            
            analysis['metrics'].append(metric_data)
        
        # Calculate overall performance score
        numeric_gaps = [m['gap'] for m in analysis['metrics'] if isinstance(m.get('gap'), (int, float))]
        if numeric_gaps:
            avg_gap = sum(numeric_gaps) / len(numeric_gaps)
            analysis['overall_gap'] = round(avg_gap, 2)
            analysis['performance_summary'] = 'Above Industry Average' if avg_gap > 0 else 'Below Industry Average'
        
        return analysis

    def get_supplier_summary(self, supplier_id: str) -> Dict[str, Any]:
        """
        Get comprehensive supplier information
        
        Args:
            supplier_id: Supplier ID (e.g., 'S001')
            
        Returns:
            Dictionary with supplier details from all sources
        """
        spend_data = self.load_spend_data()
        contracts = self.load_supplier_contracts()
        
        # Get spend info
        supplier_spend = spend_data[spend_data['Supplier_ID'] == supplier_id]
        
        # Get contract info
        supplier_contract = contracts[contracts['Supplier_ID'] == supplier_id]
        
        if len(supplier_spend) == 0:
            return {"error": f"Supplier {supplier_id} not found in spend data"}
        
        summary = {
            "supplier_id": supplier_id,
            "supplier_name": supplier_spend.iloc[0]['Supplier_Name'],
            "country": supplier_spend.iloc[0]['Supplier_Country'],
            "region": supplier_spend.iloc[0]['Supplier_Region'],
            "total_spend": float(supplier_spend['Spend_USD'].sum()),
            "transaction_count": len(supplier_spend),
            "avg_transaction_size": float(supplier_spend['Spend_USD'].mean()),
        }
        
        # Add contract info if available
        if len(supplier_contract) > 0:
            contract = supplier_contract.iloc[0]
            summary.update({
                "contract_start": str(contract['Contract_Start']),
                "contract_end": str(contract['Contract_End']),
                "payment_terms_days": int(contract['Payment_Terms_Days']),
                "esg_score": int(contract['ESG_Score'])
            })
        
        return summary

    def get_regional_summary(self) -> Dict[str, Any]:
        """
        Get regional spend distribution
        
        Returns:
            Dictionary with regional spend breakdown
        """
        spend_data = self.load_spend_data()
        
        total_spend = spend_data['Spend_USD'].sum()
        regional_spend = spend_data.groupby('Supplier_Region')['Spend_USD'].agg(['sum', 'count'])
        regional_spend['percentage'] = (regional_spend['sum'] / total_spend * 100)
        
        summary = {
            "total_spend": float(total_spend),
            "regions": {}
        }
        
        for region in regional_spend.index:
            summary["regions"][region] = {
                "spend": float(regional_spend.loc[region, 'sum']),
                "percentage": round(float(regional_spend.loc[region, 'percentage']), 2),
                "transaction_count": int(regional_spend.loc[region, 'count'])
            }
        
        return summary

    def get_category_summary(self, category: str = None) -> Dict[str, Any]:
        """
        Get category spend summary
        
        Args:
            category: Product category (e.g., 'Rice Bran Oil')
            
        Returns:
            Dictionary with category spend breakdown
        """
        spend_data = self.load_spend_data()
        
        if category:
            spend_data = spend_data[spend_data['Category'] == category]
        
        total_spend = spend_data['Spend_USD'].sum()
        supplier_count = spend_data['Supplier_ID'].nunique()
        transaction_count = len(spend_data)
        
        # Top suppliers
        top_suppliers = spend_data.groupby(['Supplier_ID', 'Supplier_Name'])['Spend_USD'].sum()
        top_suppliers = top_suppliers.sort_values(ascending=False).head(5)
        
        summary = {
            "category": category or "All Categories",
            "total_spend": float(total_spend),
            "supplier_count": supplier_count,
            "transaction_count": transaction_count,
            "avg_transaction_size": float(spend_data['Spend_USD'].mean()),
            "top_suppliers": [
                {
                    "supplier_id": sid,
                    "supplier_name": sname,
                    "spend": float(spend),
                    "percentage": round(float(spend / total_spend * 100), 2)
                }
                for (sid, sname), spend in top_suppliers.items()
            ]
        }
        
        return summary

    def clear_cache(self):
        """Clear all cached data"""
        self._cache = {}


# Example usage
if __name__ == "__main__":
    import json
    
    # Initialize loader
    loader = DataLoader()
    
    print("=" * 80)
    print("DATA LOADER TEST")
    print("=" * 80)
    
    # Test spend data
    print("\n1. SPEND DATA")
    spend_df = loader.load_spend_data()
    print(f"Loaded {len(spend_df)} transactions")
    print(f"Columns: {list(spend_df.columns)}")
    print(f"\nFirst 3 rows:")
    print(spend_df.head(3))
    
    # Test supplier contracts
    print("\n2. SUPPLIER CONTRACTS")
    contracts_df = loader.load_supplier_contracts()
    print(f"Loaded {len(contracts_df)} supplier contracts")
    print(f"Columns: {list(contracts_df.columns)}")
    
    # Test regional summary
    print("\n3. REGIONAL SUMMARY")
    regional = loader.get_regional_summary()
    print(json.dumps(regional, indent=2))
    
    # Test supplier summary
    print("\n4. SUPPLIER SUMMARY (S001)")
    supplier = loader.get_supplier_summary('S001')
    print(json.dumps(supplier, indent=2))
    
    # Test category summary
    print("\n5. CATEGORY SUMMARY (Rice Bran Oil)")
    category = loader.get_category_summary('Rice Bran Oil')
    print(json.dumps(category, indent=2))
