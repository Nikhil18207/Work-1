"""
Market Intelligence & Analysis Engine
Universal across all industries
"""

from typing import Dict, Any, List
from datetime import datetime
import numpy as np


class MarketIntelligence:
    """Analyze market trends and competitive landscape"""
    
    def __init__(self):
        self.market_segments = {
            'commodity': 'Raw materials, basic supplies',
            'manufactured': 'Produced goods, components',
            'service': 'Services, consulting, maintenance',
            'technology': 'IT, software, cloud solutions'
        }
    
    def analyze_market(self, brief_data: Dict[str, Any]) -> Dict[str, Any]:
        """Comprehensive market analysis"""
        
        category = brief_data.get('category', 'Unknown')
        total_spend = brief_data.get('total_spend', 0)
        
        return {
            'timestamp': datetime.now().isoformat(),
            'category': category,
            'market_size_estimate': self._estimate_market_size(category, total_spend),
            'market_trends': self._get_market_trends(category),
            'competitive_landscape': self._analyze_competition(brief_data),
            'supplier_capacity': self._assess_supplier_capacity(brief_data),
            'pricing_intelligence': self._analyze_pricing(brief_data),
            'innovation_landscape': self._assess_innovation(category),
            'recommendations': self._generate_market_recommendations(brief_data)
        }
    
    def _estimate_market_size(self, category: str, customer_spend: float) -> Dict[str, Any]:
        """Estimate total market size"""
        
        # Market size multipliers by category type
        multipliers = {
            'rice': 45,  # $45 market size for every $1 spent
            'palm': 50,
            'oil': 40,
            'hardware': 200,
            'cloud': 150,
            'logistics': 120,
            'packaging': 80,
        }
        
        multiplier = 100  # Default
        for key, mult in multipliers.items():
            if key.lower() in category.lower():
                multiplier = mult
                break
        
        estimated_global = customer_spend * multiplier
        customer_share = (customer_spend / estimated_global) * 100
        
        return {
            'estimated_global_market': estimated_global,
            'customer_market_share': round(customer_share, 3),
            'customer_spend': customer_spend,
            'growth_projection_3yr': round(estimated_global * 0.05, 0),  # 5% annual growth
        }
    
    def _get_market_trends(self, category: str) -> List[str]:
        """Get market trends by category"""
        
        trends = {
            'default': [
                'Shift towards sustainable sourcing',
                'Consolidation of suppliers in major markets',
                'Digital transformation in procurement',
                'Increased focus on supply chain resilience',
                'ESG and compliance requirements rising'
            ],
            'food': [
                'Growing demand for organic/certified products',
                'Traceability and transparency requirements',
                'Climate change impacting crop yields',
                'Regional trade agreements affecting pricing',
                'Food safety standards becoming stricter'
            ],
            'hardware': [
                'Chip shortage and semiconductor constraints',
                'Taiwan geopolitical tensions affecting supply',
                'Push towards local manufacturing',
                'Used/refurbished equipment market growing',
                'E-waste and recycling mandates'
            ],
            'cloud': [
                'Multi-cloud strategies becoming standard',
                'Data residency regulations increasing',
                'AI/ML integration driving innovation',
                'Cost optimization and FinOps focus',
                'Security and compliance requirements tightening'
            ]
        }
        
        # Find matching category
        for key in trends.keys():
            if key != 'default' and key in category.lower():
                return trends[key]
        
        return trends['default']
    
    def _analyze_competition(self, brief_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze competitive landscape"""
        
        num_suppliers = brief_data.get('num_suppliers', 1)
        dominant_pct = brief_data.get('dominant_supplier_pct', 0)
        
        # Herfindahl Index (concentration measure)
        hhi = dominant_pct ** 2 + ((100 - dominant_pct) / max(1, num_suppliers - 1)) ** 2
        
        competition_level = 'Low' if hhi > 2500 else 'Moderate' if hhi > 1500 else 'High'
        
        return {
            'supplier_count': num_suppliers,
            'hhi_index': round(hhi, 0),
            'competition_level': competition_level,
            'top_supplier_dominance': dominant_pct,
            'market_concentration': 'Highly Concentrated' if dominant_pct > 70 else 'Moderate' if dominant_pct > 30 else 'Diversified'
        }
    
    def _assess_supplier_capacity(self, brief_data: Dict[str, Any]) -> Dict[str, Any]:
        """Assess supplier capacity and growth potential"""
        
        total_spend = brief_data.get('total_spend', 0)
        
        return {
            'current_demand': total_spend,
            'capacity_utilization': 'High' if total_spend > 5000000 else 'Moderate' if total_spend > 1000000 else 'Low',
            'growth_potential': 'Limited' if total_spend < 500000 else 'Moderate' if total_spend < 5000000 else 'High',
            'supplier_expertise': 'Specialized knowledge required for most categories',
            'scalability': 'Moderate to High across identified suppliers'
        }
    
    def _analyze_pricing(self, brief_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze pricing intelligence"""
        
        cost_advantages = brief_data.get('cost_advantages', [])
        total_benefit = 0
        
        for adv in cost_advantages:
            if isinstance(adv, dict) and adv.get('region') == 'Blended Advantage':
                total_benefit = adv.get('max_usd', 0)
        
        current_spend = brief_data.get('dominant_supplier_spend', 0)
        cost_reduction_pct = (total_benefit / max(1, current_spend)) * 100
        
        return {
            'current_pricing': current_spend,
            'benchmark_opportunity': total_benefit,
            'potential_savings_pct': round(cost_reduction_pct, 1),
            'pricing_trend': 'Stable to slightly increasing',
            'seasonality': 'Moderate - varies by region and quarter',
            'volume_leverage': 'Available through consolidation'
        }
    
    def _assess_innovation(self, category: str) -> Dict[str, Any]:
        """Assess innovation landscape"""
        
        innovation_levels = {
            'hardware': 'Very High - rapid innovation cycle',
            'cloud': 'Very High - continuous feature releases',
            'food': 'Moderate - innovation in processing/safety',
            'logistics': 'Moderate - automation and optimization',
            'default': 'Moderate - industry-dependent'
        }
        
        level = innovation_levels.get('default')
        for key in innovation_levels.keys():
            if key != 'default' and key in category.lower():
                level = innovation_levels[key]
                break
        
        return {
            'innovation_level': level,
            'rd_investment': 'Suppliers investing 2-5% of revenue',
            'emerging_technologies': 'AI, automation, sustainability solutions',
            'adoption_rate': 'Moderate - varies by supplier'
        }
    
    def _generate_market_recommendations(self, brief_data: Dict[str, Any]) -> List[str]:
        """Generate market-based recommendations"""
        
        recommendations = []
        
        # Based on concentration
        if brief_data.get('dominant_supplier_pct', 0) > 70:
            recommendations.append('Aggressive diversification strategy needed - market supports multiple suppliers')
        
        # Based on market trends
        recommendations.append('Monitor ESG compliance - increasingly important for procurement decisions')
        recommendations.append('Explore alternative suppliers in emerging markets for cost optimization')
        recommendations.append('Invest in supplier relationship programs - critical for supply chain stability')
        
        # Based on category
        category = brief_data.get('category', '').lower()
        if 'hardware' in category or 'it' in category:
            recommendations.append('Address semiconductor supply constraints through long-term partnerships')
        elif 'food' in category or 'oil' in category:
            recommendations.append('Implement sustainability certifications to align with market demands')
        elif 'cloud' in category:
            recommendations.append('Adopt multi-cloud strategy to avoid vendor lock-in')
        
        return recommendations
