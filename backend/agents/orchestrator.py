"""
Agent Orchestrator
Routes requests to appropriate agents and combines results
"""

import sys
from pathlib import Path
from typing import Dict, Any, List, Optional

root_path = Path(__file__).parent.parent.parent
if str(root_path) not in sys.path:
    sys.path.insert(0, str(root_path))

# Import all agents
from backend.agents.data_analysis.spend_analyzer import SpendAnalyzerAgent
from backend.agents.data_analysis.regional_concentration import RegionalConcentrationAgent
from backend.agents.data_analysis.pattern_detector import PatternDetectorAgent
from backend.agents.data_analysis.threshold_tracker import ThresholdTrackerAgent

from backend.agents.intelligence.web_intelligence import WebIntelligenceAgent
from backend.agents.intelligence.risk_scoring import RiskScoringAgent
from backend.agents.intelligence.rule_engine import RuleEngineAgent
from backend.agents.intelligence.best_practice import BestPracticeAgent

from backend.agents.recommendations.savings_calculator import SavingsCalculatorAgent
from backend.agents.recommendations.action_plan_generator import ActionPlanGeneratorAgent

from backend.agents.incumbent_strategy.capability_screener import SupplierCapabilityScreenerAgent
from backend.agents.region_sourcing.region_identifier import RegionIdentifierAgent
from backend.agents.region_sourcing.supplier_ranking import SupplierRankingAgent


