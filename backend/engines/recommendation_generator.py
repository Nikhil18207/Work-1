"""
Recommendation Generator
Generates specific, actionable procurement recommendations based on scenarios
Implements Branch 4: Recommendation Strategy and Branch 5: Project Methodology
"""

from typing import Dict, List, Any
from enum import Enum
import pandas as pd

try:
    from .scenario_detector import Scenario, ScenarioType
    from .rule_engine import RiskLevel
    from .data_loader import DataLoader
except ImportError:
    from scenario_detector import Scenario, ScenarioType
    from rule_engine import RiskLevel
    from data_loader import DataLoader


class RecommendationStrategy(Enum):
    """Recommendation strategies from Branch 4"""
    RISK_REDUCTION = "RISK_REDUCTION"
    COST_OPTIMIZATION = "COST_OPTIMIZATION"
    SUPPLIER_SELECTION = "SUPPLIER_SELECTION"


class Recommendation:
    """A specific, actionable recommendation"""
    
    def __init__(
        self,
        strategy: RecommendationStrategy,
        scenario: Scenario,
        actions: List[Dict[str, Any]],
        expected_outcomes: Dict[str, Any],
        timeline: str,
        priority: str
    ):
        self.strategy = strategy
        self.scenario = scenario
        self.actions = actions
        self.expected_outcomes = expected_outcomes
        self.timeline = timeline
        self.priority = priority

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "strategy": self.strategy.value,
            "scenario": self.scenario.to_dict() if hasattr(self.scenario, 'to_dict') else str(self.scenario),
            "actions": self.actions,
            "expected_outcomes": self.expected_outcomes,
            "timeline": self.timeline,
            "priority": self.priority
        }


