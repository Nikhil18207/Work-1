"""
Enhanced Rule Book Policy Engine
Dynamically loads ALL rules from CSV file (35+ rules)
Implements quantified business rules for procurement recommendations
"""

from typing import Dict, List, Any
from enum import Enum
import pandas as pd
import os


class RiskLevel(Enum):
    """Risk severity levels"""
    CRITICAL = "CRITICAL"
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
        category: str = "General",
        details: Dict[str, Any] = None
    ):
        self.rule_id = rule_id
        self.rule_name = rule_name
        self.triggered = triggered
        self.risk_level = risk_level
        self.actual_value = actual_value
        self.threshold_value = threshold_value
        self.action_recommendation = action_recommendation
        self.category = category
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
            "category": self.category,
            "details": self.details
        }


class EnhancedRuleEngine:
    """
    Enhanced Rule Book Policy Engine
    Dynamically loads ALL rules from CSV file
    Supports 35+ procurement rules across all categories
    """

    def __init__(self):
        self.rules = self._load_rules_from_csv()
        print(f"✅ Rule Engine initialized with {len(self.rules)} rules")

    def _load_rules_from_csv(self) -> Dict[str, Dict[str, Any]]:
        """
        Load ALL rule definitions from CSV file
        Supports 35+ rules dynamically
        """
        # Get path to rule_book.csv
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        rule_file = os.path.join(base_dir, 'data', 'structured', 'rule_book.csv')
        
        try:
            rules_df = pd.read_csv(rule_file)
            rules_dict = {}
            
            for _, row in rules_df.iterrows():
                rule_id = row['Rule_ID']
                
                # Parse threshold value
                threshold = self._parse_threshold(str(row['Threshold_Value']))
                
                # Map risk level
                risk_level = self._parse_risk_level(row['Risk_Level'])
                
                rules_dict[rule_id] = {
                    "name": row['Rule_Name'],
                    "description": row['Rule_Description'],
                    "threshold": threshold,
                    "risk_level": risk_level,
                    "action": row['Action_Recommendation'],
                    "category": row.get('Category', 'General')
                }
            
            return rules_dict
            
        except Exception as e:
            print(f"⚠️ Error loading rules from CSV: {e}")
            return self._get_fallback_rules()

    def _parse_threshold(self, threshold_str: str) -> float:
        """Parse threshold value from string"""
        threshold_str = threshold_str.strip()
        
        # Remove % if present
        if '%' in threshold_str:
            return float(threshold_str.replace('%', ''))
        
        # Extract number from strings like "45 days", "6 months", "10 suppliers"
        if any(unit in threshold_str.lower() for unit in ['days', 'months', 'hours', 'suppliers', 'years']):
            numbers = ''.join(filter(str.isdigit, threshold_str.split()[0]))
            return float(numbers) if numbers else 0.0
        
        # Try direct conversion
        try:
            return float(threshold_str)
        except:
            return 0.0

    def _parse_risk_level(self, risk_str: str) -> RiskLevel:
        """Parse risk level from string"""
        risk_str = risk_str.upper().strip()
        
        if risk_str in ['HIGH', 'CRITICAL']:
            return RiskLevel.HIGH
        elif risk_str == 'MEDIUM':
            return RiskLevel.MEDIUM
        else:
            return RiskLevel.LOW

    def _get_fallback_rules(self) -> Dict[str, Dict[str, Any]]:
        """Fallback rules if CSV load fails"""
        return {
            "R001": {
                "name": "Regional Concentration",
                "description": "If >40% of category spend is concentrated in a single region",
                "threshold": 40.0,
                "risk_level": RiskLevel.HIGH,
                "action": "Diversify suppliers across additional regions",
                "category": "Geographic Risk"
            },
            "R002": {
                "name": "Tail Spend Fragmentation",
                "description": "If bottom 20% of spend is distributed across too many suppliers",
                "threshold": 10,
                "risk_level": RiskLevel.MEDIUM,
                "action": "Consolidate tail suppliers or renegotiate contracts",
                "category": "Spend Optimization"
            }
        }

    def evaluate_all_rules(self, spend_data: pd.DataFrame) -> List[RuleResult]:
        """
        Evaluate all applicable rules against spend data
        Currently implements R001 and R002 (can be extended for all 35 rules)
        """
        results = []
        
        # R001: Regional Concentration
        if "R001" in self.rules:
            r001_result = self.evaluate_regional_concentration(spend_data)
            results.append(r001_result)
        
        # R002: Tail Spend Fragmentation
        if "R002" in self.rules:
            r002_result = self.evaluate_tail_spend_fragmentation(spend_data)
            results.append(r002_result)
        
        # TODO: Add evaluation methods for other rules (R003-R035)
        # This is extensible - add new evaluation methods as needed
        
        return results

    def evaluate_regional_concentration(self, spend_data: pd.DataFrame) -> RuleResult:
        """R001: Regional Concentration Rule"""
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
            category=rule["category"],
            details=details
        )

    def evaluate_tail_spend_fragmentation(self, spend_data: pd.DataFrame) -> RuleResult:
        """R002: Tail Spend Fragmentation Rule"""
        rule = self.rules["R002"]
        
        # Calculate total spend
        total_spend = spend_data['Spend_USD'].sum()
        tail_threshold = total_spend * 0.20
        
        # Aggregate by supplier
        supplier_spend = spend_data.groupby('Supplier_ID')['Spend_USD'].sum().sort_values()
        
        # Identify tail suppliers
        cumulative_spend = supplier_spend.cumsum()
        tail_suppliers = supplier_spend[cumulative_spend <= tail_threshold]
        
        if len(tail_suppliers) == 0:
            num_tail_suppliers = max(1, int(len(supplier_spend) * 0.20))
            tail_suppliers = supplier_spend.head(num_tail_suppliers)
        
        tail_supplier_count = len(tail_suppliers)
        tail_spend_total = tail_suppliers.sum()
        tail_spend_pct = (tail_spend_total / total_spend * 100)
        supplier_density_ratio = tail_supplier_count / 20
        
        # Check threshold
        triggered = supplier_density_ratio > rule["threshold"]
        
        # Build details
        details = {
            "tail_supplier_count": tail_supplier_count,
            "tail_spend_total": float(tail_spend_total),
            "tail_spend_pct": round(tail_spend_pct, 2),
            "supplier_density_ratio": round(supplier_density_ratio, 2),
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
            category=rule["category"],
            details=details
        )

    def get_triggered_rules(self, results: List[RuleResult]) -> List[RuleResult]:
        """Filter to only triggered rules"""
        return [r for r in results if r.triggered]

    def get_highest_risk(self, results: List[RuleResult]) -> RuleResult:
        """Get the highest risk rule result"""
        risk_priority = {
            RiskLevel.CRITICAL: 4,
            RiskLevel.HIGH: 3,
            RiskLevel.MEDIUM: 2,
            RiskLevel.LOW: 1
        }
        return max(results, key=lambda r: risk_priority[r.risk_level])

    def get_rules_by_category(self, category: str) -> Dict[str, Dict[str, Any]]:
        """Get all rules in a specific category"""
        return {
            rule_id: rule_data
            for rule_id, rule_data in self.rules.items()
            if rule_data.get("category") == category
        }

    def list_all_rules(self) -> List[Dict[str, Any]]:
        """List all loaded rules"""
        return [
            {
                "rule_id": rule_id,
                **rule_data
            }
            for rule_id, rule_data in self.rules.items()
        ]


# Example usage
if __name__ == "__main__":
    # Initialize enhanced rule engine
    engine = EnhancedRuleEngine()
    
    # Load spend data
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    spend_df = pd.read_csv(os.path.join(base_dir, 'data', 'structured', 'spend_data.csv'))
    
    # Evaluate rules
    results = engine.evaluate_all_rules(spend_df)
    
    # Print results
    print("\n" + "=" * 80)
    print("RULE EVALUATION RESULTS")
    print("=" * 80)
    
    for result in results:
        print(f"\n{result.rule_id}: {result.rule_name} ({result.category})")
        print(f"Triggered: {result.triggered}")
        print(f"Risk Level: {result.risk_level.value}")
        print(f"Actual: {result.actual_value:.2f} | Threshold: {result.threshold_value}")
        print(f"Action: {result.action_recommendation}")
        print("-" * 80)
    
    # List all loaded rules
    print("\n" + "=" * 80)
    print(f"TOTAL RULES LOADED: {len(engine.rules)}")
    print("=" * 80)
    for rule_id, rule_data in engine.rules.items():
        print(f"{rule_id}: {rule_data['name']} ({rule_data['category']})")
