"""
Supplier Ranking Agent
Ranks suppliers by quality, price, and client criteria matching
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


class SupplierRankingAgent(BaseAgent):
    """
    Agent for ranking and evaluating suppliers
    
    Input:
        - product_category: str
        - region: str (optional)
        - client_criteria: Dict (optional, e.g., {'min_quality': 4.5, 'max_lead_time': 14})
        - top_n: int (default 5)
        
    Output:
        - ranked_suppliers: List[Dict]
        - scoring_breakdown: Dict
        - recommendations: List[str]
    """
    
    def __init__(self):
        super().__init__(
            name="SupplierRanking",
            description="Ranks suppliers by quality, price, and client criteria"
        )
        self.data_loader = DataLoader()
        
        # Default scoring weights
        self.DEFAULT_WEIGHTS = {
            'quality_rating': 0.30,
            'delivery_reliability': 0.25,
            'sustainability_score': 0.15,
            'price_competitiveness': 0.20,
            'certifications': 0.10
        }
    
    def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute supplier ranking
        """
        try:
            product_category = input_data.get('product_category')
            region = input_data.get('region')
            client_criteria = input_data.get('client_criteria', {})
            top_n = input_data.get('top_n', 5)
            custom_weights = input_data.get('weights', self.DEFAULT_WEIGHTS)
            
            if not product_category:
                return self._create_response(
                    success=False,
                    error="product_category is required"
                )
            
            self._log(f"Ranking suppliers for {product_category} in {region or 'all regions'}")
            
            # Load data
            supplier_df = self.data_loader.load_supplier_master()
            spend_df = self.data_loader.load_spend_data()
            
            # Filter suppliers by product category
            category_suppliers = supplier_df[
                supplier_df['product_category'].str.contains(product_category, case=False, na=False) |
                supplier_df['product_category'].str.contains('Edible Oils', case=False, na=False)
            ].copy()
            
            # Filter by region if specified
            if region:
                category_suppliers = category_suppliers[category_suppliers['region'] == region]
            
            if category_suppliers.empty:
                return self._create_response(
                    success=False,
                    error=f"No suppliers found for {product_category}" + (f" in {region}" if region else "")
                )
            
            # Score each supplier
            ranked_suppliers = []
            
            for _, supplier in category_suppliers.iterrows():
                # Calculate scores
                scores = self._calculate_supplier_scores(supplier, spend_df, client_criteria)
                
                # Calculate overall score
                overall_score = sum(
                    scores[key] * custom_weights.get(key, 0)
                    for key in scores.keys()
                )
                
                # Check criteria match
                criteria_match = self._check_criteria_match(supplier, client_criteria)
                
                supplier_data = {
                    'rank': 0,  # Will be set after sorting
                    'supplier_id': supplier['supplier_id'],
                    'supplier_name': supplier['supplier_name'],
                    'country': supplier['country'],
                    'region': supplier['region'],
                    'overall_score': round(overall_score, 2),
                    'scores': scores,
                    'quality_rating': supplier['quality_rating'],
                    'delivery_reliability': supplier['delivery_reliability_pct'],
                    'sustainability_score': supplier['sustainability_score'],
                    'lead_time_days': supplier['lead_time_days'],
                    'certifications': supplier['certifications'].split('|') if pd.notna(supplier['certifications']) else [],
                    'criteria_match': criteria_match,
                    'meets_all_criteria': criteria_match['meets_all'],
                    'strengths': self._identify_strengths(supplier, scores),
                    'weaknesses': self._identify_weaknesses(supplier, scores)
                }
                
                ranked_suppliers.append(supplier_data)
            
            # Sort by overall score
            ranked_suppliers.sort(key=lambda x: x['overall_score'], reverse=True)
            
            # Assign ranks
            for i, supplier in enumerate(ranked_suppliers, 1):
                supplier['rank'] = i
            
            # Get top N
            top_suppliers = ranked_suppliers[:top_n]
            
            # Generate scoring breakdown
            scoring_breakdown = self._generate_scoring_breakdown(
                ranked_suppliers,
                custom_weights
            )
            
            # Generate recommendations
            recommendations = self._generate_recommendations(
                top_suppliers,
                client_criteria
            )
            
            result = {
                'product_category': product_category,
                'region': region or 'All regions',
                'total_suppliers_evaluated': len(ranked_suppliers),
                'top_n': top_n,
                'ranked_suppliers': top_suppliers,
                'all_suppliers': ranked_suppliers,  # Full list
                'scoring_breakdown': scoring_breakdown,
                'recommendations': recommendations,
                'weights_used': custom_weights
            }
            
            self._log(f"Ranking complete: {len(ranked_suppliers)} suppliers evaluated, top {top_n} selected")
            
            return self._create_response(
                success=True,
                data=result,
                sources=['supplier_master.csv', 'spend_data.csv']
            )
            
        except Exception as e:
            self._log(f"Error in supplier ranking: {str(e)}", "ERROR")
            return self._create_response(
                success=False,
                error=str(e)
            )
    
    def _calculate_supplier_scores(
        self, 
        supplier: pd.Series, 
        spend_df: pd.DataFrame,
        client_criteria: Dict
    ) -> Dict[str, float]:
        """Calculate individual scores for a supplier"""
        
        scores = {}
        
        # Quality score (0-100)
        scores['quality_rating'] = (supplier['quality_rating'] / 5.0) * 100
        
        # Delivery reliability score (already 0-100)
        scores['delivery_reliability'] = supplier['delivery_reliability_pct']
        
        # Sustainability score (0-100)
        scores['sustainability_score'] = (supplier['sustainability_score'] / 10.0) * 100
        
        # Price competitiveness (simplified - based on historical spend)
        # Lower average transaction = better price = higher score
        supplier_spend = spend_df[spend_df['Supplier_ID'] == supplier['supplier_id']]
        if not supplier_spend.empty:
            avg_spend = supplier_spend['Spend_USD'].mean()
            # Normalize to 0-100 (simplified)
            scores['price_competitiveness'] = min(100, max(0, 100 - (avg_spend / 10000)))
        else:
            scores['price_competitiveness'] = 50  # Neutral if no history
        
        # Certifications score
        certs = supplier['certifications'].split('|') if pd.notna(supplier['certifications']) else []
        cert_score = min(100, len(certs) * 20)  # 20 points per cert, max 100
        scores['certifications'] = cert_score
        
        return scores
    
    def _check_criteria_match(
        self, 
        supplier: pd.Series, 
        client_criteria: Dict
    ) -> Dict[str, Any]:
        """Check if supplier meets client criteria"""
        
        matches = []
        mismatches = []
        
        # Check minimum quality
        if 'min_quality' in client_criteria:
            min_quality = client_criteria['min_quality']
            if supplier['quality_rating'] >= min_quality:
                matches.append(f"Quality {supplier['quality_rating']} ≥ {min_quality} ✓")
            else:
                mismatches.append(f"Quality {supplier['quality_rating']} < {min_quality} ✗")
        
        # Check maximum lead time
        if 'max_lead_time' in client_criteria:
            max_lead_time = client_criteria['max_lead_time']
            supplier_lead_time = supplier['lead_time_days']
            if isinstance(supplier_lead_time, (int, float)) and supplier_lead_time <= max_lead_time:
                matches.append(f"Lead time {supplier_lead_time} ≤ {max_lead_time} days ✓")
            elif isinstance(supplier_lead_time, (int, float)):
                mismatches.append(f"Lead time {supplier_lead_time} > {max_lead_time} days ✗")
        
        # Check required certifications
        if 'required_certifications' in client_criteria:
            required_certs = client_criteria['required_certifications']
            supplier_certs = supplier['certifications'].split('|') if pd.notna(supplier['certifications']) else []
            
            for req_cert in required_certs:
                if any(req_cert in cert for cert in supplier_certs):
                    matches.append(f"Has {req_cert} ✓")
                else:
                    mismatches.append(f"Missing {req_cert} ✗")
        
        # Check minimum sustainability
        if 'min_sustainability' in client_criteria:
            min_sustainability = client_criteria['min_sustainability']
            if supplier['sustainability_score'] >= min_sustainability:
                matches.append(f"Sustainability {supplier['sustainability_score']} ≥ {min_sustainability} ✓")
            else:
                mismatches.append(f"Sustainability {supplier['sustainability_score']} < {min_sustainability} ✗")
        
        return {
            'meets_all': len(mismatches) == 0,
            'matches': matches,
            'mismatches': mismatches,
            'match_count': len(matches),
            'mismatch_count': len(mismatches)
        }
    
    def _identify_strengths(
        self, 
        supplier: pd.Series, 
        scores: Dict[str, float]
    ) -> List[str]:
        """Identify supplier strengths"""
        
        strengths = []
        
        if scores['quality_rating'] >= 90:
            strengths.append(f"Excellent quality rating ({supplier['quality_rating']}/5.0)")
        
        if scores['delivery_reliability'] >= 95:
            strengths.append(f"Outstanding delivery reliability ({supplier['delivery_reliability_pct']}%)")
        
        if scores['sustainability_score'] >= 80:
            strengths.append(f"Strong sustainability practices ({supplier['sustainability_score']}/10)")
        
        if supplier['years_in_business'] >= 30:
            strengths.append(f"Established supplier ({supplier['years_in_business']} years)")
        
        certs = supplier['certifications'].split('|') if pd.notna(supplier['certifications']) else []
        if len(certs) >= 3:
            strengths.append(f"Well-certified ({len(certs)} certifications)")
        
        return strengths if strengths else ['Meets basic requirements']
    
    def _identify_weaknesses(
        self, 
        supplier: pd.Series, 
        scores: Dict[str, float]
    ) -> List[str]:
        """Identify supplier weaknesses"""
        
        weaknesses = []
        
        if scores['quality_rating'] < 80:
            weaknesses.append(f"Quality rating below target ({supplier['quality_rating']}/5.0)")
        
        if scores['delivery_reliability'] < 90:
            weaknesses.append(f"Delivery reliability needs improvement ({supplier['delivery_reliability_pct']}%)")
        
        if scores['sustainability_score'] < 70:
            weaknesses.append(f"Sustainability score below target ({supplier['sustainability_score']}/10)")
        
        if isinstance(supplier['lead_time_days'], (int, float)) and supplier['lead_time_days'] > 21:
            weaknesses.append(f"Long lead time ({supplier['lead_time_days']} days)")
        
        return weaknesses if weaknesses else ['No significant weaknesses']
    
    def _generate_scoring_breakdown(
        self, 
        ranked_suppliers: List[Dict],
        weights: Dict
    ) -> Dict[str, Any]:
        """Generate scoring breakdown"""
        
        if not ranked_suppliers:
            return {}
        
        top_supplier = ranked_suppliers[0]
        
        return {
            'top_supplier': top_supplier['supplier_name'],
            'top_score': top_supplier['overall_score'],
            'score_range': {
                'highest': ranked_suppliers[0]['overall_score'],
                'lowest': ranked_suppliers[-1]['overall_score'],
                'average': round(sum(s['overall_score'] for s in ranked_suppliers) / len(ranked_suppliers), 2)
            },
            'weights_applied': weights,
            'key_differentiators': [
                f"Quality: {top_supplier['quality_rating']}/5.0",
                f"Delivery: {top_supplier['delivery_reliability']}%",
                f"Sustainability: {top_supplier['sustainability_score']}/10"
            ]
        }
    
    def _generate_recommendations(
        self, 
        top_suppliers: List[Dict],
        client_criteria: Dict
    ) -> List[str]:
        """Generate recommendations"""
        
        recommendations = []
        
        if not top_suppliers:
            return ["No suppliers found matching criteria"]
        
        # Top supplier recommendation
        top = top_suppliers[0]
        recommendations.append(
            f"✅ RECOMMENDED: {top['supplier_name']} (Score: {top['overall_score']:.1f}/100)"
        )
        recommendations.append(
            f"   Strengths: {', '.join(top['strengths'][:2])}"
        )
        
        # Backup supplier
        if len(top_suppliers) > 1:
            backup = top_suppliers[1]
            recommendations.append(
                f"🔄 BACKUP: {backup['supplier_name']} (Score: {backup['overall_score']:.1f}/100)"
            )
        
        # Dual sourcing recommendation
        if len(top_suppliers) >= 2:
            recommendations.append(
                f"💡 STRATEGY: Dual source with 70-30 split between {top_suppliers[0]['supplier_name']} and {top_suppliers[1]['supplier_name']}"
            )
        
        # Criteria match warning
        if client_criteria and not top['meets_all_criteria']:
            recommendations.append(
                f"⚠️ WARNING: Top supplier doesn't meet all criteria. Mismatches: {', '.join(top['criteria_match']['mismatches'])}"
            )
        
        return recommendations
