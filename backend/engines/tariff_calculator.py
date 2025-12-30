"""
Tariff Calculator Engine

Calculates import/export tariffs for cross-border sourcing decisions.
Critical for accurate cost impact analysis when moving between regions.

Features:
- Real-time tariff rate lookup (placeholder for API integration)
- Country-to-country tariff calculations
- Trade agreement considerations
- Duty calculation based on product category
- Historical tariff trend analysis
"""

from typing import Dict, Any, Optional, List, Tuple
from dataclasses import dataclass
from datetime import datetime
import pandas as pd


@dataclass
class TariffRate:
    """Represents a tariff rate between two countries"""
    from_country: str
    to_country: str
    product_category: str
    tariff_rate_pct: float
    trade_agreement: Optional[str]
    effective_date: datetime
    notes: str


@dataclass
class TariffCalculation:
    """Result of tariff calculation"""
    from_country: str
    to_country: str
    product_category: str
    base_price: float
    tariff_rate_pct: float
    tariff_amount: float
    landed_cost: float
    total_cost_impact_pct: float
    trade_agreement_applied: Optional[str]
    calculation_breakdown: Dict[str, float]


class TariffCalculator:
    """
    Tariff Calculator for cross-border sourcing cost analysis
    
    In production, this would integrate with:
    - WTO Tariff Database API
    - Trade agreement databases
    - Real-time customs data
    - Country-specific duty calculators
    """
    
    def __init__(self):
        self.tariff_database = self._initialize_tariff_database()
        self.trade_agreements = self._initialize_trade_agreements()
    
    def calculate_tariff(
        self,
        from_country: str,
        to_country: str,
        product_category: str,
        base_price: float,
        quantity: float = 1.0,
        include_other_fees: bool = True
    ) -> TariffCalculation:
        """
        Calculate complete tariff and landed cost
        
        Args:
            from_country: Exporting country
            to_country: Importing country
            product_category: Product category (e.g., 'Rice Bran Oil')
            base_price: Base price per unit (FOB)
            quantity: Quantity being imported
            include_other_fees: Include customs processing, handling fees
            
        Returns:
            TariffCalculation with complete breakdown
        """
        # Get tariff rate
        tariff_rate = self._get_tariff_rate(from_country, to_country, product_category)
        
        # Check for trade agreements
        trade_agreement = self._check_trade_agreement(from_country, to_country)
        
        # Apply trade agreement discount if applicable
        effective_tariff_rate = tariff_rate
        if trade_agreement:
            effective_tariff_rate = self._apply_trade_agreement_discount(
                tariff_rate, trade_agreement
            )
        
        # Calculate tariff amount
        tariff_amount = base_price * (effective_tariff_rate / 100)
        
        # Calculate other fees
        other_fees = 0.0
        if include_other_fees:
            other_fees = self._calculate_other_fees(base_price, to_country)
        
        # Calculate landed cost
        landed_cost = base_price + tariff_amount + other_fees
        
        # Calculate total cost impact
        total_cost_impact_pct = ((landed_cost - base_price) / base_price * 100)
        
        # Breakdown
        breakdown = {
            'base_price': base_price,
            'tariff_amount': tariff_amount,
            'customs_processing_fee': other_fees * 0.3 if include_other_fees else 0,
            'handling_fee': other_fees * 0.4 if include_other_fees else 0,
            'documentation_fee': other_fees * 0.3 if include_other_fees else 0,
            'total_landed_cost': landed_cost
        }
        
        return TariffCalculation(
            from_country=from_country,
            to_country=to_country,
            product_category=product_category,
            base_price=base_price,
            tariff_rate_pct=effective_tariff_rate,
            tariff_amount=tariff_amount,
            landed_cost=landed_cost,
            total_cost_impact_pct=round(total_cost_impact_pct, 2),
            trade_agreement_applied=trade_agreement,
            calculation_breakdown=breakdown
        )
    
    def compare_tariffs(
        self,
        to_country: str,
        product_category: str,
        base_price: float,
        from_countries: List[str]
    ) -> List[TariffCalculation]:
        """
        Compare tariffs from multiple source countries
        
        Useful for evaluating which region has the lowest landed cost
        """
        comparisons = []
        
        for from_country in from_countries:
            calc = self.calculate_tariff(
                from_country=from_country,
                to_country=to_country,
                product_category=product_category,
                base_price=base_price
            )
            comparisons.append(calc)
        
        # Sort by landed cost (lowest first)
        comparisons.sort(key=lambda x: x.landed_cost)
        
        return comparisons
    
    def get_tariff_trend(
        self,
        from_country: str,
        to_country: str,
        product_category: str,
        years: int = 5
    ) -> Dict[str, Any]:
        """
        Get historical tariff trend
        
        Helps identify if tariffs are increasing/decreasing
        """
        # Placeholder - in production would query historical database
        return {
            'from_country': from_country,
            'to_country': to_country,
            'product_category': product_category,
            'current_rate': self._get_tariff_rate(from_country, to_country, product_category),
            'trend': 'STABLE',
            'historical_rates': {
                '2024': 5.0,
                '2023': 5.0,
                '2022': 4.8,
                '2021': 4.5,
                '2020': 4.5
            },
            'forecast_2025': 5.0,
            'notes': 'Tariff rates have been stable over the past 5 years'
        }
    
    def _initialize_tariff_database(self) -> Dict[str, Dict[str, float]]:
        """
        Initialize tariff database
        
        In production, this would connect to:
        - WTO Integrated Tariff Database
        - Country-specific customs databases
        - Real-time API feeds
        """
        # Simplified tariff database (placeholder)
        # Format: {(from_country, to_country, category): tariff_rate_pct}
        
        tariff_db = {
            # Rice Bran Oil tariffs
            ('Malaysia', 'USA', 'Rice Bran Oil'): 5.0,
            ('India', 'USA', 'Rice Bran Oil'): 4.5,
            ('Thailand', 'USA', 'Rice Bran Oil'): 3.5,
            ('Vietnam', 'USA', 'Rice Bran Oil'): 4.0,
            ('Indonesia', 'USA', 'Rice Bran Oil'): 4.8,
            ('China', 'USA', 'Rice Bran Oil'): 6.5,
            
            # Edible Oils (general)
            ('Malaysia', 'USA', 'Edible Oils'): 5.2,
            ('India', 'USA', 'Edible Oils'): 4.7,
            ('Thailand', 'USA', 'Edible Oils'): 3.8,
            
            # Europe destinations
            ('Malaysia', 'Europe', 'Rice Bran Oil'): 4.0,
            ('India', 'Europe', 'Rice Bran Oil'): 3.5,
            ('Thailand', 'Europe', 'Rice Bran Oil'): 2.8,
            
            # Default rates
            ('DEFAULT', 'USA', 'DEFAULT'): 5.0,
            ('DEFAULT', 'Europe', 'DEFAULT'): 4.0,
            ('DEFAULT', 'Asia', 'DEFAULT'): 3.0,
        }
        
        return tariff_db
    
    def _initialize_trade_agreements(self) -> Dict[str, Dict[str, Any]]:
        """
        Initialize trade agreement database
        
        In production, would include:
        - USMCA, CPTPP, RCEP, EU FTAs, etc.
        - Specific product exclusions/inclusions
        - Phase-in schedules
        """
        return {
            'USMCA': {
                'countries': ['USA', 'Canada', 'Mexico'],
                'discount_pct': 100,  # 100% tariff elimination
                'products_covered': ['ALL'],
                'effective_date': '2020-07-01'
            },
            'CPTPP': {
                'countries': ['Japan', 'Vietnam', 'Malaysia', 'Singapore', 'Australia', 
                            'New Zealand', 'Canada', 'Mexico', 'Peru', 'Chile', 'Brunei'],
                'discount_pct': 90,  # 90% tariff reduction
                'products_covered': ['Edible Oils', 'Rice Bran Oil'],
                'effective_date': '2018-12-30'
            },
            'RCEP': {
                'countries': ['China', 'Japan', 'South Korea', 'Australia', 'New Zealand',
                            'ASEAN'],
                'discount_pct': 85,  # 85% tariff reduction
                'products_covered': ['ALL'],
                'effective_date': '2022-01-01'
            },
            'EU-Vietnam FTA': {
                'countries': ['EU', 'Vietnam'],
                'discount_pct': 95,  # 95% tariff elimination
                'products_covered': ['ALL'],
                'effective_date': '2020-08-01'
            }
        }
    
    def get_tariff_rate(self, from_country: str, to_country: str, product_category: str) -> float:
        """Public method to get tariff rate"""
        return self._get_tariff_rate(from_country, to_country, product_category)
    
    def _get_tariff_rate(
        self, from_country: str, to_country: str, product_category: str
    ) -> float:
        """Get tariff rate from database"""
        # Try exact match
        key = (from_country, to_country, product_category)
        if key in self.tariff_database:
            return self.tariff_database[key]
        
        # Try category default
        key = (from_country, to_country, 'DEFAULT')
        if key in self.tariff_database:
            return self.tariff_database[key]
        
        # Try destination default
        key = ('DEFAULT', to_country, 'DEFAULT')
        if key in self.tariff_database:
            return self.tariff_database[key]
        
        # Ultimate default
        return 5.0  # 5% default tariff
    
    def _check_trade_agreement(
        self, from_country: str, to_country: str
    ) -> Optional[str]:
        """Check if countries have a trade agreement"""
        for agreement_name, agreement_data in self.trade_agreements.items():
            countries = agreement_data['countries']
            
            # Check if both countries are in the agreement
            if from_country in countries and to_country in countries:
                return agreement_name
            
            # Handle regional agreements (e.g., ASEAN)
            if 'ASEAN' in countries:
                asean_countries = ['Thailand', 'Vietnam', 'Malaysia', 'Indonesia', 
                                 'Singapore', 'Philippines', 'Myanmar', 'Cambodia', 
                                 'Laos', 'Brunei']
                if from_country in asean_countries and to_country in countries:
                    return agreement_name
        
        return None
    
    def _apply_trade_agreement_discount(
        self, base_tariff: float, agreement_name: str
    ) -> float:
        """Apply trade agreement discount to tariff rate"""
        agreement = self.trade_agreements.get(agreement_name)
        if not agreement:
            return base_tariff
        
        discount_pct = agreement['discount_pct']
        
        # Calculate reduced tariff
        reduced_tariff = base_tariff * (1 - discount_pct / 100)
        
        return max(0, reduced_tariff)  # Can't be negative
    
    def _calculate_other_fees(self, base_price: float, to_country: str) -> float:
        """
        Calculate other import fees
        
        Includes:
        - Customs processing fee
        - Handling fee
        - Documentation fee
        - Port charges
        """
        # Simplified calculation (typically 1-3% of value)
        fee_pct = {
            'USA': 2.0,
            'Europe': 1.8,
            'Asia': 1.5,
            'Americas': 2.2
        }
        
        pct = fee_pct.get(to_country, 2.0)
        return base_price * (pct / 100)
    
    def generate_tariff_report(
        self,
        from_country: str,
        to_country: str,
        product_category: str,
        base_price: float
    ) -> str:
        """Generate a formatted tariff report"""
        calc = self.calculate_tariff(from_country, to_country, product_category, base_price)
        
        report = f"""
╔══════════════════════════════════════════════════════════════════════╗
║                      TARIFF CALCULATION REPORT                       ║
╚══════════════════════════════════════════════════════════════════════╝

📦 SHIPMENT DETAILS:
   From: {calc.from_country}
   To: {calc.to_country}
   Product: {calc.product_category}

💰 COST BREAKDOWN:
   Base Price (FOB):              ${calc.base_price:,.2f}
   Tariff Rate:                   {calc.tariff_rate_pct}%
   Tariff Amount:                 ${calc.tariff_amount:,.2f}
   Other Fees:                    ${sum([v for k, v in calc.calculation_breakdown.items() if 'fee' in k]):,.2f}
   ─────────────────────────────────────────────────
   Total Landed Cost:             ${calc.landed_cost:,.2f}
   
📊 COST IMPACT:
   Total Cost Increase:           {calc.total_cost_impact_pct}%
   
{f"🤝 TRADE AGREEMENT: {calc.trade_agreement_applied}" if calc.trade_agreement_applied else "⚠️  No trade agreement applied"}

💡 BREAKDOWN:
"""
        for item, amount in calc.calculation_breakdown.items():
            report += f"   {item.replace('_', ' ').title():30s} ${amount:,.2f}\n"
        
        return report


