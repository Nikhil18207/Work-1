"""
Enhanced Supplier Ranking System

Identifies top suppliers in selected regions and ranks them by:
1. Quality criteria (quality rating, certifications, delivery reliability)
2. Client-specific criteria (preferences, requirements, strategic fit)
3. Cost-benefit analysis

Provides detailed reasoning for top 3 supplier selections.
"""

from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
import pandas as pd
from enum import Enum


class RankingCriteria(Enum):
    """Ranking criteria types"""
    QUALITY = "quality"
    COST = "cost"
    DELIVERY = "delivery"
    CAPACITY = "capacity"
    SUSTAINABILITY = "sustainability"
    CERTIFICATIONS = "certifications"
    EXPERIENCE = "experience"


@dataclass
class SupplierScore:
    """Supplier scoring breakdown"""
    supplier_id: str
    supplier_name: str
    region: str
    total_score: float
    quality_score: float
    cost_score: float
    delivery_score: float
    capacity_score: float
    sustainability_score: float
    certification_score: float
    client_fit_score: float
    reasoning: str


@dataclass
class Top3Recommendation:
    """Top 3 supplier recommendation with reasoning"""
    rank: int
    supplier: SupplierScore
    allocation_percentage: float
    cost_impact: float
    risk_assessment: str
    key_advantages: List[str]
    potential_concerns: List[str]
    implementation_steps: List[str]


