"""
Enhanced Region Sourcing Agent
Identifies new regions for sourcing and evaluates top suppliers
Focuses on alternatives to high-concentration regions
"""

import sys
from pathlib import Path
from typing import Dict, Any, List
import pandas as pd
from datetime import datetime

root_path = Path(__file__).parent.parent.parent.parent
if str(root_path) not in sys.path:
    sys.path.insert(0, str(root_path))

from backend.agents.base_agent import BaseAgent
from backend.engines.data_loader import DataLoader


class EnhancedRegionSourcingAgent(BaseAgent):
    """
    Enhanced Agent for identifying and evaluating new sourcing regions
    
    Features:
        - Identifies high-capacity alternative regions
        - Evaluates top suppliers in new regions
        - Compares quality ratings and pricing
        - Matches against client criteria
        - Provides region-specific risk assessment
    """
    
    MIN_QUALITY_RATING = 4.0
    MIN_DELIVERY_RELIABILITY = 90.0
    TARGET_REGIONS = ['India', 'Thailand', 'Vietnam', 'Indonesia', 'Brazil', 'Argentina']
    
    def __init__(self):
        super().__init__(
            name="EnhancedRegionSourcing",
            description="Identifies and evaluates new sourcing regions and suppliers"
        )
        self.data_loader = DataLoader()
    
    def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute enhanced region sourcing analysis
        
        Input:
            - client_id: str
            - category: str
            - exclude_regions: List[str] (optional) - regions to avoid
            - target_volume: float (optional) - volume to source
            - priority_criteria: List[str] (optional) - 'quality', 'price', 'capacity', 'delivery'
        """
        try:
            sourcing_id = f"REGION_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            self._log(f"[{sourcing_id}] Enhanced region sourcing analysis: {input_data}")
            
            # Load data
            spend_df = self.data_loader.load_spend_data()
            supplier_df = self.data_loader.load_supplier_master()
            
            # Analyze current regional distribution
            current_distribution = self._analyze_current_distribution(
                spend_df, input_data.get('client_id'), input_data.get('category')
            )
            
            # Identify new regions
            new_regions = self._identify_new_regions(
                current_distribution, supplier_df, input_data
            )
            
            # Evaluate suppliers in new regions
            supplier_evaluation = self._evaluate_regional_suppliers(
                new_regions, supplier_df, input_data
            )
            
            # Compare with current suppliers
            comparative_analysis = self._compare_with_current(
                supplier_evaluation, current_distribution, supplier_df
            )
            
            # Calculate sourcing impact
            impact_analysis = self._calculate_sourcing_impact(
                new_regions, supplier_evaluation, current_distribution, input_data
            )
            
            result = {
                'sourcing_id': sourcing_id,
                'timestamp': datetime.now().isoformat(),
                'client_id': input_data.get('client_id'),
                'category': input_data.get('category'),
                'current_distribution': current_distribution,
                'new_regions_identified': new_regions,
                'supplier_evaluation': supplier_evaluation,
                'comparative_analysis': comparative_analysis,
                'impact_analysis': impact_analysis,
                'recommendations': self._generate_region_recommendations(
                    new_regions, supplier_evaluation, comparative_analysis
                )
            }
            
            self._log(f"[{sourcing_id}] Region sourcing complete: {len(new_regions)} regions identified")
            
            return self._create_response(
                success=True,
                data=result,
                sources=['spend_data.csv', 'supplier_master.csv']
            )
            
        except Exception as e:
            self._log(f"Error in region sourcing analysis: {str(e)}", "ERROR")
            return self._create_response(
                success=False,
                error=str(e)
            )
    
    def _analyze_current_distribution(
        self, spend_df: pd.DataFrame, client_id: str, category: str
    ) -> Dict:
        """Analyze current regional distribution"""
        filtered_df = spend_df.copy()
        
        if client_id:
            filtered_df = filtered_df[filtered_df['Client_ID'] == client_id]
        
        if category:
            filtered_df = filtered_df[filtered_df['Category'] == category]
        
        if filtered_df.empty:
            return {
                'total_spend': 0,
                'regions': [],
                'concentration_risk': 'UNKNOWN'
            }
        
        total_spend = filtered_df['Spend_USD'].sum()
        
        # Regional breakdown
        regional_spend = filtered_df.groupby('Supplier_Region').agg({
            'Spend_USD': ['sum', 'count'],
            'Supplier_ID': 'nunique'
        }).reset_index()
        
        regional_spend.columns = ['Region', 'total_spend', 'transaction_count', 'supplier_count']
        regional_spend['percentage'] = (regional_spend['total_spend'] / total_spend * 100).round(2)
        regional_spend['avg_spend_per_supplier'] = (
            regional_spend['total_spend'] / regional_spend['supplier_count']
        ).round(2)
        regional_spend = regional_spend.sort_values('percentage', ascending=False)
        
        # Calculate concentration risk
        top_region_pct = regional_spend.iloc[0]['percentage'] if not regional_spend.empty else 0
        
        if top_region_pct > 60:
            concentration_risk = 'CRITICAL'
        elif top_region_pct > 50:
            concentration_risk = 'HIGH'
        elif top_region_pct > 40:
            concentration_risk = 'MEDIUM'
        else:
            concentration_risk = 'LOW'
        
        return {
            'total_spend': round(total_spend, 2),
            'total_spend_formatted': f"${total_spend:,.2f}",
            'region_count': len(regional_spend),
            'regions': regional_spend.to_dict('records'),
            'top_region': {
                'name': regional_spend.iloc[0]['Region'],
                'percentage': regional_spend.iloc[0]['percentage'],
                'spend': round(regional_spend.iloc[0]['total_spend'], 2)
            } if not regional_spend.empty else None,
            'concentration_risk': concentration_risk,
            'diversification_needed': concentration_risk in ['CRITICAL', 'HIGH']
        }
    
    def _identify_new_regions(
        self, current_distribution: Dict, supplier_df: pd.DataFrame, input_data: Dict
    ) -> List[Dict]:
        """Identify high-capacity alternative regions"""
        current_regions = [r['Region'] for r in current_distribution.get('regions', [])]
        exclude_regions = input_data.get('exclude_regions', [])
        category = input_data.get('category')
        
        # Filter suppliers by category capability
        if category:
            capable_suppliers = supplier_df[
                supplier_df['products_offered'].str.contains(category, case=False, na=False)
            ]
        else:
            capable_suppliers = supplier_df.copy()
        
        # Group by region
        regional_capacity = capable_suppliers.groupby('region').agg({
            'supplier_id': 'count',
            'annual_capacity_mt': 'sum',
            'quality_rating': 'mean',
            'delivery_reliability_pct': 'mean',
            'list_price_per_kg': 'mean'
        }).reset_index()
        
        regional_capacity.columns = ['Region', 'supplier_count', 'total_capacity_mt',
                                     'avg_quality_rating', 'avg_delivery_reliability', 
                                     'avg_price_per_kg']
        
        # Filter out current and excluded regions
        new_regions_df = regional_capacity[
            (~regional_capacity['Region'].isin(current_regions)) &
            (~regional_capacity['Region'].isin(exclude_regions))
        ]
        
        new_regions = []
        
        for _, row in new_regions_df.iterrows():
            # Calculate region score
            quality_score = (row['avg_quality_rating'] / 5.0) * 40
            capacity_score = min(40, (row['total_capacity_mt'] / 10000) * 40)  # Normalize to 10k MT
            supplier_score = min(20, row['supplier_count'] * 4)  # Max 20 points for 5+ suppliers
            
            region_score = quality_score + capacity_score + supplier_score
            
            # Assess region risk
            region_risk = self._assess_region_risk(row['Region'])
            
            new_regions.append({
                'region': row['Region'],
                'supplier_count': int(row['supplier_count']),
                'total_capacity_mt': round(row['total_capacity_mt'], 2),
                'avg_quality_rating': round(row['avg_quality_rating'], 2),
                'avg_delivery_reliability': round(row['avg_delivery_reliability'], 2),
                'avg_price_per_kg': round(row['avg_price_per_kg'], 2),
                'region_score': round(region_score, 2),
                'risk_assessment': region_risk,
                'recommended': region_risk['overall_risk'] in ['LOW', 'MEDIUM'] and region_score >= 60
            })
        
        return sorted(new_regions, key=lambda x: x['region_score'], reverse=True)
    
    def _assess_region_risk(self, region: str) -> Dict:
        """Assess geopolitical and operational risks for a region"""
        # Simplified risk assessment (in production, this would use real-time data)
        risk_profiles = {
            'India': {
                'geopolitical_risk': 'LOW',
                'trade_policy_risk': 'MEDIUM',
                'logistics_risk': 'MEDIUM',
                'currency_risk': 'MEDIUM',
                'overall_risk': 'MEDIUM',
                'notes': 'Stable democracy, growing manufacturing base, some infrastructure challenges'
            },
            'Thailand': {
                'geopolitical_risk': 'LOW',
                'trade_policy_risk': 'LOW',
                'logistics_risk': 'LOW',
                'currency_risk': 'LOW',
                'overall_risk': 'LOW',
                'notes': 'Stable, excellent infrastructure, established trade relationships'
            },
            'Vietnam': {
                'geopolitical_risk': 'LOW',
                'trade_policy_risk': 'LOW',
                'logistics_risk': 'MEDIUM',
                'currency_risk': 'MEDIUM',
                'overall_risk': 'LOW',
                'notes': 'Rapidly growing manufacturing hub, favorable trade agreements'
            },
            'Indonesia': {
                'geopolitical_risk': 'MEDIUM',
                'trade_policy_risk': 'MEDIUM',
                'logistics_risk': 'MEDIUM',
                'currency_risk': 'MEDIUM',
                'overall_risk': 'MEDIUM',
                'notes': 'Large market, archipelago logistics complexity'
            },
            'Malaysia': {
                'geopolitical_risk': 'LOW',
                'trade_policy_risk': 'LOW',
                'logistics_risk': 'LOW',
                'currency_risk': 'LOW',
                'overall_risk': 'LOW',
                'notes': 'Stable, excellent infrastructure, but may be current high-concentration region'
            },
            'Brazil': {
                'geopolitical_risk': 'MEDIUM',
                'trade_policy_risk': 'MEDIUM',
                'logistics_risk': 'HIGH',
                'currency_risk': 'HIGH',
                'overall_risk': 'MEDIUM',
                'notes': 'Large agricultural producer, currency volatility, long lead times'
            },
            'Argentina': {
                'geopolitical_risk': 'MEDIUM',
                'trade_policy_risk': 'HIGH',
                'logistics_risk': 'MEDIUM',
                'currency_risk': 'HIGH',
                'overall_risk': 'HIGH',
                'notes': 'Agricultural powerhouse, but economic and policy instability'
            }
        }
        
        return risk_profiles.get(region, {
            'geopolitical_risk': 'UNKNOWN',
            'trade_policy_risk': 'UNKNOWN',
            'logistics_risk': 'UNKNOWN',
            'currency_risk': 'UNKNOWN',
            'overall_risk': 'MEDIUM',
            'notes': 'Limited risk data available'
        })
    
    def _evaluate_regional_suppliers(
        self, new_regions: List[Dict], supplier_df: pd.DataFrame, input_data: Dict
    ) -> Dict:
        """Evaluate top suppliers in each new region"""
        category = input_data.get('category')
        priority_criteria = input_data.get('priority_criteria', ['quality', 'price', 'capacity'])
        
        regional_suppliers = {}
        
        for region_info in new_regions[:5]:  # Top 5 regions
            region = region_info['region']
            
            # Filter suppliers in this region
            region_suppliers = supplier_df[supplier_df['region'] == region].copy()
            
            if category:
                region_suppliers = region_suppliers[
                    region_suppliers['products_offered'].str.contains(category, case=False, na=False)
                ]
            
            # Filter by minimum criteria
            qualified_suppliers = region_suppliers[
                (region_suppliers['quality_rating'] >= self.MIN_QUALITY_RATING) &
                (region_suppliers['delivery_reliability_pct'] >= self.MIN_DELIVERY_RELIABILITY)
            ]
            
            # Score suppliers based on priority criteria
            for idx, row in qualified_suppliers.iterrows():
                score = 0
                
                if 'quality' in priority_criteria:
                    score += (row['quality_rating'] / 5.0) * 30
                
                if 'price' in priority_criteria:
                    # Lower price is better (inverse scoring)
                    max_price = region_suppliers['list_price_per_kg'].max()
                    if max_price > 0:
                        score += (1 - (row['list_price_per_kg'] / max_price)) * 25
                
                if 'capacity' in priority_criteria:
                    score += min(25, (row.get('annual_capacity_mt', 0) / 1000) * 25)
                
                if 'delivery' in priority_criteria:
                    score += (row['delivery_reliability_pct'] / 100) * 20
                
                qualified_suppliers.at[idx, 'supplier_score'] = round(score, 2)
            
            # Sort by score
            qualified_suppliers = qualified_suppliers.sort_values('supplier_score', ascending=False)
            
            # Top suppliers in region
            top_suppliers = []
            for _, supplier in qualified_suppliers.head(5).iterrows():
                top_suppliers.append({
                    'supplier_id': supplier['supplier_id'],
                    'supplier_name': supplier['supplier_name'],
                    'quality_rating': supplier['quality_rating'],
                    'delivery_reliability': supplier['delivery_reliability_pct'],
                    'list_price_per_kg': round(supplier['list_price_per_kg'], 2),
                    'annual_capacity_mt': supplier.get('annual_capacity_mt', 0),
                    'capacity_utilization': supplier.get('capacity_utilization_pct', 0),
                    'products_offered': supplier.get('products_offered', '').split(','),
                    'supplier_score': supplier.get('supplier_score', 0),
                    'certifications': supplier.get('certifications', '').split(',') if pd.notna(supplier.get('certifications')) else []
                })
            
            regional_suppliers[region] = {
                'region': region,
                'total_qualified_suppliers': len(qualified_suppliers),
                'top_suppliers': top_suppliers,
                'region_metrics': {
                    'avg_quality': round(qualified_suppliers['quality_rating'].mean(), 2),
                    'avg_price': round(qualified_suppliers['list_price_per_kg'].mean(), 2),
                    'total_capacity': round(qualified_suppliers['annual_capacity_mt'].sum(), 2),
                    'price_range': {
                        'min': round(qualified_suppliers['list_price_per_kg'].min(), 2),
                        'max': round(qualified_suppliers['list_price_per_kg'].max(), 2)
                    }
                }
            }
        
        return regional_suppliers
    
    def _compare_with_current(
        self, regional_suppliers: Dict, current_distribution: Dict, supplier_df: pd.DataFrame
    ) -> Dict:
        """Compare new regional suppliers with current suppliers"""
        comparisons = {}
        
        # Get current supplier metrics
        current_regions = current_distribution.get('regions', [])
        if not current_regions:
            return {'message': 'No current suppliers to compare'}
        
        current_suppliers = []
        for region_info in current_regions:
            region_suppliers = supplier_df[supplier_df['region'] == region_info['Region']]
            current_suppliers.extend(region_suppliers.to_dict('records'))
        
        if not current_suppliers:
            return {'message': 'No current supplier details available'}
        
        current_avg_quality = sum(s.get('quality_rating', 0) for s in current_suppliers) / len(current_suppliers)
        current_avg_price = sum(s.get('list_price_per_kg', 0) for s in current_suppliers) / len(current_suppliers)
        current_avg_delivery = sum(s.get('delivery_reliability_pct', 0) for s in current_suppliers) / len(current_suppliers)
        
        # Compare each new region
        for region, data in regional_suppliers.items():
            metrics = data['region_metrics']
            
            comparisons[region] = {
                'region': region,
                'quality_comparison': {
                    'current_avg': round(current_avg_quality, 2),
                    'new_region_avg': metrics['avg_quality'],
                    'difference': round(metrics['avg_quality'] - current_avg_quality, 2),
                    'better': metrics['avg_quality'] >= current_avg_quality
                },
                'price_comparison': {
                    'current_avg': round(current_avg_price, 2),
                    'new_region_avg': metrics['avg_price'],
                    'difference': round(metrics['avg_price'] - current_avg_price, 2),
                    'better': metrics['avg_price'] <= current_avg_price,
                    'savings_potential_pct': round(
                        ((current_avg_price - metrics['avg_price']) / current_avg_price * 100) 
                        if current_avg_price > 0 else 0, 2
                    )
                },
                'delivery_comparison': {
                    'current_avg': round(current_avg_delivery, 2),
                    'new_region_avg': round(
                        sum(s['delivery_reliability'] for s in data['top_suppliers']) / len(data['top_suppliers'])
                        if data['top_suppliers'] else 0, 2
                    ),
                    'difference': round(
                        (sum(s['delivery_reliability'] for s in data['top_suppliers']) / len(data['top_suppliers'])
                         if data['top_suppliers'] else 0) - current_avg_delivery, 2
                    )
                },
                'overall_assessment': self._assess_overall_comparison(
                    metrics, current_avg_quality, current_avg_price, current_avg_delivery
                )
            }
        
        return comparisons
    
    def _assess_overall_comparison(
        self, new_metrics: Dict, current_quality: float, 
        current_price: float, current_delivery: float
    ) -> str:
        """Assess overall comparison"""
        quality_better = new_metrics['avg_quality'] >= current_quality
        price_better = new_metrics['avg_price'] <= current_price
        
        if quality_better and price_better:
            return 'SUPERIOR - Better quality and pricing'
        elif quality_better:
            return 'QUALITY_ADVANTAGE - Better quality, comparable pricing'
        elif price_better:
            return 'COST_ADVANTAGE - Better pricing, comparable quality'
        else:
            return 'COMPARABLE - Similar performance to current suppliers'
    
    def _calculate_sourcing_impact(
        self, new_regions: List[Dict], regional_suppliers: Dict,
        current_distribution: Dict, input_data: Dict
    ) -> Dict:
        """Calculate impact of new region sourcing"""
        target_volume = input_data.get('target_volume', 0)
        current_spend = current_distribution.get('total_spend', 0)
        
        if not new_regions:
            return {
                'message': 'No new regions identified',
                'impact': 'NONE'
            }
        
        # Calculate potential impact
        top_region = new_regions[0]
        
        projected_new_spend = target_volume if target_volume > 0 else current_spend * 0.2  # 20% of current
        
        return {
            'current_total_spend': current_spend,
            'target_new_region_spend': round(projected_new_spend, 2),
            'projected_total_spend': round(current_spend + projected_new_spend, 2),
            'top_recommended_region': top_region['region'],
            'projected_regional_distribution': {
                'current_top_region_pct': current_distribution.get('top_region', {}).get('percentage', 0),
                'projected_top_region_pct': round(
                    (current_distribution.get('top_region', {}).get('spend', 0) / 
                     (current_spend + projected_new_spend) * 100) if current_spend + projected_new_spend > 0 else 0, 2
                ),
                'new_region_pct': round(
                    (projected_new_spend / (current_spend + projected_new_spend) * 100) 
                    if current_spend + projected_new_spend > 0 else 0, 2
                )
            },
            'risk_reduction': {
                'current_concentration_risk': current_distribution.get('concentration_risk', 'UNKNOWN'),
                'projected_concentration_risk': 'MEDIUM' if current_distribution.get('concentration_risk') == 'CRITICAL' else 'LOW',
                'improvement': current_distribution.get('concentration_risk') in ['CRITICAL', 'HIGH']
            },
            'capacity_availability': {
                'top_region_capacity_mt': top_region['total_capacity_mt'],
                'sufficient_for_target': top_region['total_capacity_mt'] > (projected_new_spend / top_region.get('avg_price_per_kg', 1))
            }
        }
    
    def _generate_region_recommendations(
        self, new_regions: List[Dict], regional_suppliers: Dict, comparative_analysis: Dict
    ) -> List[Dict]:
        """Generate region-specific recommendations"""
        recommendations = []
        
        if not new_regions:
            recommendations.append({
                'priority': 'HIGH',
                'recommendation': 'Insufficient alternative regions identified',
                'action': 'Expand search criteria or consider global sourcing partners',
                'rationale': 'Current supplier base may be optimal given constraints'
            })
            return recommendations
        
        # Recommendation 1: Top region
        top_region = new_regions[0]
        top_suppliers = regional_suppliers.get(top_region['region'], {}).get('top_suppliers', [])
        
        if top_suppliers:
            recommendations.append({
                'priority': 'HIGH',
                'recommendation': f"Establish sourcing presence in {top_region['region']}",
                'action': f"Initiate supplier qualification for top 3 suppliers in {top_region['region']}",
                'rationale': f"Region score: {top_region['region_score']}/100, "
                            f"{top_region['supplier_count']} qualified suppliers, "
                            f"{top_region['total_capacity_mt']:,.0f} MT capacity",
                'top_suppliers': [s['supplier_name'] for s in top_suppliers[:3]],
                'timeline': '60-90 days',
                'risk_level': top_region['risk_assessment']['overall_risk']
            })
        
        # Recommendation 2: Diversification
        if len(new_regions) >= 2:
            second_region = new_regions[1]
            recommendations.append({
                'priority': 'MEDIUM',
                'recommendation': f"Diversify across {top_region['region']} and {second_region['region']}",
                'action': 'Split new volume 60/40 between top two regions',
                'rationale': 'Further reduce regional concentration risk',
                'timeline': '90-120 days',
                'risk_level': 'LOW'
            })
        
        # Recommendation 3: Cost optimization
        best_price_region = min(new_regions, key=lambda x: x['avg_price_per_kg'])
        if best_price_region['avg_price_per_kg'] < new_regions[0]['avg_price_per_kg']:
            recommendations.append({
                'priority': 'MEDIUM',
                'recommendation': f"Consider {best_price_region['region']} for cost optimization",
                'action': f"Evaluate price-quality tradeoff in {best_price_region['region']}",
                'rationale': f"Average price ${best_price_region['avg_price_per_kg']:.2f}/kg vs ${new_regions[0]['avg_price_per_kg']:.2f}/kg",
                'timeline': '30-60 days',
                'risk_level': best_price_region['risk_assessment']['overall_risk']
            })
        
        return recommendations