# Example usage
if __name__ == "__main__":
    calculator = TariffCalculator()
    
    print("="*80)
    print("TARIFF CALCULATOR DEMO")
    print("="*80)
    
    # Example 1: Single calculation
    print("\n📊 Example 1: Malaysia → USA (Rice Bran Oil)")
    calc = calculator.calculate_tariff(
        from_country='Malaysia',
        to_country='USA',
        product_category='Rice Bran Oil',
        base_price=1000.0
    )
    print(calculator.generate_tariff_report('Malaysia', 'USA', 'Rice Bran Oil', 1000.0))
    
    # Example 2: Compare multiple source countries
    print("\n📊 Example 2: Compare tariffs from different countries")
    comparisons = calculator.compare_tariffs(
        to_country='USA',
        product_category='Rice Bran Oil',
        base_price=1000.0,
        from_countries=['Malaysia', 'India', 'Thailand', 'Vietnam', 'China']
    )
    
    print("\nCOMPARISON RESULTS (sorted by landed cost):")
    print(f"{'Rank':<6} {'Country':<15} {'Tariff Rate':<12} {'Landed Cost':<15} {'Cost Impact':<12}")
    print("-" * 70)
    for i, comp in enumerate(comparisons, 1):
        print(f"{i:<6} {comp.from_country:<15} {comp.tariff_rate_pct}%{'':<10} ${comp.landed_cost:,.2f}{'':<6} +{comp.total_cost_impact_pct}%")
    
    # Example 3: Tariff trend
    print("\n📊 Example 3: Tariff trend analysis")
    trend = calculator.get_tariff_trend('India', 'USA', 'Rice Bran Oil')
    print(f"\nTariff Trend ({trend['from_country']} → {trend['to_country']}):")
    print(f"Current Rate: {trend['current_rate']}%")
    print(f"Trend: {trend['trend']}")
    print(f"Forecast 2025: {trend['forecast_2025']}%")
