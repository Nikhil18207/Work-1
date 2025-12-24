"""
Confidence Score Calculator
Calculates dynamic confidence scores based on data availability and quality
"""

from typing import Dict, List, Any, Tuple
from enum import Enum
import pandas as pd


class DataCompleteness(Enum):
    """Data completeness levels"""
    COMPLETE = "COMPLETE"           # 100% - All data available
    MOSTLY_COMPLETE = "MOSTLY_COMPLETE"  # 75-99% - Minor gaps
    PARTIAL = "PARTIAL"             # 50-74% - Significant gaps
    LIMITED = "LIMITED"             # 25-49% - Major gaps
    MINIMAL = "MINIMAL"             # <25% - Very limited data


class ConfidenceScoreCalculator:
    """
    Calculates confidence scores based on:
    1. Data availability
    2. Rule coverage
    3. Recommendation specificity
    4. Data quality
    """

    def __init__(self):
        self.max_score = 100.0
        
        # Weight distribution
        self.weights = {
            'data_availability': 0.40,      # 40% - Most important
            'rule_coverage': 0.25,          # 25% - Rule evaluation
            'recommendation_quality': 0.20, # 20% - Specificity
            'data_quality': 0.15           # 15% - Data freshness/accuracy
        }

    def calculate_confidence(
        self,
        available_data: Dict[str, bool],
        rules_evaluated: List[str],
        recommendations_count: int,
        data_quality_score: float = 1.0
    ) -> Dict[str, Any]:
        """
        Calculate comprehensive confidence score
        
        Args:
            available_data: Dict of data sources and availability
                           e.g., {'spend_data': True, 'contracts': True, 'market_data': False}
            rules_evaluated: List of rule IDs evaluated (e.g., ['R001', 'R002'])
            recommendations_count: Number of specific recommendations
            data_quality_score: Data quality (0-1), default 1.0
            
        Returns:
            Confidence score breakdown
        """
        # 1. Data Availability Score (40%)
        data_score = self._calculate_data_availability(available_data)
        
        # 2. Rule Coverage Score (25%)
        rule_score = self._calculate_rule_coverage(rules_evaluated)
        
        # 3. Recommendation Quality Score (20%)
        rec_score = self._calculate_recommendation_quality(recommendations_count)
        
        # 4. Data Quality Score (15%)
        quality_score = data_quality_score * 100
        
        # Calculate weighted total
        total_score = (
            data_score * self.weights['data_availability'] +
            rule_score * self.weights['rule_coverage'] +
            rec_score * self.weights['recommendation_quality'] +
            quality_score * self.weights['data_quality']
        )
        
        # Determine confidence level
        confidence_level = self._get_confidence_level(total_score)
        
        # Calculate potential score
        potential_score = self._calculate_potential_score(available_data)
        
        # Identify missing data
        missing_data = self._identify_missing_data(available_data)
        
        return {
            'current_confidence': round(total_score, 2),
            'confidence_level': confidence_level,
            'potential_confidence': round(potential_score, 2),
            'confidence_gap': round(potential_score - total_score, 2),
            'breakdown': {
                'data_availability': round(data_score, 2),
                'rule_coverage': round(rule_score, 2),
                'recommendation_quality': round(rec_score, 2),
                'data_quality': round(quality_score, 2)
            },
            'missing_data': missing_data,
            'improvement_suggestions': self._get_improvement_suggestions(missing_data, total_score)
        }

    def _calculate_data_availability(self, available_data: Dict[str, bool]) -> float:
        """Calculate data availability score (0-100)"""
        if not available_data:
            return 0.0
        
        # Define critical vs optional data
        critical_data = ['spend_data', 'supplier_contracts', 'rule_book']
        optional_data = ['market_data', 'pricing_benchmarks', 'historical_trends', 
                        'supplier_performance', 'risk_assessments']
        
        # Calculate critical data score (70% weight)
        critical_available = sum(1 for key in critical_data if available_data.get(key, False))
        critical_score = (critical_available / len(critical_data)) * 70
        
        # Calculate optional data score (30% weight)
        optional_available = sum(1 for key in optional_data if available_data.get(key, False))
        optional_score = (optional_available / len(optional_data)) * 30 if optional_data else 0
        
        return critical_score + optional_score

    def _calculate_rule_coverage(self, rules_evaluated: List[str]) -> float:
        """Calculate rule coverage score (0-100)"""
        # Define all possible rules
        all_rules = ['R001', 'R002', 'R003', 'R004', 'R005', 'R006']
        
        if not rules_evaluated:
            return 0.0
        
        # Score based on rules evaluated
        coverage = len(rules_evaluated) / len(all_rules)
        
        # Bonus for critical rules (R001, R002)
        critical_rules = ['R001', 'R002']
        critical_evaluated = sum(1 for r in critical_rules if r in rules_evaluated)
        critical_bonus = (critical_evaluated / len(critical_rules)) * 20
        
        return min((coverage * 80) + critical_bonus, 100.0)

    def _calculate_recommendation_quality(self, recommendations_count: int) -> float:
        """Calculate recommendation quality score (0-100)"""
        # Score based on number of specific recommendations
        if recommendations_count == 0:
            return 0.0
        elif recommendations_count == 1:
            return 40.0
        elif recommendations_count == 2:
            return 70.0
        elif recommendations_count >= 3:
            return 100.0
        return 0.0

    def _get_confidence_level(self, score: float) -> str:
        """Get confidence level from score"""
        if score >= 90:
            return "VERY HIGH"
        elif score >= 75:
            return "HIGH"
        elif score >= 60:
            return "MEDIUM"
        elif score >= 40:
            return "LOW"
        else:
            return "VERY LOW"

    def _calculate_potential_score(self, available_data: Dict[str, bool]) -> float:
        """Calculate potential score if all data was available"""
        # Assume all data available
        all_data = {
            'spend_data': True,
            'supplier_contracts': True,
            'rule_book': True,
            'market_data': True,
            'pricing_benchmarks': True,
            'historical_trends': True,
            'supplier_performance': True,
            'risk_assessments': True
        }
        
        # Calculate with all data
        data_score = self._calculate_data_availability(all_data)
        rule_score = 100.0  # All rules evaluated
        rec_score = 100.0   # Maximum recommendations
        quality_score = 100.0  # Perfect quality
        
        return (
            data_score * self.weights['data_availability'] +
            rule_score * self.weights['rule_coverage'] +
            rec_score * self.weights['recommendation_quality'] +
            quality_score * self.weights['data_quality']
        )

    def _identify_missing_data(self, available_data: Dict[str, bool]) -> List[Dict[str, str]]:
        """Identify missing data sources"""
        all_data_sources = {
            'spend_data': {
                'name': 'Spend Data',
                'impact': 'HIGH',
                'description': 'Historical procurement transactions',
                'confidence_boost': '+25%'
            },
            'supplier_contracts': {
                'name': 'Supplier Contracts',
                'impact': 'HIGH',
                'description': 'Contract terms, ESG scores, payment terms',
                'confidence_boost': '+20%'
            },
            'rule_book': {
                'name': 'Rule Book',
                'impact': 'HIGH',
                'description': 'Business rules and thresholds',
                'confidence_boost': '+15%'
            },
            'market_data': {
                'name': 'Market Data',
                'impact': 'MEDIUM',
                'description': 'Market pricing, trends, forecasts',
                'confidence_boost': '+10%'
            },
            'pricing_benchmarks': {
                'name': 'Pricing Benchmarks',
                'impact': 'MEDIUM',
                'description': 'Industry pricing standards',
                'confidence_boost': '+8%'
            },
            'historical_trends': {
                'name': 'Historical Trends',
                'impact': 'MEDIUM',
                'description': 'Past performance and patterns',
                'confidence_boost': '+7%'
            },
            'supplier_performance': {
                'name': 'Supplier Performance',
                'impact': 'LOW',
                'description': 'Quality metrics, delivery times',
                'confidence_boost': '+5%'
            },
            'risk_assessments': {
                'name': 'Risk Assessments',
                'impact': 'LOW',
                'description': 'Supplier risk profiles',
                'confidence_boost': '+5%'
            }
        }
        
        missing = []
        for key, info in all_data_sources.items():
            if not available_data.get(key, False):
                missing.append({
                    'data_source': info['name'],
                    'impact': info['impact'],
                    'description': info['description'],
                    'confidence_boost': info['confidence_boost']
                })
        
        return missing

    def _get_improvement_suggestions(
        self,
        missing_data: List[Dict[str, str]],
        current_score: float
    ) -> List[str]:
        """Get suggestions to improve confidence"""
        suggestions = []
        
        # Suggest adding high-impact missing data
        high_impact = [d for d in missing_data if d['impact'] == 'HIGH']
        if high_impact:
            suggestions.append(
                f"Add {len(high_impact)} critical data source(s): " +
                ", ".join(d['data_source'] for d in high_impact[:3])
            )
        
        # Suggest adding more rules
        if current_score < 75:
            suggestions.append(
                "Evaluate additional business rules (R003-R006) for comprehensive analysis"
            )
        
        # Suggest more specific recommendations
        if current_score < 80:
            suggestions.append(
                "Provide more specific recommendations with named suppliers and quantified impacts"
            )
        
        # Suggest data quality improvements
        medium_impact = [d for d in missing_data if d['impact'] == 'MEDIUM']
        if medium_impact:
            suggestions.append(
                f"Consider adding: {', '.join(d['data_source'] for d in medium_impact[:2])}"
            )
        
        return suggestions

    def format_confidence_report(self, confidence_data: Dict[str, Any]) -> str:
        """Format confidence data as readable report"""
        report = f"""
## CONFIDENCE SCORE ANALYSIS

**Current Confidence:** {confidence_data['current_confidence']}% ({confidence_data['confidence_level']})
**Potential Confidence:** {confidence_data['potential_confidence']}% (with all data)
**Confidence Gap:** {confidence_data['confidence_gap']}%

### Score Breakdown:
- Data Availability: {confidence_data['breakdown']['data_availability']}/100 (40% weight)
- Rule Coverage: {confidence_data['breakdown']['rule_coverage']}/100 (25% weight)
- Recommendation Quality: {confidence_data['breakdown']['recommendation_quality']}/100 (20% weight)
- Data Quality: {confidence_data['breakdown']['data_quality']}/100 (15% weight)

"""
        
        if confidence_data['missing_data']:
            report += "### Missing Data Sources:\n"
            for data in confidence_data['missing_data']:
                report += f"- **{data['data_source']}** ({data['impact']} impact)\n"
                report += f"  {data['description']}\n"
                report += f"  Potential boost: {data['confidence_boost']}\n\n"
        
        if confidence_data['improvement_suggestions']:
            report += "### Improvement Suggestions:\n"
            for i, suggestion in enumerate(confidence_data['improvement_suggestions'], 1):
                report += f"{i}. {suggestion}\n"
        
        return report


