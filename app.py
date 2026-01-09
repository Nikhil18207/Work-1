"""
Procurement AI - Streamlit UI
Simple, clean interface for procurement analysis and brief generation

Supports:
- Traditional brief generation (fast, template-based)
- Agent-based brief generation (microagent architecture with RAG + LLM)
"""

import streamlit as st
import pandas as pd
import numpy as np
import logging
from pathlib import Path
from typing import Optional, List, Dict, Any, Tuple

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Base directory
BASE_DIR = Path(__file__).parent

# Page config
st.set_page_config(
    page_title="Procurement AI",
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


class CSVValidator:
    """Validates uploaded CSV files for data quality and structure"""

    REQUIRED_COLUMNS = [
        'Client_ID', 'Sector', 'Category', 'SubCategory',
        'Supplier_ID', 'Supplier_Name', 'Supplier_Country',
        'Supplier_Region', 'Spend_USD'
    ]

    OPTIONAL_COLUMNS = [
        'Supplier_City', 'Transaction_Date', 'Contract_Type',
        'Payment_Terms', 'Quality_Rating', 'Delivery_Rating', 'Risk_Score'
    ]

    VALID_REGIONS = ['APAC', 'Americas', 'Europe', 'Middle East', 'Africa', 'EMEA']

    @classmethod
    def validate(cls, df: pd.DataFrame) -> Tuple[bool, List[str], List[str]]:
        """
        Validate DataFrame structure and data quality.

        Returns:
            Tuple of (is_valid, errors, warnings)
        """
        errors = []
        warnings = []

        # Check required columns
        missing_cols = [col for col in cls.REQUIRED_COLUMNS if col not in df.columns]
        if missing_cols:
            errors.append(f"Missing required columns: {', '.join(missing_cols)}")
            return False, errors, warnings

        # Check for empty DataFrame
        if df.empty:
            errors.append("CSV file is empty")
            return False, errors, warnings

        # Validate Spend_USD is numeric and positive
        try:
            df['Spend_USD'] = pd.to_numeric(df['Spend_USD'], errors='coerce')
            if df['Spend_USD'].isna().any():
                nan_count = df['Spend_USD'].isna().sum()
                errors.append(f"{nan_count} rows have non-numeric Spend_USD values")
            if (df['Spend_USD'] < 0).any():
                neg_count = (df['Spend_USD'] < 0).sum()
                warnings.append(f"{neg_count} rows have negative Spend_USD values")
        except Exception as e:
            errors.append(f"Error validating Spend_USD: {str(e)}")

        # Validate no null values in required columns
        for col in cls.REQUIRED_COLUMNS:
            null_count = df[col].isna().sum()
            if null_count > 0:
                if col == 'Spend_USD':
                    continue  # Already handled above
                warnings.append(f"{null_count} null values in '{col}' column")

        # Validate regions if present
        if 'Supplier_Region' in df.columns:
            invalid_regions = df[~df['Supplier_Region'].isin(cls.VALID_REGIONS)]['Supplier_Region'].unique()
            if len(invalid_regions) > 0:
                warnings.append(f"Non-standard regions found: {', '.join(str(r) for r in invalid_regions[:5])}")

        # Validate ratings are in expected range
        for rating_col in ['Quality_Rating', 'Delivery_Rating']:
            if rating_col in df.columns:
                df[rating_col] = pd.to_numeric(df[rating_col], errors='coerce')
                out_of_range = ((df[rating_col] < 0) | (df[rating_col] > 5)).sum()
                if out_of_range > 0:
                    warnings.append(f"{out_of_range} rows have {rating_col} outside 0-5 range")

        # Validate Transaction_Date if present
        if 'Transaction_Date' in df.columns:
            try:
                df['Transaction_Date'] = pd.to_datetime(df['Transaction_Date'], errors='coerce')
                invalid_dates = df['Transaction_Date'].isna().sum()
                if invalid_dates > 0:
                    warnings.append(f"{invalid_dates} rows have invalid date format")
            except Exception:
                warnings.append("Could not parse Transaction_Date column")

        # Check for duplicate Supplier_IDs with different names
        supplier_name_counts = df.groupby('Supplier_ID')['Supplier_Name'].nunique()
        inconsistent_suppliers = supplier_name_counts[supplier_name_counts > 1]
        if len(inconsistent_suppliers) > 0:
            warnings.append(f"{len(inconsistent_suppliers)} Supplier_IDs have inconsistent names")

        is_valid = len(errors) == 0
        return is_valid, errors, warnings


@st.cache_data
def load_system_data() -> Optional[pd.DataFrame]:
    """Load system spend data with proper error handling"""
    try:
        spend_path = BASE_DIR / 'data' / 'structured' / 'spend_data.csv'
        if not spend_path.exists():
            logger.error(f"Spend data file not found: {spend_path}")
            return None

        df = pd.read_csv(spend_path)
        logger.info(f"Loaded {len(df)} transactions from system data")
        return df

    except pd.errors.EmptyDataError:
        logger.error("Spend data file is empty")
        return None
    except pd.errors.ParserError as e:
        logger.error(f"Error parsing spend data CSV: {e}")
        return None
    except PermissionError:
        logger.error("Permission denied reading spend data file")
        return None
    except Exception as e:
        logger.error(f"Unexpected error loading spend data: {e}")
        return None


def initialize_session_state():
    """Initialize all session state variables"""
    defaults = {
        'sys_incumbent_data': None,
        'sys_regional_data': None,
        'sys_incumbent_filename': None,
        'sys_regional_filename': None,
        'user_incumbent_data': None,
        'user_regional_data': None,
        'user_incumbent_filename': None,
        'user_regional_filename': None,
        'briefs_generated': False,
        'user_briefs_generated': False,
        'last_subcategory': None,
        'chat_messages': [],
        'chat_open': False,
        'brief_context_loaded': False,
        'use_agents': False,
        'enable_llm': True,
        'enable_rag': True,
        'enable_web_search': True,
    }

    for key, default_value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = default_value

    # Initialize chat assistant separately (requires import)
    if 'chat_assistant' not in st.session_state:
        try:
            from backend.engines.brief_chat_assistant import BriefChatAssistant
            st.session_state.chat_assistant = BriefChatAssistant()
        except ImportError as e:
            logger.warning(f"Could not initialize chat assistant: {e}")
            st.session_state.chat_assistant = None


def render_sidebar():
    """Render sidebar settings"""
    with st.sidebar:
        st.header("⚙️ Settings")

        # Agent mode toggle
        use_agents = st.toggle(
            "Use Agent Architecture",
            value=st.session_state.get('use_agents', False),
            help="Enable microagent-based brief generation with specialized agents."
        )

        # LLM and RAG toggles
        enable_llm = st.toggle(
            "Enable AI-Powered Insights",
            value=st.session_state.get('enable_llm', True),
            help="Use GPT-4 for AI-generated executive summaries, risk analysis, and recommendations."
        )

        enable_rag = st.toggle(
            "Enable RAG Context",
            value=st.session_state.get('enable_rag', True),
            help="Use Retrieval Augmented Generation for context-aware insights."
        )

        enable_web_search = st.toggle(
            "Enable Web Search Fallback",
            value=st.session_state.get('enable_web_search', True),
            help="Search the internet when verified sources don't have enough context."
        )

        st.divider()

        if use_agents:
            st.info("🤖 **Agent Mode Active**\n\nBriefs use specialized microagents:\n- DataAnalysisAgent\n- RiskAssessmentAgent\n- RecommendationAgent\n- MarketIntelligenceAgent")
        else:
            st.caption("Traditional brief generation mode")

        # Store settings in session state
        st.session_state.use_agents = use_agents
        st.session_state.enable_llm = enable_llm
        st.session_state.enable_rag = enable_rag
        st.session_state.enable_web_search = enable_web_search


def generate_briefs(
    df: pd.DataFrame,
    client_id: str,
    subcategory: str,
    custom_loader=None
) -> Dict[str, Any]:
    """
    Generate leadership briefs with proper error handling.

    Returns:
        Dictionary with 'success', 'results', and optional 'error' keys
    """
    try:
        from backend.engines.leadership_brief_generator import LeadershipBriefGenerator
        from backend.engines.docx_exporter import DOCXExporter

        # Create generator with current settings
        generator = LeadershipBriefGenerator(
            data_loader=custom_loader,
            enable_llm=st.session_state.enable_llm,
            enable_rag=st.session_state.enable_rag,
            enable_web_search=st.session_state.enable_web_search,
            use_agents=st.session_state.use_agents
        )
        exporter = DOCXExporter()

        briefs = generator.generate_both_briefs(client_id, subcategory)
        results = exporter.export_both_briefs(briefs)

        logger.info(f"Successfully generated briefs for {subcategory}")
        return {'success': True, 'results': results, 'briefs': briefs}

    except ImportError as e:
        logger.error(f"Import error generating briefs: {e}")
        return {'success': False, 'error': f"Missing dependency: {str(e)}"}
    except FileNotFoundError as e:
        logger.error(f"File not found: {e}")
        return {'success': False, 'error': f"Required file not found: {str(e)}"}
    except ValueError as e:
        logger.error(f"Value error: {e}")
        return {'success': False, 'error': f"Invalid data: {str(e)}"}
    except Exception as e:
        logger.error(f"Unexpected error generating briefs: {e}")
        return {'success': False, 'error': str(e)}


def verify_briefs(
    subcategory: str,
    source_df: pd.DataFrame
) -> Dict[str, Any]:
    """
    Verify generated briefs against source data.

    Returns:
        Dictionary with verification results
    """
    try:
        from backend.engines.brief_verifier import BriefVerifier
        import glob

        verifier = BriefVerifier()

        # Find brief files
        subcat_safe = subcategory.replace(' ', '_')
        incumbent_files = glob.glob(f"outputs/briefs/**/Incumbent_*{subcat_safe}*.docx", recursive=True)
        regional_files = glob.glob(f"outputs/briefs/**/Regional_*{subcat_safe}*.docx", recursive=True)

        incumbent_path = incumbent_files[-1] if incumbent_files else None
        regional_path = regional_files[-1] if regional_files else None

        if not incumbent_path and not regional_path:
            return {'success': False, 'error': "No brief files found"}

        results = verifier.verify_both_briefs(
            incumbent_path,
            regional_path,
            source_df,
            subcategory
        )

        return {'success': True, 'results': results}

    except ImportError as e:
        logger.error(f"Import error during verification: {e}")
        return {'success': False, 'error': f"Missing dependency: {str(e)}"}
    except Exception as e:
        logger.error(f"Verification error: {e}")
        return {'success': False, 'error': str(e)}


def render_system_data_tab(df: pd.DataFrame):
    """Render the system data tab"""
    st.subheader("Generate Briefs from System Data")
    st.caption("Use our pre-loaded multi-industry procurement data (893 suppliers, 10 sectors, 5 regions)")

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

    st.divider()
    st.caption(f"Selected: {selected_sector} → {selected_category} → **{selected_subcategory}** | Transactions: {len(final_df)}")

    # Generate button
    if st.button("🚀 Generate Leadership Briefs", type="primary", key="sys_generate"):
        if len(final_df) == 0:
            st.error(f"No data found for subcategory '{selected_subcategory}'.")
        else:
            mode_text = "agent-based" if st.session_state.use_agents else "traditional"
            with st.spinner(f"Generating briefs for {selected_subcategory} ({mode_text} mode)..."):
                client_for_subcat = final_df['Client_ID'].iloc[0]
                result = generate_briefs(final_df, client_for_subcat, selected_subcategory)

                if result['success']:
                    results = result['results']

                    # Store file data for downloads
                    if 'incumbent_docx' in results:
                        try:
                            with open(results['incumbent_docx'], 'rb') as f:
                                st.session_state.sys_incumbent_data = f.read()
                            st.session_state.sys_incumbent_filename = f"Incumbent_Concentration_{selected_subcategory.replace(' ', '_')}.docx"
                        except IOError as e:
                            logger.error(f"Error reading incumbent brief: {e}")

                    if 'regional_docx' in results:
                        try:
                            with open(results['regional_docx'], 'rb') as f:
                                st.session_state.sys_regional_data = f.read()
                            st.session_state.sys_regional_filename = f"Regional_Concentration_{selected_subcategory.replace(' ', '_')}.docx"
                        except IOError as e:
                            logger.error(f"Error reading regional brief: {e}")

                    st.session_state.briefs_generated = True

                    # Load brief context for chat assistant
                    if st.session_state.chat_assistant and ('incumbent_docx' in results or 'regional_docx' in results):
                        try:
                            st.session_state.chat_assistant.load_brief_context(
                                incumbent_path=results.get('incumbent_docx'),
                                regional_path=results.get('regional_docx'),
                                subcategory=selected_subcategory
                            )
                            st.session_state.brief_context_loaded = True
                            st.session_state.chat_messages = []
                        except Exception as e:
                            logger.warning(f"Could not load chat context: {e}")

                    st.success("✅ Briefs generated successfully!")
                else:
                    st.error(f"Error generating briefs: {result['error']}")
                    import traceback
                    st.code(traceback.format_exc())

    # Download buttons
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

        # Verification section
        render_verification_section(selected_subcategory, df)


def render_verification_section(subcategory: str, source_df: pd.DataFrame):
    """Render brief verification section"""
    st.divider()
    st.subheader("🔍 Verify Briefs Against Source Data")
    st.caption("Fact-check generated briefs against actual data")

    if st.button("🔍 Verify Briefs", type="secondary", key="verify_btn"):
        with st.spinner("Verifying briefs..."):
            result = verify_briefs(subcategory, source_df)

            if result['success']:
                results = result['results']
                st.markdown("### Verification Results")

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
            else:
                st.error(f"Verification failed: {result['error']}")


def render_upload_data_tab():
    """Render the upload data tab"""
    st.subheader("Upload Your Own Data")
    st.caption("Upload your spend data CSV to generate custom briefs")

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
- `Supplier_Region` - Region (APAC, Americas, Europe, Middle East, Africa)
- `Spend_USD` - Spend amount in USD (numeric)

**Optional columns (recommended for better analysis):**
- `Supplier_City` - City where supplier is located
- `Transaction_Date` - Date of transaction (YYYY-MM-DD)
- `Contract_Type` - Type of contract (e.g., "Fixed", "Variable")
- `Payment_Terms` - Payment terms (e.g., "Net 30", "Net 60")
- `Quality_Rating` - Quality score (1.0 - 5.0)
- `Delivery_Rating` - Delivery score (1.0 - 5.0)
- `Risk_Score` - Risk score (LOW, MEDIUM, HIGH)
        """)

        # Download sample template
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
            'Risk_Score': ['LOW', 'MEDIUM', 'LOW', 'LOW']
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

            # Validate CSV
            is_valid, errors, warnings = CSVValidator.validate(user_df)

            if not is_valid:
                for error in errors:
                    st.error(f"❌ {error}")
                return

            # Show warnings
            for warning in warnings:
                st.warning(f"⚠️ {warning}")

            st.success(f"✅ File loaded: {len(user_df)} transactions")

            st.divider()

            # Show summary
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Total Spend", f"${user_df['Spend_USD'].sum()/1e6:.2f}M")
            col2.metric("Suppliers", user_df['Supplier_ID'].nunique())
            col3.metric("Categories", user_df['SubCategory'].nunique())
            col4.metric("Countries", user_df['Supplier_Country'].nunique())

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
                        from backend.engines.data_loader import DataLoader

                        custom_loader = DataLoader()
                        custom_loader.set_spend_data(user_df)

                        result = generate_briefs(
                            user_df,
                            selected_user_client,
                            selected_user_subcategory,
                            custom_loader
                        )

                        if result['success']:
                            results = result['results']

                            if 'incumbent_docx' in results:
                                with open(results['incumbent_docx'], 'rb') as f:
                                    st.session_state.user_incumbent_data = f.read()
                                st.session_state.user_incumbent_filename = f"Incumbent_Concentration_{selected_user_subcategory.replace(' ', '_')}.docx"

                            if 'regional_docx' in results:
                                with open(results['regional_docx'], 'rb') as f:
                                    st.session_state.user_regional_data = f.read()
                                st.session_state.user_regional_filename = f"Regional_Concentration_{selected_user_subcategory.replace(' ', '_')}.docx"

                            st.session_state.user_briefs_generated = True

                            if st.session_state.chat_assistant:
                                try:
                                    st.session_state.chat_assistant.load_brief_context(
                                        incumbent_path=results.get('incumbent_docx'),
                                        regional_path=results.get('regional_docx'),
                                        subcategory=selected_user_subcategory
                                    )
                                    st.session_state.brief_context_loaded = True
                                    st.session_state.chat_messages = []
                                except Exception as e:
                                    logger.warning(f"Could not load chat context: {e}")

                            st.success("✅ Briefs generated from your data!")
                        else:
                            st.error(f"Error generating briefs: {result['error']}")

                    except ImportError as e:
                        st.error(f"Missing dependency: {str(e)}")
                    except Exception as e:
                        st.error(f"Error generating briefs: {str(e)}")
                        import traceback
                        st.code(traceback.format_exc())

            # Download buttons for user data
            if st.session_state.user_briefs_generated and st.session_state.user_incumbent_data:
                st.divider()
                st.subheader("📥 Download Generated Briefs")
                col1, col2 = st.columns(2)

                with col1:
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

                # Verification for user data
                render_verification_section(selected_user_subcategory, user_df)

        except pd.errors.EmptyDataError:
            st.error("The uploaded file is empty.")
        except pd.errors.ParserError as e:
            st.error(f"Error parsing CSV file: {str(e)}")
        except UnicodeDecodeError:
            st.error("File encoding error. Please save the CSV as UTF-8.")
        except Exception as e:
            st.error(f"Error reading file: {str(e)}")
            logger.error(f"Error reading uploaded file: {e}")


def render_chat_assistant():
    """Render the chat assistant section"""
    if not st.session_state.brief_context_loaded:
        if st.session_state.briefs_generated or st.session_state.user_briefs_generated:
            st.divider()
            st.info("💬 **Brief Assistant** - Generate briefs to start chatting about your procurement data")
        return

    if not st.session_state.chat_assistant:
        return

    st.divider()

    # Chat header
    col1, col2 = st.columns([3, 1])
    with col1:
        st.subheader("💬 Brief Assistant")
        subcategory = getattr(st.session_state.chat_assistant, 'subcategory', 'your category')
        st.caption(f"Ask questions about your **{subcategory}** brief")
    with col2:
        if st.button("🗑️ Clear Chat", key="clear_chat"):
            st.session_state.chat_messages = []
            if hasattr(st.session_state.chat_assistant, 'clear_history'):
                st.session_state.chat_assistant.clear_history()
            st.rerun()

    # Suggested questions
    if len(st.session_state.chat_messages) == 0:
        st.markdown("**Suggested questions:**")
        try:
            suggestions = st.session_state.chat_assistant.get_suggested_questions()
        except Exception:
            suggestions = [
                "What are the main risks identified?",
                "Who are the top suppliers?",
                "What is the regional concentration?",
                "What actions should we take?"
            ]

        cols = st.columns(2)
        for i, suggestion in enumerate(suggestions[:4]):
            with cols[i % 2]:
                if st.button(suggestion, key=f"suggest_{i}", use_container_width=True):
                    st.session_state.chat_messages.append({
                        "role": "user",
                        "content": suggestion
                    })
                    with st.spinner("Thinking..."):
                        try:
                            response = st.session_state.chat_assistant.chat(suggestion)
                            st.session_state.chat_messages.append({
                                "role": "assistant",
                                "content": response.get('response', 'Sorry, I encountered an error.')
                            })
                        except Exception as e:
                            st.session_state.chat_messages.append({
                                "role": "assistant",
                                "content": f"Sorry, I encountered an error: {str(e)}"
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
            try:
                response = st.session_state.chat_assistant.chat(user_input)
                assistant_message = response.get('response', 'Sorry, I encountered an error.')
            except Exception as e:
                assistant_message = f"Sorry, I encountered an error: {str(e)}"
                logger.error(f"Chat error: {e}")

            st.session_state.chat_messages.append({
                "role": "assistant",
                "content": assistant_message
            })

        st.rerun()


def main():
    """Main application entry point"""
    st.title("📊 Procurement AI")

    # Initialize session state
    initialize_session_state()

    # Render sidebar
    render_sidebar()

    # Two main options as tabs
    tab1, tab2 = st.tabs(["📁 Use System Data", "📤 Upload Your Data"])

    # TAB 1: System Data
    with tab1:
        df = load_system_data()
        if df is None:
            st.error("Could not load system data. Please check that 'data/structured/spend_data.csv' exists.")
        else:
            render_system_data_tab(df)

    # TAB 2: Upload Data
    with tab2:
        render_upload_data_tab()

    # Chat Assistant
    render_chat_assistant()


if __name__ == "__main__":
    main()
