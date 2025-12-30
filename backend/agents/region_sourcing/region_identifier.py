"""
Region Identifier Agent
Identifies alternative sourcing regions with capacity and risk analysis
"""

import sys
from pathlib import Path
from typing import Dict, Any, List

root_path = Path(__file__).parent.parent.parent.parent
if str(root_path) not in sys.path:
    sys.path.insert(0, str(root_path))

from backend.agents.base_agent import BaseAgent
from backend.engines.data_loader import DataLoader


class RegionIdentifierAgent(BaseAgent):
    """
    Agent for identifying alternative sourcing regions
    
    Input:
        - current_region: str (e.g., 'APAC', 'Malaysia')
        - product_category: str
        - client_id: str (optional)
        
    Output:
        - alternative_regions: List[Dict]
        - risk_comparison: Dict
        - capacity_analysis: Dict
        - recommendation: str
    """
    
    def __init__(self):
        super().__init__(
            name="RegionIdentifier",
            description="Identifies alternative sourcing regions with capacity and risk analysis"
        )
        self.data_loader = DataLoader()
        
        # Regional capacity and characteristics
        self.REGION_DATA = {
            'APAC': {
                'countries': ['Malaysia', 'Indonesia', 'Thailand', 'India', 'China', 'Japan'],
                'strengths': ['High capacity', 'Competitive pricing', 'Established supply chains'],
                'risks': ['Regional concentration', 'Geopolitical tensions', 'Natural disasters'],
                'capacity_score': 9
            },
            'Europe': {
                'countries': ['Spain', 'Germany', 'France', 'UK', 'Switzerland'],
                'strengths': ['High quality standards', 'Political stability', 'Strong regulations'],
                'risks': ['Higher costs', 'Limited capacity for some products'],
                'capacity_score': 7
            },
            'Americas': {
                'countries': ['USA', 'Canada', 'Mexico', 'Brazil'],
                'strengths': ['Large market', 'Advanced logistics', 'Innovation'],
                'risks': ['Higher labor costs', 'Trade policies'],
                'capacity_score': 8
            },
            'Middle East': {
                'countries': ['UAE', 'Saudi Arabia', 'Israel'],
                'strengths': ['Strategic location', 'Growing capacity'],
                'risks': ['Political instability', 'Water scarcity'],
                'capacity_score': 5
            },
            'Africa': {
                'countries': ['South Africa', 'Egypt', 'Kenya'],
                'strengths': ['Emerging markets', 'Cost competitive'],
                'risks': ['Infrastructure challenges', 'Political instability'],
                'capacity_score': 4
            }
        }
        
        # Country-specific data
        self.COUNTRY_DATA = {
            'Malaysia': {'region': 'APAC', 'capacity_score': 9, 'risk_score': 8.3, 'cost_index': 85},
            'Indonesia': {'region': 'APAC', 'capacity_score': 9, 'risk_score': 7.3, 'cost_index': 80},
            'Thailand': {'region': 'APAC', 'capacity_score': 8, 'risk_score': 8.0, 'cost_index': 82},
            'India': {'region': 'APAC', 'capacity_score': 9, 'risk_score': 7.3, 'cost_index': 75},
            'China': {'region': 'APAC', 'capacity_score': 10, 'risk_score': 7.7, 'cost_index': 78},
            'Spain': {'region': 'Europe', 'capacity_score': 7, 'risk_score': 8.3, 'cost_index': 105},
            'Germany': {'region': 'Europe', 'capacity_score': 8, 'risk_score': 9.0, 'cost_index': 110},
            'USA': {'region': 'Americas', 'capacity_score': 9, 'risk_score': 9.0, 'cost_index': 120},
            'Brazil': {'region': 'Americas', 'capacity_score': 8, 'risk_score': 6.5, 'cost_index': 90},
            'Ukraine': {'region': 'Europe', 'capacity_score': 7, 'risk_score': 4.3, 'cost_index': 70},
            'Israel': {'region': 'Middle East', 'capacity_score': 6, 'risk_score': 6.7, 'cost_index': 115}
        }
    
    def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute region identification
        """
        try:
            current_region = input_data.get('current_region')
            product_category = input_data.get('product_category')
            
            if not current_region or not product_category:
                return self._create_response(
                    success=False,
                    error="current_region and product_category are required"
                )
            
            self._log(f"Identifying alternatives to {current_region} for {product_category}")
            
            # Load supplier data to see what's available
            supplier_df = self.data_loader.load_supplier_master()
            
            # Get suppliers for this product category
            category_suppliers = supplier_df[
                supplier_df['product_category'].str.contains(product_category, case=False, na=False) |
                supplier_df['product_category'].str.contains('Edible Oils', case=False, na=False)
            ]
            
            # Identify alternative regions
            alternative_regions = []
            
            # Group suppliers by region
            regions_available = category_suppliers.groupby('region').agg({
                'supplier_id': 'count',
                'quality_rating': 'mean',
                'sustainability_score': 'mean',
                'delivery_reliability_pct': 'mean'
            }).reset_index()
            
            for _, region_row in regions_available.iterrows():
                region = region_row['region']
                
                # Skip current region
                if region == current_region:
                    continue
                
                region_info = self.REGION_DATA.get(region, {
                    'strengths': ['Available suppliers'],
                    'risks': ['Unknown'],
                    'capacity_score': 5
                })
                
                # Get countries in this region
                region_countries = category_suppliers[category_suppliers['region'] == region]['country'].unique()
                
                alternative_regions.append({
                    'region': region,
                    'supplier_count': int(region_row['supplier_id']),
                    'avg_quality_rating': round(region_row['quality_rating'], 2),
                    'avg_sustainability': round(region_row['sustainability_score'], 2),
                    'avg_delivery_reliability': round(region_row['delivery_reliability_pct'], 2),
                    'capacity_score': region_info['capacity_score'],
                    'countries': list(region_countries),
                    'strengths': region_info['strengths'],
                    'risks': region_info['risks'],
                    'recommendation_score': self._calculate_recommendation_score(region_row, region_info)
                })
            
            # Sort by recommendation score
            alternative_regions.sort(key=lambda x: x['recommendation_score'], reverse=True)
            
            # Risk comparison
            risk_comparison = self._compare_regions(
                current_region, 
                alternative_regions
            )
            
            # Capacity analysis
            capacity_analysis = self._analyze_capacity(
                alternative_regions, 
                product_category
            )
            
            # Generate recommendation
            recommendation = self._generate_recommendation(
                current_region,
                alternative_regions,
                risk_comparison
            )
            
            result = {
                'current_region': current_region,
                'product_category': product_category,
                'alternative_regions': alternative_regions,
                'alternative_count': len(alternative_regions),
                'risk_comparison': risk_comparison,
                'capacity_analysis': capacity_analysis,
                'recommendation': recommendation
            }
            
            self._log(f"Region identification complete: {len(alternative_regions)} alternatives found")
            
            return self._create_response(
                success=True,
                data=result,
                sources=['supplier_master.csv', 'regional_capacity_database']
            )
            
        except Exception as e:
            self._log(f"Error in region identification: {str(e)}", "ERROR")
            return self._create_response(
                success=False,
                error=str(e)
            )
    
    def _calculate_recommendation_score(
        self, 
        region_row: Any, 
        region_info: Dict
    ) -> float:
        """Calculate overall recommendation score for a region"""
        
        # Weighted scoring
        quality_score = region_row['quality_rating'] * 20  # Max 100
        sustainability_score = region_row['sustainability_score'] * 10  # Max 100
        delivery_score = region_row['delivery_reliability_pct']  # Already 0-100
        capacity_score = region_info['capacity_score'] * 10  # Max 100
        supplier_count_score = min(region_row['supplier_id'] * 10, 50)  # Max 50
        
        total_score = (
            quality_score * 0.25 +
            sustainability_score * 0.15 +
            delivery_score * 0.20 +
            capacity_score * 0.25 +
            supplier_count_score * 0.15
        )
        
        return round(total_score, 2)
    
    def _compare_regions(
        self, 
        current_region: str, 
        alternatives: List[Dict]
    ) -> Dict[str, Any]:
        """Compare current region with alternatives"""
        
        if not alternatives:
            return {
                'comparison': 'No alternatives available',
                'recommendation': 'Continue with current region'
            }
        
        top_alternative = alternatives[0]
        
        comparison = {
            'current_region': current_region,
            'top_alternative': top_alternative['region'],
            'score_difference': top_alternative['recommendation_score'],
            'quality_comparison': f"{top_alternative['avg_quality_rating']} vs current",
            'risk_trade_off': f"Diversification benefit vs {', '.join(top_alternative['risks'][:2])}",
            'recommendation': 'DIVERSIFY' if top_alternative['recommendation_score'] > 70 else 'EVALUATE'
        }
        
        return comparison
    
    def _analyze_capacity(
        self, 
        alternatives: List[Dict], 
        product_category: str
    ) -> Dict[str, Any]:
        """Analyze capacity across regions"""
        
        total_suppliers = sum(r['supplier_count'] for r in alternatives)
        high_capacity_regions = [r for r in alternatives if r['capacity_score'] >= 8]
        
        return {
            'total_alternative_suppliers': total_suppliers,
            'high_capacity_regions': [r['region'] for r in high_capacity_regions],
            'high_capacity_count': len(high_capacity_regions),
            'capacity_sufficient': total_suppliers >= 3,
            'recommendation': 'Sufficient capacity available' if total_suppliers >= 3 else 'Limited capacity - careful planning needed'
        }
    
    def _generate_recommendation(
        self, 
        current_region: str, 
        alternatives: List[Dict],
        risk_comparison: Dict
    ) -> str:
        """Generate recommendation"""
        
        if not alternatives:
            return f"❌ No alternative regions found for this product category. Continue with {current_region}."
        
        rec = f"🌍 REGIONAL DIVERSIFICATION OPPORTUNITY\n\n"
        rec += f"Current Region: {current_region}\n"
        rec += f"Alternative Regions Found: {len(alternatives)}\n\n"
        
        rec += "TOP 3 ALTERNATIVES:\n\n"
        for i, alt in enumerate(alternatives[:3], 1):
            rec += f"{i}. {alt['region']} (Score: {alt['recommendation_score']:.1f}/100)\n"
            rec += f"   Suppliers: {alt['supplier_count']}\n"
            rec += f"   Quality: {alt['avg_quality_rating']}/5.0\n"
            rec += f"   Countries: {', '.join(alt['countries'][:3])}\n"
            rec += f"   Strengths: {', '.join(alt['strengths'][:2])}\n"
            rec += f"   Risks: {', '.join(alt['risks'][:2])}\n\n"
        
        rec += f"RECOMMENDATION: {risk_comparison['recommendation']}\n"
        rec += f"Diversify to {alternatives[0]['region']} to reduce regional concentration risk."
        
        return rec
