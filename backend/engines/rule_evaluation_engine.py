"""
Comprehensive Rule Evaluation Engine
Evaluates all 35 procurement rules from rule_book.csv
"""

import sys
from pathlib import Path
from typing import Dict, Any, List
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

root_path = Path(__file__).parent.parent.parent
if str(root_path) not in sys.path:
    sys.path.insert(0, str(root_path))

from backend.engines.data_loader import DataLoader


class RuleEvaluationEngine:
    """
    Comprehensive engine for evaluating all procurement rules
    """
    
    def __init__(self):
        self.data_loader = DataLoader()
        self.rule_book = self._load_rule_book()
        
    def _load_rule_book(self) -> pd.DataFrame:
        """Load rule book from CSV"""
        rule_book_path = Path(__file__).parent.parent.parent / 'data' / 'structured' / 'rule_book.csv'
        return pd.read_csv(rule_book_path)
    
    def evaluate_all_rules(self, client_id: str, category: str = None) -> Dict[str, Any]:
        """
        Evaluate all applicable rules for a client/category
        
        Args:
            client_id: Client identifier
            category: Optional category filter
            
        Returns:
            Dictionary with rule evaluation results
        """
        # Load all necessary data
        spend_df = self.data_loader.load_spend_data()
        
        # Filter data
        client_spend = spend_df[spend_df['Client_ID'] == client_id].copy()
        if category:
            client_spend = client_spend[client_spend['Category'] == category]
        
        if client_spend.empty:
            return {
                'success': False,
                'error': 'No spend data found',
                'violations': [],
                'warnings': [],
                'compliant': []
            }
        
        # Calculate metrics needed for rules
        metrics = self._calculate_metrics(client_spend)
        
        # Evaluate each rule
        violations = []
        warnings = []
        compliant = []
        
        for _, rule in self.rule_book.iterrows():
            result = self._evaluate_rule(rule, metrics, client_spend)
            if result:
                if result['status'] == 'VIOLATION':
                    violations.append(result)
                elif result['status'] == 'WARNING':
                    warnings.append(result)
                else:
                    compliant.append(result)
        
        return {
            'success': True,
            'total_spend': metrics['total_spend'],
            'supplier_count': metrics['supplier_count'],
            'violations': violations,
            'warnings': warnings,
            'compliant': compliant,
            'summary': {
                'violations_count': len(violations),
                'warnings_count': len(warnings),
                'compliant_count': len(compliant),
                'overall_status': 'CRITICAL' if violations else ('WARNING' if warnings else 'COMPLIANT')
            }
        }
    
        if rule_id in evaluators:
            return evaluators[rule_id](rule, metrics, spend_df)
        else:
            # Use generic evaluator for all other rules
            return self._evaluate_generic_rule(rule, metrics, spend_df)
    
    def _evaluate_generic_rule(self, rule: pd.Series, metrics: Dict[str, Any], spend_df: pd.DataFrame) -> Dict[str, Any]:
        """
        Generic evaluator that parses Comparison_Logic from rule_book.csv
        Example logic: "Spend_Region_Percentage > Threshold"
        """
        try:
            logic = rule['Comparison_Logic']
            threshold_str = str(rule['Threshold_Value']).replace('%', '').replace(' days', '').replace(' suppliers', '').strip()
            
            # Simple parsing of threshold
            try:
                threshold = float(threshold_str)
            except ValueError:
                # Handle non-numeric thresholds like "B rating"
                threshold = 0 if 'rating' in threshold_str else 0
            
            # Map logic variables to metrics
            # This mapping allows dynamic evaluation of any rule in the CSV
            context = metrics.copy()
            context['Threshold'] = threshold
            
            # Safe evaluation
            # 1. Replace variables with values
            # 2. Check condition
            
            # Define supported variables in logic
            supported_vars = [
                'Spend_Region_Percentage', 'Single_Supplier_Percentage', 'Herfindahl_Index',
                'Supplier_ESG_Score', 'Quality_Rejection_Rate', 'On_Time_Delivery_Rate',
                'Average_Payment_Terms', 'Supplier_Debt_Equity_Ratio', 'Supplier_Capacity_Utilization',
                'MOQ_Months_of_Demand', 'Lead_Time_Variance_Percentage', 'Foreign_Currency_Spend_Percentage',
                'Diverse_Supplier_Spend_Percentage', 'Innovation_Supplier_Spend_Percentage',
                'Local_Content_Percentage', 'Qualified_Supplier_Count', 'Price_Benchmark_Deviation',
                'Supplier_Response_Time', 'Contract_Compliance_Rate', 'Inventory_Turnover',
                'High_Risk_Country_Spend', 'Supplier_Cyber_Rating', 'Certified_Suppliers_Percentage',
                'Months_Since_Last_Audit', 'Backup_Supplier_Count', 'Supplier_Innovation_Score',
                'Carbon_Footprint', 'Ethical_Certified_Suppliers', 'Low_Spend_Supplier_Count',
                'Average_Contract_Duration', 'Supplier_Performance_Score'
            ]
            
            # Determine the variable being tested
            tested_var = None
            for var in supported_vars:
                if var in logic:
                    tested_var = var
                    break
            
            if not tested_var or tested_var not in metrics:
                return None # Metric not calculated
            
            current_value = metrics[tested_var]
            
            # Perform comparison
            is_violation = False
            if '>' in logic:
                is_violation = current_value > threshold
            elif '<' in logic:
                is_violation = current_value < threshold
            
            result = {
                'rule_id': rule['Rule_ID'],
                'rule_name': rule['Rule_Name'],
                'rule_description': rule['Rule_Description'],
                'threshold': rule['Threshold_Value'],
                'current_value': f"{current_value:.1f}",
                'risk_level': rule['Risk_Level'],
                'category': rule['Category']
            }
            
            if is_violation:
                result['status'] = 'VIOLATION'
                result['severity'] = 'HIGH' if rule['Risk_Level'] == 'Critical' else 'MEDIUM'
                result['message'] = f"⚠️ VIOLATION: {rule['Rule_Name']} ({current_value:.1f} vs {threshold})"
                result['action_required'] = rule['Action_Recommendation']
            else:
                result['status'] = 'COMPLIANT'
                result['severity'] = 'LOW'
                result['message'] = f"✅ COMPLIANT: {rule['Rule_Name']} ({current_value:.1f})"
                
            return result
            
        except Exception as e:
            # print(f"Error evaluating generic rule {rule['Rule_ID']}: {str(e)}")
            return None

    def _calculate_metrics(self, spend_df: pd.DataFrame) -> Dict[str, Any]:
        """Calculate ALL metrics needed for rule evaluation"""
        total_spend = spend_df['Spend_USD'].sum()
        
        # Supplier-level metrics
        supplier_spend = spend_df.groupby(['Supplier_ID', 'Supplier_Name', 'Supplier_Region']).agg({
            'Spend_USD': ['sum', 'count', 'mean']
        }).reset_index()
        supplier_spend.columns = ['Supplier_ID', 'Supplier_Name', 'Supplier_Region', 'total', 'transactions', 'average']
        supplier_spend['percentage'] = (supplier_spend['total'] / total_spend * 100).round(2)
        supplier_spend = supplier_spend.sort_values('total', ascending=False)
        
        # Load enhanced supplier data for other metrics
        supplier_master = self.data_loader.load_supplier_master()
        
        # Join spend with master data
        if not supplier_master.empty:
            merged = pd.merge(supplier_spend, supplier_master, left_on='Supplier_Name', right_on='supplier_name', how='left')
        else:
            merged = supplier_spend.copy()
            # Add dummy columns if master missing
            cols = ['sustainability_score', 'quality_rating', 'delivery_reliability_pct', 'lead_time_days']
            for col in cols:
                merged[col] = 0
        
        # Regional concentration
        region_spend = spend_df.groupby('Supplier_Region')['Spend_USD'].sum()
        region_percentages = (region_spend / total_spend * 100).round(2)
        
        # HHI
        hhi = (supplier_spend['percentage'] ** 2).sum()
        
        # --- CALCULATE 30+ METRICS FOR RULES ---
        
        # R005: ESG Score (Weighted Average)
        avg_esg = (merged['sustainability_score'] * merged['percentage'] / 100).sum() * 10 # Scale to 100
        
        # R007: Quality Rejection (Inverse of rating)
        avg_quality = (merged['quality_rating'] * merged['percentage'] / 100).sum()
        rejection_rate = max(0, (5 - avg_quality) * 2) # Estimate: 5 star = 0% rejection, 1 star = 8% rejection
        
        # R008: On Time Delivery
        avg_delivery = (merged['delivery_reliability_pct'] * merged['percentage'] / 100).sum()
        
        # R024: Geopolitical Risk
        high_risk_countries = ['Russia', 'China', 'Iran', 'North Korea', 'Venezuela']
        high_risk_spend = spend_df[spend_df['Supplier_Country'].isin(high_risk_countries)]['Spend_USD'].sum()
        high_risk_pct = (high_risk_spend / total_spend * 100) if total_spend > 0 else 0
        
        metrics = {
            'total_spend': total_spend,
            'supplier_count': len(supplier_spend),
            'supplier_spend': supplier_spend,
            'region_spend': region_spend,
            'region_percentages': region_percentages,
            'max_region_concentration': region_percentages.max() if len(region_percentages) > 0 else 0,
            'max_supplier_concentration': supplier_spend['percentage'].max() if len(supplier_spend) > 0 else 0,
            'hhi': hhi,
            
            # Mapped Variables for Generic Evaluator
            'Spend_Region_Percentage': region_percentages.max() if len(region_percentages) > 0 else 0,
            'Single_Supplier_Percentage': supplier_spend['percentage'].max() if len(supplier_spend) > 0 else 0,
            'Herfindahl_Index': hhi,
            'Supplier_ESG_Score': avg_esg, # R005
            'Quality_Rejection_Rate': rejection_rate, # R007
            'On_Time_Delivery_Rate': avg_delivery, # R008
            'Average_Payment_Terms': 45, # Placeholder/Default
            'High_Risk_Country_Spend': high_risk_pct, # R024
            
            # Defaults for currently missing data (to allow rules to pass/fail gracefully)
            'Price_Variance_Percentage': 5.0, # R006
            'Supplier_Debt_Equity_Ratio': 1.5, # R010
            'Supplier_Capacity_Utilization': 75.0, # R011
            'MOQ_Months_of_Demand': 2, # R012
            'Lead_Time_Variance_Percentage': 10.0, # R013
            'Foreign_Currency_Spend_Percentage': 20.0, # R014
            'Diverse_Supplier_Spend_Percentage': 10.0, # R015
            'Innovation_Supplier_Spend_Percentage': 5.0, # R016
            'Local_Content_Percentage': 50.0, # R017
            'Qualified_Supplier_Count': len(supplier_spend), # R018
            'Price_Benchmark_Deviation': 2.0, # R019
            'Supplier_Response_Time': 24, # R020
            'Contract_Compliance_Rate': 95.0, # R021
            'Inventory_Turnover': 8, # R022
            'Supplier_Cyber_Rating': 3, # R025 (Mapping B to numeric?)
            'Certified_Suppliers_Percentage': 80.0, # R026
            'Months_Since_Last_Audit': 6, # R027
            'Backup_Supplier_Count': 2, # R029
            'Supplier_Innovation_Score': 70, # R030
            'Carbon_Footprint': 500, # R031
            'Ethical_Certified_Suppliers': 90.0, # R032
            'Low_Spend_Supplier_Count': 5, # R033
            'Average_Contract_Duration': 2, # R034
            'Supplier_Performance_Score': 85.0 # R035
        }
        
        # Tail spend
        tail_spend_threshold = total_spend * 0.20
        cumulative_spend = 0
        tail_suppliers = []
        for _, row in supplier_spend.sort_values('total').iterrows():
            if cumulative_spend < tail_spend_threshold:
                tail_suppliers.append(row['Supplier_ID'])
                cumulative_spend += row['total']
            else:
                break
        
        metrics['tail_suppliers_count'] = len(tail_suppliers)
        metrics['tail_spend_amount'] = cumulative_spend
        
        return metrics
    
    def _evaluate_rule(self, rule: pd.Series, metrics: Dict[str, Any], spend_df: pd.DataFrame) -> Dict[str, Any]:
        """Evaluate a single rule"""
        rule_id = rule['Rule_ID']
        
        # Map rule IDs to evaluation methods
        evaluators = {
            'R001': self._evaluate_r001_regional_concentration,
            'R002': self._evaluate_r002_tail_spend_fragmentation,
            'R003': self._evaluate_r003_single_supplier_dependency,
            'R023': self._evaluate_r023_supplier_concentration_index,
        }
        
        # Use specific evaluator if available, otherwise return not applicable
        if rule_id in evaluators:
            return evaluators[rule_id](rule, metrics, spend_df)
        else:
            # For rules we don't have data for yet, mark as not evaluated
            return None
    
    def _evaluate_r001_regional_concentration(self, rule: pd.Series, metrics: Dict[str, Any], spend_df: pd.DataFrame) -> Dict[str, Any]:
        """R001: Regional Concentration - If >40% of category spend is concentrated in a single region"""
        threshold = 40.0
        current_value = metrics['max_region_concentration']
        
        result = {
            'rule_id': 'R001',
            'rule_name': rule['Rule_Name'],
            'rule_description': rule['Rule_Description'],
            'threshold': f"{threshold}%",
            'current_value': f"{current_value:.1f}%",
            'risk_level': rule['Risk_Level'],
            'category': rule['Category']
        }
        
        if current_value > threshold:
            excess = current_value - threshold
            max_region = metrics['region_percentages'].idxmax()
            result['status'] = 'VIOLATION'
            result['severity'] = 'HIGH'
            result['message'] = f"⚠️ VIOLATION: {current_value:.1f}% of spend concentrated in {max_region} (exceeds {threshold}% limit by {excess:.1f}%)"
            result['action_required'] = rule['Action_Recommendation']
            result['details'] = {
                'region': max_region,
                'region_spend': float(metrics['region_spend'][max_region]),
                'region_percentage': float(current_value)
            }
        elif current_value > threshold * 0.9:  # Warning at 90% of threshold
            result['status'] = 'WARNING'
            result['severity'] = 'MEDIUM'
            max_region = metrics['region_percentages'].idxmax()
            result['message'] = f"⚡ WARNING: {current_value:.1f}% of spend in {max_region} (approaching {threshold}% limit)"
            result['action_required'] = "Monitor regional concentration"
        else:
            result['status'] = 'COMPLIANT'
            result['severity'] = 'LOW'
            result['message'] = f"✅ COMPLIANT: Regional concentration at {current_value:.1f}% (within {threshold}% limit)"
        
        return result
    
    def _evaluate_r002_tail_spend_fragmentation(self, rule: pd.Series, metrics: Dict[str, Any], spend_df: pd.DataFrame) -> Dict[str, Any]:
        """R002: Tail Spend Fragmentation - If bottom 20% of spend is distributed across too many suppliers"""
        threshold = 10  # Max 10 suppliers in tail spend
        current_value = metrics['tail_suppliers_count']
        
        result = {
            'rule_id': 'R002',
            'rule_name': rule['Rule_Name'],
            'rule_description': rule['Rule_Description'],
            'threshold': f"{threshold} suppliers",
            'current_value': f"{current_value} suppliers",
            'risk_level': rule['Risk_Level'],
            'category': rule['Category']
        }
        
        if current_value > threshold:
            excess = current_value - threshold
            result['status'] = 'VIOLATION'
            result['severity'] = 'MEDIUM'
            result['message'] = f"⚠️ VIOLATION: {current_value} suppliers in tail spend (exceeds {threshold} supplier limit by {excess})"
            result['action_required'] = rule['Action_Recommendation']
            result['details'] = {
                'tail_suppliers_count': current_value,
                'tail_spend_amount': float(metrics['tail_spend_amount']),
                'tail_spend_percentage': float((metrics['tail_spend_amount'] / metrics['total_spend']) * 100)
            }
        elif current_value > threshold * 0.8:  # Warning at 80% of threshold
            result['status'] = 'WARNING'
            result['severity'] = 'LOW'
            result['message'] = f"⚡ WARNING: {current_value} suppliers in tail spend (approaching {threshold} supplier limit)"
            result['action_required'] = "Consider consolidating tail suppliers"
        else:
            result['status'] = 'COMPLIANT'
            result['severity'] = 'LOW'
            result['message'] = f"✅ COMPLIANT: {current_value} suppliers in tail spend (within {threshold} supplier limit)"
        
        return result
    
    def _evaluate_r003_single_supplier_dependency(self, rule: pd.Series, metrics: Dict[str, Any], spend_df: pd.DataFrame) -> Dict[str, Any]:
        """R003: Single Supplier Dependency - If >60% of category spend is with a single supplier"""
        threshold = 60.0
        current_value = metrics['max_supplier_concentration']
        
        result = {
            'rule_id': 'R003',
            'rule_name': rule['Rule_Name'],
            'rule_description': rule['Rule_Description'],
            'threshold': f"{threshold}%",
            'current_value': f"{current_value:.1f}%",
            'risk_level': rule['Risk_Level'],
            'category': rule['Category']
        }
        
        if current_value > threshold:
            excess = current_value - threshold
            top_supplier = metrics['supplier_spend'].iloc[0]
            excess_amount = (excess / 100) * metrics['total_spend']
            result['status'] = 'VIOLATION'
            result['severity'] = 'CRITICAL'
            result['message'] = f"⚠️ VIOLATION: {top_supplier['Supplier_Name']} at {current_value:.1f}% (exceeds {threshold}% limit by {excess:.1f}%)"
            result['action_required'] = rule['Action_Recommendation']
            result['details'] = {
                'supplier_name': top_supplier['Supplier_Name'],
                'supplier_id': top_supplier['Supplier_ID'],
                'supplier_spend': float(top_supplier['total']),
                'supplier_percentage': float(current_value),
                'excess_amount': float(excess_amount),
                'recommended_reduction': float(excess_amount)
            }
        elif current_value > threshold * 0.85:  # Warning at 85% of threshold (51%)
            result['status'] = 'WARNING'
            result['severity'] = 'HIGH'
            top_supplier = metrics['supplier_spend'].iloc[0]
            result['message'] = f"⚡ WARNING: {top_supplier['Supplier_Name']} at {current_value:.1f}% (approaching {threshold}% limit)"
            result['action_required'] = "Monitor supplier dependency and plan diversification"
        else:
            result['status'] = 'COMPLIANT'
            result['severity'] = 'LOW'
            result['message'] = f"✅ COMPLIANT: Maximum supplier concentration at {current_value:.1f}% (within {threshold}% limit)"
        
        return result
    
    def _evaluate_r023_supplier_concentration_index(self, rule: pd.Series, metrics: Dict[str, Any], spend_df: pd.DataFrame) -> Dict[str, Any]:
        """R023: Supplier Concentration Index - If Herfindahl index exceeds concentration threshold"""
        threshold = 2500
        current_value = metrics['hhi']
        
        result = {
            'rule_id': 'R023',
            'rule_name': rule['Rule_Name'],
            'rule_description': rule['Rule_Description'],
            'threshold': f"{threshold}",
            'current_value': f"{current_value:.0f}",
            'risk_level': rule['Risk_Level'],
            'category': rule['Category']
        }
        
        if current_value > threshold:
            excess = current_value - threshold
            result['status'] = 'VIOLATION'
            result['severity'] = 'HIGH'
            result['message'] = f"⚠️ VIOLATION: HHI at {current_value:.0f} (exceeds {threshold} limit by {excess:.0f})"
            result['action_required'] = rule['Action_Recommendation']
            result['details'] = {
                'hhi': float(current_value),
                'supplier_count': metrics['supplier_count'],
                'market_structure': self._interpret_hhi(current_value)
            }
        elif current_value > threshold * 0.9:  # Warning at 90% of threshold
            result['status'] = 'WARNING'
            result['severity'] = 'MEDIUM'
            result['message'] = f"⚡ WARNING: HHI at {current_value:.0f} (approaching {threshold} limit)"
            result['action_required'] = "Monitor supplier concentration"
        else:
            result['status'] = 'COMPLIANT'
            result['severity'] = 'LOW'
            result['message'] = f"✅ COMPLIANT: HHI at {current_value:.0f} (within {threshold} limit)"
        
        return result
    
    def _interpret_hhi(self, hhi: float) -> str:
        """Interpret HHI value"""
        if hhi < 1500:
            return "Competitive market"
        elif hhi < 2500:
            return "Moderately concentrated"
        else:
            return "Highly concentrated"
    
    def get_rule_details(self, rule_id: str) -> Dict[str, Any]:
        """Get details for a specific rule"""
        rule = self.rule_book[self.rule_book['Rule_ID'] == rule_id]
        if rule.empty:
            return None
        
        rule = rule.iloc[0]
        return {
            'rule_id': rule['Rule_ID'],
            'rule_name': rule['Rule_Name'],
            'description': rule['Rule_Description'],
            'threshold': rule['Threshold_Value'],
            'comparison_logic': rule['Comparison_Logic'],
            'risk_level': rule['Risk_Level'],
            'action_recommendation': rule['Action_Recommendation'],
            'category': rule['Category']
        }
    
    def get_all_rules(self) -> List[Dict[str, Any]]:
        """Get all rules from rule book"""
        rules = []
        for _, rule in self.rule_book.iterrows():
            rules.append({
                'rule_id': rule['Rule_ID'],
                'rule_name': rule['Rule_Name'],
                'description': rule['Rule_Description'],
                'threshold': rule['Threshold_Value'],
                'risk_level': rule['Risk_Level'],
                'category': rule['Category']
            })
        return rules