# Example usage
if __name__ == "__main__":
    calculator = ConfidenceScoreCalculator()
    
    # Example 1: Current system (spend data + contracts + rules)
    print("=" * 80)
    print("EXAMPLE 1: CURRENT SYSTEM")
    print("=" * 80)
    
    current_data = {
        'spend_data': True,
        'supplier_contracts': True,
        'rule_book': True,
        'market_data': False,
        'pricing_benchmarks': False,
        'historical_trends': False,
        'supplier_performance': False,
        'risk_assessments': False
    }
    
    confidence = calculator.calculate_confidence(
        available_data=current_data,
        rules_evaluated=['R001', 'R002'],
        recommendations_count=3,
        data_quality_score=1.0
    )
    
    print(calculator.format_confidence_report(confidence))
    
    # Example 2: Limited data
    print("\n" + "=" * 80)
    print("EXAMPLE 2: LIMITED DATA")
    print("=" * 80)
    
    limited_data = {
        'spend_data': True,
        'supplier_contracts': False,
        'rule_book': True,
        'market_data': False
    }
    
    confidence_limited = calculator.calculate_confidence(
        available_data=limited_data,
        rules_evaluated=['R001'],
        recommendations_count=1,
        data_quality_score=0.8
    )
    
    print(calculator.format_confidence_report(confidence_limited))