class AgentOrchestrator:
    """
    Main orchestrator that coordinates all agents
    Routes requests to appropriate agents and combines results
    """
    
    def __init__(self):
        # Initialize all agents
        self.agents = {
            # Data Analysis
            'spend_analyzer': SpendAnalyzerAgent(),
            'regional_concentration': RegionalConcentrationAgent(),
            'pattern_detector': PatternDetectorAgent(),
            'threshold_tracker': ThresholdTrackerAgent(),
            
            # Intelligence
            'web_intelligence': WebIntelligenceAgent(),
            'risk_scoring': RiskScoringAgent(),
            'rule_engine': RuleEngineAgent(),
            'best_practice': BestPracticeAgent(),
            
            # Recommendations
            'savings_calculator': SavingsCalculatorAgent(),
            'action_plan_generator': ActionPlanGeneratorAgent(),
            
            # Incumbent Strategy
            'capability_screener': SupplierCapabilityScreenerAgent(),
            
            # Region Sourcing
            'region_identifier': RegionIdentifierAgent(),
            'supplier_ranking': SupplierRankingAgent()
        }
        
        print(f"✅ Orchestrator initialized with {len(self.agents)} agents")
    
    def execute_workflow(self, workflow_type: str, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a complete workflow by coordinating multiple agents
        
        Workflows:
            - 'comprehensive_analysis': Full analysis for a client/category
            - 'rule_evaluation': Evaluate specific rule with recommendations
            - 'savings_opportunity': Calculate savings with action plan
            - 'risk_assessment': Complete risk analysis
            - 'supplier_comparison': Compare suppliers
        """
        
        print(f"\n{'='*80}")
        print(f"🚀 EXECUTING WORKFLOW: {workflow_type}")
        print(f"{'='*80}\n")
        
        if workflow_type == 'comprehensive_analysis':
            return self._comprehensive_analysis_workflow(input_data)
        elif workflow_type == 'rule_evaluation':
            return self._rule_evaluation_workflow(input_data)
        elif workflow_type == 'savings_opportunity':
            return self._savings_opportunity_workflow(input_data)
        elif workflow_type == 'risk_assessment':
            return self._risk_assessment_workflow(input_data)
        elif workflow_type == 'supplier_comparison':
            return self._supplier_comparison_workflow(input_data)
        else:
            return {
                'success': False,
                'error': f"Unknown workflow type: {workflow_type}"
            }
    
    def _comprehensive_analysis_workflow(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Complete analysis workflow combining multiple agents
        """
        client_id = input_data.get('client_id')
        category = input_data.get('category')
        
        print(f"📊 Running comprehensive analysis for {client_id} - {category}\n")
        
        results = {}
        
        # Step 1: Spend Analysis
        print("1️⃣  Analyzing spend data...")
        spend_result = self.agents['spend_analyzer'].execute({
            'client_id': client_id,
            'category': category
        })
        results['spend_analysis'] = spend_result['data'] if spend_result['success'] else None
        
        # Step 2: Regional Concentration
        print("2️⃣  Analyzing regional concentration...")
        regional_result = self.agents['regional_concentration'].execute({
            'client_id': client_id,
            'category': category
        })
        results['regional_analysis'] = regional_result['data'] if regional_result['success'] else None
        
        # Step 3: Pattern Detection
        print("3️⃣  Detecting patterns...")
        pattern_result = self.agents['pattern_detector'].execute({
            'client_id': client_id,
            'category': category
        })
        results['patterns'] = pattern_result['data'] if pattern_result['success'] else None
        
        # Step 4: Threshold Tracking
        print("4️⃣  Checking rule thresholds...")
        threshold_result = self.agents['threshold_tracker'].execute({
            'client_id': client_id,
            'category': category
        })
        results['thresholds'] = threshold_result['data'] if threshold_result['success'] else None
        
        # Step 5: Web Intelligence (Market Prices)
        print("5️⃣  Gathering market intelligence...")
        web_result = self.agents['web_intelligence'].execute({
            'query_type': 'market_price',
            'product': category,
            'region': input_data.get('region', '')
        })
        results['market_intelligence'] = web_result['data'] if web_result['success'] else None
        
        # Step 6: Generate Summary
        print("6️⃣  Generating summary...\n")
        summary = self._generate_comprehensive_summary(results, client_id, category)
        results['summary'] = summary
        
        print(f"{'='*80}")
        print(f"✅ COMPREHENSIVE ANALYSIS COMPLETE")
        print(f"{'='*80}\n")
        
        return {
            'success': True,
            'workflow': 'comprehensive_analysis',
            'client_id': client_id,
            'category': category,
            'results': results
        }
    
    def _rule_evaluation_workflow(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Rule evaluation workflow with detailed recommendations
        """
        rule_id = input_data.get('rule_id')
        client_id = input_data.get('client_id')
        
        print(f"📋 Evaluating rule {rule_id} for client {client_id}\n")
        
        results = {}
        
        # Step 1: Evaluate the rule
        print(f"1️⃣  Evaluating rule {rule_id}...")
        rule_result = self.agents['rule_engine'].execute(input_data)
        results['rule_evaluation'] = rule_result['data'] if rule_result['success'] else None
        
        if not rule_result['success']:
            return {
                'success': False,
                'error': rule_result.get('error', 'Rule evaluation failed')
            }
        
        rule_data = rule_result['data']
        
        # Step 2: If violations exist, calculate impact
        if rule_data.get('violations'):
            print("2️⃣  Calculating impact of violations...")
            
            # Get spend analysis for context
            spend_result = self.agents['spend_analyzer'].execute({
                'client_id': client_id,
                'category': input_data.get('category')
            })
            results['spend_context'] = spend_result['data'] if spend_result['success'] else None
            
            # Risk scoring for violating suppliers
            print("3️⃣  Scoring supplier risks...")
            risk_scores = []
            for violation in rule_data['violations'][:3]:  # Top 3 violations
                supplier_id = violation.get('supplier_id')
                if supplier_id:
                    risk_result = self.agents['risk_scoring'].execute({'supplier_id': supplier_id})
                    if risk_result['success']:
                        risk_scores.append(risk_result['data'])
            
            results['risk_scores'] = risk_scores
            
            # Generate action plan
            print("4️⃣  Generating action plan...")
            action_plan_result = self.agents['action_plan_generator'].execute({
                'scenario': 'rule_violation_fix',
                'analysis_results': rule_data
            })
            results['action_plan'] = action_plan_result['data'] if action_plan_result['success'] else None
        
        # Step 3: Get best practices
        print("5️⃣  Retrieving best practices...\n")
        best_practice_result = self.agents['best_practice'].execute({
            'scenario': 'quality_assurance' if 'quality' in rule_id.lower() else 'risk_mitigation'
        })
        results['best_practices'] = best_practice_result['data'] if best_practice_result['success'] else None
        
        print(f"{'='*80}")
        print(f"✅ RULE EVALUATION COMPLETE")
        print(f"{'='*80}\n")
        
        return {
            'success': True,
            'workflow': 'rule_evaluation',
            'rule_id': rule_id,
            'client_id': client_id,
            'results': results
        }
    
    def _savings_opportunity_workflow(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Savings opportunity workflow with detailed calculations
        """
        client_id = input_data.get('client_id')
        category = input_data.get('category')
        scenario = input_data.get('scenario', 'price_negotiation')
        
        print(f"💰 Calculating savings opportunity for {client_id} - {category}\n")
        
        results = {}
        
        # Step 1: Get current spend
        print("1️⃣  Analyzing current spend...")
        spend_result = self.agents['spend_analyzer'].execute({
            'client_id': client_id,
            'category': category
        })
        results['spend_analysis'] = spend_result['data'] if spend_result['success'] else None
        
        # Step 2: Get market price intelligence
        print("2️⃣  Gathering market prices...")
        web_result = self.agents['web_intelligence'].execute({
            'query_type': 'market_price',
            'product': category,
            'region': input_data.get('region', '')
        })
        results['market_intelligence'] = web_result['data'] if web_result['success'] else None
        
        # Step 3: Calculate savings
        print("3️⃣  Calculating savings potential...")
        savings_result = self.agents['savings_calculator'].execute({
            'client_id': client_id,
            'category': category,
            'scenario': scenario,
            'market_price': input_data.get('market_price'),
            'target_price': input_data.get('target_price')
        })
        results['savings_calculation'] = savings_result['data'] if savings_result['success'] else None
        
        # Step 4: Generate action plan
        print("4️⃣  Creating action plan...")
        action_plan_result = self.agents['action_plan_generator'].execute({
            'scenario': scenario,
            'analysis_results': savings_result['data'] if savings_result['success'] else {}
        })
        results['action_plan'] = action_plan_result['data'] if action_plan_result['success'] else None
        
        # Step 5: Get best practices
        print("5️⃣  Retrieving best practices...\n")
        best_practice_result = self.agents['best_practice'].execute({
            'scenario': 'cost_optimization'
        })
        results['best_practices'] = best_practice_result['data'] if best_practice_result['success'] else None
        
        print(f"{'='*80}")
        print(f"✅ SAVINGS OPPORTUNITY ANALYSIS COMPLETE")
        print(f"{'='*80}\n")
        
        return {
            'success': True,
            'workflow': 'savings_opportunity',
            'client_id': client_id,
            'category': category,
            'results': results
        }
    
    def _risk_assessment_workflow(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Risk assessment workflow
        """
        supplier_id = input_data.get('supplier_id')
        
        print(f"⚠️  Assessing risk for supplier {supplier_id}\n")
        
        results = {}
        
        # Step 1: Risk scoring
        print("1️⃣  Calculating risk score...")
        risk_result = self.agents['risk_scoring'].execute({
            'supplier_id': supplier_id
        })
        results['risk_score'] = risk_result['data'] if risk_result['success'] else None
        
        # Step 2: Best practices for risk mitigation
        print("2️⃣  Retrieving risk mitigation best practices...\n")
        best_practice_result = self.agents['best_practice'].execute({
            'scenario': 'risk_mitigation'
        })
        results['best_practices'] = best_practice_result['data'] if best_practice_result['success'] else None
        
        print(f"{'='*80}")
        print(f"✅ RISK ASSESSMENT COMPLETE")
        print(f"{'='*80}\n")
        
        return {
            'success': True,
            'workflow': 'risk_assessment',
            'supplier_id': supplier_id,
            'results': results
        }
    
    def _supplier_comparison_workflow(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Compare two suppliers
        """
        supplier_id_1 = input_data.get('supplier_id_1')
        supplier_id_2 = input_data.get('supplier_id_2')
        
        print(f"🔄 Comparing suppliers {supplier_id_1} vs {supplier_id_2}\n")
        
        results = {}
        
        # Risk comparison
        print("1️⃣  Comparing risk scores...")
        comparison_result = self.agents['risk_scoring'].compare_suppliers(supplier_id_1, supplier_id_2)
        results['risk_comparison'] = comparison_result['data'] if comparison_result['success'] else None
        
        print(f"\n{'='*80}")
        print(f"✅ SUPPLIER COMPARISON COMPLETE")
        print(f"{'='*80}\n")
        
        return {
            'success': True,
            'workflow': 'supplier_comparison',
            'results': results
        }
    
    def _generate_comprehensive_summary(self, results: Dict, client_id: str, category: str) -> str:
        """Generate executive summary"""
        
        summary = f"📊 COMPREHENSIVE ANALYSIS SUMMARY\n"
        summary += f"{'='*80}\n\n"
        summary += f"Client: {client_id}\n"
        summary += f"Category: {category}\n\n"
        
        # Spend summary
        if results.get('spend_analysis'):
            spend = results['spend_analysis']
            summary += f"💰 SPEND OVERVIEW:\n"
            summary += f"   Total Spend: {spend.get('total_spend_formatted', 'N/A')}\n"
            summary += f"   Transactions: {spend.get('transaction_count', 'N/A')}\n"
            summary += f"   Top Supplier: {spend.get('top_supplier', {}).get('name', 'N/A')} "
            summary += f"({spend.get('top_supplier', {}).get('percentage', 0):.1f}%)\n\n"
        
        # Regional risk
        if results.get('regional_analysis'):
            regional = results['regional_analysis']
            summary += f"🌍 REGIONAL CONCENTRATION:\n"
            summary += f"   Risk Level: {regional.get('risk_level', 'N/A')}\n"
            summary += f"   {regional.get('risk_explanation', '')}\n\n"
        
        # Threshold violations
        if results.get('thresholds'):
            thresholds = results['thresholds']
            summary += f"📋 RULE COMPLIANCE:\n"
            summary += f"   Violations: {thresholds.get('violations_count', 0)}\n"
            summary += f"   Warnings: {thresholds.get('warnings_count', 0)}\n"
            summary += f"   Status: {thresholds.get('overall_status', 'N/A')}\n\n"
        
        summary += f"{'='*80}\n"
        
        return summary
    
    def get_agent_status(self) -> Dict[str, Any]:
        """Get status of all agents"""
        return {
            agent_name: agent.get_info()
            for agent_name, agent in self.agents.items()
        }
