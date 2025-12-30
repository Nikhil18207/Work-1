"""
Spend Analyzer Agent
Calculates spend percentages, totals, breakdowns
"""

import sys
from pathlib import Path
from typing import Dict, Any
import pandas as pd

root_path = Path(__file__).parent.parent.parent.parent
if str(root_path) not in sys.path:
    sys.path.insert(0, str(root_path))

from backend.agents.base_agent import BaseAgent
from backend.engines.data_loader import DataLoader


class SpendAnalyzerAgent(BaseAgent):
    """
    Agent for analyzing spend data
    
    Input:
        - client_id: str (optional)
        - category: str (optional)
        - supplier_id: str (optional)
        - region: str (optional)
        
    Output:
        - total_spend: float
        - spend_by_supplier: Dict
        - spend_by_region: Dict
        - spend_by_category: Dict
        - transaction_count: int
        - average_transaction: float
        - time_period: Dict
    """
    
    def __init__(self):
        super().__init__(
            name="SpendAnalyzer",
            description="Analyzes spend data with detailed breakdowns"
        )
        self.data_loader = DataLoader()
    
    def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute spend analysis
        """
        try:
            self._log(f"Analyzing spend data: {input_data}")
            
            # Load spend data
            spend_df = self.data_loader.load_spend_data()
            
            # Apply filters
            filtered_df = spend_df.copy()
            
            filters_applied = []
            if input_data.get('client_id'):
                filtered_df = filtered_df[filtered_df['Client_ID'] == input_data['client_id']]
                filters_applied.append(f"Client: {input_data['client_id']}")
            
            if input_data.get('category'):
                filtered_df = filtered_df[filtered_df['Category'] == input_data['category']]
                filters_applied.append(f"Category: {input_data['category']}")
            
            if input_data.get('supplier_id'):
                filtered_df = filtered_df[filtered_df['Supplier_ID'] == input_data['supplier_id']]
                filters_applied.append(f"Supplier: {input_data['supplier_id']}")
            
            if input_data.get('region'):
                filtered_df = filtered_df[filtered_df['Supplier_Region'] == input_data['region']]
                filters_applied.append(f"Region: {input_data['region']}")
            
            if filtered_df.empty:
                return self._create_response(
                    success=False,
                    error="No data found matching the filters"
                )
            
            # Calculate metrics
            total_spend = filtered_df['Spend_USD'].sum()
            transaction_count = len(filtered_df)
            average_transaction = total_spend / transaction_count if transaction_count > 0 else 0
            
            # Spend by supplier
            spend_by_supplier = filtered_df.groupby(['Supplier_ID', 'Supplier_Name'])['Spend_USD'].agg([
                ('total', 'sum'),
                ('transactions', 'count'),
                ('average', 'mean')
            ]).reset_index()
            
            spend_by_supplier['percentage'] = (spend_by_supplier['total'] / total_spend * 100).round(2)
            spend_by_supplier = spend_by_supplier.sort_values('total', ascending=False)
            
            # Spend by region
            spend_by_region = filtered_df.groupby('Supplier_Region')['Spend_USD'].agg([
                ('total', 'sum'),
                ('transactions', 'count')
            ]).reset_index()
            
            spend_by_region['percentage'] = (spend_by_region['total'] / total_spend * 100).round(2)
            spend_by_region = spend_by_region.sort_values('total', ascending=False)
            
            # Spend by category
            spend_by_category = filtered_df.groupby('Category')['Spend_USD'].agg([
                ('total', 'sum'),
                ('transactions', 'count')
            ]).reset_index()
            
            spend_by_category['percentage'] = (spend_by_category['total'] / total_spend * 100).round(2)
            spend_by_category = spend_by_category.sort_values('total', ascending=False)
            
            # Time period
            filtered_df['Transaction_Date'] = pd.to_datetime(filtered_df['Transaction_Date'])
            time_period = {
                'start_date': filtered_df['Transaction_Date'].min().strftime('%Y-%m-%d'),
                'end_date': filtered_df['Transaction_Date'].max().strftime('%Y-%m-%d'),
                'duration_days': (filtered_df['Transaction_Date'].max() - filtered_df['Transaction_Date'].min()).days
            }
            
            # Format output
            result = {
                'filters_applied': filters_applied,
                'total_spend': round(total_spend, 2),
                'total_spend_formatted': f"${total_spend:,.2f}",
                'transaction_count': transaction_count,
                'average_transaction': round(average_transaction, 2),
                'average_transaction_formatted': f"${average_transaction:,.2f}",
                'time_period': time_period,
                'spend_by_supplier': spend_by_supplier.to_dict('records'),
                'spend_by_region': spend_by_region.to_dict('records'),
                'spend_by_category': spend_by_category.to_dict('records'),
                'top_supplier': {
                    'id': spend_by_supplier.iloc[0]['Supplier_ID'],
                    'name': spend_by_supplier.iloc[0]['Supplier_Name'],
                    'spend': round(spend_by_supplier.iloc[0]['total'], 2),
                    'percentage': spend_by_supplier.iloc[0]['percentage']
                } if not spend_by_supplier.empty else None
            }
            
            self._log(f"Analysis complete: ${total_spend:,.2f} across {transaction_count} transactions")
            
            return self._create_response(
                success=True,
                data=result,
                sources=['spend_data.csv']
            )
            
        except Exception as e:
            self._log(f"Error in spend analysis: {str(e)}", "ERROR")
            return self._create_response(
                success=False,
                error=str(e)
            )