class EnhancedSupplierRanking:
    """
    Enhanced supplier ranking system
    
    Features:
    - Multi-criteria scoring
    - Client-specific weighting
    - Detailed reasoning generation
    - Top 3 selection with allocation recommendations
    """
    
    def __init__(self, data_loader):
        self.data_loader = data_loader
        self.default_weights = {
            RankingCriteria.QUALITY: 25,
            RankingCriteria.COST: 25,
            RankingCriteria.DELIVERY: 15,
            RankingCriteria.CAPACITY: 15,
            RankingCriteria.SUSTAINABILITY: 10,
            RankingCriteria.CERTIFICATIONS: 10
        }
    
    def rank_suppliers_in_regions(
        self,
        regions: List[str],
        category: str,
        client_id: str,
        client_criteria: Optional[Dict[str, float]] = None,
        top_n: int = 10
    ) -> List[SupplierScore]:
        """
        Rank suppliers in selected regions
        
        Args:
            regions: List of regions to search
            category: Product category
            client_id: Client identifier
            client_criteria: Optional client-specific criteria weights
            top_n: Number of top suppliers to return
            
        Returns:
            List of top N suppliers with scores
        """
        supplier_df = self.data_loader.load_supplier_master()
        client_df = self.data_loader.load_client_master()
        
        # Get client requirements
        client_info = client_df[client_df['client_id'] == client_id]
        if not client_info.empty:
            client_info = client_info.iloc[0]
        else:
            client_info = None
        
        # Filter suppliers by region and category
        filtered_suppliers = supplier_df[
            supplier_df['region'].isin(regions)
        ].copy()
        
        # Filter by category capability (if product_category column exists)
        if 'product_category' in filtered_suppliers.columns:
            filtered_suppliers = filtered_suppliers[
                filtered_suppliers['product_category'].str.contains(
                    category, case=False, na=False
                )
            ]
        
        if filtered_suppliers.empty:
            return []
        
        # Score each supplier
        supplier_scores = []
        
        for _, supplier in filtered_suppliers.iterrows():
            score = self._calculate_supplier_score(
                supplier, client_info, client_criteria
            )
            supplier_scores.append(score)
        
        # Sort by total score
        supplier_scores.sort(key=lambda x: x.total_score, reverse=True)
        
        return supplier_scores[:top_n]
    
    def select_top_3_with_reasoning(
        self,
        supplier_scores: List[SupplierScore],
        total_volume: float,
        category: str
    ) -> List[Top3Recommendation]:
        """
        Select top 3 suppliers with detailed reasoning
        
        Args:
            supplier_scores: List of scored suppliers
            total_volume: Total volume to allocate
            category: Product category
            
        Returns:
            Top 3 recommendations with reasoning
        """
        if len(supplier_scores) < 3:
            # If less than 3 suppliers, use what we have
            top_3_suppliers = supplier_scores
        else:
            top_3_suppliers = supplier_scores[:3]
        
        recommendations = []
        
        # Calculate allocation percentages
        # Use score-based allocation (higher score = higher allocation)
        total_scores = sum(s.total_score for s in top_3_suppliers)
        
        for rank, supplier in enumerate(top_3_suppliers, 1):
            # Calculate allocation percentage based on score
            if total_scores > 0:
                allocation_pct = (supplier.total_score / total_scores) * 100
            else:
                allocation_pct = 100 / len(top_3_suppliers)
            
            # Cap at 30% per supplier (R003 rule)
            allocation_pct = min(allocation_pct, 30.0)
            
            # Generate recommendation
            recommendation = self._generate_recommendation(
                rank, supplier, allocation_pct, category
            )
            recommendations.append(recommendation)
        
        # Normalize allocations to 100%
        total_allocation = sum(r.allocation_percentage for r in recommendations)
        if total_allocation > 0:
            for rec in recommendations:
                rec.allocation_percentage = round(
                    (rec.allocation_percentage / total_allocation) * 100, 1
                )
        
        return recommendations
    
    def _get_supplier_price(self, supplier: pd.Series, category: str) -> float:
        """
        Get supplier price from pricing benchmarks
        
        Since supplier_master.csv doesn't have prices, we use:
        1. Pricing benchmarks by product category and region
        2. Apply supplier quality premium/discount
        """
        region = supplier.get('region', 'Global')
        quality_rating = supplier.get('quality_rating', 4.0)
        
        # Get market benchmark price
        benchmark_price = self._get_market_benchmark_price(category, region)
        
        # Adjust based on supplier quality (higher quality = slight premium)
        quality_factor = 1.0
        if quality_rating >= 4.5:
            quality_factor = 1.05  # 5% premium for excellent quality
        elif quality_rating >= 4.0:
            quality_factor = 1.0   # Market price for good quality
        elif quality_rating >= 3.5:
            quality_factor = 0.95  # 5% discount for average quality
        else:
            quality_factor = 0.90  # 10% discount for below average
        
        return benchmark_price * quality_factor
    
    def _get_market_benchmark_price(self, category: str, region: str = 'Global') -> float:
        """
        Get market benchmark price from pricing_benchmarks.csv
        
        Args:
            category: Product category (e.g., 'Rice Bran Oil')
            region: Region (e.g., 'Asia Pacific', 'Europe', 'Global')
            
        Returns:
            Benchmark price in USD per kg
        """
        try:
            # Load pricing benchmarks
            pricing_df = pd.read_csv('data/structured/pricing_benchmarks.csv')
            
            # Map category to product category in benchmarks
            category_map = {
                'Rice Bran Oil': 'Vegetable Oils',
                'Sunflower Oil': 'Vegetable Oils',
                'Palm Oil': 'Vegetable Oils',
                'Canola Oil': 'Vegetable Oils',
                'Olive Oil': 'Olive Oil',
                'Wheat Flour': 'Grains & Flours',
                'Corn Flour': 'Grains & Flours',
                'Turmeric': 'Spices & Seasonings',
                'Butter': 'Dairy Products',
                'Sugar': 'Sweeteners',
                'Almonds': 'Nuts & Seeds',
                'Salmon': 'Seafood'
            }
            
            product_category = category_map.get(category, 'Vegetable Oils')
            
            # Try to find exact match (category + region)
            exact_match = pricing_df[
                (pricing_df['product_category'] == product_category) &
                (pricing_df['region'] == region)
            ]
            
            if not exact_match.empty:
                return exact_match.iloc[0]['benchmark_price_usd_per_kg']
            
            # Try global benchmark
            global_match = pricing_df[
                (pricing_df['product_category'] == product_category) &
                (pricing_df['region'] == 'Global')
            ]
            
            if not global_match.empty:
                return global_match.iloc[0]['benchmark_price_usd_per_kg']
            
            # Fallback to first match in category
            category_match = pricing_df[
                pricing_df['product_category'] == product_category
            ]
            
            if not category_match.empty:
                return category_match.iloc[0]['benchmark_price_usd_per_kg']
            
            # Ultimate fallback
            return 2.50  # Default vegetable oil price
            
        except Exception as e:
            print(f"Warning: Could not load pricing benchmarks: {e}")
            return 2.50  # Default fallback
    
    def _calculate_supplier_score(
        self,
        supplier: pd.Series,
        client_info: Optional[pd.Series],
        client_criteria: Optional[Dict[str, float]]
    ) -> SupplierScore:
        """Calculate comprehensive supplier score"""
        
        # Use client criteria weights if provided, otherwise use defaults
        weights = client_criteria if client_criteria else self.default_weights
        
        # Quality score (0-100)
        quality_rating = supplier.get('quality_rating', 0)
        quality_score = (quality_rating / 5.0) * 100
        
        # Cost score (0-100) - lower price is better
        # Get real price from pricing benchmarks
        list_price = self._get_supplier_price(supplier, category)
        market_benchmark = self._get_market_benchmark_price(category, supplier.get('region', 'Global'))
        
        if market_benchmark > 0:
            # Calculate cost score based on how supplier price compares to market
            price_ratio = list_price / market_benchmark
            if price_ratio <= 0.9:  # 10% below market
                cost_score = 100
            elif price_ratio <= 1.0:  # At or slightly below market
                cost_score = 90
            elif price_ratio <= 1.1:  # Up to 10% above market
                cost_score = 70
            elif price_ratio <= 1.2:  # Up to 20% above market
                cost_score = 50
            else:  # More than 20% above market
                cost_score = 30
        else:
            # Fallback if no benchmark available
            cost_score = 70  # Neutral score
        
        # Delivery score (0-100)
        delivery_reliability = supplier.get('delivery_reliability_pct', 0)
        delivery_score = delivery_reliability
        
        # Capacity score (0-100)
        capacity = supplier.get('annual_capacity_tons', 0)
        capacity_score = min(100, (capacity / 10000) * 100)  # Normalize to 10k tons
        
        # Sustainability score (0-100)
        sustainability_rating = supplier.get('sustainability_score', 0)
        sustainability_score = (sustainability_rating / 10.0) * 100
        
        # Certification score (0-100)
        certifications = str(supplier.get('certifications', '')).split('|')
        certification_score = min(100, len(certifications) * 20)  # 20 points per cert, max 100
        
        # Client fit score (0-100)
        client_fit_score = self._calculate_client_fit(supplier, client_info)
        
        # Calculate weighted total score
        total_score = (
            quality_score * weights.get(RankingCriteria.QUALITY, 25) / 100 +
            cost_score * weights.get(RankingCriteria.COST, 25) / 100 +
            delivery_score * weights.get(RankingCriteria.DELIVERY, 15) / 100 +
            capacity_score * weights.get(RankingCriteria.CAPACITY, 15) / 100 +
            sustainability_score * weights.get(RankingCriteria.SUSTAINABILITY, 10) / 100 +
            certification_score * weights.get(RankingCriteria.CERTIFICATIONS, 10) / 100
        )
        
        # Generate reasoning
        reasoning = self._generate_scoring_reasoning(
            supplier, quality_score, cost_score, delivery_score,
            capacity_score, sustainability_score, certification_score
        )
        
        return SupplierScore(
            supplier_id=supplier.get('supplier_id', 'UNKNOWN'),
            supplier_name=supplier.get('supplier_name', 'Unknown Supplier'),
            region=supplier.get('region', 'Unknown'),
            total_score=round(total_score, 2),
            quality_score=round(quality_score, 2),
            cost_score=round(cost_score, 2),
            delivery_score=round(delivery_score, 2),
            capacity_score=round(capacity_score, 2),
            sustainability_score=round(sustainability_score, 2),
            certification_score=round(certification_score, 2),
            client_fit_score=round(client_fit_score, 2),
            reasoning=reasoning
        )
    
    def _calculate_client_fit(
        self, supplier: pd.Series, client_info: Optional[pd.Series]
    ) -> float:
        """Calculate how well supplier fits client requirements"""
        if client_info is None:
            return 70.0  # Default moderate fit
        
        fit_score = 70.0  # Base score
        
        # Check certification requirements
        required_certs = str(client_info.get('certifications_required', '')).split('|')
        supplier_certs = str(supplier.get('certifications', '')).split('|')
        
        if required_certs and required_certs[0]:
            matching_certs = set(required_certs) & set(supplier_certs)
            cert_match_pct = len(matching_certs) / len(required_certs) * 100
            fit_score = cert_match_pct
        
        # Check quality requirements
        min_quality = client_info.get('quality_requirements', 'Standard')
        supplier_quality = supplier.get('quality_rating', 0)
        
        if min_quality == 'Premium' and supplier_quality >= 4.5:
            fit_score += 10
        elif min_quality == 'High' and supplier_quality >= 4.0:
            fit_score += 5
        
        return min(100, fit_score)
    
    def _generate_scoring_reasoning(
        self, supplier: pd.Series, quality_score: float, cost_score: float,
        delivery_score: float, capacity_score: float, sustainability_score: float,
        certification_score: float
    ) -> str:
        """Generate human-readable reasoning for the score"""
        strengths = []
        weaknesses = []
        
        # Identify strengths (score > 80)
        if quality_score > 80:
            strengths.append(f"Excellent quality rating ({supplier.get('quality_rating', 0)}/5)")
        if cost_score > 80:
            strengths.append("Competitive pricing")
        if delivery_score > 90:
            strengths.append(f"Outstanding delivery reliability ({delivery_score:.0f}%)")
        if capacity_score > 70:
            strengths.append("Sufficient production capacity")
        if sustainability_score > 80:
            strengths.append("Strong sustainability practices")
        if certification_score > 60:
            strengths.append("Well-certified supplier")
        
        # Identify weaknesses (score < 60)
        if quality_score < 60:
            weaknesses.append("Below-average quality rating")
        if cost_score < 60:
            weaknesses.append("Higher pricing than market average")
        if delivery_score < 85:
            weaknesses.append("Delivery reliability needs improvement")
        if capacity_score < 50:
            weaknesses.append("Limited production capacity")
        
        # Build reasoning string
        reasoning = ""
        if strengths:
            reasoning += "Strengths: " + ", ".join(strengths) + ". "
        if weaknesses:
            reasoning += "Areas for improvement: " + ", ".join(weaknesses) + "."
        
        if not reasoning:
            reasoning = "Balanced supplier profile across all criteria."
        
        return reasoning
    
    def _generate_recommendation(
        self, rank: int, supplier: SupplierScore, allocation_pct: float, category: str
    ) -> Top3Recommendation:
        """Generate detailed recommendation for a supplier"""
        
        # Identify key advantages
        key_advantages = []
        if supplier.quality_score > 80:
            key_advantages.append(f"High quality rating ({supplier.quality_score:.0f}/100)")
        if supplier.cost_score > 75:
            key_advantages.append("Competitive pricing advantage")
        if supplier.delivery_score > 90:
            key_advantages.append(f"Excellent delivery reliability ({supplier.delivery_score:.0f}%)")
        if supplier.sustainability_score > 80:
            key_advantages.append("Strong ESG performance")
        
        # Identify potential concerns
        potential_concerns = []
        if supplier.quality_score < 70:
            potential_concerns.append("Quality rating below target")
        if supplier.delivery_score < 85:
            potential_concerns.append("Delivery performance needs monitoring")
        if supplier.capacity_score < 60:
            potential_concerns.append("Capacity constraints may limit scalability")
        
        # Generate implementation steps
        implementation_steps = [
            f"1. Initiate supplier qualification process for {supplier.supplier_name}",
            f"2. Request detailed quotation for {category}",
            "3. Conduct site visit and quality audit",
            f"4. Negotiate contract terms for {allocation_pct:.1f}% volume allocation",
            "5. Start with pilot order (8-12 weeks)",
            "6. Review performance and scale up if successful"
        ]
        
        # Calculate cost impact (simplified)
        cost_impact = (supplier.cost_score - 75) / 10  # Rough estimate
        
        # Risk assessment
        if supplier.total_score > 85:
            risk_assessment = "LOW - Strong supplier profile"
        elif supplier.total_score > 70:
            risk_assessment = "MEDIUM - Good supplier, monitor performance"
        else:
            risk_assessment = "MEDIUM-HIGH - Requires close oversight"
        
        return Top3Recommendation(
            rank=rank,
            supplier=supplier,
            allocation_percentage=allocation_pct,
            cost_impact=round(cost_impact, 2),
            risk_assessment=risk_assessment,
            key_advantages=key_advantages,
            potential_concerns=potential_concerns if potential_concerns else ["None identified"],
            implementation_steps=implementation_steps
        )
    
    def generate_ranking_report(
        self, recommendations: List[Top3Recommendation]
    ) -> str:
        """Generate formatted ranking report"""
        report = """
╔══════════════════════════════════════════════════════════════════════╗
║                   TOP 3 SUPPLIER RECOMMENDATIONS                     ║
╚══════════════════════════════════════════════════════════════════════╝
"""
        
        for rec in recommendations:
            supplier = rec.supplier
            report += f"""
{'='*74}
RANK #{rec.rank}: {supplier.supplier_name} ({supplier.region})
{'='*74}

📊 OVERALL SCORE: {supplier.total_score}/100

💰 ALLOCATION: {rec.allocation_percentage}% of volume

📈 SCORE BREAKDOWN:
   Quality:         {supplier.quality_score}/100  {'█' * int(supplier.quality_score/10)}
   Cost:            {supplier.cost_score}/100  {'█' * int(supplier.cost_score/10)}
   Delivery:        {supplier.delivery_score}/100  {'█' * int(supplier.delivery_score/10)}
   Capacity:        {supplier.capacity_score}/100  {'█' * int(supplier.capacity_score/10)}
   Sustainability:  {supplier.sustainability_score}/100  {'█' * int(supplier.sustainability_score/10)}
   Certifications:  {supplier.certification_score}/100  {'█' * int(supplier.certification_score/10)}

✅ KEY ADVANTAGES:
"""
            for adv in rec.key_advantages:
                report += f"   • {adv}\n"
            
            report += f"\n⚠️  POTENTIAL CONCERNS:\n"
            for concern in rec.potential_concerns:
                report += f"   • {concern}\n"
            
            report += f"\n🎯 RISK ASSESSMENT: {rec.risk_assessment}\n"
            
            report += f"\n📋 IMPLEMENTATION STEPS:\n"
            for step in rec.implementation_steps:
                report += f"   {step}\n"
            
            report += f"\n💡 REASONING:\n   {supplier.reasoning}\n"
        
        return report


# Example usage
if __name__ == "__main__":
    from backend.engines.data_loader import DataLoader
    
    data_loader = DataLoader()
    ranking_system = EnhancedSupplierRanking(data_loader)
    
    print("="*80)
    print("ENHANCED SUPPLIER RANKING SYSTEM DEMO")
    print("="*80)
    
    # Rank suppliers in India and Thailand
    print("\n📊 Ranking suppliers in India and Thailand for Rice Bran Oil...")
    
    supplier_scores = ranking_system.rank_suppliers_in_regions(
        regions=['APAC'],  # Using APAC as example
        category='Rice Bran Oil',
        client_id='C001',
        top_n=10
    )
    
    print(f"\n✅ Found {len(supplier_scores)} qualified suppliers")
    
    if supplier_scores:
        # Select top 3
        top_3 = ranking_system.select_top_3_with_reasoning(
            supplier_scores=supplier_scores,
            total_volume=1000000,
            category='Rice Bran Oil'
        )
        
        # Generate report
        report = ranking_system.generate_ranking_report(top_3)
        print(report)
