"""
Supplier Scorecard & Implementation Roadmap
"""

from typing import Dict, Any, List
from datetime import datetime, timedelta


class SupplierScorecard:
    """Generate supplier performance scorecard"""
    
    def generate_scorecard(self, brief_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comprehensive supplier scorecard"""
        
        dominant_supplier = brief_data.get('dominant_supplier', 'Unknown')
        alternate_supplier = brief_data.get('potential_alternate_supplier', 'Unknown')
        
        return {
            'timestamp': datetime.now().isoformat(),
            'category': brief_data.get('category', 'Unknown'),
            'suppliers': {
                dominant_supplier: self._score_supplier(dominant_supplier, True),
                alternate_supplier: self._score_supplier(alternate_supplier, False)
            },
            'scoring_methodology': {
                'quality': '25%',
                'delivery': '20%',
                'price': '20%',
                'responsiveness': '15%',
                'financial_stability': '10%',
                'innovation': '10%'
            },
            'recommendations': self._generate_scorecard_recommendations(brief_data)
        }
    
    def _score_supplier(self, supplier_name: str, is_incumbent: bool) -> Dict[str, Any]:
        """Score individual supplier"""
        
        if is_incumbent:
            # Incumbent supplier typically higher scores for performance
            return {
                'overall_score': 85,
                'overall_grade': 'A',
                'quality': {'score': 88, 'feedback': 'Consistent quality, minor deviations < 0.5%'},
                'delivery': {'score': 90, 'feedback': 'On-time delivery 98%'},
                'price': {'score': 75, 'feedback': 'Higher than market average'},
                'responsiveness': {'score': 85, 'feedback': 'Good communication, avg response 2 hours'},
                'financial_stability': {'score': 82, 'feedback': 'Stable financials, BBB+ rated'},
                'innovation': {'score': 78, 'feedback': 'Some R&D, limited product innovation'},
                'risk_rating': 'Low',
                'recommended_action': 'Maintain relationship, negotiate better terms'
            }
        else:
            # Alternate supplier typically lower scores due to less history
            return {
                'overall_score': 78,
                'overall_grade': 'B+',
                'quality': {'score': 82, 'feedback': 'Good quality records, need validation'},
                'delivery': {'score': 80, 'feedback': 'Reliable delivery based on available data'},
                'price': {'score': 92, 'feedback': 'Competitive pricing, good cost structure'},
                'responsiveness': {'score': 85, 'feedback': 'Quick to engage, willing to partner'},
                'financial_stability': {'score': 75, 'feedback': 'Stable but smaller than incumbent'},
                'innovation': {'score': 80, 'feedback': 'Good R&D pipeline'},
                'risk_rating': 'Medium',
                'recommended_action': 'Pilot program with 10-15% volume, expand based on performance'
            }


class ImplementationRoadmap:
    """Generate phased implementation roadmap"""
    
    def generate_roadmap(self, brief_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate 24-month implementation roadmap"""
        
        return {
            'timestamp': datetime.now().isoformat(),
            'category': brief_data.get('category', 'Unknown'),
            'duration_months': 24,
            'total_investment': 250000,
            'expected_savings': brief_data.get('cost_advantages', [{}])[-1].get('max_usd', 0) if brief_data.get('cost_advantages') else 0,
            'phases': [
                self._generate_phase_0(),
                self._generate_phase_1(),
                self._generate_phase_2(),
                self._generate_phase_3(),
                self._generate_phase_4()
            ],
            'critical_path': self._get_critical_path(),
            'success_metrics': self._get_success_metrics(brief_data)
        }
    
    def _generate_phase_0(self) -> Dict[str, Any]:
        """Phase 0: Foundation (Months 0-2)"""
        return {
            'phase': 'Phase 0 - Foundation & Planning',
            'duration_months': 2,
            'start_date': (datetime.now()).strftime('%Y-%m-%d'),
            'end_date': (datetime.now() + timedelta(days=60)).strftime('%Y-%m-%d'),
            'activities': [
                'Stakeholder alignment and governance setup',
                'RFQ preparation and market analysis',
                'Supplier evaluation criteria definition',
                'Technology assessment for integration',
                'Create detailed project plan'
            ],
            'deliverables': [
                'Governance charter',
                'RFQ documents',
                'Supplier evaluation matrix',
                'Technology roadmap',
                'Detailed project schedule'
            ],
            'budget': 50000,
            'risks': ['Executive buy-in', 'Resource availability'],
            'kpis': ['Stakeholder sign-off by day 30']
        }
    
    def _generate_phase_1(self) -> Dict[str, Any]:
        """Phase 1: Procurement (Months 2-6)"""
        return {
            'phase': 'Phase 1 - Procurement & Evaluation',
            'duration_months': 4,
            'start_date': (datetime.now() + timedelta(days=60)).strftime('%Y-%m-%d'),
            'end_date': (datetime.now() + timedelta(days=180)).strftime('%Y-%m-%d'),
            'activities': [
                'Issue RFQ to 5-10 potential suppliers',
                'Conduct supplier evaluations and due diligence',
                'Negotiate contracts with top 2-3 suppliers',
                'Establish service level agreements',
                'Plan pilot with selected supplier'
            ],
            'deliverables': [
                'RFQ responses analyzed',
                'Supplier scorecards',
                'Executed contracts',
                'Service level agreements',
                'Pilot test plan'
            ],
            'budget': 75000,
            'risks': ['Supplier responsiveness', 'Price negotiations'],
            'kpis': ['Contracts signed by day 120', 'Cost reduction 5-8%']
        }
    
    def _generate_phase_2(self) -> Dict[str, Any]:
        """Phase 2: Pilot (Months 6-12)"""
        return {
            'phase': 'Phase 2 - Pilot & Validation',
            'duration_months': 6,
            'start_date': (datetime.now() + timedelta(days=180)).strftime('%Y-%m-%d'),
            'end_date': (datetime.now() + timedelta(days=360)).strftime('%Y-%m-%d'),
            'activities': [
                'Execute pilot with 10-15% volume',
                'Monitor quality and delivery KPIs',
                'Gather feedback from business units',
                'Make adjustments and optimizations',
                'Prepare for full rollout'
            ],
            'deliverables': [
                'Pilot results report',
                'Quality metrics dashboard',
                'Cost analysis',
                'Lessons learned document',
                'Full rollout plan'
            ],
            'budget': 60000,
            'risks': ['Quality issues', 'Integration problems'],
            'kpis': ['Quality on-time delivery >95%', 'Cost parity or better']
        }
    
    def _generate_phase_3(self) -> Dict[str, Any]:
        """Phase 3: Rollout (Months 12-18)"""
        return {
            'phase': 'Phase 3 - Full Rollout',
            'duration_months': 6,
            'start_date': (datetime.now() + timedelta(days=360)).strftime('%Y-%m-%d'),
            'end_date': (datetime.now() + timedelta(days=540)).strftime('%Y-%m-%d'),
            'activities': [
                'Scale to 100% volume across all regions',
                'Consolidate previous supplier base',
                'Optimize processes and workflows',
                'Implement continuous improvement',
                'Establish supplier partnership program'
            ],
            'deliverables': [
                'Migration completion',
                'Process documentation',
                'Training materials',
                'Supplier partnership agreements',
                'Consolidated metrics dashboard'
            ],
            'budget': 50000,
            'risks': ['Supply disruption', 'Change management'],
            'kpis': ['100% volume transition', '8-12% cost reduction achieved']
        }
    
    def _generate_phase_4(self) -> Dict[str, Any]:
        """Phase 4: Optimization (Months 18-24)"""
        return {
            'phase': 'Phase 4 - Optimization & Sustain',
            'duration_months': 6,
            'start_date': (datetime.now() + timedelta(days=540)).strftime('%Y-%m-%d'),
            'end_date': (datetime.now() + timedelta(days=720)).strftime('%Y-%m-%d'),
            'activities': [
                'Fine-tune supplier management',
                'Explore additional sourcing options',
                'Implement strategic initiatives',
                'Evaluate technology upgrades',
                'Plan for continuous improvement'
            ],
            'deliverables': [
                'Optimization report',
                'Strategic recommendations',
                'Technology refresh plan',
                'Supplier innovation pipeline',
                'Long-term supplier strategy'
            ],
            'budget': 15000,
            'risks': ['Complacency', 'Market changes'],
            'kpis': ['Sustained 10-15% cost savings', 'Supplier satisfaction >85%']
        }
    
    def _get_critical_path(self) -> List[str]:
        """Get critical path activities"""
        return [
            'Stakeholder alignment (critical)',
            'Supplier selection and contracting',
            'Pilot execution and validation',
            'Full rollout and volume transition'
        ]
    
    def _get_success_metrics(self, brief_data: Dict[str, Any]) -> Dict[str, str]:
        """Get success metrics for roadmap"""
        
        return {
            'cost_savings': '8-15% annual spend reduction',
            'delivery_performance': '>95% on-time delivery',
            'quality': '<0.5% defect rate',
            'supplier_satisfaction': '>85% satisfaction score',
            'innovation': '2+ new initiatives per year',
            'risk_reduction': 'Concentration <50%',
            'timeline': 'Complete in 24 months',
            'roi': '>300% ROI on investment'
        }
