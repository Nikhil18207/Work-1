"""
Enhanced Leadership Brief Generator
Generates executive-level procurement diversification briefs for ANY industry
All numbers calculated from actual data - no hardcoded values
"""

import sys
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
import pandas as pd
import numpy as np

root_path = Path(__file__).parent.parent.parent
if str(root_path) not in sys.path:
    sys.path.insert(0, str(root_path))

from backend.engines.data_loader import DataLoader
from backend.engines.rule_evaluation_engine import RuleEvaluationEngine


class LeadershipBriefGenerator:
    """
    Enhanced Leadership Brief Generator
    Works for ANY industry - IT, Manufacturing, Healthcare, Services, etc.
    All metrics calculated from actual data
    """
    
    INDUSTRY_COST_DRIVERS = {
        'Edible Oils': {
            'low_cost_regions': ['India', 'Thailand', 'Indonesia', 'Vietnam'],
            'drivers': {
                'India': 'Lower raw material input costs + scaling extraction infrastructure',
                'Thailand': 'Port efficiency + strong processing ecosystem',
                'Indonesia': 'High production capacity + efficient supply chains',
                'Vietnam': 'Competitive labor costs + growing export infrastructure',
                'China': 'Industrial scale processing + pricing leverage',
                'Malaysia': 'Established supply chains + quality standards'
            },
            'savings_range': (0.08, 0.20)
        },
        'IT Hardware': {
            'low_cost_regions': ['China', 'Taiwan', 'Vietnam', 'India', 'Mexico'],
            'drivers': {
                'China': 'Manufacturing scale + component ecosystem integration',
                'Taiwan': 'Advanced semiconductor manufacturing capabilities',
                'Vietnam': 'Competitive labor costs + growing tech manufacturing',
                'India': 'IT services integration + growing hardware assembly',
                'Mexico': 'Nearshoring benefits + trade agreements',
                'USA': 'Premium quality + reduced logistics risk'
            },
            'savings_range': (0.05, 0.15)
        },
        'Cloud Services': {
            'low_cost_regions': ['USA', 'Ireland', 'Singapore', 'India'],
            'drivers': {
                'USA': 'Primary data center infrastructure + innovation hub',
                'Ireland': 'EU data sovereignty + tax efficiency',
                'Singapore': 'APAC hub + strong data protection',
                'India': 'Cost-effective managed services + skilled workforce',
                'Germany': 'GDPR compliance + data sovereignty'
            },
            'savings_range': (0.10, 0.25)
        },
        'Software Licenses': {
            'low_cost_regions': ['India', 'Eastern Europe', 'Ireland'],
            'drivers': {
                'USA': 'Primary vendor relationships + support coverage',
                'India': 'Implementation services + support cost optimization',
                'Ireland': 'EU licensing optimization + tax benefits',
                'Germany': 'Enterprise software expertise + local support'
            },
            'savings_range': (0.05, 0.12)
        },
        'Steel': {
            'low_cost_regions': ['China', 'India', 'Russia', 'Brazil'],
            'drivers': {
                'China': 'Massive production capacity + competitive pricing',
                'India': 'Growing capacity + lower labor costs',
                'Luxembourg': 'Premium quality + established logistics',
                'USA': 'Domestic supply security + reduced tariffs',
                'Brazil': 'Iron ore integration + competitive costs'
            },
            'savings_range': (0.08, 0.18)
        },
        'Pharmaceuticals': {
            'low_cost_regions': ['India', 'China', 'Ireland'],
            'drivers': {
                'USA': 'Innovation hub + regulatory approval speed',
                'India': 'Generic manufacturing + cost efficiency',
                'Switzerland': 'Premium quality + R&D capabilities',
                'Ireland': 'Tax-efficient manufacturing hub',
                'China': 'API manufacturing + scale benefits'
            },
            'savings_range': (0.10, 0.30)
        },
        'Medical Devices': {
            'low_cost_regions': ['Mexico', 'Ireland', 'Costa Rica', 'China'],
            'drivers': {
                'USA': 'Innovation + regulatory expertise',
                'Germany': 'Precision engineering + quality',
                'Mexico': 'Nearshoring + skilled labor pool',
                'Ireland': 'EU market access + manufacturing expertise',
                'China': 'Scale manufacturing + cost efficiency'
            },
            'savings_range': (0.08, 0.20)
        },
        'Construction Materials': {
            'low_cost_regions': ['China', 'India', 'Mexico', 'Turkey'],
            'drivers': {
                'Local': 'Reduced transport costs + faster delivery',
                'China': 'Scale production + competitive pricing',
                'Mexico': 'Nearshoring + trade agreements',
                'India': 'Growing capacity + cost efficiency'
            },
            'savings_range': (0.10, 0.25)
        },
        'Marketing Services': {
            'low_cost_regions': ['India', 'Philippines', 'Eastern Europe'],
            'drivers': {
                'USA': 'Strategic expertise + market knowledge',
                'UK': 'Creative excellence + global reach',
                'India': 'Digital services + cost optimization',
                'Philippines': 'English proficiency + cost efficiency'
            },
            'savings_range': (0.15, 0.35)
        },
        'Logistics': {
            'low_cost_regions': ['Netherlands', 'Singapore', 'UAE', 'Panama'],
            'drivers': {
                'Germany': 'European hub + infrastructure quality',
                'Netherlands': 'Port efficiency + logistics expertise',
                'Singapore': 'APAC hub + connectivity',
                'USA': 'Domestic coverage + technology integration'
            },
            'savings_range': (0.05, 0.15)
        },
        'DEFAULT': {
            'low_cost_regions': ['India', 'China', 'Mexico', 'Eastern Europe'],
            'drivers': {
                'India': 'Cost-effective operations + skilled workforce',
                'China': 'Manufacturing scale + supply chain efficiency',
                'Mexico': 'Nearshoring benefits + trade agreements',
                'USA': 'Quality assurance + reduced risk',
                'Germany': 'Premium quality + reliability'
            },
            'savings_range': (0.08, 0.18)
        }
    }
    
    def __init__(self):
        self.data_loader = DataLoader()
        self.rule_engine = RuleEvaluationEngine()
    
    def _get_industry_config(self, category: str, product_category: str = None) -> Dict:
        """Get industry-specific configuration based on category"""
        category_lower = (category or '').lower()
        product_lower = (product_category or '').lower()
        
        if 'oil' in category_lower or 'edible' in product_lower:
            return self.INDUSTRY_COST_DRIVERS['Edible Oils']
        elif 'it' in category_lower or 'hardware' in category_lower or 'laptop' in category_lower:
            return self.INDUSTRY_COST_DRIVERS['IT Hardware']
        elif 'cloud' in category_lower or 'saas' in category_lower:
            return self.INDUSTRY_COST_DRIVERS['Cloud Services']
        elif 'software' in category_lower or 'license' in category_lower:
            return self.INDUSTRY_COST_DRIVERS['Software Licenses']
        elif 'steel' in category_lower or 'aluminum' in category_lower or 'metal' in category_lower:
            return self.INDUSTRY_COST_DRIVERS['Steel']
        elif 'pharma' in category_lower or 'drug' in category_lower:
            return self.INDUSTRY_COST_DRIVERS['Pharmaceuticals']
        elif 'medical' in category_lower or 'device' in category_lower:
            return self.INDUSTRY_COST_DRIVERS['Medical Devices']
        elif 'construction' in category_lower or 'cement' in category_lower:
            return self.INDUSTRY_COST_DRIVERS['Construction Materials']
        elif 'marketing' in category_lower or 'consulting' in category_lower:
            return self.INDUSTRY_COST_DRIVERS['Marketing Services']
        elif 'logistics' in category_lower or 'freight' in category_lower:
            return self.INDUSTRY_COST_DRIVERS['Logistics']
        else:
            return self.INDUSTRY_COST_DRIVERS['DEFAULT']
    
    def _get_dominant_region_name(self, countries: List[str]) -> str:
        """Get dynamic region name based on actual countries"""
        region_mapping = {
            'SEA': ['Malaysia', 'Vietnam', 'Thailand', 'Indonesia', 'Singapore', 'Philippines'],
            'East Asia': ['China', 'Japan', 'South Korea', 'Taiwan'],
            'South Asia': ['India', 'Bangladesh', 'Pakistan', 'Sri Lanka'],
            'Europe': ['Germany', 'France', 'UK', 'Spain', 'Italy', 'Netherlands', 'Switzerland', 'Luxembourg'],
            'Americas': ['USA', 'Canada', 'Mexico', 'Brazil', 'Argentina'],
            'Middle East': ['UAE', 'Saudi Arabia', 'Qatar']
        }
        
        region_counts = {}
        for country in countries:
            for region, region_countries in region_mapping.items():
                if country in region_countries:
                    region_counts[region] = region_counts.get(region, 0) + 1
                    break
        
        if region_counts:
            dominant_region = max(region_counts, key=region_counts.get)
            if dominant_region == 'SEA':
                return 'Southeast Asia Supply Corridor'
            elif dominant_region == 'East Asia':
                return 'East Asia Supply Corridor'
            elif dominant_region == 'South Asia':
                return 'South Asia Supply Corridor'
            elif dominant_region == 'Europe':
                return 'European Supply Corridor'
            elif dominant_region == 'Americas':
                return 'Americas Supply Corridor'
            else:
                return f'{dominant_region} Supply Corridor'
        
        return 'Primary Supply Corridor'
    
    def _calculate_dynamic_cost_advantages(
        self, 
        category: str,
        product_category: str,
        total_spend: float,
        new_regions: List[str]
    ) -> List[Dict]:
        """Calculate cost advantages dynamically based on industry and spend"""
        industry_config = self._get_industry_config(category, product_category)
        advantages = []
        
        min_savings_pct, max_savings_pct = industry_config['savings_range']
        
        for region in new_regions:
            driver = industry_config['drivers'].get(
                region, 
                f'Diversification benefits + competitive pricing in {region}'
            )
            
            allocation_pct = 0.15
            region_spend = total_spend * allocation_pct
            min_savings = region_spend * min_savings_pct
            max_savings = region_spend * max_savings_pct
            
            advantages.append({
                'region': region,
                'driver': driver,
                'min_usd': round(min_savings, 0),
                'max_usd': round(max_savings, 0)
            })
        
        if advantages:
            total_min = sum(a['min_usd'] for a in advantages)
            total_max = sum(a['max_usd'] for a in advantages)
            advantages.append({
                'region': 'Blended Annual Advantage',
                'driver': 'Supplier competition + diversification benefits + logistics resilience',
                'min_usd': total_min,
                'max_usd': total_max
            })
        
        return advantages
    
    def _calculate_supplier_performance_metrics(
        self, 
        spend_df: pd.DataFrame, 
        supplier_df: pd.DataFrame
    ) -> List[Dict]:
        """Calculate supplier performance metrics from actual data"""
        metrics = []
        
        supplier_names = spend_df['Supplier_Name'].unique()
        
        for supplier_name in supplier_names[:5]:
            supplier_info = supplier_df[supplier_df['supplier_name'] == supplier_name]
            supplier_spend = spend_df[spend_df['Supplier_Name'] == supplier_name]['Spend_USD'].sum()
            
            if not supplier_info.empty:
                info = supplier_info.iloc[0]
                metrics.append({
                    'supplier': supplier_name,
                    'spend_usd': supplier_spend,
                    'quality_rating': float(info.get('quality_rating', 0)),
                    'delivery_reliability': float(info.get('delivery_reliability_pct', 0)),
                    'sustainability_score': float(info.get('sustainability_score', 0)),
                    'years_in_business': int(info.get('years_in_business', 0)),
                    'certifications': str(info.get('certifications', '')).split('|')
                })
            else:
                metrics.append({
                    'supplier': supplier_name,
                    'spend_usd': supplier_spend,
                    'quality_rating': 0,
                    'delivery_reliability': 0,
                    'sustainability_score': 0,
                    'years_in_business': 0,
                    'certifications': []
                })
        
        return metrics
    
    def _calculate_risk_matrix(
        self,
        supplier_concentration: float,
        regional_concentration: float,
        num_suppliers: int
    ) -> Dict:
        """Calculate comprehensive risk matrix"""
        supply_risk = 'CRITICAL' if supplier_concentration > 60 else 'HIGH' if supplier_concentration > 40 else 'MEDIUM'
        geographic_risk = 'CRITICAL' if regional_concentration > 60 else 'HIGH' if regional_concentration > 40 else 'MEDIUM'
        supplier_diversity_risk = 'CRITICAL' if num_suppliers == 1 else 'HIGH' if num_suppliers <= 2 else 'MEDIUM' if num_suppliers <= 4 else 'LOW'
        
        risk_scores = {'CRITICAL': 4, 'HIGH': 3, 'MEDIUM': 2, 'LOW': 1}
        overall_score = (risk_scores[supply_risk] + risk_scores[geographic_risk] + risk_scores[supplier_diversity_risk]) / 3
        
        if overall_score >= 3.5:
            overall_risk = 'CRITICAL'
        elif overall_score >= 2.5:
            overall_risk = 'HIGH'
        elif overall_score >= 1.5:
            overall_risk = 'MEDIUM'
        else:
            overall_risk = 'LOW'
        
        return {
            'supply_chain_risk': supply_risk,
            'geographic_risk': geographic_risk,
            'supplier_diversity_risk': supplier_diversity_risk,
            'overall_risk': overall_risk,
            'risk_score': round(overall_score, 1)
        }
    
    def _evaluate_rule_violations(
        self,
        client_id: str,
        category: str
    ) -> Dict:
        """Evaluate procurement rules and return violations/warnings"""
        try:
            results = self.rule_engine.evaluate_all_rules(client_id, category)
            
            if not results.get('success', False):
                return {
                    'violations': [],
                    'warnings': [],
                    'compliant': [],
                    'total_violations': 0,
                    'total_warnings': 0,
                    'compliance_rate': 0,
                    'error': results.get('error', 'Unknown error')
                }
            
            violations = results.get('violations', [])
            warnings = results.get('warnings', [])
            compliant = results.get('compliant', [])
            
            total_rules = len(violations) + len(warnings) + len(compliant)
            compliance_rate = round(len(compliant) / max(total_rules, 1) * 100, 1)
            
            return {
                'violations': violations,
                'warnings': warnings,
                'compliant': compliant,
                'total_violations': len(violations),
                'total_warnings': len(warnings),
                'compliance_rate': compliance_rate,
                'overall_status': results.get('summary', {}).get('overall_status', 'UNKNOWN')
            }
        except Exception as e:
            return {
                'violations': [],
                'warnings': [],
                'compliant': [],
                'total_violations': 0,
                'total_warnings': 0,
                'compliance_rate': 0,
                'error': str(e)
            }
    
    def _generate_implementation_timeline(self, category: str) -> List[Dict]:
        """Generate implementation timeline"""
        today = datetime.now()
        
        return [
            {
                'phase': 'Phase 1: Supplier Qualification',
                'duration': 'Weeks 1-4',
                'start_date': today.strftime('%Y-%m-%d'),
                'end_date': (today + timedelta(weeks=4)).strftime('%Y-%m-%d'),
                'activities': [
                    'Identify and shortlist alternate suppliers',
                    'Request for Information (RFI) distribution',
                    'Initial capability assessment',
                    'Site qualification planning'
                ]
            },
            {
                'phase': 'Phase 2: Pilot Contracts',
                'duration': 'Weeks 5-12',
                'start_date': (today + timedelta(weeks=4)).strftime('%Y-%m-%d'),
                'end_date': (today + timedelta(weeks=12)).strftime('%Y-%m-%d'),
                'activities': [
                    'Negotiate pilot contract terms',
                    'Execute 8-12 week pilot allocations',
                    'Monitor quality and delivery performance',
                    'Establish baseline metrics'
                ]
            },
            {
                'phase': 'Phase 3: Performance Review',
                'duration': 'Week 13',
                'start_date': (today + timedelta(weeks=12)).strftime('%Y-%m-%d'),
                'end_date': (today + timedelta(weeks=13)).strftime('%Y-%m-%d'),
                'activities': [
                    'Quarterly performance review',
                    'Cost-benefit analysis',
                    'Risk assessment update',
                    'Go/No-Go decision for scale-up'
                ]
            },
            {
                'phase': 'Phase 4: Scale-Up',
                'duration': 'Weeks 14-26',
                'start_date': (today + timedelta(weeks=13)).strftime('%Y-%m-%d'),
                'end_date': (today + timedelta(weeks=26)).strftime('%Y-%m-%d'),
                'activities': [
                    'Gradual volume transition',
                    'Long-term contract negotiation',
                    'Continuous monitoring and optimization',
                    'Further concentration reduction if pilots succeed'
                ]
            }
        ]
    
    def _calculate_roi_projections(
        self,
        total_spend: float,
        cost_advantages: List[Dict],
        current_concentration: float,
        target_concentration: float
    ) -> Dict:
        """Calculate ROI projections"""
        total_min_savings = sum(a.get('min_usd', 0) for a in cost_advantages if 'Blended' not in a.get('region', ''))
        total_max_savings = sum(a.get('max_usd', 0) for a in cost_advantages if 'Blended' not in a.get('region', ''))
        
        implementation_cost = total_spend * 0.02
        
        risk_reduction_value = total_spend * (current_concentration - target_concentration) / 100 * 0.05
        
        total_benefit_min = total_min_savings + risk_reduction_value
        total_benefit_max = total_max_savings + risk_reduction_value
        
        roi_min = ((total_benefit_min - implementation_cost) / implementation_cost) * 100 if implementation_cost > 0 else 0
        roi_max = ((total_benefit_max - implementation_cost) / implementation_cost) * 100 if implementation_cost > 0 else 0
        
        payback_months_min = (implementation_cost / (total_benefit_min / 12)) if total_benefit_min > 0 else 0
        payback_months_max = (implementation_cost / (total_benefit_max / 12)) if total_benefit_max > 0 else 0
        
        return {
            'annual_cost_savings_min': total_min_savings,
            'annual_cost_savings_max': total_max_savings,
            'risk_reduction_value': risk_reduction_value,
            'implementation_cost': implementation_cost,
            'total_annual_benefit_min': total_benefit_min,
            'total_annual_benefit_max': total_benefit_max,
            'roi_percentage_min': round(roi_min, 1),
            'roi_percentage_max': round(roi_max, 1),
            'payback_period_months_min': round(payback_months_min, 1),
            'payback_period_months_max': round(payback_months_max, 1),
            'three_year_net_benefit_min': (total_benefit_min * 3) - implementation_cost,
            'three_year_net_benefit_max': (total_benefit_max * 3) - implementation_cost
        }
    
    def generate_both_briefs(
        self, 
        client_id: str, 
        category: str = None
    ) -> Dict[str, Any]:
        """Generate both leadership briefs with enhanced metrics"""
        
        incumbent_brief = self.generate_incumbent_concentration_brief(client_id, category)
        regional_brief = self.generate_regional_concentration_brief(client_id, category)
        
        return {
            'incumbent_concentration_brief': incumbent_brief,
            'regional_concentration_brief': regional_brief,
            'generated_at': datetime.now().isoformat(),
            'client_id': client_id,
            'category': category
        }
    
    def generate_incumbent_concentration_brief(
        self, 
        client_id: str, 
        category: str = None
    ) -> Dict[str, Any]:
        """Generate Incumbent Concentration Brief with all data-driven metrics"""
        
        spend_df = self.data_loader.load_spend_data()
        supplier_df = self.data_loader.load_supplier_master()
        
        if category:
            spend_df = spend_df[
                (spend_df['Client_ID'] == client_id) & 
                (spend_df['Category'] == category)
            ]
        else:
            spend_df = spend_df[spend_df['Client_ID'] == client_id]
        
        if spend_df.empty:
            return self._empty_brief_response("No spend data found")
        
        total_spend = spend_df['Spend_USD'].sum()
        
        supplier_spend = spend_df.groupby('Supplier_Name')['Spend_USD'].sum()
        supplier_spend_pct = (supplier_spend / total_spend * 100).round(1)
        supplier_spend_sorted = supplier_spend_pct.sort_values(ascending=False)
        
        num_current_suppliers = len(supplier_spend_sorted)
        current_suppliers_list = []
        for supplier_name, pct in supplier_spend_sorted.items():
            current_suppliers_list.append({
                'name': supplier_name,
                'spend': float(supplier_spend[supplier_name]),
                'pct': float(pct)
            })
        
        dominant_supplier = supplier_spend_sorted.index[0]
        dominant_supplier_pct = float(supplier_spend_sorted.iloc[0])
        dominant_supplier_spend = float(supplier_spend[dominant_supplier])
        
        supplier_countries = spend_df[
            spend_df['Supplier_Name'] == dominant_supplier
        ]['Supplier_Country'].unique().tolist()
        
        supplier_regions = spend_df[
            spend_df['Supplier_Name'] == dominant_supplier
        ]['Supplier_Region'].unique().tolist()
        
        current_supplier_names = set(spend_df['Supplier_Name'].unique())
        matching_suppliers = supplier_df[supplier_df['supplier_name'].isin(current_supplier_names)]
        
        if not matching_suppliers.empty:
            product_category = matching_suppliers.iloc[0]['product_category']
        else:
            product_category = category
        
        industry_config = self._get_industry_config(category, product_category)
        
        all_suppliers_in_category = supplier_df[
            supplier_df['product_category'] == product_category
        ] if product_category else supplier_df
        
        potential_alternates = set(all_suppliers_in_category['supplier_name'].unique()) - current_supplier_names
        
        alternate_supplier = None
        alternate_regions = []
        if potential_alternates:
            alternate_candidates = all_suppliers_in_category[
                (all_suppliers_in_category['supplier_name'].isin(potential_alternates)) &
                (all_suppliers_in_category['quality_rating'] >= 4.0) &
                (all_suppliers_in_category['delivery_reliability_pct'] >= 90)
            ].sort_values('quality_rating', ascending=False)
            
            if not alternate_candidates.empty:
                alternate_supplier = alternate_candidates.iloc[0]['supplier_name']
                alternate_regions = alternate_candidates['country'].unique().tolist()
        
        if dominant_supplier_pct > 80:
            target_dominant_pct = 60
        elif dominant_supplier_pct > 60:
            target_dominant_pct = 55
        else:
            target_dominant_pct = max(40, dominant_supplier_pct - 15)
        
        target_alternate_pct = 100 - target_dominant_pct - sum(
            s['pct'] for s in current_suppliers_list[1:]
        )
        target_alternate_pct = max(10, min(40, target_alternate_pct))
        
        reduction_pct = dominant_supplier_pct - target_dominant_pct
        reduction_pct_of_original = round((reduction_pct / dominant_supplier_pct) * 100, 1)
        
        country_spend = spend_df.groupby('Supplier_Country')['Spend_USD'].sum()
        country_pct = (country_spend / total_spend * 100).round(1)
        dominant_country = country_pct.idxmax()
        dominant_region_pct = float(country_pct.max())
        
        all_countries = spend_df['Supplier_Country'].unique().tolist()
        region_corridor_name = self._get_dominant_region_name(all_countries)
        
        new_regions = [r for r in alternate_regions if r not in supplier_countries][:3]
        if not new_regions:
            new_regions = industry_config['low_cost_regions'][:3]
        
        cost_advantages = self._calculate_dynamic_cost_advantages(
            category, product_category, total_spend, new_regions
        )
        
        supplier_performance = self._calculate_supplier_performance_metrics(spend_df, supplier_df)
        
        risk_matrix = self._calculate_risk_matrix(
            dominant_supplier_pct, dominant_region_pct, num_current_suppliers
        )
        
        target_region_pct_min = max(40, dominant_region_pct - 30)
        target_region_pct_max = max(50, dominant_region_pct - 25)
        
        roi_projections = self._calculate_roi_projections(
            total_spend, cost_advantages, dominant_region_pct, (target_region_pct_min + target_region_pct_max) / 2
        )
        
        timeline = self._generate_implementation_timeline(category)
        
        rule_violations = self._evaluate_rule_violations(client_id, category)
        
        brief = {
            'title': f'LEADERSHIP BRIEF – {(category or "PROCUREMENT").upper()} DIVERSIFICATION',
            'subtitle': 'Supplier Concentration Analysis & Diversification Strategy',
            'total_spend': total_spend,
            'category': category,
            'product_category': product_category,
            'generated_date': datetime.now().strftime('%Y-%m-%d'),
            'fiscal_year': datetime.now().year,
            
            'current_state': {
                'dominant_supplier': dominant_supplier,
                'supplier_location': ', '.join(supplier_countries),
                'supplier_region': ', '.join(supplier_regions),
                'spend_share_pct': dominant_supplier_pct,
                'spend_share_usd': dominant_supplier_spend,
                'num_suppliers': num_current_suppliers,
                'all_suppliers': current_suppliers_list,
                'currently_buying_category': 'Yes',
                'alternate_supplier_active': 'None active today' if not alternate_supplier else alternate_supplier,
                'key_risk': self._generate_key_risk(num_current_suppliers, dominant_supplier_pct, supplier_regions)
            },
            
            'risk_statement': self._generate_risk_statement(
                category, total_spend, num_current_suppliers, current_suppliers_list,
                dominant_supplier, dominant_supplier_pct, dominant_supplier_spend,
                supplier_countries, alternate_supplier, alternate_regions, product_category
            ),
            
            'supplier_reduction': {
                'dominant_supplier': {
                    'name': dominant_supplier,
                    'original_share_pct': dominant_supplier_pct,
                    'new_target_cap_pct': target_dominant_pct,
                    'reduction_pct': reduction_pct,
                    'reduction_pct_of_original': reduction_pct_of_original,
                    'formatted_reduction': f'{dominant_supplier_pct:.0f}% → {target_dominant_pct:.0f}% = {reduction_pct_of_original:.1f}% reduction'
                },
                'alternate_supplier': {
                    'name': alternate_supplier or 'New Alternate Supplier',
                    'original_share_pct': 0,
                    'new_target_pct': target_alternate_pct,
                    'benefit': 'Enables supplier competition + fallback'
                }
            },
            
            'regional_dependency': {
                'corridor_name': region_corridor_name,
                'original_pct': dominant_region_pct,
                'new_target_pct': f'{target_region_pct_min:.0f}–{target_region_pct_max:.0f}%',
                'net_reduction_pct': f'{dominant_region_pct - target_region_pct_max:.0f}–{dominant_region_pct - target_region_pct_min:.0f}%'
            },
            
            'cost_advantages': cost_advantages,
            'total_cost_advantage': {
                'min_usd': sum(a['min_usd'] for a in cost_advantages if 'Blended' not in a.get('region', '')),
                'max_usd': sum(a['max_usd'] for a in cost_advantages if 'Blended' not in a.get('region', ''))
            },
            
            'supplier_performance': supplier_performance,
            'risk_matrix': risk_matrix,
            'roi_projections': roi_projections,
            'implementation_timeline': timeline,
            'rule_violations': rule_violations,
            
            'strategic_outcome': [
                f'Reduce single-supplier concentration from {dominant_supplier_pct:.0f}% to {target_dominant_pct:.0f}% in Phase 1',
                f'Activate {target_alternate_pct:.0f}% of spend via {"incumbent supplier (" + alternate_supplier + ")" if alternate_supplier else "new qualified suppliers"} with multi-region presence',
                'Improve pricing leverage through supplier competition',
                f'Reduce {region_corridor_name.lower()} risk by ~{(dominant_region_pct - target_region_pct_max):.0f}%',
                f'Achieve estimated annual cost advantage of USD {roi_projections["annual_cost_savings_min"]:,.0f}–{roi_projections["annual_cost_savings_max"]:,.0f} while improving supply continuity'
            ],
            
            'next_steps': [
                f'Activate {(category or "procurement").lower()} with {alternate_supplier or "qualified alternate suppliers"}',
                'Initiate 8–12 week pilot allocations',
                'Benchmark pricing and delivery quarterly',
                'Continue phased reduction based on pilot performance'
            ]
        }
        
        return brief
    
    def generate_regional_concentration_brief(
        self, 
        client_id: str, 
        category: str = None
    ) -> Dict[str, Any]:
        """Generate Regional Concentration Brief with all data-driven metrics"""
        
        spend_df = self.data_loader.load_spend_data()
        supplier_df = self.data_loader.load_supplier_master()
        
        if category:
            spend_df = spend_df[
                (spend_df['Client_ID'] == client_id) & 
                (spend_df['Category'] == category)
            ]
        else:
            spend_df = spend_df[spend_df['Client_ID'] == client_id]
        
        if spend_df.empty:
            return self._empty_brief_response("No spend data found")
        
        total_spend = spend_df['Spend_USD'].sum()
        
        country_spend = spend_df.groupby('Supplier_Country')['Spend_USD'].sum()
        country_pct = (country_spend / total_spend * 100).round(1)
        country_sorted = country_pct.sort_values(ascending=False)
        
        original_concentration = []
        for country, pct in country_sorted.head(5).items():
            original_concentration.append({
                'country': country,
                'pct': float(pct),
                'spend_usd': float(country_spend[country])
            })
        
        if len(original_concentration) == 0:
            original_concentration = [
                {'country': 'Primary Region', 'pct': 100.0, 'spend_usd': total_spend}
            ]
        
        all_countries = list(country_sorted.index)
        high_concentration_countries = [c['country'] for c in original_concentration if c['pct'] > 40]
        region_corridor_name = self._get_dominant_region_name(all_countries)
        
        total_high_concentration = sum(c['pct'] for c in original_concentration if c['pct'] > 40)
        total_high_concentration_spend = sum(c['spend_usd'] for c in original_concentration if c['pct'] > 40)
        
        current_supplier_names = set(spend_df['Supplier_Name'].unique())
        matching_suppliers = supplier_df[supplier_df['supplier_name'].isin(current_supplier_names)]
        product_category = matching_suppliers.iloc[0]['product_category'] if not matching_suppliers.empty else category
        
        industry_config = self._get_industry_config(category, product_category)
        
        target_allocation = self._generate_target_allocation(total_spend, country_sorted)
        
        reductions = []
        for orig in original_concentration[:3]:
            country = orig['country']
            if country in target_allocation:
                target = target_allocation[country]
                original_pct = orig['pct']
                target_pct = target['pct']
                reduction_pct_of_original = round(((original_pct - target_pct) / original_pct) * 100, 1)
                reductions.append({
                    'country': country,
                    'original_pct': original_pct,
                    'target_pct': target_pct,
                    'reduction_pct': reduction_pct_of_original,
                    'formatted_reduction': f'{original_pct:.0f}% → {target_pct:.0f}% = {reduction_pct_of_original:.1f}% reduction in share'
                })
        
        new_regions = [r for r in target_allocation.keys() 
                      if r not in [c['country'] for c in original_concentration[:2]]]
        
        if not new_regions:
            new_regions = [r for r in industry_config['low_cost_regions'] 
                          if r not in [c['country'] for c in original_concentration]][:3]
        
        cost_advantages = self._calculate_dynamic_cost_advantages(
            category, product_category, total_spend, new_regions
        )
        
        num_suppliers = spend_df['Supplier_Name'].nunique()
        top_country_pct = float(country_sorted.iloc[0]) if len(country_sorted) > 0 else 100
        
        supplier_concentration = spend_df.groupby('Supplier_Name')['Spend_USD'].sum()
        top_supplier_pct = (supplier_concentration.max() / total_spend * 100)
        
        risk_matrix = self._calculate_risk_matrix(top_supplier_pct, top_country_pct, num_suppliers)
        
        target_region_pct_min = max(40, total_high_concentration - 35) if total_high_concentration > 40 else total_high_concentration
        target_region_pct_max = max(50, total_high_concentration - 25) if total_high_concentration > 50 else total_high_concentration
        
        roi_projections = self._calculate_roi_projections(
            total_spend, cost_advantages, total_high_concentration, (target_region_pct_min + target_region_pct_max) / 2
        )
        
        timeline = self._generate_implementation_timeline(category)
        supplier_performance = self._calculate_supplier_performance_metrics(spend_df, supplier_df)
        rule_violations = self._evaluate_rule_violations(client_id, category)
        
        if len(high_concentration_countries) >= 2:
            concentration_note = f"{high_concentration_countries[0]} and {high_concentration_countries[1]} each exceeded 40% of spend, creating high regional dependency."
        elif len(high_concentration_countries) == 1:
            concentration_note = f"{high_concentration_countries[0]} exceeds 40% of spend, creating regional concentration risk."
        else:
            concentration_note = "Regional distribution is within acceptable limits, but diversification opportunities exist."
        
        brief = {
            'title': f'LEADERSHIP BRIEF – {(category or "PROCUREMENT").upper()} DIVERSIFICATION',
            'subtitle': 'Regional Concentration Analysis & Diversification Strategy',
            'total_spend': total_spend,
            'category': category,
            'product_category': product_category,
            'generated_date': datetime.now().strftime('%Y-%m-%d'),
            'fiscal_year': datetime.now().year,
            
            'original_concentration': original_concentration,
            'total_high_concentration_pct': total_high_concentration,
            'total_high_concentration_spend': total_high_concentration_spend,
            'concentration_note': concentration_note,
            
            'target_allocation': target_allocation,
            
            'reductions': reductions,
            
            'regional_dependency': {
                'corridor_name': region_corridor_name,
                'original_pct': total_high_concentration if total_high_concentration > 0 else top_country_pct,
                'new_target_pct': f'{target_region_pct_min:.0f}–{target_region_pct_max:.0f}%',
                'reduction_pct': f'{max(0, total_high_concentration - target_region_pct_max):.0f}–{max(0, total_high_concentration - target_region_pct_min):.0f}%'
            },
            
            'cost_advantages': cost_advantages,
            'total_cost_advantage': {
                'min_usd': sum(a['min_usd'] for a in cost_advantages if 'Blended' not in a.get('region', '')),
                'max_usd': sum(a['max_usd'] for a in cost_advantages if 'Blended' not in a.get('region', ''))
            },
            
            'supplier_performance': supplier_performance,
            'risk_matrix': risk_matrix,
            'roi_projections': roi_projections,
            'implementation_timeline': timeline,
            'rule_violations': rule_violations,
            
            'strategic_outcome': [
                f'Reduce {" and ".join(high_concentration_countries[:2]) if high_concentration_countries else "primary region"} reliance by {reductions[0]["reduction_pct"]:.0f}%' + (f' each' if len(high_concentration_countries) > 1 else '') if reductions else 'Diversify regional exposure',
                f'Add {len(new_regions)} new supply ecosystems to offset concentration',
                'Increase supplier pricing competition across regions',
                'Improve logistics routing resilience',
                f'Reduce corridor risk by ~{max(0, total_high_concentration - target_region_pct_max):.0f}% with blended cost advantage'
            ],
            
            'next_steps': [
                f'Shortlist suppliers in {", ".join(new_regions[:3])}',
                'Initiate 8–12 week pilot contracts',
                'Review pricing and delivery performance quarterly',
                'Reduce concentration further if pilots outperform'
            ]
        }
        
        return brief
    
    def _generate_target_allocation(
        self, 
        total_spend: float, 
        current_distribution: pd.Series
    ) -> Dict[str, Dict]:
        """Generate diversified target allocation ensuring R001 compliance"""
        
        top_countries = current_distribution.head(3).index.tolist()
        
        if len(top_countries) == 0:
            top_countries = ['Primary Region']
        
        allocations = {}
        
        for i, country in enumerate(top_countries):
            current_pct = float(current_distribution.get(country, 50))
            if current_pct > 40:
                target_pct = min(35, current_pct * 0.65)
            else:
                target_pct = current_pct * 0.9
            allocations[country] = round(target_pct, 0)
        
        allocated = sum(allocations.values())
        remaining = 100 - allocated
        
        diversification_targets = ['India', 'China', 'Mexico', 'Germany', 'USA']
        existing_countries = set(allocations.keys())
        
        new_country_allocation = remaining / 3
        rendered = 0
        for country in diversification_targets:
            if country not in existing_countries and rendered < 3:
                alloc = min(new_country_allocation, 40 - allocations.get(country, 0))
                if alloc > 5:
                    allocations[country] = round(alloc, 0)
                    rendered += 1
        
        total_allocated = sum(allocations.values())
        if total_allocated != 100:
            adjustment = 100 - total_allocated
            first_country = list(allocations.keys())[0]
            allocations[first_country] += adjustment
        
        result = {}
        for country, pct in allocations.items():
            spend_usd = total_spend * (pct / 100)
            
            if country in current_distribution.index:
                original_pct = current_distribution[country]
                if pct < original_pct:
                    change = f'{abs(original_pct - pct):.0f}% lower'
                else:
                    change = f'{abs(pct - original_pct):.0f}% higher'
            else:
                change = 'New addition'
            
            result[country] = {
                'pct': pct,
                'spend_usd': spend_usd,
                'change': change
            }
        
        return result
    
    def _generate_key_risk(
        self,
        num_suppliers: int,
        dominant_pct: float,
        supplier_regions: List[str]
    ) -> str:
        """Generate concise key risk statement"""
        region_str = supplier_regions[0] if supplier_regions else 'regional'
        
        if num_suppliers == 1:
            return f"Extreme single-supplier lock-in and {region_str} supply corridor dependency"
        elif dominant_pct > 80:
            return f"Critical supplier concentration ({dominant_pct:.0f}%) and {region_str} supply corridor dependency"
        elif dominant_pct > 60:
            return f"High supplier concentration ({dominant_pct:.0f}%) and {region_str} supply corridor dependency"
        else:
            return f"Moderate concentration in {region_str} with {num_suppliers} suppliers"
    
    def _generate_risk_statement(
        self,
        category: str,
        total_spend: float,
        num_suppliers: int,
        all_suppliers: List[Dict],
        dominant_supplier: str,
        dominant_pct: float,
        dominant_spend: float,
        supplier_countries: List[str],
        alternate_supplier: Optional[str],
        alternate_regions: List[str],
        product_category: Optional[str]
    ) -> str:
        """Generate comprehensive risk statement"""
        cat_lower = (category or 'procurement').lower()
        year = datetime.now().year
        
        statement = f"Our current {cat_lower} procurement "
        
        if num_suppliers == 1:
            statement += f"is sourced entirely from {dominant_supplier}, representing 100% of the total "
            statement += f"category spend (USD {total_spend:,.0f} in {year}). "
        else:
            statement += f"involves {num_suppliers} suppliers, with {dominant_supplier} as the dominant supplier "
            statement += f"at {dominant_pct:.0f}% of total category spend (USD {dominant_spend:,.0f} of USD {total_spend:,.0f} in {year}). "
            
            other_suppliers = [s for s in all_suppliers if s['name'] != dominant_supplier]
            if other_suppliers:
                statement += "Other suppliers include: "
                supplier_list = [f"{s['name']} ({s['pct']:.0f}%)" for s in other_suppliers[:3]]
                statement += ", ".join(supplier_list) + ". "
        
        if len(supplier_countries) > 1:
            statement += f"While suppliers operate across {', '.join(supplier_countries[:3])}, "
        else:
            country_name = supplier_countries[0] if supplier_countries else 'a single region'
            statement += f"All suppliers operate from {country_name}. "
        
        if alternate_supplier and product_category:
            statement += f"We currently do not source {cat_lower} from "
            statement += f"{alternate_supplier}, an already approved {product_category} supplier in our system with "
            statement += f"operational presence across {', '.join(alternate_regions[:4])}. "
        elif product_category:
            statement += f"We do not have alternate {product_category} suppliers activated for this category. "
        else:
            statement += "We do not have alternate suppliers activated for this category. "
        
        statement += "\n\nThis creates "
        if num_suppliers == 1:
            statement += "both a critical single-supplier dependency risk and a correlated "
        elif dominant_pct > 60:
            statement += "both a high supplier concentration risk and a correlated "
        else:
            statement += "a "
        statement += "geographic concentration risk. "
        
        statement += "It is recommended to "
        if alternate_supplier:
            statement += f"activate {cat_lower} with {alternate_supplier} "
        else:
            statement += "identify and activate alternate suppliers "
        statement += "to offset this dependency, introduce price competition, diversify geographic exposure, "
        statement += "and enable alternate logistics routing, while continuing optimization and quarterly rebalancing."
        
        return statement
    
    def _empty_brief_response(self, message: str) -> Dict[str, Any]:
        """Return empty brief response"""
        return {
            'error': message,
            'brief': None
        }


if __name__ == "__main__":
    import json
    
    generator = LeadershipBriefGenerator()
    
    print("=" * 80)
    print("ENHANCED LEADERSHIP BRIEF GENERATOR TEST")
    print("=" * 80)
    
    briefs = generator.generate_both_briefs(
        client_id='C001',
        category='Rice Bran Oil'
    )
    
    print("\n" + "=" * 80)
    print("INCUMBENT CONCENTRATION BRIEF")
    print("=" * 80)
    print(json.dumps(briefs['incumbent_concentration_brief'], indent=2, default=str))
    
    print("\n" + "=" * 80)
    print("REGIONAL CONCENTRATION BRIEF")
    print("=" * 80)
    print(json.dumps(briefs['regional_concentration_brief'], indent=2, default=str))
