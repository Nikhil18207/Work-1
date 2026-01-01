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

    # Load knowledge base documents
    print("\n[1/4] Loading knowledge base documents...")
    kb_path = root_path / "data" / "knowledge_base"
    kb_docs = load_documents_from_directory(kb_path)
    documents.extend(kb_docs)
    print(f"  Loaded {len(kb_docs)} knowledge base documents")

    # Load structured data descriptions
    print("\n[2/4] Creating structured data descriptions...")
    structured_path = root_path / "data" / "structured"
    struct_docs = load_structured_data_descriptions(structured_path)
    documents.extend(struct_docs)
    print(f"  Created {len(struct_docs)} data descriptions")

    # Add procurement domain knowledge
    print("\n[3/4] Adding procurement domain knowledge...")
    domain_docs = [
        {
            'content': """
Supplier Concentration Risk Management:
- High supplier concentration (>50% with single supplier) creates significant supply chain risk
- Best practice is to maintain at least 3-5 qualified suppliers for critical categories
- Geographic diversification reduces exposure to regional disruptions
- Dual sourcing strategies balance cost efficiency with risk mitigation
""",
            'metadata': {'source': 'domain_knowledge', 'file_name': 'supplier_risk.txt', 'category': 'risk_management'}
        },
        {
            'content': """
Regional Procurement Strategy:
- Low-cost regions include India, China, Vietnam, Mexico for manufacturing
- Consider total cost of ownership including logistics, quality, and lead times
- Nearshoring provides faster response and lower logistics costs
- Currency fluctuation risk should be factored into regional decisions
""",
            'metadata': {'source': 'domain_knowledge', 'file_name': 'regional_strategy.txt', 'category': 'sourcing'}
        },
        {
            'content': """
Procurement ROI Calculations:
- Cost savings typically range 5-20% through strategic sourcing
- Implementation costs include qualification, transition, and ongoing management
- Payback period for diversification initiatives typically 6-18 months
- 3-year net benefit = (Annual Savings x 3) - Implementation Cost
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
""",
            'metadata': {'source': 'domain_knowledge', 'file_name': 'risk_assessment.txt', 'category': 'risk_management'}
        }
    ]
    documents.extend(domain_docs)
    print(f"  Added {len(domain_docs)} domain knowledge documents")

    print(f"\n  TOTAL DOCUMENTS: {len(documents)}")

    if not documents:
        print("\n[ERROR] No documents found to index!")
        return

    # Create FAISS index
    print("\n[4/4] Creating FAISS index...")
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
