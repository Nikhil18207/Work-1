"""
Enhanced Incumbent Supplier Strategy Agent
Screens incumbent suppliers for expansion opportunities
Validates against constraints (30% max rule, capacity, etc.)
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


class IncumbentStrategyAgent(BaseAgent):
    """
    Enhanced Agent for incumbent supplier expansion strategy
    
    Features:
        - Screens current suppliers for expansion potential
        - Validates against 30% max concentration rule
        - Assesses capacity and capability
        - Identifies low-risk regions
        - Provides specific expansion recommendations
    """
    
    MAX_SUPPLIER_CONCENTRATION = 30.0  # Maximum 30% per supplier
    IDEAL_SUPPLIER_CONCENTRATION = 20.0  # Ideal target
    MIN_QUALITY_RATING = 4.0
    MIN_DELIVERY_RELIABILITY = 90.0
    
    def __init__(self):
        super().__init__(
            name="IncumbentStrategy",
            description="Analyzes incumbent suppliers for strategic expansion opportunities"
        )
        self.data_loader = DataLoader()
    
    def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute incumbent supplier strategy analysis
        
        Input:
            - client_id: str
            - category: str (optional)
            - target_category: str (optional) - category to expand into
            - expansion_volume: float (optional) - additional spend to allocate
        """
        try:
            strategy_id = f"INCUMBENT_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            self._log(f"[{strategy_id}] Analyzing incumbent supplier strategy: {input_data}")
            
            # Load data
            spend_df = self.data_loader.load_spend_data()
            supplier_df = self.data_loader.load_supplier_master()
            
            # Filter current spend
            current_spend = spend_df.copy()
            if input_data.get('client_id'):
                current_spend = current_spend[current_spend['Client_ID'] == input_data['client_id']]
            
            if input_data.get('category'):
                current_spend = current_spend[current_spend['Category'] == input_data['category']]
            
            if current_spend.empty:
                return self._create_response(
                    success=False,
                    error="No current spend data found"
                )
            
            total_current_spend = current_spend['Spend_USD'].sum()
            
            # Screen incumbent suppliers
            screening_results = self._screen_incumbent_suppliers(
                current_spend, supplier_df, total_current_spend
            )
            
            # Validate against constraints
            constraint_validation = self._validate_constraints(
                screening_results, total_current_spend, input_data.get('expansion_volume', 0)
            )
            
            # Identify expansion opportunities
            expansion_opportunities = self._identify_expansion_opportunities(
                screening_results, constraint_validation, supplier_df, input_data
            )
            
            # Calculate impact
            impact_analysis = self._calculate_expansion_impact(
                expansion_opportunities, total_current_spend, input_data.get('expansion_volume', 0)
            )
            
            result = {
                'strategy_id': strategy_id,
                'timestamp': datetime.now().isoformat(),
                'client_id': input_data.get('client_id'),
                'current_category': input_data.get('category'),
                'target_category': input_data.get('target_category'),
                'current_total_spend': round(total_current_spend, 2),
                'expansion_volume': input_data.get('expansion_volume', 0),
                'screening_summary': {
                    'total_incumbents': len(screening_results['all_suppliers']),
                    'qualified_for_expansion': len(screening_results['qualified']),
                    'disqualified': len(screening_results['disqualified']),
                    'high_potential': len(screening_results['high_potential'])
                },
                'screening_results': screening_results,
                'constraint_validation': constraint_validation,
                'expansion_opportunities': expansion_opportunities,
                'impact_analysis': impact_analysis,
                'recommendations': self._generate_incumbent_recommendations(
                    expansion_opportunities, constraint_validation
                )
            }
            
            self._log(f"[{strategy_id}] Strategy complete: {len(expansion_opportunities)} opportunities identified")
            
            return self._create_response(
                success=True,
                data=result,
                sources=['spend_data.csv', 'supplier_master.csv']
            )
            
        except Exception as e:
            self._log(f"Error in incumbent strategy analysis: {str(e)}", "ERROR")
            return self._create_response(
                success=False,
                error=str(e)
            )
    
    def _screen_incumbent_suppliers(
        self, spend_df: pd.DataFrame, supplier_df: pd.DataFrame, total_spend: float
    ) -> Dict:
        """Screen incumbent suppliers for expansion potential"""
        # Calculate current supplier metrics
        supplier_metrics = spend_df.groupby(['Supplier_ID', 'Supplier_Name']).agg({
            'Spend_USD': ['sum', 'count', 'mean'],
            'Supplier_Region': 'first',
            'Category': lambda x: list(x.unique())
        }).reset_index()
        
        supplier_metrics.columns = ['Supplier_ID', 'Supplier_Name', 'total_spend', 
                                     'transaction_count', 'avg_transaction', 
                                     'primary_region', 'categories_supplied']
        
        supplier_metrics['current_percentage'] = (
            supplier_metrics['total_spend'] / total_spend * 100
        ).round(2)
        
        supplier_metrics['room_for_growth'] = (
            self.IDEAL_SUPPLIER_CONCENTRATION - supplier_metrics['current_percentage']
        ).round(2)
        
        all_suppliers = []
        qualified = []
        disqualified = []
        high_potential = []
        
        for _, row in supplier_metrics.iterrows():
            # Get supplier details
            supplier_info = supplier_df[supplier_df['supplier_id'] == row['Supplier_ID']]
            
            if supplier_info.empty:
                continue
            
            supplier_details = supplier_info.iloc[0]
            
            supplier_record = {
                'supplier_id': row['Supplier_ID'],
                'supplier_name': row['Supplier_Name'],
                'current_spend': round(row['total_spend'], 2),
                'current_percentage': row['current_percentage'],
                'room_for_growth_pct': row['room_for_growth'],
                'room_for_growth_usd': round((row['room_for_growth'] / 100) * total_spend, 2),
                'primary_region': row['primary_region'],
                'categories_supplied': row['categories_supplied'],
                'category_count': len(row['categories_supplied']),
                'quality_rating': supplier_details['quality_rating'],
                'delivery_reliability': supplier_details['delivery_reliability_pct'],
                'annual_capacity_mt': supplier_details.get('annual_capacity_mt', 0),
                'capacity_utilization': supplier_details.get('capacity_utilization_pct', 0),
                'products_offered': supplier_details.get('products_offered', '').split(',') if pd.notna(supplier_details.get('products_offered')) else []
            }
            
            all_suppliers.append(supplier_record)
            
            # Screening criteria
            screening_checks = {
                'quality_check': supplier_record['quality_rating'] >= self.MIN_QUALITY_RATING,
                'delivery_check': supplier_record['delivery_reliability'] >= self.MIN_DELIVERY_RELIABILITY,
                'capacity_check': supplier_record['capacity_utilization'] < 85,  # Has capacity
                'concentration_check': supplier_record['current_percentage'] < self.MAX_SUPPLIER_CONCENTRATION,
                'growth_room_check': supplier_record['room_for_growth_pct'] > 5  # At least 5% room
            }
            
            supplier_record['screening_checks'] = screening_checks
            supplier_record['passed_screening'] = all(screening_checks.values())
            
            # Calculate screening score
            screening_score = sum([
                30 if screening_checks['quality_check'] else 0,
                25 if screening_checks['delivery_check'] else 0,
                20 if screening_checks['capacity_check'] else 0,
                15 if screening_checks['concentration_check'] else 0,
                10 if screening_checks['growth_room_check'] else 0
            ])
            
            supplier_record['screening_score'] = screening_score
            
            if supplier_record['passed_screening']:
                qualified.append(supplier_record)
                
                # High potential: excellent performance + significant room for growth
                if (supplier_record['quality_rating'] >= 4.5 and 
                    supplier_record['delivery_reliability'] >= 95 and
                    supplier_record['room_for_growth_pct'] >= 10):
                    high_potential.append(supplier_record)
            else:
                failed_checks = [k for k, v in screening_checks.items() if not v]
                supplier_record['disqualification_reasons'] = failed_checks
                disqualified.append(supplier_record)
        
        return {
            'all_suppliers': sorted(all_suppliers, key=lambda x: x['screening_score'], reverse=True),
            'qualified': sorted(qualified, key=lambda x: x['screening_score'], reverse=True),
            'disqualified': disqualified,
            'high_potential': sorted(high_potential, key=lambda x: x['room_for_growth_pct'], reverse=True)
        }
    
    def _validate_constraints(
        self, screening_results: Dict, current_total_spend: float, expansion_volume: float
    ) -> Dict:
        """Validate expansion against business constraints"""
        validation_results = {
            'max_30_pct_rule': [],
            'capacity_constraints': [],
            'ideal_spend_impact': {},
            'risk_assessment': []
        }
        
        projected_total_spend = current_total_spend + expansion_volume
        
        for supplier in screening_results['qualified']:
            # Rule Check: Max 30% per supplier
            max_additional_spend = (self.MAX_SUPPLIER_CONCENTRATION / 100 * projected_total_spend) - supplier['current_spend']
            ideal_additional_spend = (self.IDEAL_SUPPLIER_CONCENTRATION / 100 * projected_total_spend) - supplier['current_spend']
            
            validation_results['max_30_pct_rule'].append({
                'supplier_id': supplier['supplier_id'],
                'supplier_name': supplier['supplier_name'],
                'current_spend': supplier['current_spend'],
                'current_percentage': supplier['current_percentage'],
                'max_allowed_spend': round(self.MAX_SUPPLIER_CONCENTRATION / 100 * projected_total_spend, 2),
                'max_additional_spend': round(max(0, max_additional_spend), 2),
                'ideal_additional_spend': round(max(0, ideal_additional_spend), 2),
                'can_accept_full_expansion': max_additional_spend >= expansion_volume,
                'percentage_of_expansion_allowed': round(
                    min(100, (max_additional_spend / expansion_volume * 100) if expansion_volume > 0 else 0), 2
                )
            })
            
            # Capacity assessment
            available_capacity_mt = supplier['annual_capacity_mt'] * (100 - supplier['capacity_utilization']) / 100
            
            validation_results['capacity_constraints'].append({
                'supplier_id': supplier['supplier_id'],
                'supplier_name': supplier['supplier_name'],
                'total_capacity_mt': supplier['annual_capacity_mt'],
                'current_utilization_pct': supplier['capacity_utilization'],
                'available_capacity_mt': round(available_capacity_mt, 2),
                'capacity_status': 'ADEQUATE' if supplier['capacity_utilization'] < 80 else 'LIMITED'
            })
            
            # Risk assessment
            risk_level = 'LOW'
            risk_factors = []
            
            if supplier['current_percentage'] > 20:
                risk_level = 'MEDIUM'
                risk_factors.append('Already significant concentration')
            
            if supplier['capacity_utilization'] > 75:
                risk_level = 'MEDIUM' if risk_level == 'LOW' else 'HIGH'
                risk_factors.append('High capacity utilization')
            
            if supplier['primary_region'] in ['Malaysia', 'China']:  # Example high-risk regions
                risk_factors.append('Geopolitically sensitive region')
            
            validation_results['risk_assessment'].append({
                'supplier_id': supplier['supplier_id'],
                'supplier_name': supplier['supplier_name'],
                'risk_level': risk_level,
                'risk_factors': risk_factors,
                'mitigation_required': len(risk_factors) > 0
            })
        
        # Calculate ideal spend impact
        if expansion_volume > 0:
            validation_results['ideal_spend_impact'] = {
                'expansion_volume': expansion_volume,
                'projected_total_spend': projected_total_spend,
                'recommended_distribution': 'Split among 2-3 qualified incumbents',
                'max_per_supplier': round(expansion_volume / 2, 2),  # Split at least 2 ways
                'ideal_per_supplier': round(expansion_volume / 3, 2)  # Ideally 3 ways
            }
        
        return validation_results
    
    def _identify_expansion_opportunities(
        self, screening_results: Dict, constraint_validation: Dict,
        supplier_df: pd.DataFrame, input_data: Dict
    ) -> List[Dict]:
        """Identify specific expansion opportunities"""
        opportunities = []
        
        target_category = input_data.get('target_category')
        expansion_volume = input_data.get('expansion_volume', 0)
        
        for supplier in screening_results['high_potential']:
            # Find constraint validation for this supplier
            constraint = next(
                (c for c in constraint_validation['max_30_pct_rule'] 
                 if c['supplier_id'] == supplier['supplier_id']), None
            )
            
            capacity = next(
                (c for c in constraint_validation['capacity_constraints']
                 if c['supplier_id'] == supplier['supplier_id']), None
            )
            
            risk = next(
                (r for r in constraint_validation['risk_assessment']
                 if r['supplier_id'] == supplier['supplier_id']), None
            )
            
            if not constraint:
                continue
            
            # Check if supplier can supply target category
            can_supply_target = False
            if target_category:
                can_supply_target = target_category in supplier['products_offered']
            else:
                can_supply_target = True  # No specific target, assume yes
            
            if not can_supply_target:
                continue
            
            # Calculate recommended expansion volume
            recommended_volume = min(
                constraint['ideal_additional_spend'],
                expansion_volume / 2 if expansion_volume > 0 else constraint['ideal_additional_spend']
            )
            
            opportunity = {
                'supplier_id': supplier['supplier_id'],
                'supplier_name': supplier['supplier_name'],
                'opportunity_type': 'INCUMBENT_EXPANSION',
                'priority': 'HIGH' if supplier in screening_results['high_potential'][:3] else 'MEDIUM',
                'current_relationship': {
                    'spend': supplier['current_spend'],
                    'percentage': supplier['current_percentage'],
                    'categories': supplier['categories_supplied'],
                    'quality_rating': supplier['quality_rating'],
                    'delivery_reliability': supplier['delivery_reliability']
                },
                'expansion_potential': {
                    'can_supply_target_category': can_supply_target,
                    'target_category': target_category,
                    'max_additional_spend': constraint['max_additional_spend'],
                    'recommended_additional_spend': round(recommended_volume, 2),
                    'projected_total_spend': round(supplier['current_spend'] + recommended_volume, 2),
                    'projected_percentage': round(
                        (supplier['current_spend'] + recommended_volume) / 
                        (constraint_validation['ideal_spend_impact'].get('projected_total_spend', 1)) * 100, 2
                    ) if expansion_volume > 0 else 0
                },
                'capacity_assessment': {
                    'total_capacity_mt': capacity['total_capacity_mt'] if capacity else 0,
                    'available_capacity_mt': capacity['available_capacity_mt'] if capacity else 0,
                    'capacity_status': capacity['capacity_status'] if capacity else 'UNKNOWN'
                },
                'risk_profile': {
                    'risk_level': risk['risk_level'] if risk else 'UNKNOWN',
                    'risk_factors': risk['risk_factors'] if risk else [],
                    'region': supplier['primary_region']
                },
                'rationale': self._generate_expansion_rationale(supplier, constraint, capacity),
                'action_steps': self._generate_expansion_action_steps(
                    supplier, recommended_volume, target_category
                )
            }
            
            opportunities.append(opportunity)
        
        return sorted(opportunities, key=lambda x: x['expansion_potential']['recommended_additional_spend'], reverse=True)
    
    def _generate_expansion_rationale(
        self, supplier: Dict, constraint: Dict, capacity: Dict
    ) -> List[str]:
        """Generate specific rationale for expansion"""
        rationale = []
        
        rationale.append(
            f"Proven performance: Quality {supplier['quality_rating']}/5.0, "
            f"Delivery {supplier['delivery_reliability']}%"
        )
        
        rationale.append(
            f"Currently at {supplier['current_percentage']:.1f}% of spend, "
            f"room to grow to {self.IDEAL_SUPPLIER_CONCENTRATION}%"
        )
        
        if supplier['category_count'] > 1:
            rationale.append(
                f"Multi-category supplier (currently supplying {supplier['category_count']} categories)"
            )
        
        if capacity and capacity['capacity_status'] == 'ADEQUATE':
            rationale.append(
                f"Adequate capacity: {capacity['available_capacity_mt']:.0f} MT available"
            )
        
        rationale.append(
            f"Low-risk expansion: Established relationship in {supplier['primary_region']}"
        )
        
        return rationale
    
    def _generate_expansion_action_steps(
        self, supplier: Dict, volume: float, target_category: str
    ) -> List[Dict]:
        """Generate specific action steps for expansion"""
        steps = [
            {
                'step': 1,
                'action': f"Validate {supplier['supplier_name']}'s capability for {target_category or 'additional volume'}",
                'timeline': '7 days',
                'owner': 'Category Manager'
            },
            {
                'step': 2,
                'action': f"Negotiate pricing for ${volume:,.0f} additional volume",
                'timeline': '14 days',
                'owner': 'Procurement Manager'
            },
            {
                'step': 3,
                'action': f"Confirm capacity and delivery timelines",
                'timeline': '14 days',
                'owner': 'Supply Chain Manager'
            },
            {
                'step': 4,
                'action': f"Place pilot order (20% of target volume)",
                'timeline': '30 days',
                'owner': 'Buyer'
            },
            {
                'step': 5,
                'action': f"Ramp up to full volume based on pilot performance",
                'timeline': '60-90 days',
                'owner': 'Category Manager'
            }
        ]
        
        return steps
    
    def _calculate_expansion_impact(
        self, opportunities: List[Dict], current_spend: float, expansion_volume: float
    ) -> Dict:
        """Calculate impact of expansion strategy"""
        if not opportunities:
            return {
                'total_opportunities': 0,
                'message': 'No qualified incumbent expansion opportunities found'
            }
        
        total_recommended_volume = sum(
            opp['expansion_potential']['recommended_additional_spend'] 
            for opp in opportunities
        )
        
        return {
            'total_opportunities': len(opportunities),
            'high_priority_count': sum(1 for opp in opportunities if opp['priority'] == 'HIGH'),
            'total_recommended_expansion': round(total_recommended_volume, 2),
            'expansion_coverage': round(
                (total_recommended_volume / expansion_volume * 100) if expansion_volume > 0 else 0, 2
            ),
            'projected_supplier_concentration': {
                'current_top_supplier_pct': max(
                    opp['current_relationship']['percentage'] for opp in opportunities
                ) if opportunities else 0,
                'projected_top_supplier_pct': max(
                    opp['expansion_potential']['projected_percentage'] for opp in opportunities
                ) if opportunities else 0,
                'within_30_pct_limit': all(
                    opp['expansion_potential']['projected_percentage'] <= self.MAX_SUPPLIER_CONCENTRATION
                    for opp in opportunities
                )
            },
            'risk_distribution': {
                'low_risk': sum(1 for opp in opportunities if opp['risk_profile']['risk_level'] == 'LOW'),
                'medium_risk': sum(1 for opp in opportunities if opp['risk_profile']['risk_level'] == 'MEDIUM'),
                'high_risk': sum(1 for opp in opportunities if opp['risk_profile']['risk_level'] == 'HIGH')
            }
        }
    
    def _generate_incumbent_recommendations(
        self, opportunities: List[Dict], constraint_validation: Dict
    ) -> List[Dict]:
        """Generate strategic recommendations"""
        recommendations = []
        
        if not opportunities:
            recommendations.append({
                'priority': 'HIGH',
                'recommendation': 'No qualified incumbent suppliers for expansion',
                'action': 'Consider new supplier sourcing strategy',
                'rationale': 'Current incumbents either at capacity or do not meet quality/delivery standards'
            })
            return recommendations
        
        # Recommendation 1: Top incumbent expansion
        top_opportunity = opportunities[0]
        recommendations.append({
            'priority': 'HIGH',
            'recommendation': f"Expand with {top_opportunity['supplier_name']}",
            'action': f"Allocate ${top_opportunity['expansion_potential']['recommended_additional_spend']:,.0f} additional spend",
            'rationale': f"Top-performing incumbent with {top_opportunity['current_relationship']['quality_rating']}/5.0 quality, "
                        f"{top_opportunity['expansion_potential']['recommended_additional_spend']:,.0f} room for growth",
            'timeline': '30-60 days',
            'risk_level': top_opportunity['risk_profile']['risk_level']
        })
        
        # Recommendation 2: Diversified approach
        if len(opportunities) >= 2:
            recommendations.append({
                'priority': 'MEDIUM',
                'recommendation': 'Diversify expansion across multiple incumbents',
                'action': f"Split volume among top {min(3, len(opportunities))} qualified suppliers",
                'rationale': 'Maintain concentration limits while leveraging proven relationships',
                'timeline': '60-90 days',
                'risk_level': 'LOW'
            })
        
        # Recommendation 3: Constraint compliance
        recommendations.append({
            'priority': 'CRITICAL',
            'recommendation': 'Maintain 30% concentration limit',
            'action': 'Ensure no single supplier exceeds 30% of total spend',
            'rationale': 'Compliance with procurement policy and risk management',
            'timeline': 'Ongoing',
            'risk_level': 'COMPLIANCE'
        })
        
        return recommendations
