"""
Scenario Detector
Identifies procurement scenarios based on spend patterns and rule violations
"""

from typing import Dict, List, Any
from enum import Enum
import pandas as pd

# Handle imports for both module and standalone execution
try:
    from .rule_engine import RuleEngine, RuleResult, RiskLevel
    from .data_loader import DataLoader
except ImportError:
    from rule_engine import RuleEngine, RuleResult, RiskLevel
    from data_loader import DataLoader


class ScenarioType(Enum):
    """Types of procurement scenarios"""
    HIGH_CONCENTRATION = "HIGH_CONCENTRATION"  # Rice Bran Oil scenario
    WELL_DISTRIBUTED = "WELL_DISTRIBUTED"      # Olive Oil scenario
    TAIL_FRAGMENTATION = "TAIL_FRAGMENTATION"  # Too many small suppliers
    BALANCED = "BALANCED"                       # Optimal state


class Scenario:
    """Represents a detected procurement scenario"""
    
    def __init__(
        self,
        scenario_type: ScenarioType,
        category: str,
        risk_level: RiskLevel,
        triggered_rules: List[RuleResult],
        details: Dict[str, Any]
    ):
        self.scenario_type = scenario_type
        self.category = category
        self.risk_level = risk_level
        self.triggered_rules = triggered_rules
        self.details = details

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "scenario_type": self.scenario_type.value,
            "category": self.category,
            "risk_level": self.risk_level.value,
            "triggered_rules": [r.to_dict() for r in self.triggered_rules],
            "details": self.details
        }


