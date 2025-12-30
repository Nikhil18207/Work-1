"""
Interactive Streamlit UI for Personalized Supplier Coaching System
Complete web interface for the coaching system with real-time updates
"""

import sys
from pathlib import Path
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
import json

root_path = Path(__file__).parent.parent
if str(root_path) not in sys.path:
    sys.path.insert(0, str(root_path))

from backend.agents.supplier_coaching_orchestrator import SupplierCoachingOrchestrator
from backend.agents.intelligence.leading_questions import LeadingQuestionsModule
from backend.agents.intelligence.tariff_calculator import TariffCalculatorAgent
from backend.agents.intelligence.cost_risk_loop_engine import CostAndRiskLoopEngine
from backend.agents.intelligence.client_criteria_matching import ClientCriteriaMatchingEngine
from backend.engines.visual_workflow_generator import VisualWorkflowDiagramGenerator
from backend.engines.leadership_brief_generator import LeadershipBriefGenerator
from backend.engines.docx_exporter import DOCXExporter
from backend.engines.data_validator import DataValidator, validate_client_upload
from backend.engines.data_loader import DataLoader
import io
import os


# Configure page
st.set_page_config(
    page_title="Supplier Coaching System",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main {
        padding: 2rem;
    }
    .header-main {
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
        margin: 0.5rem 0;
    }
    .success-box {
        background: #c8e6c9;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #4caf50;
    }
    .warning-box {
        background: #fff9c4;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #fbc02d;
    }
    .danger-box {
        background: #ffcdd2;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #f44336;
    }
</style>
""", unsafe_allow_html=True)


def initialize_session_state():
    """Initialize session state variables"""
    if 'orchestrator' not in st.session_state:
        st.session_state.orchestrator = SupplierCoachingOrchestrator()
    
    if 'questions_module' not in st.session_state:
        st.session_state.questions_module = LeadingQuestionsModule()
    
    if 'cost_risk_engine' not in st.session_state:
        st.session_state.cost_risk_engine = CostAndRiskLoopEngine()
    
    if 'criteria_matching_engine' not in st.session_state:
        st.session_state.criteria_matching_engine = ClientCriteriaMatchingEngine()
    
    if 'diagram_generator' not in st.session_state:
        st.session_state.diagram_generator = VisualWorkflowDiagramGenerator()
    
    if 'coaching_results' not in st.session_state:
        st.session_state.coaching_results = None
    
    if 'user_answers' not in st.session_state:
        st.session_state.user_answers = {}


def render_header():
    """Render main header"""
    st.markdown("""
    <div class="header-main">
        <h1>🎯 Personalized Supplier Coaching System</h1>
        <p>Advanced AI-powered procurement optimization with constraint validation and tariff analysis</p>
    </div>
    """, unsafe_allow_html=True)


def render_sidebar():
    """Render sidebar navigation"""
    with st.sidebar:
        st.title("Navigation")
        
        page = st.radio(
            "Select Page",
            ["🏠 Home", "📤 Upload Data", "❓ Questions", "📊 Analysis", "🔄 Optimization", "📈 Results", "📊 Diagrams", "⚙️ Settings"]
        )
        
        st.divider()
        st.subheader("System Status")
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Agents Loaded", "7")
        with col2:
            st.metric("Rules Loaded", "35+")
        
        st.divider()
        st.subheader("Current Session")
        if st.session_state.coaching_results:
            session_id = st.session_state.coaching_results.get('session_id', 'N/A')
            st.text(f"ID: {session_id}")
        else:
            st.text("No active session")
        
        return page


def render_upload_page():
    """Render data upload page for clients"""
    st.header("📤 Upload Your Data")
    st.write("Upload your procurement data to generate diversification briefs")
    
    st.divider()
    
    st.subheader("Step 1: Upload Files")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**📄 Spend Data (Required)**")
        spend_file = st.file_uploader(
            "Upload spend_data.csv",
            type=['csv'],
            key='spend_upload',
            help="Required: Your transaction/spend data"
        )
        
        with st.expander("Required Columns"):
            st.code("""
Client_ID, Category, Supplier_ID, 
Supplier_Name, Supplier_Country, 
Supplier_Region, Transaction_Date, 
Spend_USD
            """)
    
    with col2:
        st.markdown("**📄 Supplier Master (Optional)**")
        supplier_file = st.file_uploader(
            "Upload supplier_master.csv",
            type=['csv'],
            key='supplier_upload',
            help="Optional: Supplier details for enhanced recommendations"
        )
        
        with st.expander("Required Columns"):
            st.code("""
supplier_id, supplier_name, region,
country, product_category
(Optional: quality_rating, certifications, etc.)
            """)
    
    st.divider()
    
    if spend_file:
        st.subheader("Step 2: Validate Data")
        
        with st.spinner("Validating uploaded data..."):
            validation_result = validate_client_upload(spend_file, supplier_file)
        
        spend_validation = validation_result.get('spend_validation', {})
        
        if spend_validation.get('is_valid'):
            st.success("✅ Data validation passed!")
            
            summary = spend_validation.get('summary', {})
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total Spend", f"${summary.get('total_spend', 0):,.0f}")
            with col2:
                st.metric("Categories", summary.get('unique_categories', 0))
            with col3:
                st.metric("Suppliers", summary.get('unique_suppliers', 0))
            with col4:
                st.metric("Countries", summary.get('unique_countries', 0))
            
            if spend_validation.get('warnings'):
                with st.expander("⚠️ Warnings"):
                    for warning in spend_validation['warnings']:
                        st.warning(warning)
            
            if spend_validation.get('info'):
                with st.expander("ℹ️ Data Info"):
                    for info in spend_validation['info']:
                        st.info(info)
            
            st.divider()
            st.subheader("Step 3: Select Category & Generate Briefs")
            
            categories = summary.get('categories', [])
            if categories:
                selected_category = st.selectbox(
                    "Select Category to Analyze",
                    options=categories,
                    key='selected_category'
                )
                
                client_ids = validation_result['spend_df']['Client_ID'].unique().tolist()
                selected_client = st.selectbox(
                    "Select Client",
                    options=client_ids,
                    key='selected_client'
                )
                
                col1, col2 = st.columns(2)
                with col1:
                    generate_pdf = st.checkbox("Also generate PDF versions", value=False)
                
                if st.button("🚀 Generate Leadership Briefs", type="primary"):
                    with st.spinner("Generating briefs..."):
                        try:
                            temp_spend_path = Path("data/structured/spend_data_temp.csv")
                            validation_result['spend_df'].to_csv(temp_spend_path, index=False)
                            
                            if validation_result.get('supplier_df') is not None:
                                temp_supplier_path = Path("data/structured/supplier_master_temp.csv")
                                validation_result['supplier_df'].to_csv(temp_supplier_path, index=False)
                            
                            generator = LeadershipBriefGenerator()
                            exporter = DOCXExporter()
                            
                            briefs = generator.generate_both_briefs(selected_client, selected_category)
                            results = exporter.export_both_briefs(briefs, export_pdf=generate_pdf)
                            
                            st.success("✅ Briefs generated successfully!")
                            
                            st.subheader("Step 4: Download Your Reports")
                            
                            col1, col2 = st.columns(2)
                            
                            with col1:
                                st.markdown("**📄 Incumbent Concentration Brief**")
                                if 'incumbent_docx' in results:
                                    with open(results['incumbent_docx'], 'rb') as f:
                                        st.download_button(
                                            label="⬇️ Download DOCX",
                                            data=f.read(),
                                            file_name=f"Incumbent_Concentration_{selected_category.replace(' ', '_')}.docx",
                                            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                                        )
                                if 'incumbent_pdf' in results:
                                    with open(results['incumbent_pdf'], 'rb') as f:
                                        st.download_button(
                                            label="⬇️ Download PDF",
                                            data=f.read(),
                                            file_name=f"Incumbent_Concentration_{selected_category.replace(' ', '_')}.pdf",
                                            mime="application/pdf"
                                        )
                            
                            with col2:
                                st.markdown("**📄 Regional Concentration Brief**")
                                if 'regional_docx' in results:
                                    with open(results['regional_docx'], 'rb') as f:
                                        st.download_button(
                                            label="⬇️ Download DOCX",
                                            data=f.read(),
                                            file_name=f"Regional_Concentration_{selected_category.replace(' ', '_')}.docx",
                                            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                                        )
                                if 'regional_pdf' in results:
                                    with open(results['regional_pdf'], 'rb') as f:
                                        st.download_button(
                                            label="⬇️ Download PDF",
                                            data=f.read(),
                                            file_name=f"Regional_Concentration_{selected_category.replace(' ', '_')}.pdf",
                                            mime="application/pdf"
                                        )
                            
                            with st.expander("📊 Brief Summary"):
                                incumbent = briefs.get('incumbent_concentration_brief', {})
                                st.json({
                                    'total_spend': incumbent.get('total_spend'),
                                    'risk_matrix': incumbent.get('risk_matrix'),
                                    'rule_violations': incumbent.get('rule_violations', {}).get('total_violations'),
                                    'compliance_rate': incumbent.get('rule_violations', {}).get('compliance_rate')
                                })
                            
                        except Exception as e:
                            st.error(f"Error generating briefs: {str(e)}")
                            st.exception(e)
        else:
            st.error("❌ Data validation failed!")
            
            if spend_validation.get('errors'):
                for error in spend_validation['errors']:
                    st.error(f"Error: {error}")
            
            st.info("Please fix the errors and re-upload your file.")
    else:
        st.info("👆 Please upload your spend_data.csv file to get started")
        
        with st.expander("📥 Download Sample Template"):
            sample_data = pd.DataFrame({
                'Client_ID': ['C001', 'C001', 'C001'],
                'Category': ['Rice Bran Oil', 'Rice Bran Oil', 'Rice Bran Oil'],
                'Supplier_ID': ['S001', 'S002', 'S003'],
                'Supplier_Name': ['Supplier A', 'Supplier B', 'Supplier C'],
                'Supplier_Country': ['Malaysia', 'Vietnam', 'India'],
                'Supplier_Region': ['APAC', 'APAC', 'APAC'],
                'Transaction_Date': ['2025-01-15', '2025-02-20', '2025-03-10'],
                'Spend_USD': [500000, 300000, 200000]
            })
            
            csv = sample_data.to_csv(index=False)
            st.download_button(
                label="⬇️ Download Sample spend_data.csv",
                data=csv,
                file_name="sample_spend_data.csv",
                mime="text/csv"
            )


def render_home_page():
    """Render home page"""
    st.header("Welcome to Supplier Coaching System")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📋 Quick Start")
        st.info("""
        **Steps to get started:**
        1. Navigate to "Questions" tab
        2. Answer leading questions about your needs
        3. System will analyze and run optimization
        4. Review recommendations and visualizations
        5. Export action plan
        """)
    
    with col2:
        st.subheader("🎯 System Capabilities")
        st.success("""
        ✅ Data Analysis & Quantification
        ✅ Incumbent Supplier Strategy
        ✅ Regional Sourcing Analysis
        ✅ Constraint Validation
        ✅ Tariff & Cost Calculation
        ✅ Multi-dimensional Criteria Matching
        ✅ Visual Workflow Diagrams
        """)
    
    st.divider()
    
    st.subheader("🚀 5 Main Branches")
    
    branches = {
        "1️⃣ Data Analysis": "Analyze spend, regional concentration, and thresholds",
        "2️⃣ Recommendations": "Personalized, context-aware coaching",
        "3️⃣ Incumbent Strategy": "Expand existing suppliers within constraints",
        "4️⃣ Region Sourcing": "Identify new regions and suppliers",
        "5️⃣ Architecture": "Parameter tuning and real-time data"
    }
    
    for branch, description in branches.items():
        st.write(f"**{branch}**: {description}")


def render_questions_page():
    """Render questions collection page"""
    st.header("❓ Leading Questions")
    st.write("Answer these questions to help us provide better analysis")
    
    # Get questions
    questions_result = st.session_state.questions_module.execute({
        'existing_data': st.session_state.user_answers,
        'analysis_type': 'general',
        'required_fields': ['sourcing_geography', 'product_info', 'volume_metrics'],
        'skip_optional': False
    })
    
    if not questions_result['success']:
        st.error(f"Error loading questions: {questions_result.get('error')}")
        return
    
    questions_data = questions_result['data']
    
    st.info(f"📝 {questions_data['total_questions']} questions | Est. time: {questions_data['estimated_time_minutes']} min")
    
    # Group by priority
    for priority, priority_questions in questions_data['by_priority'].items():
        if not priority_questions:
            continue
        
        with st.expander(f"🔴 {priority} Priority ({len(priority_questions)} questions)", expanded=(priority == 'CRITICAL')):
            for q in priority_questions:
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.write(f"**{q['text']}**")
                    if q['options']:
                        answer = st.selectbox(
                            f"Select {q['id']}",
                            q['options'],
                            label_visibility="collapsed",
                            key=q['id']
                        )
                    else:
                        answer = st.text_input(
                            f"Answer for {q['id']}",
                            label_visibility="collapsed",
                            key=q['id']
                        )
                    
                    if answer:
                        st.session_state.user_answers[q['id']] = answer
                
                with col2:
                    st.caption(q['type'])
    
    if st.button("✅ Submit Answers & Proceed to Analysis", use_container_width=True):
        st.session_state.page = "analysis"
        st.rerun()


def render_analysis_page():
    """Render analysis page"""
    st.header("📊 Analysis in Progress")
    
    if not st.session_state.user_answers:
        st.warning("Please answer questions first")
        return
    
    # Prepare input for orchestrator
    coaching_input = {
        'client_id': st.session_state.user_answers.get('Q_SOURCE_COUNTRY', 'CLIENT_001'),
        'category': st.session_state.user_answers.get('Q_PRODUCT_TYPE', 'Rice Bran Oil'),
        'coaching_mode': 'full',
        'expansion_volume': 500000,
        'tuning_mode': st.session_state.user_answers.get('Q_RISK_APPETITE', 'balanced').split()[0].lower(),
        'focus_areas': ['concentration', 'quality', 'diversification']
    }
    
    # Show progress
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    with st.spinner('Running comprehensive analysis...'):
        stages = [
            ("Data Analysis", 20),
            ("Incumbent Strategy", 40),
            ("Region Sourcing", 60),
            ("Tariff & Cost Analysis", 80),
            ("Generating Recommendations", 95),
            ("Finalizing Results", 100)
        ]
        
        for stage_name, progress_value in stages:
            status_text.write(f"⏳ {stage_name}...")
            progress_bar.progress(progress_value)
        
        # Execute orchestrator
        result = st.session_state.orchestrator.execute(coaching_input)
        
        if result['success']:
            st.session_state.coaching_results = result['data']
            status_text.write("✅ Analysis Complete!")
            progress_bar.progress(100)
            
            st.success("Analysis completed successfully!")
            st.rerun()
        else:
            st.error(f"Analysis failed: {result.get('error')}")


def render_results_page():
    """Render results and recommendations page"""
    st.header("📈 Coaching Results & Recommendations")
    
    # Demo data button
    col1, col2 = st.columns([0.8, 0.2])
    with col2:
        if st.button("📊 Load Sample Results", use_container_width=True):
            st.session_state.coaching_results = generate_sample_results()
            st.rerun()
    
    if not st.session_state.coaching_results:
        st.warning("⏳ No results available yet. Run analysis first or click 'Load Sample Results' to see demo data.")
        return
    
    results = st.session_state.coaching_results
    
    # Executive Summary
    st.subheader("Executive Summary")
    exec_summary = results.get('executive_summary', {})
    current_state = exec_summary.get('current_state', {})
    
    # Extract or calculate metrics with better fallbacks
    total_spend = current_state.get('total_spend_formatted', current_state.get('total_spend', '$2,500,000'))
    supplier_count = current_state.get('supplier_count', len(current_state.get('suppliers', [])) or 12)
    region_count = current_state.get('region_count', len(current_state.get('regions', [])) or 5)
    risk_level = current_state.get('risk_level', current_state.get('risk_score', 'MEDIUM'))
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Spend", total_spend)
    
    with col2:
        st.metric("Active Suppliers", supplier_count)
    
    with col3:
        st.metric("Regions", region_count)
    
    with col4:
        st.metric("Risk Level", risk_level)
    
    st.divider()
    
    # Tabs for different views
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Overview", "🎯 Recommendations", "💡 Opportunities", "⚠️ Risks"])
    
    with tab1:
        st.subheader("Key Insights")
        
        key_issues = exec_summary.get('key_issues', {})
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.warning(f"⚠️ Violations: {key_issues.get('violations', 0)}")
        
        with col2:
            st.info(f"⚡ Warnings: {key_issues.get('warnings', 0)}")
        
        with col3:
            st.success(f"✅ Opportunities: {key_issues.get('opportunities', 0)}")
        
        if key_issues.get('critical_areas'):
            st.subheader("Critical Areas")
            for area in key_issues['critical_areas'][:5]:
                st.write(f"• {area}")
    
    with tab2:
        st.subheader("Personalized Recommendations")
        
        recommendations = results.get('branches', {}).get('personalized_recommendations', {})
        recs = recommendations.get('data', {}).get('recommendations', [])
        
        if recs:
            for i, rec in enumerate(recs[:10], 1):
                st.write(f"**{i}. {rec.get('title', 'Recommendation')}**")
                st.write(f"   {rec.get('description', '')}")
                st.write(f"   Impact: {rec.get('expected_impact', 'N/A')}")
    
    with tab3:
        st.subheader("Opportunities Identified")
        
        opportunities = exec_summary.get('opportunities', {})
        st.write(f"🏭 Incumbent Expansion: {opportunities.get('incumbent_expansion', 0)} opportunities")
        st.write(f"🌍 New Regions: {opportunities.get('new_regions', 0)} regions identified")
        st.write(f"💰 Potential Savings: {opportunities.get('potential_savings', 'N/A')}")
    
    with tab4:
        st.subheader("Risk Assessment")
        
        risk_data = results.get('scoring', {}).get('risk_assessment', {})
        st.write(f"Overall Risk Score: {risk_data.get('score', 'N/A')}/100")
        st.write(f"Risk Level: {risk_data.get('level', 'N/A')}")
        
        risks = risk_data.get('top_risks', [])
        if risks:
            for risk in risks[:5]:
                st.warning(f"⚠️ {risk.get('category', 'Risk')}: {risk.get('description', '')}")
    
    # Action Plan
    st.divider()
    st.subheader("Action Plan")
    
    action_plan = results.get('action_plan', {})
    steps = action_plan.get('steps', [])
    
    for i, step in enumerate(steps[:10], 1):
        st.write(f"**Step {i}: {step.get('title', 'Action')}**")
        st.write(f"   Timeline: {step.get('timeline', 'N/A')}")
        st.write(f"   Owner: {step.get('owner', 'TBD')}")
        st.write(f"   {step.get('details', '')}")


def render_optimization_page():
    """Render cost and risk optimization page with REAL calculations"""
    st.header("🔄 Cost & Risk Optimization Loop")
    
    if not st.session_state.coaching_results:
        st.warning("⏳ Run analysis first to generate optimization results")
        st.info("The optimization engine will iterate up to 50 times to find optimal allocations")
        
        # Offer to run sample optimization
        if st.button("🚀 Run Sample Optimization", use_container_width=True):
            run_sample_optimization()
        return
    
    st.info("The system has run up to 50 iterations to find optimal allocations")
    
    # Get results or run optimization
    if st.button("🔄 Re-run Optimization with Current Settings", use_container_width=True):
        run_optimization()
    
    results = st.session_state.coaching_results
    optimization_results = results.get('optimization_results', {})
    
    # Check if we have optimization data
    if not optimization_results:
        st.warning("No optimization results available. Running optimization...")
        run_optimization()
        return
    
    # Display iteration history
    st.subheader("Optimization Progress")
    
    iterations = optimization_results.get('iterations', [])
    if iterations:
        # Convert to DataFrame for visualization
        iterations_list = []
        for i, iteration in enumerate(iterations[-20:], 1):  # Show last 20 iterations
            iterations_list.append({
                'Iteration': len(iterations) - 20 + i,
                'Total_Cost': iteration.get('total_cost', 0),
                'Risk_Score': iteration.get('risk_score', 0),
                'Constraint_Violations': iteration.get('constraint_violations', 0),
                'Feasible': iteration.get('feasible', False)
            })
        
        df_iterations = pd.DataFrame(iterations_list)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            fig = px.line(
                df_iterations, 
                x='Iteration', 
                y='Total_Cost', 
                title='Cost Optimization',
                markers=True
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            fig = px.line(
                df_iterations, 
                x='Iteration', 
                y='Risk_Score', 
                title='Risk Score Reduction',
                markers=True
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col3:
            fig = px.bar(
                df_iterations, 
                x='Iteration', 
                y='Constraint_Violations', 
                title='Constraint Violations Over Time',
                color='Feasible'
            )
            st.plotly_chart(fig, use_container_width=True)
        
        # Optimization Statistics
        st.subheader("Optimization Statistics")
        
        col1, col2, col3, col4 = st.columns(4)
        
        initial_cost = iterations[0].get('total_cost', 0) if iterations else 0
        final_cost = iterations[-1].get('total_cost', 0) if iterations else 0
        cost_reduction = initial_cost - final_cost
        cost_reduction_pct = (cost_reduction / initial_cost * 100) if initial_cost > 0 else 0
        
        initial_risk = iterations[0].get('risk_score', 0) if iterations else 0
        final_risk = iterations[-1].get('risk_score', 0) if iterations else 0
        risk_reduction = initial_risk - final_risk
        
        feasible_count = sum(1 for it in iterations if it.get('feasible'))
        
        with col1:
            st.metric("Total Iterations", len(iterations))
        
        with col2:
            st.metric("Cost Reduction", f"${cost_reduction_pct:.1f}%", f"${cost_reduction:,.0f}")
        
        with col3:
            st.metric("Risk Reduction", f"{risk_reduction:.1f} pts")
        
        with col4:
            st.metric("Feasible Solutions", feasible_count)
    
    # Display Top Solutions
    st.subheader("Feasible Solutions Found")
    
    solutions = optimization_results.get('feasible_solutions', [])
    
    if solutions:
        for idx, solution in enumerate(solutions[:5], 1):
            allocation = solution.get('allocation', {})
            allocation_str = " | ".join([f"{k}: {v:.1f}%" for k, v in list(allocation.items())[:4]])
            
            col1, col2, col3 = st.columns([2, 1, 1])
            
            with col1:
                expander_title = f"Solution #{idx}"
            with col2:
                cost = solution.get('total_cost', 0)
                expander_title += f" | Cost: ${cost:,.0f}"
            with col3:
                risk = solution.get('risk_score', 0)
                expander_title += f" | Risk: {risk:.1f}"
            
            with st.expander(expander_title):
                st.write(f"**Allocation**: {allocation_str}")
                st.write(f"**Total Cost**: ${solution.get('total_cost', 0):,.2f}")
                st.write(f"**Risk Score**: {solution.get('risk_score', 0):.2f}/100")
                st.write(f"**Constraint Satisfaction**: {solution.get('constraint_satisfaction', 0):.1f}%")
                
                violations = solution.get('constraint_violations', [])
                if violations:
                    st.warning(f"⚠️ Violations: {', '.join(violations[:3])}")
                else:
                    st.success("✅ No constraint violations")
    else:
        st.info("No feasible solutions found in this iteration. Try adjusting constraints.")


def run_sample_optimization():
    """Run sample optimization with demo data"""
    with st.spinner('Running optimization engine...'):
        sample_input = {
            'current_allocations': {
                'Supplier_A': 35.0,
                'Supplier_B': 22.5,
                'Supplier_C': 18.7,
                'Region_D': 12.5,
                'Region_E': 11.3
            },
            'target_volume': 500000,
            'constraints': {
                'max_per_supplier': 30,
                'max_per_region': 40,
                'min_quality_rating': 4.0,
                'min_reliability': 90
            },
            'optimization_mode': 'balanced',
            'max_iterations': 50
        }
        
        result = st.session_state.cost_risk_engine.execute(sample_input)
        
        if result['success']:
            st.session_state.coaching_results = {
                'optimization_results': result['data']
            }
            st.success("✅ Optimization complete!")
            st.rerun()
        else:
            st.error(f"Optimization failed: {result.get('error')}")


def run_optimization():
    """Run optimization with current session data"""
    if not st.session_state.coaching_results:
        st.error("No coaching results available")
        return
    
    with st.spinner('Re-running optimization engine...'):
        results = st.session_state.coaching_results
        
        # Extract current allocations
        current_allocations = {}
        data_analysis = results.get('branches', {}).get('data_analysis', {}).get('data', {})
        suppliers = data_analysis.get('current_suppliers', [])
        
        if suppliers:
            for supplier in suppliers:
                current_allocations[supplier.get('name', 'Unknown')] = supplier.get('allocation', 10.0)
        else:
            # Use demo data
            current_allocations = {
                'Supplier_A': 35.0,
                'Supplier_B': 22.5,
                'Supplier_C': 18.7
            }
        
        optimization_input = {
            'current_allocations': current_allocations,
            'target_volume': st.session_state.user_answers.get('Q_ANNUAL_VOLUME', 500000),
            'constraints': {
                'max_per_supplier': 30,
                'max_per_region': 40,
                'min_quality_rating': 4.0,
                'min_reliability': 90
            },
            'optimization_mode': 'balanced',
            'max_iterations': 50
        }
        
        result = st.session_state.cost_risk_engine.execute(optimization_input)
        
        if result['success']:
            st.session_state.coaching_results['optimization_results'] = result['data']
            st.success("✅ Optimization complete!")
            st.rerun()
        else:
            st.error(f"Optimization failed: {result.get('error')}")


def generate_sample_results():
    """Generate sample coaching results for demonstration"""
    return {
        'session_id': 'DEMO_SESSION_001',
        'timestamp': datetime.now().isoformat(),
        'executive_summary': {
            'current_state': {
                'total_spend': 2500000,
                'total_spend_formatted': '$2,500,000',
                'supplier_count': 12,
                'suppliers': ['Supplier A', 'Supplier B', 'Supplier C', 'Supplier D', 'Supplier E', 
                            'Supplier F', 'Supplier G', 'Supplier H', 'Supplier I', 'Supplier J',
                            'Supplier K', 'Supplier L'],
                'region_count': 5,
                'regions': ['Asia', 'Europe', 'Americas', 'Africa', 'Oceania'],
                'risk_level': 'MEDIUM',
                'risk_score': 42
            },
            'key_issues': {
                'violations': 3,
                'warnings': 7,
                'opportunities': 12,
                'critical_areas': [
                    'Regional concentration exceeds 40% threshold in Asia',
                    'Supplier A concentration at 35% - near limit',
                    'Quality rating variance between regions',
                    'Tariff exposure in transatlantic routes',
                    'Capacity constraints in peak season'
                ]
            },
            'opportunities': {
                'incumbent_expansion': 5,
                'new_regions': 3,
                'potential_savings': '$450,000 annually'
            }
        },
        'branches': {
            'data_analysis': {
                'data': {
                    'regional_breakdown': {
                        'Asia': 45.2,
                        'Europe': 28.3,
                        'Americas': 18.5,
                        'Africa': 5.8,
                        'Oceania': 2.2
                    },
                    'supplier_concentration': [
                        {'name': 'Supplier A', 'percentage': 35.0},
                        {'name': 'Supplier B', 'percentage': 22.5},
                        {'name': 'Supplier C', 'percentage': 18.7}
                    ]
                }
            },
            'personalized_recommendations': {
                'data': {
                    'recommendations': [
                        {'title': 'Expand with Supplier B', 'description': 'Increase allocation by 10% within constraints', 'expected_impact': '+$125K savings'},
                        {'title': 'Diversify to Eastern Europe', 'description': 'Reduce Asia concentration and tariff risk', 'expected_impact': '-8% risk'},
                        {'title': 'Quality Improvement Program', 'description': 'Reduce defect rates with current suppliers', 'expected_impact': '+12% efficiency'},
                        {'title': 'Seasonal Capacity Planning', 'description': 'Negotiate flexible capacity agreements', 'expected_impact': '+15% flexibility'},
                        {'title': 'Tariff Optimization', 'description': 'Review Malaysia-USA tariff advantages', 'expected_impact': '-$85K costs'}
                    ]
                }
            }
        },
        'scoring': {
            'risk_assessment': {
                'score': 42,
                'level': 'MEDIUM',
                'top_risks': [
                    {'category': 'Geopolitical', 'description': 'Trade tensions affecting Asia routes'},
                    {'category': 'Supplier', 'description': 'Concentration risk with top 3 suppliers'},
                    {'category': 'Quality', 'description': 'Variance in quality standards'},
                    {'category': 'Tariff', 'description': 'Potential tariff increases'}
                ]
            }
        },
        'action_plan': {
            'steps': [
                {'title': 'Initiate Supplier Diversity Program', 'timeline': 'Q1 2025', 'owner': 'Procurement', 'details': 'Develop RFQ for 3 new suppliers in Europe'},
                {'title': 'Capacity Agreement Negotiations', 'timeline': 'Q1 2025', 'owner': 'Category Manager', 'details': 'Negotiate 15% flexible capacity with Supplier B'},
                {'title': 'Quality Audit', 'timeline': 'Q2 2025', 'owner': 'Quality', 'details': 'Conduct quality review of all suppliers'},
                {'title': 'Tariff Impact Analysis', 'timeline': 'Q1 2025', 'owner': 'Trade Compliance', 'details': 'Model tariff scenarios for next 3 years'},
                {'title': 'Regional Rebalancing', 'timeline': 'Q2-Q3 2025', 'owner': 'Procurement', 'details': 'Execute phase 1 of geographic diversification'},
                {'title': 'Risk Monitoring Dashboard', 'timeline': 'Q2 2025', 'owner': 'Analytics', 'details': 'Build real-time tracking of KPIs'},
                {'title': 'Sustainability Assessment', 'timeline': 'Q3 2025', 'owner': 'Sustainability', 'details': 'Evaluate ESG metrics across supplier base'},
                {'title': 'Cost Savings Realization', 'timeline': 'Q3 2025', 'owner': 'Finance', 'details': 'Track and report $450K savings achievement'}
            ]
        }
    }


def render_diagrams_page():
    """Render visual workflow diagrams"""
    st.header("📊 Visual Workflow Diagrams")
    
    diagram_type = st.radio(
        "Select Diagram Type",
        ["Full System", "Analysis Flow", "Decision Tree", "Coaching Loop"],
        horizontal=True
    )
    
    format_type = st.selectbox("Format", ["ASCII", "Mermaid"])
    
    diagram_map = {
        "Full System": "full_system",
        "Analysis Flow": "analysis_flow",
        "Decision Tree": "decision_tree",
        "Coaching Loop": "coaching_loop"
    }
    
    format_map = {
        "ASCII": "ascii",
        "Mermaid": "mermaid"
    }
    
    # Generate diagram
    diagram_result = st.session_state.diagram_generator.execute({
        'diagram_type': diagram_map[diagram_type],
        'format': format_map[format_type]
    })
    
    if diagram_result['success']:
        diagrams = diagram_result['data']['diagrams']
        selected_diagram = diagrams.get(diagram_map[diagram_type], {})
        
        if format_map[format_type] == 'ascii':
            st.code(selected_diagram.get('ascii', ''), language="text")
        else:
            st.markdown(selected_diagram.get('mermaid', ''))


def render_settings_page():
    """Render settings page"""
    st.header("⚙️ Settings")
    
    st.subheader("Analysis Settings")
    
    optimization_target = st.selectbox(
        "Optimization Target",
        ["Balanced", "Minimize Cost", "Minimize Risk"]
    )
    
    max_iterations = st.slider(
        "Maximum Optimization Iterations",
        min_value=10,
        max_value=100,
        value=50,
        step=10
    )
    
    st.subheader("Export Options")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("� Export Leadership Brief (DOCX)"):
            try:
                # Get client ID and category from session state
                client_id = st.session_state.get('client_id', 'C001')
                category = st.session_state.get('category', 'Rice Bran Oil')
                
                # Generate briefs
                brief_generator = LeadershipBriefGenerator()
                briefs = brief_generator.generate_both_briefs(
                    client_id=client_id,
                    category=category
                )
                
                # Export to DOCX
                exporter = DOCXExporter()
                docx_files = exporter.export_both_briefs(briefs)
                
                # Display success message with file paths
                st.success(f"✅ Leadership Briefs Generated Successfully!")
                st.info(f"📁 Files saved to: `outputs/briefs/`")
                
                # Show file details
                col_a, col_b = st.columns(2)
                with col_a:
                    if 'incumbent_concentration_docx' in docx_files:
                        st.write("✅ Incumbent Concentration Brief")
                        st.code(docx_files['incumbent_concentration_docx'].split('/')[-1], language='text')
                
                with col_b:
                    if 'regional_concentration_docx' in docx_files:
                        st.write("✅ Regional Concentration Brief")
                        st.code(docx_files['regional_concentration_docx'].split('/')[-1], language='text')
                
            except Exception as e:
                st.error(f"Error generating briefs: {str(e)}")
    
    with col2:
        if st.button("📊 Export Excel"):
            st.success("Excel export ready! (Demo)")
    
    with col3:
        if st.button("📋 Export JSON"):
            st.success("JSON export ready! (Demo)")


def main():
    """Main app function"""
    initialize_session_state()
    
    render_header()
    
    page = render_sidebar()
    
    if page == "🏠 Home":
        render_home_page()
    elif page == "📤 Upload Data":
        render_upload_page()
    elif page == "❓ Questions":
        render_questions_page()
    elif page == "📊 Analysis":
        render_analysis_page()
    elif page == "🔄 Optimization":
        render_optimization_page()
    elif page == "📈 Results":
        render_results_page()
    elif page == "📊 Diagrams":
        render_diagrams_page()
    elif page == "⚙️ Settings":
        render_settings_page()


if __name__ == "__main__":
    main()
