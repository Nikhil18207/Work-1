"""
Leadership Brief Formatter

Formats the leadership briefs into the EXACT format shown in the Word documents:
1. Incumbent Concentration Brief
2. Regional Concentration Brief

Outputs to Markdown, Plain Text, and DOCX formats.
"""

from typing import Dict, Any
from datetime import datetime


class BriefFormatter:
    """
    Formats leadership briefs into professional output formats
    """
    
    def format_incumbent_brief_markdown(self, brief: Dict[str, Any]) -> str:
        """
        Format Incumbent Concentration Brief to Markdown
        
        Matches the exact format from Incumbent concentration.docx
        """
        
        total_spend = brief['total_spend']
        category = brief.get('category', 'PROCUREMENT')
        current = brief['current_state']
        reduction = brief['supplier_reduction']
        regional = brief['regional_dependency']
        cost_adv = brief['cost_advantages']
        total_cost = brief['total_cost_advantage']
        outcome = brief['strategic_outcome']
        next_steps = brief['next_steps']
        
        md = f"""# Incumbent concentration

# LEADERSHIP BRIEF – {category.upper()} PROCUREMENT DIVERSIFICATION

**Assumed Total Category Spend 2024: USD {total_spend:,.0f}**

## CURRENT STATE – SUPPLIER CONCENTRATION RISK

| Metric | 2024 Original |
|--------|---------------|
| Supplier | {current['dominant_supplier']} |
| Supplier Location | {current['supplier_location']} |
| Spend Share | {current['spend_share_pct']:.0f}% = USD {current['spend_share_usd']:,.0f} |
| Current {category} Buying from Supplier | {current['currently_buying_category']} |
| Alternate Supplier for {category} | {current['alternate_supplier_active']} |
| Key Risk | {current['key_risk']} |

## OVERALL RISK STATEMENT

{brief['risk_statement']}

## SUPPLIER SHARE REDUCTION IMPACT (TARGET STATE)

| Supplier | Original Share | New Target Cap | Reduction in Concentration |
|----------|----------------|----------------|---------------------------|
| {reduction['dominant_supplier']['name']} | {reduction['dominant_supplier']['original_share_pct']:.0f}% | {reduction['dominant_supplier']['new_target_cap_pct']:.0f}% | {reduction['dominant_supplier']['reduction_pct']:.0f}% reduction |
| {reduction['alternate_supplier']['name']} | {reduction['alternate_supplier']['original_share_pct']:.0f}% | {reduction['alternate_supplier']['new_target_pct']:.0f}% | {reduction['alternate_supplier']['benefit']} |

## REGIONAL DEPENDENCY IMPROVEMENT

| Metric | Original 2024 | New Target | Net Reduction |
|--------|---------------|------------|---------------|
| Southeast Asia Supply Corridor | {regional['original_sea_pct']:.0f}% | {regional['new_target_pct']} | {regional['net_reduction_pct']} reduction |

## COST ADVANTAGE PROJECTION FROM ADDING ALTERNATE SUPPLIER

| Region of Presence | Advantage Driver | Estimated Annual Cost Benefit (USD) |
|--------------------|------------------|-------------------------------------|
"""
        
        # Add cost advantages
        for adv in cost_adv[:-1]:  # Exclude blended (last one)
            md += f"| {adv['region']} | {adv['driver']} | {adv['min_usd']:,} – {adv['max_usd']:,} |\n"
        
        # Add blended advantage
        if cost_adv:
            blended = cost_adv[-1]
            md += f"| {blended['region']} | {blended['driver']} | {blended['min_usd']:,} – {blended['max_usd']:,} |\n"
        
        md += f"""
## STRATEGIC OUTCOME

"""
        for item in outcome:
            md += f"- {item}\n"
        
        md += f"""
## NEXT STEPS

"""
        for i, step in enumerate(next_steps, 1):
            md += f"{i}. {step}\n"
        
        return md
    
    def format_regional_brief_markdown(self, brief: Dict[str, Any]) -> str:
        """
        Format Regional Concentration Brief to Markdown
        
        Matches the exact format from RegionalConcentration.docx
        """
        
        total_spend = brief['total_spend']
        category = brief.get('category', 'PROCUREMENT')
        original = brief['original_concentration']
        target = brief['target_allocation']
        reductions = brief['reductions']
        regional = brief['regional_dependency']
        cost_adv = brief['cost_advantages']
        outcome = brief['strategic_outcome']
        next_steps = brief['next_steps']
        
        md = f"""# RegionalConcentration

# LEADERSHIP BRIEF – {category.upper()} PROCUREMENT DIVERSIFICATION

**Total Spend 2024: USD {total_spend:,.0f}**

## ORIGINAL SPEND CONCENTRATION (2024)

| Country | % of Total Spend | Cost (USD) |
|---------|------------------|------------|
"""
        
        # Add original concentration (top countries)
        for orig in original[:2]:
            md += f"| {orig['country']} | {orig['pct']:.0f}% | {orig['spend_usd']:,.0f} |\n"
        
        # Calculate total
        total_orig_pct = sum(o['pct'] for o in original[:2])
        total_orig_spend = sum(o['spend_usd'] for o in original[:2])
        
        md += f"| **Total SEA Concentration** | **{total_orig_pct:.0f}%** | **{total_orig_spend:,.0f}** |\n"
        md += f"""
{original[0]['country']} and {original[1]['country'] if len(original) > 1 else 'other regions'} each exceeded 40% of spend, creating high regional dependency.

## DIVERSIFIED TARGET STATE (NEW SPLIT)

| Country / Region | New % Allocation | New Cost (USD) | Change vs Original |
|------------------|------------------|----------------|-------------------|
"""
        
        # Add target allocation
        for country, data in target.items():
            md += f"| {country} | {data['pct']:.0f}% | {data['spend_usd']:,.0f} | {data['change']} |\n"
        
        md += f"| **Total** | **100%** | **{total_spend:,.0f}** | Balanced cost + risk mix |\n"
        
        md += f"""
## REDUCTION IN SPEND SHARE

| Country | Reduction in Spend Share |
|---------|--------------------------|
"""
        
        # Add reductions
        for red in reductions:
            md += f"| {red['country']} | {red['original_pct']:.0f}% → {red['target_pct']:.0f}% = {red['reduction_pct']:.1f}% reduction in share |\n"
        
        md += f"""
## REGIONAL DEPENDENCY IMPROVEMENT

| Metric | Original 2024 | New Target | Reduction |
|--------|---------------|------------|-----------|
| SEA Regional Dependency | {regional['original_sea_pct']:.0f}% | {regional['new_target_pct']} | {regional['reduction_pct']} reduction |

## REGIONAL COST ADVANTAGE DRIVERS

| Region | Cost Benefit Driver | Estimated Annual Advantage (USD) |
|--------|---------------------|----------------------------------|
"""
        
        # Add cost advantages
        for adv in cost_adv[:-1]:  # Exclude blended (last one)
            md += f"| {adv['region']} | {adv['driver']} | {adv['min_usd']:,} – {adv['max_usd']:,} |\n"
        
        # Add blended advantage
        if cost_adv:
            blended = cost_adv[-1]
            md += f"| {blended['region']} | {blended['driver']} | {blended['min_usd']:,} – {blended['max_usd']:,} |\n"
        
        md += f"""
## STRATEGIC OUTCOME

"""
        for item in outcome:
            md += f"- {item}\n"
        
        md += f"""
## NEXT STEPS

"""
        for i, step in enumerate(next_steps, 1):
            md += f"{i}. {step}\n"
        
        return md
    
    def save_briefs_to_files(
        self,
        incumbent_brief: Dict[str, Any],
        regional_brief: Dict[str, Any],
        output_dir: str = "outputs/briefs"
    ):
        """
        Save both briefs to files
        
        Args:
            incumbent_brief: Incumbent concentration brief data
            regional_brief: Regional concentration brief data
            output_dir: Output directory
        """
        import os
        from pathlib import Path
        
        # Create output directory
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        
        # Generate timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Format briefs
        incumbent_md = self.format_incumbent_brief_markdown(incumbent_brief)
        regional_md = self.format_regional_brief_markdown(regional_brief)
        
        # Save Incumbent Brief
        incumbent_file = os.path.join(output_dir, f"Incumbent_Concentration_{timestamp}.md")
        with open(incumbent_file, 'w', encoding='utf-8') as f:
            f.write(incumbent_md)
        
        # Save Regional Brief
        regional_file = os.path.join(output_dir, f"Regional_Concentration_{timestamp}.md")
        with open(regional_file, 'w', encoding='utf-8') as f:
            f.write(regional_md)
        
        print(f"\n✅ Briefs saved:")
        print(f"   📄 {incumbent_file}")
        print(f"   📄 {regional_file}")
        
        return {
            'incumbent_file': incumbent_file,
            'regional_file': regional_file
        }


# Example usage
if __name__ == "__main__":
    from backend.engines.leadership_brief_generator import LeadershipBriefGenerator
    
    print("="*80)
    print("BRIEF FORMATTER DEMO")
    print("="*80)
    
    # Generate briefs
    generator = LeadershipBriefGenerator()
    briefs = generator.generate_both_briefs(
        client_id='C001',
        category='Rice Bran Oil'
    )
    
    # Format and save
    formatter = BriefFormatter()
    files = formatter.save_briefs_to_files(
        incumbent_brief=briefs['incumbent_concentration_brief'],
        regional_brief=briefs['regional_concentration_brief']
    )
    
    print("\n" + "="*80)
    print("✅ BRIEFS GENERATED SUCCESSFULLY")
    print("="*80)
