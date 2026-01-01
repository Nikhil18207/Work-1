"""
Data Loader
Loads and manages all data sources for the recommendation system
"""

import pandas as pd
import os
from typing import Dict, Any, List, Optional
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
    
    def set_spend_data(self, df: pd.DataFrame):
        """
        Inject custom spend data DataFrame (for user uploads)
        This overrides the default CSV file loading.
        """
        # Ensure date column is datetime
        if 'Transaction_Date' in df.columns:
            df['Transaction_Date'] = pd.to_datetime(df['Transaction_Date'])
        self._cache['spend_data'] = df
    
    def set_supplier_master(self, df: pd.DataFrame):
        """
        Inject custom supplier master DataFrame (for user uploads)
        This overrides the default CSV file loading.
        """
        self._cache['supplier_master'] = df

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

    # ========================================================================
    # HIERARCHICAL INDUSTRY TAXONOMY METHODS
    # Support for Sector > Category > SubCategory structure
    # ========================================================================

    def load_industry_taxonomy(self, force_reload: bool = False) -> pd.DataFrame:
        """
        Load industry taxonomy (Sector > Category > SubCategory hierarchy)

        Returns:
            DataFrame with columns: Sector_ID, Sector_Name, Category_ID, Category_Name,
                                   SubCategory_ID, SubCategory_Name, Description,
                                   Risk_Profile, Strategic_Importance
        """
        if 'industry_taxonomy' not in self._cache or force_reload:
            file_path = self.data_dir / 'industry_taxonomy.csv'
            if file_path.exists():
                self._cache['industry_taxonomy'] = pd.read_csv(file_path)
            else:
                # Return empty DataFrame if file doesn't exist
                self._cache['industry_taxonomy'] = pd.DataFrame()

        return self._cache['industry_taxonomy'].copy()

    def get_all_sectors(self) -> List[Dict[str, Any]]:
        """
        Get all available sectors with their categories

        Returns:
            List of sector dictionaries with nested categories
        """
        spend_data = self.load_spend_data()

        if 'Sector' not in spend_data.columns:
            # Fallback for old data format
            return self._get_sectors_from_categories()

        sectors = []
        for sector in spend_data['Sector'].unique():
            sector_data = spend_data[spend_data['Sector'] == sector]
            sector_spend = float(sector_data['Spend_USD'].sum())

            categories = []
            for category in sector_data['Category'].unique():
                cat_data = sector_data[sector_data['Category'] == category]
                cat_spend = float(cat_data['Spend_USD'].sum())

                subcategories = []
                if 'SubCategory' in cat_data.columns:
                    for subcat in cat_data['SubCategory'].unique():
                        subcat_data = cat_data[cat_data['SubCategory'] == subcat]
                        subcategories.append({
                            'name': subcat,
                            'spend': float(subcat_data['Spend_USD'].sum()),
                            'suppliers': int(subcat_data['Supplier_ID'].nunique())
                        })

                categories.append({
                    'name': category,
                    'spend': cat_spend,
                    'suppliers': int(cat_data['Supplier_ID'].nunique()),
                    'subcategories': subcategories
                })

            sectors.append({
                'name': sector,
                'spend': sector_spend,
                'suppliers': int(sector_data['Supplier_ID'].nunique()),
                'categories': categories
            })

        return sorted(sectors, key=lambda x: x['spend'], reverse=True)

    def _get_sectors_from_categories(self) -> List[Dict[str, Any]]:
        """Fallback method to infer sectors from category names"""
        spend_data = self.load_spend_data()

        # Map categories to sectors based on naming patterns
        sector_mapping = {
            'Food & Beverages': ['Oil', 'Rice', 'Wheat', 'Coffee', 'Tea', 'Sugar', 'Dairy',
                               'Poultry', 'Beef', 'Seafood', 'Protein', 'Grain', 'Spice'],
            'Information Technology': ['IT', 'Hardware', 'Software', 'Cloud', 'Cyber',
                                       'Telecom', 'Network', 'Server', 'Laptop', 'SaaS'],
            'Manufacturing & Industrial': ['Steel', 'Aluminum', 'Copper', 'Plastic',
                                           'Chemical', 'Manufacturing', 'Industrial',
                                           'Machinery', 'Robot', 'MRO'],
            'Healthcare & Life Sciences': ['Pharma', 'Medical', 'Health', 'Drug', 'Vaccine'],
            'Energy & Utilities': ['Energy', 'Electricity', 'Gas', 'Solar', 'Wind',
                                   'Renewable', 'Fuel', 'Battery'],
            'Construction & Real Estate': ['Construction', 'Building', 'Cement', 'Concrete',
                                           'Lumber', 'HVAC', 'Plumbing'],
            'Logistics & Transportation': ['Logistics', 'Freight', 'Warehouse', 'Fleet',
                                           'Transport', 'Shipping'],
            'Professional Services': ['Consulting', 'Legal', 'Account', 'Marketing',
                                     'PR', 'Advertising', 'Financial'],
            'Facilities & Corporate': ['Office', 'Facility', 'Cleaning', 'Security',
                                       'Travel', 'Event'],
            'Human Resources': ['HR', 'Staffing', 'Recruit', 'Training', 'Payroll']
        }

        def get_sector(category_name):
            cat_lower = category_name.lower()
            for sector, keywords in sector_mapping.items():
                if any(kw.lower() in cat_lower for kw in keywords):
                    return sector
            return 'Other'

        spend_data['_inferred_sector'] = spend_data['Category'].apply(get_sector)

        sectors = []
        for sector in spend_data['_inferred_sector'].unique():
            sector_data = spend_data[spend_data['_inferred_sector'] == sector]

            categories = []
            for category in sector_data['Category'].unique():
                cat_data = sector_data[sector_data['Category'] == category]
                categories.append({
                    'name': category,
                    'spend': float(cat_data['Spend_USD'].sum()),
                    'suppliers': int(cat_data['Supplier_ID'].nunique()),
                    'subcategories': []
                })

            sectors.append({
                'name': sector,
                'spend': float(sector_data['Spend_USD'].sum()),
                'suppliers': int(sector_data['Supplier_ID'].nunique()),
                'categories': sorted(categories, key=lambda x: x['spend'], reverse=True)
            })

        return sorted(sectors, key=lambda x: x['spend'], reverse=True)

    def get_sector_summary(self, sector: str) -> Dict[str, Any]:
        """
        Get detailed summary for a specific sector

        Args:
            sector: Sector name (e.g., 'Food & Beverages')

        Returns:
            Dictionary with sector details, categories, and spend breakdown
        """
        spend_data = self.load_spend_data()

        if 'Sector' not in spend_data.columns:
            return {"error": "Sector data not available. Using legacy format."}

        sector_data = spend_data[spend_data['Sector'] == sector]

        if len(sector_data) == 0:
            return {"error": f"Sector '{sector}' not found"}

        total_spend = float(sector_data['Spend_USD'].sum())

        # Get category breakdown
        category_breakdown = sector_data.groupby('Category').agg({
            'Spend_USD': 'sum',
            'Supplier_ID': 'nunique',
            'Supplier_Country': lambda x: list(x.unique())
        }).reset_index()

        categories = []
        for _, row in category_breakdown.iterrows():
            categories.append({
                'name': row['Category'],
                'spend': float(row['Spend_USD']),
                'percentage': round(float(row['Spend_USD'] / total_spend * 100), 2),
                'suppliers': int(row['Supplier_ID']),
                'countries': row['Supplier_Country']
            })

        # Get regional breakdown
        regional_breakdown = sector_data.groupby('Supplier_Region')['Spend_USD'].sum()
        regions = {
            region: {
                'spend': float(spend),
                'percentage': round(float(spend / total_spend * 100), 2)
            }
            for region, spend in regional_breakdown.items()
        }

        return {
            'sector': sector,
            'total_spend': total_spend,
            'total_suppliers': int(sector_data['Supplier_ID'].nunique()),
            'total_categories': int(sector_data['Category'].nunique()),
            'categories': sorted(categories, key=lambda x: x['spend'], reverse=True),
            'regions': regions
        }

    def get_subcategory_data(
        self,
        client_id: str = None,
        subcategory: str = None,
        category: str = None
    ) -> pd.DataFrame:
        """
        Get spend data filtered by subcategory (or category for backward compatibility)

        Args:
            client_id: Optional client filter
            subcategory: SubCategory name (e.g., 'Rice Bran Oil')
            category: Category name (falls back if SubCategory not available)

        Returns:
            Filtered DataFrame
        """
        spend_data = self.load_spend_data()

        if client_id:
            spend_data = spend_data[spend_data['Client_ID'] == client_id]

        # Try SubCategory first, then Category
        if 'SubCategory' in spend_data.columns and subcategory:
            spend_data = spend_data[spend_data['SubCategory'] == subcategory]
        elif category:
            spend_data = spend_data[spend_data['Category'] == category]

        return spend_data

    def get_hierarchy_path(self, subcategory: str) -> Dict[str, str]:
        """
        Get the full hierarchy path for a subcategory

        Args:
            subcategory: SubCategory name (e.g., 'Rice Bran Oil')

        Returns:
            Dictionary with sector, category, subcategory
        """
        spend_data = self.load_spend_data()

        if 'SubCategory' not in spend_data.columns:
            # Fallback for old format
            return {
                'sector': 'Unknown',
                'category': subcategory,
                'subcategory': subcategory
            }

        subcat_data = spend_data[spend_data['SubCategory'] == subcategory]

        if len(subcat_data) == 0:
            # Try matching on Category instead
            subcat_data = spend_data[spend_data['Category'] == subcategory]

        if len(subcat_data) == 0:
            return {
                'sector': 'Unknown',
                'category': 'Unknown',
                'subcategory': subcategory
            }

        return {
            'sector': subcat_data.iloc[0].get('Sector', 'Unknown'),
            'category': subcat_data.iloc[0].get('Category', 'Unknown'),
            'subcategory': subcat_data.iloc[0].get('SubCategory', subcategory)
        }

    def search_categories(self, query: str) -> List[Dict[str, Any]]:
        """
        Search across sectors, categories, and subcategories

        Args:
            query: Search string

        Returns:
            List of matching items with their hierarchy
        """
        spend_data = self.load_spend_data()
        query_lower = query.lower()

        results = []

        # Search in Sectors
        if 'Sector' in spend_data.columns:
            for sector in spend_data['Sector'].unique():
                if query_lower in sector.lower():
                    results.append({
                        'type': 'sector',
                        'name': sector,
                        'path': sector,
                        'spend': float(spend_data[spend_data['Sector'] == sector]['Spend_USD'].sum())
                    })

        # Search in Categories
        for category in spend_data['Category'].unique():
            if query_lower in category.lower():
                sector = spend_data[spend_data['Category'] == category]['Sector'].iloc[0] if 'Sector' in spend_data.columns else 'N/A'
                results.append({
                    'type': 'category',
                    'name': category,
                    'path': f"{sector} > {category}",
                    'spend': float(spend_data[spend_data['Category'] == category]['Spend_USD'].sum())
                })

        # Search in SubCategories
        if 'SubCategory' in spend_data.columns:
            for subcat in spend_data['SubCategory'].unique():
                if query_lower in subcat.lower():
                    row = spend_data[spend_data['SubCategory'] == subcat].iloc[0]
                    results.append({
                        'type': 'subcategory',
                        'name': subcat,
                        'path': f"{row.get('Sector', 'N/A')} > {row['Category']} > {subcat}",
                        'spend': float(spend_data[spend_data['SubCategory'] == subcat]['Spend_USD'].sum())
                    })

        return sorted(results, key=lambda x: x['spend'], reverse=True)

    def resolve_category_input(
        self,
        input_value: str,
        client_id: str = None
    ) -> Dict[str, Any]:
        """
        Robust category resolver that handles ANY input - sector, category, or subcategory.

        This is the MAIN method to use when you have ambiguous category input.
        It will:
        1. Search across all hierarchy levels (Sector, Category, SubCategory)
        2. Determine what level the input matches
        3. Return filtered spend data with proper hierarchy metadata
        4. Handle partial/fuzzy matching if exact match not found

        Args:
            input_value: Any category-related input (sector, category, or subcategory name)
            client_id: Optional client filter

        Returns:
            Dictionary with:
                - success: bool
                - match_type: 'sector' | 'category' | 'subcategory' | 'none'
                - hierarchy: {sector, category, subcategory} - resolved hierarchy
                - spend_data: filtered DataFrame
                - total_spend: float
                - supplier_count: int
                - suppliers: list of supplier dicts with spend breakdown
                - regions: regional spend breakdown
                - error: str (if success=False)
        """
        if not input_value:
            return {
                'success': False,
                'match_type': 'none',
                'error': 'No input value provided'
            }

        spend_data = self.load_spend_data()
        supplier_master = self.load_supplier_master()

        if client_id:
            spend_data = spend_data[spend_data['Client_ID'] == client_id]

        input_lower = input_value.strip().lower()

        # Strategy 1: Try exact match on SubCategory (most specific)
        if 'SubCategory' in spend_data.columns:
            for subcat in spend_data['SubCategory'].dropna().unique():
                if subcat.lower() == input_lower:
                    return self._build_resolved_response(
                        spend_data[spend_data['SubCategory'] == subcat],
                        supplier_master,
                        'subcategory',
                        subcat
                    )

        # Strategy 2: Try exact match on Category
        for category in spend_data['Category'].dropna().unique():
            if category.lower() == input_lower:
                return self._build_resolved_response(
                    spend_data[spend_data['Category'] == category],
                    supplier_master,
                    'category',
                    category
                )

        # Strategy 3: Try exact match on Sector
        if 'Sector' in spend_data.columns:
            for sector in spend_data['Sector'].dropna().unique():
                if sector.lower() == input_lower:
                    return self._build_resolved_response(
                        spend_data[spend_data['Sector'] == sector],
                        supplier_master,
                        'sector',
                        sector
                    )

        # Strategy 4: Try partial/fuzzy matching (contains search)
        # Check subcategory first (most specific)
        if 'SubCategory' in spend_data.columns:
            for subcat in spend_data['SubCategory'].dropna().unique():
                if input_lower in subcat.lower() or subcat.lower() in input_lower:
                    return self._build_resolved_response(
                        spend_data[spend_data['SubCategory'] == subcat],
                        supplier_master,
                        'subcategory',
                        subcat
                    )

        # Check category
        for category in spend_data['Category'].dropna().unique():
            if input_lower in category.lower() or category.lower() in input_lower:
                return self._build_resolved_response(
                    spend_data[spend_data['Category'] == category],
                    supplier_master,
                    'category',
                    category
                )

        # Check sector
        if 'Sector' in spend_data.columns:
            for sector in spend_data['Sector'].dropna().unique():
                if input_lower in sector.lower() or sector.lower() in input_lower:
                    return self._build_resolved_response(
                        spend_data[spend_data['Sector'] == sector],
                        supplier_master,
                        'sector',
                        sector
                    )

        # Strategy 5: Check supplier_master for matching product_category or subcategory
        if not supplier_master.empty:
            # Check subcategory in supplier_master
            if 'subcategory' in supplier_master.columns:
                for subcat in supplier_master['subcategory'].dropna().unique():
                    if input_lower == subcat.lower() or input_lower in subcat.lower():
                        # Find matching spend data through supplier matching
                        matching_suppliers = supplier_master[
                            supplier_master['subcategory'].str.lower() == subcat.lower()
                        ]['supplier_name'].unique()

                        matched_spend = spend_data[
                            spend_data['Supplier_Name'].isin(matching_suppliers)
                        ]

                        if not matched_spend.empty:
                            return self._build_resolved_response(
                                matched_spend,
                                supplier_master,
                                'subcategory',
                                subcat
                            )

            # Check product_category in supplier_master
            if 'product_category' in supplier_master.columns:
                for prod_cat in supplier_master['product_category'].dropna().unique():
                    if input_lower == prod_cat.lower() or input_lower in prod_cat.lower():
                        matching_suppliers = supplier_master[
                            supplier_master['product_category'].str.lower() == prod_cat.lower()
                        ]['supplier_name'].unique()

                        matched_spend = spend_data[
                            spend_data['Supplier_Name'].isin(matching_suppliers)
                        ]

                        if not matched_spend.empty:
                            return self._build_resolved_response(
                                matched_spend,
                                supplier_master,
                                'category',
                                prod_cat
                            )

        # No match found
        return {
            'success': False,
            'match_type': 'none',
            'error': f"Could not resolve '{input_value}' to any sector, category, or subcategory",
            'suggestions': self._get_suggestions(input_value, spend_data)
        }

    def _build_resolved_response(
        self,
        filtered_data: pd.DataFrame,
        supplier_master: pd.DataFrame,
        match_type: str,
        matched_value: str
    ) -> Dict[str, Any]:
        """
        Build a standardized response for resolved category data
        """
        if filtered_data.empty:
            return {
                'success': False,
                'match_type': match_type,
                'error': f"No spend data found for {match_type}: {matched_value}"
            }

        # Build hierarchy from the data
        hierarchy = {
            'sector': None,
            'category': None,
            'subcategory': None
        }

        first_row = filtered_data.iloc[0]

        if 'Sector' in filtered_data.columns:
            hierarchy['sector'] = first_row.get('Sector')
        if 'Category' in filtered_data.columns:
            hierarchy['category'] = first_row.get('Category')
        if 'SubCategory' in filtered_data.columns:
            hierarchy['subcategory'] = first_row.get('SubCategory')

        # Override with matched value at appropriate level
        if match_type == 'sector':
            hierarchy['sector'] = matched_value
        elif match_type == 'category':
            hierarchy['category'] = matched_value
        elif match_type == 'subcategory':
            hierarchy['subcategory'] = matched_value

        # Calculate metrics
        total_spend = float(filtered_data['Spend_USD'].sum())

        # Get supplier breakdown
        supplier_spend = filtered_data.groupby(['Supplier_ID', 'Supplier_Name']).agg({
            'Spend_USD': 'sum',
            'Supplier_Region': 'first',
            'Supplier_Country': 'first'
        }).reset_index()

        supplier_spend['percentage'] = (supplier_spend['Spend_USD'] / total_spend * 100).round(2)
        supplier_spend = supplier_spend.sort_values('Spend_USD', ascending=False)

        suppliers = []
        for _, row in supplier_spend.iterrows():
            supplier_info = {
                'supplier_id': row['Supplier_ID'],
                'supplier_name': row['Supplier_Name'],
                'spend': float(row['Spend_USD']),
                'percentage': float(row['percentage']),
                'region': row['Supplier_Region'],
                'country': row['Supplier_Country']
            }

            # Add additional info from supplier_master if available
            if not supplier_master.empty:
                master_match = supplier_master[
                    supplier_master['supplier_name'] == row['Supplier_Name']
                ]
                if not master_match.empty:
                    master_row = master_match.iloc[0]
                    supplier_info['product_category'] = master_row.get('product_category')
                    supplier_info['subcategory'] = master_row.get('subcategory')
                    supplier_info['sector'] = master_row.get('sector')

            suppliers.append(supplier_info)

        # Get regional breakdown
        regional_spend = filtered_data.groupby('Supplier_Region')['Spend_USD'].sum()
        regions = {
            region: {
                'spend': float(spend),
                'percentage': round(float(spend / total_spend * 100), 2)
            }
            for region, spend in regional_spend.items()
        }

        return {
            'success': True,
            'match_type': match_type,
            'matched_value': matched_value,
            'hierarchy': hierarchy,
            'total_spend': total_spend,
            'supplier_count': len(suppliers),
            'suppliers': suppliers,
            'regions': regions,
            'spend_data': filtered_data
        }

    def _get_suggestions(self, input_value: str, spend_data: pd.DataFrame) -> List[str]:
        """
        Get suggestions when no exact match is found
        """
        suggestions = []
        input_lower = input_value.lower()

        # Get all unique values
        all_values = set()

        if 'Sector' in spend_data.columns:
            all_values.update(spend_data['Sector'].dropna().unique())
        all_values.update(spend_data['Category'].dropna().unique())
        if 'SubCategory' in spend_data.columns:
            all_values.update(spend_data['SubCategory'].dropna().unique())

        # Find similar values (simple similarity check)
        for value in all_values:
            value_lower = value.lower()
            # Check for word overlap
            input_words = set(input_lower.split())
            value_words = set(value_lower.split())

            if input_words & value_words:  # Any common words
                suggestions.append(value)

        return suggestions[:5]  # Return top 5 suggestions


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
