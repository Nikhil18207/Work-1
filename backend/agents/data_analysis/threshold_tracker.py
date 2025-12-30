"""
Threshold Tracker Agent
Tracks rule thresholds and proximity to limits using comprehensive rule evaluation
"""

import sys
from pathlib import Path
from typing import Dict, Any

root_path = Path(__file__).parent.parent.parent.parent
if str(root_path) not in sys.path:
    sys.path.insert(0, str(root_path))

from backend.agents.base_agent import BaseAgent
from backend.engines.rule_evaluation_engine import RuleEvaluationEngine


class ThresholdTrackerAgent(BaseAgent):
    """
    Agent for tracking rule thresholds using comprehensive rule evaluation
    
    Input:
        - client_id: str
        - category: str (optional)
        
    Output:
        - threshold_status: List[Dict] (all thresholds and their status)
        - violations: List[Dict] (thresholds exceeded)
        - warnings: List[Dict] (close to thresholds)
    """
    
    def __init__(self):
        super().__init__(
            name="ThresholdTracker",
            description="Tracks procurement rule thresholds and violations"
        )
        self.rule_engine = RuleEvaluationEngine()
    
    def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute threshold tracking using comprehensive rule evaluation
        """
        try:
            self._log(f"Tracking thresholds: {input_data}")
            
            if not input_data.get('client_id'):
                return self._create_response(
                    success=False,
                    error="client_id is required"
                )
            
            # Use comprehensive rule evaluation engine
            results = self.rule_engine.evaluate_all_rules(
                client_id=input_data['client_id'],
                category=input_data.get('category')
            )
            
            if not results['success']:
                return self._create_response(
                    success=False,
                    error=results.get('error', 'Rule evaluation failed')
                )
            
            # Transform results to match expected format
            violations = results['violations']
            warnings = results['warnings']
            compliant = results['compliant']
            
            # Combine all checks
            threshold_checks = violations + warnings + compliant
            
            result = {
                'total_checks': len(threshold_checks),
                'violations_count': len(violations),
                'warnings_count': len(warnings),
                'ok_count': len(compliant),
                'threshold_checks': threshold_checks,
                'violations': violations,
                'warnings': warnings,
                'compliant': compliant,
                'overall_status': results['summary']['overall_status'],
                'total_spend': results['total_spend'],
                'supplier_count': results['supplier_count']
            }
            
            self._log(f"Threshold tracking complete: {len(violations)} violations, {len(warnings)} warnings")
            
            return self._create_response(
                success=True,
                data=result,
                sources=['spend_data.csv', 'rule_book.csv']
            )
            
        except Exception as e:
            self._log(f"Error in threshold tracking: {str(e)}", "ERROR")
            return self._create_response(
                success=False,
                error=str(e)
            )
