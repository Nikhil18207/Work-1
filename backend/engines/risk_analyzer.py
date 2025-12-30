"""
Risk Analyzer - Comprehensive risk assessment engine
Universal across all industries
"""

import numpy as np
from typing import Dict, Any, List
from datetime import datetime


class RiskAnalyzer:
    """Analyze procurement risks across multiple dimensions"""
    
    def __init__(self):
        self.risk_categories = {
            'supplier_concentration': 0,
            'financial_stability': 0,
            'geopolitical': 0,
            'supply_chain_resilience': 0,
            'regulatory_compliance': 0,
            'market_volatility': 0,
            'quality_risk': 0,
            'esg_risk': 0,
        }
    
    def analyze_risks(self, brief_data: Dict[str, Any]) -> Dict[str, Any]:
        """Comprehensive risk analysis"""
        
        scores = {}
        details = {}
        
        # 1. Supplier Concentration Risk
        dominant_pct = brief_data.get('dominant_supplier_pct', 0)
        concentration_score = self._calculate_concentration_risk(dominant_pct)
        scores['Supplier Concentration'] = concentration_score
        details['Supplier Concentration'] = {
            'score': concentration_score,
            'description': f"Dominant supplier has {dominant_pct:.0f}% share",
            'mitigation': 'Diversify to multiple suppliers'
        }
        
        # 2. Financial Stability Risk
        financial_score = self._calculate_financial_risk(brief_data)
        scores['Financial Stability'] = financial_score
        details['Financial Stability'] = {
            'score': financial_score,
            'description': 'Supplier financial health assessment',
            'mitigation': 'Conduct credit checks, request financial statements'
        }
        
        # 3. Geopolitical Risk
        geopolitical_score = self._calculate_geopolitical_risk(brief_data)
        scores['Geopolitical Risk'] = geopolitical_score
        details['Geopolitical Risk'] = {
            'score': geopolitical_score,
            'description': 'Regional supply corridor concentration',
            'mitigation': 'Expand to geographically diverse suppliers'
        }
        
        # 4. Supply Chain Resilience
        resilience_score = self._calculate_resilience_risk(brief_data)
        scores['Supply Chain Resilience'] = resilience_score
        details['Supply Chain Resilience'] = {
            'score': resilience_score,
            'description': 'Overall supply chain robustness',
            'mitigation': 'Build strategic inventory, develop contingency plans'
        }
        
        # 5. Regulatory Compliance Risk
        compliance_score = self._calculate_compliance_risk(brief_data)
        scores['Regulatory Compliance'] = compliance_score
        details['Regulatory Compliance'] = {
            'score': compliance_score,
            'description': 'Tariffs, sanctions, certifications',
            'mitigation': 'Monitor regulatory changes, maintain certifications'
        }
        
        # 6. Market Volatility Risk
        volatility_score = self._calculate_volatility_risk(brief_data)
        scores['Market Volatility'] = volatility_score
        details['Market Volatility'] = {
            'score': volatility_score,
            'description': 'Price and availability volatility',
            'mitigation': 'Use hedging strategies, long-term contracts'
        }
        
        # 7. Quality Risk
        quality_score = self._calculate_quality_risk(brief_data)
        scores['Quality Risk'] = quality_score
        details['Quality Risk'] = {
            'score': quality_score,
            'description': 'Product quality and consistency',
            'mitigation': 'Implement quality assurance programs'
        }
        
        # 8. ESG Risk
        esg_score = self._calculate_esg_risk(brief_data)
        scores['ESG Risk'] = esg_score
        details['ESG Risk'] = {
            'score': esg_score,
            'description': 'Environmental, social, governance compliance',
            'mitigation': 'Audit supplier ESG practices, establish standards'
        }
        
        # Overall Risk Score
        overall_score = np.mean(list(scores.values()))
        
        return {
            'timestamp': datetime.now().isoformat(),
            'category': brief_data.get('category', 'Procurement'),
            'risk_scores': scores,
            'risk_details': details,
            'overall_risk_score': round(overall_score, 1),
            'overall_risk_level': self._get_risk_level(overall_score),
            'summary': self._generate_risk_summary(scores, details)
        }
    
    def _calculate_concentration_risk(self, dominant_pct: float) -> float:
        """Calculate supplier concentration risk (0-10)"""
        if dominant_pct > 90:
            return 10.0
        elif dominant_pct > 70:
            return 8.0
        elif dominant_pct > 50:
            return 6.0
        elif dominant_pct > 30:
            return 3.0
        else:
            return 1.0
    
    def _calculate_financial_risk(self, brief_data: Dict[str, Any]) -> float:
        """Calculate supplier financial stability risk"""
        # Base assessment
        risk = 5.0
        
        # Factors that reduce risk
        supplier_count = brief_data.get('num_suppliers', 1)
        if supplier_count > 3:
            risk -= 2.0
        
        return max(1.0, min(10.0, risk))
    
    def _calculate_geopolitical_risk(self, brief_data: Dict[str, Any]) -> float:
        """Calculate geopolitical risk based on region concentration"""
        regional_dep = brief_data.get('regional_dependency', {})
        sea_concentration = regional_dep.get('original_sea_pct', 0)
        
        if sea_concentration > 85:
            return 8.5
        elif sea_concentration > 70:
            return 7.0
        elif sea_concentration > 50:
            return 5.0
        else:
            return 3.0
    
    def _calculate_resilience_risk(self, brief_data: Dict[str, Any]) -> float:
        """Calculate supply chain resilience"""
        dominant_pct = brief_data.get('dominant_supplier_pct', 0)
        num_suppliers = brief_data.get('num_suppliers', 1)
        
        resilience = 5.0
        
        if dominant_pct > 70:
            resilience += 3.0
        if num_suppliers < 2:
            resilience += 2.0
        
        return min(10.0, resilience)
    
    def _calculate_compliance_risk(self, brief_data: Dict[str, Any]) -> float:
        """Calculate regulatory and compliance risk"""
        # Default moderate risk
        return 4.5
    
    def _calculate_volatility_risk(self, brief_data: Dict[str, Any]) -> float:
        """Calculate market volatility risk"""
        # Default moderate risk
        return 5.0
    
    def _calculate_quality_risk(self, brief_data: Dict[str, Any]) -> float:
        """Calculate quality risk"""
        # Default moderate risk
        return 4.0
    
    def _calculate_esg_risk(self, brief_data: Dict[str, Any]) -> float:
        """Calculate ESG risk"""
        # Default moderate risk
        return 5.5
    
    def _get_risk_level(self, score: float) -> str:
        """Get risk level label"""
        if score > 7.5:
            return 'CRITICAL'
        elif score > 6.0:
            return 'HIGH'
        elif score > 4.0:
            return 'MEDIUM'
        else:
            return 'LOW'
    
    def _generate_risk_summary(self, scores: Dict[str, float], details: Dict[str, Any]) -> str:
        """Generate risk summary statement"""
        top_risks = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:3]
        
        summary = "Top Risk Areas: "
        summary += ", ".join([f"{risk[0]} ({risk[1]:.1f}/10)" for risk in top_risks])
        
        return summary
