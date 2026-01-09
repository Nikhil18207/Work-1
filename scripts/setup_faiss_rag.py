"""
Setup FAISS RAG Vector Store
Creates FAISS index from knowledge base documents
"""

import sys
from pathlib import Path
import pandas as pd

# Add project root to path
root_path = Path(__file__).parent.parent
sys.path.insert(0, str(root_path))

from backend.engines.faiss_vector_store import FAISSVectorStore


def load_documents_from_directory(directory: Path) -> list:
    """Load all text/markdown documents from directory"""
    documents = []

    if not directory.exists():
        return documents

    # Load markdown files
    for md_file in directory.glob("**/*.md"):
        try:
            content = md_file.read_text(encoding='utf-8')
            documents.append({
                'content': content,
                'metadata': {
                    'source': md_file.name,
                    'file_name': md_file.name,
                    'category': 'knowledge_base',
                    'file_type': 'markdown'
                }
            })
        except Exception as e:
            print(f"  Warning: Could not read {md_file.name}: {e}")

    # Load text files
    for txt_file in directory.glob("**/*.txt"):
        try:
            content = txt_file.read_text(encoding='utf-8')
            documents.append({
                'content': content,
                'metadata': {
                    'source': txt_file.name,
                    'file_name': txt_file.name,
                    'category': 'knowledge_base',
                    'file_type': 'text'
                }
            })
        except Exception as e:
            print(f"  Warning: Could not read {txt_file.name}: {e}")

    return documents


def load_structured_data_descriptions(directory: Path) -> list:
    """Create searchable descriptions from CSV files"""
    documents = []

    if not directory.exists():
        return documents

    for csv_file in directory.glob("*.csv"):
        try:
            df = pd.read_csv(csv_file)

            # Create a description of the data
            description = f"""
Data Source: {csv_file.name}
Columns: {', '.join(df.columns)}
Total Records: {len(df)}

Sample Data (first 5 rows):
{df.head().to_string()}
"""
            documents.append({
                'content': description,
                'metadata': {
                    'source': csv_file.name,
                    'file_name': csv_file.name,
                    'category': 'structured_data',
                    'file_type': 'csv'
                }
            })

            # For spend_data, also create category-specific documents
            if csv_file.name == 'spend_data.csv' and 'Category' in df.columns:
                for category in df['Category'].unique()[:10]:
                    cat_df = df[df['Category'] == category]
                    cat_desc = f"""
Category: {category}
Total Spend: ${cat_df['Spend_USD'].sum():,.0f}
Number of Suppliers: {cat_df['Supplier_ID'].nunique()}
Countries: {', '.join(cat_df['Supplier_Country'].unique()[:5])}
Regions: {', '.join(cat_df['Supplier_Region'].unique()[:5])}
"""
                    documents.append({
                        'content': cat_desc,
                        'metadata': {
                            'source': csv_file.name,
                            'file_name': f"{csv_file.name}:{category}",
                            'category': category,
                            'file_type': 'csv_analysis'
                        }
                    })

        except Exception as e:
            print(f"  Warning: Could not process {csv_file.name}: {e}")

    return documents


