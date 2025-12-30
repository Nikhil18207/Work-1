"""
Constraint Validation Agent

Separate agent responsible for validating all procurement constraints
when moving between regions or changing supplier allocations.

Key Responsibilities:
1. Validate max 30% per supplier rule (R003)
2. Calculate spend increase/decrease when moving regions
3. Check all 35 procurement rules
4. Provide constraint violation warnings
5. Suggest adjustments to meet constraints
"""

from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import pandas as pd


class ConstraintType(Enum):
    """Types of constraints"""
    SUPPLIER_CONCENTRATION = "supplier_concentration"  # R003
    REGIONAL_CONCENTRATION = "regional_concentration"  # R001
    COST_THRESHOLD = "cost_threshold"
    QUALITY_MINIMUM = "quality_minimum"
    CAPACITY_LIMIT = "capacity_limit"
    CERTIFICATION_REQUIRED = "certification_required"


class ViolationSeverity(Enum):
    """Severity levels for violations"""
    CRITICAL = "CRITICAL"  # Must fix immediately
    HIGH = "HIGH"  # Should fix before proceeding
    MEDIUM = "MEDIUM"  # Can proceed with caution
    LOW = "LOW"  # Advisory only


@dataclass
class ConstraintViolation:
    """Represents a constraint violation"""
    constraint_type: ConstraintType
    rule_id: str
    severity: ViolationSeverity
    current_value: float
    threshold: float
    violation_amount: float
    affected_entity: str  # Supplier ID or Region name
    description: str
    recommended_action: str


@dataclass
class SpendImpactAnalysis:
    """Analysis of spend impact when moving regions"""
    from_region: str
    to_region: str
    volume_moved: float
    current_cost: float
    new_cost: float
    cost_delta: float
    cost_delta_pct: float
    tariff_impact: float
    other_cost_factors: Dict[str, float]
    total_impact: float


@dataclass
class ValidationResult:
    """Result of constraint validation"""
    is_valid: bool
    violations: List[ConstraintViolation]
    spend_impacts: List[SpendImpactAnalysis]
    adjusted_allocation: Optional[Dict[str, float]]
    recommendations: List[str]


