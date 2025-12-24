"""
RAG Pipeline Setup Script
Complete setup and initialization of the RAG system
"""

import os
import sys
from pathlib import Path
import warnings
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Suppress numpy deprecation warnings
warnings.filterwarnings('ignore', category=DeprecationWarning)
warnings.filterwarnings('ignore', category=FutureWarning)

# Add parent directory to path so we can import backend
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.engines.document_processor import DocumentProcessor
from backend.engines.vector_store_manager import VectorStoreManager
from backend.engines.rag_engine import RAGEngine


def setup_rag_pipeline(reset: bool = False):
    """
    Complete RAG pipeline setup
    
    Args:
        reset: Reset existing vector store
    """
    print("\n" + "="*70)
    print("🚀 RAG PIPELINE SETUP")
    print("="*70)
    
    # Step 1: Process Documents
    print("\n📚 STEP 1: Processing Documents")
    print("-"*70)
    
    processor = DocumentProcessor(
        chunk_size=1000,
        chunk_overlap=200,
        data_directory="./data"
    )
    
    # Process unstructured corpus
    documents = processor.process_unstructured_corpus()
    
    # Process structured data (CSV files)
    structured_docs = processor.process_structured_policies()
    documents.extend(structured_docs)
    
    # Process calculated/derived data
    calculated_docs = processor.process_calculated_data()
    documents.extend(calculated_docs)
    
    if not documents:
        print("\n❌ No documents found to process!")
        print("   Make sure you have documents in data/unstructured/")
        return False
    
    # Show statistics
    stats = processor.get_document_stats(documents)
    print("\n📊 Document Statistics:")
    print(f"   Total Documents: {stats['total_documents']}")
    print(f"   Total Characters: {stats['total_characters']:,}")
    print(f"   Average Chunk Size: {stats['average_chunk_size']}")
    print(f"   Categories: {stats['categories']}")
    
    # Step 2: Create Vector Store
    print("\n" + "-"*70)
    print("🔮 STEP 2: Creating Vector Store")
    print("-"*70)
    
    try:
        # Delete old vector_db if exists to avoid conflicts
        import shutil
        old_path = Path("./data/vector_db")
        if old_path.exists():
            print("🗑️  Removing old vector database...")
            shutil.rmtree(old_path, ignore_errors=True)
        
        vector_store = VectorStoreManager(
            persist_directory="./data/vector_db",
            collection_name="procurement_docs",
            embedding_model="text-embedding-3-small"
        )
        
        # Create collection
        vector_store.create_collection(documents, reset=reset)
        
        # Show statistics
        vs_stats = vector_store.get_statistics()
        print("\n📊 Vector Store Statistics:")
        for key, value in vs_stats.items():
            print(f"   {key}: {value}")
        
    except Exception as e:
        print(f"\n❌ Error creating vector store: {e}")
        return False
    
    # Step 3: Test RAG Engine
    print("\n" + "-"*70)
    print("🧪 STEP 3: Testing RAG Engine")
    print("-"*70)
    
    try:
        rag = RAGEngine(
            vector_store_manager=vector_store,
            model="gpt-4"
        )
        
        # Test query
        test_question = "What are the key supplier selection criteria?"
        print(f"\n🔍 Test Query: {test_question}")
        
        response = rag.query(
            question=test_question,
            k=3,
            verbose=False
        )
        
        print(f"\n💬 Answer:")
        print(f"   {response['answer'][:200]}...")
        
        if response.get('sources'):
            print(f"\n📚 Sources: {len(response['sources'])} documents")
        
    except Exception as e:
        print(f"\n⚠️  RAG engine test failed: {e}")
        print("   (This is OK if you don't have OpenAI API key set)")
    
    # Success!
    print("\n" + "="*70)
    print("✅ RAG PIPELINE SETUP COMPLETE!")
    print("="*70)
    print("\n📝 Next Steps:")
    print("   1. Run demos/demo_rag.py to test the system")
    print("   2. Integrate RAG into backend/llm_recommendation_system.py")
    print("   3. Add RAG endpoints to backend/api/routes.py")
    print("\n" + "="*70 + "\n")
    
    return True


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Setup RAG Pipeline")
    parser.add_argument(
        "--reset",
        action="store_true",
        help="Reset existing vector store"
    )
    
    args = parser.parse_args()
    
    # Run setup
    success = setup_rag_pipeline(reset=args.reset)
    
    if success:
        print("✅ Setup completed successfully!")
        sys.exit(0)
    else:
        print("❌ Setup failed!")
        sys.exit(1)
