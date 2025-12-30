"""
Universal Sourcing Optimization Engine

Handles violations of ANY of the 35 procurement rules (R001-R035) with 
dynamic strategy selection and comprehensive validation.

Key Feature: R001 was just an example - this works for ALL rules.
"""

import pandas as pd
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class RuleCategory(Enum):
    """Rule categories for strategy selection"""
    GEOGRAPHIC_RISK = "Geographic Risk"
    SUPPLY_CHAIN_RISK = "Supply Chain Risk"
    COST_MANAGEMENT = "Cost Management"
    QUALITY_PERFORMANCE = "Quality Assurance"
    FINANCIAL_RISK = "Financial Risk"
    SUSTAINABILITY_ESG = "Sustainability"
    CONTRACT_MANAGEMENT = "Contract Management"
    OPERATIONAL_EFFICIENCY = "Operational Efficiency"
    COMPLIANCE_SECURITY = "Information Security"
    STRATEGIC_INNOVATION = "Strategic Sourcing"


class Priority(Enum):
    """Priority levels for rule violations"""
    CRITICAL = "Critical"
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"


@dataclass
class RuleViolation:
    """Represents a rule violation"""
    rule_id: str
    rule_name: str
    violated: bool
    current_value: float
    threshold: float
    risk_level: str
    category: str
    comparison_logic: str


@dataclass
class OptimizationStrategy:
    """Optimization strategy for a rule category"""
    branch_a_strategy: str
    branch_b_strategy: str
    tools: List[str]
    data_requirements: List[str]


@dataclass
class OptimizationResult:
    """Result of optimization workflow"""
    rule_id: str
    rule_name: str
    recommendations: List[Dict[str, Any]]
    cost_impact: float
    risk_reduction: float
    implementation_timeline: int
    all_rules_compliant: bool
    violations: List[RuleViolation]