def main():
    print("=" * 60)
    print(" SETTING UP FAISS RAG VECTOR STORE")
    print("=" * 60)

    documents = []

    # Load UNSTRUCTURED documents (policies, best practices, risk assessments)
    print("\n[1/5] Loading UNSTRUCTURED documents (policies, best practices)...")
    unstructured_path = root_path / "data" / "unstructured"
    unstructured_docs = load_documents_from_directory(unstructured_path)
    documents.extend(unstructured_docs)
    print(f"  ✅ Loaded {len(unstructured_docs)} unstructured documents")

    # Load STRUCTURED data descriptions (CSVs)
    print("\n[2/5] Loading STRUCTURED data (CSV files)...")
    structured_path = root_path / "data" / "structured"
    struct_docs = load_structured_data_descriptions(structured_path)
    documents.extend(struct_docs)
    print(f"  ✅ Created {len(struct_docs)} structured data descriptions")

    # Load CALCULATED data
    print("\n[3/5] Loading CALCULATED data...")
    calculated_path = root_path / "data" / "calculated"
    calculated_docs = load_structured_data_descriptions(calculated_path)
    documents.extend(calculated_docs)
    print(f"  ✅ Created {len(calculated_docs)} calculated data descriptions")

    # Add procurement domain knowledge
    print("\n[4/5] Adding procurement domain knowledge...")
    domain_docs = [
        {
            'content': """
Supplier Concentration Risk Management:
- High supplier concentration (>50% with single supplier) creates significant supply chain risk
- Best practice is to maintain at least 3-5 qualified suppliers for critical categories
- Geographic diversification across Americas, Europe, APAC, Middle East, and Africa reduces exposure
- Dual sourcing strategies balance cost efficiency with risk mitigation
- Consider suppliers from emerging markets like Africa and Middle East for diversification
""",
            'metadata': {'source': 'domain_knowledge', 'file_name': 'supplier_risk.txt', 'category': 'risk_management'}
        },
        {
            'content': """
Regional Procurement Strategy - Global Overview:
- Americas: USA, Canada, Mexico, Brazil - strong infrastructure, established supply chains
- Europe: Germany, UK, France, Netherlands - quality focus, regulatory compliance
- APAC: China, India, Vietnam, Thailand - manufacturing scale, cost efficiency
- Middle East: UAE, Saudi Arabia, Turkey - logistics hub, growing industrial base
- Africa: South Africa, Egypt, Morocco, Kenya - emerging markets, competitive labor costs
- Consider total cost of ownership including logistics, quality, and lead times
- Nearshoring provides faster response and lower logistics costs
""",
            'metadata': {'source': 'domain_knowledge', 'file_name': 'regional_strategy.txt', 'category': 'sourcing'}
        },
        {
            'content': """
Africa Procurement Opportunities:
- South Africa: African industrial leader, established infrastructure, regional hub
- Egypt: Strategic Suez Canal location, growing manufacturing, MENA gateway
- Morocco: EU proximity, Tanger Med port, competitive labor, growing industries
- Kenya: East Africa hub, digital innovation, logistics gateway
- Nigeria: Large market, growing economy, oil & gas expertise
- Tunisia: Skilled workforce, EU proximity, manufacturing capabilities
- Ghana: Stable economy, growing tech sector, West Africa hub
Benefits: Cost efficiency, market access, diversification, emerging talent pools
""",
            'metadata': {'source': 'domain_knowledge', 'file_name': 'africa_sourcing.txt', 'category': 'regional'}
        },
        {
            'content': """
Middle East Procurement Opportunities:
- UAE (Dubai, Abu Dhabi): World-class logistics hub, business-friendly, regional HQ location
- Saudi Arabia: Vision 2030 investments, industrial diversification, large market
- Turkey: Europe-Asia bridge, diverse manufacturing, established industries
- Qatar: Premium infrastructure, LNG expertise, growing diversification
- Jordan: Pharma hub, skilled workforce, trade agreements
- Israel: Technology innovation, R&D capabilities, startup ecosystem
Benefits: Strategic location, infrastructure investment, growing industrial base
""",
            'metadata': {'source': 'domain_knowledge', 'file_name': 'middle_east_sourcing.txt', 'category': 'regional'}
        },
        {
            'content': """
Procurement ROI Calculations:
- Cost savings typically range 5-20% through strategic sourcing
- Implementation costs include qualification, transition, and ongoing management
- Payback period for diversification initiatives typically 6-18 months
- 3-year net benefit = (Annual Savings x 3) - Implementation Cost
- Africa/Middle East expansion can yield 10-25% cost savings in select categories
""",
            'metadata': {'source': 'domain_knowledge', 'file_name': 'roi_calculations.txt', 'category': 'financial'}
        },
        {
            'content': """
Supply Chain Risk Assessment:
- Single source dependency: CRITICAL risk - immediate action required
- Geographic concentration: HIGH risk if >70% from one region
- Quality risk: Monitor supplier ratings below 4.0
- Financial risk: Track supplier financial health indicators
- Compliance risk: Ensure supplier meets regulatory requirements
- Geopolitical risk: Diversify across stable regions (Americas, Europe, APAC, GCC)
- Emerging market risk: Balance growth opportunities with due diligence
""",
            'metadata': {'source': 'domain_knowledge', 'file_name': 'risk_assessment.txt', 'category': 'risk_management'}
        },
        {
            'content': """
Global Supplier Database Coverage:
- 893 qualified suppliers across 5 geographic regions
- Americas: 332 suppliers (USA, Canada, Mexico, Brazil, Argentina, Chile, Colombia)
- Europe: 225 suppliers (Germany, UK, France, Netherlands, Switzerland, Italy, Spain)
- APAC: 185 suppliers (China, India, Japan, South Korea, Singapore, Australia, Thailand)
- Middle East: 91 suppliers (UAE, Saudi Arabia, Turkey, Qatar, Israel, Jordan)
- Africa: 60 suppliers (South Africa, Egypt, Morocco, Kenya, Nigeria, Ghana)
- 10 industry sectors, 41 categories, 140 subcategories covered
""",
            'metadata': {'source': 'domain_knowledge', 'file_name': 'supplier_coverage.txt', 'category': 'database'}
        }
    ]
    documents.extend(domain_docs)
    print(f"  ✅ Added {len(domain_docs)} domain knowledge documents")

    print(f"\n  📊 TOTAL DOCUMENTS: {len(documents)}")

    if not documents:
        print("\n[ERROR] No documents found to index!")
        return

    # Create FAISS index
    print("\n[5/5] Creating FAISS index...")
    faiss_store = FAISSVectorStore(
        persist_directory="./data/faiss_db",
        embedding_model="text-embedding-3-small"
    )

    faiss_store.create_index(documents, reset=True)

    # Test search
    print("\n Testing search...")
    test_queries = [
        "supplier concentration risk",
        "cost savings procurement",
        "regional sourcing strategy"
    ]

    for query in test_queries:
        results = faiss_store.search(query, k=2)
        print(f"\n  Query: '{query}'")
        for i, r in enumerate(results, 1):
            print(f"    {i}. Score: {r['score']:.4f} - {r['metadata'].get('source', 'unknown')}")

    print("\n" + "=" * 60)
    print(" FAISS RAG SETUP COMPLETE!")
    print(f" Index saved to: data/faiss_db")
    print("=" * 60)


if __name__ == "__main__":
    main()
