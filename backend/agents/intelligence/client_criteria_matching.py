"""
Advanced Client Criteria Matching Engine
Sophisticated matching of suppliers and regions to detailed client criteria
Multi-dimensional scoring and ranking
"""

import sys
from pathlib import Path
from typing import Dict, Any, List, Tuple
from dataclasses import dataclass
import pandas as pd
from datetime import datetime
from enum import Enum

root_path = Path(__file__).parent.parent.parent.parent
if str(root_path) not in sys.path:
    sys.path.insert(0, str(root_path))

from backend.agents.base_agent import BaseAgent


class CriteriaWeight(Enum):
    """Importance weights for criteria"""
    CRITICAL = 100
    VERY_HIGH = 85
    HIGH = 70
    MEDIUM = 50
    LOW = 25
    OPTIONAL = 10


@dataclass
class CriteriaDimension:
    """Represents one evaluation dimension"""
    dimension_name: str
    criteria: Dict[str, float]  # criterion -> score (0-100)
    weight: float  # Overall weight of this dimension
    calculated_score: float = 0.0


@dataclass
class MatchScore:
    """Score for entity matching to criteria"""
    entity_id: str
    entity_name: str
    entity_type: str  # 'supplier' or 'region'
    overall_score: float
    dimension_scores: Dict[str, float]
    strength_areas: List[str]
    weakness_areas: List[str]
    detailed_analysis: Dict[str, Any]
    rank: int = 0