class ScenarioDetector:
    """
    Detects procurement scenarios based on spend patterns and rule violations
    Maps to Branch 3: Sample Data Scenarios
    """

    def __init__(self):
        self.rule_engine = RuleEngine()
        self.data_loader = DataLoader()

    def detect_scenario(
        self,
        category: str = "Rice Bran Oil",
        spend_data: pd.DataFrame = None
    ) -> Scenario:
        """
        Detect the procurement scenario for a given category
        
        Args:
            category: Product category to analyze
            spend_data: Optional spend data (if None, loads from data loader)
            
        Returns:
            Scenario object with detected pattern
        """
        # Load data if not provided
        if spend_data is None:
            spend_data = self.data_loader.load_spend_data()
        
        # Filter by category if specified
        if category:
            spend_data = spend_data[spend_data['Category'] == category]
        
        # Evaluate rules
        rule_results = self.rule_engine.evaluate_all_rules(spend_data)
        triggered_rules = self.rule_engine.get_triggered_rules(rule_results)
        
        # Determine scenario type
        scenario_type, risk_level, details = self._classify_scenario(
            rule_results,
            triggered_rules,
            spend_data
        )
        
        return Scenario(
            scenario_type=scenario_type,
            category=category,
            risk_level=risk_level,
            triggered_rules=triggered_rules,
            details=details
        )

    def _classify_scenario(
        self,
        rule_results: List[RuleResult],
        triggered_rules: List[RuleResult],
        spend_data: pd.DataFrame
    ) -> tuple:
        """
        Classify the scenario based on rule results
        
        Returns:
            Tuple of (scenario_type, risk_level, details)
        """
        # Get rule results by ID
        r001 = next((r for r in rule_results if r.rule_id == "R001"), None)
        r002 = next((r for r in rule_results if r.rule_id == "R002"), None)
        
        # Calculate additional metrics
        total_spend = spend_data['Spend_USD'].sum()
        regional_spend = spend_data.groupby('Supplier_Region')['Spend_USD'].sum()
        max_region = regional_spend.idxmax()
        max_concentration = (regional_spend.max() / total_spend * 100)
        
        # Scenario 1: HIGH CONCENTRATION (Rice Bran Oil pattern)
        if r001 and r001.triggered and r001.actual_value > 70:
            return (
                ScenarioType.HIGH_CONCENTRATION,
                RiskLevel.HIGH,
                {
                    "pattern": "Rice Bran Oil Scenario",
                    "description": f"{max_concentration:.1f}% spend concentrated in {max_region}",
                    "concentration_region": max_region,
                    "concentration_pct": round(max_concentration, 2),
                    "fragile_supply_chain": True,
                    "primary_concern": "Geographic concentration risk",
                    "recommended_strategy": "Risk Reduction"
                }
            )
        
        # Scenario 2: MODERATE CONCENTRATION
        elif r001 and r001.triggered:
            return (
                ScenarioType.HIGH_CONCENTRATION,
                RiskLevel.MEDIUM,
                {
                    "pattern": "Moderate Concentration",
                    "description": f"{max_concentration:.1f}% spend in {max_region} (above 40% threshold)",
                    "concentration_region": max_region,
                    "concentration_pct": round(max_concentration, 2),
                    "fragile_supply_chain": False,
                    "primary_concern": "Regional concentration",
                    "recommended_strategy": "Risk Reduction"
                }
            )
        
        # Scenario 3: TAIL FRAGMENTATION (only tail spend issue)
        elif r002 and r002.triggered and not (r001 and r001.triggered):
            return (
                ScenarioType.TAIL_FRAGMENTATION,
                RiskLevel.MEDIUM,
                {
                    "pattern": "Tail Spend Fragmentation",
                    "description": f"Too many suppliers ({r002.details['tail_supplier_count']}) in bottom 20% spend",
                    "tail_supplier_count": r002.details['tail_supplier_count'],
                    "consolidation_opportunity": True,
                    "primary_concern": "Supplier fragmentation",
                    "recommended_strategy": "Cost Optimization"
                }
            )
        
        # Scenario 4: WELL DISTRIBUTED (Olive Oil pattern)
        elif not any(r.triggered for r in rule_results):
            return (
                ScenarioType.WELL_DISTRIBUTED,
                RiskLevel.LOW,
                {
                    "pattern": "Olive Oil Scenario",
                    "description": "Spend well distributed across regions",
                    "concentration_region": max_region,
                    "concentration_pct": round(max_concentration, 2),
                    "fragile_supply_chain": False,
                    "primary_concern": "Cost optimization",
                    "recommended_strategy": "Cost Optimization"
                }
            )
        
        # Scenario 5: BALANCED (multiple minor issues)
        else:
            return (
                ScenarioType.BALANCED,
                RiskLevel.LOW,
                {
                    "pattern": "Balanced Portfolio",
                    "description": "Minor optimization opportunities",
                    "primary_concern": "Continuous improvement",
                    "recommended_strategy": "Supplier Selection"
                }
            )

    def get_scenario_description(self, scenario: Scenario) -> str:
        """
        Get human-readable description of the scenario
        
        Args:
            scenario: Detected scenario
            
        Returns:
            Formatted description string
        """
        lines = []
        lines.append(f"📊 SCENARIO: {scenario.details['pattern']}")
        lines.append(f"Category: {scenario.category}")
        lines.append(f"Risk Level: {scenario.risk_level.value}")
        lines.append(f"\nDescription: {scenario.details['description']}")
        
        if scenario.triggered_rules:
            lines.append(f"\n⚠️ Triggered Rules:")
            for rule in scenario.triggered_rules:
                lines.append(f"  - {rule.rule_id}: {rule.rule_name}")
                lines.append(f"    Actual: {rule.actual_value:.2f} | Threshold: {rule.threshold_value}")
        
        lines.append(f"\n🎯 Primary Concern: {scenario.details['primary_concern']}")
        lines.append(f"📋 Recommended Strategy: {scenario.details['recommended_strategy']}")
        
        return "\n".join(lines)


# Example usage
if __name__ == "__main__":
    # Initialize detector
    detector = ScenarioDetector()
    
    print("=" * 80)
    print("SCENARIO DETECTION TEST")
    print("=" * 80)
    
    # Detect scenario for Rice Bran Oil
    scenario = detector.detect_scenario("Rice Bran Oil")
    
    print("\n" + detector.get_scenario_description(scenario))
    
    print("\n" + "=" * 80)
    print("DETAILED SCENARIO DATA")
    print("=" * 80)
    
    import json
    print(json.dumps(scenario.to_dict(), indent=2))
