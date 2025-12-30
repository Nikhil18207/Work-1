"""
Master Orchestrator for Personalized Supplier Coaching System
Coordinates all agents and provides comprehensive coaching
"""

import sys
from pathlib import Path
from typing import Dict, Any, List
from datetime import datetime

root_path = Path(__file__).parent.parent.parent
if str(root_path) not in sys.path:
    sys.path.insert(0, str(root_path))

from backend.agents.base_agent import BaseAgent
from backend.agents.data_analysis.spend_analyzer import SpendAnalyzerAgent
from backend.agents.data_analysis.threshold_tracker import ThresholdTrackerAgent
from backend.agents.data_analysis.regional_concentration import RegionalConcentrationAgent
from backend.agents.data_analysis.pattern_detector import PatternDetectorAgent
from backend.agents.recommendations.personalized_coach import PersonalizedCoachAgent
from backend.agents.incumbent_strategy.enhanced_incumbent_strategy import IncumbentStrategyAgent
from backend.agents.region_sourcing.enhanced_region_sourcing import EnhancedRegionSourcingAgent
from backend.agents.intelligence.web_scraping_agent import WebScrapingAgent
from backend.engines.parameter_tuning_engine import ParameterTuningEngine


class SupplierCoachingOrchestrator(BaseAgent):
    """
    Master Orchestrator for Personalized Supplier Coaching System
    
    Coordinates 5 main branches:
    1. Data Analysis & Quantification
    2. Personalized Recommendations
    3. Incumbent Supplier Strategy
    4. Additional Region Sourcing
    5. System Architecture (Parameter Tuning + Web Scraping)
    """
    
    def __init__(self):
        super().__init__(
            name="SupplierCoachingOrchestrator",
            description="Master orchestrator for personalized supplier coaching"
        )
        
        # Initialize all agents
        self._initialize_agents()
    
    def _initialize_agents(self):
        """Initialize all specialized agents"""
        # Branch 1: Data Analysis & Quantification
        self.spend_analyzer = SpendAnalyzerAgent()
        self.threshold_tracker = ThresholdTrackerAgent()
        self.regional_concentration = RegionalConcentrationAgent()
        self.pattern_detector = PatternDetectorAgent()
        
        # Branch 2: Personalized Recommendations
        self.personalized_coach = PersonalizedCoachAgent()
        
        # Branch 3: Incumbent Supplier Strategy
        self.incumbent_strategy = IncumbentStrategyAgent()
        
        # Branch 4: Additional Region Sourcing
        self.region_sourcing = EnhancedRegionSourcingAgent()
        
        # Branch 5: System Architecture
        self.web_scraping = WebScrapingAgent()
        self.parameter_tuning = ParameterTuningEngine()
        
        self._log("All agents initialized successfully")
    
    def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute comprehensive supplier coaching analysis
        
        Input:
            - client_id: str (required)
            - category: str (optional)
            - coaching_mode: str - 'full', 'quick', 'focused'
            - focus_areas: List[str] (optional) - specific areas to focus on
            - expansion_volume: float (optional) - volume to allocate
            - tuning_mode: str (optional) - 'conservative', 'balanced', 'aggressive'
        """
        try:
            session_id = f"COACHING_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            self._log(f"[{session_id}] Starting comprehensive coaching session")
            self._log(f"[{session_id}] Input: {input_data}")
            
            if not input_data.get('client_id'):
                return self._create_response(
                    success=False,
                    error="client_id is required"
                )
            
            coaching_mode = input_data.get('coaching_mode', 'full')
            focus_areas = input_data.get('focus_areas', [])
            
            # Initialize results structure
            results = {
                'session_id': session_id,
                'timestamp': datetime.now().isoformat(),
                'client_id': input_data['client_id'],
                'category': input_data.get('category'),
                'coaching_mode': coaching_mode,
                'branches': {}
            }
            
            # Branch 1: Data Analysis & Quantification
            self._log(f"[{session_id}] Executing Branch 1: Data Analysis & Quantification")
            results['branches']['data_analysis'] = self._execute_data_analysis_branch(
                input_data, session_id
            )
            
            # Branch 5: System Architecture (Parameter Tuning first to inform other branches)
            self._log(f"[{session_id}] Executing Branch 5: System Architecture")
            results['branches']['system_architecture'] = self._execute_system_architecture_branch(
                input_data, session_id
            )
            
            # Branch 3: Incumbent Supplier Strategy
            if coaching_mode == 'full' or 'incumbent' in focus_areas:
                self._log(f"[{session_id}] Executing Branch 3: Incumbent Supplier Strategy")
                results['branches']['incumbent_strategy'] = self._execute_incumbent_strategy_branch(
                    input_data, session_id, results['branches']['data_analysis']
                )
            
            # Branch 4: Additional Region Sourcing
            if coaching_mode == 'full' or 'regions' in focus_areas:
                self._log(f"[{session_id}] Executing Branch 4: Additional Region Sourcing")
                results['branches']['region_sourcing'] = self._execute_region_sourcing_branch(
                    input_data, session_id, results['branches']['data_analysis']
                )
            
            # Branch 2: Personalized Recommendations (synthesizes all insights)
            self._log(f"[{session_id}] Executing Branch 2: Personalized Recommendations")
            results['branches']['personalized_recommendations'] = self._execute_personalized_recommendations_branch(
                input_data, session_id, results['branches']
            )
            
            # Generate Executive Summary
            results['executive_summary'] = self._generate_executive_summary(results)
            
            # Generate Action Plan
            results['action_plan'] = self._generate_action_plan(results)
            
            # Calculate Overall Scores
            results['scoring'] = self._calculate_overall_scores(results)
            
            self._log(f"[{session_id}] Coaching session complete")
            
            return self._create_response(
                success=True,
                data=results,
                sources=['all_agents']
            )
            
        except Exception as e:
            self._log(f"Error in coaching orchestration: {str(e)}", "ERROR")
            return self._create_response(
                success=False,
                error=str(e)
            )
    
    def _execute_data_analysis_branch(
        self, input_data: Dict, session_id: str
    ) -> Dict:
        """Execute Branch 1: Data Analysis & Quantification"""
        branch_results = {
            'branch_name': 'Data Analysis & Quantification',
            'components': {}
        }
        
        # Component 1: Spend Analysis
        self._log(f"[{session_id}] Running Spend Analyzer")
        spend_result = self.spend_analyzer.execute(input_data)
        branch_results['components']['spend_analysis'] = spend_result['data'] if spend_result['success'] else {}
        
        # Component 2: Threshold Tracking
        self._log(f"[{session_id}] Running Threshold Tracker")
        threshold_result = self.threshold_tracker.execute(input_data)
        branch_results['components']['threshold_tracking'] = threshold_result['data'] if threshold_result['success'] else {}
        
        # Component 3: Regional Concentration
        self._log(f"[{session_id}] Running Regional Concentration Analyzer")
        regional_result = self.regional_concentration.execute(input_data)
        branch_results['components']['regional_concentration'] = regional_result['data'] if regional_result['success'] else {}
        
        # Component 4: Pattern Detection
        self._log(f"[{session_id}] Running Pattern Detector")
        pattern_result = self.pattern_detector.execute(input_data)
        branch_results['components']['pattern_detection'] = pattern_result['data'] if pattern_result['success'] else {}
        
        # Synthesize quantification metrics
        branch_results['quantification_summary'] = self._synthesize_quantification_metrics(
            branch_results['components']
        )
        
        return branch_results
    
    def _execute_system_architecture_branch(
        self, input_data: Dict, session_id: str
    ) -> Dict:
        """Execute Branch 5: System Architecture (Parameter Tuning + Web Scraping)"""
        branch_results = {
            'branch_name': 'System Architecture',
            'components': {}
        }
        
        # Component 1: Parameter Tuning
        self._log(f"[{session_id}] Running Parameter Tuning Engine")
        tuning_input = {
            **input_data,
            'tuning_mode': input_data.get('tuning_mode', 'balanced')
        }
        tuning_result = self.parameter_tuning.execute(tuning_input)
        branch_results['components']['parameter_tuning'] = tuning_result['data'] if tuning_result['success'] else {}
        
        # Component 2: Web Scraping (Real-time Intelligence)
        self._log(f"[{session_id}] Running Web Scraping Agent")
        scraping_input = {
            'data_type': 'all',
            'category': input_data.get('category'),
            'region': 'Global'
        }
        scraping_result = self.web_scraping.execute(scraping_input)
        branch_results['components']['web_scraping'] = scraping_result['data'] if scraping_result['success'] else {}
        
        return branch_results
    
    def _execute_incumbent_strategy_branch(
        self, input_data: Dict, session_id: str, data_analysis: Dict
    ) -> Dict:
        """Execute Branch 3: Incumbent Supplier Strategy"""
        branch_results = {
            'branch_name': 'Incumbent Supplier Strategy',
            'components': {}
        }
        
        # Prepare input with expansion volume
        incumbent_input = {
            **input_data,
            'expansion_volume': input_data.get('expansion_volume', 0)
        }
        
        # Execute incumbent strategy analysis
        self._log(f"[{session_id}] Running Incumbent Strategy Agent")
        incumbent_result = self.incumbent_strategy.execute(incumbent_input)
        branch_results['components']['incumbent_analysis'] = incumbent_result['data'] if incumbent_result['success'] else {}
        
        # Extract key insights
        if incumbent_result['success']:
            branch_results['screening_summary'] = incumbent_result['data'].get('screening_summary', {})
            branch_results['expansion_opportunities'] = incumbent_result['data'].get('expansion_opportunities', [])
            branch_results['constraint_validation'] = incumbent_result['data'].get('constraint_validation', {})
        
        return branch_results
    
    def _execute_region_sourcing_branch(
        self, input_data: Dict, session_id: str, data_analysis: Dict
    ) -> Dict:
        """Execute Branch 4: Additional Region Sourcing"""
        branch_results = {
            'branch_name': 'Additional Region Sourcing',
            'components': {}
        }
        
        # Identify regions to exclude (current high-concentration regions)
        exclude_regions = []
        regional_data = data_analysis.get('components', {}).get('regional_concentration', {})
        if regional_data:
            high_concentration_regions = [
                r['region'] for r in regional_data.get('regional_breakdown', [])
                if r.get('percentage', 0) > 40
            ]
            exclude_regions = high_concentration_regions
        
        # Prepare input
        region_input = {
            **input_data,
            'exclude_regions': exclude_regions,
            'target_volume': input_data.get('expansion_volume', 0),
            'priority_criteria': ['quality', 'price', 'capacity']
        }
        
        # Execute region sourcing analysis
        self._log(f"[{session_id}] Running Enhanced Region Sourcing Agent")
        region_result = self.region_sourcing.execute(region_input)
        branch_results['components']['region_analysis'] = region_result['data'] if region_result['success'] else {}
        
        # Extract key insights
        if region_result['success']:
            branch_results['new_regions'] = region_result['data'].get('new_regions_identified', [])
            branch_results['supplier_evaluation'] = region_result['data'].get('supplier_evaluation', {})
            branch_results['comparative_analysis'] = region_result['data'].get('comparative_analysis', {})
        
        return branch_results
    
    def _execute_personalized_recommendations_branch(
        self, input_data: Dict, session_id: str, all_branches: Dict
    ) -> Dict:
        """Execute Branch 2: Personalized Recommendations"""
        branch_results = {
            'branch_name': 'Personalized Recommendations',
            'components': {}
        }
        
        # Prepare comprehensive input for personalized coach
        coach_input = {
            **input_data,
            'threshold_violations': all_branches.get('data_analysis', {}).get('components', {}).get('threshold_tracking', {}).get('violations', []),
            'current_suppliers': all_branches.get('data_analysis', {}).get('components', {}).get('spend_analysis', {}).get('spend_by_supplier', []),
            'focus_area': input_data.get('focus_areas', ['concentration', 'quality', 'diversification'])[0] if input_data.get('focus_areas') else 'concentration'
        }
        
        # Execute personalized coaching
        self._log(f"[{session_id}] Running Personalized Coach Agent")
        coach_result = self.personalized_coach.execute(coach_input)
        branch_results['components']['coaching'] = coach_result['data'] if coach_result['success'] else {}
        
        # Extract key recommendations
        if coach_result['success']:
            branch_results['personalized_recommendations'] = coach_result['data'].get('personalized_recommendations', [])
            branch_results['implementation_roadmap'] = coach_result['data'].get('implementation_roadmap', {})
            branch_results['confidence_scores'] = coach_result['data'].get('confidence_scores', {})
        
        return branch_results
    
    def _synthesize_quantification_metrics(self, components: Dict) -> Dict:
        """Synthesize quantification metrics from all data analysis components"""
        synthesis = {
            'total_spend': 0,
            'supplier_count': 0,
            'region_count': 0,
            'violation_count': 0,
            'warning_count': 0,
            'risk_level': 'UNKNOWN',
            'concentration_metrics': {},
            'pattern_insights': []
        }
        
        # Extract from spend analysis
        spend_data = components.get('spend_analysis', {})
        if spend_data:
            synthesis['total_spend'] = spend_data.get('total_spend', 0)
            synthesis['supplier_count'] = len(spend_data.get('spend_by_supplier', []))
            synthesis['region_count'] = len(spend_data.get('spend_by_region', []))
        
        # Extract from threshold tracking
        threshold_data = components.get('threshold_tracking', {})
        if threshold_data:
            synthesis['violation_count'] = threshold_data.get('violations_count', 0)
            synthesis['warning_count'] = threshold_data.get('warnings_count', 0)
            synthesis['risk_level'] = threshold_data.get('overall_status', 'UNKNOWN')
        
        # Extract from regional concentration
        regional_data = components.get('regional_concentration', {})
        if regional_data:
            synthesis['concentration_metrics'] = {
                'regional_risk': regional_data.get('concentration_risk', 'UNKNOWN'),
                'top_region_percentage': regional_data.get('top_region', {}).get('percentage', 0)
            }
        
        # Extract from pattern detection
        pattern_data = components.get('pattern_detection', {})
        if pattern_data:
            synthesis['pattern_insights'] = pattern_data.get('patterns', [])
        
        return synthesis
    
    def _generate_executive_summary(self, results: Dict) -> Dict:
        """Generate executive summary of coaching session"""
        data_analysis = results['branches'].get('data_analysis', {})
        quant_summary = data_analysis.get('quantification_summary', {})
        
        summary = {
            'session_id': results['session_id'],
            'client_id': results['client_id'],
            'category': results['category'],
            'timestamp': results['timestamp'],
            
            # Current State
            'current_state': {
                'total_spend': quant_summary.get('total_spend', 0),
                'total_spend_formatted': f"${quant_summary.get('total_spend', 0):,.2f}",
                'supplier_count': quant_summary.get('supplier_count', 0),
                'region_count': quant_summary.get('region_count', 0),
                'risk_level': quant_summary.get('risk_level', 'UNKNOWN')
            },
            
            # Key Issues
            'key_issues': {
                'violations': quant_summary.get('violation_count', 0),
                'warnings': quant_summary.get('warning_count', 0),
                'critical_areas': self._identify_critical_areas(results)
            },
            
            # Opportunities
            'opportunities': {
                'incumbent_expansion': len(results['branches'].get('incumbent_strategy', {}).get('expansion_opportunities', [])),
                'new_regions': len(results['branches'].get('region_sourcing', {}).get('new_regions', [])),
                'total_recommendations': len(results['branches'].get('personalized_recommendations', {}).get('personalized_recommendations', []))
            },
            
            # Market Intelligence
            'market_intelligence': self._summarize_market_intelligence(results),
            
            # Next Steps
            'immediate_actions': self._identify_immediate_actions(results)
        }
        
        return summary
    
    def _identify_critical_areas(self, results: Dict) -> List[str]:
        """Identify critical areas requiring attention"""
        critical_areas = []
        
        data_analysis = results['branches'].get('data_analysis', {})
        threshold_data = data_analysis.get('components', {}).get('threshold_tracking', {})
        
        if threshold_data:
            violations = threshold_data.get('violations', [])
            for violation in violations:
                if violation.get('severity') == 'HIGH':
                    critical_areas.append(violation.get('message', 'Unknown issue'))
        
        return critical_areas[:5]  # Top 5 critical areas
    
    def _summarize_market_intelligence(self, results: Dict) -> Dict:
        """Summarize market intelligence from web scraping"""
        system_arch = results['branches'].get('system_architecture', {})
        web_data = system_arch.get('components', {}).get('web_scraping', {})
        
        if not web_data:
            return {'available': False}
        
        insights = web_data.get('aggregated_insights', {})
        
        return {
            'available': True,
            'key_insights_count': len(insights.get('key_insights', [])),
            'opportunities_count': len(insights.get('opportunities', [])),
            'threats_count': len(insights.get('threats', [])),
            'top_insights': insights.get('key_insights', [])[:3]
        }
    
    def _identify_immediate_actions(self, results: Dict) -> List[Dict]:
        """Identify immediate actions required"""
        actions = []
        
        # From threshold violations
        data_analysis = results['branches'].get('data_analysis', {})
        threshold_data = data_analysis.get('components', {}).get('threshold_tracking', {})
        
        if threshold_data:
            violations = threshold_data.get('violations', [])
            for violation in violations[:3]:  # Top 3 violations
                if violation.get('severity') == 'HIGH':
                    actions.append({
                        'priority': 'CRITICAL',
                        'action': f"Address {violation.get('rule', 'compliance')} violation",
                        'description': violation.get('message', ''),
                        'timeline': '7 days'
                    })
        
        # From personalized recommendations
        recommendations = results['branches'].get('personalized_recommendations', {})
        rec_list = recommendations.get('personalized_recommendations', [])
        
        for rec in rec_list[:2]:  # Top 2 recommendations
            if rec.get('priority') in ['CRITICAL', 'HIGH']:
                actions.append({
                    'priority': rec.get('priority'),
                    'action': rec.get('title', ''),
                    'description': rec.get('current_situation', ''),
                    'timeline': '30 days'
                })
        
        return actions[:5]  # Top 5 immediate actions
    
    def _generate_action_plan(self, results: Dict) -> Dict:
        """Generate comprehensive action plan"""
        action_plan = {
            'phases': {},
            'total_actions': 0,
            'estimated_duration': '180 days'
        }
        
        # Get implementation roadmap from personalized recommendations
        recommendations = results['branches'].get('personalized_recommendations', {})
        roadmap = recommendations.get('implementation_roadmap', {})
        
        if roadmap:
            action_plan['phases'] = roadmap
            action_plan['total_actions'] = sum(
                len(phase.get('recommendations', []))
                for phase in roadmap.values()
            )
        
        return action_plan
    
    def _calculate_overall_scores(self, results: Dict) -> Dict:
        """Calculate overall performance and health scores"""
        scores = {
            'current_health_score': 0,
            'projected_health_score': 0,
            'improvement_potential': 0,
            'breakdown': {}
        }
        
        data_analysis = results['branches'].get('data_analysis', {})
        quant_summary = data_analysis.get('quantification_summary', {})
        
        # Calculate current health score (0-100)
        health_components = {
            'diversification': 0,
            'quality': 0,
            'compliance': 0,
            'risk_management': 0
        }
        
        # Diversification score (30 points)
        supplier_count = quant_summary.get('supplier_count', 0)
        if supplier_count >= 10:
            health_components['diversification'] = 30
        elif supplier_count >= 5:
            health_components['diversification'] = 20
        elif supplier_count >= 3:
            health_components['diversification'] = 10
        
        # Compliance score (30 points)
        violation_count = quant_summary.get('violation_count', 0)
        if violation_count == 0:
            health_components['compliance'] = 30
        elif violation_count <= 2:
            health_components['compliance'] = 20
        elif violation_count <= 5:
            health_components['compliance'] = 10
        
        # Risk management score (40 points)
        risk_level = quant_summary.get('risk_level', 'UNKNOWN')
        risk_scores = {
            'OK': 40,
            'WARNING': 30,
            'CRITICAL': 10,
            'UNKNOWN': 20
        }
        health_components['risk_management'] = risk_scores.get(risk_level, 20)
        
        scores['current_health_score'] = sum(health_components.values())
        scores['breakdown'] = health_components
        
        # Projected improvement (simplified)
        scores['projected_health_score'] = min(100, scores['current_health_score'] + 20)
        scores['improvement_potential'] = scores['projected_health_score'] - scores['current_health_score']
        
        return scores
