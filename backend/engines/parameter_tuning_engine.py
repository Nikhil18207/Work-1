"""
Logic-Based Parameter Tuning Engine
Dynamically adjusts thresholds and parameters based on context and data
"""

import sys
from pathlib import Path
from typing import Dict, Any, List
from datetime import datetime
import pandas as pd

root_path = Path(__file__).parent.parent.parent.parent
if str(root_path) not in sys.path:
    sys.path.insert(0, str(root_path))

from backend.agents.base_agent import BaseAgent
from backend.engines.data_loader import DataLoader


class ParameterTuningEngine(BaseAgent):
    """
    Engine for logic-based parameter tuning
    
    Features:
        - Dynamic threshold adjustment
        - Context-aware parameter optimization
        - Risk-based tuning
        - Historical performance analysis
        - Adaptive learning from outcomes
    """
    
    # Default parameters
    DEFAULT_PARAMS = {
        'supplier_concentration_max': 30.0,
        'supplier_concentration_ideal': 20.0,
        'region_concentration_max': 50.0,
        'min_quality_rating': 4.0,
        'min_delivery_reliability': 90.0,
        'price_variance_tolerance': 10.0,
        'capacity_utilization_threshold': 80.0
    }
    
    def __init__(self):
        super().__init__(
            name="ParameterTuning",
            description="Dynamically tunes parameters based on context and data"
        )
        self.data_loader = DataLoader()
        self.tuning_history = []
    
    def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute parameter tuning
        
        Input:
            - client_id: str
            - category: str (optional)
            - tuning_mode: str - 'conservative', 'balanced', 'aggressive'
            - context: Dict (optional) - additional context for tuning
            - parameters_to_tune: List[str] (optional) - specific parameters to tune
        """
        try:
            tuning_id = f"TUNE_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            self._log(f"[{tuning_id}] Parameter tuning request: {input_data}")
            
            # Load data for analysis
            spend_df = self.data_loader.load_spend_data()
            supplier_df = self.data_loader.load_supplier_master()
            
            # Filter data
            filtered_spend = spend_df.copy()
            if input_data.get('client_id'):
                filtered_spend = filtered_spend[filtered_spend['Client_ID'] == input_data['client_id']]
            
            if input_data.get('category'):
                filtered_spend = filtered_spend[filtered_spend['Category'] == input_data['category']]
            
            if filtered_spend.empty:
                return self._create_response(
                    success=False,
                    error="No data found for parameter tuning"
                )
            
            # Analyze current state
            current_state = self._analyze_current_state(filtered_spend, supplier_df)
            
            # Determine tuning mode
            tuning_mode = input_data.get('tuning_mode', 'balanced')
            
            # Tune parameters
            tuned_parameters = self._tune_parameters(
                current_state, tuning_mode, input_data
            )
            
            # Validate tuned parameters
            validation_results = self._validate_tuned_parameters(
                tuned_parameters, current_state
            )
            
            # Calculate impact
            impact_analysis = self._calculate_tuning_impact(
                tuned_parameters, current_state
            )
            
            # Generate recommendations
            recommendations = self._generate_tuning_recommendations(
                tuned_parameters, validation_results, impact_analysis
            )
            
            # Record tuning
            tuning_record = {
                'tuning_id': tuning_id,
                'timestamp': datetime.now().isoformat(),
                'client_id': input_data.get('client_id'),
                'category': input_data.get('category'),
                'tuning_mode': tuning_mode,
                'default_parameters': self.DEFAULT_PARAMS.copy(),
                'tuned_parameters': tuned_parameters,
                'current_state': current_state,
                'validation_results': validation_results,
                'impact_analysis': impact_analysis,
                'recommendations': recommendations
            }
            
            self.tuning_history.append(tuning_record)
            
            self._log(f"[{tuning_id}] Parameter tuning complete")
            
            return self._create_response(
                success=True,
                data=tuning_record,
                sources=['spend_data.csv', 'supplier_master.csv']
            )
            
        except Exception as e:
            self._log(f"Error in parameter tuning: {str(e)}", "ERROR")
            return self._create_response(
                success=False,
                error=str(e)
            )
    
    def _analyze_current_state(
        self, spend_df: pd.DataFrame, supplier_df: pd.DataFrame
    ) -> Dict:
        """Analyze current state to inform parameter tuning"""
        total_spend = spend_df['Spend_USD'].sum()
        
        # Supplier metrics
        supplier_concentration = spend_df.groupby('Supplier_ID').agg({
            'Spend_USD': 'sum'
        }).reset_index()
        supplier_concentration['percentage'] = (
            supplier_concentration['Spend_USD'] / total_spend * 100
        )
        
        # Region metrics
        region_concentration = spend_df.groupby('Supplier_Region').agg({
            'Spend_USD': 'sum',
            'Supplier_ID': 'nunique'
        }).reset_index()
        region_concentration['percentage'] = (
            region_concentration['Spend_USD'] / total_spend * 100
        )
        
        # Quality and performance
        active_suppliers = spend_df['Supplier_ID'].unique()
        active_supplier_data = supplier_df[supplier_df['supplier_id'].isin(active_suppliers)]
        
        return {
            'total_spend': total_spend,
            'supplier_count': len(active_suppliers),
            'region_count': spend_df['Supplier_Region'].nunique(),
            'max_supplier_concentration': supplier_concentration['percentage'].max(),
            'avg_supplier_concentration': supplier_concentration['percentage'].mean(),
            'max_region_concentration': region_concentration['percentage'].max(),
            'avg_quality_rating': active_supplier_data['quality_rating'].mean(),
            'min_quality_rating': active_supplier_data['quality_rating'].min(),
            'avg_delivery_reliability': active_supplier_data['delivery_reliability_pct'].mean(),
            'price_variance': spend_df['Spend_USD'].std() / spend_df['Spend_USD'].mean() * 100,
            'supplier_distribution': supplier_concentration.to_dict('records'),
            'region_distribution': region_concentration.to_dict('records')
        }
    
    def _tune_parameters(
        self, current_state: Dict, tuning_mode: str, input_data: Dict
    ) -> Dict:
        """Tune parameters based on current state and mode"""
        tuned = self.DEFAULT_PARAMS.copy()
        
        # Get parameters to tune
        params_to_tune = input_data.get('parameters_to_tune', list(self.DEFAULT_PARAMS.keys()))
        
        # Apply tuning logic based on mode
        if tuning_mode == 'conservative':
            tuned = self._apply_conservative_tuning(tuned, current_state, params_to_tune)
        elif tuning_mode == 'aggressive':
            tuned = self._apply_aggressive_tuning(tuned, current_state, params_to_tune)
        else:  # balanced
            tuned = self._apply_balanced_tuning(tuned, current_state, params_to_tune)
        
        # Apply context-specific adjustments
        if input_data.get('context'):
            tuned = self._apply_context_adjustments(tuned, input_data['context'])
        
        return tuned
    
    def _apply_conservative_tuning(
        self, params: Dict, state: Dict, params_to_tune: List[str]
    ) -> Dict:
        """Apply conservative tuning - stricter thresholds"""
        tuned = params.copy()
        
        # Stricter concentration limits
        if 'supplier_concentration_max' in params_to_tune:
            # If current max is high, be more conservative
            if state['max_supplier_concentration'] > 35:
                tuned['supplier_concentration_max'] = 25.0
            else:
                tuned['supplier_concentration_max'] = 28.0
        
        if 'supplier_concentration_ideal' in params_to_tune:
            tuned['supplier_concentration_ideal'] = 15.0
        
        if 'region_concentration_max' in params_to_tune:
            if state['max_region_concentration'] > 60:
                tuned['region_concentration_max'] = 40.0
            else:
                tuned['region_concentration_max'] = 45.0
        
        # Stricter quality requirements
        if 'min_quality_rating' in params_to_tune:
            tuned['min_quality_rating'] = 4.5
        
        if 'min_delivery_reliability' in params_to_tune:
            tuned['min_delivery_reliability'] = 95.0
        
        # Lower price variance tolerance
        if 'price_variance_tolerance' in params_to_tune:
            tuned['price_variance_tolerance'] = 8.0
        
        return tuned
    
    def _apply_balanced_tuning(
        self, params: Dict, state: Dict, params_to_tune: List[str]
    ) -> Dict:
        """Apply balanced tuning - moderate adjustments"""
        tuned = params.copy()
        
        # Adjust based on current state
        if 'supplier_concentration_max' in params_to_tune:
            if state['max_supplier_concentration'] > 40:
                # Currently too concentrated, tighten
                tuned['supplier_concentration_max'] = 28.0
            elif state['max_supplier_concentration'] < 20:
                # Well diversified, can be slightly more flexible
                tuned['supplier_concentration_max'] = 32.0
            # else keep default 30.0
        
        if 'supplier_concentration_ideal' in params_to_tune:
            # Adjust ideal based on supplier count
            if state['supplier_count'] < 3:
                tuned['supplier_concentration_ideal'] = 25.0  # Fewer suppliers, higher ideal
            elif state['supplier_count'] > 10:
                tuned['supplier_concentration_ideal'] = 15.0  # Many suppliers, lower ideal
        
        if 'min_quality_rating' in params_to_tune:
            # Adjust based on average quality
            if state['avg_quality_rating'] >= 4.5:
                tuned['min_quality_rating'] = 4.3  # High average, can maintain high standard
            elif state['avg_quality_rating'] < 4.0:
                tuned['min_quality_rating'] = 3.8  # Lower average, slightly more flexible
        
        if 'min_delivery_reliability' in params_to_tune:
            if state['avg_delivery_reliability'] >= 95:
                tuned['min_delivery_reliability'] = 92.0
            elif state['avg_delivery_reliability'] < 90:
                tuned['min_delivery_reliability'] = 88.0
        
        return tuned
    
    def _apply_aggressive_tuning(
        self, params: Dict, state: Dict, params_to_tune: List[str]
    ) -> Dict:
        """Apply aggressive tuning - more flexible thresholds"""
        tuned = params.copy()
        
        # More flexible concentration limits
        if 'supplier_concentration_max' in params_to_tune:
            tuned['supplier_concentration_max'] = 35.0
        
        if 'supplier_concentration_ideal' in params_to_tune:
            tuned['supplier_concentration_ideal'] = 25.0
        
        if 'region_concentration_max' in params_to_tune:
            tuned['region_concentration_max'] = 60.0
        
        # More flexible quality requirements
        if 'min_quality_rating' in params_to_tune:
            tuned['min_quality_rating'] = 3.5
        
        if 'min_delivery_reliability' in params_to_tune:
            tuned['min_delivery_reliability'] = 85.0
        
        # Higher price variance tolerance
        if 'price_variance_tolerance' in params_to_tune:
            tuned['price_variance_tolerance'] = 15.0
        
        return tuned
    
    def _apply_context_adjustments(self, params: Dict, context: Dict) -> Dict:
        """Apply context-specific adjustments"""
        tuned = params.copy()
        
        # Market volatility adjustment
        if context.get('market_volatility') == 'HIGH':
            tuned['price_variance_tolerance'] *= 1.5
            tuned['min_delivery_reliability'] -= 2.0
        
        # Supply shortage adjustment
        if context.get('supply_shortage') == True:
            tuned['min_quality_rating'] -= 0.3
            tuned['supplier_concentration_max'] += 5.0
        
        # Critical category adjustment
        if context.get('category_criticality') == 'HIGH':
            tuned['min_quality_rating'] += 0.2
            tuned['min_delivery_reliability'] += 3.0
            tuned['supplier_concentration_max'] -= 5.0
        
        # New market entry adjustment
        if context.get('market_entry') == 'NEW':
            tuned['min_quality_rating'] -= 0.2
            tuned['supplier_concentration_max'] += 5.0
        
        return tuned
    
    def _validate_tuned_parameters(
        self, tuned_params: Dict, current_state: Dict
    ) -> Dict:
        """Validate tuned parameters against current state"""
        validation = {
            'valid': True,
            'warnings': [],
            'errors': [],
            'parameter_checks': {}
        }
        
        # Check supplier concentration
        if current_state['max_supplier_concentration'] > tuned_params['supplier_concentration_max']:
            validation['warnings'].append({
                'parameter': 'supplier_concentration_max',
                'message': f"Current max concentration ({current_state['max_supplier_concentration']:.1f}%) exceeds tuned threshold ({tuned_params['supplier_concentration_max']:.1f}%)",
                'action_required': 'Immediate supplier diversification needed'
            })
        
        # Check quality ratings
        if current_state['min_quality_rating'] < tuned_params['min_quality_rating']:
            validation['warnings'].append({
                'parameter': 'min_quality_rating',
                'message': f"Some suppliers below tuned minimum quality ({tuned_params['min_quality_rating']})",
                'action_required': 'Supplier improvement or replacement needed'
            })
        
        # Check region concentration
        if current_state['max_region_concentration'] > tuned_params['region_concentration_max']:
            validation['warnings'].append({
                'parameter': 'region_concentration_max',
                'message': f"Current regional concentration ({current_state['max_region_concentration']:.1f}%) exceeds threshold",
                'action_required': 'Geographic diversification needed'
            })
        
        # Validate parameter relationships
        if tuned_params['supplier_concentration_ideal'] >= tuned_params['supplier_concentration_max']:
            validation['errors'].append({
                'parameters': ['supplier_concentration_ideal', 'supplier_concentration_max'],
                'message': 'Ideal concentration must be less than maximum',
                'fix': 'Adjust ideal to be 5-10% below maximum'
            })
            validation['valid'] = False
        
        validation['parameter_checks'] = {
            'supplier_concentration_compliant': current_state['max_supplier_concentration'] <= tuned_params['supplier_concentration_max'],
            'quality_compliant': current_state['min_quality_rating'] >= tuned_params['min_quality_rating'],
            'region_concentration_compliant': current_state['max_region_concentration'] <= tuned_params['region_concentration_max']
        }
        
        return validation
    
    def _calculate_tuning_impact(
        self, tuned_params: Dict, current_state: Dict
    ) -> Dict:
        """Calculate impact of parameter tuning"""
        impact = {
            'parameter_changes': [],
            'expected_outcomes': [],
            'risk_assessment': {}
        }
        
        # Calculate changes
        for param, tuned_value in tuned_params.items():
            default_value = self.DEFAULT_PARAMS[param]
            if tuned_value != default_value:
                change_pct = ((tuned_value - default_value) / default_value * 100) if default_value != 0 else 0
                impact['parameter_changes'].append({
                    'parameter': param,
                    'default_value': default_value,
                    'tuned_value': tuned_value,
                    'change': tuned_value - default_value,
                    'change_pct': round(change_pct, 2),
                    'direction': 'STRICTER' if tuned_value < default_value else 'MORE_FLEXIBLE'
                })
        
        # Expected outcomes
        if tuned_params['supplier_concentration_max'] < self.DEFAULT_PARAMS['supplier_concentration_max']:
            impact['expected_outcomes'].append({
                'outcome': 'Increased supplier diversification',
                'impact': 'POSITIVE',
                'magnitude': 'MEDIUM',
                'timeline': '3-6 months'
            })
        
        if tuned_params['min_quality_rating'] > self.DEFAULT_PARAMS['min_quality_rating']:
            impact['expected_outcomes'].append({
                'outcome': 'Improved overall quality',
                'impact': 'POSITIVE',
                'magnitude': 'HIGH',
                'timeline': '1-3 months'
            })
        
        # Risk assessment
        strictness_score = sum(
            1 for change in impact['parameter_changes']
            if change['direction'] == 'STRICTER'
        )
        
        flexibility_score = sum(
            1 for change in impact['parameter_changes']
            if change['direction'] == 'MORE_FLEXIBLE'
        )
        
        if strictness_score > flexibility_score:
            impact['risk_assessment'] = {
                'overall_direction': 'STRICTER',
                'supplier_pool_impact': 'May reduce available supplier options',
                'cost_impact': 'Potential cost increase from higher quality requirements',
                'risk_mitigation': 'Lower supply chain risk, higher quality assurance'
            }
        elif flexibility_score > strictness_score:
            impact['risk_assessment'] = {
                'overall_direction': 'MORE_FLEXIBLE',
                'supplier_pool_impact': 'Expanded supplier options',
                'cost_impact': 'Potential cost savings',
                'risk_mitigation': 'May increase quality or concentration risks'
            }
        else:
            impact['risk_assessment'] = {
                'overall_direction': 'BALANCED',
                'supplier_pool_impact': 'Minimal change',
                'cost_impact': 'Neutral',
                'risk_mitigation': 'Balanced risk-reward profile'
            }
        
        return impact
    
    def _generate_tuning_recommendations(
        self, tuned_params: Dict, validation: Dict, impact: Dict
    ) -> List[Dict]:
        """Generate recommendations based on tuning results"""
        recommendations = []
        
        # Address validation warnings
        for warning in validation.get('warnings', []):
            recommendations.append({
                'priority': 'HIGH',
                'type': 'COMPLIANCE',
                'recommendation': f"Address {warning['parameter']} compliance issue",
                'action': warning['action_required'],
                'rationale': warning['message']
            })
        
        # Address validation errors
        for error in validation.get('errors', []):
            recommendations.append({
                'priority': 'CRITICAL',
                'type': 'PARAMETER_FIX',
                'recommendation': f"Fix parameter relationship issue",
                'action': error['fix'],
                'rationale': error['message']
            })
        
        # Recommendations based on impact
        if impact['risk_assessment']['overall_direction'] == 'STRICTER':
            recommendations.append({
                'priority': 'MEDIUM',
                'type': 'SUPPLIER_DEVELOPMENT',
                'recommendation': 'Invest in supplier development programs',
                'action': 'Help current suppliers meet stricter requirements',
                'rationale': 'Maintain supplier relationships while improving performance'
            })
        
        if impact['risk_assessment']['overall_direction'] == 'MORE_FLEXIBLE':
            recommendations.append({
                'priority': 'MEDIUM',
                'type': 'RISK_MONITORING',
                'recommendation': 'Implement enhanced monitoring',
                'action': 'Increase frequency of supplier performance reviews',
                'rationale': 'More flexible parameters require closer monitoring'
            })
        
        # General recommendation
        recommendations.append({
            'priority': 'LOW',
            'type': 'CONTINUOUS_IMPROVEMENT',
            'recommendation': 'Review and adjust parameters quarterly',
            'action': 'Schedule regular parameter tuning reviews',
            'rationale': 'Market conditions and business needs evolve over time'
        })
        
        return recommendations