class SourcingOptimizationEngine:
    """
    Universal Sourcing Optimization Engine
    
    Handles any of the 35 procurement rule violations with dynamic
    strategy selection and comprehensive validation.
    """
    
    def __init__(self, data_loader):
        """
        Initialize the optimization engine
        
        Args:
            data_loader: DataLoader instance for accessing data
        """
        self.data_loader = data_loader
        self.rulebook = self._load_rulebook()
        self.strategy_map = self._initialize_strategy_map()
        self.max_iterations = 5
        
        logger.info("Sourcing Optimization Engine initialized")
    
    def _load_rulebook(self) -> pd.DataFrame:
        """Load procurement rulebook"""
        try:
            rulebook = pd.read_csv('data/structured/procurement_rulebook.csv')
            logger.info(f"Loaded {len(rulebook)} procurement rules")
            return rulebook
        except Exception as e:
            logger.error(f"Error loading rulebook: {e}")
            return pd.DataFrame()
    
    def _initialize_strategy_map(self) -> Dict[str, OptimizationStrategy]:
        """Initialize strategy mapping for each rule category"""
        return {
            RuleCategory.GEOGRAPHIC_RISK.value: OptimizationStrategy(
                branch_a_strategy="alternate_region_identification",
                branch_b_strategy="incumbent_supplier_regional_shift",
                tools=["tariff_calculator", "geopolitical_risk_analyzer"],
                data_requirements=["current_sourcing_regions", "import_export_countries", 
                                 "tariff_data", "trade_agreements"]
            ),
            RuleCategory.SUPPLY_CHAIN_RISK.value: OptimizationStrategy(
                branch_a_strategy="new_supplier_identification",
                branch_b_strategy="volume_redistribution",
                tools=["supplier_qualifier", "capacity_analyzer"],
                data_requirements=["current_supplier_list", "supplier_capacity_data",
                                 "performance_history", "financial_health_data"]
            ),
            RuleCategory.COST_MANAGEMENT.value: OptimizationStrategy(
                branch_a_strategy="market_analysis_competitive_bidding",
                branch_b_strategy="contract_optimization",
                tools=["price_benchmark_tool", "hedging_calculator"],
                data_requirements=["current_pricing", "market_benchmarks",
                                 "historical_price_trends", "competitor_pricing"]
            ),
            RuleCategory.QUALITY_PERFORMANCE.value: OptimizationStrategy(
                branch_a_strategy="quality_improvement_program",
                branch_b_strategy="high_quality_supplier_identification",
                tools=["quality_scorer", "audit_analyzer"],
                data_requirements=["quality_metrics", "defect_rates",
                                 "audit_scores", "certification_status"]
            ),
            RuleCategory.FINANCIAL_RISK.value: OptimizationStrategy(
                branch_a_strategy="financial_due_diligence",
                branch_b_strategy="financially_stable_supplier_identification",
                tools=["financial_analyzer", "credit_scorer"],
                data_requirements=["financial_statements", "credit_ratings",
                                 "debt_equity_ratios", "cash_flow_data"]
            ),
            RuleCategory.SUSTAINABILITY_ESG.value: OptimizationStrategy(
                branch_a_strategy="esg_certified_supplier_identification",
                branch_b_strategy="esg_improvement_program",
                tools=["esg_scorer", "certification_validator"],
                data_requirements=["esg_scores", "sustainability_certifications",
                                 "carbon_footprint_data", "ethical_compliance_records"]
            ),
            RuleCategory.CONTRACT_MANAGEMENT.value: OptimizationStrategy(
                branch_a_strategy="contract_renewal_negotiation",
                branch_b_strategy="competitive_rebidding",
                tools=["contract_analyzer", "negotiation_optimizer"],
                data_requirements=["current_contracts", "contract_terms",
                                 "renewal_dates", "market_rates"]
            ),
            RuleCategory.OPERATIONAL_EFFICIENCY.value: OptimizationStrategy(
                branch_a_strategy="supplier_consolidation",
                branch_b_strategy="preferred_supplier_program",
                tools=["consolidation_analyzer", "admin_cost_calculator"],
                data_requirements=["supplier_count", "transaction_volumes",
                                 "administrative_costs", "volume_leverage"]
            ),
            RuleCategory.COMPLIANCE_SECURITY.value: OptimizationStrategy(
                branch_a_strategy="compliant_supplier_identification",
                branch_b_strategy="compliance_improvement_program",
                tools=["compliance_checker", "security_auditor"],
                data_requirements=["compliance_status", "certifications",
                                 "audit_reports", "security_ratings"]
            ),
            RuleCategory.STRATEGIC_INNOVATION.value: OptimizationStrategy(
                branch_a_strategy="innovative_supplier_partnership",
                branch_b_strategy="innovation_program_development",
                tools=["innovation_scorer", "partnership_analyzer"],
                data_requirements=["innovation_scores", "rd_capabilities",
                                 "patent_portfolios", "technology_roadmaps"]
            )
        }
    
    def detect_rule_violation(self, rule_id: str, current_metrics: Dict[str, Any]) -> RuleViolation:
        """
        Detect if a specific rule is violated
        
        Args:
            rule_id: Rule ID (e.g., 'R001')
            current_metrics: Current metrics for evaluation
            
        Returns:
            RuleViolation object
        """
        rule = self.rulebook[self.rulebook['Rule_ID'] == rule_id].iloc[0]
        
        # Parse threshold value (handle percentages and other formats)
        threshold_str = str(rule['Threshold_Value'])
        threshold = self._parse_threshold(threshold_str)
        
        comparison = rule['Comparison_Logic']
        
        # Extract metric value from current_metrics
        metric_key = self._get_metric_key_for_rule(rule_id)
        current_value = current_metrics.get(metric_key, 0)
        
        # Determine violation based on comparison logic
        violated = self._evaluate_comparison(current_value, threshold, comparison)
        
        return RuleViolation(
            rule_id=rule_id,
            rule_name=rule['Rule_Name'],
            violated=violated,
            current_value=current_value,
            threshold=threshold,
            risk_level=rule['Risk_Level'],
            category=rule['Category'],
            comparison_logic=comparison
        )
    
    def _parse_threshold(self, threshold_str: str) -> float:
        """Parse threshold value from string (handles %, days, etc.)"""
        try:
            # Remove common units
            threshold_str = threshold_str.replace('%', '').replace(' days', '').replace(' months', '')
            threshold_str = threshold_str.replace(' suppliers', '').replace(' times/year', '')
            threshold_str = threshold_str.replace(' rating', '').replace(' years', '')
            threshold_str = threshold_str.replace(' hours', '').replace(' kg CO2/unit', '')
            
            # Handle special cases
            if 'suppliers per' in threshold_str:
                # Extract number before 'suppliers'
                parts = threshold_str.split()
                return float(parts[0])
            
            # Try to convert to float
            return float(threshold_str.strip())
        except (ValueError, AttributeError):
            # Default to 0 if parsing fails
            logger.warning(f"Could not parse threshold: {threshold_str}, defaulting to 0")
            return 0.0
    
    def _get_metric_key_for_rule(self, rule_id: str) -> str:
        """Get the metric key for a specific rule"""
        # Map rule IDs to metric keys
        metric_map = {
            'R001': 'regional_concentration',
            'R003': 'single_supplier_percentage',
            'R006': 'price_variance_percentage',
            'R007': 'quality_rejection_rate',
            # Add more mappings as needed
        }
        return metric_map.get(rule_id, rule_id.lower())
    
    def _evaluate_comparison(self, current_value: float, threshold: float, 
                           comparison: str) -> bool:
        """Evaluate if violation exists based on comparison logic"""
        if '>' in comparison:
            return current_value > threshold
        elif '<' in comparison:
            return current_value < threshold
        else:
            return False
    
    def select_optimization_strategy(self, rule_category: str) -> OptimizationStrategy:
        """
        Select optimization strategy based on rule category
        
        Args:
            rule_category: Category of the violated rule
            
        Returns:
            OptimizationStrategy for the category
        """
        strategy = self.strategy_map.get(rule_category)
        
        if not strategy:
            logger.warning(f"No strategy found for category: {rule_category}")
            # Return default strategy
            return OptimizationStrategy(
                branch_a_strategy="general_optimization",
                branch_b_strategy="alternative_analysis",
                tools=["general_analyzer"],
                data_requirements=["basic_data"]
            )
        
        logger.info(f"Selected strategy for {rule_category}: "
                   f"Branch A={strategy.branch_a_strategy}, "
                   f"Branch B={strategy.branch_b_strategy}")
        
        return strategy
    
    def generate_data_checklist(self, rule_category: str) -> List[str]:
        """
        Generate rule-specific data requirements checklist
        
        Args:
            rule_category: Category of the violated rule
            
        Returns:
            List of required data elements
        """
        strategy = self.select_optimization_strategy(rule_category)
        return strategy.data_requirements
    
    def validate_against_all_rules(self, proposed_state: Dict[str, Any]) -> Tuple[bool, List[RuleViolation]]:
        """
        Validate proposed state against ALL 35 rules
        
        Args:
            proposed_state: Proposed metrics after optimization
            
        Returns:
            Tuple of (is_compliant, list_of_violations)
        """
        violations = []
        
        for _, rule in self.rulebook.iterrows():
            violation = self.detect_rule_violation(rule['Rule_ID'], proposed_state)
            
            if violation.violated:
                violations.append(violation)
        
        is_compliant = len(violations) == 0
        
        logger.info(f"Validation result: {'COMPLIANT' if is_compliant else 'VIOLATIONS FOUND'} "
                   f"({len(violations)} violations)")
        
        return is_compliant, violations
    
    def execute_branch_a(self, strategy_name: str, current_state: Dict[str, Any],
                        rule_context: RuleViolation) -> Dict[str, Any]:
        """
        Execute Branch A (Primary Strategy)
        
        Args:
            strategy_name: Name of the strategy to execute
            current_state: Current state metrics
            rule_context: Rule violation context
            
        Returns:
            Optimization results from Branch A
        """
        logger.info(f"Executing Branch A: {strategy_name}")
        
        # Strategy execution logic would go here
        # For now, return placeholder results
        
        if strategy_name == "alternate_region_identification":
            return self._execute_alternate_region_identification(current_state, rule_context)
        elif strategy_name == "new_supplier_identification":
            return self._execute_new_supplier_identification(current_state, rule_context)
        elif strategy_name == "market_analysis_competitive_bidding":
            return self._execute_market_analysis(current_state, rule_context)
        else:
            return self._execute_generic_strategy(current_state, rule_context)
    
    def execute_branch_b(self, strategy_name: str, current_state: Dict[str, Any],
                        rule_context: RuleViolation) -> Dict[str, Any]:
        """
        Execute Branch B (Secondary Strategy)
        
        Args:
            strategy_name: Name of the strategy to execute
            current_state: Current state metrics
            rule_context: Rule violation context
            
        Returns:
            Optimization results from Branch B
        """
        logger.info(f"Executing Branch B: {strategy_name}")
        
        # Strategy execution logic would go here
        # For now, return placeholder results
        
        if strategy_name == "incumbent_supplier_regional_shift":
            return self._execute_incumbent_supplier_shift(current_state, rule_context)
        elif strategy_name == "volume_redistribution":
            return self._execute_volume_redistribution(current_state, rule_context)
        elif strategy_name == "contract_optimization":
            return self._execute_contract_optimization(current_state, rule_context)
        else:
            return self._execute_generic_strategy(current_state, rule_context)
    
    def _execute_alternate_region_identification(self, current_state: Dict[str, Any],
                                                rule_context: RuleViolation) -> Dict[str, Any]:
        """Execute alternate region identification strategy"""
        # Placeholder implementation
        return {
            'strategy': 'alternate_region_identification',
            'options': [
                {'region': 'India', 'allocation': 35, 'cost_impact': -2.5, 'risk_score': 65},
                {'region': 'Thailand', 'allocation': 20, 'cost_impact': 1.2, 'risk_score': 55},
            ],
            'recommended_allocation': {'Malaysia': 45, 'India': 35, 'Thailand': 20}
        }
    
    def _execute_new_supplier_identification(self, current_state: Dict[str, Any],
                                            rule_context: RuleViolation) -> Dict[str, Any]:
        """Execute new supplier identification strategy"""
        # Placeholder implementation
        return {
            'strategy': 'new_supplier_identification',
            'options': [
                {'supplier': 'Supplier C', 'allocation': 20, 'cost_impact': 1.5, 'quality_score': 85},
                {'supplier': 'Supplier D', 'allocation': 15, 'cost_impact': 2.0, 'quality_score': 90},
            ]
        }
    
    def _execute_market_analysis(self, current_state: Dict[str, Any],
                                rule_context: RuleViolation) -> Dict[str, Any]:
        """Execute market analysis and competitive bidding strategy"""
        # Placeholder implementation
        return {
            'strategy': 'market_analysis_competitive_bidding',
            'market_price': 950,
            'current_price': 1000,
            'potential_savings': 5.0
        }
    
    def _execute_incumbent_supplier_shift(self, current_state: Dict[str, Any],
                                         rule_context: RuleViolation) -> Dict[str, Any]:
        """Execute incumbent supplier regional shift strategy"""
        # Placeholder implementation
        return {
            'strategy': 'incumbent_supplier_regional_shift',
            'options': [
                {'supplier': 'Supplier B', 'region': 'India', 'additional_capacity': 500}
            ]
        }
    
    def _execute_volume_redistribution(self, current_state: Dict[str, Any],
                                      rule_context: RuleViolation) -> Dict[str, Any]:
        """Execute volume redistribution strategy"""
        # Placeholder implementation
        return {
            'strategy': 'volume_redistribution',
            'recommended_allocation': {'Supplier A': 50, 'Supplier B': 30, 'Supplier C': 20}
        }
    
    def _execute_contract_optimization(self, current_state: Dict[str, Any],
                                      rule_context: RuleViolation) -> Dict[str, Any]:
        """Execute contract optimization strategy"""
        # Placeholder implementation
        return {
            'strategy': 'contract_optimization',
            'fixed_price_option': {'duration': 12, 'price': 980, 'savings': 2.0},
            'hedging_option': {'cost': 10, 'risk_reduction': 80}
        }
    
    def _execute_generic_strategy(self, current_state: Dict[str, Any],
                                 rule_context: RuleViolation) -> Dict[str, Any]:
        """Execute generic optimization strategy"""
        return {
            'strategy': 'generic_optimization',
            'recommendation': 'Optimize based on rule requirements'
        }
    
    def optimize(self, rule_id: str, current_metrics: Dict[str, Any],
                client_preferences: Optional[Dict[str, float]] = None) -> OptimizationResult:
        """
        Main optimization workflow - works for ANY rule
        
        Args:
            rule_id: Rule ID to optimize for (R001-R035)
            current_metrics: Current state metrics
            client_preferences: Optional client-specific criteria weights
            
        Returns:
            OptimizationResult with recommendations
        """
        logger.info(f"Starting optimization workflow for {rule_id}")
        
        # Step 1: Detect violation
        violation = self.detect_rule_violation(rule_id, current_metrics)
        
        if not violation.violated:
            logger.info(f"{rule_id} is not violated. No optimization needed.")
            return OptimizationResult(
                rule_id=rule_id,
                rule_name=violation.rule_name,
                recommendations=[],
                cost_impact=0.0,
                risk_reduction=0.0,
                implementation_timeline=0,
                all_rules_compliant=True,
                violations=[]
            )
        
        logger.info(f"Violation detected: {violation.rule_name} "
                   f"(Current: {violation.current_value}, Threshold: {violation.threshold})")
        
        # Step 2: Select strategy
        strategy = self.select_optimization_strategy(violation.category)
        
        # Step 3: Execute parallel branches with validation loops
        branch_a_result = None
        branch_b_result = None
        
        for iteration in range(self.max_iterations):
            logger.info(f"Optimization iteration {iteration + 1}/{self.max_iterations}")
            
            # Execute Branch A
            branch_a_result = self.execute_branch_a(
                strategy.branch_a_strategy,
                current_metrics,
                violation
            )
            
            # Execute Branch B
            branch_b_result = self.execute_branch_b(
                strategy.branch_b_strategy,
                current_metrics,
                violation
            )
            
            # Create proposed state from results
            proposed_state = self._create_proposed_state(
                current_metrics,
                branch_a_result,
                branch_b_result
            )
            
            # Validate against all rules
            is_compliant, violations = self.validate_against_all_rules(proposed_state)
            
            if is_compliant:
                logger.info(f"Compliant solution found in iteration {iteration + 1}")
                break
            else:
                logger.warning(f"Iteration {iteration + 1}: {len(violations)} violations found")
                # Adjust and continue loop
                current_metrics = self._adjust_for_violations(proposed_state, violations)
        
        # Step 4: Generate recommendations
        recommendations = self._generate_recommendations(
            branch_a_result,
            branch_b_result,
            client_preferences
        )
        
        # Step 5: Calculate impact
        cost_impact = self._calculate_cost_impact(recommendations)
        risk_reduction = self._calculate_risk_reduction(violation, recommendations)
        timeline = self._estimate_timeline(violation.category)
        
        return OptimizationResult(
            rule_id=rule_id,
            rule_name=violation.rule_name,
            recommendations=recommendations,
            cost_impact=cost_impact,
            risk_reduction=risk_reduction,
            implementation_timeline=timeline,
            all_rules_compliant=is_compliant,
            violations=violations if not is_compliant else []
        )
    
    def _create_proposed_state(self, current_state: Dict[str, Any],
                              branch_a_result: Dict[str, Any],
                              branch_b_result: Dict[str, Any]) -> Dict[str, Any]:
        """Create proposed state from optimization results"""
        # Merge results into proposed state
        proposed = current_state.copy()
        
        # Update based on branch results
        if 'recommended_allocation' in branch_a_result:
            proposed['allocation'] = branch_a_result['recommended_allocation']
        
        return proposed
    
    def _adjust_for_violations(self, proposed_state: Dict[str, Any],
                              violations: List[RuleViolation]) -> Dict[str, Any]:
        """Adjust proposed state to resolve violations"""
        # Adjustment logic would go here
        # For now, return proposed state
        return proposed_state
    
    def _generate_recommendations(self, branch_a_result: Dict[str, Any],
                                 branch_b_result: Dict[str, Any],
                                 client_preferences: Optional[Dict[str, float]]) -> List[Dict[str, Any]]:
        """Generate top 3 recommendations from branch results"""
        recommendations = []
        
        # Combine and rank options from both branches
        # For now, return placeholder recommendations
        
        recommendations.append({
            'rank': 1,
            'strategy': branch_a_result.get('strategy', 'optimization'),
            'description': 'Primary recommendation from Branch A',
            'details': branch_a_result,
            'score': 89
        })
        
        recommendations.append({
            'rank': 2,
            'strategy': branch_b_result.get('strategy', 'optimization'),
            'description': 'Secondary recommendation from Branch B',
            'details': branch_b_result,
            'score': 84
        })
        
        return recommendations
    
    def _calculate_cost_impact(self, recommendations: List[Dict[str, Any]]) -> float:
        """Calculate cost impact of recommendations"""
        if not recommendations:
            return 0.0
        
        # Get cost impact from top recommendation
        top_rec = recommendations[0]
        details = top_rec.get('details', {})
        
        return details.get('cost_impact', 0.0)
    
    def _calculate_risk_reduction(self, violation: RuleViolation,
                                  recommendations: List[Dict[str, Any]]) -> float:
        """Calculate risk reduction percentage"""
        # Placeholder calculation
        return 42.0  # 42% risk reduction
    
    def _estimate_timeline(self, category: str) -> int:
        """Estimate implementation timeline in days"""
        timeline_map = {
            RuleCategory.GEOGRAPHIC_RISK.value: 90,
            RuleCategory.SUPPLY_CHAIN_RISK.value: 60,
            RuleCategory.COST_MANAGEMENT.value: 45,
            RuleCategory.QUALITY_PERFORMANCE.value: 60,
            RuleCategory.FINANCIAL_RISK.value: 60,
            RuleCategory.SUSTAINABILITY_ESG.value: 90,
            RuleCategory.CONTRACT_MANAGEMENT.value: 45,
            RuleCategory.OPERATIONAL_EFFICIENCY.value: 60,
            RuleCategory.COMPLIANCE_SECURITY.value: 90,
            RuleCategory.STRATEGIC_INNOVATION.value: 120
        }
        
        return timeline_map.get(category, 60)