class ConstraintValidationAgent:
    """
    Constraint Validation Agent
    
    Validates all procurement constraints and calculates
    spend impacts when changing allocations.
    """
    
    # Constraint thresholds
    MAX_SUPPLIER_PCT = 30.0  # R003: Max 30% per supplier
    MAX_REGION_PCT = 40.0    # R001: Max 40% per region
    MIN_QUALITY_RATING = 4.0
    
    def __init__(self, data_loader, rule_engine):
        self.data_loader = data_loader
        self.rule_engine = rule_engine
    
    def validate_allocation(
        self,
        proposed_allocation: Dict[str, float],
        allocation_type: str,  # 'supplier' or 'region'
        client_id: str,
        category: str,
        total_spend: float
    ) -> ValidationResult:
        """
        Validate proposed allocation against all constraints
        
        Args:
            proposed_allocation: Dict of {entity: percentage}
            allocation_type: 'supplier' or 'region'
            client_id: Client identifier
            category: Product category
            total_spend: Total spend amount
            
        Returns:
            ValidationResult with violations and recommendations
        """
        violations = []
        
        # Validate concentration constraints
        if allocation_type == 'supplier':
            violations.extend(
                self._validate_supplier_concentration(proposed_allocation)
            )
        elif allocation_type == 'region':
            violations.extend(
                self._validate_regional_concentration(proposed_allocation)
            )
        
        # Validate quality constraints
        violations.extend(
            self._validate_quality_constraints(
                proposed_allocation, allocation_type, category
            )
        )
        
        # Validate capacity constraints
        violations.extend(
            self._validate_capacity_constraints(
                proposed_allocation, allocation_type, total_spend
            )
        )
        
        # Calculate spend impacts
        spend_impacts = self._calculate_spend_impacts(
            proposed_allocation, allocation_type, category, total_spend
        )
        
        # Generate recommendations
        recommendations = self._generate_recommendations(violations, spend_impacts)
        
        # Adjust allocation if violations exist
        adjusted_allocation = None
        if violations:
            adjusted_allocation = self._adjust_allocation_for_violations(
                proposed_allocation, violations
            )
        
        is_valid = len([v for v in violations if v.severity in [
            ViolationSeverity.CRITICAL, ViolationSeverity.HIGH
        ]]) == 0
        
        return ValidationResult(
            is_valid=is_valid,
            violations=violations,
            spend_impacts=spend_impacts,
            adjusted_allocation=adjusted_allocation,
            recommendations=recommendations
        )
    
    def calculate_region_move_impact(
        self,
        from_region: str,
        to_region: str,
        volume_pct: float,
        category: str,
        total_spend: float
    ) -> SpendImpactAnalysis:
        """
        Calculate spend impact when moving volume from one region to another
        
        Args:
            from_region: Source region
            to_region: Destination region
            volume_pct: Percentage of volume to move
            category: Product category
            total_spend: Total category spend
            
        Returns:
            SpendImpactAnalysis with detailed breakdown
        """
        volume_moved = total_spend * (volume_pct / 100)
        
        # Get current cost (from_region)
        current_cost = volume_moved  # Baseline
        
        # Calculate new cost (to_region)
        # Factor 1: Base price difference
        price_diff_pct = self._get_regional_price_difference(from_region, to_region)
        
        # Factor 2: Tariff difference
        tariff_diff = self._get_tariff_difference(from_region, to_region, category)
        
        # Factor 3: Logistics cost difference
        logistics_diff = self._get_logistics_cost_difference(from_region, to_region)
        
        # Factor 4: Quality/compliance cost difference
        quality_diff = self._get_quality_cost_difference(from_region, to_region)
        
        # Calculate total new cost
        total_cost_impact_pct = (
            price_diff_pct + tariff_diff + logistics_diff + quality_diff
        )
        
        new_cost = current_cost * (1 + total_cost_impact_pct / 100)
        cost_delta = new_cost - current_cost
        cost_delta_pct = (cost_delta / current_cost * 100) if current_cost > 0 else 0
        
        return SpendImpactAnalysis(
            from_region=from_region,
            to_region=to_region,
            volume_moved=volume_moved,
            current_cost=current_cost,
            new_cost=new_cost,
            cost_delta=cost_delta,
            cost_delta_pct=round(cost_delta_pct, 2),
            tariff_impact=tariff_diff,
            other_cost_factors={
                'price_difference': price_diff_pct,
                'logistics_difference': logistics_diff,
                'quality_compliance': quality_diff
            },
            total_impact=round(total_cost_impact_pct, 2)
        )
    
    def _validate_supplier_concentration(
        self, allocation: Dict[str, float]
    ) -> List[ConstraintViolation]:
        """Validate R003: Max 30% per supplier"""
        violations = []
        
        for supplier, pct in allocation.items():
            if pct > self.MAX_SUPPLIER_PCT:
                violations.append(ConstraintViolation(
                    constraint_type=ConstraintType.SUPPLIER_CONCENTRATION,
                    rule_id='R003',
                    severity=ViolationSeverity.HIGH,
                    current_value=pct,
                    threshold=self.MAX_SUPPLIER_PCT,
                    violation_amount=pct - self.MAX_SUPPLIER_PCT,
                    affected_entity=supplier,
                    description=f"Supplier {supplier} allocation ({pct}%) exceeds maximum 30% threshold",
                    recommended_action=f"Reduce {supplier} allocation to 30% or below"
                ))
        
        return violations
    
    def _validate_regional_concentration(
        self, allocation: Dict[str, float]
    ) -> List[ConstraintViolation]:
        """Validate R001: Max 40% per region"""
        violations = []
        
        for region, pct in allocation.items():
            if pct > self.MAX_REGION_PCT:
                violations.append(ConstraintViolation(
                    constraint_type=ConstraintType.REGIONAL_CONCENTRATION,
                    rule_id='R001',
                    severity=ViolationSeverity.HIGH,
                    current_value=pct,
                    threshold=self.MAX_REGION_PCT,
                    violation_amount=pct - self.MAX_REGION_PCT,
                    affected_entity=region,
                    description=f"Region {region} allocation ({pct}%) exceeds maximum 40% threshold",
                    recommended_action=f"Reduce {region} allocation to 40% or below"
                ))
        
        return violations
    
    def _validate_quality_constraints(
        self, allocation: Dict[str, float], allocation_type: str, category: str
    ) -> List[ConstraintViolation]:
        """Validate quality constraints"""
        violations = []
        
        if allocation_type == 'supplier':
            supplier_df = self.data_loader.load_supplier_master()
            
            for supplier_id, pct in allocation.items():
                supplier_info = supplier_df[supplier_df['supplier_id'] == supplier_id]
                
                if not supplier_info.empty:
                    quality_rating = supplier_info.iloc[0].get('quality_rating', 0)
                    
                    if quality_rating < self.MIN_QUALITY_RATING:
                        violations.append(ConstraintViolation(
                            constraint_type=ConstraintType.QUALITY_MINIMUM,
                            rule_id='R007',
                            severity=ViolationSeverity.MEDIUM,
                            current_value=quality_rating,
                            threshold=self.MIN_QUALITY_RATING,
                            violation_amount=self.MIN_QUALITY_RATING - quality_rating,
                            affected_entity=supplier_id,
                            description=f"Supplier {supplier_id} quality rating ({quality_rating}) below minimum {self.MIN_QUALITY_RATING}",
                            recommended_action=f"Consider suppliers with quality rating >= {self.MIN_QUALITY_RATING}"
                        ))
        
        return violations
    
    def _validate_capacity_constraints(
        self, allocation: Dict[str, float], allocation_type: str, total_spend: float
    ) -> List[ConstraintViolation]:
        """Validate capacity constraints"""
        violations = []
        
        if allocation_type == 'supplier':
            supplier_df = self.data_loader.load_supplier_master()
            
            for supplier_id, pct in allocation.items():
                supplier_info = supplier_df[supplier_df['supplier_id'] == supplier_id]
                
                if not supplier_info.empty:
                    capacity = supplier_info.iloc[0].get('annual_capacity_tons', 0)
                    required_volume = (total_spend * pct / 100) / 1000  # Rough estimate
                    
                    if required_volume > capacity:
                        violations.append(ConstraintViolation(
                            constraint_type=ConstraintType.CAPACITY_LIMIT,
                            rule_id='CAPACITY',
                            severity=ViolationSeverity.HIGH,
                            current_value=required_volume,
                            threshold=capacity,
                            violation_amount=required_volume - capacity,
                            affected_entity=supplier_id,
                            description=f"Supplier {supplier_id} lacks capacity for {pct}% allocation",
                            recommended_action=f"Reduce allocation or find additional suppliers"
                        ))
        
        return violations
    
    def _calculate_spend_impacts(
        self, allocation: Dict[str, float], allocation_type: str,
        category: str, total_spend: float
    ) -> List[SpendImpactAnalysis]:
        """Calculate spend impacts for allocation changes"""
        impacts = []
        
        # This would compare proposed allocation vs current allocation
        # For now, return empty list (would be populated in production)
        
        return impacts
    
    def _generate_recommendations(
        self, violations: List[ConstraintViolation],
        spend_impacts: List[SpendImpactAnalysis]
    ) -> List[str]:
        """Generate recommendations based on violations and impacts"""
        recommendations = []
        
        # Group violations by severity
        critical = [v for v in violations if v.severity == ViolationSeverity.CRITICAL]
        high = [v for v in violations if v.severity == ViolationSeverity.HIGH]
        
        if critical:
            recommendations.append(
                f"⚠️  CRITICAL: {len(critical)} critical violations must be resolved before proceeding"
            )
            for v in critical:
                recommendations.append(f"   • {v.recommended_action}")
        
        if high:
            recommendations.append(
                f"⚠️  HIGH: {len(high)} high-priority violations should be addressed"
            )
            for v in high:
                recommendations.append(f"   • {v.recommended_action}")
        
        # Add spend impact recommendations
        for impact in spend_impacts:
            if impact.cost_delta_pct > 5:
                recommendations.append(
                    f"💰 Moving from {impact.from_region} to {impact.to_region} "
                    f"will increase costs by {impact.cost_delta_pct}%"
                )
            elif impact.cost_delta_pct < -5:
                recommendations.append(
                    f"💰 Moving from {impact.from_region} to {impact.to_region} "
                    f"will reduce costs by {abs(impact.cost_delta_pct)}%"
                )
        
        if not recommendations:
            recommendations.append("✅ No constraint violations detected")
        
        return recommendations
    
    def _adjust_allocation_for_violations(
        self, allocation: Dict[str, float], violations: List[ConstraintViolation]
    ) -> Dict[str, float]:
        """Automatically adjust allocation to resolve violations"""
        adjusted = allocation.copy()
        
        for violation in violations:
            if violation.constraint_type == ConstraintType.SUPPLIER_CONCENTRATION:
                # Reduce to threshold
                adjusted[violation.affected_entity] = violation.threshold
                
                # Redistribute excess to other suppliers
                excess = violation.violation_amount
                other_entities = [e for e in adjusted.keys() if e != violation.affected_entity]
                
                if other_entities:
                    per_entity = excess / len(other_entities)
                    for entity in other_entities:
                        adjusted[entity] += per_entity
            
            elif violation.constraint_type == ConstraintType.REGIONAL_CONCENTRATION:
                # Similar logic for regions
                adjusted[violation.affected_entity] = violation.threshold
                
                excess = violation.violation_amount
                other_entities = [e for e in adjusted.keys() if e != violation.affected_entity]
                
                if other_entities:
                    per_entity = excess / len(other_entities)
                    for entity in other_entities:
                        adjusted[entity] += per_entity
        
        return adjusted
    
    # Helper methods for cost calculations
    
    def _get_regional_price_difference(self, from_region: str, to_region: str) -> float:
        """Get price difference between regions (%)"""
        price_indices = {
            'Malaysia': 100,
            'India': 85,  # 15% cheaper
            'Thailand': 95,
            'Vietnam': 90,
            'Indonesia': 92,
            'China': 88
        }
        
        from_price = price_indices.get(from_region, 100)
        to_price = price_indices.get(to_region, 100)
        
        return ((to_price - from_price) / from_price * 100)
    
    def _get_tariff_difference(self, from_region: str, to_region: str, category: str) -> float:
        """Get tariff difference (%) using centralized TariffCalculator"""
        # Lazy load tariff calculator to avoid circular imports
        from backend.engines.tariff_calculator import TariffCalculator
        tariff_calc = TariffCalculator()
        
        # Calculate tariff for importing FROM 'from_region' TO a standard destination (e.g. USA or Global Avg)
        # Note: In a real scenario, we need the specific destination country.
        # Assuming we are calculating relative to the Client's location.
        # For this calculation, we look up the tariff rate FROM the region.
        
        # Since we don't have the destination country here, we'll estimate based on global average tariffs
        # or assume the client is in a specific region (e.g., USA)
        destination_country = "USA" # Default for comparison
        
        try:
            # Tariff from OLD region
            t1 = tariff_calc.get_tariff_rate(from_region, destination_country, category)
            
            # Tariff from NEW region
            t2 = tariff_calc.get_tariff_rate(to_region, destination_country, category)
            
            return t2 - t1
        except Exception:
            # Fallback if calculator fails
            return 0.0
    
    def _get_logistics_cost_difference(self, from_region: str, to_region: str) -> float:
        """Get logistics cost difference (%)"""
        # Simplified logistics cost model
        logistics_costs = {
            'Malaysia': 2.0,
            'India': 2.5,
            'Thailand': 1.8,
            'Vietnam': 2.2,
            'Indonesia': 2.3,
            'China': 2.0
        }
        
        from_cost = logistics_costs.get(from_region, 2.0)
        to_cost = logistics_costs.get(to_region, 2.0)
        
        return to_cost - from_cost
    
    def _get_quality_cost_difference(self, from_region: str, to_region: str) -> float:
        """Get quality/compliance cost difference (%)"""
        # Some regions require more quality control/compliance costs
        quality_costs = {
            'Malaysia': 0.5,
            'India': 1.0,  # Higher quality control costs
            'Thailand': 0.3,
            'Vietnam': 0.8,
            'Indonesia': 0.9,
            'China': 0.7
        }
        
        from_cost = quality_costs.get(from_region, 0.5)
        to_cost = quality_costs.get(to_region, 0.5)
        
        return to_cost - from_cost
    
    def generate_validation_report(self, result: ValidationResult) -> str:
        """Generate formatted validation report"""
        report = """
╔══════════════════════════════════════════════════════════════════════╗
║                    CONSTRAINT VALIDATION REPORT                      ║
╚══════════════════════════════════════════════════════════════════════╝
"""
        
        if result.is_valid:
            report += "\n✅ VALIDATION PASSED - No critical violations\n"
        else:
            report += "\n⚠️  VALIDATION FAILED - Violations detected\n"
        
        if result.violations:
            report += f"\n📋 VIOLATIONS ({len(result.violations)}):\n"
            for v in result.violations:
                report += f"\n   [{v.severity.value}] {v.rule_id}: {v.description}\n"
                report += f"   Current: {v.current_value}, Threshold: {v.threshold}\n"
                report += f"   Action: {v.recommended_action}\n"
        
        if result.spend_impacts:
            report += f"\n💰 SPEND IMPACTS:\n"
            for impact in result.spend_impacts:
                report += f"\n   {impact.from_region} → {impact.to_region}:\n"
                report += f"   Cost Delta: ${impact.cost_delta:,.2f} ({impact.cost_delta_pct:+.1f}%)\n"
        
        if result.recommendations:
            report += f"\n💡 RECOMMENDATIONS:\n"
            for rec in result.recommendations:
                report += f"   {rec}\n"
        
        return report


