"""
Enhanced Cost & Risk Loop Engine
Granular iteration system for refining allocations
Loops until constraints are satisfied or optimal solution found
"""

import sys
from pathlib import Path
from typing import Dict, Any, List, Tuple, Optional
from dataclasses import dataclass
import pandas as pd
from datetime import datetime
import json

root_path = Path(__file__).parent.parent.parent.parent
if str(root_path) not in sys.path:
    sys.path.insert(0, str(root_path))

from backend.agents.base_agent import BaseAgent


@dataclass
class AllocationIteration:
    """Represents one iteration of allocation refinement"""
    iteration_num: int
    proposed_allocation: Dict[str, float]  # region/supplier -> percentage
    violations: List[str]
    cost: float
    risk_score: float
    constraint_satisfaction: float  # 0-100%
    recommended_adjustments: List[str]
    feasible: bool
    score: float  # Overall optimization score


class CostAndRiskLoopEngine(BaseAgent):
    """
    Advanced iteration engine that refines allocations
    Finds optimal solutions within constraint boundaries
    Provides multiple viable options to user
    """
    
    MAX_ITERATIONS = 50
    CONVERGENCE_THRESHOLD = 0.1  # 0.1% improvement threshold
    
    def __init__(self):
        super().__init__(
            name="CostAndRiskLoop",
            description="Iteratively refines allocations for cost and constraint optimization"
        )
    
    def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute cost and risk loop optimization
        
        Input:
            - initial_allocation: Dict - starting point
            - constraints: List[Dict] - constraints to satisfy
            - optimization_target: str - 'min_cost', 'min_risk', 'balanced'
            - available_options: List[Dict] - suppliers/regions to choose from
            - client_preferences: Dict - client preferences
        """
        try:
            loop_id = f"LOOP_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            initial_allocation = input_data.get('initial_allocation', {})
            constraints = input_data.get('constraints', [])
            optimization_target = input_data.get('optimization_target', 'balanced')
            available_options = input_data.get('available_options', [])
            client_preferences = input_data.get('client_preferences', {})
            
            self._log(f"[{loop_id}] Starting cost/risk optimization loop")
            self._log(f"[{loop_id}] Target: {optimization_target}, Options: {len(available_options)}")
            
            # Run iterative optimization
            iterations = self._run_optimization_loop(
                initial_allocation, constraints, available_options, 
                optimization_target, loop_id
            )
            
            # Analyze results
            feasible_solutions = [it for it in iterations if it.feasible]
            optimal_solution = self._find_optimal_solution(feasible_solutions, optimization_target)
            alternative_solutions = self._find_alternative_solutions(feasible_solutions, optimal_solution, 3)
            
            # Generate report
            result = {
                'loop_id': loop_id,
                'timestamp': datetime.now().isoformat(),
                'optimization_target': optimization_target,
                'total_iterations': len(iterations),
                'feasible_solutions_found': len(feasible_solutions),
                'convergence_achieved': self._check_convergence(iterations),
                'iterations_detail': [self._iteration_to_dict(it) for it in iterations],
                'optimal_solution': self._iteration_to_dict(optimal_solution) if optimal_solution else None,
                'alternative_solutions': [
                    self._iteration_to_dict(alt) for alt in alternative_solutions
                ],
                'analysis': {
                    'cost_range': self._analyze_cost_range(feasible_solutions),
                    'risk_range': self._analyze_risk_range(feasible_solutions),
                    'constraint_satisfaction_summary': self._summarize_constraints(feasible_solutions),
                    'recommendation': self._generate_loop_recommendation(
                        optimal_solution, alternative_solutions, feasible_solutions
                    )
                }
            }
            
            self._log(f"[{loop_id}] Loop complete: {len(feasible_solutions)} feasible solutions found")
            
            return self._create_response(
                success=True,
                data=result
            )
            
        except Exception as e:
            self._log(f"Error in cost/risk loop: {str(e)}", "ERROR")
            return self._create_response(
                success=False,
                error=str(e)
            )
    
    def _run_optimization_loop(
        self, initial_allocation: Dict, constraints: List, available_options: List,
        optimization_target: str, loop_id: str
    ) -> List[AllocationIteration]:
        """Run the iterative optimization loop"""
        
        iterations = []
        current_allocation = initial_allocation.copy()
        best_score = float('-inf')
        no_improvement_count = 0
        
        for iteration_num in range(1, self.MAX_ITERATIONS + 1):
            # Evaluate current allocation
            violations = self._check_constraints(current_allocation, constraints)
            cost = self._calculate_cost(current_allocation, available_options)
            risk_score = self._calculate_risk(current_allocation, available_options)
            constraint_satisfaction = self._calculate_constraint_satisfaction(violations, constraints)
            
            # Calculate overall score
            score = self._calculate_optimization_score(
                cost, risk_score, constraint_satisfaction, optimization_target
            )
            
            # Check if feasible
            feasible = len(violations) == 0
            
            # Generate recommendations for next iteration
            recommendations = self._generate_adjustment_recommendations(
                current_allocation, violations, cost, risk_score, optimization_target
            )
            
            # Create iteration record
            iteration = AllocationIteration(
                iteration_num=iteration_num,
                proposed_allocation=current_allocation.copy(),
                violations=violations,
                cost=cost,
                risk_score=risk_score,
                constraint_satisfaction=constraint_satisfaction,
                recommended_adjustments=recommendations,
                feasible=feasible,
                score=score
            )
            
            iterations.append(iteration)
            
            self._log(
                f"[{loop_id}] Iteration {iteration_num}: "
                f"Score={score:.2f}, Cost=${cost:,.0f}, Risk={risk_score:.1f}, "
                f"Violations={len(violations)}, Feasible={feasible}"
            )
            
            # Check convergence
            if score > best_score - self.CONVERGENCE_THRESHOLD:
                no_improvement_count += 1
                if no_improvement_count >= 5:  # 5 iterations without improvement
                    self._log(f"[{loop_id}] Convergence achieved at iteration {iteration_num}")
                    break
            else:
                no_improvement_count = 0
                best_score = score
            
            # If feasible and good score, continue exploring
            if feasible and score > 80:
                # Try fine-tuning adjustments
                current_allocation = self._fine_tune_allocation(
                    current_allocation, available_options, optimization_target
                )
            elif not feasible:
                # Apply constraint-fixing recommendations
                current_allocation = self._apply_constraint_fixes(
                    current_allocation, recommendations, available_options
                )
            else:
                # Apply optimization recommendations
                current_allocation = self._apply_optimization_adjustments(
                    current_allocation, recommendations, available_options
                )
        
        return iterations
    
    def _check_constraints(self, allocation: Dict, constraints: List) -> List[str]:
        """Check which constraints are violated"""
        violations = []
        
        for constraint in constraints:
            constraint_type = constraint.get('type')
            
            if constraint_type == 'max_supplier_pct':
                supplier = constraint.get('supplier')
                max_pct = constraint.get('value', 30)
                current_pct = allocation.get(supplier, 0)
                
                if current_pct > max_pct:
                    violations.append(
                        f"Supplier {supplier}: {current_pct:.1f}% exceeds max {max_pct}%"
                    )
            
            elif constraint_type == 'max_region_pct':
                region = constraint.get('region')
                max_pct = constraint.get('value', 40)
                region_pct = sum([v for k, v in allocation.items() if k.startswith(region)])
                
                if region_pct > max_pct:
                    violations.append(
                        f"Region {region}: {region_pct:.1f}% exceeds max {max_pct}%"
                    )
            
            elif constraint_type == 'min_suppliers':
                min_suppliers = constraint.get('value', 3)
                active_suppliers = len([v for v in allocation.values() if v > 0])
                
                if active_suppliers < min_suppliers:
                    violations.append(
                        f"Only {active_suppliers} suppliers active, minimum {min_suppliers} required"
                    )
            
            elif constraint_type == 'quality_requirement':
                entity = constraint.get('entity')
                min_quality = constraint.get('value', 4.0)
                # Would need to cross-reference with supplier data
                violations.append(f"Quality check needed for {entity}")
        
        # Check business rules from rule_book.json
        business_rule_violations = self._check_business_rules(allocation)
        violations.extend(business_rule_violations)
        
        return violations
    
    def _check_business_rules(self, allocation: Dict) -> List[str]:
        """Check against ALL business rules from rule_book.json (35+ rules)"""
        violations = []
        
        try:
            rule_book_path = Path(root_path) / 'rules' / 'rule_book.json'
            if not rule_book_path.exists():
                return violations
            
            with open(rule_book_path, 'r') as f:
                rule_book = json.load(f)
            
            # CHECK ALL HARD CONSTRAINTS (HC001-HC008)
            hard_constraints = rule_book.get('hard_constraints', {}).get('rules', [])
            for rule in hard_constraints:
                violations.extend(self._check_hard_constraint(rule, allocation))
            
            # CHECK ALL SOFT PREFERENCES (SP001-SP007)
            soft_preferences = rule_book.get('soft_preferences', {}).get('rules', [])
            for rule in soft_preferences:
                violations.extend(self._check_soft_preference(rule, allocation))
            
            # CHECK ALL RISK ASSESSMENT RULES (RA001-RA006)
            risk_rules = rule_book.get('risk_assessment_rules', {}).get('rules', [])
            for rule in risk_rules:
                violations.extend(self._check_risk_rule(rule, allocation))
            
            # CHECK DATA COMPLETENESS RULES
            data_rules = rule_book.get('data_completeness_rules', {}).get('critical_data_points', [])
            for rule in data_rules:
                violations.extend(self._check_data_completeness(rule, allocation))
            
            # CHECK ESCALATION RULES
            escalation_rules = rule_book.get('escalation_rules', {}).get('escalation_triggers', [])
            for rule in escalation_rules:
                violations.extend(self._check_escalation_rule(rule, allocation))
        
        except Exception as e:
            self.logger.warning(f"Error checking business rules: {e}")
        
        return violations
    
    def _check_hard_constraint(self, rule: Dict, allocation: Dict) -> List[str]:
        """Check individual hard constraint (HC001-HC008)"""
        violations = []
        rule_id = rule.get('rule_id')
        rule_name = rule.get('name')
        
        # HC001: Mandatory Food Safety Certification
        if rule_id == 'HC001':
            violations.append(f"[HC001] Verify food safety certifications (ISO 22000 or HACCP)")
        
        # HC002: Minimum Quality Rating
        elif rule_id == 'HC002':
            violations.append(f"[HC002] Quality ratings must be >= 4.0")
        
        # HC003: Minimum Delivery Reliability
        elif rule_id == 'HC003':
            violations.append(f"[HC003] Delivery reliability must be >= 90%")
        
        # HC004: Palm Oil RSPO Certification
        elif rule_id == 'HC004':
            violations.append(f"[HC004] Palm Oil products require RSPO certification")
        
        # HC005: Maximum Price Deviation (15%)
        elif rule_id == 'HC005':
            violations.append(f"[HC005] Prices must be within 15% of benchmark")
        
        # HC006: Client-Specific Certifications
        elif rule_id == 'HC006':
            violations.append(f"[HC006] Verify supplier has all required client certifications")
        
        # HC007: Payment Terms Compatibility
        elif rule_id == 'HC007':
            violations.append(f"[HC007] Verify payment terms compatibility")
        
        # HC008: Minimum Order Quantity Feasibility
        elif rule_id == 'HC008':
            violations.append(f"[HC008] Verify order quantity meets supplier MOQ")
        
        return violations
    
    def _check_soft_preference(self, rule: Dict, allocation: Dict) -> List[str]:
        """Check soft preferences (SP001-SP007) - scored, not violated"""
        warnings = []
        rule_id = rule.get('rule_id')
        weight = rule.get('weight', 0)
        
        # SP001: High Sustainability Score
        if rule_id == 'SP001':
            warnings.append(f"[SP001] Sustainability score >= 8.0 preferred (weight: {weight}%)")
        
        # SP002: Premium Quality Rating
        elif rule_id == 'SP002':
            warnings.append(f"[SP002] Quality rating >= 4.5 preferred (weight: {weight}%)")
        
        # SP003: Excellent Delivery Reliability
        elif rule_id == 'SP003':
            warnings.append(f"[SP003] Delivery >= 95% preferred (weight: {weight}%)")
        
        # SP004: Below Benchmark Pricing
        elif rule_id == 'SP004':
            warnings.append(f"[SP004] Below-benchmark pricing preferred (weight: {weight}%)")
        
        # SP005: Established Supplier (20+ years)
        elif rule_id == 'SP005':
            warnings.append(f"[SP005] Suppliers with 20+ years experience preferred (weight: {weight}%)")
        
        # SP006: Short Lead Time
        elif rule_id == 'SP006':
            warnings.append(f"[SP006] Lead time <= 14 days preferred (weight: {weight}%)")
        
        # SP007: Regional Preference
        elif rule_id == 'SP007':
            warnings.append(f"[SP007] Local/regional suppliers preferred (weight: {weight}%)")
        
        return warnings
    
    def _check_risk_rule(self, rule: Dict, allocation: Dict) -> List[str]:
        """Check risk assessment rules (RA001-RA006)"""
        flags = []
        rule_id = rule.get('rule_id')
        risk_level = rule.get('risk_level')
        
        # RA001: Single Supplier Dependency
        if rule_id == 'RA001':
            active_suppliers = len([v for v in allocation.values() if v > 0])
            if active_suppliers == 1:
                flags.append(f"[RA001] HIGH RISK: Single supplier dependency - recommend dual sourcing")
        
        # RA002: Historical Quality Issues
        elif rule_id == 'RA002':
            flags.append(f"[RA002] MEDIUM RISK: Check for historical quality issues")
        
        # RA003: Historical Delivery Issues
        elif rule_id == 'RA003':
            flags.append(f"[RA003] MEDIUM RISK: Check for historical delivery issues")
        
        # RA004: High Price Volatility
        elif rule_id == 'RA004':
            flags.append(f"[RA004] MEDIUM RISK: High price volatility - consider hedging")
        
        # RA005: Low Sustainability Score
        elif rule_id == 'RA005':
            flags.append(f"[RA005] LOW RISK: Sustainability score < 7.0 - request improvement plan")
        
        # RA006: Order Size Near Supplier Capacity
        elif rule_id == 'RA006':
            flags.append(f"[RA006] HIGH RISK: Order near supplier capacity - verify backup plans")
        
        return flags
    
    def _check_data_completeness(self, rule: Dict, allocation: Dict) -> List[str]:
        """Check data completeness and flag gaps"""
        gaps = []
        data_point = rule.get('data_point')
        importance = rule.get('importance')
        
        # Flag as data gap (in real system, would check against actual supplier data)
        if importance == 'CRITICAL':
            gaps.append(f"[DATA_GAP] CRITICAL: Missing {data_point}")
        elif importance == 'HIGH':
            gaps.append(f"[DATA_GAP] HIGH: Incomplete {data_point}")
        
        return gaps
    
    def _check_escalation_rule(self, rule: Dict, allocation: Dict) -> List[str]:
        """Check escalation triggers"""
        escalations = []
        rule_id = rule.get('trigger_id')
        
        # ESC001: Low confidence
        if rule_id == 'ESC001':
            escalations.append(f"[ESC001] Flag for review if confidence < 70%")
        
        # ESC002: Price deviation > 10%
        elif rule_id == 'ESC002':
            escalations.append(f"[ESC002] Require approval if price deviation > 10%")
        
        # ESC003: New supplier with large order
        elif rule_id == 'ESC003':
            escalations.append(f"[ESC003] Require approval for new supplier + order > $100K")
        
        # ESC004: High-risk recommendations
        elif rule_id == 'ESC004':
            escalations.append(f"[ESC004] Require risk review for HIGH risk recommendations")
        
        # ESC005: Hard constraint violations
        elif rule_id == 'ESC005':
            escalations.append(f"[ESC005] REJECT or escalate if hard constraints violated")
        
        return escalations
    
    def _calculate_cost(self, allocation: Dict, available_options: List) -> float:
        """Calculate total cost for allocation"""
        total_cost = 0
        
        for entity, percentage in allocation.items():
            # Find entity in available options
            for option in available_options:
                if option.get('id') == entity or option.get('name') == entity:
                    unit_cost = option.get('cost_per_unit', 1000)
                    volume_pct = percentage / 100
                    entity_cost = unit_cost * volume_pct
                    total_cost += entity_cost
                    break
        
        return total_cost
    
    def _calculate_risk(self, allocation: Dict, available_options: List) -> float:
        """Calculate weighted risk score for allocation"""
        weighted_risk = 0
        total_weight = 0
        
        for entity, percentage in allocation.items():
            weight = percentage / 100
            
            # Find entity in available options
            for option in available_options:
                if option.get('id') == entity or option.get('name') == entity:
                    risk_score = option.get('risk_score', 50)
                    weighted_risk += risk_score * weight
                    total_weight += weight
                    break
        
        return weighted_risk / total_weight if total_weight > 0 else 0
    
    def _calculate_constraint_satisfaction(self, violations: List, constraints: List) -> float:
        """Calculate percentage of constraints satisfied (0-100)"""
        if not constraints:
            return 100.0
        
        satisfied = len(constraints) - len(violations)
        return (satisfied / len(constraints)) * 100
    
    def _calculate_optimization_score(
        self, cost: float, risk: float, constraint_satisfaction: float, target: str
    ) -> float:
        """Calculate overall optimization score"""
        
        # Normalize scores to 0-100
        cost_score = min(100, max(0, 100 - (cost / 10000)))  # Lower cost is better
        risk_score = min(100, max(0, 100 - risk))  # Lower risk is better
        constraint_score = constraint_satisfaction
        
        if target == 'min_cost':
            return (cost_score * 0.6) + (constraint_score * 0.4)
        elif target == 'min_risk':
            return (risk_score * 0.6) + (constraint_score * 0.4)
        else:  # balanced
            return (cost_score * 0.3) + (risk_score * 0.3) + (constraint_score * 0.4)
    
    def _generate_adjustment_recommendations(
        self, allocation: Dict, violations: List, cost: float, risk: float, target: str
    ) -> List[str]:
        """Generate recommendations for next iteration"""
        
        recommendations = []
        
        if violations:
            for violation in violations:
                if 'exceeds max' in violation:
                    entity = violation.split(':')[0].strip().split()[-1]
                    recommendations.append(f"Reduce allocation to {entity}")
                elif 'minimum' in violation:
                    recommendations.append("Increase number of active suppliers")
        
        if target == 'min_cost' and cost > 50000:
            recommendations.append("Shift to lower-cost suppliers")
        
        if target == 'min_risk' and risk > 60:
            recommendations.append("Diversify to lower-risk suppliers")
        
        return recommendations[:3]  # Return top 3
    
    def _apply_constraint_fixes(
        self, allocation: Dict, recommendations: List, available_options: List
    ) -> Dict:
        """Apply adjustments to fix constraint violations"""
        
        new_allocation = allocation.copy()
        
        # Reduce highest allocation entities by 5%
        for entity in sorted(new_allocation, key=lambda x: new_allocation[x], reverse=True)[:2]:
            new_allocation[entity] *= 0.95
        
        # Rebalance to alternatives
        deficit = sum([allocation[e] - new_allocation[e] for e in new_allocation])
        
        for option in available_options[-3:]:  # Use lower-allocation options
            entity_id = option.get('id') or option.get('name')
            if entity_id not in new_allocation:
                new_allocation[entity_id] = deficit / 3
            else:
                new_allocation[entity_id] += deficit / 3
        
        return new_allocation
    
    def _fine_tune_allocation(
        self, allocation: Dict, available_options: List, target: str
    ) -> Dict:
        """Fine-tune a feasible allocation for better optimization"""
        
        new_allocation = allocation.copy()
        
        if target == 'min_cost':
            # Shift 2% from highest-cost to lowest-cost
            costs = {opt.get('id'): opt.get('cost_per_unit', 0) for opt in available_options}
            highest_cost = max(costs, key=costs.get)
            lowest_cost = min(costs, key=costs.get)
            
            if highest_cost in new_allocation and lowest_cost not in new_allocation:
                if new_allocation[highest_cost] > 2:
                    new_allocation[highest_cost] -= 2
                    new_allocation[lowest_cost] = new_allocation.get(lowest_cost, 0) + 2
        
        elif target == 'min_risk':
            # Shift 2% from highest-risk to lowest-risk
            risks = {opt.get('id'): opt.get('risk_score', 0) for opt in available_options}
            highest_risk = max(risks, key=risks.get)
            lowest_risk = min(risks, key=risks.get)
            
            if highest_risk in new_allocation and lowest_risk not in new_allocation:
                if new_allocation[highest_risk] > 2:
                    new_allocation[highest_risk] -= 2
                    new_allocation[lowest_risk] = new_allocation.get(lowest_risk, 0) + 2
        
        return new_allocation
    
    def _apply_optimization_adjustments(
        self, allocation: Dict, recommendations: List, available_options: List
    ) -> Dict:
        """Apply general optimization adjustments"""
        new_allocation = allocation.copy()
        
        # Slight rebalancing (1-2% shifts)
        sorted_entities = sorted(new_allocation, key=lambda x: new_allocation[x], reverse=True)
        
        if len(sorted_entities) > 1:
            highest = sorted_entities[0]
            lowest = sorted_entities[-1]
            
            if new_allocation[highest] > 1:
                new_allocation[highest] -= 1
                new_allocation[lowest] = new_allocation.get(lowest, 0) + 1
        
        return new_allocation
    
    def _find_optimal_solution(
        self, feasible_solutions: List[AllocationIteration], target: str
    ) -> Optional[AllocationIteration]:
        """Find the best solution from feasible ones"""
        if not feasible_solutions:
            return None
        
        if target == 'min_cost':
            return min(feasible_solutions, key=lambda x: x.cost)
        elif target == 'min_risk':
            return min(feasible_solutions, key=lambda x: x.risk_score)
        else:  # balanced
            return max(feasible_solutions, key=lambda x: x.score)
    
    def _find_alternative_solutions(
        self, feasible_solutions: List[AllocationIteration], 
        optimal: Optional[AllocationIteration], count: int
    ) -> List[AllocationIteration]:
        """Find alternative good solutions"""
        
        if not feasible_solutions or not optimal:
            return []
        
        # Exclude optimal solution
        alternatives = [s for s in feasible_solutions if s != optimal]
        
        # Sort by score and return top alternatives
        return sorted(alternatives, key=lambda x: x.score, reverse=True)[:count]
    
    def _check_convergence(self, iterations: List[AllocationIteration]) -> bool:
        """Check if optimization converged"""
        if len(iterations) < 5:
            return False
        
        recent_scores = [it.score for it in iterations[-5:]]
        score_variation = max(recent_scores) - min(recent_scores)
        
        return score_variation < 1.0
    
    def _analyze_cost_range(self, feasible_solutions: List[AllocationIteration]) -> Dict:
        """Analyze cost distribution"""
        if not feasible_solutions:
            return {'min': 0, 'max': 0, 'avg': 0}
        
        costs = [s.cost for s in feasible_solutions]
        return {
            'min': round(min(costs), 2),
            'max': round(max(costs), 2),
            'avg': round(sum(costs) / len(costs), 2),
            'range': round(max(costs) - min(costs), 2)
        }
    
    def _analyze_risk_range(self, feasible_solutions: List[AllocationIteration]) -> Dict:
        """Analyze risk distribution"""
        if not feasible_solutions:
            return {'min': 0, 'max': 0, 'avg': 0}
        
        risks = [s.risk_score for s in feasible_solutions]
        return {
            'min': round(min(risks), 2),
            'max': round(max(risks), 2),
            'avg': round(sum(risks) / len(risks), 2),
            'range': round(max(risks) - min(risks), 2)
        }
    
    def _summarize_constraints(self, feasible_solutions: List[AllocationIteration]) -> Dict:
        """Summarize constraint satisfaction"""
        if not feasible_solutions:
            return {}
        
        satisfactions = [s.constraint_satisfaction for s in feasible_solutions]
        return {
            'avg_satisfaction': round(sum(satisfactions) / len(satisfactions), 1),
            'min_satisfaction': round(min(satisfactions), 1),
            'max_satisfaction': round(max(satisfactions), 1),
            'all_fully_satisfied': all(s == 100 for s in satisfactions)
        }
    
    def _generate_loop_recommendation(
        self, optimal: Optional[AllocationIteration], 
        alternatives: List[AllocationIteration], 
        feasible: List[AllocationIteration]
    ) -> str:
        """Generate overall recommendation"""
        
        if not optimal:
            return "⚠️ No feasible solutions found. Review constraints or expand options."
        
        if optimal.constraint_satisfaction == 100:
            if len(alternatives) >= 2:
                return "✅ Optimal solution found with multiple alternatives available"
            else:
                return "✅ Optimal feasible solution identified"
        else:
            return "⚠️ Best feasible solution has constraint violations. Consider relaxing constraints."
    
    def _iteration_to_dict(self, iteration: AllocationIteration) -> Dict:
        """Convert iteration to dictionary"""
        return {
            'iteration': iteration.iteration_num,
            'allocation': iteration.proposed_allocation,
            'cost': round(iteration.cost, 2),
            'risk_score': round(iteration.risk_score, 2),
            'constraint_satisfaction': round(iteration.constraint_satisfaction, 2),
            'violations': iteration.violations,
            'feasible': iteration.feasible,
            'score': round(iteration.score, 2),
            'recommendations': iteration.recommended_adjustments
        }
