"""
Check RAG Vector Database - Verify Policy Documents are Embedded
"""

import sys
from pathlib import Path

# Add workspace root to path
root_path = Path(__file__).parent
if str(root_path) not in sys.path:
    sys.path.insert(0, str(root_path))

from backend.engines.vector_store_manager import VectorStoreManager

def check_vector_database():
    """Check what's in the vector database"""
    
    print("\n" + "="*80)
    print("🔍 CHECKING RAG VECTOR DATABASE")
    print("="*80 + "\n")
    
    try:
        # Initialize vector store
        vector_store = VectorStoreManager(
            persist_directory="./data/vector_db",
            collection_name="procurement_docs",
            provider="openai"
        )
        
        # Load collection
        print("📂 Loading vector database...")
        if vector_store.load_collection():
            print("✅ Vector database loaded successfully!\n")
            
            # Get statistics
            stats = vector_store.get_collection_stats()
            
            print("📊 DATABASE STATISTICS:")
            print("="*80)
            print(f"Total Documents: {stats['total_documents']}")
            print(f"Total Embeddings: {stats['total_embeddings']}")
            print(f"Collection Name: {stats['collection_name']}")
            print(f"Persist Directory: {stats['persist_directory']}")
            print("\n")
            
            # Get documents by category
            print("📁 DOCUMENTS BY CATEGORY:")
            print("="*80)
            
            categories = stats.get('categories', {})
            if categories:
                for category, count in sorted(categories.items(), key=lambda x: x[1], reverse=True):
                    print(f"  {category}: {count} chunks")
            else:
                print("  No category information available")
            
            print("\n")
            
            # Get unique sources
            print("📄 POLICY DOCUMENTS EMBEDDED:")
            print("="*80)
            
            sources = stats.get('sources', [])
            if sources:
                policy_docs = [s for s in sources if 'polic' in s.lower()]
                other_docs = [s for s in sources if 'polic' not in s.lower()]
                
                if policy_docs:
                    print("\n✅ POLICY DOCUMENTS:")
                    for i, source in enumerate(sorted(policy_docs), 1):
                        print(f"  {i}. {source}")
                
                if other_docs:
                    print("\n📚 OTHER DOCUMENTS:")
                    for i, source in enumerate(sorted(other_docs), 1):
                        print(f"  {i}. {source}")
                
                print(f"\n📊 Total Unique Documents: {len(sources)}")
            else:
                print("  No source information available")
            
            print("\n" + "="*80)
            print("✅ VERIFICATION COMPLETE!")
            print("="*80 + "\n")
            
            # Check for new policy documents
            print("🔍 CHECKING FOR NEW POLICY DOCUMENTS:")
            print("="*80)
            
            policy_dir = Path("data/unstructured/policies")
            if policy_dir.exists():
                policy_files = list(policy_dir.glob("*.md"))
                print(f"\nFound {len(policy_files)} policy files in directory:")
                for i, file in enumerate(sorted(policy_files), 1):
                    file_name = file.name
                    embedded = any(file_name in s for s in sources)
                    status = "✅ Embedded" if embedded else "❌ Not embedded"
                    print(f"  {i}. {file_name} - {status}")
            
            print("\n" + "="*80 + "\n")
            
            return True
        else:
            print("❌ Failed to load vector database")
            print("   Run: python scripts/setup_rag.py")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        print("\nTroubleshooting:")
        print("  1. Make sure vector database exists: data/vector_db/")
        print("  2. Run setup: python scripts/setup_rag.py")
        print("  3. Check environment variables")
        return False


if __name__ == "__main__":
    check_vector_database()
