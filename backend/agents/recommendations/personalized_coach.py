"""
Personalized Supplier Coaching Agent
Provides context-aware, specific, and actionable recommendations
Avoids generic advice and tailors guidance to specific situations
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


class PersonalizedCoachAgent(BaseAgent):
    """
    Agent for providing personalized, context-aware supplier coaching
    
    Features:
        - Context-aware recommendations
        - Specific actionable steps
        - Personalized to client situation
        - Avoids generic advice
        - Includes implementation roadmap
        - Risk-aware guidance
    """
    
    def __init__(self):
        super().__init__(
            name="PersonalizedCoach",
            description="Provides context-aware, personalized supplier coaching"
        )
        self.data_loader = DataLoader()
    
    def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute personalized coaching analysis
        
        Input:
            - client_id: str
            - category: str (optional)
            - focus_area: str (optional) - 'concentration', 'quality', 'cost', 'diversification'
            - threshold_violations: List (optional) - from threshold tracker
            - current_suppliers: List (optional) - current supplier analysis
        """
        try:
            coaching_id = f"COACH_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            self._log(f"[{coaching_id}] Generating personalized coaching: {input_data}")
            
            # Load data
            spend_df = self.data_loader.load_spend_data()
            supplier_df = self.data_loader.load_supplier_master()
            
            # Apply filters
            filtered_df = spend_df.copy()
            if input_data.get('client_id'):
                filtered_df = filtered_df[filtered_df['Client_ID'] == input_data['client_id']]
            
            if input_data.get('category'):
                filtered_df = filtered_df[filtered_df['Category'] == input_data['category']]
            
            if filtered_df.empty:
                return self._create_response(
                    success=False,
                    error="No data found for coaching analysis"
                )
            
            # Analyze current situation
            situation_analysis = self._analyze_current_situation(
                filtered_df, supplier_df, input_data
            )
            
            # Generate personalized recommendations
            recommendations = self._generate_personalized_recommendations(
                situation_analysis, input_data
            )
            
            # Create implementation roadmap
            roadmap = self._create_implementation_roadmap(
                recommendations, situation_analysis
            )
            
            # Calculate confidence scores
            confidence_scores = self._calculate_confidence_scores(
                recommendations, situation_analysis
            )
            
            result = {
                'coaching_id': coaching_id,
                'timestamp': datetime.now().isoformat(),
                'client_id': input_data.get('client_id'),
                'category': input_data.get('category'),
                'situation_analysis': situation_analysis,
                'personalized_recommendations': recommendations,
                'implementation_roadmap': roadmap,
                'confidence_scores': confidence_scores,
                'coaching_summary': self._generate_coaching_summary(
                    situation_analysis, recommendations
                )
            }
            
            self._log(f"[{coaching_id}] Coaching complete: {len(recommendations)} recommendations")
            
            return self._create_response(
                success=True,
                data=result,
                sources=['spend_data.csv', 'supplier_master.csv']
            )
            
        except Exception as e:
            self._log(f"Error in personalized coaching: {str(e)}", "ERROR")
            return self._create_response(
                success=False,
                error=str(e)
            )
    
    def _analyze_current_situation(
        self, spend_df: pd.DataFrame, supplier_df: pd.DataFrame, 
        input_data: Dict
    ) -> Dict:
        """Analyze the current procurement situation in detail"""
        total_spend = spend_df['Spend_USD'].sum()
        
        # Supplier concentration analysis
        supplier_concentration = spend_df.groupby(['Supplier_ID', 'Supplier_Name']).agg({
            'Spend_USD': ['sum', 'count', 'mean']
        }).reset_index()
        supplier_concentration.columns = ['Supplier_ID', 'Supplier_Name', 
                                          'total_spend', 'transaction_count', 'avg_transaction']
        supplier_concentration['percentage'] = (
            supplier_concentration['total_spend'] / total_spend * 100
        ).round(2)
        supplier_concentration = supplier_concentration.sort_values('percentage', ascending=False)
        
        # Regional analysis
        region_concentration = spend_df.groupby('Supplier_Region').agg({
            'Spend_USD': 'sum',
            'Supplier_ID': 'nunique'
        }).reset_index()
        region_concentration.columns = ['Region', 'total_spend', 'supplier_count']
        region_concentration['percentage'] = (
            region_concentration['total_spend'] / total_spend * 100
        ).round(2)
        region_concentration = region_concentration.sort_values('percentage', ascending=False)
        
        # Quality and performance analysis
        supplier_performance = []
        for _, row in supplier_concentration.iterrows():
            supplier_info = supplier_df[supplier_df['supplier_id'] == row['Supplier_ID']]
            if not supplier_info.empty:
                perf = supplier_info.iloc[0]
                supplier_performance.append({
                    'supplier_id': row['Supplier_ID'],
                    'supplier_name': row['Supplier_Name'],
                    'spend_percentage': row['percentage'],
                    'quality_rating': perf['quality_rating'],
                    'delivery_reliability': perf['delivery_reliability_pct'],
                    'capacity_utilization': perf.get('capacity_utilization_pct', 0),
                    'risk_score': self._calculate_supplier_risk_score(perf, row)
                })
        
        # Identify key issues
        key_issues = self._identify_key_issues(
            supplier_concentration, region_concentration, supplier_performance
        )
        
        # Identify opportunities
        opportunities = self._identify_opportunities(
            supplier_concentration, region_concentration, supplier_performance, supplier_df
        )
        
        return {
            'total_spend': round(total_spend, 2),
            'total_spend_formatted': f"${total_spend:,.2f}",
            'supplier_count': spend_df['Supplier_ID'].nunique(),
            'region_count': spend_df['Supplier_Region'].nunique(),
            'transaction_count': len(spend_df),
            'top_supplier': {
                'name': supplier_concentration.iloc[0]['Supplier_Name'],
                'percentage': supplier_concentration.iloc[0]['percentage'],
                'spend': round(supplier_concentration.iloc[0]['total_spend'], 2)
            } if not supplier_concentration.empty else None,
            'top_region': {
                'name': region_concentration.iloc[0]['Region'],
                'percentage': region_concentration.iloc[0]['percentage'],
                'supplier_count': int(region_concentration.iloc[0]['supplier_count'])
            } if not region_concentration.empty else None,
            'supplier_concentration': supplier_concentration.head(10).to_dict('records'),
            'region_concentration': region_concentration.to_dict('records'),
            'supplier_performance': supplier_performance,
            'key_issues': key_issues,
            'opportunities': opportunities
        }
    
    def _calculate_supplier_risk_score(self, supplier_info: pd.Series, spend_info: pd.Series) -> float:
        """Calculate comprehensive risk score for a supplier"""
        risk_score = 0
        
        # Concentration risk (0-40 points)
        concentration = spend_info['percentage']
        if concentration > 30:
            risk_score += 40
        elif concentration > 20:
            risk_score += 20 + (concentration - 20) * 2
        else:
            risk_score += concentration
        
        # Quality risk (0-30 points)
        quality = supplier_info['quality_rating']
        if quality < 3.0:
            risk_score += 30
        elif quality < 4.0:
            risk_score += 20
        elif quality < 4.5:
            risk_score += 10
        
        # Delivery risk (0-30 points)
        delivery = supplier_info['delivery_reliability_pct']
        if delivery < 85:
            risk_score += 30
        elif delivery < 90:
            risk_score += 20
        elif delivery < 95:
            risk_score += 10
        
        return round(risk_score, 2)
    
    def _identify_key_issues(
        self, supplier_conc: pd.DataFrame, region_conc: pd.DataFrame,
        supplier_perf: List[Dict]
    ) -> List[Dict]:
        """Identify specific key issues in the current setup"""
        issues = []
        
        # Issue 1: High concentration
        for supplier in supplier_conc.head(3).to_dict('records'):
            if supplier['percentage'] > 30:
                issues.append({
                    'type': 'HIGH_CONCENTRATION',
                    'severity': 'CRITICAL',
                    'entity': supplier['Supplier_Name'],
                    'metric': f"{supplier['percentage']:.1f}%",
                    'description': f"Over-reliance on {supplier['Supplier_Name']} ({supplier['percentage']:.1f}% of spend)",
                    'impact': f"${supplier['total_spend']:,.0f} at risk if supplier fails",
                    'specific_concern': "Single point of failure in supply chain"
                })
            elif supplier['percentage'] > 20:
                issues.append({
                    'type': 'MODERATE_CONCENTRATION',
                    'severity': 'HIGH',
                    'entity': supplier['Supplier_Name'],
                    'metric': f"{supplier['percentage']:.1f}%",
                    'description': f"Significant dependency on {supplier['Supplier_Name']}",
                    'impact': f"Limited negotiation leverage",
                    'specific_concern': "Approaching concentration threshold"
                })
        
        # Issue 2: Regional concentration
        for region in region_conc.to_dict('records'):
            if region['percentage'] > 50:
                issues.append({
                    'type': 'REGIONAL_CONCENTRATION',
                    'severity': 'HIGH',
                    'entity': region['Region'],
                    'metric': f"{region['percentage']:.1f}%",
                    'description': f"Over-concentration in {region['Region']}",
                    'impact': f"Vulnerable to regional disruptions (geopolitical, natural disasters)",
                    'specific_concern': f"Only {region['supplier_count']} suppliers in this region"
                })
        
        # Issue 3: Performance issues
        for perf in supplier_perf:
            if perf['quality_rating'] < 4.0:
                issues.append({
                    'type': 'QUALITY_CONCERN',
                    'severity': 'MEDIUM',
                    'entity': perf['supplier_name'],
                    'metric': f"{perf['quality_rating']}/5.0",
                    'description': f"Below-standard quality from {perf['supplier_name']}",
                    'impact': "Potential product quality and customer satisfaction issues",
                    'specific_concern': f"Currently spending {perf['spend_percentage']:.1f}% with this supplier"
                })
            
            if perf['delivery_reliability'] < 90:
                issues.append({
                    'type': 'DELIVERY_CONCERN',
                    'severity': 'MEDIUM',
                    'entity': perf['supplier_name'],
                    'metric': f"{perf['delivery_reliability']}%",
                    'description': f"Unreliable delivery from {perf['supplier_name']}",
                    'impact': "Inventory management challenges and potential stockouts",
                    'specific_concern': f"Affecting {perf['spend_percentage']:.1f}% of spend"
                })
        
        return issues
    
    def _identify_opportunities(
        self, supplier_conc: pd.DataFrame, region_conc: pd.DataFrame,
        supplier_perf: List[Dict], supplier_df: pd.DataFrame
    ) -> List[Dict]:
        """Identify specific opportunities for improvement"""
        opportunities = []
        
        # Opportunity 1: Underutilized high-quality suppliers
        for perf in supplier_perf:
            if (perf['quality_rating'] >= 4.5 and 
                perf['delivery_reliability'] >= 95 and 
                perf['spend_percentage'] < 10):
                opportunities.append({
                    'type': 'EXPAND_HIGH_PERFORMER',
                    'priority': 'HIGH',
                    'supplier': perf['supplier_name'],
                    'current_spend': f"{perf['spend_percentage']:.1f}%",
                    'description': f"Expand relationship with high-performing {perf['supplier_name']}",
                    'rationale': f"Quality: {perf['quality_rating']}/5.0, Delivery: {perf['delivery_reliability']}%",
                    'potential_impact': "Improve overall quality while reducing concentration risk"
                })
        
        # Opportunity 2: Geographic diversification
        underrepresented_regions = region_conc[region_conc['percentage'] < 10]
        for _, region in underrepresented_regions.iterrows():
            opportunities.append({
                'type': 'GEOGRAPHIC_DIVERSIFICATION',
                'priority': 'MEDIUM',
                'region': region['Region'],
                'current_spend': f"{region['percentage']:.1f}%",
                'description': f"Expand sourcing from {region['Region']}",
                'rationale': f"Currently only {region['percentage']:.1f}% of spend, {region['supplier_count']} suppliers available",
                'potential_impact': "Reduce regional concentration risk"
            })
        
        # Opportunity 3: New supplier potential
        all_suppliers = supplier_df[supplier_df['quality_rating'] >= 4.0]
        current_supplier_ids = supplier_conc['Supplier_ID'].tolist()
        potential_suppliers = all_suppliers[~all_suppliers['supplier_id'].isin(current_supplier_ids)]
        
        for _, supplier in potential_suppliers.head(5).iterrows():
            opportunities.append({
                'type': 'NEW_SUPPLIER_POTENTIAL',
                'priority': 'MEDIUM',
                'supplier': supplier['supplier_name'],
                'region': supplier['region'],
                'description': f"Consider onboarding {supplier['supplier_name']}",
                'rationale': f"Quality: {supplier['quality_rating']}/5.0, Capacity: {supplier.get('annual_capacity_mt', 'N/A')} MT",
                'potential_impact': "Increase supplier base and negotiation leverage"
            })
        
        return opportunities
    
    def _create_recommendation_from_violation(self, violation: Dict, situation: Dict) -> Dict:
        """Create a specific recommendation from a rule violation"""
        rule_id = violation.get('rule_id', '')
        
        # Map rule violations to specific recommendations
        if rule_id == 'R003':  # Single Supplier Dependency
            details = violation.get('details', {})
            supplier_name = details.get('supplier_name', 'Unknown')
            current_pct = details.get('supplier_percentage', 0)
            excess_amount = details.get('excess_amount', 0)
            
            return {
                'id': f"REC_R003",
                'priority': 'CRITICAL',
                'category': 'SINGLE_SUPPLIER_DEPENDENCY',
                'rule_id': 'R003',
                'title': f"Reduce dependency on {supplier_name}",
                'current_situation': f"{supplier_name} represents {current_pct:.1f}% of total spend",
                'target_state': f"Reduce to maximum 60% (ideally 40-50%)",
                'specific_actions': [
                    {
                        'step': 1,
                        'action': f"Identify ${excess_amount:,.0f} worth of products to move",
                        'timeline': '30 days',
                        'owner': 'Procurement Manager'
                    },
                    {
                        'step': 2,
                        'action': f"Qualify 2-3 alternative suppliers",
                        'timeline': '45 days',
                        'owner': 'Sourcing Team'
                    }
                ],
                'expected_outcome': f"Reduce concentration to 50-55%, mitigate ${details.get('supplier_spend', 0):,.0f} in supply risk",
                'rationale': f"Over-reliance on single supplier creates significant supply chain vulnerability. Rule R003 threshold is 60%."
            }
        
        elif rule_id == 'R001':  # Regional Concentration
            details = violation.get('details', {})
            region = details.get('region', 'Unknown')
            current_pct = details.get('region_percentage', 0)
            
            return {
                'id': f"REC_R001",
                'priority': 'HIGH',
                'category': 'REGIONAL_CONCENTRATION',
                'rule_id': 'R001',
                'title': f"Diversify beyond {region}",
                'current_situation': f"{current_pct:.1f}% of spend concentrated in {region}",
                'target_state': f"Reduce to <40%, establish presence in 2+ additional regions",
                'specific_actions': [
                    {
                        'step': 1,
                        'action': f"Identify alternative regions with production capacity",
                        'timeline': '15 days',
                        'owner': 'Market Intelligence Team'
                    },
                    {
                        'step': 2,
                        'action': f"Shortlist 3-5 suppliers in target regions (India, Thailand, Vietnam)",
                        'timeline': '30 days',
                        'owner': 'Sourcing Team'
                    }
                ],
                'expected_outcome': f"Establish 15-20% of spend in alternative regions, reduce {region} exposure to 35-40%",
                'rationale': f"Regional concentration exceeds 40% threshold (Rule R001). Diversification reduces geopolitical and natural disaster risks."
            }
        
        elif rule_id == 'R002':  # Tail Spend Fragmentation
            details = violation.get('details', {})
            tail_suppliers = details.get('tail_suppliers_count', 0)
            
            return {
                'id': f"REC_R002",
                'priority': 'MEDIUM',
                'category': 'TAIL_SPEND_CONSOLIDATION',
                'rule_id': 'R002',
                'title': f"Consolidate tail spend suppliers",
                'current_situation': f"{tail_suppliers} suppliers in bottom 20% of spend",
                'target_state': f"Reduce to maximum 10 suppliers in tail spend",
                'specific_actions': [
                    {
                        'step': 1,
                        'action': f"Analyze tail spend suppliers for consolidation opportunities",
                        'timeline': '15 days',
                        'owner': 'Procurement Analyst'
                    },
                    {
                        'step': 2,
                        'action': f"Renegotiate contracts or consolidate to top-performing suppliers",
                        'timeline': '60 days',
                        'owner': 'Procurement Manager'
                    }
                ],
                'expected_outcome': f"Reduce administrative overhead and improve negotiation leverage",
                'rationale': f"Excessive fragmentation in tail spend (Rule R002). Consolidation reduces complexity and costs."
            }
        
        elif rule_id == 'R023':  # Supplier Concentration Index (HHI)
            details = violation.get('details', {})
            hhi = details.get('hhi', 0)
            market_structure = details.get('market_structure', 'Unknown')
            
            return {
                'id': f"REC_R023",
                'priority': 'HIGH',
                'category': 'MARKET_CONCENTRATION',
                'rule_id': 'R023',
                'title': f"Reduce supplier concentration (HHI)",
                'current_situation': f"HHI at {hhi:.0f} ({market_structure})",
                'target_state': f"Reduce HHI to <2500 (moderately concentrated market)",
                'specific_actions': [
                    {
                        'step': 1,
                        'action': f"Identify opportunities to split volume among more suppliers",
                        'timeline': '30 days',
                        'owner': 'Strategic Sourcing'
                    },
                    {
                        'step': 2,
                        'action': f"Qualify and onboard additional suppliers",
                        'timeline': '90 days',
                        'owner': 'Sourcing Team'
                    }
                ],
                'expected_outcome': f"Improve market competition and negotiation leverage",
                'rationale': f"High market concentration (Rule R023). Lower HHI indicates healthier supplier competition."
            }
        
        # Default recommendation for other rules
        return {
            'id': f"REC_{rule_id}",
            'priority': violation.get('severity', 'MEDIUM'),
            'category': 'RULE_COMPLIANCE',
            'rule_id': rule_id,
            'title': f"Address {violation.get('rule_name', 'Rule Violation')}",
            'current_situation': violation.get('message', ''),
            'target_state': f"Comply with {violation.get('rule_name', 'rule')} requirements",
            'specific_actions': [
                {
                    'step': 1,
                    'action': violation.get('action_required', 'Take corrective action'),
                    'timeline': '30 days',
                    'owner': 'Procurement Manager'
                }
            ],
            'expected_outcome': f"Achieve compliance with procurement rules",
            'rationale': violation.get('rule_description', 'Compliance with procurement policies')
        }
    
    def _generate_personalized_recommendations(
        self, situation: Dict, input_data: Dict
    ) -> List[Dict]:
        """Generate specific, actionable, personalized recommendations based on rule violations"""
        recommendations = []
        
        # Get rule violations from input if provided
        rule_violations = input_data.get('threshold_violations', [])
        
        # Process rule violations first (highest priority)
        for violation in rule_violations:
            if violation.get('status') == 'VIOLATION':
                rec = self._create_recommendation_from_violation(violation, situation)
                if rec:
                    recommendations.append(rec)
        
        # Then process identified issues from situation analysis
        for issue in situation['key_issues']:
            if issue['type'] == 'HIGH_CONCENTRATION':
                # Extract numeric value from impact string
                impact_value = float(issue['impact'].replace('$', '').replace(',', '').split(' ')[0])
                
                recommendations.append({
                    'id': f"REC_{len(recommendations) + 1}",
                    'priority': 'CRITICAL',
                    'category': 'CONCENTRATION_REDUCTION',
                    'title': f"Reduce dependency on {issue['entity']}",
                    'current_situation': f"{issue['entity']} represents {issue['metric']} of total spend",
                    'target_state': f"Reduce to maximum 30% (ideally 20-25%)",
                    'specific_actions': [
                        {
                            'step': 1,
                            'action': f"Identify ${impact_value * 0.3:,.0f} worth of products to move",
                            'timeline': '30 days',
                            'owner': 'Procurement Manager'
                        },
                        {
                            'step': 2,
                            'action': f"Qualify 2-3 alternative suppliers from situation analysis",
                            'timeline': '45 days',
                            'owner': 'Sourcing Team'
                        },
                        {
                            'step': 3,
                            'action': f"Pilot orders with selected alternatives (10-15% of identified volume)",
                            'timeline': '60 days',
                            'owner': 'Category Manager'
                        },
                        {
                            'step': 4,
                            'action': f"Gradually transition volume based on performance",
                            'timeline': '90-180 days',
                            'owner': 'Procurement Manager'
                        }
                    ],
                    'expected_outcome': f"Reduce concentration to 25-28%, mitigate ${impact_value:,.0f} in supply risk",
                    'rationale': f"Over-reliance on single supplier creates significant supply chain vulnerability. Moving {impact_value * 0.3:,.0f} to alternatives reduces risk while maintaining quality.",
                    'risk_mitigation': [
                        "Maintain quality standards through rigorous qualification",
                        "Ensure pricing competitiveness before transition",
                        "Keep existing supplier engaged during transition"
                    ],
                    'success_metrics': [
                        f"Spend with {issue['entity']} reduced to <30%",
                        "No quality degradation",
                        "Maintain or improve cost position"
                    ]
                })
            
            elif issue['type'] == 'REGIONAL_CONCENTRATION':
                recommendations.append({
                    'id': f"REC_{len(recommendations) + 1}",
                    'priority': 'HIGH',
                    'category': 'GEOGRAPHIC_DIVERSIFICATION',
                    'title': f"Diversify beyond {issue['entity']}",
                    'current_situation': f"{issue['metric']} of spend concentrated in {issue['entity']}",
                    'target_state': f"Reduce to <50%, establish presence in 2+ additional regions",
                    'specific_actions': [
                        {
                            'step': 1,
                            'action': f"Identify alternative regions with production capacity",
                            'timeline': '15 days',
                            'owner': 'Market Intelligence Team'
                        },
                        {
                            'step': 2,
                            'action': f"Shortlist 3-5 suppliers in target regions (India, Thailand, Vietnam)",
                            'timeline': '30 days',
                            'owner': 'Sourcing Team'
                        },
                        {
                            'step': 3,
                            'action': f"Conduct supplier audits and capability assessments",
                            'timeline': '60 days',
                            'owner': 'Quality Team'
                        },
                        {
                            'step': 4,
                            'action': f"Place trial orders representing 10-15% of category spend",
                            'timeline': '90 days',
                            'owner': 'Category Manager'
                        }
                    ],
                    'expected_outcome': f"Establish 15-20% of spend in alternative regions, reduce {issue['entity']} exposure to 40-45%",
                    'risk_mitigation': [
                        "Assess geopolitical and trade policy risks in new regions",
                        "Validate logistics and lead time implications",
                        "Ensure regulatory compliance in new markets"
                    ],
                    'success_metrics': [
                        f"{issue['entity']} concentration <50%",
                        "Successful deliveries from 2+ new regions",
                        "Maintained or improved landed costs"
                    ]
                })
            
            elif issue['type'] == 'QUALITY_CONCERN':
                recommendations.append({
                    'id': f"REC_{len(recommendations) + 1}",
                    'priority': 'HIGH',
                    'category': 'QUALITY_IMPROVEMENT',
                    'title': f"Address quality issues with {issue['entity']}",
                    'current_situation': f"{issue['entity']} quality rating at {issue['metric']}",
                    'target_state': f"Improve to ≥4.0 or replace with higher-quality alternative",
                    'specific_actions': [
                        {
                            'step': 1,
                            'action': f"Conduct root cause analysis of quality issues with {issue['entity']}",
                            'timeline': '15 days',
                            'owner': 'Quality Manager'
                        },
                        {
                            'step': 2,
                            'action': f"Develop corrective action plan with supplier",
                            'timeline': '30 days',
                            'owner': 'Supplier Development Team'
                        },
                        {
                            'step': 3,
                            'action': f"Simultaneously qualify backup suppliers",
                            'timeline': '45 days',
                            'owner': 'Sourcing Team'
                        },
                        {
                            'step': 4,
                            'action': f"Implement 90-day improvement monitoring period",
                            'timeline': '90 days',
                            'owner': 'Quality Manager'
                        },
                        {
                            'step': 5,
                            'action': f"Make go/no-go decision based on improvement trajectory",
                            'timeline': '120 days',
                            'owner': 'Procurement Director'
                        }
                    ],
                    'expected_outcome': f"Quality rating ≥4.0 or successful transition to alternative supplier",
                    'risk_mitigation': [
                        "Have qualified backup ready before making changes",
                        "Gradual transition to minimize disruption",
                        "Maintain quality inspection protocols"
                    ],
                    'success_metrics': [
                        "Quality rating ≥4.0",
                        "Reduction in defect rates by 50%",
                        "No supply disruptions during transition"
                    ]
                })
        
        # Add opportunity-based recommendations
        for opp in situation['opportunities'][:3]:  # Top 3 opportunities
            if opp['type'] == 'EXPAND_HIGH_PERFORMER':
                recommendations.append({
                    'id': f"REC_{len(recommendations) + 1}",
                    'priority': 'MEDIUM',
                    'category': 'SUPPLIER_EXPANSION',
                    'title': f"Expand volume with high-performing {opp['supplier']}",
                    'current_situation': f"{opp['supplier']} currently at {opp['current_spend']} with excellent performance",
                    'target_state': f"Increase to 15-20% of spend",
                    'specific_actions': [
                        {
                            'step': 1,
                            'action': f"Assess {opp['supplier']}'s capacity for increased volume",
                            'timeline': '15 days',
                            'owner': 'Sourcing Team'
                        },
                        {
                            'step': 2,
                            'action': f"Negotiate volume-based pricing improvements",
                            'timeline': '30 days',
                            'owner': 'Procurement Manager'
                        },
                        {
                            'step': 3,
                            'action': f"Gradually increase order volumes by 5% monthly",
                            'timeline': '90 days',
                            'owner': 'Category Manager'
                        }
                    ],
                    'expected_outcome': f"Increase high-quality supplier share while potentially reducing costs",
                    'risk_mitigation': [
                        "Monitor capacity constraints",
                        "Ensure quality maintained at higher volumes",
                        "Avoid creating new concentration risk"
                    ],
                    'success_metrics': [
                        f"{opp['supplier']} at 15-20% of spend",
                        "Quality maintained at ≥4.5",
                        "Cost savings of 3-5% through volume leverage"
                    ]
                })
        
        return recommendations
    
    def _create_implementation_roadmap(
        self, recommendations: List[Dict], situation: Dict
    ) -> Dict:
        """Create a phased implementation roadmap"""
        # Sort recommendations by priority
        priority_order = {'CRITICAL': 1, 'HIGH': 2, 'MEDIUM': 3, 'LOW': 4}
        sorted_recs = sorted(recommendations, key=lambda x: priority_order.get(x['priority'], 5))
        
        roadmap = {
            'phase_1_immediate': {
                'timeline': '0-30 days',
                'focus': 'Critical actions and assessments',
                'recommendations': [],
                'key_milestones': []
            },
            'phase_2_short_term': {
                'timeline': '30-90 days',
                'focus': 'Supplier qualification and pilot programs',
                'recommendations': [],
                'key_milestones': []
            },
            'phase_3_medium_term': {
                'timeline': '90-180 days',
                'focus': 'Volume transitions and optimization',
                'recommendations': [],
                'key_milestones': []
            },
            'phase_4_long_term': {
                'timeline': '180+ days',
                'focus': 'Continuous improvement and monitoring',
                'recommendations': [],
                'key_milestones': []
            }
        }
        
        # Distribute recommendations across phases
        for rec in sorted_recs:
            if rec['priority'] in ['CRITICAL', 'HIGH']:
                roadmap['phase_1_immediate']['recommendations'].append(rec['id'])
                roadmap['phase_2_short_term']['recommendations'].append(rec['id'])
            else:
                roadmap['phase_2_short_term']['recommendations'].append(rec['id'])
                roadmap['phase_3_medium_term']['recommendations'].append(rec['id'])
        
        # Add key milestones
        roadmap['phase_1_immediate']['key_milestones'] = [
            "Complete all critical assessments",
            "Identify alternative suppliers",
            "Initiate quality improvement plans"
        ]
        
        roadmap['phase_2_short_term']['key_milestones'] = [
            "Qualify 2-3 new suppliers",
            "Place pilot orders",
            "Achieve quality targets with existing suppliers"
        ]
        
        roadmap['phase_3_medium_term']['key_milestones'] = [
            "Reduce top supplier concentration to <30%",
            "Establish presence in 2+ new regions",
            "Achieve cost savings targets"
        ]
        
        roadmap['phase_4_long_term']['key_milestones'] = [
            "Maintain balanced supplier portfolio",
            "Continuous performance monitoring",
            "Regular market intelligence updates"
        ]
        
        return roadmap
    
    def _calculate_confidence_scores(
        self, recommendations: List[Dict], situation: Dict
    ) -> Dict:
        """Calculate confidence scores for recommendations"""
        scores = {}
        
        for rec in recommendations:
            confidence = 100.0
            
            # Reduce confidence based on data availability
            if situation['supplier_count'] < 3:
                confidence -= 20
            
            # Reduce confidence for complex changes
            if rec['category'] == 'GEOGRAPHIC_DIVERSIFICATION':
                confidence -= 10
            
            # Increase confidence for data-backed recommendations
            if len(situation['supplier_performance']) > 5:
                confidence += 5
            
            scores[rec['id']] = {
                'confidence_score': round(max(60, min(100, confidence)), 1),
                'data_quality': 'HIGH' if situation['transaction_count'] > 100 else 'MEDIUM',
                'recommendation_strength': rec['priority']
            }
        
        return scores
    
    def _generate_coaching_summary(
        self, situation: Dict, recommendations: List[Dict]
    ) -> str:
        """Generate executive summary of coaching"""
        summary = f"""
PERSONALIZED COACHING SUMMARY

Current Situation:
- Total Spend: {situation['total_spend_formatted']}
- Active Suppliers: {situation['supplier_count']}
- Geographic Regions: {situation['region_count']}

Key Issues Identified: {len(situation['key_issues'])}
{chr(10).join([f"  • {issue['description']}" for issue in situation['key_issues'][:3]])}

Top Recommendations: {len(recommendations)}
{chr(10).join([f"  {i+1}. [{rec['priority']}] {rec['title']}" for i, rec in enumerate(recommendations[:5])])}

Expected Outcomes:
- Reduced concentration risk
- Improved supplier performance
- Enhanced supply chain resilience
- Potential cost savings of 3-8%

Next Steps:
1. Review and prioritize recommendations
2. Assign ownership for each action
3. Initiate Phase 1 activities within 7 days
4. Schedule 30-day progress review
"""
        return summary.strip()
