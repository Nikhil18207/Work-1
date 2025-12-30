"""
Action Plan Generator Agent
Creates specific, actionable step-by-step plans
"""

import sys
from pathlib import Path
from typing import Dict, Any, List
from datetime import datetime, timedelta

root_path = Path(__file__).parent.parent.parent.parent
if str(root_path) not in sys.path:
    sys.path.insert(0, str(root_path))

from backend.agents.base_agent import BaseAgent


class ActionPlanGeneratorAgent(BaseAgent):
    """
    Agent for generating actionable plans
    
    Input:
        - scenario: str
        - analysis_results: Dict (from other agents)
        - timeline_weeks: int (optional)
        
    Output:
        - action_plan: List[Dict] (steps with timeline)
        - milestones: List[Dict]
        - expected_outcomes: Dict
    """
    
    def __init__(self):
        super().__init__(
            name="ActionPlanGenerator",
            description="Generates specific, actionable step-by-step plans"
        )
    
    def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute action plan generation
        """
        try:
            scenario = input_data.get('scenario', 'general')
            analysis_results = input_data.get('analysis_results', {})
            timeline_weeks = input_data.get('timeline_weeks', 12)
            
            self._log(f"Generating action plan for scenario: {scenario}")
            
            # Generate plan based on scenario
            if scenario == 'price_negotiation':
                plan = self._generate_price_negotiation_plan(analysis_results, timeline_weeks)
            elif scenario == 'supplier_consolidation':
                plan = self._generate_supplier_consolidation_plan(analysis_results, timeline_weeks)
            elif scenario == 'risk_mitigation':
                plan = self._generate_risk_mitigation_plan(analysis_results, timeline_weeks)
            elif scenario == 'rule_violation_fix':
                plan = self._generate_rule_violation_plan(analysis_results, timeline_weeks)
            else:
                plan = self._generate_general_plan(analysis_results, timeline_weeks)
            
            self._log(f"Action plan generated: {len(plan['steps'])} steps")
            
            return self._create_response(
                success=True,
                data=plan,
                sources=['best_practices_database']
            )
            
        except Exception as e:
            self._log(f"Error generating action plan: {str(e)}", "ERROR")
            return self._create_response(
                success=False,
                error=str(e)
            )
    
    def _generate_price_negotiation_plan(self, analysis: Dict, timeline_weeks: int) -> Dict[str, Any]:
        """Generate plan for price negotiation"""
        
        start_date = datetime.now()
        
        steps = [
            {
                'step': 1,
                'action': 'Gather market intelligence and pricing data',
                'description': 'Collect current market prices, competitor quotes, and industry benchmarks',
                'owner': 'Procurement Analyst',
                'timeline': 'Week 1',
                'due_date': (start_date + timedelta(weeks=1)).strftime('%Y-%m-%d'),
                'deliverable': 'Market pricing report with 3+ data sources'
            },
            {
                'step': 2,
                'action': 'Analyze current spend and identify savings potential',
                'description': 'Calculate exact savings opportunity and build business case',
                'owner': 'Procurement Manager',
                'timeline': 'Week 2',
                'due_date': (start_date + timedelta(weeks=2)).strftime('%Y-%m-%d'),
                'deliverable': 'Savings analysis document'
            },
            {
                'step': 3,
                'action': 'Prepare negotiation strategy and talking points',
                'description': 'Develop negotiation approach, fallback positions, and alternatives',
                'owner': 'Category Manager',
                'timeline': 'Week 3',
                'due_date': (start_date + timedelta(weeks=3)).strftime('%Y-%m-%d'),
                'deliverable': 'Negotiation playbook'
            },
            {
                'step': 4,
                'action': 'Schedule and conduct supplier negotiation meeting',
                'description': 'Present market data, request price reduction, discuss terms',
                'owner': 'Procurement Manager',
                'timeline': 'Week 4',
                'due_date': (start_date + timedelta(weeks=4)).strftime('%Y-%m-%d'),
                'deliverable': 'Meeting notes and initial supplier response'
            },
            {
                'step': 5,
                'action': 'Evaluate supplier response and counter-offer if needed',
                'description': 'Review supplier proposal, compare to targets, negotiate further',
                'owner': 'Category Manager',
                'timeline': 'Week 5-6',
                'due_date': (start_date + timedelta(weeks=6)).strftime('%Y-%m-%d'),
                'deliverable': 'Final negotiated terms'
            },
            {
                'step': 6,
                'action': 'Finalize contract amendments and implement new pricing',
                'description': 'Update contracts, communicate changes, monitor implementation',
                'owner': 'Procurement Manager',
                'timeline': 'Week 7-8',
                'due_date': (start_date + timedelta(weeks=8)).strftime('%Y-%m-%d'),
                'deliverable': 'Signed contract amendment'
            }
        ]
        
        milestones = [
            {'milestone': 'Market data collected', 'week': 1},
            {'milestone': 'Business case approved', 'week': 2},
            {'milestone': 'Negotiation completed', 'week': 6},
            {'milestone': 'New pricing implemented', 'week': 8}
        ]
        
        expected_outcomes = {
            'cost_savings': analysis.get('potential_savings', 'TBD'),
            'timeline': f"{timeline_weeks} weeks",
            'success_probability': '75-85%',
            'key_risks': [
                'Supplier may not agree to full price reduction',
                'May require volume commitments',
                'Contract renegotiation delays'
            ]
        }
        
        return {
            'scenario': 'price_negotiation',
            'steps': steps,
            'total_steps': len(steps),
            'milestones': milestones,
            'expected_outcomes': expected_outcomes,
            'timeline_weeks': timeline_weeks
        }
    
    def _generate_supplier_consolidation_plan(self, analysis: Dict, timeline_weeks: int) -> Dict[str, Any]:
        """Generate plan for supplier consolidation"""
        
        start_date = datetime.now()
        
        steps = [
            {
                'step': 1,
                'action': 'Analyze current supplier base and performance',
                'description': 'Evaluate all suppliers on quality, delivery, cost, and risk',
                'owner': 'Procurement Team',
                'timeline': 'Week 1-2',
                'due_date': (start_date + timedelta(weeks=2)).strftime('%Y-%m-%d'),
                'deliverable': 'Supplier scorecard and ranking'
            },
            {
                'step': 2,
                'action': 'Identify consolidation opportunities',
                'description': 'Determine which suppliers to retain, expand, or phase out',
                'owner': 'Category Manager',
                'timeline': 'Week 3',
                'due_date': (start_date + timedelta(weeks=3)).strftime('%Y-%m-%d'),
                'deliverable': 'Consolidation strategy document'
            },
            {
                'step': 3,
                'action': 'Negotiate volume increases with retained suppliers',
                'description': 'Discuss increased volumes and request volume discounts',
                'owner': 'Procurement Manager',
                'timeline': 'Week 4-6',
                'due_date': (start_date + timedelta(weeks=6)).strftime('%Y-%m-%d'),
                'deliverable': 'Negotiated volume agreements'
            },
            {
                'step': 4,
                'action': 'Develop transition plan for supplier exits',
                'description': 'Plan orderly wind-down of relationships with exited suppliers',
                'owner': 'Procurement Analyst',
                'timeline': 'Week 7',
                'due_date': (start_date + timedelta(weeks=7)).strftime('%Y-%m-%d'),
                'deliverable': 'Transition timeline and communication plan'
            },
            {
                'step': 5,
                'action': 'Execute gradual volume shift',
                'description': 'Incrementally move volume from exited to retained suppliers',
                'owner': 'Procurement Team',
                'timeline': 'Week 8-12',
                'due_date': (start_date + timedelta(weeks=12)).strftime('%Y-%m-%d'),
                'deliverable': 'Completed volume transfers'
            },
            {
                'step': 6,
                'action': 'Monitor performance and validate savings',
                'description': 'Track KPIs, measure savings, address any issues',
                'owner': 'Category Manager',
                'timeline': 'Week 13+',
                'due_date': (start_date + timedelta(weeks=16)).strftime('%Y-%m-%d'),
                'deliverable': 'Post-implementation review'
            }
        ]
        
        milestones = [
            {'milestone': 'Consolidation strategy approved', 'week': 3},
            {'milestone': 'Volume agreements signed', 'week': 6},
            {'milestone': 'Transition 50% complete', 'week': 10},
            {'milestone': 'Consolidation complete', 'week': 12}
        ]
        
        expected_outcomes = {
            'cost_savings': analysis.get('potential_savings', 'TBD'),
            'supplier_reduction': f"{analysis.get('current_suppliers', 'X')} → {analysis.get('target_suppliers', 'Y')} suppliers",
            'timeline': f"{timeline_weeks} weeks",
            'success_probability': '70-80%'
        }
        
        return {
            'scenario': 'supplier_consolidation',
            'steps': steps,
            'total_steps': len(steps),
            'milestones': milestones,
            'expected_outcomes': expected_outcomes,
            'timeline_weeks': timeline_weeks
        }
    
    def _generate_risk_mitigation_plan(self, analysis: Dict, timeline_weeks: int) -> Dict[str, Any]:
        """Generate plan for risk mitigation"""
        
        steps = [
            {
                'step': 1,
                'action': 'Identify and assess all procurement risks',
                'description': 'Comprehensive risk assessment across suppliers, regions, categories',
                'timeline': 'Week 1-2'
            },
            {
                'step': 2,
                'action': 'Develop risk mitigation strategies',
                'description': 'Create specific plans for each identified risk',
                'timeline': 'Week 3-4'
            },
            {
                'step': 3,
                'action': 'Implement risk controls and monitoring',
                'description': 'Put mitigation measures in place and track effectiveness',
                'timeline': 'Week 5+'
            }
        ]
        
        return {
            'scenario': 'risk_mitigation',
            'steps': steps,
            'total_steps': len(steps),
            'timeline_weeks': timeline_weeks
        }
    
    def _generate_rule_violation_plan(self, analysis: Dict, timeline_weeks: int) -> Dict[str, Any]:
        """Generate plan to fix rule violations"""
        
        violations = analysis.get('violations', [])
        
        steps = []
        for i, violation in enumerate(violations, 1):
            steps.append({
                'step': i,
                'action': f"Address {violation.get('rule_name', 'violation')}",
                'description': violation.get('action_required', 'Fix violation'),
                'timeline': f"Week {i}",
                'priority': violation.get('severity', 'MEDIUM')
            })
        
        return {
            'scenario': 'rule_violation_fix',
            'steps': steps,
            'total_steps': len(steps),
            'timeline_weeks': timeline_weeks
        }
    
    def _generate_general_plan(self, analysis: Dict, timeline_weeks: int) -> Dict[str, Any]:
        """Generate general action plan"""
        
        steps = [
            {
                'step': 1,
                'action': 'Analyze current situation',
                'description': 'Gather data and understand current state',
                'timeline': 'Week 1-2'
            },
            {
                'step': 2,
                'action': 'Develop improvement strategy',
                'description': 'Create plan based on analysis',
                'timeline': 'Week 3-4'
            },
            {
                'step': 3,
                'action': 'Implement improvements',
                'description': 'Execute the plan',
                'timeline': 'Week 5+'
            }
        ]
        
        return {
            'scenario': 'general',
            'steps': steps,
            'total_steps': len(steps),
            'timeline_weeks': timeline_weeks
        }
