"""
Rule Engine Agent
Evaluates specific procurement rules with detailed analysis
"""

import sys
from pathlib import Path
from typing import Dict, Any
import json
import pandas as pd

root_path = Path(__file__).parent.parent.parent.parent
if str(root_path) not in sys.path:
    sys.path.insert(0, str(root_path))

from backend.agents.base_agent import BaseAgent
from backend.engines.data_loader import DataLoader


class RuleEngineAgent(BaseAgent):
    """
    Agent for evaluating specific procurement rules
    
    Input:
        - rule_id: str (e.g., 'HC001', 'SP001')
        - client_id: str
        - category: str (optional)
        - supplier_id: str (optional)
        
    Output:
        - rule_status: str (PASS/FAIL/WARNING)
        - rule_details: Dict
        - current_situation: Dict
        - gap_analysis: Dict
        - recommendation: str
    """
    
    def __init__(self):
        super().__init__(
            name="RuleEngine",
            description="Evaluates specific procurement rules with detailed analysis"
        )
        self.data_loader = DataLoader()
        
        # Load rule book
        rule_book_path = Path(__file__).parent.parent.parent.parent / 'rules' / 'rule_book.json'
        with open(rule_book_path, 'r') as f:
            self.rule_book = json.load(f)
    
    def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute rule evaluation
        """
        try:
            rule_id = input_data.get('rule_id')
            client_id = input_data.get('client_id')
            
            if not rule_id or not client_id:
                return self._create_response(
                    success=False,
                    error="rule_id and client_id are required"
                )
            
            self._log(f"Evaluating rule {rule_id} for client {client_id}")
            
            # Find the rule
            rule = self._find_rule(rule_id)
            if not rule:
                return self._create_response(
                    success=False,
                    error=f"Rule {rule_id} not found in rule book"
                )
            
            # Load data
            spend_df = self.data_loader.load_spend_data()
            supplier_df = self.data_loader.load_supplier_master()
            
            # Filter by client
            client_spend = spend_df[spend_df['Client_ID'] == client_id]
            
            if input_data.get('category'):
                client_spend = client_spend[client_spend['Category'] == input_data['category']]
            
            if client_spend.empty:
                return self._create_response(
                    success=False,
                    error="No spend data found for this client"
                )
            
            # Evaluate the rule based on its ID
            if rule_id.startswith('HC'):  # Hard Constraint
                result = self._evaluate_hard_constraint(rule, client_spend, supplier_df, input_data)
            elif rule_id.startswith('SP'):  # Soft Preference
                result = self._evaluate_soft_preference(rule, client_spend, supplier_df, input_data)
            elif rule_id.startswith('RA'):  # Risk Assessment
                result = self._evaluate_risk_assessment(rule, client_spend, supplier_df, input_data)
            else:
                result = self._create_response(
                    success=False,
                    error=f"Unknown rule type for {rule_id}"
                )
            
            return result
            
        except Exception as e:
            self._log(f"Error evaluating rule: {str(e)}", "ERROR")
            return self._create_response(
                success=False,
                error=str(e)
            )
    
    def _find_rule(self, rule_id: str) -> Dict[str, Any]:
        """Find a rule in the rule book"""
        for category in ['hard_constraints', 'soft_preferences', 'risk_assessment_rules']:
            if category in self.rule_book:
                for rule in self.rule_book[category].get('rules', []):
                    if rule.get('rule_id') == rule_id:
                        return rule
        return None
    
    def _evaluate_hard_constraint(self, rule: Dict, client_spend: pd.DataFrame, supplier_df: pd.DataFrame, input_data: Dict) -> Dict[str, Any]:
        """Evaluate a hard constraint rule"""
        rule_id = rule['rule_id']
        
        # HC001: Mandatory Food Safety Certification
        if rule_id == 'HC001':
            return self._evaluate_food_safety_cert(rule, client_spend, supplier_df)
        
        # HC002: Minimum Quality Rating
        elif rule_id == 'HC002':
            return self._evaluate_quality_rating(rule, client_spend, supplier_df)
        
        # HC003: Minimum Delivery Reliability
        elif rule_id == 'HC003':
            return self._evaluate_delivery_reliability(rule, client_spend, supplier_df)
        
        # Default evaluation
        else:
            return self._create_response(
                success=True,
                data={
                    'rule_id': rule_id,
                    'rule_name': rule.get('name', ''),
                    'status': 'NOT_IMPLEMENTED',
                    'message': f"Evaluation logic for {rule_id} not yet implemented"
                }
            )
    
    def _evaluate_food_safety_cert(self, rule: Dict, client_spend: pd.DataFrame, supplier_df: pd.DataFrame) -> Dict[str, Any]:
        """Evaluate HC001: Food Safety Certification"""
        required_certs = ['ISO 22000', 'HACCP']
        
        violations = []
        compliant = []
        
        for supplier_id in client_spend['Supplier_ID'].unique():
            supplier = supplier_df[supplier_df['supplier_id'] == supplier_id]
            if not supplier.empty:
                supplier = supplier.iloc[0]
                certs = supplier['certifications'].split('|') if pd.notna(supplier['certifications']) else []
                
                has_required_cert = any(req_cert in certs for req_cert in required_certs)
                
                supplier_spend = client_spend[client_spend['Supplier_ID'] == supplier_id]['Spend_USD'].sum()
                
                if not has_required_cert:
                    violations.append({
                        'supplier_id': supplier_id,
                        'supplier_name': supplier['supplier_name'],
                        'certifications': certs,
                        'spend': round(supplier_spend, 2),
                        'issue': f"Missing required certification (needs {' or '.join(required_certs)})"
                    })
                else:
                    compliant.append({
                        'supplier_id': supplier_id,
                        'supplier_name': supplier['supplier_name'],
                        'certifications': certs,
                        'spend': round(supplier_spend, 2)
                    })
        
        total_spend = client_spend['Spend_USD'].sum()
        violation_spend = sum(v['spend'] for v in violations)
        
        status = 'FAIL' if violations else 'PASS'
        
        result = {
            'rule_id': 'HC001',
            'rule_name': rule['name'],
            'rule_description': rule['condition'],
            'status': status,
            'violations': violations,
            'compliant_suppliers': compliant,
            'violation_count': len(violations),
            'compliant_count': len(compliant),
            'total_spend': round(total_spend, 2),
            'violation_spend': round(violation_spend, 2),
            'violation_spend_percentage': round((violation_spend / total_spend * 100) if total_spend > 0 else 0, 2),
            'recommendation': self._generate_recommendation_hc001(violations, total_spend) if violations else "✅ All suppliers have required food safety certifications"
        }
        
        self._log(f"HC001 evaluation: {status} - {len(violations)} violations")
        
        return self._create_response(
            success=True,
            data=result,
            sources=['supplier_master.csv', 'spend_data.csv', 'rule_book.json']
        )
    
    def _generate_recommendation_hc001(self, violations: list, total_spend: float) -> str:
        """Generate recommendation for HC001 violations"""
        violation_spend = sum(v['spend'] for v in violations)
        
        rec = f"⚠️ CRITICAL: {len(violations)} supplier(s) lack required food safety certifications\n\n"
        rec += f"Impact: ${violation_spend:,.0f} ({violation_spend/total_spend*100:.1f}% of spend) at risk\n\n"
        rec += "IMMEDIATE ACTIONS REQUIRED:\n"
        
        for i, v in enumerate(violations, 1):
            rec += f"{i}. {v['supplier_name']}: Request ISO 22000 or HACCP certification within 30 days\n"
            rec += f"   Current spend: ${v['spend']:,.0f}\n"
            rec += f"   Alternative: Source from certified suppliers\n\n"
        
        return rec
    
    def _evaluate_quality_rating(self, rule: Dict, client_spend: pd.DataFrame, supplier_df: pd.DataFrame) -> Dict[str, Any]:
        """Evaluate HC002: Minimum Quality Rating"""
        min_rating = 4.0
        
        violations = []
        compliant = []
        
        for supplier_id in client_spend['Supplier_ID'].unique():
            supplier = supplier_df[supplier_df['supplier_id'] == supplier_id]
            if not supplier.empty:
                supplier = supplier.iloc[0]
                quality_rating = supplier['quality_rating']
                supplier_spend = client_spend[client_spend['Supplier_ID'] == supplier_id]['Spend_USD'].sum()
                
                if quality_rating < min_rating:
                    gap = min_rating - quality_rating
                    violations.append({
                        'supplier_id': supplier_id,
                        'supplier_name': supplier['supplier_name'],
                        'quality_rating': quality_rating,
                        'required_rating': min_rating,
                        'gap': round(gap, 2),
                        'spend': round(supplier_spend, 2),
                        'issue': f"Quality rating {quality_rating} below minimum {min_rating}"
                    })
                else:
                    compliant.append({
                        'supplier_id': supplier_id,
                        'supplier_name': supplier['supplier_name'],
                        'quality_rating': quality_rating,
                        'spend': round(supplier_spend, 2)
                    })
        
        total_spend = client_spend['Spend_USD'].sum()
        violation_spend = sum(v['spend'] for v in violations)
        
        status = 'FAIL' if violations else 'PASS'
        
        result = {
            'rule_id': 'HC002',
            'rule_name': rule['name'],
            'status': status,
            'violations': violations,
            'compliant_suppliers': compliant,
            'total_spend': round(total_spend, 2),
            'violation_spend': round(violation_spend, 2),
            'recommendation': f"⚠️ {len(violations)} supplier(s) below minimum quality rating - consider alternatives or quality improvement plans" if violations else "✅ All suppliers meet minimum quality standards"
        }
        
        return self._create_response(
            success=True,
            data=result,
            sources=['supplier_master.csv', 'spend_data.csv']
        )
    
    def _evaluate_delivery_reliability(self, rule: Dict, client_spend: pd.DataFrame, supplier_df: pd.DataFrame) -> Dict[str, Any]:
        """Evaluate HC003: Minimum Delivery Reliability"""
        min_reliability = 90
        
        violations = []
        compliant = []
        
        for supplier_id in client_spend['Supplier_ID'].unique():
            supplier = supplier_df[supplier_df['supplier_id'] == supplier_id]
            if not supplier.empty:
                supplier = supplier.iloc[0]
                delivery_reliability = supplier['delivery_reliability_pct']
                supplier_spend = client_spend[client_spend['Supplier_ID'] == supplier_id]['Spend_USD'].sum()
                
                if delivery_reliability < min_reliability:
                    gap = min_reliability - delivery_reliability
                    violations.append({
                        'supplier_id': supplier_id,
                        'supplier_name': supplier['supplier_name'],
                        'delivery_reliability': delivery_reliability,
                        'required_reliability': min_reliability,
                        'gap': round(gap, 2),
                        'spend': round(supplier_spend, 2),
                        'issue': f"Delivery reliability {delivery_reliability}% below minimum {min_reliability}%"
                    })
                else:
                    compliant.append({
                        'supplier_id': supplier_id,
                        'supplier_name': supplier['supplier_name'],
                        'delivery_reliability': delivery_reliability,
                        'spend': round(supplier_spend, 2)
                    })
        
        total_spend = client_spend['Spend_USD'].sum()
        violation_spend = sum(v['spend'] for v in violations)
        
        status = 'FAIL' if violations else 'PASS'
        
        result = {
            'rule_id': 'HC003',
            'rule_name': rule['name'],
            'status': status,
            'violations': violations,
            'compliant_suppliers': compliant,
            'total_spend': round(total_spend, 2),
            'violation_spend': round(violation_spend, 2),
            'recommendation': f"⚠️ {len(violations)} supplier(s) below minimum delivery reliability - negotiate SLAs or find alternatives" if violations else "✅ All suppliers meet delivery reliability standards"
        }
        
        return self._create_response(
            success=True,
            data=result,
            sources=['supplier_master.csv', 'spend_data.csv']
        )
    
    def _evaluate_soft_preference(self, rule: Dict, client_spend: pd.DataFrame, supplier_df: pd.DataFrame, input_data: Dict) -> Dict[str, Any]:
        """Evaluate soft preference rules"""
        return self._create_response(
            success=True,
            data={
                'rule_id': rule['rule_id'],
                'rule_name': rule.get('name', ''),
                'status': 'NOT_IMPLEMENTED',
                'message': "Soft preference evaluation not yet implemented"
            }
        )
    
    def _evaluate_risk_assessment(self, rule: Dict, client_spend: pd.DataFrame, supplier_df: pd.DataFrame, input_data: Dict) -> Dict[str, Any]:
        """Evaluate risk assessment rules"""
        return self._create_response(
            success=True,
            data={
                'rule_id': rule['rule_id'],
                'rule_name': rule.get('name', ''),
                'status': 'NOT_IMPLEMENTED',
                'message': "Risk assessment evaluation not yet implemented"
            }
        )