class ClientCriteriaMatchingEngine(BaseAgent):
    """
    Advanced matching engine for evaluating suppliers and regions
    against detailed client criteria
    """
    
    # Default criteria weights
    DEFAULT_DIMENSION_WEIGHTS = {
        'quality': 0.25,
        'cost': 0.20,
        'reliability': 0.20,
        'capacity': 0.15,
        'sustainability': 0.10,
        'innovation': 0.10
    }
    
    def __init__(self):
        super().__init__(
            name="ClientCriteriaMatchingEngine",
            description="Advanced multi-dimensional criteria matching for suppliers and regions"
        )
    
    def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute detailed criteria matching
        
        Input:
            - entities: List[Dict] - suppliers or regions to evaluate
            - entity_type: str - 'supplier' or 'region'
            - client_criteria: Dict - detailed criteria and weights
            - benchmark_data: Dict - market benchmarks
            - comparison_mode: str - 'absolute', 'relative', 'hybrid'
        """
        try:
            match_id = f"MATCH_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            entities = input_data.get('entities', [])
            entity_type = input_data.get('entity_type', 'supplier')
            client_criteria = input_data.get('client_criteria', self._get_default_criteria())
            benchmark_data = input_data.get('benchmark_data', {})
            comparison_mode = input_data.get('comparison_mode', 'hybrid')
            
            self._log(f"[{match_id}] Matching {len(entities)} {entity_type}s against criteria")
            
            # Evaluate each entity
            match_scores = []
            for entity in entities:
                score = self._evaluate_entity(
                    entity, entity_type, client_criteria, benchmark_data, comparison_mode
                )
                match_scores.append(score)
            
            # Sort by score
            match_scores = sorted(match_scores, key=lambda x: x.overall_score, reverse=True)
            
            # Add ranks
            for rank, score in enumerate(match_scores, 1):
                score.rank = rank
            
            # Perform comparative analysis
            comparative_analysis = self._perform_comparative_analysis(
                match_scores, entities, benchmark_data
            )
            
            # Generate detailed report
            result = {
                'match_id': match_id,
                'timestamp': datetime.now().isoformat(),
                'entity_type': entity_type,
                'total_entities_evaluated': len(entities),
                'scores': [self._score_to_dict(s) for s in match_scores],
                'top_3_matches': [self._score_to_dict(s) for s in match_scores[:3]],
                'comparative_analysis': comparative_analysis,
                'scoring_summary': self._generate_scoring_summary(match_scores),
                'recommendations': self._generate_matching_recommendations(match_scores, entity_type),
                'detailed_scorecards': self._generate_scorecards(match_scores[:5])
            }
            
            self._log(f"[{match_id}] Matching complete. Top match: {match_scores[0].entity_name}")
            
            return self._create_response(
                success=True,
                data=result
            )
            
        except Exception as e:
            self._log(f"Error in criteria matching: {str(e)}", "ERROR")
            return self._create_response(
                success=False,
                error=str(e)
            )
    
    def _get_default_criteria(self) -> Dict:
        """Get default evaluation criteria"""
        return {
            'quality': {
                'quality_rating': {'weight': 0.4, 'target': 4.5, 'range': (0, 5)},
                'certifications': {'weight': 0.3, 'target': 'multiple', 'range': (0, 5)},
                'defect_rate': {'weight': 0.3, 'target': 'low', 'range': (0, 5)}
            },
            'cost': {
                'list_price': {'weight': 0.5, 'target': 'low', 'range': (0, 100)},
                'volume_discounts': {'weight': 0.3, 'target': 'high', 'range': (0, 5)},
                'payment_terms': {'weight': 0.2, 'target': 'favorable', 'range': (0, 5)}
            },
            'reliability': {
                'delivery_reliability': {'weight': 0.4, 'target': 95, 'range': (0, 100)},
                'lead_time_consistency': {'weight': 0.3, 'target': 'low_variance', 'range': (0, 5)},
                'supply_continuity': {'weight': 0.3, 'target': 'guaranteed', 'range': (0, 5)}
            },
            'capacity': {
                'annual_capacity': {'weight': 0.4, 'target': 'high', 'range': (0, 10000)},
                'capacity_utilization': {'weight': 0.4, 'target': 'moderate', 'range': (0, 100)},
                'expansion_capability': {'weight': 0.2, 'target': 'yes', 'range': (0, 5)}
            },
            'sustainability': {
                'environmental_certifications': {'weight': 0.4, 'target': 'multiple', 'range': (0, 5)},
                'carbon_footprint': {'weight': 0.3, 'target': 'low', 'range': (0, 5)},
                'social_compliance': {'weight': 0.3, 'target': 'strong', 'range': (0, 5)}
            },
            'innovation': {
                'r_and_d_investment': {'weight': 0.4, 'target': 'high', 'range': (0, 5)},
                'product_development': {'weight': 0.4, 'target': 'active', 'range': (0, 5)},
                'technology_adoption': {'weight': 0.2, 'target': 'modern', 'range': (0, 5)}
            }
        }
    
    def _evaluate_entity(
        self, entity: Dict, entity_type: str, client_criteria: Dict,
        benchmark_data: Dict, comparison_mode: str
    ) -> MatchScore:
        """Evaluate single entity against criteria"""
        
        dimension_scores = {}
        strengths = []
        weaknesses = []
        detailed_analysis = {}
        
        # Evaluate each dimension
        for dimension, criteria_set in client_criteria.items():
            dimension_score = self._evaluate_dimension(
                entity, dimension, criteria_set, benchmark_data, entity_type, comparison_mode
            )
            dimension_scores[dimension] = dimension_score
            
            # Track strengths and weaknesses
            if dimension_score > 80:
                strengths.append(dimension)
            elif dimension_score < 40:
                weaknesses.append(dimension)
            
            # Detailed analysis
            detailed_analysis[dimension] = {
                'score': round(dimension_score, 2),
                'analysis': self._analyze_dimension_performance(
                    entity, dimension, criteria_set, dimension_score
                )
            }
        
        # Calculate weighted overall score
        weights = self.DEFAULT_DIMENSION_WEIGHTS
        overall_score = sum([
            dimension_scores.get(dim, 0) * weights.get(dim, 0)
            for dim in dimension_scores.keys()
        ]) / sum(weights.values())
        
        return MatchScore(
            entity_id=entity.get('id') or entity.get('supplier_id') or entity.get('region'),
            entity_name=entity.get('name') or entity.get('supplier_name') or entity.get('region'),
            entity_type=entity_type,
            overall_score=overall_score,
            dimension_scores=dimension_scores,
            strength_areas=strengths,
            weakness_areas=weaknesses,
            detailed_analysis=detailed_analysis
        )
    
    def _evaluate_dimension(
        self, entity: Dict, dimension: str, criteria_set: Dict,
        benchmark_data: Dict, entity_type: str, comparison_mode: str
    ) -> float:
        """Evaluate single dimension"""
        
        dimension_scores = []
        
        for criterion, criterion_config in criteria_set.items():
            criterion_weight = criterion_config.get('weight', 1.0)
            target = criterion_config.get('target')
            value_range = criterion_config.get('range', (0, 100))
            
            # Get entity value for this criterion
            entity_value = self._get_entity_criterion_value(entity, dimension, criterion)
            
            # Get benchmark if available
            benchmark_value = benchmark_data.get(f"{dimension}_{criterion}", target)
            
            # Calculate score
            score = self._calculate_criterion_score(
                entity_value, target, benchmark_value, value_range, comparison_mode
            )
            
            weighted_score = score * criterion_weight
            dimension_scores.append(weighted_score)
        
        # Average dimension score
        avg_dimension_score = sum(dimension_scores) / len(dimension_scores) if dimension_scores else 50
        
        return avg_dimension_score
    
    def _get_entity_criterion_value(self, entity: Dict, dimension: str, criterion: str) -> Any:
        """Get entity value for specific criterion"""
        
        # Try direct mapping
        possible_keys = [
            f"{dimension}_{criterion}",
            f"{criterion}",
            f"{dimension}",
            criterion.lower(),
            criterion.replace('_', ' ').lower()
        ]
        
        for key in possible_keys:
            if key in entity:
                return entity[key]
        
        # Return default if not found
        return 0
    
    def _calculate_criterion_score(
        self, entity_value: Any, target: Any, benchmark: Any, value_range: Tuple, comparison_mode: str
    ) -> float:
        """Calculate score for single criterion (0-100)"""
        
        # Handle None/missing values
        if entity_value is None:
            return 0
        
        # Numeric comparison
        if isinstance(entity_value, (int, float)) and isinstance(target, (int, float)):
            return self._numeric_score(entity_value, target, value_range, comparison_mode)
        
        # String/categorical comparison
        elif isinstance(entity_value, str):
            return self._categorical_score(entity_value, target)
        
        # Boolean
        elif isinstance(entity_value, bool):
            return 100 if entity_value else 0
        
        else:
            return 50  # Default neutral score
    
    def _numeric_score(
        self, entity_value: float, target: float, value_range: Tuple, comparison_mode: str
    ) -> float:
        """Score numeric criterion"""
        
        min_val, max_val = value_range
        
        if comparison_mode == 'absolute':
            # Direct comparison to target
            if entity_value >= target:
                return min(100, (entity_value / max(target, 1)) * 100)
            else:
                return (entity_value / max(target, 1)) * 100
        
        elif comparison_mode == 'relative':
            # Normalize to range
            normalized = (entity_value - min_val) / (max_val - min_val + 1)
            return min(100, max(0, normalized * 100))
        
        else:  # hybrid
            # Combine both approaches
            absolute_score = self._numeric_score(entity_value, target, value_range, 'absolute')
            relative_score = self._numeric_score(entity_value, target, value_range, 'relative')
            return (absolute_score * 0.6) + (relative_score * 0.4)
    
    def _categorical_score(self, entity_value: str, target: Any) -> float:
        """Score categorical criterion"""
        
        if isinstance(target, str):
            if entity_value.lower() == target.lower():
                return 100
            elif entity_value.lower().startswith(target.lower()):
                return 80
            else:
                return 40
        
        elif target == 'multiple':
            # Count how many values
            count = len(str(entity_value).split(','))
            return min(100, count * 20)
        
        elif target in ['high', 'good', 'strong', 'modern']:
            value_lower = entity_value.lower()
            if value_lower in ['high', 'good', 'strong', 'modern', 'yes', 'excellent']:
                return 90
            elif value_lower in ['medium', 'moderate', 'fair']:
                return 60
            else:
                return 30
        
        elif target in ['low', 'minimal', 'none']:
            value_lower = entity_value.lower()
            if value_lower in ['low', 'minimal', 'none', 'no']:
                return 90
            elif value_lower in ['medium', 'moderate']:
                return 60
            else:
                return 30
        
        else:
            return 50
    
    def _analyze_dimension_performance(
        self, entity: Dict, dimension: str, criteria_set: Dict, score: float
    ) -> str:
        """Generate performance analysis for dimension"""
        
        if score > 85:
            return f"Excellent {dimension} performance"
        elif score > 70:
            return f"Strong {dimension} performance"
        elif score > 50:
            return f"Adequate {dimension} performance"
        elif score > 30:
            return f"Weak {dimension} performance"
        else:
            return f"Poor {dimension} performance"
    
    def _perform_comparative_analysis(
        self, match_scores: List[MatchScore], entities: List[Dict], benchmark_data: Dict
    ) -> Dict:
        """Perform comparative analysis across all entities"""
        
        if len(match_scores) < 2:
            return {}
        
        # Gap analysis
        top_score = match_scores[0].overall_score
        scores = [s.overall_score for s in match_scores]
        
        return {
            'score_range': {
                'min': round(min(scores), 2),
                'max': round(max(scores), 2),
                'avg': round(sum(scores) / len(scores), 2),
                'gap_between_top_2': round(match_scores[0].overall_score - (match_scores[1].overall_score if len(match_scores) > 1 else 0), 2)
            },
            'dimension_leaders': self._identify_dimension_leaders(match_scores),
            'dimension_laggards': self._identify_dimension_laggards(match_scores),
            'diversity_index': self._calculate_diversity_index(match_scores)
        }
    
    def _identify_dimension_leaders(self, match_scores: List[MatchScore]) -> Dict[str, str]:
        """Identify best entity in each dimension"""
        
        leaders = {}
        dimensions = self.DEFAULT_DIMENSION_WEIGHTS.keys()
        
        for dimension in dimensions:
            best_entity = max(
                match_scores,
                key=lambda x: x.dimension_scores.get(dimension, 0)
            )
            leaders[dimension] = best_entity.entity_name
        
        return leaders
    
    def _identify_dimension_laggards(self, match_scores: List[MatchScore]) -> Dict[str, str]:
        """Identify weakest entity in each dimension"""
        
        laggards = {}
        dimensions = self.DEFAULT_DIMENSION_WEIGHTS.keys()
        
        for dimension in dimensions:
            worst_entity = min(
                match_scores,
                key=lambda x: x.dimension_scores.get(dimension, 100)
            )
            laggards[dimension] = worst_entity.entity_name
        
        return laggards
    
    def _calculate_diversity_index(self, match_scores: List[MatchScore]) -> float:
        """Calculate how diverse the scores are (0-100)"""
        
        scores = [s.overall_score for s in match_scores]
        avg_score = sum(scores) / len(scores)
        variance = sum([(s - avg_score) ** 2 for s in scores]) / len(scores)
        
        # Normalize to 0-100 scale
        std_dev = variance ** 0.5
        diversity = min(100, std_dev * 5)  # Scale factor
        
        return round(diversity, 2)
    
    def _generate_scoring_summary(self, match_scores: List[MatchScore]) -> Dict:
        """Generate overall scoring summary"""
        
        return {
            'total_entities': len(match_scores),
            'excellent_matches': len([s for s in match_scores if s.overall_score > 80]),
            'good_matches': len([s for s in match_scores if 70 <= s.overall_score <= 80]),
            'fair_matches': len([s for s in match_scores if 50 <= s.overall_score < 70]),
            'poor_matches': len([s for s in match_scores if s.overall_score < 50]),
            'average_score': round(sum([s.overall_score for s in match_scores]) / len(match_scores), 2),
            'median_score': round(sorted([s.overall_score for s in match_scores])[len(match_scores)//2], 2)
        }
    
    def _generate_matching_recommendations(
        self, match_scores: List[MatchScore], entity_type: str
    ) -> List[str]:
        """Generate recommendations based on matching results"""
        
        recommendations = []
        
        if match_scores[0].overall_score > 85:
            recommendations.append(
                f"🟢 HIGHLY RECOMMENDED: {match_scores[0].entity_name} is an excellent match"
            )
        elif match_scores[0].overall_score > 70:
            recommendations.append(
                f"🟡 RECOMMENDED: {match_scores[0].entity_name} meets requirements with room for improvement"
            )
        else:
            recommendations.append(
                f"🔴 PROCEED WITH CAUTION: Top match has significant gaps in key areas"
            )
        
        if len(match_scores) > 1 and match_scores[1].overall_score > 75:
            recommendations.append(
                f"💡 BACKUP OPTION: {match_scores[1].entity_name} is a strong alternative"
            )
        
        return recommendations
    
    def _generate_scorecards(self, top_entities: List[MatchScore]) -> List[Dict]:
        """Generate detailed scorecards for top entities"""
        
        scorecards = []
        
        for entity in top_entities:
            scorecard = {
                'entity_name': entity.entity_name,
                'overall_score': round(entity.overall_score, 2),
                'rank': entity.rank,
                'dimension_scores': {
                    dim: round(score, 2)
                    for dim, score in entity.dimension_scores.items()
                },
                'strengths': entity.strength_areas,
                'weaknesses': entity.weakness_areas,
                'detailed_analysis': entity.detailed_analysis
            }
            scorecards.append(scorecard)
        
        return scorecards
    
    def _score_to_dict(self, score: MatchScore) -> Dict:
        """Convert MatchScore to dictionary"""
        return {
            'entity_id': score.entity_id,
            'entity_name': score.entity_name,
            'overall_score': round(score.overall_score, 2),
            'rank': score.rank,
            'dimension_scores': {
                dim: round(s, 2) for dim, s in score.dimension_scores.items()
            },
            'strengths': score.strength_areas,
            'weaknesses': score.weakness_areas
        }
