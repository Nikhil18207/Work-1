"""
PDF Exporter - Generate professional PDF reports
"""

from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak, Image
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from pathlib import Path
from typing import Dict, Any, List
from datetime import datetime


class PDFExporter:
    """Generate professional PDF reports"""
    
    def __init__(self, output_dir: str = "./outputs/reports"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def _get_styles(self):
        """Get custom styles for PDF"""
        styles = getSampleStyleSheet()
        
        styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=styles['Heading1'],
            fontSize=20,
            textColor=colors.HexColor('#003366'),
            spaceAfter=30,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        ))
        
        styles.add(ParagraphStyle(
            name='CustomHeading',
            parent=styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor('#003366'),
            spaceAfter=12,
            fontName='Helvetica-Bold'
        ))
        
        styles.add(ParagraphStyle(
            name='CustomBody',
            parent=styles['BodyText'],
            fontSize=10,
            spaceAfter=10,
            alignment=TA_LEFT
        ))
        
        return styles
    
    def export_executive_summary(
        self,
        brief_data: Dict[str, Any],
        filename: str = None
    ) -> str:
        """Export executive summary as PDF"""
        from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        category = brief_data.get('category', 'Procurement')
        
        if not filename:
            category_clean = category.replace(' ', '_')
            filename = f"Executive_Summary_{category_clean}_{timestamp}.pdf"
        
        filepath = self.output_dir / filename
        doc = SimpleDocTemplate(str(filepath), pagesize=letter)
        
        styles = self._get_styles()
        story = []
        
        # Title
        story.append(Paragraph(
            f"EXECUTIVE SUMMARY – {category.upper()} PROCUREMENT",
            styles['CustomTitle']
        ))
        
        story.append(Paragraph(
            f"Generated: {datetime.now().strftime('%B %d, %Y')}",
            styles['Normal']
        ))
        story.append(Spacer(1, 0.2*inch))
        
        # Key Metrics
        story.append(Paragraph("KEY METRICS", styles['CustomHeading']))
        
        total_spend = brief_data.get('total_spend', 0)
        category_name = brief_data.get('category', 'Category')
        
        metrics_data = [
            ['Metric', 'Value'],
            ['Total Annual Spend', f"${float(total_spend):,.0f}"],
            ['Category', category_name],
            ['Current Suppliers', str(brief_data.get('num_suppliers', 'N/A'))],
            ['Concentration Risk', 'High' if brief_data.get('dominant_supplier_pct', 0) > 70 else 'Medium'],
        ]
        
        metrics_table = Table(metrics_data, colWidths=[3*inch, 2*inch])
        metrics_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#003366')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))
        
        story.append(metrics_table)
        story.append(Spacer(1, 0.3*inch))
        
        # Top Risks
        story.append(Paragraph("TOP 3 RISKS", styles['CustomHeading']))
        
        risk_statement = brief_data.get('risk_statement', 'Supply chain concentration risk identified.')
        story.append(Paragraph(f"1. {risk_statement[:200]}...", styles['CustomBody']))
        
        story.append(Paragraph("2. Geopolitical and regulatory uncertainties affecting supply routes.", styles['CustomBody']))
        story.append(Paragraph("3. Supplier financial stability and capacity constraints.", styles['CustomBody']))
        
        story.append(Spacer(1, 0.3*inch))
        
        # Recommendations
        story.append(Paragraph("KEY RECOMMENDATIONS", styles['CustomHeading']))
        
        next_steps = brief_data.get('next_steps', [])
        for i, step in enumerate(next_steps[:3], 1):
            story.append(Paragraph(f"{i}. {step}", styles['CustomBody']))
        
        story.append(Spacer(1, 0.3*inch))
        
        # Expected Benefits
        story.append(Paragraph("EXPECTED BENEFITS", styles['CustomHeading']))
        
        cost_advantages = brief_data.get('cost_advantages', [])
        if cost_advantages:
            total_benefit = 0
            for adv in cost_advantages:
                if isinstance(adv, dict) and adv.get('region') == 'Blended Advantage':
                    total_benefit = adv.get('max_usd', 0)
            
            story.append(Paragraph(
                f"• Estimated Annual Savings: ${float(total_benefit):,.0f}",
                styles['CustomBody']
            ))
        
        story.append(Paragraph("• Improved supply chain resilience", styles['CustomBody']))
        story.append(Paragraph("• Enhanced supplier competition and pricing leverage", styles['CustomBody']))
        story.append(Paragraph("• Reduced geopolitical and operational risks", styles['CustomBody']))
        
        # Build PDF
        doc.build(story)
        return str(filepath)
    
    def export_comprehensive_report(
        self,
        briefs: Dict[str, Dict[str, Any]],
        additional_data: Dict[str, Any] = None,
        filename: str = None
    ) -> str:
        """Export comprehensive analysis report as PDF"""
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        category = briefs.get('incumbent_concentration_brief', {}).get('category', 'Procurement')
        
        if not filename:
            category_clean = category.replace(' ', '_')
            filename = f"Comprehensive_Report_{category_clean}_{timestamp}.pdf"
        
        filepath = self.output_dir / filename
        doc = SimpleDocTemplate(str(filepath), pagesize=letter)
        
        styles = self._get_styles()
        story = []
        
        # Title Page
        story.append(Paragraph(
            f"COMPREHENSIVE PROCUREMENT ANALYSIS",
            styles['CustomTitle']
        ))
        
        story.append(Paragraph(
            f"Category: {category}",
            styles['Normal']
        ))
        
        story.append(Paragraph(
            f"Date: {datetime.now().strftime('%B %d, %Y')}",
            styles['Normal']
        ))
        
        story.append(Spacer(1, 0.5*inch))
        
        # Table of Contents
        story.append(Paragraph("TABLE OF CONTENTS", styles['CustomHeading']))
        
        toc_items = [
            "1. Executive Summary",
            "2. Risk Analysis",
            "3. Market Intelligence",
            "4. Supplier Analysis",
            "5. Cost Optimization",
            "6. Implementation Roadmap",
            "7. Scenario Analysis",
            "8. Appendices"
        ]
        
        for item in toc_items:
            story.append(Paragraph(item, styles['Normal']))
        
        story.append(PageBreak())
        
        # Sections
        story.append(Paragraph("1. EXECUTIVE SUMMARY", styles['CustomHeading']))
        
        incumbent = briefs.get('incumbent_concentration_brief', {})
        story.append(Paragraph(
            f"Total Annual Spend: ${float(incumbent.get('total_spend', 0)):,.0f}",
            styles['CustomBody']
        ))
        
        story.append(Spacer(1, 0.3*inch))
        
        story.append(Paragraph("2. RISK ANALYSIS", styles['CustomHeading']))
        
        if additional_data and 'risk_scores' in additional_data:
            risk_scores = additional_data['risk_scores']
            risk_data = [['Risk Type', 'Score', 'Status']]
            for risk_type, score in risk_scores.items():
                status = '🔴 High' if score > 7 else '🟡 Medium' if score > 4 else '🟢 Low'
                risk_data.append([risk_type, str(score), status])
            
            risk_table = Table(risk_data, colWidths=[2.5*inch, 1.5*inch, 1.5*inch])
            risk_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#003366')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ]))
            story.append(risk_table)
        
        # Build PDF
        doc.build(story)
        return str(filepath)
