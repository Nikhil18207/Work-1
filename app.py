"""
Beroe Procurement AI - Streamlit UI
Simple, clean interface for procurement analysis and brief generation
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

    # Two main options as tabs
    tab1, tab2 = st.tabs(["📁 Use System Data", "📤 Upload Your Data"])

    # ========== TAB 1: System Data ==========
    with tab1:
        st.subheader("Generate Briefs from System Data")
        st.caption("Use our pre-loaded multi-industry procurement data (312 suppliers, 10 sectors)")

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
                with st.spinner(f"Generating briefs for {selected_subcategory}..."):
                    try:
                        from backend.engines.leadership_brief_generator import LeadershipBriefGenerator
                        from backend.engines.docx_exporter import DOCXExporter

                        generator = LeadershipBriefGenerator()
                        exporter = DOCXExporter()

                        # Get client that has data for this subcategory
                        client_for_subcat = final_df['Client_ID'].iloc[0] if len(final_df) > 0 else "C001"
                        briefs = generator.generate_both_briefs(client_for_subcat, selected_subcategory)
                        results = exporter.export_both_briefs(briefs)

                        st.success("✅ Briefs generated successfully!")

                        # Download buttons
                        col1, col2 = st.columns(2)

                        with col1:
                            if 'incumbent_docx' in results:
                                with open(results['incumbent_docx'], 'rb') as f:
                                    file_data = f.read()
                                st.download_button(
                                    label="📥 Download Incumbent Concentration Brief",
                                    data=file_data,
                                    file_name=f"Incumbent_Concentration_{selected_subcategory.replace(' ', '_')}.docx",
                                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                                    key="sys_inc_download"
                                )
                                st.caption(f"Saved to: {results['incumbent_docx']}")

                        with col2:
                            if 'regional_docx' in results:
                                with open(results['regional_docx'], 'rb') as f:
                                    file_data = f.read()
                                st.download_button(
                                    label="📥 Download Regional Concentration Brief",
                                    data=file_data,
                                    file_name=f"Regional_Concentration_{selected_subcategory.replace(' ', '_')}.docx",
                                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                                    key="sys_reg_download"
                                )
                                st.caption(f"Saved to: {results['regional_docx']}")

                    except Exception as e:
                        st.error(f"Error generating briefs: {str(e)}")
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
            st.code("""
Required columns:
- Client_ID
- Sector
- Category
- SubCategory
- Supplier_ID
- Supplier_Name
- Supplier_Country
- Supplier_Region
- Transaction_Date
- Spend_USD
- Quality_Rating (optional)
- Delivery_Rating (optional)
            """)

            # Download sample template
            sample_data = pd.DataFrame({
                'Client_ID': ['C001', 'C001', 'C001'],
                'Sector': ['Food & Beverages', 'Food & Beverages', 'Information Technology'],
                'Category': ['Edible Oils', 'Edible Oils', 'Cloud Services'],
                'SubCategory': ['Rice Bran Oil', 'Palm Oil', 'IaaS'],
                'Supplier_ID': ['S001', 'S002', 'S201'],
                'Supplier_Name': ['Supplier A', 'Supplier B', 'Supplier C'],
                'Supplier_Country': ['Malaysia', 'Indonesia', 'USA'],
                'Supplier_Region': ['APAC', 'APAC', 'Americas'],
                'Transaction_Date': ['2025-01-15', '2025-02-20', '2025-03-10'],
                'Spend_USD': [500000, 450000, 850000],
                'Quality_Rating': [4.5, 4.2, 4.8],
                'Delivery_Rating': [4.3, 4.0, 4.6]
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
                    with st.spinner("Generating briefs from your data..."):
                        try:
                            from backend.engines.leadership_brief_generator import LeadershipBriefGenerator
                            from backend.engines.docx_exporter import DOCXExporter
                            from backend.engines.data_loader import DataLoader

                            # Create custom data loader with uploaded data
                            custom_loader = DataLoader()
                            custom_loader.set_spend_data(user_df)

                            generator = LeadershipBriefGenerator(data_loader=custom_loader)
                            exporter = DOCXExporter()

                            briefs = generator.generate_both_briefs(selected_user_client, selected_user_subcategory)
                            results = exporter.export_both_briefs(briefs)

                            st.success("✅ Briefs generated from your data!")

                            col1, col2 = st.columns(2)

                            with col1:
                                if 'incumbent_docx' in results:
                                    with open(results['incumbent_docx'], 'rb') as f:
                                        file_data = f.read()
                                    st.download_button(
                                        label="📥 Download Incumbent Concentration Brief",
                                        data=file_data,
                                        file_name=f"Incumbent_Concentration_{selected_user_subcategory.replace(' ', '_')}.docx",
                                        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                                        key="user_inc_download"
                                    )
                                    st.caption(f"Saved to: {results['incumbent_docx']}")

                            with col2:
                                if 'regional_docx' in results:
                                    with open(results['regional_docx'], 'rb') as f:
                                        file_data = f.read()
                                    st.download_button(
                                        label="📥 Download Regional Concentration Brief",
                                        data=file_data,
                                        file_name=f"Regional_Concentration_{selected_user_subcategory.replace(' ', '_')}.docx",
                                        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                                        key="user_reg_download"
                                    )
                                    st.caption(f"Saved to: {results['regional_docx']}")

                        except Exception as e:
                            st.error(f"Error generating briefs: {str(e)}")
                            import traceback
                            st.code(traceback.format_exc())

            except Exception as e:
                st.error(f"Error reading file: {str(e)}")


if __name__ == "__main__":
    main()
