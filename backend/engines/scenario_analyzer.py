"""
Scenario Analyzer & Benchmark Comparator
"""

from typing import Dict, Any, List
from datetime import datetime


class ScenarioAnalyzer:
    """What-if scenario analysis"""
    
    def analyze_scenarios(self, brief_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate multiple scenarios and outcomes"""
        
        return {
            'timestamp': datetime.now().isoformat(),
            'category': brief_data.get('category', 'Unknown'),
            'baseline_scenario': self._get_baseline(brief_data),
            'optimistic_scenario': self._get_optimistic_scenario(brief_data),
            'pessimistic_scenario': self._get_pessimistic_scenario(brief_data),
            'alternative_scenarios': [
                self._get_supply_disruption_scenario(brief_data),
                self._get_price_shock_scenario(brief_data),
                self._get_regulatory_scenario(brief_data),
                self._get_competitive_scenario(brief_data)
            ],
            'scenario_comparison': self._compare_scenarios(brief_data)
        }
    
    def _get_baseline(self, brief_data: Dict[str, Any]) -> Dict[str, Any]:
        """Baseline scenario - status quo"""
        
        spend = brief_data.get('total_spend', 0)
        
        return {
            'name': 'Baseline (Status Quo)',
            'description': 'Continue with current suppliers and operations',
            'probability': '20%',
            'annual_spend': spend,
            'cost_impact': 0,
            'risk_score': 8.0,
            'outcomes': {
                'year_1': {'spend': spend, 'savings': 0, 'risk': 'High'},
                'year_2': {'spend': spend * 1.02, 'savings': 0, 'risk': 'High'},
                'year_3': {'spend': spend * 1.04, 'savings': 0, 'risk': 'High'}
            },
            'key_assumptions': [
                'No supplier changes',
                '2% annual inflation',
                'Supply chain remains stable',
                'No major market disruptions'
            ]
        }
    
    def _get_optimistic_scenario(self, brief_data: Dict[str, Any]) -> Dict[str, Any]:
        """Optimistic scenario - best case"""
        
        spend = brief_data.get('total_spend', 0)
        cost_advantages = brief_data.get('cost_advantages', [])
        
        max_savings = 0
        for adv in cost_advantages:
            if isinstance(adv, dict) and adv.get('region') == 'Blended Advantage':
                max_savings = adv.get('max_usd', 0)
        
        return {
            'name': 'Optimistic (Best Case)',
            'description': 'Perfect execution of diversification strategy',
            'probability': '25%',
            'annual_spend': spend,
            'cost_impact': -max_savings * 1.2,  # 20% better than expected
            'risk_score': 3.0,
            'outcomes': {
                'year_1': {
                    'spend': spend * 0.95,
                    'savings': max_savings * 0.5,
                    'risk': 'Low'
                },
                'year_2': {
                    'spend': spend * 0.92,
                    'savings': max_savings * 1.0,
                    'risk': 'Low'
                },
                'year_3': {
                    'spend': spend * 0.90,
                    'savings': max_savings * 1.2,
                    'risk': 'Very Low'
                }
            },
            'key_assumptions': [
                'All suppliers perform above expectations',
                'No quality issues',
                'Market prices decline',
                'Supplier capacity unlimited'
            ]
        }
    
    def _get_pessimistic_scenario(self, brief_data: Dict[str, Any]) -> Dict[str, Any]:
        """Pessimistic scenario - worst case"""
        
        spend = brief_data.get('total_spend', 0)
        
        return {
            'name': 'Pessimistic (Worst Case)',
            'description': 'Implementation delays and supplier issues',
            'probability': '15%',
            'annual_spend': spend,
            'cost_impact': spend * 0.15,  # 15% increase
            'risk_score': 9.0,
            'outcomes': {
                'year_1': {
                    'spend': spend * 1.10,
                    'savings': 0,
                    'risk': 'Critical'
                },
                'year_2': {
                    'spend': spend * 1.08,
                    'savings': -spend * 0.05,
                    'risk': 'High'
                },
                'year_3': {
                    'spend': spend * 1.05,
                    'savings': 0,
                    'risk': 'High'
                }
            },
            'key_assumptions': [
                'Supplier quality issues',
                'Delayed implementation',
                'Prices increase beyond forecast',
                'Supply disruptions'
            ]
        }
    
    def _get_supply_disruption_scenario(self, brief_data: Dict[str, Any]) -> Dict[str, Any]:
        """Supply disruption scenario (geopolitical, pandemic, etc)"""
        
        spend = brief_data.get('total_spend', 0)
        dominant_pct = brief_data.get('dominant_supplier_pct', 0)
        
        disruption_cost = spend * (dominant_pct / 100) * 0.30  # 30% cost impact for concentrated supply
        
        return {
            'name': 'Supply Disruption',
            'description': 'Major supply chain disruption (geopolitical, pandemic, etc)',
            'probability': '15%',
            'trigger': 'Unexpected supply chain shock',
            'duration_months': 3,
            'cost_impact': disruption_cost,
            'mitigation': 'Multiple suppliers reduce impact by 70%',
            'outcomes': {
                'immediate': f'${disruption_cost:,.0f} cost overrun',
                'recovery': '6-12 months',
                'long_term': 'If diversified, minimal impact'
            }
        }
    
    def _get_price_shock_scenario(self, brief_data: Dict[str, Any]) -> Dict[str, Any]:
        """Price shock scenario (commodity price spike, inflation)"""
        
        spend = brief_data.get('total_spend', 0)
        
        return {
            'name': 'Price Shock',
            'description': 'Significant commodity price increase (15-20%)',
            'probability': '25%',
            'trigger': 'Commodity price spike, currency fluctuation',
            'cost_impact': spend * 0.15,
            'mitigation': 'Long-term contracts and hedging',
            'outcomes': {
                'unhedged': f'${spend * 0.15:,.0f} additional cost',
                'hedged': f'${spend * 0.05:,.0f} cost increase',
                'with_alternatives': f'${spend * 0.03:,.0f} cost increase'
            }
        }
    
    def _get_regulatory_scenario(self, brief_data: Dict[str, Any]) -> Dict[str, Any]:
        """Regulatory/compliance scenario"""
        
        spend = brief_data.get('total_spend', 0)
        
        return {
            'name': 'Regulatory Changes',
            'description': 'New tariffs, sanctions, or compliance requirements',
            'probability': '20%',
            'trigger': 'Policy/regulatory change',
            'cost_impact': spend * 0.10,
            'mitigation': 'Geographic diversification + compliance programs',
            'outcomes': {
                'no_mitigation': f'${spend * 0.10:,.0f} cost increase',
                'with_diversification': f'${spend * 0.03:,.0f} cost increase',
                'legal_risk': 'Significant if non-compliant'
            }
        }
    
    def _get_competitive_scenario(self, brief_data: Dict[str, Any]) -> Dict[str, Any]:
        """Competitive dynamics scenario"""
        
        spend = brief_data.get('total_spend', 0)
        
        return {
            'name': 'Competitive Pressure',
            'description': 'New competitors entering market, price wars',
            'probability': '20%',
            'trigger': 'Market disruption, new entrants',
            'cost_impact': -spend * 0.08,  # 8% savings opportunity
            'mitigation': 'Maintain strong supplier relationships',
            'outcomes': {
                'opportunity': f'${spend * 0.08:,.0f} savings',
                'risk': 'Quality dilution from new suppliers',
                'timeline': '6-12 months'
            }
        }
    
    def _compare_scenarios(self, brief_data: Dict[str, Any]) -> Dict[str, Any]:
        """Compare scenarios"""
        
        spend = brief_data.get('total_spend', 0)
        
        return {
            'best_case': 'Optimistic - 15-20% savings',
            'most_likely': 'Optimistic/Baseline - 8-12% savings',
            'worst_case': 'Pessimistic - 15% cost increase',
            'expected_value': f'${spend * 0.08:,.0f} savings (weighted)',
            'recommendation': 'Pursue diversification with risk mitigation'
        }


class BenchmarkAnalyzer:
    """Benchmark against industry standards"""
    
    def benchmark_analysis(self, brief_data: Dict[str, Any]) -> Dict[str, Any]:
        """Industry and peer benchmarking"""
        
        category = brief_data.get('category', 'Unknown')
        
        return {
            'timestamp': datetime.now().isoformat(),
            'category': category,
            'your_metrics': self._get_your_metrics(brief_data),
            'industry_benchmarks': self._get_industry_benchmarks(category),
            'peer_comparison': self._get_peer_comparison(brief_data),
            'performance_gaps': self._identify_gaps(brief_data),
            'recommendations': self._benchmark_recommendations(brief_data)
        }
    
    def _get_your_metrics(self, brief_data: Dict[str, Any]) -> Dict[str, Any]:
        """Your current metrics"""
        
        dominant_pct = brief_data.get('dominant_supplier_pct', 0)
        spend = brief_data.get('total_spend', 0)
        
        return {
            'supplier_concentration': f'{dominant_pct:.1f}%',
            'supplier_count': brief_data.get('num_suppliers', 'N/A'),
            'annual_spend': f'${spend:,.0f}',
            'regional_concentration': brief_data.get('regional_dependency', {}).get('original_sea_pct', 0),
            'cost_per_unit': 'TBD based on volume'
        }
    
    def _get_industry_benchmarks(self, category: str) -> Dict[str, Any]:
        """Industry benchmarks"""
        
        benchmarks = {
            'food': {
                'supplier_concentration': '35-45%',
                'supplier_count': '4-6 primary',
                'geographic_concentration': '40-50%',
                'cost_variance': '5-8%',
                'quality_standard': '<0.2% defect',
                'lead_time': '30-45 days'
            },
            'hardware': {
                'supplier_concentration': '30-40%',
                'supplier_count': '5-8 primary',
                'geographic_concentration': '35-45%',
                'cost_variance': '3-6%',
                'quality_standard': '<0.1% defect',
                'lead_time': '45-90 days'
            },
            'cloud': {
                'supplier_concentration': '40-50%',
                'supplier_count': '2-4 primary',
                'geographic_concentration': '30-40%',
                'cost_variance': '5-10%',
                'uptime_standard': '>99.9%',
                'support_response': '<2 hours'
            },
            'default': {
                'supplier_concentration': '40-50%',
                'supplier_count': '3-5',
                'cost_variance': '5-8%',
                'quality_standard': 'TBD',
                'delivery_performance': '>95%'
            }
        }
        
        bench = benchmarks.get('default')
        for key in benchmarks.keys():
            if key != 'default' and key in category.lower():
                bench = benchmarks[key]
                break
        
        return bench
    
    def _get_peer_comparison(self, brief_data: Dict[str, Any]) -> Dict[str, str]:
        """Compare to peer companies"""
        
        dominant_pct = brief_data.get('dominant_supplier_pct', 0)
        
        percentile = 'Below Average' if dominant_pct > 60 else 'Average' if dominant_pct > 40 else 'Above Average'
        
        return {
            'your_concentration': f'{dominant_pct:.0f}%',
            'peer_average': '45%',
            'top_quartile': '<30%',
            'your_percentile': percentile,
            'recommendation': 'Move toward top quartile (30% or less)'
        }
    
    def _identify_gaps(self, brief_data: Dict[str, Any]) -> List[Dict[str, str]]:
        """Identify performance gaps"""
        
        gaps = []
        
        dominant_pct = brief_data.get('dominant_supplier_pct', 0)
        if dominant_pct > 50:
            gaps.append({
                'metric': 'Supplier Concentration',
                'your_performance': f'{dominant_pct:.0f}%',
                'benchmark': '40%',
                'gap': f'{dominant_pct - 40:.0f}% above benchmark',
                'priority': 'High'
            })
        
        supplier_count = brief_data.get('num_suppliers', 0)
        if supplier_count < 3:
            gaps.append({
                'metric': 'Supplier Count',
                'your_performance': str(supplier_count),
                'benchmark': '3-5',
                'gap': f'{3 - supplier_count} below benchmark',
                'priority': 'High'
            })
        
        return gaps
    
    def _benchmark_recommendations(self, brief_data: Dict[str, Any]) -> List[str]:
        """Benchmarking-based recommendations"""
        
        return [
            'Reduce dominant supplier concentration to match industry standard',
            'Expand supplier base to 4-6 primary suppliers',
            'Implement supplier performance metrics aligned with peers',
            'Conduct competitive bidding annually',
            'Monitor peer strategies quarterly',
            'Achieve top quartile performance within 24 months'
        ]
