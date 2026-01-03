"""
Beroe Procurement AI - Streamlit UI
Simple, clean interface for procurement analysis and brief generation

Supports:
- Traditional brief generation (fast, template-based)
- Agent-based brief generation (microagent architecture with RAG + LLM)
"""

import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

# Base directory
BASE_DIR = Path(__file__).parent

# Page config
st.set_page_config(
    page_title="Beroe Procurement AI",
    page_icon="📊",
    layout="wide"
)

# Simple CSS
st.markdown("""
<style>
    .main { padding: 1rem; }
    .stMetric { background: #f8f9fa; padding: 1rem; border-radius: 8px; }
</style>
""", unsafe_allow_html=True)


@st.cache_data
def load_system_data():
    """Load system spend data"""
    try:
        spend_path = BASE_DIR / 'data' / 'structured' / 'spend_data.csv'
        return pd.read_csv(spend_path)
    except:
        return None


def main():
    st.title("📊 Beroe Procurement AI")

    # Sidebar configuration
    with st.sidebar:
        st.header("⚙️ Settings")

        # Agent mode toggle
        use_agents = st.toggle(
            "Use Agent Architecture",
            value=False,
            help="Enable microagent-based brief generation with specialized agents for data analysis, risk assessment, recommendations, and market intelligence."
        )

        # LLM and RAG toggles
        enable_llm = st.toggle(
            "Enable AI-Powered Insights",
            value=True,
            help="Use GPT-4 for AI-generated executive summaries, risk analysis, and recommendations."
        )

        enable_rag = st.toggle(
            "Enable RAG Context",
            value=True,
            help="Use Retrieval Augmented Generation for context-aware insights from knowledge base."
        )

        enable_web_search = st.toggle(
            "Enable Web Search Fallback",
            value=True,
            help="When verified sources don't have enough context, search the internet and cite sources. Uses Serper API."
        )

        st.divider()

        if use_agents:
            st.info("🤖 **Agent Mode Active**\n\nBriefs will be generated using specialized microagents:\n- DataAnalysisAgent\n- RiskAssessmentAgent\n- RecommendationAgent\n- MarketIntelligenceAgent")
        else:
            st.caption("Traditional brief generation mode")

        # Store settings in session state
        st.session_state.use_agents = use_agents
        st.session_state.enable_llm = enable_llm
        st.session_state.enable_rag = enable_rag
        st.session_state.enable_web_search = enable_web_search

    # Initialize session state for storing generated files
    if 'sys_incumbent_data' not in st.session_state:
        st.session_state.sys_incumbent_data = None
    if 'sys_regional_data' not in st.session_state:
        st.session_state.sys_regional_data = None
    if 'sys_incumbent_filename' not in st.session_state:
        st.session_state.sys_incumbent_filename = None
    if 'sys_regional_filename' not in st.session_state:
        st.session_state.sys_regional_filename = None
    if 'user_incumbent_data' not in st.session_state:
        st.session_state.user_incumbent_data = None
    if 'user_regional_data' not in st.session_state:
        st.session_state.user_regional_data = None
    if 'user_incumbent_filename' not in st.session_state:
        st.session_state.user_incumbent_filename = None
    if 'user_regional_filename' not in st.session_state:
        st.session_state.user_regional_filename = None
    if 'briefs_generated' not in st.session_state:
        st.session_state.briefs_generated = False
    if 'user_briefs_generated' not in st.session_state:
        st.session_state.user_briefs_generated = False
    if 'last_subcategory' not in st.session_state:
        st.session_state.last_subcategory = None

    # Chat assistant state
    if 'chat_assistant' not in st.session_state:
        from backend.engines.brief_chat_assistant import BriefChatAssistant
        st.session_state.chat_assistant = BriefChatAssistant()
    if 'chat_messages' not in st.session_state:
        st.session_state.chat_messages = []
    if 'chat_open' not in st.session_state:
        st.session_state.chat_open = False
    if 'brief_context_loaded' not in st.session_state:
        st.session_state.brief_context_loaded = False

    # Two main options as tabs
    tab1, tab2 = st.tabs(["📁 Use System Data", "📤 Upload Your Data"])

    # ========== TAB 1: System Data ==========
    with tab1:
        st.subheader("Generate Briefs from System Data")
        st.caption("Use our pre-loaded multi-industry procurement data (893 suppliers, 10 sectors, 5 regions including Africa & Middle East)")

        df = load_system_data()

        if df is None:
            st.error("Could not load system data.")
            return

        # Filters in columns
        col1, col2, col3 = st.columns(3)

        with col1:
            sectors = sorted(df['Sector'].unique().tolist())
            selected_sector = st.selectbox("1. Select Sector", sectors, key="sys_sector")

        with col2:
            filtered_df = df[df['Sector'] == selected_sector]
            categories = sorted(filtered_df['Category'].unique().tolist())
            selected_category = st.selectbox("2. Select Category", categories, key="sys_category")

        with col3:
            filtered_df = filtered_df[filtered_df['Category'] == selected_category]
            subcategories = sorted(filtered_df['SubCategory'].unique().tolist())
            selected_subcategory = st.selectbox("3. Select SubCategory", subcategories, key="sys_subcategory")

        # Clear old downloads when subcategory changes
        if st.session_state.last_subcategory != selected_subcategory:
            st.session_state.briefs_generated = False
            st.session_state.sys_incumbent_data = None
            st.session_state.sys_regional_data = None
            st.session_state.last_subcategory = selected_subcategory

        # Show preview of selected data
        final_df = df[df['SubCategory'] == selected_subcategory]

        st.divider()

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Spend", f"${final_df['Spend_USD'].sum()/1e6:.2f}M")
        col2.metric("Suppliers", final_df['Supplier_ID'].nunique())
        col3.metric("Countries", final_df['Supplier_Country'].nunique())
        col4.metric("Transactions", len(final_df))

        # Supplier breakdown
        with st.expander("View Suppliers", expanded=False):
            supplier_summary = final_df.groupby(['Supplier_Name', 'Supplier_Country', 'Supplier_Region']).agg({
                'Spend_USD': 'sum',
                'Quality_Rating': 'mean'
            }).reset_index()
            supplier_summary = supplier_summary.sort_values('Spend_USD', ascending=False)
            supplier_summary['Spend_USD'] = supplier_summary['Spend_USD'].apply(lambda x: f"${x:,.0f}")
            supplier_summary['Quality_Rating'] = supplier_summary['Quality_Rating'].round(1)
            supplier_summary.columns = ['Supplier', 'Country', 'Region', 'Spend', 'Quality']
            st.dataframe(supplier_summary, use_container_width=True, hide_index=True)

        # Generate button
        st.divider()

        # Debug info
        st.caption(f"Selected: {selected_sector} → {selected_category} → **{selected_subcategory}** | Transactions: {len(final_df)}")

        if st.button("🚀 Generate Leadership Briefs", type="primary", key="sys_generate"):
            if len(final_df) == 0:
                st.error(f"No data found for subcategory '{selected_subcategory}'. Please select a different subcategory.")
            else:
                mode_text = "agent-based" if st.session_state.use_agents else "traditional"
                with st.spinner(f"Generating briefs for {selected_subcategory} ({mode_text} mode)..."):
                    try:
                        from backend.engines.leadership_brief_generator import LeadershipBriefGenerator
                        from backend.engines.docx_exporter import DOCXExporter

                        # Create generator with current settings
                        generator = LeadershipBriefGenerator(
                            enable_llm=st.session_state.enable_llm,
                            enable_rag=st.session_state.enable_rag,
                            enable_web_search=st.session_state.enable_web_search,
                            use_agents=st.session_state.use_agents
                        )
                        exporter = DOCXExporter()

                        # Get client that has data for this subcategory
                        client_for_subcat = final_df['Client_ID'].iloc[0] if len(final_df) > 0 else "C001"
                        briefs = generator.generate_both_briefs(client_for_subcat, selected_subcategory)
                        results = exporter.export_both_briefs(briefs)

                        # Store file data in session state for persistent downloads
                        if 'incumbent_docx' in results:
                            with open(results['incumbent_docx'], 'rb') as f:
                                st.session_state.sys_incumbent_data = f.read()
                            st.session_state.sys_incumbent_filename = f"Incumbent_Concentration_{selected_subcategory.replace(' ', '_')}.docx"

                        if 'regional_docx' in results:
                            with open(results['regional_docx'], 'rb') as f:
                                st.session_state.sys_regional_data = f.read()
                            st.session_state.sys_regional_filename = f"Regional_Concentration_{selected_subcategory.replace(' ', '_')}.docx"

                        st.session_state.briefs_generated = True

                        # Load brief context for chat assistant
                        if 'incumbent_docx' in results or 'regional_docx' in results:
                            st.session_state.chat_assistant.load_brief_context(
                                incumbent_path=results.get('incumbent_docx'),
                                regional_path=results.get('regional_docx'),
                                subcategory=selected_subcategory
                            )
                            st.session_state.brief_context_loaded = True
                            st.session_state.chat_messages = []  # Reset chat for new brief

                        st.success("✅ Briefs generated successfully!")

                    except Exception as e:
                        st.error(f"Error generating briefs: {str(e)}")
                        import traceback
                        st.code(traceback.format_exc())

        # Show download buttons if briefs have been generated (persists across reruns)
        if st.session_state.briefs_generated and st.session_state.sys_incumbent_data:
            st.divider()
            st.subheader("📥 Download Generated Briefs")
            col1, col2 = st.columns(2)

            with col1:
                if st.session_state.sys_incumbent_data:
                    st.download_button(
                        label="📥 Download Incumbent Concentration Brief",
                        data=st.session_state.sys_incumbent_data,
                        file_name=st.session_state.sys_incumbent_filename,
                        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                        key="sys_inc_download"
                    )

            with col2:
                if st.session_state.sys_regional_data:
                    st.download_button(
                        label="📥 Download Regional Concentration Brief",
                        data=st.session_state.sys_regional_data,
                        file_name=st.session_state.sys_regional_filename,
                        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                        key="sys_reg_download"
                    )

            # ========== VERIFICATION SECTION ==========
            st.divider()
            st.subheader("🔍 Verify Briefs Against Source Data")
            st.caption("Use Perplexity AI to fact-check generated briefs against actual data")

            if st.button("🔍 Verify Briefs", type="secondary", key="sys_verify"):
                with st.spinner("Verifying briefs with Perplexity AI..."):
                    try:
                        from backend.engines.brief_verifier import BriefVerifier
                        from backend.engines.data_loader import DataLoader

                        verifier = BriefVerifier()
                        loader = DataLoader()
                        source_df = loader.load_spend_data()

                        # Get the file paths from session state filenames
                        # We need to find the actual paths
                        import glob
                        subcat_safe = selected_subcategory.replace(' ', '_')
                        incumbent_files = glob.glob(f"outputs/briefs/**/Incumbent_*{subcat_safe}*.docx", recursive=True)
                        regional_files = glob.glob(f"outputs/briefs/**/Regional_*{subcat_safe}*.docx", recursive=True)

                        incumbent_path = incumbent_files[-1] if incumbent_files else None
                        regional_path = regional_files[-1] if regional_files else None

                        if incumbent_path or regional_path:
                            results = verifier.verify_both_briefs(
                                incumbent_path,
                                regional_path,
                                source_df,
                                selected_subcategory
                            )

                            # Display results
                            st.markdown("### Verification Results")

                            # Overall status
                            status_color = "green" if results['overall_status'] == 'PASS' else "orange"
                            st.markdown(f"**Overall Status:** :{status_color}[{results['overall_status']}]")

                            # Incumbent brief
                            with st.expander("📄 Incumbent Brief Verification", expanded=True):
                                inc_result = results.get('incumbent', {})
                                inc_status = inc_result.get('overall_status', 'ERROR')
                                inc_color = "green" if inc_status == 'PASS' else "red"
                                st.markdown(f"**Status:** :{inc_color}[{inc_status}]")
                                st.markdown(f"**Accuracy Score:** {inc_result.get('accuracy_score', 0)}%")

                                if inc_result.get('discrepancies'):
                                    st.warning("Discrepancies Found:")
                                    for d in inc_result['discrepancies']:
                                        st.markdown(f"- **{d['field']}**: DOCX={d['docx_value']}, Expected={d['expected_value']}")
                                else:
                                    st.success("No discrepancies found!")

                                if inc_result.get('llm_analysis', {}).get('analysis'):
                                    st.markdown("**AI Analysis:**")
                                    st.info(inc_result['llm_analysis']['analysis'])

                            # Regional brief
                            with st.expander("📄 Regional Brief Verification", expanded=True):
                                reg_result = results.get('regional', {})
                                reg_status = reg_result.get('overall_status', 'ERROR')
                                reg_color = "green" if reg_status == 'PASS' else "red"
                                st.markdown(f"**Status:** :{reg_color}[{reg_status}]")
                                st.markdown(f"**Accuracy Score:** {reg_result.get('accuracy_score', 0)}%")

                                if reg_result.get('discrepancies'):
                                    st.warning("Discrepancies Found:")
                                    for d in reg_result['discrepancies']:
                                        st.markdown(f"- **{d['field']}**: DOCX={d['docx_value']}, Expected={d['expected_value']}")
                                else:
                                    st.success("No discrepancies found!")

                                if reg_result.get('llm_analysis', {}).get('analysis'):
                                    st.markdown("**AI Analysis:**")
                                    st.info(reg_result['llm_analysis']['analysis'])

                            # Expected vs Actual comparison
                            with st.expander("📊 Expected Values from Source Data"):
                                expected = results.get('incumbent', {}).get('expected_values', {})
                                if expected and 'error' not in expected:
                                    col1, col2, col3 = st.columns(3)
                                    with col1:
                                        st.metric("Total Spend", f"${expected.get('total_spend', 0):,.0f}")
                                    with col2:
                                        st.metric("Suppliers", expected.get('num_suppliers', 0))
                                    with col3:
                                        st.metric("Transactions", expected.get('num_transactions', 0))

                                    st.markdown(f"**Dominant Supplier:** {expected.get('dominant_supplier', 'N/A')} ({expected.get('dominant_supplier_pct', 0):.1f}%)")
                                    st.markdown(f"**Dominant Region:** {expected.get('dominant_region', 'N/A')} ({expected.get('dominant_region_pct', 0):.1f}%)")

                        else:
                            st.error("Could not find generated brief files. Please generate briefs first.")

                    except Exception as e:
                        st.error(f"Verification failed: {str(e)}")
                        import traceback
                        st.code(traceback.format_exc())

    # ========== TAB 2: Upload Data ==========
    with tab2:
        st.subheader("Upload Your Own Data")
        st.caption("Upload your spend data CSV to generate custom briefs")

        # File upload
        uploaded_file = st.file_uploader("Upload spend_data.csv", type=['csv'])

        # Show required format
        with st.expander("📋 Required CSV Format"):
            st.markdown("""
**Required columns:**
- `Client_ID` - Your client/company identifier
- `Sector` - Industry sector (e.g., "Food & Beverages", "Information Technology")
- `Category` - Category name (e.g., "Edible Oils", "Cloud Services")
- `SubCategory` - Subcategory name (e.g., "Rice Bran Oil", "IaaS")
- `Supplier_ID` - Unique supplier identifier
- `Supplier_Name` - Supplier company name
- `Supplier_Country` - Country where supplier is located
- `Supplier_Region` - Region (APAC, Americas, EMEA, etc.)
- `Spend_USD` - Spend amount in USD

**Optional columns (recommended for better analysis):**
- `Supplier_City` - City where supplier is located
- `Transaction_Date` - Date of transaction (YYYY-MM-DD)
- `Contract_Type` - Type of contract (e.g., "Fixed", "Variable")
- `Payment_Terms` - Payment terms (e.g., "Net 30", "Net 60")
- `Quality_Rating` - Quality score (1.0 - 5.0)
- `Delivery_Rating` - Delivery score (1.0 - 5.0)
- `Risk_Score` - Risk score (1.0 - 10.0)
            """)

            # Download sample template with ALL useful columns
            sample_data = pd.DataFrame({
                'Client_ID': ['C001', 'C001', 'C001', 'C001'],
                'Sector': ['Food & Beverages', 'Food & Beverages', 'Information Technology', 'Information Technology'],
                'Category': ['Edible Oils', 'Edible Oils', 'Cloud Services', 'Cloud Services'],
                'SubCategory': ['Rice Bran Oil', 'Palm Oil', 'IaaS', 'IaaS'],
                'Supplier_ID': ['S001', 'S002', 'S201', 'S202'],
                'Supplier_Name': ['Adani Wilmar', 'Cargill Foods', 'Amazon Web Services', 'Microsoft Azure'],
                'Supplier_Country': ['India', 'Indonesia', 'USA', 'USA'],
                'Supplier_Region': ['APAC', 'APAC', 'Americas', 'Americas'],
                'Supplier_City': ['Mumbai', 'Jakarta', 'Seattle', 'Redmond'],
                'Transaction_Date': ['2025-01-15', '2025-02-20', '2025-03-10', '2025-03-15'],
                'Spend_USD': [500000, 450000, 850000, 650000],
                'Contract_Type': ['Fixed', 'Variable', 'Fixed', 'Fixed'],
                'Payment_Terms': ['Net 30', 'Net 45', 'Net 30', 'Net 30'],
                'Quality_Rating': [4.5, 4.2, 4.8, 4.7],
                'Delivery_Rating': [4.3, 4.0, 4.6, 4.5],
                'Risk_Score': [3.2, 4.1, 2.5, 2.8]
            })

            st.download_button(
                "⬇️ Download Sample Template",
                sample_data.to_csv(index=False),
                "sample_spend_data.csv",
                "text/csv"
            )

        if uploaded_file is not None:
            try:
                user_df = pd.read_csv(uploaded_file)

                # Validate required columns
                required_cols = ['Client_ID', 'Sector', 'Category', 'SubCategory',
                               'Supplier_ID', 'Supplier_Name', 'Supplier_Country',
                               'Supplier_Region', 'Spend_USD']

                missing_cols = [col for col in required_cols if col not in user_df.columns]

                if missing_cols:
                    st.error(f"Missing required columns: {', '.join(missing_cols)}")
                    return

                st.success(f"✅ File loaded: {len(user_df)} transactions")

                st.divider()

                # Show summary
                col1, col2, col3, col4 = st.columns(4)
                col1.metric("Total Spend", f"${user_df['Spend_USD'].sum()/1e6:.2f}M")
                col2.metric("Suppliers", user_df['Supplier_ID'].nunique())
                col3.metric("Categories", user_df['SubCategory'].nunique())
                col4.metric("Countries", user_df['Supplier_Country'].nunique())

                # Select category for brief
                st.divider()

                col1, col2 = st.columns(2)

                with col1:
                    user_subcategories = sorted(user_df['SubCategory'].unique().tolist())
                    selected_user_subcategory = st.selectbox("Select SubCategory for Brief", user_subcategories, key="user_subcategory")

                with col2:
                    user_clients = user_df['Client_ID'].unique().tolist()
                    selected_user_client = st.selectbox("Select Client", user_clients, key="user_client")

                # Preview selected data
                preview_df = user_df[user_df['SubCategory'] == selected_user_subcategory]
                with st.expander("View Selected Data", expanded=False):
                    st.dataframe(preview_df, use_container_width=True, hide_index=True)

                # Generate button
                if st.button("🚀 Generate Leadership Briefs", type="primary", key="user_generate"):
                    mode_text = "agent-based" if st.session_state.use_agents else "traditional"
                    with st.spinner(f"Generating briefs from your data ({mode_text} mode)..."):
                        try:
                            from backend.engines.leadership_brief_generator import LeadershipBriefGenerator
                            from backend.engines.docx_exporter import DOCXExporter
                            from backend.engines.data_loader import DataLoader

                            # Create custom data loader with uploaded data
                            custom_loader = DataLoader()
                            custom_loader.set_spend_data(user_df)

                            # Create generator with current settings and custom data loader
                            generator = LeadershipBriefGenerator(
                                data_loader=custom_loader,
                                enable_llm=st.session_state.enable_llm,
                                enable_rag=st.session_state.enable_rag,
                                enable_web_search=st.session_state.enable_web_search,
                                use_agents=st.session_state.use_agents
                            )
                            exporter = DOCXExporter()

                            briefs = generator.generate_both_briefs(selected_user_client, selected_user_subcategory)
                            results = exporter.export_both_briefs(briefs)

                            # Store file data in session state for persistent downloads
                            if 'incumbent_docx' in results:
                                with open(results['incumbent_docx'], 'rb') as f:
                                    st.session_state.user_incumbent_data = f.read()
                                st.session_state.user_incumbent_filename = f"Incumbent_Concentration_{selected_user_subcategory.replace(' ', '_')}.docx"

                            if 'regional_docx' in results:
                                with open(results['regional_docx'], 'rb') as f:
                                    st.session_state.user_regional_data = f.read()
                                st.session_state.user_regional_filename = f"Regional_Concentration_{selected_user_subcategory.replace(' ', '_')}.docx"

                            st.session_state.user_briefs_generated = True

                            # Load brief context for chat assistant
                            if 'incumbent_docx' in results or 'regional_docx' in results:
                                st.session_state.chat_assistant.load_brief_context(
                                    incumbent_path=results.get('incumbent_docx'),
                                    regional_path=results.get('regional_docx'),
                                    subcategory=selected_user_subcategory
                                )
                                st.session_state.brief_context_loaded = True
                                st.session_state.chat_messages = []  # Reset chat for new brief

                            st.success("✅ Briefs generated from your data!")

                        except Exception as e:
                            st.error(f"Error generating briefs: {str(e)}")
                            import traceback
                            st.code(traceback.format_exc())

                # Show download buttons if briefs have been generated (persists across reruns)
                if st.session_state.user_briefs_generated and st.session_state.user_incumbent_data:
                    st.divider()
                    st.subheader("📥 Download Generated Briefs")
                    col1, col2 = st.columns(2)

                    with col1:
                        if st.session_state.user_incumbent_data:
                            st.download_button(
                                label="📥 Download Incumbent Concentration Brief",
                                data=st.session_state.user_incumbent_data,
                                file_name=st.session_state.user_incumbent_filename,
                                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                                key="user_inc_download"
                            )

                    with col2:
                        if st.session_state.user_regional_data:
                            st.download_button(
                                label="📥 Download Regional Concentration Brief",
                                data=st.session_state.user_regional_data,
                                file_name=st.session_state.user_regional_filename,
                                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                                key="user_reg_download"
                            )

                    # ========== VERIFICATION SECTION (Upload Tab) ==========
                    st.divider()
                    st.subheader("🔍 Verify Briefs Against Your Data")
                    st.caption("Use Perplexity AI to fact-check generated briefs against your uploaded data")

                    if st.button("🔍 Verify Briefs", type="secondary", key="user_verify"):
                        with st.spinner("Verifying briefs with Perplexity AI..."):
                            try:
                                from backend.engines.brief_verifier import BriefVerifier

                                verifier = BriefVerifier()

                                # Get the file paths
                                import glob
                                subcat_safe = selected_user_subcategory.replace(' ', '_')
                                incumbent_files = glob.glob(f"outputs/briefs/**/Incumbent_*{subcat_safe}*.docx", recursive=True)
                                regional_files = glob.glob(f"outputs/briefs/**/Regional_*{subcat_safe}*.docx", recursive=True)

                                incumbent_path = incumbent_files[-1] if incumbent_files else None
                                regional_path = regional_files[-1] if regional_files else None

                                if incumbent_path or regional_path:
                                    results = verifier.verify_both_briefs(
                                        incumbent_path,
                                        regional_path,
                                        user_df,  # Use the uploaded dataframe
                                        selected_user_subcategory
                                    )

                                    # Display results
                                    st.markdown("### Verification Results")

                                    # Overall status
                                    status_color = "green" if results['overall_status'] == 'PASS' else "orange"
                                    st.markdown(f"**Overall Status:** :{status_color}[{results['overall_status']}]")

                                    # Incumbent brief
                                    with st.expander("📄 Incumbent Brief Verification", expanded=True):
                                        inc_result = results.get('incumbent', {})
                                        inc_status = inc_result.get('overall_status', 'ERROR')
                                        inc_color = "green" if inc_status == 'PASS' else "red"
                                        st.markdown(f"**Status:** :{inc_color}[{inc_status}]")
                                        st.markdown(f"**Accuracy Score:** {inc_result.get('accuracy_score', 0)}%")

                                        if inc_result.get('discrepancies'):
                                            st.warning("Discrepancies Found:")
                                            for d in inc_result['discrepancies']:
                                                st.markdown(f"- **{d['field']}**: DOCX={d['docx_value']}, Expected={d['expected_value']}")
                                        else:
                                            st.success("No discrepancies found!")

                                        if inc_result.get('llm_analysis', {}).get('analysis'):
                                            st.markdown("**AI Analysis:**")
                                            st.info(inc_result['llm_analysis']['analysis'])

                                    # Regional brief
                                    with st.expander("📄 Regional Brief Verification", expanded=True):
                                        reg_result = results.get('regional', {})
                                        reg_status = reg_result.get('overall_status', 'ERROR')
                                        reg_color = "green" if reg_status == 'PASS' else "red"
                                        st.markdown(f"**Status:** :{reg_color}[{reg_status}]")
                                        st.markdown(f"**Accuracy Score:** {reg_result.get('accuracy_score', 0)}%")

                                        if reg_result.get('discrepancies'):
                                            st.warning("Discrepancies Found:")
                                            for d in reg_result['discrepancies']:
                                                st.markdown(f"- **{d['field']}**: DOCX={d['docx_value']}, Expected={d['expected_value']}")
                                        else:
                                            st.success("No discrepancies found!")

                                        if reg_result.get('llm_analysis', {}).get('analysis'):
                                            st.markdown("**AI Analysis:**")
                                            st.info(reg_result['llm_analysis']['analysis'])

                                    # Expected vs Actual comparison
                                    with st.expander("📊 Expected Values from Your Data"):
                                        expected = results.get('incumbent', {}).get('expected_values', {})
                                        if expected and 'error' not in expected:
                                            col1, col2, col3 = st.columns(3)
                                            with col1:
                                                st.metric("Total Spend", f"${expected.get('total_spend', 0):,.0f}")
                                            with col2:
                                                st.metric("Suppliers", expected.get('num_suppliers', 0))
                                            with col3:
                                                st.metric("Transactions", expected.get('num_transactions', 0))

                                            st.markdown(f"**Dominant Supplier:** {expected.get('dominant_supplier', 'N/A')} ({expected.get('dominant_supplier_pct', 0):.1f}%)")
                                            st.markdown(f"**Dominant Region:** {expected.get('dominant_region', 'N/A')} ({expected.get('dominant_region_pct', 0):.1f}%)")

                                else:
                                    st.error("Could not find generated brief files. Please generate briefs first.")

                            except Exception as e:
                                st.error(f"Verification failed: {str(e)}")
                                import traceback
                                st.code(traceback.format_exc())

            except Exception as e:
                st.error(f"Error reading file: {str(e)}")

    # ========== CHAT ASSISTANT (Inline at bottom) ==========
    # Show chat when briefs have been generated
    if st.session_state.brief_context_loaded:
        st.divider()

        # Chat header
        col1, col2 = st.columns([3, 1])
        with col1:
            st.subheader("💬 Brief Assistant")
            subcategory = st.session_state.chat_assistant.subcategory
            st.caption(f"Ask questions about your **{subcategory}** brief")
        with col2:
            if st.button("🗑️ Clear Chat", key="clear_chat"):
                st.session_state.chat_messages = []
                st.session_state.chat_assistant.clear_history()
                st.rerun()

        # Suggested questions
        if len(st.session_state.chat_messages) == 0:
            st.markdown("**Suggested questions:**")
            suggestions = st.session_state.chat_assistant.get_suggested_questions()
            cols = st.columns(2)
            for i, suggestion in enumerate(suggestions[:4]):
                with cols[i % 2]:
                    if st.button(suggestion, key=f"suggest_{i}", use_container_width=True):
                        st.session_state.chat_messages.append({
                            "role": "user",
                            "content": suggestion
                        })
                        with st.spinner("Thinking..."):
                            response = st.session_state.chat_assistant.chat(suggestion)
                            st.session_state.chat_messages.append({
                                "role": "assistant",
                                "content": response.get('response', 'Sorry, I encountered an error.')
                            })
                        st.rerun()

        # Display chat messages
        for message in st.session_state.chat_messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        # Chat input
        user_input = st.chat_input("Ask about your procurement brief...")

        if user_input:
            st.session_state.chat_messages.append({
                "role": "user",
                "content": user_input
            })

            with st.spinner("Thinking..."):
                response = st.session_state.chat_assistant.chat(user_input)
                assistant_message = response.get('response', 'Sorry, I encountered an error.')
                st.session_state.chat_messages.append({
                    "role": "assistant",
                    "content": assistant_message
                })

            st.rerun()

    elif st.session_state.briefs_generated or st.session_state.user_briefs_generated:
        st.divider()
        st.info("💬 **Brief Assistant** - Generate briefs to start chatting about your procurement data")


if __name__ == "__main__":
    main()
