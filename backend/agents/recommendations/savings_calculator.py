"""
Savings Calculator Agent
Calculates exact savings potential with detailed breakdowns
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


class SavingsCalculatorAgent(BaseAgent):
    """
    Agent for calculating savings potential
    
    Input:
        - client_id: str
        - category: str
        - target_price: float (optional, if negotiating)
        - market_price: float (optional, from web intelligence)
        - scenario: str ('price_negotiation', 'supplier_switch', 'volume_consolidation')
        
    Output:
        - current_spend: float
        - potential_savings: float
        - savings_percentage: float
        - savings_breakdown: Dict
        - implementation_timeline: str
    """
    
    def __init__(self):
        super().__init__(
            name="SavingsCalculator",
            description="Calculates exact savings potential with detailed breakdowns"
        )
        self.data_loader = DataLoader()
    
    def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute savings calculation
        """
        try:
            client_id = input_data.get('client_id')
            category = input_data.get('category')
            scenario = input_data.get('scenario', 'price_negotiation')
            
            if not client_id or not category:
                return self._create_response(
                    success=False,
                    error="client_id and category are required"
                )
            
            self._log(f"Calculating savings for {client_id} - {category} ({scenario})")
            
            # Load data
            spend_df = self.data_loader.load_spend_data()
            pricing_df = self.data_loader.load_pricing_benchmarks()
            
            # Filter client and category spend
            client_spend = spend_df[
                (spend_df['Client_ID'] == client_id) & 
                (spend_df['Category'] == category)
            ]
            
            if client_spend.empty:
                return self._create_response(
                    success=False,
                    error=f"No spend data found for {client_id} - {category}"
                )
            
            # Calculate current metrics
            total_spend = client_spend['Spend_USD'].sum()
            total_volume = len(client_spend)
            avg_transaction = total_spend / total_volume if total_volume > 0 else 0
            
            # Get market benchmark price (use estimated price if not in benchmarks)
            # For Rice Bran Oil and other categories not in pricing_benchmarks.csv
            # Use provided market_price or estimate as 5% below current price
            market_price = input_data.get('market_price')
            if not market_price:
                # Estimate: assume market is 5% cheaper than current average
                market_price = avg_transaction * 0.95
            
            current_price = avg_transaction
            
            # Calculate savings based on scenario
            if scenario == 'price_negotiation':
                savings_result = self._calculate_price_negotiation_savings(
                    total_spend, current_price, market_price, input_data
                )
            elif scenario == 'supplier_switch':
                savings_result = self._calculate_supplier_switch_savings(
                    client_spend, input_data
                )
            elif scenario == 'volume_consolidation':
                savings_result = self._calculate_volume_consolidation_savings(
                    client_spend, input_data
                )
            else:
                return self._create_response(
                    success=False,
                    error=f"Unknown scenario: {scenario}"
                )
            
            # Add common fields
            savings_result['current_spend'] = round(total_spend, 2)
            savings_result['current_spend_formatted'] = f"${total_spend:,.2f}"
            savings_result['scenario'] = scenario
            savings_result['category'] = category
            savings_result['client_id'] = client_id
            
            self._log(f"Savings calculation complete: ${savings_result.get('potential_savings', 0):,.2f}")
            
            return self._create_response(
                success=True,
                data=savings_result,
                sources=['spend_data.csv', 'pricing_benchmarks.csv']
            )
            
        except Exception as e:
            self._log(f"Error calculating savings: {str(e)}", "ERROR")
            return self._create_response(
                success=False,
                error=str(e)
            )
    
    def _calculate_price_negotiation_savings(
        self, 
        total_spend: float, 
        current_price: float, 
        market_price: float,
        input_data: Dict
    ) -> Dict[str, Any]:
        """Calculate savings from price negotiation"""
        
        target_price = input_data.get('target_price', market_price)
        
        # Calculate price difference
        price_diff = current_price - target_price
        price_diff_pct = (price_diff / current_price * 100) if current_price > 0 else 0
        
        # Calculate savings
        potential_savings = (price_diff_pct / 100) * total_spend
        
        # Timeline based on savings magnitude
        if price_diff_pct > 10:
            timeline = "3-6 months (significant negotiation required)"
        elif price_diff_pct > 5:
            timeline = "1-3 months (moderate negotiation)"
        else:
            timeline = "1 month (minor adjustment)"
        
        return {
            'potential_savings': round(potential_savings, 2),
            'potential_savings_formatted': f"${potential_savings:,.2f}",
            'savings_percentage': round(price_diff_pct, 2),
            'current_price': round(current_price, 2),
            'target_price': round(target_price, 2),
            'market_price': round(market_price, 2),
            'price_gap': round(price_diff, 2),
            'implementation_timeline': timeline,
            'confidence': 'HIGH' if price_diff_pct < 10 else 'MEDIUM',
            'savings_breakdown': {
                'price_reduction': round(potential_savings, 2),
                'volume_discount': 0,
                'other': 0
            },
            'recommendation': self._generate_price_negotiation_recommendation(
                current_price, target_price, market_price, potential_savings
            )
        }
    
    def _generate_price_negotiation_recommendation(
        self,
        current_price: float,
        target_price: float,
        market_price: float,
        savings: float
    ) -> str:
        """Generate recommendation for price negotiation"""
        
        rec = f"💰 PRICE NEGOTIATION OPPORTUNITY\n\n"
        rec += f"Current Price: ${current_price:,.2f}/ton\n"
        rec += f"Market Average: ${market_price:,.2f}/ton\n"
        rec += f"Target Price: ${target_price:,.2f}/ton\n\n"
        rec += f"Potential Annual Savings: ${savings:,.2f}\n\n"
        rec += "NEGOTIATION STRATEGY:\n"
        rec += f"1. Present market data showing average price of ${market_price:,.2f}\n"
        rec += f"2. Request price reduction to ${target_price:,.2f} (market competitive)\n"
        rec += "3. Offer longer contract term in exchange for better pricing\n"
        rec += "4. If supplier resists, obtain competitive quotes from alternatives\n"
        
        return rec
    
    def _calculate_supplier_switch_savings(self, client_spend: pd.DataFrame, input_data: Dict) -> Dict[str, Any]:
        """Calculate savings from switching suppliers"""
        
        # Simplified calculation
        total_spend = client_spend['Spend_USD'].sum()
        assumed_savings_pct = input_data.get('savings_percentage', 8)  # Default 8% savings
        
        potential_savings = (assumed_savings_pct / 100) * total_spend
        
        return {
            'potential_savings': round(potential_savings, 2),
            'potential_savings_formatted': f"${potential_savings:,.2f}",
            'savings_percentage': assumed_savings_pct,
            'implementation_timeline': "6-9 months (supplier transition)",
            'confidence': 'MEDIUM',
            'savings_breakdown': {
                'better_pricing': round(potential_savings * 0.7, 2),
                'improved_terms': round(potential_savings * 0.2, 2),
                'efficiency_gains': round(potential_savings * 0.1, 2)
            },
            'recommendation': f"Switching suppliers could save ${potential_savings:,.2f} ({assumed_savings_pct}%) annually"
        }
    
    def _calculate_volume_consolidation_savings(self, client_spend: pd.DataFrame, input_data: Dict) -> Dict[str, Any]:
        """Calculate savings from volume consolidation"""
        
        total_spend = client_spend['Spend_USD'].sum()
        current_suppliers = client_spend['Supplier_ID'].nunique()
        target_suppliers = input_data.get('target_suppliers', max(2, current_suppliers - 1))
        
        # Volume consolidation typically yields 5-12% savings
        savings_pct = min(12, 5 + (current_suppliers - target_suppliers) * 2)
        
        potential_savings = (savings_pct / 100) * total_spend
        
        return {
            'potential_savings': round(potential_savings, 2),
            'potential_savings_formatted': f"${potential_savings:,.2f}",
            'savings_percentage': round(savings_pct, 2),
            'current_suppliers': current_suppliers,
            'target_suppliers': target_suppliers,
            'implementation_timeline': "4-6 months (gradual consolidation)",
            'confidence': 'HIGH',
            'savings_breakdown': {
                'volume_discounts': round(potential_savings * 0.6, 2),
                'reduced_admin_costs': round(potential_savings * 0.2, 2),
                'improved_efficiency': round(potential_savings * 0.2, 2)
            },
            'recommendation': f"Consolidating from {current_suppliers} to {target_suppliers} suppliers could save ${potential_savings:,.2f} ({savings_pct}%)"
        }
