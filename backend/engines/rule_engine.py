"""
Rule Book Policy Engine
Implements quantified business rules for procurement recommendations
"""

from typing import Dict, List, Any
from enum import Enum
import pandas as pd


class RiskLevel(Enum):
    """Risk severity levels"""
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


class RuleResult:
    """Result of a rule evaluation"""
    def __init__(
        self,
        rule_id: str,
        rule_name: str,
        triggered: bool,
        risk_level: RiskLevel,
        actual_value: float,
        threshold_value: float,
        action_recommendation: str,
        details: Dict[str, Any] = None
    ):
        self.rule_id = rule_id
        self.rule_name = rule_name
        self.triggered = triggered
        self.risk_level = risk_level
        self.actual_value = actual_value
        self.threshold_value = threshold_value
        self.action_recommendation = action_recommendation
        self.details = details or {}

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "rule_id": self.rule_id,
            "rule_name": self.rule_name,
            "triggered": self.triggered,
            "risk_level": self.risk_level.value,
            "actual_value": self.actual_value,
            "threshold_value": self.threshold_value,
            "action_recommendation": self.action_recommendation,
            "details": self.details
        }


class RuleEngine:
    """
    Rule Book Policy Engine
    Evaluates quantified business rules against spend data
    """

    def __init__(self):
        self.rules = self._load_rules()

    def _load_rules(self) -> Dict[str, Dict[str, Any]]:
        """Load rule definitions"""
        return {
            "R001": {
                "name": "Regional Concentration",
                "description": "If >40% of category spend is concentrated in a single region",
                "threshold": 40.0,  # percentage
                "risk_level": RiskLevel.HIGH,
                "action": "Diversify suppliers across additional regions"
            },
            "R002": {
                "name": "Tail Spend Fragmentation",
                "description": "If bottom 20% of spend is distributed across too many suppliers",
                "threshold": 10,  # suppliers per low spend bucket
                "risk_level": RiskLevel.MEDIUM,
                "action": "Consolidate tail suppliers or renegotiate contracts"
            }
        }

    def evaluate_all_rules(self, spend_data: pd.DataFrame) -> List[RuleResult]:
        """
        Evaluate all rules against spend data
        
        Args:
            spend_data: DataFrame with columns: Supplier_Region, Spend_USD, Supplier_ID
            
        Returns:
            List of RuleResult objects
        """
        results = []
        
        # R001: Regional Concentration
        r001_result = self.evaluate_regional_concentration(spend_data)
        results.append(r001_result)
        
        # R002: Tail Spend Fragmentation
        r002_result = self.evaluate_tail_spend_fragmentation(spend_data)
        results.append(r002_result)
        
        return results

    def evaluate_regional_concentration(self, spend_data: pd.DataFrame) -> RuleResult:
        """
        R001: Regional Concentration Rule
        
        Checks if >40% of spend is concentrated in a single region
        """
        rule = self.rules["R001"]
        
        # Calculate regional spend distribution
        total_spend = spend_data['Spend_USD'].sum()
        regional_spend = spend_data.groupby('Supplier_Region')['Spend_USD'].sum()
        regional_pct = (regional_spend / total_spend * 100).sort_values(ascending=False)
        
        # Get highest concentration
        max_region = regional_pct.index[0]
        max_concentration = regional_pct.iloc[0]
        
        # Check threshold
        triggered = max_concentration > rule["threshold"]
        
        # Build details
        details = {
            "max_region": max_region,
            "max_concentration_pct": round(max_concentration, 2),
            "regional_distribution": {
                region: round(pct, 2) 
                for region, pct in regional_pct.items()
            },
            "total_spend": float(total_spend)
        }
        
        return RuleResult(
            rule_id="R001",
            rule_name=rule["name"],
            triggered=triggered,
            risk_level=rule["risk_level"] if triggered else RiskLevel.LOW,
            actual_value=max_concentration,
            threshold_value=rule["threshold"],
            action_recommendation=rule["action"] if triggered else "Maintain current regional distribution",
            details=details
        )

    def evaluate_tail_spend_fragmentation(self, spend_data: pd.DataFrame) -> RuleResult:
        """
        R002: Tail Spend Fragmentation Rule
        
        Checks if bottom 20% of spend has too many suppliers (>10)
        """
        rule = self.rules["R002"]
        
        # Calculate total spend
        total_spend = spend_data['Spend_USD'].sum()
        tail_threshold = total_spend * 0.20  # Bottom 20%
        
        # Aggregate by supplier
        supplier_spend = spend_data.groupby('Supplier_ID')['Spend_USD'].sum().sort_values()
        
        # Identify tail suppliers (cumulative sum approach)
        cumulative_spend = supplier_spend.cumsum()
        tail_suppliers = supplier_spend[cumulative_spend <= tail_threshold]
        
        # If no suppliers in exact bottom 20%, take lowest spending suppliers
        if len(tail_suppliers) == 0:
            num_tail_suppliers = max(1, int(len(supplier_spend) * 0.20))
            tail_suppliers = supplier_spend.head(num_tail_suppliers)
        
        tail_supplier_count = len(tail_suppliers)
        tail_spend_total = tail_suppliers.sum()
        tail_spend_pct = (tail_spend_total / total_spend * 100)
        
        # Calculate density ratio
        supplier_density_ratio = tail_supplier_count / 20  # per 20% bucket
        
        # Check threshold
        triggered = supplier_density_ratio > rule["threshold"]
        
        # Build details
        details = {
            "tail_supplier_count": tail_supplier_count,
            "tail_spend_total": float(tail_spend_total),
            "tail_spend_pct": round(tail_spend_pct, 2),
            "supplier_density_ratio": round(supplier_density_ratio, 2),
            "tail_suppliers": tail_suppliers.to_dict(),
            "consolidation_opportunity": tail_supplier_count > 10
        }
        
        return RuleResult(
            rule_id="R002",
            rule_name=rule["name"],
            triggered=triggered,
            risk_level=rule["risk_level"] if triggered else RiskLevel.LOW,
            actual_value=supplier_density_ratio,
            threshold_value=rule["threshold"],
            action_recommendation=rule["action"] if triggered else "Tail spend is optimized",
            details=details
        )

    def get_triggered_rules(self, results: List[RuleResult]) -> List[RuleResult]:
        """Filter to only triggered rules"""
        return [r for r in results if r.triggered]

    def get_highest_risk(self, results: List[RuleResult]) -> RuleResult:
        """Get the highest risk rule result"""
        risk_priority = {RiskLevel.HIGH: 3, RiskLevel.MEDIUM: 2, RiskLevel.LOW: 1}
        return max(results, key=lambda r: risk_priority[r.risk_level])


# Example usage
if __name__ == "__main__":
    # Test with sample data
    import pandas as pd
    
    # Load spend data
    import os
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    spend_df = pd.read_csv(os.path.join(base_dir, 'data', 'structured', 'spend_data.csv'))
    
    # Initialize rule engine
    engine = RuleEngine()
    
    # Evaluate rules
    results = engine.evaluate_all_rules(spend_df)
    
    # Print results
    print("=" * 80)
    print("RULE EVALUATION RESULTS")
    print("=" * 80)
    
    for result in results:
        print(f"\n{result.rule_id}: {result.rule_name}")
        print(f"Triggered: {result.triggered}")
        print(f"Risk Level: {result.risk_level.value}")
        print(f"Actual: {result.actual_value:.2f} | Threshold: {result.threshold_value}")
        print(f"Action: {result.action_recommendation}")
        print(f"Details: {result.details}")
        print("-" * 80)
