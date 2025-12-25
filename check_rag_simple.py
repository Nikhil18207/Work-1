"""
Check RAG Vector Database - Simple Version (No API Key Required)
"""

import chromadb
from pathlib import Path

def check_vector_database():
    """Check what's in the vector database"""
    
    print("\n" + "="*80)
    print("🔍 CHECKING RAG VECTOR DATABASE")
    print("="*80 + "\n")
    
    try:
        # Connect to ChromaDB
        persist_dir = "./data/vector_db"
        print(f"📂 Connecting to: {persist_dir}")
        
        client = chromadb.PersistentClient(path=persist_dir)
        
        # Get collection
        collection = client.get_collection(name="procurement_docs")
        
        print("✅ Vector database loaded successfully!\n")
        
        # Get count
        count = collection.count()
        print("📊 DATABASE STATISTICS:")
        print("="*80)
        print(f"Total Embeddings: {count}")
        print(f"Collection Name: procurement_docs")
        print(f"Persist Directory: {persist_dir}")
        print("\n")
        
        # Get all documents
        print("📄 FETCHING DOCUMENT INFORMATION...")
        results = collection.get(
            include=['metadatas']
        )
        
        # Extract unique sources
        sources = set()
        categories = {}
        
        for metadata in results['metadatas']:
            if metadata:
                source = metadata.get('file_name', metadata.get('source', 'Unknown'))
                category = metadata.get('category', 'Uncategorized')
                
                sources.add(source)
                categories[category] = categories.get(category, 0) + 1
        
        # Display categories
        print("\n📁 DOCUMENTS BY CATEGORY:")
        print("="*80)
        for category, count in sorted(categories.items(), key=lambda x: x[1], reverse=True):
            print(f"  {category}: {count} chunks")
        
        # Display sources
        print("\n📄 POLICY DOCUMENTS EMBEDDED:")
        print("="*80)
        
        policy_docs = sorted([s for s in sources if 'polic' in s.lower()])
        other_docs = sorted([s for s in sources if 'polic' not in s.lower()])
        
        if policy_docs:
            print("\n✅ POLICY DOCUMENTS:")
            for i, source in enumerate(policy_docs, 1):
                print(f"  {i}. {source}")
        
        if other_docs:
            print("\n📚 OTHER DOCUMENTS:")
            for i, source in enumerate(other_docs, 1):
                print(f"  {i}. {source}")
        
        print(f"\n📊 Total Unique Documents: {len(sources)}")
        
        # Check for new policy documents
        print("\n" + "="*80)
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
        
        print("\n" + "="*80)
        print("✅ VERIFICATION COMPLETE!")
        print("="*80 + "\n")
        
        # Summary
        print("📋 SUMMARY:")
        print("="*80)
        print(f"  Total Embeddings: {count}")
        print(f"  Unique Documents: {len(sources)}")
        print(f"  Policy Documents: {len(policy_docs)}")
        print(f"  Other Documents: {len(other_docs)}")
        print(f"  Categories: {len(categories)}")
        print("\n" + "="*80 + "\n")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("\nTroubleshooting:")
        print("  1. Make sure vector database exists: data/vector_db/")
        print("  2. Run setup: python scripts/setup_rag.py")
        return False


if __name__ == "__main__":
    check_vector_database()
