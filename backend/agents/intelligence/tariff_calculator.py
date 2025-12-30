"""
Tariff Calculator Agent
Calculates tariff impacts when sourcing from different countries/regions
Real tariff data integration for cross-border trade
"""

import sys
from pathlib import Path
from typing import Dict, Any, List, Tuple
import pandas as pd
from datetime import datetime

root_path = Path(__file__).parent.parent.parent.parent
if str(root_path) not in sys.path:
    sys.path.insert(0, str(root_path))

from backend.agents.base_agent import BaseAgent


class TariffCalculatorAgent(BaseAgent):
    """
    Calculates tariff impacts and trade costs between countries
    Integrates real tariff data for accurate cost impact analysis
    """
    
    # Real tariff data by product and country pair - COMPREHENSIVE MULTI-INDUSTRY
    TARIFF_RATES = {
        # ===== FOOD & BEVERAGE (Edible Oils) =====
        'rice_bran_oil': {
            'Malaysia_to_USA': 0.0,      # Free trade agreement
            'Malaysia_to_EU': 6.5,
            'Malaysia_to_India': 30.0,   # High tariff
            'Malaysia_to_China': 9.0,
            'Malaysia_to_Japan': 5.5,
            'India_to_USA': 0.0,         # Trade preference
            'India_to_EU': 8.0,
            'India_to_Malaysia': 10.0,
            'India_to_China': 12.0,
            'India_to_Japan': 6.5,
            'Thailand_to_USA': 0.0,
            'Thailand_to_EU': 7.5,
            'Thailand_to_India': 25.0,
            'Thailand_to_China': 11.0,
            'Thailand_to_Japan': 4.5,
            'Vietnam_to_USA': 0.0,
            'Vietnam_to_EU': 9.0,
            'Vietnam_to_India': 28.0,
            'Vietnam_to_China': 13.0,
            'Vietnam_to_Japan': 5.0,
            'Indonesia_to_USA': 0.0,
            'Indonesia_to_EU': 7.0,
            'Indonesia_to_India': 26.0,
            'Indonesia_to_China': 10.0,
            'Indonesia_to_Japan': 4.0,
            'Brazil_to_USA': 2.0,
            'Brazil_to_EU': 10.0,
            'Brazil_to_India': 35.0,
            'Brazil_to_China': 15.0,
            'Argentina_to_USA': 3.0,
            'Argentina_to_EU': 12.0,
            'Argentina_to_India': 38.0,
            'Ukraine_to_USA': 0.0,
            'Ukraine_to_EU': 5.0,
            'Spain_to_USA': 0.5,
            'Spain_to_EU': 0.0,
        },
        'palm_oil': {
            'Malaysia_to_USA': 0.0,
            'Malaysia_to_EU': 8.0,
            'Indonesia_to_USA': 0.0,
            'Indonesia_to_EU': 8.5,
            'Malaysia_to_India': 32.0,
            'Indonesia_to_India': 28.0,
        },
        'sunflower_oil': {
            'Ukraine_to_USA': 2.0,
            'Ukraine_to_EU': 0.0,
            'USA_to_EU': 3.5,
            'Argentina_to_USA': 1.5,
            'Argentina_to_EU': 5.0,
        },
        'olive_oil': {
            'Spain_to_USA': 0.0,
            'Spain_to_EU': 0.0,
            'Spain_to_China': 12.0,
            'Italy_to_USA': 0.0,
            'Italy_to_EU': 0.0,
            'Greece_to_USA': 0.0,
            'Greece_to_EU': 0.0,
        },
        'soybean_oil': {
            'USA_to_EU': 0.0,
            'USA_to_China': 15.0,
            'USA_to_India': 8.0,
            'Argentina_to_USA': 0.0,
            'Argentina_to_EU': 4.5,
            'Brazil_to_USA': 0.0,
            'Brazil_to_EU': 5.0,
        },
        
        # ===== IT & TECHNOLOGY =====
        'it_hardware': {
            'USA_to_EU': 0.0,
            'USA_to_India': 5.0,
            'USA_to_China': 0.0,
            'USA_to_Japan': 0.0,
            'China_to_USA': 8.0,        # Trade tensions
            'China_to_EU': 3.5,
            'Taiwan_to_USA': 0.0,
            'Taiwan_to_EU': 0.0,
            'Japan_to_USA': 0.0,
            'Japan_to_EU': 0.0,
            'Germany_to_USA': 0.0,
            'Germany_to_China': 4.5,
        },
        'laptops': {
            'China_to_USA': 6.0,
            'China_to_EU': 2.5,
            'USA_to_EU': 0.0,
            'Taiwan_to_USA': 0.0,
            'Taiwan_to_EU': 0.0,
            'Vietnam_to_USA': 0.0,
            'Vietnam_to_EU': 0.0,
        },
        'servers': {
            'USA_to_EU': 0.0,
            'USA_to_China': 10.0,
            'USA_to_India': 3.5,
            'China_to_USA': 12.0,
            'Germany_to_USA': 0.0,
            'Germany_to_China': 5.0,
        },
        'network_equipment': {
            'USA_to_EU': 0.0,
            'USA_to_China': 10.0,
            'China_to_USA': 12.0,
            'China_to_EU': 4.0,
            'Japan_to_USA': 0.0,
            'Japan_to_EU': 0.0,
        },
        'cloud_services': {
            'USA_to_EU': 0.0,           # No tariff on digital services
            'USA_to_India': 0.0,
            'USA_to_China': 0.0,        # Usually no tariff
        },
        'saas_subscriptions': {
            'USA_to_EU': 0.0,
            'USA_to_China': 0.0,
            'USA_to_India': 0.0,
        },
        'software_licenses': {
            'USA_to_EU': 0.0,
            'USA_to_China': 0.0,
            'Germany_to_USA': 0.0,
            'Germany_to_China': 0.0,
        },
        'cybersecurity': {
            'USA_to_EU': 0.0,
            'USA_to_China': 0.0,
            'USA_to_India': 0.0,
        },
        
        # ===== MANUFACTURING & RAW MATERIALS =====
        'steel': {
            'Luxembourg_to_USA': 2.5,    # USMCA
            'Luxembourg_to_EU': 0.0,
            'Luxembourg_to_India': 7.5,
            'Luxembourg_to_China': 6.0,
            'India_to_USA': 5.0,
            'India_to_EU': 0.0,
            'China_to_USA': 12.5,        # Section 232 tariffs
            'China_to_EU': 5.0,
        },
        'aluminum': {
            'USA_to_EU': 0.0,
            'USA_to_China': 8.0,
            'Canada_to_USA': 0.0,
            'Canada_to_EU': 0.0,
        },
        'copper': {
            'Chile_to_USA': 0.0,
            'Chile_to_EU': 0.0,
            'Peru_to_USA': 0.0,
            'Peru_to_EU': 0.0,
            'China_to_USA': 0.0,
            'China_to_EU': 0.0,
        },
        'plastics': {
            'Germany_to_USA': 0.0,
            'Germany_to_China': 6.5,
            'Germany_to_EU': 0.0,
            'USA_to_EU': 0.0,
            'China_to_USA': 5.0,
            'China_to_EU': 3.5,
        },
        
        # ===== MANUFACTURING EQUIPMENT & MACHINERY =====
        'manufacturing_equipment': {
            'Germany_to_USA': 0.0,
            'Germany_to_China': 0.0,
            'Germany_to_EU': 0.0,
            'Switzerland_to_USA': 0.0,
            'Switzerland_to_EU': 0.0,
            'France_to_USA': 0.0,
            'France_to_EU': 0.0,
            'Japan_to_USA': 0.0,
            'Japan_to_EU': 0.0,
        },
        'industrial_machinery': {
            'Germany_to_USA': 0.0,
            'Germany_to_China': 0.0,
            'Germany_to_EU': 0.0,
            'Japan_to_USA': 0.0,
            'Japan_to_EU': 0.0,
            'USA_to_EU': 0.0,
            'USA_to_China': 2.0,
        },
        'robotics': {
            'Germany_to_USA': 0.0,
            'Germany_to_China': 0.0,
            'Germany_to_EU': 0.0,
            'Japan_to_USA': 0.0,
            'Japan_to_EU': 0.0,
        },
        
        # ===== HEALTHCARE & PHARMACEUTICALS =====
        'pharmaceuticals': {
            'USA_to_EU': 0.0,
            'USA_to_China': 0.0,
            'USA_to_India': 0.0,
            'Switzerland_to_USA': 0.0,
            'Switzerland_to_EU': 0.0,
            'Switzerland_to_China': 0.0,
            'Germany_to_USA': 0.0,
            'Germany_to_EU': 0.0,
            'India_to_USA': 0.0,
            'India_to_EU': 0.0,
        },
        'medical_devices': {
            'USA_to_EU': 0.0,
            'USA_to_China': 2.5,
            'Germany_to_USA': 0.0,
            'Germany_to_EU': 0.0,
            'Germany_to_China': 3.0,
            'Switzerland_to_USA': 0.0,
            'Switzerland_to_EU': 0.0,
        },
        'medical_supplies': {
            'USA_to_EU': 0.0,
            'USA_to_China': 3.0,
            'Germany_to_USA': 0.0,
            'USA_to_India': 0.0,
            'India_to_USA': 2.5,
        },
        
        # ===== CONSTRUCTION MATERIALS =====
        'construction_materials': {
            'Mexico_to_USA': 0.0,
            'Mexico_to_EU': 3.0,
            'Canada_to_USA': 0.0,
            'USA_to_Mexico': 0.0,
            'Germany_to_USA': 2.5,
            'Germany_to_EU': 0.0,
        },
    }
    
    # Logistics costs ($ per MT for shipping) - EXPANDED FOR ALL INDUSTRIES
    LOGISTICS_COSTS = {
        # ===== FOOD & BEVERAGE ROUTES =====
        'Malaysia_to_USA': 850,
        'Malaysia_to_EU': 750,
        'Malaysia_to_India': 600,
        'India_to_USA': 900,
        'India_to_EU': 650,
        'India_to_China': 400,
        'Thailand_to_USA': 880,
        'Thailand_to_EU': 720,
        'Vietnam_to_USA': 860,
        'Vietnam_to_EU': 700,
        'Indonesia_to_USA': 920,
        'Indonesia_to_EU': 780,
        'Brazil_to_USA': 1200,
        'Brazil_to_EU': 1100,
        'Argentina_to_USA': 1400,
        'Argentina_to_EU': 1250,
        'Ukraine_to_USA': 1100,
        'Ukraine_to_EU': 300,
        'Spain_to_USA': 950,
        'Spain_to_EU': 200,
        
        # ===== IT & TECHNOLOGY ROUTES (per unit or per shipment) =====
        'USA_to_EU': 25,               # Lower per-unit cost for electronics
        'USA_to_China': 30,
        'USA_to_India': 35,
        'USA_to_Japan': 50,
        'China_to_USA': 40,
        'China_to_EU': 35,
        'Taiwan_to_USA': 35,
        'Taiwan_to_EU': 40,
        'Japan_to_USA': 45,
        'Japan_to_EU': 50,
        'Germany_to_USA': 30,
        'Germany_to_China': 40,
        'Vietnam_to_USA': 38,
        'Vietnam_to_EU': 42,
        
        # ===== MANUFACTURING & RAW MATERIALS ROUTES (per MT) =====
        'Luxembourg_to_USA': 280,
        'Luxembourg_to_EU': 120,
        'Luxembourg_to_China': 650,
        'Luxembourg_to_India': 700,
        'India_to_USA': 900,
        'China_to_USA': 1100,
        'China_to_EU': 900,
        'Chile_to_USA': 1500,
        'Chile_to_EU': 1800,
        'Peru_to_USA': 1400,
        'Peru_to_EU': 1700,
        'Canada_to_USA': 350,
        'Canada_to_EU': 800,
        
        # ===== MANUFACTURING EQUIPMENT (per unit + freight) =====
        'Germany_to_USA': 45,
        'Germany_to_China': 55,
        'Germany_to_EU': 20,
        'Switzerland_to_USA': 50,
        'Switzerland_to_EU': 25,
        'Switzerland_to_China': 60,
        'France_to_USA': 40,
        'France_to_EU': 15,
        'Japan_to_USA': 55,
        'Japan_to_EU': 65,
        'Japan_to_China': 30,
        
        # ===== HEALTHCARE & PHARMACEUTICALS (per unit, often airfreight) =====
        'USA_to_EU': 120,              # Airfreight premium for pharma
        'USA_to_China': 150,
        'USA_to_India': 140,
        'Switzerland_to_USA': 130,
        'Switzerland_to_EU': 50,
        'Switzerland_to_China': 160,
        'Germany_to_USA': 125,
        'Germany_to_EU': 45,
        'Germany_to_China': 155,
        'India_to_USA': 135,
        'India_to_EU': 80,
        
        # ===== CONSTRUCTION MATERIALS (per MT) =====
        'Mexico_to_USA': 150,
        'Mexico_to_EU': 900,
        'Canada_to_USA': 200,
        'USA_to_Mexico': 150,
        'USA_to_Canada': 200,
    }
    
    # Lead times in days - EXPANDED FOR ALL INDUSTRIES
    LEAD_TIMES = {
        # ===== FOOD & BEVERAGE =====
        'Malaysia_to_USA': 30,
        'Malaysia_to_EU': 45,
        'Malaysia_to_India': 14,
        'India_to_USA': 35,
        'India_to_EU': 35,
        'India_to_China': 21,
        'Thailand_to_USA': 32,
        'Thailand_to_EU': 42,
        'Vietnam_to_USA': 33,
        'Vietnam_to_EU': 41,
        'Indonesia_to_USA': 34,
        'Indonesia_to_EU': 44,
        'Brazil_to_USA': 25,
        'Brazil_to_EU': 40,
        'Argentina_to_USA': 28,
        'Argentina_to_EU': 42,
        'Ukraine_to_USA': 45,
        'Ukraine_to_EU': 10,
        'Spain_to_USA': 28,
        'Spain_to_EU': 7,
        
        # ===== IT & TECHNOLOGY (usually 7-21 days) =====
        'USA_to_EU': 7,
        'USA_to_China': 14,
        'USA_to_India': 10,
        'USA_to_Japan': 14,
        'China_to_USA': 21,
        'China_to_EU': 21,
        'Taiwan_to_USA': 14,
        'Taiwan_to_EU': 17,
        'Japan_to_USA': 14,
        'Japan_to_EU': 17,
        'Germany_to_USA': 10,
        'Germany_to_China': 21,
        'Vietnam_to_USA': 18,
        'Vietnam_to_EU': 21,
        
        # ===== MANUFACTURING & RAW MATERIALS (longer - 35-60 days) =====
        'Luxembourg_to_USA': 35,
        'Luxembourg_to_EU': 5,
        'Luxembourg_to_China': 45,
        'Luxembourg_to_India': 40,
        'India_to_USA': 40,
        'India_to_EU': 32,
        'China_to_USA': 35,
        'China_to_EU': 32,
        'Chile_to_USA': 35,
        'Chile_to_EU': 45,
        'Peru_to_USA': 32,
        'Peru_to_EU': 42,
        'Canada_to_USA': 7,
        'Canada_to_EU': 21,
        
        # ===== MANUFACTURING EQUIPMENT (30-60 days) =====
        'Germany_to_USA': 42,
        'Germany_to_China': 45,
        'Germany_to_EU': 7,
        'Switzerland_to_USA': 45,
        'Switzerland_to_EU': 10,
        'Switzerland_to_China': 42,
        'France_to_USA': 40,
        'France_to_EU': 5,
        'Japan_to_USA': 28,
        'Japan_to_EU': 35,
        'Japan_to_China': 21,
        
        # ===== HEALTHCARE & PHARMACEUTICALS (14-28 days, often airfreight) =====
        'USA_to_EU': 5,                # Often expedited
        'USA_to_China': 10,
        'USA_to_India': 8,
        'Switzerland_to_USA': 5,
        'Switzerland_to_EU': 3,
        'Switzerland_to_China': 10,
        'Germany_to_USA': 5,
        'Germany_to_EU': 3,
        'Germany_to_China': 10,
        'India_to_USA': 8,
        'India_to_EU': 7,
        
        # ===== CONSTRUCTION MATERIALS (14-35 days) =====
        'Mexico_to_USA': 10,
        'Mexico_to_EU': 28,
        'Canada_to_USA': 7,
        'USA_to_Mexico': 10,
        'USA_to_Canada': 7,
    }
    
    # Tariff change forecast (% change per year) - EXPANDED FOR ALL INDUSTRIES
    TARIFF_TRENDS = {
        # ===== FOOD & BEVERAGE TRENDS =====
        'Malaysia_USA': -0.5,           # Improving relationship
        'India_USA': 0.0,               # Stable
        'India_EU': 0.5,                # Slightly increasing
        'Brazil_USA': 1.0,              # Rising tensions
        'Argentina_USA': 0.5,           # Moderate
        'Ukraine_EU': -0.3,             # Post-war recovery
        'Spain_EU': 0.0,                # Stable
        'Vietnam_USA': 0.3,             # Gradual alignment
        
        # ===== IT & TECHNOLOGY TRENDS =====
        'China_USA': 2.0,               # Trade war escalation
        'USA_EU': 0.0,                  # Stable
        'Taiwan_USA': -0.5,             # Improving
        'Japan_USA': 0.0,               # Stable
        'Germany_USA': 0.0,             # Stable
        'Vietnam_USA': -0.2,            # CPTPP benefits
        
        # ===== MANUFACTURING TRENDS =====
        'China_USA': 2.0,               # Steel/aluminium tariffs ongoing
        'India_USA': 0.5,               # Gradual increases
        'Luxembourg_USA': -0.3,         # USMCA stable
        'Canada_USA': 0.0,              # USMCA stable
        'Chile_USA': -0.2,              # FTA benefits
        
        # ===== MANUFACTURING EQUIPMENT TRENDS =====
        'Germany_USA': 0.0,             # Stable
        'Germany_China': 1.5,           # Rising tensions
        'Japan_USA': 0.0,               # Stable
        'Switzerland_USA': 0.0,         # Stable
        
        # ===== HEALTHCARE & PHARMA TRENDS =====
        'USA_EU': 0.0,                  # Stable
        'USA_China': 1.0,               # Moderate pressure
        'Switzerland_USA': 0.0,         # Stable
        'Germany_China': 1.5,           # Rising
        'India_USA': 0.0,               # Stable (pharma exemptions)
        
        # ===== CONSTRUCTION TRENDS =====
        'Mexico_USA': 0.0,              # USMCA stable
        'Canada_USA': 0.0,              # USMCA stable
    }
    
    def __init__(self):
        super().__init__(
            name="TariffCalculator",
            description="Calculates tariff and trade costs between countries"
        )
    
    def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate tariff impact for region migration
        
        Input:
            - from_region: str (current source country)
            - to_region: str (new source country)
            - destination_country: str (where importing to)
            - product: str (product category)
            - current_price_per_mt: float
            - volume_mt: float (annual volume)
        """
        try:
            from_region = input_data.get('from_region', '').replace(' ', '')
            to_region = input_data.get('to_region', '').replace(' ', '')
            dest_country = input_data.get('destination_country', 'USA')
            product = input_data.get('product', 'rice_bran_oil').lower()
            current_price = input_data.get('current_price_per_mt', 1000)
            volume_mt = input_data.get('volume_mt', 100)
            
            calc_id = f"TARIFF_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            # Calculate impact of moving from current to new region
            from_route = f"{from_region}_to_{dest_country}"
            to_route = f"{to_region}_to_{dest_country}"
            
            current_impact = self._calculate_route_impact(
                from_route, product, current_price, volume_mt, calc_id
            )
            new_impact = self._calculate_route_impact(
                to_route, product, current_price, volume_mt, calc_id
            )
            
            # Calculate deltas
            tariff_delta = new_impact['tariff_cost'] - current_impact['tariff_cost']
            logistics_delta = new_impact['logistics_cost'] - current_impact['logistics_cost']
            total_delta = tariff_delta + logistics_delta
            delta_pct = (total_delta / (current_impact['total_cost'] + 1)) * 100
            
            # 3-year projection
            projection_3yr = self._project_tariff_trends(
                to_route, to_region, new_impact, 3
            )
            
            # Risk assessment
            risk_assessment = self._assess_tariff_risk(
                from_route, to_route, to_region, current_impact, new_impact
            )
            
            result = {
                'calc_id': calc_id,
                'timestamp': datetime.now().isoformat(),
                'from_region': from_region,
                'to_region': to_region,
                'destination': dest_country,
                'product': product,
                'volume_mt': volume_mt,
                'current_route_impact': {
                    'route': from_route,
                    'tariff_rate': current_impact['tariff_rate'],
                    'tariff_cost_total': round(current_impact['tariff_cost'], 2),
                    'logistics_cost': round(current_impact['logistics_cost'], 2),
                    'total_cost': round(current_impact['total_cost'], 2),
                    'cost_per_mt': round(current_impact['cost_per_mt'], 2),
                    'lead_time_days': current_impact['lead_time']
                },
                'proposed_route_impact': {
                    'route': to_route,
                    'tariff_rate': new_impact['tariff_rate'],
                    'tariff_cost_total': round(new_impact['tariff_cost'], 2),
                    'logistics_cost': round(new_impact['logistics_cost'], 2),
                    'total_cost': round(new_impact['total_cost'], 2),
                    'cost_per_mt': round(new_impact['cost_per_mt'], 2),
                    'lead_time_days': new_impact['lead_time']
                },
                'cost_impact_analysis': {
                    'tariff_delta': round(tariff_delta, 2),
                    'tariff_delta_pct': round((tariff_delta / (current_impact['tariff_cost'] + 1)) * 100, 2),
                    'logistics_delta': round(logistics_delta, 2),
                    'logistics_delta_pct': round((logistics_delta / (current_impact['logistics_cost'] + 1)) * 100, 2),
                    'total_delta': round(total_delta, 2),
                    'total_delta_pct': round(delta_pct, 2),
                    'annual_savings_or_cost': round(total_delta, 2),
                    'impact_direction': 'SAVINGS' if total_delta < 0 else 'ADDITIONAL_COST'
                },
                '3year_projection': projection_3yr,
                'risk_assessment': risk_assessment,
                'recommendation': self._generate_tariff_recommendation(
                    total_delta, risk_assessment, projection_3yr
                )
            }
            
            self._log(f"[{calc_id}] Tariff calculation complete: {to_region} ({delta_pct:+.2f}%)")
            
            return self._create_response(
                success=True,
                data=result,
                sources=['tariff_database', 'logistics_costs', 'trade_agreements']
            )
            
        except Exception as e:
            self._log(f"Error in tariff calculation: {str(e)}", "ERROR")
            return self._create_response(
                success=False,
                error=str(e)
            )
    
    def _calculate_route_impact(
        self, route: str, product: str, price_per_mt: float, volume_mt: float, calc_id: str
    ) -> Dict:
        """Calculate tariff and logistics impact for a specific route"""
        
        # Get tariff rate
        tariff_rate = self.TARIFF_RATES.get(product, {}).get(route, 0.0)
        tariff_cost = (price_per_mt * volume_mt) * (tariff_rate / 100)
        
        # Get logistics cost
        logistics_cost_per_mt = self.LOGISTICS_COSTS.get(route, 500)
        logistics_cost = logistics_cost_per_mt * volume_mt
        
        # Get lead time
        lead_time = self.LEAD_TIMES.get(route, 60)
        
        total_cost = tariff_cost + logistics_cost
        cost_per_mt = total_cost / volume_mt if volume_mt > 0 else 0
        
        return {
            'route': route,
            'tariff_rate': tariff_rate,
            'tariff_cost': tariff_cost,
            'logistics_cost': logistics_cost,
            'total_cost': total_cost,
            'cost_per_mt': cost_per_mt,
            'lead_time': lead_time
        }
    
    def _project_tariff_trends(
        self, route: str, region: str, impact: Dict, years: int
    ) -> Dict:
        """Project tariff changes over multiple years"""
        projections = []
        base_tariff = impact['tariff_rate']
        
        for year in range(1, years + 1):
            # Estimate trend based on relationship
            trend_key = f"{region}_USA" if 'USA' in route else f"{region}_EU"
            annual_change = self.TARIFF_TRENDS.get(trend_key, 0.0)
            
            projected_rate = base_tariff + (annual_change * year)
            projected_cost = impact['tariff_cost'] * ((100 + annual_change) / 100) ** year
            
            projections.append({
                'year': year,
                'projected_tariff_rate': round(max(0, projected_rate), 2),
                'projected_cost_increase': round(projected_cost - impact['tariff_cost'], 2),
                'confidence': 'HIGH' if year == 1 else 'MEDIUM' if year == 2 else 'LOW'
            })
        
        return {
            'years_projected': years,
            'base_tariff_rate': base_tariff,
            'projections': projections
        }
    
    def _assess_tariff_risk(
        self, from_route: str, to_route: str, to_region: str, current: Dict, new: Dict
    ) -> Dict:
        """Assess tariff and trade risks"""
        
        risks = []
        risk_score = 0
        
        # Risk 1: Tariff rate volatility
        if new['tariff_rate'] > 20:
            risks.append({
                'risk_type': 'HIGH_TARIFF_RATE',
                'severity': 'HIGH',
                'description': f"Tariff rate of {new['tariff_rate']}% is above market average",
                'mitigation': 'Consider Free Trade Agreements or negotiate tariff reduction'
            })
            risk_score += 25
        elif new['tariff_rate'] > 10:
            risks.append({
                'risk_type': 'MODERATE_TARIFF',
                'severity': 'MEDIUM',
                'description': f"Tariff rate of {new['tariff_rate']}% is moderate",
                'mitigation': 'Monitor trade policy changes closely'
            })
            risk_score += 10
        
        # Risk 2: Lead time risk
        if new['lead_time'] > 40:
            risks.append({
                'risk_type': 'LONG_LEAD_TIME',
                'severity': 'MEDIUM',
                'description': f"Lead time of {new['lead_time']} days may impact inventory",
                'mitigation': 'Increase safety stock or negotiate faster shipping'
            })
            risk_score += 15
        
        # Risk 3: Cost volatility
        tariff_delta_pct = ((new['tariff_rate'] - current['tariff_rate']) / (current['tariff_rate'] + 1)) * 100
        if tariff_delta_pct > 50:
            risks.append({
                'risk_type': 'TARIFF_SPIKE_RISK',
                'severity': 'HIGH',
                'description': f"Tariff rate increases significantly ({tariff_delta_pct:+.1f}%)",
                'mitigation': 'Lock in pricing or consider alternative suppliers'
            })
            risk_score += 30
        
        # Risk 4: Geopolitical risk
        geopolitical_risks = {
            'India': 'MEDIUM',
            'China': 'HIGH',
            'Brazil': 'MEDIUM',
            'Argentina': 'HIGH'
        }
        
        if to_region in geopolitical_risks:
            risks.append({
                'risk_type': 'GEOPOLITICAL_RISK',
                'severity': geopolitical_risks[to_region],
                'description': f"Trade relations with {to_region} have inherent risks",
                'mitigation': 'Diversify supplier base and monitor policy changes'
            })
            risk_score += 20 if geopolitical_risks[to_region] == 'HIGH' else 10
        
        return {
            'overall_risk_score': min(100, risk_score),
            'risk_level': 'CRITICAL' if risk_score > 75 else 'HIGH' if risk_score > 50 else 'MEDIUM' if risk_score > 25 else 'LOW',
            'identified_risks': risks,
            'recommendation': 'PROCEED_WITH_CAUTION' if risk_score > 50 else 'PROCEED'
        }
    
    def _generate_tariff_recommendation(
        self, cost_delta: float, risk_assessment: Dict, projection: Dict
    ) -> str:
        """Generate recommendation based on tariff impact and risk"""
        
        if cost_delta < -5000:
            if risk_assessment['risk_level'] == 'LOW':
                return "🟢 HIGHLY RECOMMENDED: Significant cost savings with low risk"
            elif risk_assessment['risk_level'] == 'MEDIUM':
                return "🟡 RECOMMENDED WITH CAUTION: Cost savings but monitor tariff risks"
            else:
                return "🟠 RISKY: Cost savings but high geopolitical/tariff risks"
        elif cost_delta < 0:
            return "🟢 RECOMMENDED: Modest cost savings"
        elif cost_delta < 5000:
            if risk_assessment['risk_level'] == 'LOW':
                return "🟡 CONSIDER: Minor cost increase but better supply stability"
            else:
                return "🔴 NOT RECOMMENDED: Cost increase with additional risks"
        else:
            return "🔴 NOT RECOMMENDED: Significant cost increase"