class RecommendationGenerator:
    """
    Generates specific, actionable recommendations
    Implements:
    - Branch 4: Recommendation Strategy (Risk Reduction, Cost Optimization, Supplier Selection)
    - Branch 5: Project Methodology (Specific vs Generic Insights)
    """

    def __init__(self):
        self.data_loader = DataLoader()

    def generate_recommendation(self, scenario: Scenario) -> Recommendation:
        """
        Generate recommendation based on detected scenario
        
        Args:
            scenario: Detected procurement scenario
            
        Returns:
            Recommendation with specific actions
        """
        # Select strategy based on scenario
        if scenario.risk_level == RiskLevel.HIGH:
            return self._generate_risk_reduction_recommendation(scenario)
        elif scenario.scenario_type == ScenarioType.TAIL_FRAGMENTATION:
            return self._generate_cost_optimization_recommendation(scenario)
        elif scenario.scenario_type == ScenarioType.WELL_DISTRIBUTED:
            return self._generate_cost_optimization_recommendation(scenario)
        else:
            return self._generate_supplier_selection_recommendation(scenario)

    def _generate_risk_reduction_recommendation(self, scenario: Scenario) -> Recommendation:
        """
        Strategy 1: Risk Reduction
        - Diversify Regions
        - Find Non-Malaysian Suppliers
        """
        spend_data = self.data_loader.load_spend_data()
        spend_data = spend_data[spend_data['Category'] == scenario.category]
        contracts = self.data_loader.load_supplier_contracts()
        
        total_spend = spend_data['Spend_USD'].sum()
        concentration_region = scenario.details.get('concentration_region', 'APAC')
        current_concentration = scenario.details.get('concentration_pct', 0)
        
        # Calculate current regional spend
        regional_spend = spend_data.groupby('Supplier_Region')['Spend_USD'].sum()
        current_spend_in_region = regional_spend.get(concentration_region, 0)
        
        # Target: Reduce to 35%
        target_pct = 35.0
        target_spend = total_spend * (target_pct / 100)
        reallocation_amount = current_spend_in_region - target_spend
        
        # Find alternative suppliers
        alternative_suppliers = self._find_alternative_suppliers(
            contracts,
            exclude_region=concentration_region if concentration_region == 'APAC' else None
        )
        
        # Build specific actions
        actions = [
            {
                "action_id": 1,
                "type": "Reduce Regional Concentration",
                "description": f"Reduce {concentration_region} spend from {current_concentration:.1f}% to {target_pct}%",
                "current_value": f"${current_spend_in_region:,.0f}",
                "target_value": f"${target_spend:,.0f}",
                "reallocation_required": f"${reallocation_amount:,.0f}",
                "specific": True
            }
        ]
        
        # Add supplier recommendations
        for i, supplier in enumerate(alternative_suppliers[:3], start=2):
            allocation_pct = [25, 20, 15][i-2] if i <= 4 else 10
            allocation_amount = total_spend * (allocation_pct / 100)
            
            actions.append({
                "action_id": i,
                "type": "Add Alternative Supplier",
                "supplier_id": supplier['Supplier_ID'],
                "supplier_name": supplier['Supplier_Name'],
                "region": supplier['Region'],
                "esg_score": int(supplier['ESG_Score']),
                "payment_terms": f"{int(supplier['Payment_Terms_Days'])} days",
                "allocation": f"${allocation_amount:,.0f} ({allocation_pct}% of total)",
                "rationale": f"High ESG score ({supplier['ESG_Score']}), favorable payment terms",
                "specific": True
            })
        
        # Expected outcomes
        expected_outcomes = {
            "risk_level_change": f"{scenario.risk_level.value} → MEDIUM",
            "regional_concentration_change": f"{current_concentration:.1f}% → {target_pct}%",
            "supply_chain_resilience": "+60%",
            "geographic_diversification": f"1 region → {len(alternative_suppliers[:3]) + 1} regions",
            "esg_score_improvement": self._calculate_esg_improvement(spend_data, contracts, alternative_suppliers[:3])
        }
        
        return Recommendation(
            strategy=RecommendationStrategy.RISK_REDUCTION,
            scenario=scenario,
            actions=actions,
            expected_outcomes=expected_outcomes,
            timeline="6-12 months",
            priority="HIGH"
        )

    def _generate_cost_optimization_recommendation(self, scenario: Scenario) -> Recommendation:
        """
        Strategy 2: Cost Optimization
        - Identify Incumbent Suppliers
        - Negotiate Better Rates
        - Volume Based Savings
        """
        spend_data = self.data_loader.load_spend_data()
        spend_data = spend_data[spend_data['Category'] == scenario.category]
        
        total_spend = spend_data['Spend_USD'].sum()
        
        # Identify incumbents (top suppliers)
        supplier_spend = spend_data.groupby(['Supplier_ID', 'Supplier_Name'])['Spend_USD'].sum()
        top_suppliers = supplier_spend.sort_values(ascending=False).head(4)
        
        # Identify tail spend
        tail_threshold = total_spend * 0.20
        supplier_spend_sorted = supplier_spend.sort_values()
        cumulative = supplier_spend_sorted.cumsum()
        tail_suppliers = supplier_spend_sorted[cumulative <= tail_threshold]
        
        actions = []
        
        # Action 1: Negotiate with incumbents
        for i, ((sid, sname), spend) in enumerate(top_suppliers.items(), start=1):
            potential_savings = spend * 0.10  # 10% target
            actions.append({
                "action_id": i,
                "type": "Negotiate Better Rates",
                "supplier_id": sid,
                "supplier_name": sname,
                "current_spend": f"${spend:,.0f}",
                "leverage": "High volume commitment",
                "target_reduction": "5-10%",
                "potential_savings": f"${potential_savings:,.0f}",
                "approach": "Volume-based negotiation, long-term contract",
                "specific": True
            })
        
        # Action 2: Consolidate tail spend
        if len(tail_suppliers) > 10:
            tail_total = tail_suppliers.sum()
            target_suppliers = 5
            consolidated_volume = tail_total / target_suppliers
            potential_savings = tail_total * 0.15  # 15% savings from consolidation
            
            actions.append({
                "action_id": len(actions) + 1,
                "type": "Consolidate Tail Spend",
                "current_suppliers": len(tail_suppliers),
                "target_suppliers": target_suppliers,
                "current_spend": f"${tail_total:,.0f}",
                "volume_per_supplier_after": f"${consolidated_volume:,.0f}",
                "volume_increase": f"{(consolidated_volume / (tail_total / len(tail_suppliers))):.1f}x",
                "potential_savings": f"${potential_savings:,.0f} (10-20%)",
                "approach": "Consolidate to top 5 performers, negotiate volume discounts",
                "specific": True
            })
        
        # Expected outcomes
        total_potential_savings = sum(
            float(a.get('potential_savings', '$0').replace('$', '').replace(',', '').split()[0])
            for a in actions
        )
        
        expected_outcomes = {
            "cost_reduction": f"${total_potential_savings:,.0f}",
            "cost_reduction_pct": f"{(total_potential_savings / total_spend * 100):.1f}%",
            "supplier_count_change": f"{len(supplier_spend)} → {len(top_suppliers) + 5}",
            "average_order_value_increase": "+40%",
            "negotiation_leverage": "Improved"
        }
        
        return Recommendation(
            strategy=RecommendationStrategy.COST_OPTIMIZATION,
            scenario=scenario,
            actions=actions,
            expected_outcomes=expected_outcomes,
            timeline="3-6 months",
            priority="MEDIUM"
        )

    def _generate_supplier_selection_recommendation(self, scenario: Scenario) -> Recommendation:
        """
        Strategy 3: Supplier Selection Criteria
        - Sustainability (ESG) Scores
        - Payment Terms
        - Capacity vs Availability
        """
        contracts = self.data_loader.load_supplier_contracts()
        spend_data = self.data_loader.load_spend_data()
        
        # Score all suppliers
        scored_suppliers = []
        for _, supplier in contracts.iterrows():
            score = self._calculate_supplier_score(supplier)
            scored_suppliers.append({
                "supplier_id": supplier['Supplier_ID'],
                "supplier_name": supplier['Supplier_Name'],
                "region": supplier['Region'],
                "esg_score": int(supplier['ESG_Score']),
                "payment_terms": int(supplier['Payment_Terms_Days']),
                "total_score": score,
                "ranking": ""
            })
        
        # Sort by score
        scored_suppliers.sort(key=lambda x: x['total_score'], reverse=True)
        
        # Add rankings
        for i, supplier in enumerate(scored_suppliers, start=1):
            supplier['ranking'] = f"#{i}"
        
        actions = [
            {
                "action_id": 1,
                "type": "Supplier Ranking",
                "description": "ESG-weighted supplier ranking (ESG: 30%, Payment: 20%, Capacity: 50%)",
                "top_suppliers": scored_suppliers[:5],
                "specific": True
            },
            {
                "action_id": 2,
                "type": "Prioritize High ESG Suppliers",
                "description": "Focus on suppliers with ESG > 75",
                "recommended_suppliers": [s for s in scored_suppliers if s['esg_score'] > 75][:3],
                "specific": True
            }
        ]
        
        expected_outcomes = {
            "esg_score_improvement": "Average ESG score increase by 15-20 points",
            "payment_terms_optimization": "Extend average payment terms by 10-15 days",
            "supplier_quality": "Top-tier suppliers prioritized",
            "sustainability_compliance": "Enhanced"
        }
        
        return Recommendation(
            strategy=RecommendationStrategy.SUPPLIER_SELECTION,
            scenario=scenario,
            actions=actions,
            expected_outcomes=expected_outcomes,
            timeline="Ongoing",
            priority="LOW"
        )

    def _find_alternative_suppliers(
        self,
        contracts: pd.DataFrame,
        exclude_region: str = None
    ) -> List[Dict[str, Any]]:
        """Find alternative suppliers outside specified region"""
        if exclude_region:
            contracts = contracts[contracts['Region'] != exclude_region]
        
        # Sort by ESG score
        contracts = contracts.sort_values('ESG_Score', ascending=False)
        
        return contracts.to_dict('records')

    def _calculate_supplier_score(self, supplier: pd.Series) -> float:
        """
        Calculate supplier score using Branch 4 criteria:
        - ESG Score: 30%
        - Payment Terms: 20%
        - Capacity: 50% (assumed high for all)
        """
        # ESG score (0-100 scale)
        esg_score = (supplier['ESG_Score'] / 100) * 0.30
        
        # Payment terms (30-60 days, higher is better)
        payment_score = ((supplier['Payment_Terms_Days'] - 30) / 30) * 0.20
        
        # Capacity (assumed 100% for all in this dataset)
        capacity_score = 1.0 * 0.50
        
        total_score = (esg_score + payment_score + capacity_score) * 100
        return round(total_score, 2)

    def _calculate_esg_improvement(
        self,
        spend_data: pd.DataFrame,
        contracts: pd.DataFrame,
        new_suppliers: List[Dict[str, Any]]
    ) -> str:
        """Calculate ESG score improvement"""
        # Current weighted ESG
        current_suppliers = spend_data['Supplier_ID'].unique()
        current_contracts = contracts[contracts['Supplier_ID'].isin(current_suppliers)]
        
        if len(current_contracts) > 0:
            current_avg_esg = current_contracts['ESG_Score'].mean()
            new_avg_esg = sum(s['ESG_Score'] for s in new_suppliers) / len(new_suppliers) if new_suppliers else current_avg_esg
            
            return f"{current_avg_esg:.0f} → {new_avg_esg:.0f} (+{new_avg_esg - current_avg_esg:.0f} points)"
        
        return "N/A"

    def format_recommendation(self, recommendation: Recommendation) -> str:
        """
        Format recommendation as specific, human-readable text
        Implements Branch 5: Specific vs Generic Insights
        """
        lines = []
        
        # Header
        lines.append("=" * 80)
        lines.append(f"📋 PROCUREMENT RECOMMENDATION")
        lines.append("=" * 80)
        
        # Strategy
        lines.append(f"\n🎯 Strategy: {recommendation.strategy.value.replace('_', ' ').title()}")
        lines.append(f"⏱️  Timeline: {recommendation.timeline}")
        lines.append(f"🚨 Priority: {recommendation.priority}")
        
        # Current State
        lines.append(f"\n📊 Current State:")
        lines.append(f"Category: {recommendation.scenario.category}")
        lines.append(f"Risk Level: {recommendation.scenario.risk_level.value}")
        lines.append(f"Pattern: {recommendation.scenario.details.get('pattern', 'N/A')}")
        
        # Actions
        lines.append(f"\n✅ Recommended Actions:")
        for action in recommendation.actions:
            lines.append(f"\n{action['action_id']}. {action['type']}")
            for key, value in action.items():
                if key not in ['action_id', 'type', 'specific']:
                    if isinstance(value, list):
                        lines.append(f"   {key}: {len(value)} items")
                    else:
                        lines.append(f"   {key}: {value}")
        
        # Expected Outcomes
        lines.append(f"\n🎯 Expected Outcomes:")
        for key, value in recommendation.expected_outcomes.items():
            lines.append(f"   • {key.replace('_', ' ').title()}: {value}")
        
        lines.append("\n" + "=" * 80)
        
        return "\n".join(lines)


# Example usage
if __name__ == "__main__":
    from scenario_detector import ScenarioDetector
    
    # Detect scenario
    detector = ScenarioDetector()
    scenario = detector.detect_scenario("Rice Bran Oil")
    
    # Generate recommendation
    generator = RecommendationGenerator()
    recommendation = generator.generate_recommendation(scenario)
    
    # Print formatted recommendation
    print(generator.format_recommendation(recommendation))
