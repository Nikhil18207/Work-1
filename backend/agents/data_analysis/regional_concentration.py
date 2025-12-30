"""
Regional Concentration Agent
Identifies regional concentration risks
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


class RegionalConcentrationAgent(BaseAgent):
    """
    Agent for analyzing regional concentration risks
    
    Input:
        - client_id: str (optional)
        - category: str (optional)
        
    Output:
        - concentration_score: float (0-100, higher = more concentrated/risky)
        - regional_breakdown: List[Dict]
        - risk_level: str (LOW/MEDIUM/HIGH)
        - diversification_recommendation: str
    """
    
    def __init__(self):
        super().__init__(
            name="RegionalConcentration",
            description="Analyzes regional concentration and diversification risks"
        )
        self.data_loader = DataLoader()
        
        # Risk thresholds
        self.THRESHOLDS = {
            'single_region_high_risk': 70,  # >70% in one region = HIGH RISK
            'single_region_medium_risk': 50,  # >50% in one region = MEDIUM RISK
            'herfindahl_high_risk': 5000,  # Herfindahl index > 5000 = HIGH RISK
            'herfindahl_medium_risk': 2500  # Herfindahl index > 2500 = MEDIUM RISK
        }
    
    def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute regional concentration analysis
        """
        try:
            self._log(f"Analyzing regional concentration: {input_data}")
            
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
            
            # Calculate regional breakdown
            total_spend = filtered_df['Spend_USD'].sum()
            
            regional_breakdown = filtered_df.groupby('Supplier_Region')['Spend_USD'].agg([
                ('total_spend', 'sum'),
                ('transaction_count', 'count'),
                ('supplier_count', lambda x: filtered_df[filtered_df['Supplier_Region'] == x.name]['Supplier_ID'].nunique())
            ]).reset_index()
            
            regional_breakdown['percentage'] = (regional_breakdown['total_spend'] / total_spend * 100).round(2)
            regional_breakdown = regional_breakdown.sort_values('percentage', ascending=False)
            
            # Calculate Herfindahl-Hirschman Index (HHI) for concentration
            # HHI = sum of squared market shares (0-10000)
            # 0-1500: Low concentration
            # 1500-2500: Moderate concentration
            # 2500+: High concentration
            hhi = sum((regional_breakdown['percentage'] ** 2))
            
            # Get top region concentration
            top_region_percentage = regional_breakdown.iloc[0]['percentage'] if not regional_breakdown.empty else 0
            top_region_name = regional_breakdown.iloc[0]['Supplier_Region'] if not regional_breakdown.empty else "N/A"
            
            # Determine risk level
            if top_region_percentage > self.THRESHOLDS['single_region_high_risk'] or hhi > self.THRESHOLDS['herfindahl_high_risk']:
                risk_level = "HIGH"
                risk_explanation = f"⚠️ HIGH RISK: {top_region_percentage:.1f}% of spend concentrated in {top_region_name}"
            elif top_region_percentage > self.THRESHOLDS['single_region_medium_risk'] or hhi > self.THRESHOLDS['herfindahl_medium_risk']:
                risk_level = "MEDIUM"
                risk_explanation = f"⚡ MEDIUM RISK: {top_region_percentage:.1f}% of spend in {top_region_name}"
            else:
                risk_level = "LOW"
                risk_explanation = f"✅ LOW RISK: Well-diversified across regions"
            
            # Generate diversification recommendation
            if risk_level == "HIGH":
                target_percentage = 40  # Target max 40% in any region
                reduction_needed = top_region_percentage - target_percentage
                recommendation = (
                    f"URGENT: Reduce {top_region_name} dependency from {top_region_percentage:.1f}% to {target_percentage}%. "
                    f"Shift ${(reduction_needed/100 * total_spend):,.0f} ({reduction_needed:.1f}%) to alternative regions."
                )
            elif risk_level == "MEDIUM":
                target_percentage = 45
                reduction_needed = top_region_percentage - target_percentage
                recommendation = (
                    f"RECOMMENDED: Reduce {top_region_name} concentration from {top_region_percentage:.1f}% to {target_percentage}%. "
                    f"Diversify ${(reduction_needed/100 * total_spend):,.0f} to other regions."
                )
            else:
                recommendation = f"MAINTAIN: Current regional diversification is healthy. Continue monitoring."
            
            # Identify alternative regions
            all_regions = regional_breakdown['Supplier_Region'].tolist()
            underutilized_regions = [
                {
                    'region': row['Supplier_Region'],
                    'current_percentage': row['percentage'],
                    'expansion_potential': f"Can increase by {(30 - row['percentage']):.1f}%"
                }
                for _, row in regional_breakdown.iterrows()
                if row['percentage'] < 30
            ]
            
            result = {
                'concentration_score': round(hhi, 2),
                'herfindahl_index': round(hhi, 2),
                'risk_level': risk_level,
                'risk_explanation': risk_explanation,
                'top_region': {
                    'name': top_region_name,
                    'percentage': round(top_region_percentage, 2),
                    'spend': round(regional_breakdown.iloc[0]['total_spend'], 2) if not regional_breakdown.empty else 0
                },
                'regional_breakdown': regional_breakdown.to_dict('records'),
                'region_count': len(regional_breakdown),
                'diversification_recommendation': recommendation,
                'alternative_regions': underutilized_regions,
                'thresholds': self.THRESHOLDS
            }
            
            self._log(f"Regional analysis complete: {risk_level} risk, HHI={hhi:.0f}")
            
            return self._create_response(
                success=True,
                data=result,
                sources=['spend_data.csv']
            )
            
        except Exception as e:
            self._log(f"Error in regional concentration analysis: {str(e)}", "ERROR")
            return self._create_response(
                success=False,
                error=str(e)
            )