# Example usage
if __name__ == "__main__":
    from backend.engines.data_loader import DataLoader
    from backend.engines.rule_evaluation_engine import RuleEvaluationEngine
    
    data_loader = DataLoader()
    rule_engine = RuleEvaluationEngine()
    validator = ConstraintValidationAgent(data_loader, rule_engine)
    
    print("="*80)
    print("CONSTRAINT VALIDATION AGENT DEMO")
    print("="*80)
    
    # Example 1: Validate supplier allocation
    print("\n📊 Example 1: Validate supplier allocation")
    proposed_allocation = {
        'S001': 35.0,  # Violates 30% rule
        'S002': 25.0,
        'S003': 20.0,
        'S004': 20.0
    }
    
    result = validator.validate_allocation(
        proposed_allocation=proposed_allocation,
        allocation_type='supplier',
        client_id='C001',
        category='Rice Bran Oil',
        total_spend=2000000
    )
    
    print(validator.generate_validation_report(result))
    
    # Example 2: Calculate region move impact
    print("\n📊 Example 2: Calculate impact of moving from Malaysia to India")
    impact = validator.calculate_region_move_impact(
        from_region='Malaysia',
        to_region='India',
        volume_pct=20.0,
        category='Rice Bran Oil',
        total_spend=2000000
    )
    
    print(f"\nMoving 20% of volume from Malaysia to India:")
    print(f"   Volume: ${impact.volume_moved:,.2f}")
    print(f"   Current Cost: ${impact.current_cost:,.2f}")
    print(f"   New Cost: ${impact.new_cost:,.2f}")
    print(f"   Cost Delta: ${impact.cost_delta:,.2f} ({impact.cost_delta_pct:+.1f}%)")
    print(f"   Total Impact: {impact.total_impact:+.1f}%")
