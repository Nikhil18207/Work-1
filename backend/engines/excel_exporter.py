"""
Excel Exporter - Generate Excel reports with multiple sheets
"""

import pandas as pd
from pathlib import Path
from typing import Dict, Any, List
from datetime import datetime
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils.dataframe import dataframe_to_rows


class ExcelExporter:
    """Export analysis data to Excel workbooks"""
    
    def __init__(self, output_dir: str = "./outputs/reports"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def export_comprehensive_analysis(
        self,
        briefs: Dict[str, Dict[str, Any]],
        additional_analysis: Dict[str, Any] = None,
        filename: str = None
    ) -> str:
        """Export comprehensive analysis to Excel with multiple sheets"""
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        category = briefs.get('incumbent_concentration_brief', {}).get('category', 'Procurement')
        
        if not filename:
            category_clean = category.replace(' ', '_')
            filename = f"Analysis_{category_clean}_{timestamp}.xlsx"
        
        filepath = self.output_dir / filename
        
        with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
            # Sheet 1: Executive Summary
            summary_data = self._create_summary_sheet(briefs)
            summary_data.to_excel(writer, sheet_name='Executive Summary', index=False)
            
            # Sheet 2: Incumbent Analysis
            incumbent = briefs.get('incumbent_concentration_brief', {})
            incumbent_df = self._create_incumbent_sheet(incumbent)
            incumbent_df.to_excel(writer, sheet_name='Incumbent Analysis', index=False)
            
            # Sheet 3: Regional Analysis
            regional = briefs.get('regional_concentration_brief', {})
            regional_df = self._create_regional_sheet(regional)
            regional_df.to_excel(writer, sheet_name='Regional Analysis', index=False)
            
            # Sheet 4: Risk Scores
            if additional_analysis and 'risk_scores' in additional_analysis:
                risk_df = pd.DataFrame([
                    {'Risk Type': k, 'Score': v, 'Status': self._risk_status(v)}
                    for k, v in additional_analysis['risk_scores'].items()
                ])
                risk_df.to_excel(writer, sheet_name='Risk Assessment', index=False)
            
            # Sheet 5: Cost Analysis
            if additional_analysis and 'cost_breakdown' in additional_analysis:
                cost_df = pd.DataFrame(additional_analysis['cost_breakdown'])
                cost_df.to_excel(writer, sheet_name='Cost Analysis', index=False)
            
            # Sheet 6: Supplier Scorecard
            if additional_analysis and 'supplier_scores' in additional_analysis:
                supplier_df = pd.DataFrame(additional_analysis['supplier_scores'])
                supplier_df.to_excel(writer, sheet_name='Supplier Scorecard', index=False)
            
            # Sheet 7: Implementation Plan
            if additional_analysis and 'roadmap' in additional_analysis:
                roadmap_df = pd.DataFrame(additional_analysis['roadmap'])
                roadmap_df.to_excel(writer, sheet_name='Implementation Roadmap', index=False)
            
            # Sheet 8: Market Intelligence
            if additional_analysis and 'market_data' in additional_analysis:
                market_df = pd.DataFrame(additional_analysis['market_data'])
                market_df.to_excel(writer, sheet_name='Market Intelligence', index=False)
        
        return str(filepath)
    
    def _create_summary_sheet(self, briefs: Dict[str, Any]) -> pd.DataFrame:
        """Create executive summary sheet"""
        incumbent = briefs.get('incumbent_concentration_brief', {})
        
        return pd.DataFrame([
            {'Metric': 'Category', 'Value': incumbent.get('category', 'N/A')},
            {'Metric': 'Total Annual Spend', 'Value': f"${float(incumbent.get('total_spend', 0)):,.0f}"},
            {'Metric': 'Current Suppliers', 'Value': incumbent.get('num_suppliers', 'N/A')},
            {'Metric': 'Dominant Supplier', 'Value': incumbent.get('dominant_supplier', 'N/A')},
            {'Metric': 'Dominant Supplier %', 'Value': f"{incumbent.get('dominant_supplier_pct', 0):.1f}%"},
            {'Metric': 'Risk Level', 'Value': 'High' if incumbent.get('dominant_supplier_pct', 0) > 70 else 'Medium'},
        ])
    
    def _create_incumbent_sheet(self, incumbent: Dict[str, Any]) -> pd.DataFrame:
        """Create incumbent analysis sheet"""
        current_state = incumbent.get('current_state', {})
        
        return pd.DataFrame([
            {'Analysis': 'Supplier', 'Current': current_state.get('dominant_supplier', 'N/A'), 'Target': incumbent.get('potential_alternate_supplier', 'N/A')},
            {'Analysis': 'Spend Share %', 'Current': f"{current_state.get('spend_share_pct', 0):.1f}%", 'Target': f"{100 - incumbent.get('alternate_target_pct', 38):.1f}%"},
            {'Analysis': 'Spend USD', 'Current': f"${float(current_state.get('spend_share_usd', 0)):,.0f}", 'Target': f"Optimized"},
            {'Analysis': 'Risk Status', 'Current': 'High Concentration', 'Target': 'Diversified'},
        ])
    
    def _create_regional_sheet(self, regional: Dict[str, Any]) -> pd.DataFrame:
        """Create regional analysis sheet"""
        original = regional.get('original_concentration', [])
        
        data = []
        for region in original:
            if isinstance(region, dict):
                data.append({
                    'Country': region.get('country', 'N/A'),
                    'Current %': f"{region.get('pct', 0):.1f}%",
                    'Current Spend': f"${float(region.get('spend_usd', 0)):,.0f}",
                })
        
        return pd.DataFrame(data) if data else pd.DataFrame([{'Country': 'N/A', 'Current %': '0%', 'Current Spend': '$0'}])
    
    def _risk_status(self, score: float) -> str:
        """Get risk status label"""
        if score > 7:
            return 'High Risk'
        elif score > 4:
            return 'Medium Risk'
        else:
            return 'Low Risk'