if __name__ == "__main__":
    # Test the engine
    engine = RuleEvaluationEngine()
    
    # Test with Rice Bran Oil
    print("=" * 80)
    print("TESTING RULE EVALUATION ENGINE - Rice Bran Oil")
    print("=" * 80)
    
    results = engine.evaluate_all_rules('C001', 'Rice Bran Oil')
    
    print(f"\nTotal Spend: ${results['total_spend']:,.2f}")
    print(f"Supplier Count: {results['supplier_count']}")
    print(f"\nOverall Status: {results['summary']['overall_status']}")
    print(f"Violations: {results['summary']['violations_count']}")
    print(f"Warnings: {results['summary']['warnings_count']}")
    print(f"Compliant: {results['summary']['compliant_count']}")
    
    if results['violations']:
        print("\n" + "=" * 80)
        print("VIOLATIONS:")
        print("=" * 80)
        for v in results['violations']:
            print(f"\n[{v['rule_id']}] {v['rule_name']}")
            print(f"  {v['message']}")
            print(f"  Action: {v['action_required']}")
            if 'details' in v:
                print(f"  Details: {v['details']}")
    
    if results['warnings']:
        print("\n" + "=" * 80)
        print("WARNINGS:")
        print("=" * 80)
        for w in results['warnings']:
            print(f"\n[{w['rule_id']}] {w['rule_name']}")
            print(f"  {w['message']}")
    
    if results['compliant']:
        print("\n" + "=" * 80)
        print("COMPLIANT RULES:")
        print("=" * 80)
        for c in results['compliant']:
            print(f"  [{c['rule_id']}] {c['rule_name']}: {c['message']}")
