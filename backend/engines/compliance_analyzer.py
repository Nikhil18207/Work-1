"""
Compliance & Sustainability Analyzer
"""

from typing import Dict, Any, List
from datetime import datetime, timedelta


class ComplianceAnalyzer:
    """Analyze compliance and ESG/sustainability requirements"""
    
    def analyze_compliance(self, brief_data: Dict[str, Any]) -> Dict[str, Any]:
        """Comprehensive compliance analysis"""
        
        category = brief_data.get('category', 'Unknown')
        
        return {
            'timestamp': datetime.now().isoformat(),
            'category': category,
            'certifications_required': self._get_required_certifications(category),
            'trade_compliance': self._analyze_trade_compliance(brief_data),
            'esg_requirements': self._analyze_esg(category),
            'regulatory_changes': self._get_regulatory_changes(category),
            'supplier_compliance_status': self._assess_supplier_compliance(brief_data),
            'risk_flags': self._identify_compliance_risks(brief_data, category),
            'recommendations': self._generate_compliance_recommendations(category)
        }
    
    def _get_required_certifications(self, category: str) -> Dict[str, List[str]]:
        """Get required certifications by category"""
        
        certifications = {
            'food': [
                'FSSC 22000 (Food Safety Management)',
                'ISO 22000 (Food Safety)',
                'Organic Certification (if applicable)',
                'HACCP Certification',
                'SQF (Safe Quality Food)',
                'BRC (British Retail Consortium)'
            ],
            'hardware': [
                'ISO 9001 (Quality Management)',
                'ISO 14001 (Environmental Management)',
                'RoHS Compliance (Hazardous Substances)',
                'WEEE Compliance (E-waste)',
                'CE Marking (EU compliance)',
                'FCC Certification (US)'
            ],
            'cloud': [
                'ISO 27001 (Information Security)',
                'SOC 2 Type II (Security & Compliance)',
                'GDPR Compliance (EU)',
                'HIPAA (Healthcare, if applicable)',
                'ISO 27018 (Cloud Privacy)',
                'FedRAMP (US Government)'
            ],
            'packaging': [
                'ISO 9001',
                'Food Contact Materials Compliance',
                'Recycling Certifications',
                'ISO 14001',
                'FSQS (if food-related)'
            ],
            'default': [
                'ISO 9001 (Quality Management)',
                'ISO 14001 (Environmental Management)',
                'ISO 45001 (Health & Safety)'
            ]
        }
        
        certs = certifications.get('default')
        for key in certifications.keys():
            if key != 'default' and key in category.lower():
                certs = certifications[key]
                break
        
        return {
            'current': certs[:2],  # Assume first 2 are current
            'in_progress': certs[2:3],  # Assume one in progress
            'required': certs,
            'gap': certs[3:] if len(certs) > 3 else []
        }
    
    def _analyze_trade_compliance(self, brief_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze trade and tariff compliance"""
        
        regional_dep = brief_data.get('regional_dependency', {})
        
        return {
            'tariff_exposure': 'High' if regional_dep.get('original_sea_pct', 0) > 70 else 'Moderate',
            'trade_agreements': [
                'Review USMCA (US-Mexico-Canada)',
                'Monitor CPTPP (Trans-Pacific Partnership)',
                'Evaluate RCEP (Regional Comprehensive Economic Partnership)',
                'Check UK trade agreements (post-Brexit)'
            ],
            'sanctions_check': 'OFAC (US), EU sanctions lists monitoring required',
            'origin_verification': 'Country of origin certificates required',
            'import_export_licenses': 'Verify license requirements for target markets',
            'tariff_codes': 'Verify correct HS codes for all products'
        }
    
    def _analyze_esg(self, category: str) -> Dict[str, Any]:
        """Analyze ESG and sustainability requirements"""
        
        return {
            'environmental': {
                'carbon_footprint': 'Scope 1, 2, 3 emissions tracking required',
                'water_usage': 'Water conservation and quality compliance',
                'waste_management': 'Zero-waste to landfill initiatives',
                'packaging': 'Sustainable packaging requirements',
                'certifications': 'ISO 14001, B-Corp, or equivalent'
            },
            'social': {
                'labor_practices': 'Fair labor standards (ILO conventions)',
                'diversity': 'LGBTQ+, women, minority supplier programs',
                'community': 'Local community impact assessments',
                'supply_chain': 'No forced labor, child labor, human trafficking',
                'certifications': 'Fair Trade, ethical sourcing'
            },
            'governance': {
                'transparency': 'Disclosure of ESG metrics',
                'ethics': 'Anti-corruption, bribery policies',
                'audit': 'Regular ESG audits and monitoring',
                'board_diversity': 'Diverse leadership representation',
                'data_privacy': 'GDPR, CCPA, data protection compliance'
            },
            'reporting': 'GRI, SASB, or TCFD standards'
        }
    
    def _get_regulatory_changes(self, category: str) -> List[Dict[str, str]]:
        """Get upcoming regulatory changes"""
        
        changes = [
            {
                'regulation': 'EU Digital Product Passport',
                'effective': '2026-2027',
                'impact': 'Requires detailed product information disclosure',
                'action': 'Prepare product data infrastructure'
            },
            {
                'regulation': 'Carbon Border Adjustment Mechanism (CBAM)',
                'effective': '2025-2026',
                'impact': 'Carbon tariffs on imports',
                'action': 'Measure and report carbon emissions'
            },
            {
                'regulation': 'Corporate Sustainability Due Diligence (CSDDD)',
                'effective': '2024-2025',
                'impact': 'Supply chain due diligence requirements',
                'action': 'Conduct supplier audits'
            }
        ]
        
        if 'food' in category.lower():
            changes.append({
                'regulation': 'Farm to Fork Strategy',
                'effective': '2024-2030',
                'impact': 'Sustainability in food supply chains',
                'action': 'Adopt sustainable farming practices'
            })
        
        return changes
    
    def _assess_supplier_compliance(self, brief_data: Dict[str, Any]) -> Dict[str, Any]:
        """Assess supplier compliance status"""
        
        dominant_supplier = brief_data.get('dominant_supplier', 'Unknown')
        
        return {
            'supplier': dominant_supplier,
            'audit_status': 'Current',
            'last_audit': (datetime.now() - timedelta(days=90)).isoformat(),
            'certifications_held': 'ISO 9001, ISO 14001',
            'non_conformances': 'None critical',
            'compliance_score': 'A (95%)',
            'next_audit': (datetime.now() + timedelta(days=270)).isoformat()
        }
    
    def _identify_compliance_risks(self, brief_data: Dict[str, Any], category: str) -> List[Dict[str, str]]:
        """Identify compliance risks"""
        
        risks = []
        
        dominant_pct = brief_data.get('dominant_supplier_pct', 0)
        if dominant_pct > 70:
            risks.append({
                'risk': 'Single supplier compliance risk',
                'severity': 'High',
                'mitigation': 'Diversify to multiple suppliers with same certifications'
            })
        
        regional_dep = brief_data.get('regional_dependency', {})
        if regional_dep.get('original_sea_pct', 0) > 70:
            risks.append({
                'risk': 'Geopolitical compliance exposure',
                'severity': 'High',
                'mitigation': 'Expand to geographically diverse, politically stable suppliers'
            })
        
        if 'food' in category.lower():
            risks.append({
                'risk': 'Food safety regulation changes',
                'severity': 'Medium',
                'mitigation': 'Implement advanced food traceability system'
            })
        
        return risks
    
    def _generate_compliance_recommendations(self, category: str) -> List[str]:
        """Generate compliance recommendations"""
        
        recommendations = [
            'Establish compliance monitoring dashboard',
            'Implement supplier compliance training programs',
            'Conduct annual third-party audit of supply chain',
            'Maintain updated certifications and licenses',
            'Monitor regulatory changes quarterly',
            'Document all compliance evidence and audit trails',
            'Establish crisis management protocols'
        ]
        
        if 'food' in category.lower():
            recommendations.append('Implement traceability system (blockchain-ready)')
            recommendations.append('Conduct food safety audits (FSSC 22000)')
        
        if 'cloud' in category.lower():
            recommendations.append('Complete SOC 2 Type II certification')
            recommendations.append('Implement GDPR data processing agreements')
        
        return recommendations
