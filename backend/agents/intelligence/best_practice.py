"""
Best Practice Agent
Provides industry best practices with context
"""

import sys
from pathlib import Path
from typing import Dict, Any

root_path = Path(__file__).parent.parent.parent.parent
if str(root_path) not in sys.path:
    sys.path.insert(0, str(root_path))

from backend.agents.base_agent import BaseAgent


class BestPracticeAgent(BaseAgent):
    """
    Agent for providing best practices
    
    Input:
        - scenario: str (e.g., 'supplier_consolidation', 'risk_mitigation')
        - industry: str (optional)
        - category: str (optional)
        
    Output:
        - best_practices: List[Dict]
        - recommendations: List[str]
    """
    
    def __init__(self):
        super().__init__(
            name="BestPractice",
            description="Provides industry best practices and recommendations"
        )
        
        # Best practices database
        self.BEST_PRACTICES = {
            'supplier_consolidation': [
                {
                    'practice': 'Maintain 2-3 suppliers per category',
                    'rationale': 'Balance between cost efficiency and supply chain resilience',
                    'implementation': 'Allocate 50-30-20% split among top 3 suppliers',
                    'risk_mitigation': 'Prevents single-source dependency while maintaining negotiating power'
                },
                {
                    'practice': 'Gradual consolidation over 6-12 months',
                    'rationale': 'Allows time to validate supplier performance',
                    'implementation': 'Phase out underperforming suppliers incrementally',
                    'risk_mitigation': 'Reduces transition risk and maintains supply continuity'
                }
            ],
            'risk_mitigation': [
                {
                    'practice': 'Geographic diversification',
                    'rationale': 'Reduces regional concentration risk',
                    'implementation': 'Source from 2-3 different regions, max 50% from any single region',
                    'risk_mitigation': 'Protects against regional disruptions (natural disasters, political instability)'
                },
                {
                    'practice': 'Dual sourcing for critical categories',
                    'rationale': 'Ensures supply continuity',
                    'implementation': '70-30 split between primary and backup supplier',
                    'risk_mitigation': 'Maintains supply even if primary supplier fails'
                }
            ],
            'cost_optimization': [
                {
                    'practice': 'Annual price benchmarking',
                    'rationale': 'Ensures competitive pricing',
                    'implementation': 'Compare prices against market benchmarks quarterly',
                    'risk_mitigation': 'Prevents price drift and identifies savings opportunities'
                },
                {
                    'practice': 'Volume consolidation',
                    'rationale': 'Leverage buying power',
                    'implementation': 'Consolidate spend with fewer suppliers to negotiate better rates',
                    'risk_mitigation': 'Achieves 5-15% cost savings through volume discounts'
                }
            ],
            'quality_assurance': [
                {
                    'practice': 'Mandatory certifications',
                    'rationale': 'Ensures quality and compliance',
                    'implementation': 'Require ISO 22000/HACCP for food products',
                    'risk_mitigation': 'Reduces quality issues and regulatory risks'
                },
                {
                    'practice': 'Regular supplier audits',
                    'rationale': 'Maintains quality standards',
                    'implementation': 'Conduct annual on-site audits for strategic suppliers',
                    'risk_mitigation': 'Early detection of quality degradation'
                }
            ]
        }
    
    def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute best practice retrieval
        """
        try:
            scenario = input_data.get('scenario', 'general')
            
            self._log(f"Retrieving best practices for scenario: {scenario}")
            
            # Get relevant best practices
            practices = self.BEST_PRACTICES.get(scenario, [])
            
            if not practices:
                # Return general best practices
                practices = [
                    {
                        'practice': 'Data-driven decision making',
                        'rationale': 'Reduces bias and improves outcomes',
                        'implementation': 'Use historical data and market intelligence for procurement decisions'
                    },
                    {
                        'practice': 'Supplier relationship management',
                        'rationale': 'Builds long-term partnerships',
                        'implementation': 'Regular communication and performance reviews with key suppliers'
                    }
                ]
            
            # Generate recommendations
            recommendations = [p['practice'] for p in practices]
            
            result = {
                'scenario': scenario,
                'best_practices': practices,
                'recommendations': recommendations,
                'practice_count': len(practices)
            }
            
            self._log(f"Best practices retrieved: {len(practices)} practices")
            
            return self._create_response(
                success=True,
                data=result,
                sources=['industry_best_practices_database']
            )
            
        except Exception as e:
            self._log(f"Error retrieving best practices: {str(e)}", "ERROR")
            return self._create_response(
                success=False,
                error=str(e)
            )
