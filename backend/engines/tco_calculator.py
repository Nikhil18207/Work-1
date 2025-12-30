"""
TCO Calculator - Total Cost of Ownership Analysis
"""

from typing import Dict, Any, List
from datetime import datetime


class TCOCalculator:
    """Calculate Total Cost of Ownership across all dimensions"""
    
    def calculate_tco(self, brief_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Comprehensive TCO analysis including:
        - Material cost
        - Logistics and freight
        - Quality and returns
        - Risk and compliance
        - Hidden costs
        """
        
        total_spend = brief_data.get('total_spend', 0)
        category = brief_data.get('category', 'Unknown')
        
        # Component calculations
        material_cost = total_spend  # Base material cost
        
        logistics_cost = self._calculate_logistics(total_spend, category)
        quality_cost = self._calculate_quality(total_spend, category)
        risk_cost = self._calculate_risk_cost(brief_data)
        compliance_cost = self._calculate_compliance(total_spend, category)
        hidden_costs = self._calculate_hidden_costs(total_spend)
        
        total_tco = material_cost + logistics_cost + quality_cost + risk_cost + compliance_cost + hidden_costs
        
        # Calculate impact of diversification
        optimized_tco = self._calculate_optimized_tco(brief_data, total_tco)
        tco_savings = total_tco - optimized_tco
        
        return {
            'timestamp': datetime.now().isoformat(),
            'category': category,
            'current_state': {
                'material_cost': material_cost,
                'logistics_cost': logistics_cost,
                'quality_cost': quality_cost,
                'risk_cost': risk_cost,
                'compliance_cost': compliance_cost,
                'hidden_costs': hidden_costs,
                'total_tco': total_tco,
                'tco_breakdown_pct': self._get_breakdown_pct(material_cost, logistics_cost, quality_cost, risk_cost, compliance_cost, hidden_costs, total_tco)
            },
            'optimized_state': {
                'material_cost': material_cost * 0.95,  # 5% material savings
                'logistics_cost': logistics_cost * 0.85,  # 15% logistics savings
                'quality_cost': quality_cost * 0.92,  # 8% quality improvement
                'risk_cost': risk_cost * 0.70,  # 30% risk reduction
                'compliance_cost': compliance_cost,
                'hidden_costs': hidden_costs * 0.75,  # 25% hidden cost reduction
                'total_tco': optimized_tco,
            },
            'tco_improvement': {
                'savings_usd': tco_savings,
                'savings_pct': round((tco_savings / total_tco) * 100, 2),
                'payback_period_months': self._calculate_payback_period(tco_savings),
                'roi_percentage': round((tco_savings / total_spend) * 100, 2)
            },
            '3_year_projection': self._project_3_year_savings(tco_savings),
            'recommendations': self._generate_tco_recommendations(brief_data, tco_savings)
        }
    
    def _calculate_logistics(self, spend: float, category: str) -> float:
        """Calculate logistics costs as % of spend"""
        
        # Logistics cost varies by category
        logistics_pct = {
            'food': 0.12,  # 12% for food
            'hardware': 0.10,  # 10% for hardware
            'cloud': 0.02,  # 2% for cloud/services
            'packaging': 0.08,  # 8% for packaging
            'default': 0.10  # 10% default
        }
        
        pct = logistics_pct.get('default')
        for key in logistics_pct.keys():
            if key != 'default' and key in category.lower():
                pct = logistics_pct[key]
                break
        
        return spend * pct
    
    def _calculate_quality(self, spend: float, category: str) -> float:
        """Calculate quality and defect costs"""
        
        # Quality costs (including returns, defects, rework)
        quality_pct = {
            'hardware': 0.08,  # 8% for hardware
            'food': 0.05,  # 5% for food
            'cloud': 0.03,  # 3% for cloud
            'default': 0.05  # 5% default
        }
        
        pct = quality_pct.get('default')
        for key in quality_pct.keys():
            if key != 'default' and key in category.lower():
                pct = quality_pct[key]
                break
        
        return spend * pct
    
    def _calculate_risk_cost(self, brief_data: Dict[str, Any]) -> float:
        """Calculate risk-related costs"""
        
        spend = brief_data.get('total_spend', 0)
        dominant_pct = brief_data.get('dominant_supplier_pct', 0)
        
        # Higher concentration = higher risk cost
        if dominant_pct > 80:
            risk_pct = 0.08
        elif dominant_pct > 60:
            risk_pct = 0.05
        else:
            risk_pct = 0.02
        
        return spend * risk_pct
    
    def _calculate_compliance(self, spend: float, category: str) -> float:
        """Calculate compliance and certification costs"""
        
        compliance_pct = {
            'food': 0.06,  # 6% for food (certifications, audits)
            'hardware': 0.04,  # 4% for hardware
            'cloud': 0.05,  # 5% for cloud (security, compliance)
            'default': 0.03  # 3% default
        }
        
        pct = compliance_pct.get('default')
        for key in compliance_pct.keys():
            if key != 'default' and key in category.lower():
                pct = compliance_pct[key]
                break
        
        return spend * pct
    
    def _calculate_hidden_costs(self, spend: float) -> float:
        """Calculate hidden costs (expediting, emergency shipping, management overhead)"""
        return spend * 0.04  # 4% of spend
    
    def _calculate_optimized_tco(self, brief_data: Dict[str, Any], current_tco: float) -> float:
        """Calculate TCO after optimization"""
        
        # Account for cost advantages from brief
        cost_advantages = brief_data.get('cost_advantages', [])
        total_benefit = 0
        
        for adv in cost_advantages:
            if isinstance(adv, dict):
                max_benefit = adv.get('max_usd', 0)
                total_benefit += max_benefit
        
        # Optimization savings (5-15% reduction in TCO)
        optimization_savings = current_tco * 0.08
        
        return current_tco - total_benefit - optimization_savings
    
    def _get_breakdown_pct(self, material, logistics, quality, risk, compliance, hidden, total):
        """Get cost breakdown percentages"""
        
        if total == 0:
            return {}
        
        return {
            'material': round((material / total) * 100, 1),
            'logistics': round((logistics / total) * 100, 1),
            'quality': round((quality / total) * 100, 1),
            'risk': round((risk / total) * 100, 1),
            'compliance': round((compliance / total) * 100, 1),
            'hidden': round((hidden / total) * 100, 1),
        }
    
    def _calculate_payback_period(self, savings: float, annual_investment: float = 100000) -> int:
        """Calculate payback period in months"""
        
        if savings <= 0:
            return 0
        
        payback_years = annual_investment / max(1, savings)
        return int(payback_years * 12)
    
    def _project_3_year_savings(self, annual_savings: float) -> Dict[str, float]:
        """Project 3-year savings with compounding"""
        
        return {
            'year_1': annual_savings,
            'year_2': annual_savings * 1.03,  # 3% improvement
            'year_3': annual_savings * 1.06,  # 6% improvement
            'total_3_year': annual_savings * 3.09,
            'cumulative_roi': (annual_savings * 3.09) / 100000  # Assuming 100k investment
        }
    
    def _generate_tco_recommendations(self, brief_data: Dict[str, Any], savings: float) -> List[str]:
        """Generate TCO optimization recommendations"""
        
        recommendations = []
        
        if savings > 0:
            recommendations.append(f'Potential annual savings of ${savings:,.0f} through optimization')
        
        recommendations.append('Implement supplier relationship management (SRM) to reduce hidden costs')
        recommendations.append('Consolidate shipments to reduce logistics costs')
        recommendations.append('Establish quality metrics and KPIs with suppliers')
        recommendations.append('Negotiate volume discounts based on consolidation')
        recommendations.append('Implement supply chain visibility tools to reduce risk')
        
        return recommendations
