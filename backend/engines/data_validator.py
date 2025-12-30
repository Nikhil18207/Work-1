"""
Data Validator Module
Validates uploaded client data (spend_data.csv and supplier_master.csv)
Ensures data quality before generating briefs
"""

import pandas as pd
from typing import Dict, Any, List, Tuple, Optional
from datetime import datetime
import io


class DataValidator:
    """
    Validates client-uploaded data files
    Returns validation results with errors, warnings, and suggestions
    """
    
    REQUIRED_SPEND_COLUMNS = [
        'Client_ID',
        'Category', 
        'Supplier_ID',
        'Supplier_Name',
        'Supplier_Country',
        'Supplier_Region',
        'Transaction_Date',
        'Spend_USD'
    ]
    
    REQUIRED_SUPPLIER_COLUMNS = [
        'supplier_id',
        'supplier_name',
        'region',
        'country',
        'product_category'
    ]
    
    OPTIONAL_SUPPLIER_COLUMNS = [
        'quality_rating',
        'certifications',
        'sustainability_score',
        'delivery_reliability_pct',
        'lead_time_days',
        'min_order_quantity',
        'payment_terms_offered',
        'years_in_business',
        'annual_capacity_tons'
    ]
    
    VALID_REGIONS = ['APAC', 'Europe', 'Americas', 'Middle East', 'Africa']
    
    def __init__(self):
        self.errors = []
        self.warnings = []
        self.info = []
    
    def validate_spend_data(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Validate spend data file
        
        Returns:
            Dictionary with is_valid, errors, warnings, and summary
        """
        self.errors = []
        self.warnings = []
        self.info = []
        
        if df is None or df.empty:
            self.errors.append("File is empty or could not be read")
            return self._build_result(False)
        
        self._check_required_columns(df, self.REQUIRED_SPEND_COLUMNS, "spend_data")
        
        if self.errors:
            return self._build_result(False)
        
        self._validate_client_id(df)
        self._validate_category(df)
        self._validate_supplier_id(df)
        self._validate_supplier_name(df)
        self._validate_country(df)
        self._validate_region(df)
        self._validate_date(df)
        self._validate_spend(df)
        
        summary = self._generate_spend_summary(df)
        
        is_valid = len(self.errors) == 0
        return self._build_result(is_valid, summary)
    
    def validate_supplier_master(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Validate supplier master file (optional file)
        
        Returns:
            Dictionary with is_valid, errors, warnings, and summary
        """
        self.errors = []
        self.warnings = []
        self.info = []
        
        if df is None or df.empty:
            self.warnings.append("Supplier master file is empty - using basic analysis only")
            return self._build_result(True)
        
        self._check_required_columns(df, self.REQUIRED_SUPPLIER_COLUMNS, "supplier_master")
        
        if self.errors:
            return self._build_result(False)
        
        missing_optional = [col for col in self.OPTIONAL_SUPPLIER_COLUMNS if col not in df.columns]
        if missing_optional:
            self.info.append(f"Optional columns not provided: {', '.join(missing_optional)}")
        
        if 'quality_rating' in df.columns:
            invalid_ratings = df[(df['quality_rating'] < 0) | (df['quality_rating'] > 5)]['quality_rating'].count()
            if invalid_ratings > 0:
                self.warnings.append(f"{invalid_ratings} rows have quality_rating outside 0-5 range")
        
        if 'sustainability_score' in df.columns:
            invalid_scores = df[(df['sustainability_score'] < 0) | (df['sustainability_score'] > 10)]['sustainability_score'].count()
            if invalid_scores > 0:
                self.warnings.append(f"{invalid_scores} rows have sustainability_score outside 0-10 range")
        
        summary = {
            'total_suppliers': len(df),
            'unique_categories': df['product_category'].nunique() if 'product_category' in df.columns else 0,
            'unique_countries': df['country'].nunique() if 'country' in df.columns else 0
        }
        
        is_valid = len(self.errors) == 0
        return self._build_result(is_valid, summary)
    
    def _check_required_columns(self, df: pd.DataFrame, required: List[str], file_type: str):
        """Check if all required columns are present"""
        missing = [col for col in required if col not in df.columns]
        if missing:
            self.errors.append(f"Missing required columns in {file_type}: {', '.join(missing)}")
            
        present = [col for col in required if col in df.columns]
        self.info.append(f"Found {len(present)}/{len(required)} required columns")
    
    def _validate_client_id(self, df: pd.DataFrame):
        """Validate Client_ID column"""
        null_count = df['Client_ID'].isna().sum()
        if null_count > 0:
            self.errors.append(f"{null_count} rows have missing Client_ID")
        
        unique_clients = df['Client_ID'].nunique()
        self.info.append(f"Found {unique_clients} unique client(s)")
    
    def _validate_category(self, df: pd.DataFrame):
        """Validate Category column"""
        null_count = df['Category'].isna().sum()
        if null_count > 0:
            self.errors.append(f"{null_count} rows have missing Category")
        
        unique_categories = df['Category'].nunique()
        self.info.append(f"Found {unique_categories} unique categories")
    
    def _validate_supplier_id(self, df: pd.DataFrame):
        """Validate Supplier_ID column"""
        null_count = df['Supplier_ID'].isna().sum()
        if null_count > 0:
            self.warnings.append(f"{null_count} rows have missing Supplier_ID")
    
    def _validate_supplier_name(self, df: pd.DataFrame):
        """Validate Supplier_Name column"""
        null_count = df['Supplier_Name'].isna().sum()
        if null_count > 0:
            self.errors.append(f"{null_count} rows have missing Supplier_Name")
        
        unique_suppliers = df['Supplier_Name'].nunique()
        self.info.append(f"Found {unique_suppliers} unique suppliers")
    
    def _validate_country(self, df: pd.DataFrame):
        """Validate Supplier_Country column"""
        null_count = df['Supplier_Country'].isna().sum()
        if null_count > 0:
            self.warnings.append(f"{null_count} rows have missing Supplier_Country")
        
        unique_countries = df['Supplier_Country'].nunique()
        self.info.append(f"Found {unique_countries} unique countries")
    
    def _validate_region(self, df: pd.DataFrame):
        """Validate Supplier_Region column"""
        null_count = df['Supplier_Region'].isna().sum()
        if null_count > 0:
            self.warnings.append(f"{null_count} rows have missing Supplier_Region")
        
        invalid_regions = df[~df['Supplier_Region'].isin(self.VALID_REGIONS)]['Supplier_Region'].unique()
        if len(invalid_regions) > 0:
            self.warnings.append(f"Non-standard regions found: {', '.join(str(r) for r in invalid_regions[:5])}")
    
    def _validate_date(self, df: pd.DataFrame):
        """Validate Transaction_Date column"""
        null_count = df['Transaction_Date'].isna().sum()
        if null_count > 0:
            self.warnings.append(f"{null_count} rows have missing Transaction_Date")
        
        try:
            df['Transaction_Date'] = pd.to_datetime(df['Transaction_Date'], errors='coerce')
            invalid_dates = df['Transaction_Date'].isna().sum()
            if invalid_dates > 0:
                self.warnings.append(f"{invalid_dates} rows have invalid date format")
        except Exception:
            self.warnings.append("Could not parse Transaction_Date - will use as-is")
    
    def _validate_spend(self, df: pd.DataFrame):
        """Validate Spend_USD column"""
        null_count = df['Spend_USD'].isna().sum()
        if null_count > 0:
            self.errors.append(f"{null_count} rows have missing Spend_USD")
        
        try:
            df['Spend_USD'] = pd.to_numeric(df['Spend_USD'], errors='coerce')
            negative_spend = (df['Spend_USD'] < 0).sum()
            if negative_spend > 0:
                self.warnings.append(f"{negative_spend} rows have negative Spend_USD values")
            
            zero_spend = (df['Spend_USD'] == 0).sum()
            if zero_spend > 0:
                self.warnings.append(f"{zero_spend} rows have zero Spend_USD")
        except Exception:
            self.errors.append("Could not parse Spend_USD as numeric values")
    
    def _generate_spend_summary(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Generate summary statistics for spend data"""
        try:
            return {
                'total_rows': len(df),
                'total_spend': float(df['Spend_USD'].sum()),
                'unique_clients': int(df['Client_ID'].nunique()),
                'unique_categories': int(df['Category'].nunique()),
                'unique_suppliers': int(df['Supplier_Name'].nunique()),
                'unique_countries': int(df['Supplier_Country'].nunique()),
                'date_range': {
                    'min': str(df['Transaction_Date'].min()),
                    'max': str(df['Transaction_Date'].max())
                },
                'categories': df['Category'].unique().tolist()
            }
        except Exception as e:
            return {'error': str(e)}
    
    def _build_result(self, is_valid: bool, summary: Dict = None) -> Dict[str, Any]:
        """Build validation result dictionary"""
        return {
            'is_valid': is_valid,
            'errors': self.errors,
            'warnings': self.warnings,
            'info': self.info,
            'summary': summary or {},
            'can_proceed': is_valid and len(self.errors) == 0
        }
    
    @staticmethod
    def parse_csv_from_upload(uploaded_file) -> Tuple[Optional[pd.DataFrame], Optional[str]]:
        """
        Parse uploaded file to DataFrame
        
        Returns:
            Tuple of (DataFrame, error_message)
        """
        try:
            if uploaded_file is None:
                return None, "No file uploaded"
            
            content = uploaded_file.getvalue()
            df = pd.read_csv(io.BytesIO(content))
            return df, None
        except Exception as e:
            return None, f"Error reading file: {str(e)}"


def validate_client_upload(
    spend_file,
    supplier_file=None
) -> Dict[str, Any]:
    """
    Main function to validate client uploaded files
    
    Args:
        spend_file: Uploaded spend_data.csv file
        supplier_file: Optional uploaded supplier_master.csv file
        
    Returns:
        Validation results dictionary
    """
    validator = DataValidator()
    
    spend_df, spend_error = DataValidator.parse_csv_from_upload(spend_file)
    if spend_error:
        return {
            'is_valid': False,
            'spend_validation': {'is_valid': False, 'errors': [spend_error]},
            'supplier_validation': None,
            'can_proceed': False
        }
    
    spend_result = validator.validate_spend_data(spend_df)
    
    supplier_result = None
    supplier_df = None
    if supplier_file:
        supplier_df, supplier_error = DataValidator.parse_csv_from_upload(supplier_file)
        if supplier_error:
            supplier_result = {'is_valid': False, 'errors': [supplier_error], 'warnings': []}
        else:
            supplier_result = validator.validate_supplier_master(supplier_df)
    
    can_proceed = spend_result['is_valid']
    
    return {
        'is_valid': can_proceed,
        'spend_validation': spend_result,
        'supplier_validation': supplier_result,
        'spend_df': spend_df,
        'supplier_df': supplier_df,
        'can_proceed': can_proceed
    }


if __name__ == "__main__":
    validator = DataValidator()
    
    sample_spend = pd.DataFrame({
        'Client_ID': ['C001', 'C001', 'C001'],
        'Category': ['Rice Bran Oil', 'Rice Bran Oil', 'Rice Bran Oil'],
        'Supplier_ID': ['S001', 'S002', 'S003'],
        'Supplier_Name': ['Supplier A', 'Supplier B', 'Supplier C'],
        'Supplier_Country': ['Malaysia', 'Vietnam', 'India'],
        'Supplier_Region': ['APAC', 'APAC', 'APAC'],
        'Transaction_Date': ['2025-01-15', '2025-02-20', '2025-03-10'],
        'Spend_USD': [500000, 300000, 200000]
    })
    
    result = validator.validate_spend_data(sample_spend)
    
    print("="*60)
    print("DATA VALIDATION TEST")
    print("="*60)
    print(f"Is Valid: {result['is_valid']}")
    print(f"Errors: {result['errors']}")
    print(f"Warnings: {result['warnings']}")
    print(f"Info: {result['info']}")
    print(f"Summary: {result['summary']}")
