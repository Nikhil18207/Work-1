"""
Pattern Detector Agent
Identifies spending patterns and anomalies
"""

import sys
from pathlib import Path
from typing import Dict, Any, List
import pandas as pd
import numpy as np

root_path = Path(__file__).parent.parent.parent.parent
if str(root_path) not in sys.path:
    sys.path.insert(0, str(root_path))

from backend.agents.base_agent import BaseAgent
from backend.engines.data_loader import DataLoader


class PatternDetectorAgent(BaseAgent):
    """
    Agent for detecting patterns in spend data
    
    Input:
        - client_id: str (optional)
        - category: str (optional)
        
    Output:
        - trends: Dict (increasing/decreasing/stable)
        - seasonality: Dict
        - anomalies: List[Dict]
        - price_volatility: Dict
    """
    
    def __init__(self):
        super().__init__(
            name="PatternDetector",
            description="Detects spending patterns, trends, and anomalies"
        )
        self.data_loader = DataLoader()
    
    def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute pattern detection
        """
        try:
            self._log(f"Detecting patterns: {input_data}")
            
            # Load spend data
            spend_df = self.data_loader.load_spend_data()
            
            # Apply filters
            filtered_df = spend_df.copy()
            
            if input_data.get('client_id'):
                filtered_df = filtered_df[filtered_df['Client_ID'] == input_data['client_id']]
            
            if input_data.get('category'):
                filtered_df = filtered_df[filtered_df['Category'] == input_data['category']]
            
            if filtered_df.empty:
                return self._create_response(
                    success=False,
                    error="No data found matching the filters"
                )
            
            # Convert dates
            filtered_df['Transaction_Date'] = pd.to_datetime(filtered_df['Transaction_Date'])
            filtered_df = filtered_df.sort_values('Transaction_Date')
            
            # Detect spend trend
            monthly_spend = filtered_df.groupby(filtered_df['Transaction_Date'].dt.to_period('M'))['Spend_USD'].sum()
            
            if len(monthly_spend) >= 2:
                first_half_avg = monthly_spend.iloc[:len(monthly_spend)//2].mean()
                second_half_avg = monthly_spend.iloc[len(monthly_spend)//2:].mean()
                trend_change = ((second_half_avg - first_half_avg) / first_half_avg * 100) if first_half_avg > 0 else 0
                
                if trend_change > 10:
                    trend = "INCREASING"
                    trend_explanation = f"Spend increased by {trend_change:.1f}% (${first_half_avg:,.0f} → ${second_half_avg:,.0f}/month)"
                elif trend_change < -10:
                    trend = "DECREASING"
                    trend_explanation = f"Spend decreased by {abs(trend_change):.1f}% (${first_half_avg:,.0f} → ${second_half_avg:,.0f}/month)"
                else:
                    trend = "STABLE"
                    trend_explanation = f"Spend stable at ~${second_half_avg:,.0f}/month (±{abs(trend_change):.1f}%)"
            else:
                trend = "INSUFFICIENT_DATA"
                trend_explanation = "Need more data points to detect trend"
                trend_change = 0
            
            # Detect price volatility
            price_by_supplier = filtered_df.groupby('Supplier_ID')['Spend_USD'].agg(['mean', 'std', 'count'])
            price_by_supplier['cv'] = (price_by_supplier['std'] / price_by_supplier['mean'] * 100).fillna(0)
            
            avg_volatility = price_by_supplier['cv'].mean()
            
            if avg_volatility > 20:
                volatility_level = "HIGH"
                volatility_explanation = f"⚠️ HIGH price volatility ({avg_volatility:.1f}% coefficient of variation)"
            elif avg_volatility > 10:
                volatility_level = "MEDIUM"
                volatility_explanation = f"⚡ MEDIUM price volatility ({avg_volatility:.1f}% CV)"
            else:
                volatility_level = "LOW"
                volatility_explanation = f"✅ LOW price volatility ({avg_volatility:.1f}% CV)"
            
            # Detect anomalies (transactions > 2 std dev from mean)
            mean_spend = filtered_df['Spend_USD'].mean()
            std_spend = filtered_df['Spend_USD'].std()
            
            anomalies = []
            for _, row in filtered_df.iterrows():
                z_score = (row['Spend_USD'] - mean_spend) / std_spend if std_spend > 0 else 0
                if abs(z_score) > 2:
                    anomalies.append({
                        'date': row['Transaction_Date'].strftime('%Y-%m-%d'),
                        'supplier': row['Supplier_Name'],
                        'amount': round(row['Spend_USD'], 2),
                        'z_score': round(z_score, 2),
                        'deviation': f"{((row['Spend_USD'] - mean_spend) / mean_spend * 100):.1f}% from average",
                        'type': 'UNUSUALLY_HIGH' if z_score > 0 else 'UNUSUALLY_LOW'
                    })
            
            # Supplier switching pattern
            supplier_changes = filtered_df.groupby('Supplier_ID').size()
            supplier_consistency = {
                'total_suppliers': len(supplier_changes),
                'primary_supplier': supplier_changes.idxmax() if not supplier_changes.empty else None,
                'primary_supplier_transactions': int(supplier_changes.max()) if not supplier_changes.empty else 0,
                'supplier_switching_rate': f"{(len(supplier_changes) - 1) / len(filtered_df) * 100:.1f}%" if len(filtered_df) > 0 else "0%"
            }
            
            result = {
                'trend': {
                    'direction': trend,
                    'change_percentage': round(trend_change, 2),
                    'explanation': trend_explanation
                },
                'volatility': {
                    'level': volatility_level,
                    'coefficient_of_variation': round(avg_volatility, 2),
                    'explanation': volatility_explanation
                },
                'anomalies': {
                    'count': len(anomalies),
                    'transactions': anomalies[:5]  # Top 5 anomalies
                },
                'supplier_consistency': supplier_consistency,
                'data_points_analyzed': len(filtered_df),
                'time_span_days': (filtered_df['Transaction_Date'].max() - filtered_df['Transaction_Date'].min()).days
            }
            
            self._log(f"Pattern detection complete: {trend} trend, {volatility_level} volatility, {len(anomalies)} anomalies")
            
            return self._create_response(
                success=True,
                data=result,
                sources=['spend_data.csv']
            )
            
        except Exception as e:
            self._log(f"Error in pattern detection: {str(e)}", "ERROR")
            return self._create_response(
                success=False,
                error=str(e)
            )
