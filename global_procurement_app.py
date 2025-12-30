"""
Global Procurement LLM System - Streamlit UI
Complete system with document upload and comprehensive analysis
"""

import sys
from pathlib import Path
import streamlit as st
import pandas as pd
from datetime import datetime

root_path = Path(__file__).parent
if str(root_path) not in sys.path:
    sys.path.insert(0, str(root_path))

from backend.engines.document_parser import DocumentParser
from backend.engines.leadership_brief_generator import LeadershipBriefGenerator
from backend.engines.docx_exporter import DOCXExporter
from backend.engines.pdf_exporter import PDFExporter
from backend.engines.excel_exporter import ExcelExporter
from backend.engines.risk_analyzer import RiskAnalyzer
from backend.engines.market_intelligence import MarketIntelligence
from backend.engines.tco_calculator import TCOCalculator
from backend.engines.compliance_analyzer import ComplianceAnalyzer
from backend.engines.implementation_roadmap import SupplierScorecard, ImplementationRoadmap
from backend.engines.scenario_analyzer import ScenarioAnalyzer, BenchmarkAnalyzer


# Page config
st.set_page_config(
    page_title="Global Procurement LLM System",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    .main { padding: 2rem; }
    .header { 
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 2rem;
        border-radius: 10px;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: #f0f2f6;
        padding: 1.5rem;
        border-radius: 8px;
        margin: 1rem 0;
        border-left: 4px solid #667eea;
    }
    .success { color: #06d6a0; }
    .warning { color: #f77f00; }
    .danger { color: #d62828; }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'uploaded_file' not in st.session_state:
    st.session_state.uploaded_file = None
if 'parsed_data' not in st.session_state:
    st.session_state.parsed_data = None
if 'analysis_results' not in st.session_state:
    st.session_state.analysis_results = {}
if 'brief_data' not in st.session_state:
    st.session_state.brief_data = None
if 'last_analysis' not in st.session_state:
    st.session_state.last_analysis = None

# Prevent flickering by caching data
@st.cache_resource
def get_analyzers():
    return {
        'risk': RiskAnalyzer(),
        'market': MarketIntelligence(),
        'tco': TCOCalculator(),
        'compliance': ComplianceAnalyzer(),
        'parser': DocumentParser(),
        'generator': LeadershipBriefGenerator()
    }

# Header
st.markdown("""
<div class="header">
    <h1>🌍 Global Procurement LLM System</h1>
    <p>Comprehensive procurement analysis across all industries</p>
</div>
""", unsafe_allow_html=True)

# Sidebar navigation
with st.sidebar:
    st.title("Navigation")
    page = st.radio(
        "Select Analysis:",
        [
            "📤 Upload & Parse",
            "📊 Briefs Generation",
            "⚠️ Risk Analysis",
            "📈 Market Intelligence",
            "💰 TCO Analysis",
            "✅ Compliance",
            "🎯 Supplier Scorecard",
            "🛣️ Implementation Roadmap",
            "📉 Scenario Analysis",
            "📊 Benchmarking",
            "📥 Download Reports"
        ]
    )

# PAGE 1: Document Upload and Parsing
if page == "📤 Upload & Parse":
    st.header("📤 Document Upload & Parsing")
    
    st.info("""
    Upload your procurement data in any format:
    - **CSV**: Comma-separated values
    - **Excel**: XLSX or XLS files
    - **PDF**: Scan or export PDFs
    - **Word**: DOCX documents
    """)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        uploaded_file = st.file_uploader(
            "Choose a file",
            type=["csv", "xlsx", "xls", "pdf", "docx"]
        )
    
    if uploaded_file:
        st.session_state.uploaded_file = uploaded_file
        
        with st.spinner("Parsing document..."):
            parser = DocumentParser()
            result = parser.parse_upload(uploaded_file.read(), uploaded_file.name)
        
        if 'error' not in result:
            st.success("✅ Document parsed successfully!")
            
            st.subheader("File Information")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Format", result.get('format', 'Unknown'))
            with col2:
                st.metric("Rows", result.get('rows', 'N/A'))
            with col3:
                st.metric("Columns", result.get('columns', 'N/A'))
            
            if 'data' in result and isinstance(result['data'], pd.DataFrame):
                st.session_state.parsed_data = result['data']
                
                st.subheader("Data Preview")
                st.dataframe(result['data'].head(), use_container_width=True)
                
                # Extract metrics
                st.subheader("Extracted Metrics")
                metrics = parser.extract_spend_data(result['data'])
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    if 'total_spend' in metrics['metrics']:
                        st.metric("Total Spend", f"${metrics['metrics']['total_spend']:,.0f}")
                with col2:
                    if 'categories' in metrics['metrics']:
                        st.metric("Categories", len(metrics['metrics']['categories']))
                with col3:
                    if 'suppliers' in metrics['metrics']:
                        st.metric("Suppliers", len(metrics['metrics']['suppliers']))
        else:
            st.error(f"❌ Error: {result.get('error')}")

# PAGE 2: Brief Generation
elif page == "📊 Briefs Generation":
    st.header("📊 Incumbent & Regional Concentration Briefs")
    
    st.info("💡 Tip: Upload a file first to generate briefs with your actual data, or use sample data below.")
    
    col1, col2 = st.columns(2)
    
    with col1:
        client_id = st.text_input("Client ID", "C001")
    with col2:
        category = st.text_input("Product Category", "Rice Bran Oil")
    
    col3, col4 = st.columns(2)
    with col3:
        total_spend = st.number_input("Total Spend ($)", value=5000000, min_value=0)
    with col4:
        dominant_supplier_pct = st.slider("Dominant Supplier %", 0, 100, 75)
    
    if st.button("Generate Briefs", key="generate_briefs"):
        with st.spinner("Generating briefs..."):
            try:
                # Create brief data with user inputs
                brief_data = {
                    'client_id': client_id,
                    'category': category,
                    'total_spend': total_spend,
                    'dominant_supplier': 'ABC Supplier Inc',
                    'dominant_supplier_pct': dominant_supplier_pct,
                    'suppliers': ['ABC Supplier Inc', 'XYZ Company', 'New Supplier'],
                    'regions': ['Asia', 'Americas', 'Europe'],
                    'concentration_by_region': {
                        'Asia': dominant_supplier_pct * 0.9,
                        'Americas': dominant_supplier_pct * 0.8,
                        'Europe': dominant_supplier_pct * 0.6
                    }
                }
                
                generator = LeadershipBriefGenerator()
                briefs = generator.generate_both_briefs(client_id, category)
                
                # Enhance briefs with actual data
                briefs['incumbent_concentration_brief'].update({
                    'total_spend': total_spend,
                    'dominant_supplier_pct': dominant_supplier_pct
                })
                
                st.session_state.analysis_results['briefs'] = briefs
                st.session_state.brief_data = brief_data
                
                st.success("✅ Briefs generated successfully!")
                
                # Display summary
                incumbent = briefs['incumbent_concentration_brief']
                regional = briefs['regional_concentration_brief']
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Total Spend", f"${incumbent.get('total_spend', 0):,.0f}")
                with col2:
                    st.metric("Dominant Supplier %", f"{incumbent.get('dominant_supplier_pct', 0):.0f}%")
                with col3:
                    st.metric("Risk Level", "High" if incumbent.get('dominant_supplier_pct', 0) > 70 else "Medium")
                
                # Display briefs
                st.subheader("Incumbent Concentration Brief")
                
                # Extract from correct nested structure
                current_state = incumbent.get('current_state', {})
                dominant_supplier_name = current_state.get('dominant_supplier', 'N/A')
                spend_share = current_state.get('spend_share_pct', incumbent.get('dominant_supplier_pct', 0))
                
                st.json({
                    "Dominant Supplier": dominant_supplier_name,
                    "Spend Share": f"{spend_share:.0f}%",
                    "Risk": incumbent.get('risk_statement', 'N/A')[:200] + "..."
                })
                
                st.subheader("Regional Concentration Brief")
                
                # Extract regional data from correct structure
                original_concentration = incumbent.get('regional_dependency', {}).get('original_sea_pct', 0)
                num_suppliers = incumbent.get('num_current_suppliers', len(incumbent.get('all_current_suppliers', [])))
                
                st.json({
                    "Original Concentration": f"{original_concentration:.0f}%",
                    "Regions": num_suppliers
                })
                
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")

# PAGE 3: Risk Analysis
elif page == "⚠️ Risk Analysis":
    st.header("⚠️ Comprehensive Risk Analysis")
    
    if 'briefs' not in st.session_state.analysis_results or not st.session_state.analysis_results['briefs']:
        st.warning("⚠️ Please generate briefs first in '📊 Briefs Generation' page!")
        
        # Provide sample data for testing
        if st.button("Use Sample Data"):
            sample_brief = {
                'incumbent_concentration_brief': {
                    'total_spend': 5000000,
                    'dominant_supplier': 'ABC Foods Inc',
                    'dominant_supplier_pct': 78.5,
                    'category': 'Rice Bran Oil',
                    'suppliers': ['ABC Foods Inc', 'XYZ Oils LLC', 'New Supplier'],
                },
                'regional_concentration_brief': {
                    'sea_concentration_pct': 70,
                }
            }
            st.session_state.analysis_results['briefs'] = sample_brief
            st.rerun()
    else:
        with st.spinner("Analyzing risks..."):
            analyzer = RiskAnalyzer()
            risk_results = analyzer.analyze_risks(st.session_state.analysis_results['briefs']['incumbent_concentration_brief'])
            st.session_state.analysis_results['risk'] = risk_results
        
        st.success("✅ Risk analysis complete!")
        
        # Risk scores
        st.subheader("Risk Scores")
        risk_df = pd.DataFrame([
            {"Risk Type": k, "Score": v}
            for k, v in risk_results['risk_scores'].items()
        ]).sort_values("Score", ascending=False)
        
        st.dataframe(risk_df, use_container_width=True)
        
        # Overall risk
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Overall Risk Score", f"{risk_results['overall_risk_score']:.1f}/10")
        with col2:
            st.metric("Risk Level", risk_results['overall_risk_level'])
        
        # Risk details
        st.subheader("Risk Mitigation Strategies")
        for risk_type, details in risk_results['risk_details'].items():
            with st.expander(f"📌 {risk_type} (Score: {details['score']:.1f})"):
                st.write(f"**Description:** {details['description']}")
                st.write(f"**Mitigation:** {details['mitigation']}")

# PAGE 4: Market Intelligence
elif page == "📈 Market Intelligence":
    st.header("📈 Market Intelligence & Trends")
    
    if 'briefs' not in st.session_state.analysis_results:
        st.warning("Please generate briefs first!")
    else:
        with st.spinner("Analyzing market..."):
            market = MarketIntelligence()
            market_results = market.analyze_market(st.session_state.analysis_results['briefs']['incumbent_concentration_brief'])
            st.session_state.analysis_results['market'] = market_results
        
        st.success("✅ Market analysis complete!")
        
        # Market size
        st.subheader("Market Size Estimate")
        market_size = market_results['market_size_estimate']
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Estimated Global Market", f"${market_size['estimated_global_market']:,.0f}")
        with col2:
            st.metric("Your Market Share", f"{market_size['customer_market_share']:.3f}%")
        with col3:
            st.metric("3-Year Growth", f"${market_size['growth_projection_3yr']:,.0f}")
        
        # Market trends
        st.subheader("Market Trends")
        for trend in market_results['market_trends']:
            st.write(f"✓ {trend}")
        
        # Competitive landscape
        st.subheader("Competitive Landscape")
        comp = market_results['competitive_landscape']
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Supplier Count", comp['supplier_count'])
        with col2:
            st.metric("Competition Level", comp['competition_level'])
        with col3:
            st.metric("Market Concentration", comp['market_concentration'])

# PAGE 5: TCO Analysis
elif page == "💰 TCO Analysis":
    st.header("💰 Total Cost of Ownership Analysis")
    
    if 'briefs' not in st.session_state.analysis_results:
        st.warning("Please generate briefs first!")
    else:
        with st.spinner("Calculating TCO..."):
            tco_calc = TCOCalculator()
            tco_results = tco_calc.calculate_tco(st.session_state.analysis_results['briefs']['incumbent_concentration_brief'])
            st.session_state.analysis_results['tco'] = tco_results
        
        st.success("✅ TCO analysis complete!")
        
        # Current vs Optimized
        col1, col2, col3 = st.columns(3)
        current = tco_results['current_state']['total_tco']
        optimized = tco_results['optimized_state']['total_tco']
        savings = tco_results['tco_improvement']['savings_usd']
        
        with col1:
            st.metric("Current TCO", f"${current:,.0f}")
        with col2:
            st.metric("Optimized TCO", f"${optimized:,.0f}")
        with col3:
            st.metric("Potential Savings", f"${savings:,.0f}", delta=f"-{tco_results['tco_improvement']['savings_pct']:.1f}%")
        
        # Cost breakdown
        st.subheader("TCO Breakdown")
        breakdown = tco_results['current_state']['tco_breakdown_pct']
        
        st.json(breakdown)

# PAGE 6: Compliance
elif page == "✅ Compliance":
    st.header("✅ Compliance & ESG Analysis")
    
    if 'briefs' not in st.session_state.analysis_results:
        st.warning("Please generate briefs first!")
    else:
        with st.spinner("Analyzing compliance..."):
            compliance = ComplianceAnalyzer()
            comp_results = compliance.analyze_compliance(st.session_state.analysis_results['briefs']['incumbent_concentration_brief'])
            st.session_state.analysis_results['compliance'] = comp_results
        
        st.success("✅ Compliance analysis complete!")
        
        # Certifications
        st.subheader("Required Certifications")
        certs = comp_results['certifications_required']
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Current", len(certs['current']))
        with col2:
            st.metric("In Progress", len(certs['in_progress']))
        with col3:
            st.metric("Gap", len(certs['gap']))
        
        st.write("**Current Certifications:**")
        for cert in certs['current']:
            st.write(f"✅ {cert}")
        
        st.write("**Gap Analysis:**")
        for cert in certs['gap']:
            st.write(f"⚠️ {cert}")
        
        # ESG
        st.subheader("ESG Requirements")
        esg = comp_results['esg_requirements']
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.write("**Environmental**")
            for item, detail in esg['environmental'].items():
                st.caption(f"🌱 {detail}")
        with col2:
            st.write("**Social**")
            for item, detail in esg['social'].items():
                st.caption(f"👥 {detail}")
        with col3:
            st.write("**Governance**")
            for item, detail in esg['governance'].items():
                st.caption(f"📋 {detail}")

# PAGE 7: Supplier Scorecard
elif page == "🎯 Supplier Scorecard":
    st.header("🎯 Supplier Performance Scorecard")
    
    if 'briefs' not in st.session_state.analysis_results:
        st.warning("Please generate briefs first!")
    else:
        with st.spinner("Generating scorecard..."):
            scorecard = SupplierScorecard()
            scorecard_results = scorecard.generate_scorecard(st.session_state.analysis_results['briefs']['incumbent_concentration_brief'])
            st.session_state.analysis_results['scorecard'] = scorecard_results
        
        st.success("✅ Scorecard generated!")
        
        for supplier, scores in scorecard_results['suppliers'].items():
            st.subheader(f"{supplier}")
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Overall Score", scores['overall_score'])
            with col2:
                st.metric("Grade", scores['overall_grade'])
            with col3:
                st.metric("Risk", scores['risk_rating'])
            
            st.write(f"**Recommendation:** {scores['recommended_action']}")
            
            # Detailed scores
            cols = st.columns(3)
            metrics = ['quality', 'delivery', 'price']
            for idx, metric in enumerate(metrics):
                with cols[idx]:
                    score_data = scores[metric]
                    st.metric(metric.upper(), score_data['score'])
                    st.caption(score_data['feedback'])

# PAGE 8: Implementation Roadmap
elif page == "🛣️ Implementation Roadmap":
    st.header("🛣️ 24-Month Implementation Roadmap")
    
    if 'briefs' not in st.session_state.analysis_results:
        st.warning("Please generate briefs first!")
    else:
        with st.spinner("Generating roadmap..."):
            roadmap = ImplementationRoadmap()
            roadmap_results = roadmap.generate_roadmap(st.session_state.analysis_results['briefs']['incumbent_concentration_brief'])
            st.session_state.analysis_results['roadmap'] = roadmap_results
        
        st.success("✅ Roadmap generated!")
        
        st.metric("Total Investment", f"${roadmap_results['total_investment']:,.0f}")
        
        # Phases
        for phase in roadmap_results['phases']:
            with st.expander(f"📍 {phase['phase']} ({phase['duration_months']} months)"):
                st.write(f"**Timeline:** {phase['start_date']} to {phase['end_date']}")
                st.write(f"**Budget:** ${phase['budget']:,.0f}")
                
                st.write("**Activities:**")
                for activity in phase['activities']:
                    st.write(f"✓ {activity}")
                
                st.write("**KPIs:**")
                for kpi in phase['kpis']:
                    st.write(f"📊 {kpi}")

# PAGE 9: Scenario Analysis
elif page == "📉 Scenario Analysis":
    st.header("📉 What-If Scenario Analysis")
    
    if 'briefs' not in st.session_state.analysis_results:
        st.warning("Please generate briefs first!")
    else:
        with st.spinner("Analyzing scenarios..."):
            scenario = ScenarioAnalyzer()
            scenario_results = scenario.analyze_scenarios(st.session_state.analysis_results['briefs']['incumbent_concentration_brief'])
            st.session_state.analysis_results['scenario'] = scenario_results
        
        st.success("✅ Scenarios analyzed!")
        
        # Scenario comparison
        st.subheader("Scenario Comparison")
        
        scenarios_data = [
            scenario_results['baseline_scenario'],
            scenario_results['optimistic_scenario'],
            scenario_results['pessimistic_scenario']
        ]
        
        for scenario_data in scenarios_data:
            with st.expander(f"{scenario_data['name']} (P: {scenario_data['probability']})"):
                st.write(f"**Description:** {scenario_data['description']}")
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Risk Score", scenario_data['risk_score'])
                with col2:
                    st.metric("Cost Impact", f"${scenario_data['cost_impact']:,.0f}")
                with col3:
                    st.metric("Probability", scenario_data['probability'])
                
                st.write("**Key Assumptions:**")
                for assumption in scenario_data['key_assumptions']:
                    st.write(f"• {assumption}")

# PAGE 10: Benchmarking
elif page == "📊 Benchmarking":
    st.header("📊 Industry Benchmarking")
    
    if 'briefs' not in st.session_state.analysis_results:
        st.warning("Please generate briefs first!")
    else:
        with st.spinner("Benchmarking..."):
            benchmark = BenchmarkAnalyzer()
            bench_results = benchmark.benchmark_analysis(st.session_state.analysis_results['briefs']['incumbent_concentration_brief'])
            st.session_state.analysis_results['benchmark'] = bench_results
        
        st.success("✅ Benchmarking complete!")
        
        # Your metrics vs benchmark
        st.subheader("Your Performance vs Industry")
        
        your_metrics = bench_results['your_metrics']
        industry_bench = bench_results['industry_benchmarks']
        
        st.write("**Your Metrics:**")
        st.json(your_metrics)
        
        st.write("**Industry Benchmarks:**")
        st.json(industry_bench)
        
        # Gaps
        st.subheader("Performance Gaps")
        gaps = bench_results['performance_gaps']
        if gaps:
            gaps_df = pd.DataFrame(gaps)
            st.dataframe(gaps_df, use_container_width=True)
        else:
            st.success("✅ No major gaps identified!")

# PAGE 11: Download Reports
elif page == "📥 Download Reports":
    st.header("📥 Download All Reports")
    
    if not st.session_state.analysis_results:
        st.warning("Please complete analysis first!")
    else:
        col1, col2, col3, col4 = st.columns(4)
        
        briefs = st.session_state.analysis_results.get('briefs', {})
        category = briefs.get('incumbent_concentration_brief', {}).get('category', 'Procurement')
        
        # DOCX Export
        with col1:
            if st.button("📄 Download DOCX"):
                with st.spinner("Generating DOCX..."):
                    exporter = DOCXExporter()
                    docx_files = exporter.export_both_briefs(briefs)
                    st.success("✅ DOCX files generated!")
                    st.json({
                        "Incumbent": Path(docx_files['incumbent']).name,
                        "Regional": Path(docx_files['regional']).name
                    })
        
        # PDF Export
        with col2:
            if st.button("📋 Download PDF"):
                with st.spinner("Generating PDF..."):
                    pdf_exporter = PDFExporter()
                    pdf_files = []
                    
                    # Executive summary
                    exec_pdf = pdf_exporter.export_executive_summary(
                        briefs['incumbent_concentration_brief']
                    )
                    pdf_files.append(exec_pdf)
                    
                    # Comprehensive report
                    comp_pdf = pdf_exporter.export_comprehensive_report(
                        briefs,
                        st.session_state.analysis_results
                    )
                    pdf_files.append(comp_pdf)
                    
                    st.success("✅ PDF files generated!")
        
        # Excel Export
        with col3:
            if st.button("📊 Download Excel"):
                with st.spinner("Generating Excel..."):
                    excel_exporter = ExcelExporter()
                    excel_file = excel_exporter.export_comprehensive_analysis(
                        briefs,
                        st.session_state.analysis_results
                    )
                    st.success("✅ Excel file generated!")
                    st.write(f"File: {Path(excel_file).name}")
        
        # All Reports Zip
        with col4:
            if st.button("📦 Download All"):
                st.info("All reports have been generated in outputs/ folder")
        
        st.subheader("Generated Files")
        st.info("""
        **DOCX:** Incumbent_Concentration + Regional_Concentration
        **PDF:** Executive Summary + Comprehensive Report
        **Excel:** Multi-sheet analysis workbook
        """)

st.sidebar.markdown("---")
st.sidebar.markdown("🌍 **Global Procurement LLM System** v1.0")
st.sidebar.caption("Powered by advanced AI and procurement expertise")
