"""
Risk Scoring Agent
Calculates comprehensive risk scores with detailed breakdowns
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


class RiskScoringAgent(BaseAgent):
    """
    Agent for calculating detailed risk scores
    
    Input:
        - supplier_id: str
        - client_id: str (optional)
        - scenario: str (optional, e.g., 'switch_supplier', 'increase_volume')
        
    Output:
        - overall_risk_score: float (0-100)
        - risk_breakdown: Dict (by category)
        - risk_factors: List[Dict] (specific risks identified)
        - comparison: Dict (if comparing scenarios)
    """
    
    def __init__(self):
        super().__init__(
            name="RiskScoring",
            description="Calculates comprehensive risk scores with detailed breakdowns"
        )
        self.data_loader = DataLoader()
        
        # Country risk scores (simplified - in production, use real geopolitical data)
        self.COUNTRY_RISK_SCORES = {
            'Malaysia': {'political': 8, 'trade': 9, 'logistics': 8, 'overall': 8.3},
            'Indonesia': {'political': 7, 'trade': 8, 'logistics': 7, 'overall': 7.3},
            'Thailand': {'political': 7, 'trade': 9, 'logistics': 8, 'overall': 8.0},
            'India': {'political': 8, 'trade': 8, 'logistics': 6, 'overall': 7.3},
            'China': {'political': 7, 'trade': 7, 'logistics': 9, 'overall': 7.7},
            'USA': {'political': 9, 'trade': 9, 'logistics': 9, 'overall': 9.0},
            'Ukraine': {'political': 4, 'trade': 5, 'logistics': 4, 'overall': 4.3},
            'Israel': {'political': 6, 'trade': 7, 'logistics': 7, 'overall': 6.7},
            'Spain': {'political': 8, 'trade': 9, 'logistics': 8, 'overall': 8.3},
            'Germany': {'political': 9, 'trade': 9, 'logistics': 9, 'overall': 9.0},
            'Switzerland': {'political': 10, 'trade': 9, 'logistics': 8, 'overall': 9.0},
            'UK': {'political': 8, 'trade': 8, 'logistics': 8, 'overall': 8.0},
            'France': {'political': 8, 'trade': 9, 'logistics': 8, 'overall': 8.3},
            'Japan': {'political': 9, 'trade': 9, 'logistics': 9, 'overall': 9.0},
            'Mexico': {'political': 6, 'trade': 8, 'logistics': 7, 'overall': 7.0},
            'Canada': {'political': 9, 'trade': 9, 'logistics': 8, 'overall': 8.7},
            'Denmark': {'political': 10, 'trade': 9, 'logistics': 8, 'overall': 9.0},
            'Luxembourg': {'political': 10, 'trade': 9, 'logistics': 7, 'overall': 8.7},
            'Liechtenstein': {'political': 10, 'trade': 8, 'logistics': 6, 'overall': 8.0}
        }
    
    def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute risk scoring
        """
        try:
            supplier_id = input_data.get('supplier_id')
            if not supplier_id:
                return self._create_response(
                    success=False,
                    error="supplier_id is required"
                )
            
            self._log(f"Calculating risk score for supplier {supplier_id}")
            
            # Load supplier data
            supplier_df = self.data_loader.load_supplier_master()
            supplier = supplier_df[supplier_df['supplier_id'] == supplier_id]
            
            if supplier.empty:
                return self._create_response(
                    success=False,
                    error=f"Supplier {supplier_id} not found"
                )
            
            supplier = supplier.iloc[0]
            
            # Calculate risk components
            risk_breakdown = {}
            risk_factors = []
            
            # 1. Quality Risk (0-100, lower is better)
            quality_rating = supplier['quality_rating']
            quality_risk = max(0, (5.0 - quality_rating) / 5.0 * 100)
            risk_breakdown['quality_risk'] = round(quality_risk, 2)
            
            if quality_rating < 4.0:
                risk_factors.append({
                    'category': 'Quality',
                    'severity': 'HIGH',
                    'score': round(quality_risk, 2),
                    'description': f"Quality rating {quality_rating} below minimum 4.0",
                    'impact': f"+{round(quality_risk, 1)} risk points"
                })
            elif quality_rating < 4.5:
                risk_factors.append({
                    'category': 'Quality',
                    'severity': 'MEDIUM',
                    'score': round(quality_risk, 2),
                    'description': f"Quality rating {quality_rating} is acceptable but not premium",
                    'impact': f"+{round(quality_risk, 1)} risk points"
                })
            
            # 2. Delivery Risk
            delivery_reliability = supplier['delivery_reliability_pct']
            delivery_risk = max(0, (100 - delivery_reliability))
            risk_breakdown['delivery_risk'] = round(delivery_risk, 2)
            
            if delivery_reliability < 90:
                risk_factors.append({
                    'category': 'Delivery',
                    'severity': 'HIGH',
                    'score': round(delivery_risk, 2),
                    'description': f"Delivery reliability {delivery_reliability}% below minimum 90%",
                    'impact': f"+{round(delivery_risk, 1)} risk points"
                })
            elif delivery_reliability < 95:
                risk_factors.append({
                    'category': 'Delivery',
                    'severity': 'MEDIUM',
                    'score': round(delivery_risk, 2),
                    'description': f"Delivery reliability {delivery_reliability}% is acceptable",
                    'impact': f"+{round(delivery_risk, 1)} risk points"
                })
            
            # 3. Geopolitical Risk
            country = supplier['country']
            country_risk_data = self.COUNTRY_RISK_SCORES.get(country, {'overall': 5.0, 'political': 5, 'trade': 5, 'logistics': 5})
            geopolitical_risk = (10 - country_risk_data['overall']) * 10  # Convert to 0-100 scale
            risk_breakdown['geopolitical_risk'] = round(geopolitical_risk, 2)
            risk_breakdown['country_risk_details'] = country_risk_data
            
            if country_risk_data['overall'] < 7:
                risk_factors.append({
                    'category': 'Geopolitical',
                    'severity': 'HIGH' if country_risk_data['overall'] < 5 else 'MEDIUM',
                    'score': round(geopolitical_risk, 2),
                    'description': f"{country} has elevated geopolitical risk (score: {country_risk_data['overall']}/10)",
                    'impact': f"+{round(geopolitical_risk, 1)} risk points",
                    'details': {
                        'political_stability': f"{country_risk_data['political']}/10",
                        'trade_environment': f"{country_risk_data['trade']}/10",
                        'logistics_infrastructure': f"{country_risk_data['logistics']}/10"
                    }
                })
            
            # 4. Sustainability Risk
            sustainability_score = supplier['sustainability_score']
            sustainability_risk = max(0, (10 - sustainability_score) * 10)
            risk_breakdown['sustainability_risk'] = round(sustainability_risk, 2)
            
            if sustainability_score < 7.0:
                risk_factors.append({
                    'category': 'Sustainability',
                    'severity': 'MEDIUM',
                    'score': round(sustainability_risk, 2),
                    'description': f"Sustainability score {sustainability_score} below target 7.0",
                    'impact': f"+{round(sustainability_risk, 1)} risk points"
                })
            
            # 5. Lead Time Risk
            lead_time = supplier['lead_time_days']
            if isinstance(lead_time, (int, float)):
                lead_time_risk = min(100, (lead_time / 30) * 50)  # 30+ days = 50 risk points
                risk_breakdown['lead_time_risk'] = round(lead_time_risk, 2)
                
                if lead_time > 21:
                    risk_factors.append({
                        'category': 'Lead Time',
                        'severity': 'MEDIUM' if lead_time < 30 else 'HIGH',
                        'score': round(lead_time_risk, 2),
                        'description': f"Lead time {lead_time} days is lengthy",
                        'impact': f"+{round(lead_time_risk, 1)} risk points"
                    })
            else:
                lead_time_risk = 0
                risk_breakdown['lead_time_risk'] = 0
            
            # Calculate overall risk score (weighted average)
            weights = {
                'quality_risk': 0.30,
                'delivery_risk': 0.25,
                'geopolitical_risk': 0.25,
                'sustainability_risk': 0.10,
                'lead_time_risk': 0.10
            }
            
            overall_risk_score = sum(
                risk_breakdown.get(key, 0) * weight 
                for key, weight in weights.items()
            )
            
            # Determine risk level
            if overall_risk_score < 20:
                risk_level = "LOW"
                risk_level_description = "✅ Low risk supplier - suitable for strategic sourcing"
            elif overall_risk_score < 40:
                risk_level = "MEDIUM"
                risk_level_description = "⚡ Medium risk - acceptable with monitoring"
            else:
                risk_level = "HIGH"
                risk_level_description = "⚠️ High risk - requires mitigation strategies"
            
            result = {
                'supplier_id': supplier_id,
                'supplier_name': supplier['supplier_name'],
                'country': country,
                'overall_risk_score': round(overall_risk_score, 2),
                'risk_level': risk_level,
                'risk_level_description': risk_level_description,
                'risk_breakdown': risk_breakdown,
                'risk_factors': risk_factors,
                'risk_factor_count': len(risk_factors),
                'weights_used': weights
            }
            
            self._log(f"Risk scoring complete: {overall_risk_score:.1f} ({risk_level})")
            
            return self._create_response(
                success=True,
                data=result,
                sources=['supplier_master.csv', 'geopolitical_risk_database']
            )
            
        except Exception as e:
            self._log(f"Error in risk scoring: {str(e)}", "ERROR")
            return self._create_response(
                success=False,
                error=str(e)
            )
    
    def compare_suppliers(self, supplier_id_1: str, supplier_id_2: str) -> Dict[str, Any]:
        """
        Compare risk scores between two suppliers
        """
        try:
            result1 = self.execute({'supplier_id': supplier_id_1})
            result2 = self.execute({'supplier_id': supplier_id_2})
            
            if not result1['success'] or not result2['success']:
                return self._create_response(
                    success=False,
                    error="Failed to score one or both suppliers"
                )
            
            data1 = result1['data']
            data2 = result2['data']
            
            risk_delta = data2['overall_risk_score'] - data1['overall_risk_score']
            
            comparison = {
                'supplier_1': {
                    'id': data1['supplier_id'],
                    'name': data1['supplier_name'],
                    'risk_score': data1['overall_risk_score'],
                    'risk_level': data1['risk_level']
                },
                'supplier_2': {
                    'id': data2['supplier_id'],
                    'name': data2['supplier_name'],
                    'risk_score': data2['overall_risk_score'],
                    'risk_level': data2['risk_level']
                },
                'risk_delta': round(risk_delta, 2),
                'risk_delta_percentage': round((risk_delta / data1['overall_risk_score'] * 100) if data1['overall_risk_score'] > 0 else 0, 2),
                'recommendation': f"Switching from {data1['supplier_name']} to {data2['supplier_name']} would " +
                                 (f"INCREASE risk by {abs(risk_delta):.1f} points ({abs(risk_delta / data1['overall_risk_score'] * 100):.1f}%)" if risk_delta > 0 
                                  else f"DECREASE risk by {abs(risk_delta):.1f} points ({abs(risk_delta / data1['overall_risk_score'] * 100):.1f}%)")
            }
            
            return self._create_response(
                success=True,
                data=comparison,
                sources=['supplier_master.csv']
            )
            
        except Exception as e:
            return self._create_response(
                success=False,
                error=str(e)
            )
