"""
Supplier Capability Screener Agent
Checks if current suppliers can provide other products/categories
"""

import sys
from pathlib import Path
from typing import Dict, Any, List
import pandas as pd

root_path = Path(__file__).parent.parent.parent.parent
if str(root_path) not in sys.path:
    sys.path.insert(0, str(root_path))

from backend.agents.base_agent import BaseAgent
from backend.engines.data_loader import DataLoader


class SupplierCapabilityScreenerAgent(BaseAgent):
    """
    Agent for screening supplier capabilities
    
    Input:
        - client_id: str
        - current_category: str (what they're buying now)
        - target_category: str (what they want to buy)
        
    Output:
        - capable_suppliers: List[Dict] (suppliers who can provide target category)
        - expansion_opportunities: List[Dict]
        - risk_assessment: Dict
    """
    
    def __init__(self):
        super().__init__(
            name="SupplierCapabilityScreener",
            description="Screens current suppliers for expansion opportunities"
        )
        self.data_loader = DataLoader()
        
        # Product category relationships (which suppliers can provide which products)
        self.CATEGORY_RELATIONSHIPS = {
            'Rice Bran Oil': ['Edible Oils', 'Sunflower Oil', 'Palm Oil', 'Soybean Oil'],
            'Sunflower Oil': ['Edible Oils', 'Rice Bran Oil', 'Palm Oil'],
            'Palm Oil': ['Edible Oils', 'Rice Bran Oil', 'Sunflower Oil'],
            'Soybean Oil': ['Edible Oils', 'Rice Bran Oil', 'Sunflower Oil'],
            'Olive Oil': ['Edible Oils']
        }
    
    def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute capability screening
        """
        try:
            client_id = input_data.get('client_id')
            current_category = input_data.get('current_category')
            target_category = input_data.get('target_category')
            
            if not all([client_id, current_category, target_category]):
                return self._create_response(
                    success=False,
                    error="client_id, current_category, and target_category are required"
                )
            
            self._log(f"Screening suppliers: {current_category} → {target_category}")
            
            # Load data
            spend_df = self.data_loader.load_spend_data()
            supplier_df = self.data_loader.load_supplier_master()
            
            # Get current suppliers for this client and category
            current_suppliers = spend_df[
                (spend_df['Client_ID'] == client_id) & 
                (spend_df['Category'] == current_category)
            ]['Supplier_ID'].unique()
            
            if len(current_suppliers) == 0:
                return self._create_response(
                    success=False,
                    error=f"No current suppliers found for {current_category}"
                )
            
            # Check which current suppliers can provide target category
            capable_suppliers = []
            expansion_opportunities = []
            
            for supplier_id in current_suppliers:
                supplier_info = supplier_df[supplier_df['supplier_id'] == supplier_id]
                
                if supplier_info.empty:
                    continue
                
                supplier = supplier_info.iloc[0]
                
                # Check if supplier's product category matches target
                supplier_category = supplier['product_category']
                
                # Check capability
                can_provide = self._check_capability(
                    supplier_category, 
                    current_category, 
                    target_category
                )
                
                # Get current spend with this supplier
                current_spend = spend_df[
                    (spend_df['Client_ID'] == client_id) & 
                    (spend_df['Supplier_ID'] == supplier_id)
                ]['Spend_USD'].sum()
                
                supplier_data = {
                    'supplier_id': supplier_id,
                    'supplier_name': supplier['supplier_name'],
                    'country': supplier['country'],
                    'region': supplier['region'],
                    'product_category': supplier_category,
                    'current_spend': round(current_spend, 2),
                    'quality_rating': supplier['quality_rating'],
                    'delivery_reliability': supplier['delivery_reliability_pct'],
                    'sustainability_score': supplier['sustainability_score'],
                    'certifications': supplier['certifications'].split('|') if pd.notna(supplier['certifications']) else []
                }
                
                if can_provide:
                    # Calculate expansion potential
                    expansion_potential = self._calculate_expansion_potential(
                        supplier, current_spend
                    )
                    
                    supplier_data['expansion_potential'] = expansion_potential
                    supplier_data['recommendation'] = f"✅ {supplier['supplier_name']} can provide {target_category}"
                    
                    capable_suppliers.append(supplier_data)
                    
                    # Add to expansion opportunities
                    expansion_opportunities.append({
                        'supplier': supplier['supplier_name'],
                        'opportunity': f"Expand from {current_category} to {target_category}",
                        'current_spend': round(current_spend, 2),
                        'potential_additional_spend': expansion_potential['potential_spend'],
                        'benefits': expansion_potential['benefits'],
                        'risks': expansion_potential['risks']
                    })
                else:
                    supplier_data['can_provide'] = False
                    supplier_data['reason'] = f"Specializes in {supplier_category}, not {target_category}"
            
            # Risk assessment
            risk_assessment = self._assess_expansion_risk(
                capable_suppliers, 
                current_category, 
                target_category
            )
            
            result = {
                'client_id': client_id,
                'current_category': current_category,
                'target_category': target_category,
                'current_suppliers_count': len(current_suppliers),
                'capable_suppliers_count': len(capable_suppliers),
                'capable_suppliers': capable_suppliers,
                'expansion_opportunities': expansion_opportunities,
                'risk_assessment': risk_assessment,
                'recommendation': self._generate_recommendation(
                    capable_suppliers, 
                    expansion_opportunities
                )
            }
            
            self._log(f"Screening complete: {len(capable_suppliers)}/{len(current_suppliers)} suppliers can provide {target_category}")
            
            return self._create_response(
                success=True,
                data=result,
                sources=['spend_data.csv', 'supplier_master.csv']
            )
            
        except Exception as e:
            self._log(f"Error in capability screening: {str(e)}", "ERROR")
            return self._create_response(
                success=False,
                error=str(e)
            )
    
    def _check_capability(
        self, 
        supplier_category: str, 
        current_category: str, 
        target_category: str
    ) -> bool:
        """Check if supplier can provide target category"""
        
        # If supplier category is "Edible Oils", they can provide any oil
        if supplier_category == 'Edible Oils':
            related = self.CATEGORY_RELATIONSHIPS.get(target_category, [])
            return 'Edible Oils' in related or target_category in ['Rice Bran Oil', 'Sunflower Oil', 'Palm Oil', 'Soybean Oil', 'Olive Oil']
        
        # Check if target category is in related categories
        related = self.CATEGORY_RELATIONSHIPS.get(current_category, [])
        return target_category in related or supplier_category == target_category
    
    def _calculate_expansion_potential(
        self, 
        supplier: pd.Series, 
        current_spend: float
    ) -> Dict[str, Any]:
        """Calculate expansion potential for a supplier"""
        
        # Estimate potential additional spend (conservative: 50% of current)
        potential_spend = current_spend * 0.5
        
        # Benefits of expanding with existing supplier
        benefits = [
            "Existing relationship and trust",
            "Potential volume discounts",
            "Simplified vendor management",
            "Known quality and reliability"
        ]
        
        # Add specific benefits based on supplier metrics
        if supplier['quality_rating'] >= 4.5:
            benefits.append(f"High quality rating ({supplier['quality_rating']})")
        
        if supplier['delivery_reliability_pct'] >= 95:
            benefits.append(f"Excellent delivery reliability ({supplier['delivery_reliability_pct']}%)")
        
        # Risks
        risks = []
        
        # Check if expansion would exceed 30% concentration
        total_potential = current_spend + potential_spend
        if total_potential > current_spend * 1.8:  # Simplified check
            risks.append("May exceed 30% supplier concentration limit")
        
        if supplier['sustainability_score'] < 8.0:
            risks.append(f"Moderate sustainability score ({supplier['sustainability_score']})")
        
        return {
            'potential_spend': round(potential_spend, 2),
            'potential_spend_formatted': f"${potential_spend:,.2f}",
            'total_spend_with_expansion': round(total_potential, 2),
            'benefits': benefits,
            'risks': risks if risks else ['Low risk expansion'],
            'confidence': 'HIGH' if len(risks) == 0 else 'MEDIUM'
        }
    
    def _assess_expansion_risk(
        self, 
        capable_suppliers: List[Dict], 
        current_category: str, 
        target_category: str
    ) -> Dict[str, Any]:
        """Assess overall risk of expansion strategy"""
        
        if len(capable_suppliers) == 0:
            return {
                'risk_level': 'HIGH',
                'explanation': f"No current suppliers can provide {target_category} - must onboard new suppliers",
                'mitigation': 'Search for new suppliers or negotiate capability expansion with current suppliers'
            }
        elif len(capable_suppliers) == 1:
            return {
                'risk_level': 'MEDIUM',
                'explanation': f"Only 1 current supplier can provide {target_category} - single source risk",
                'mitigation': 'Consider dual sourcing or backup supplier'
            }
        else:
            return {
                'risk_level': 'LOW',
                'explanation': f"{len(capable_suppliers)} current suppliers can provide {target_category} - good diversification",
                'mitigation': 'Proceed with expansion, maintain multi-supplier strategy'
            }
    
    def _generate_recommendation(
        self, 
        capable_suppliers: List[Dict], 
        expansion_opportunities: List[Dict]
    ) -> str:
        """Generate recommendation"""
        
        if len(capable_suppliers) == 0:
            return "❌ No current suppliers can provide the target category. Recommend searching for new suppliers."
        
        rec = f"✅ EXPANSION OPPORTUNITY IDENTIFIED\n\n"
        rec += f"Found {len(capable_suppliers)} current supplier(s) who can provide the target category:\n\n"
        
        for i, opp in enumerate(expansion_opportunities[:3], 1):
            rec += f"{i}. {opp['supplier']}\n"
            rec += f"   Current Spend: ${opp['current_spend']:,.2f}\n"
            rec += f"   Potential Additional: {opp['potential_additional_spend']}\n"
            rec += f"   Benefits: {', '.join(opp['benefits'][:2])}\n\n"
        
        rec += "RECOMMENDATION: Leverage existing relationships for cost savings and simplified vendor management."
        
        return rec
