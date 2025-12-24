"""
RAG Pipeline Setup Script - Google Gemini Version
Complete setup and initialization of the RAG system using Google Gemini
"""

import os
import sys
from pathlib import Path
import warnings
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

print(f"DEBUG: Current sys.path: {sys.path}")
print(f"DEBUG: Python executable: {sys.executable}")

# Suppress warnings
warnings.filterwarnings('ignore', category=DeprecationWarning)
warnings.filterwarnings('ignore', category=FutureWarning)

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.engines.document_processor import DocumentProcessor
from backend.engines.vector_store_manager import VectorStoreManager
from backend.engines.rag_engine import RAGEngine

def setup_rag_gemini(reset: bool = False):
    print("\n" + "="*70)
    print("🚀 RAG PIPELINE SETUP (GOOGLE GEMINI)")
    print("="*70)
    
    # Step 1: Process Documents
    print("\n📚 STEP 1: Processing Documents")
    print("-"*70)
    
    processor = DocumentProcessor(
        chunk_size=1000,
        chunk_overlap=200,
        data_directory="./data"
    )
    
    documents = processor.process_unstructured_corpus()
    policy_docs = processor.process_structured_policies()
    documents.extend(policy_docs)
    
    if not documents:
        print("\n❌ No documents found!")
        return False
        
    print(f"\n📊 Total chunks to embed: {len(documents)}")
    
    # Step 2: Create Vector Store
    print("\n" + "-"*70)
    print("🔮 STEP 2: Creating Vector Store (Gemini Embeddings)")
    print("-"*70)
    
    try:
        # Use a separate directory for gemini embeddings to avoid conflicts with OpenAI ones
        persist_dir = "./data/vector_db_gemini"
        
        if reset and os.path.exists(persist_dir):
            import shutil
            shutil.rmtree(persist_dir)
            
        vector_store = VectorStoreManager(
            persist_directory=persist_dir,
            collection_name="procurement_docs_gemini",
            provider="google"
        )
        
        vector_store.create_collection(documents, reset=reset)
        print("\n✅ Vector store created successfully with Gemini!")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return False
        
    # Step 3: Test RAG Engine
    print("\n" + "-"*70)
    print("🧪 STEP 3: Testing RAG Engine (Gemini Pro)")
    print("-"*70)
    
    try:
        rag = RAGEngine(
            vector_store_manager=vector_store,
            provider="google",
            model="gemini-pro"
        )
        
        test_question = "What are the key supplier selection criteria?"
        print(f"\n🔍 Test Query: {test_question}")
        
        response = rag.query(question=test_question)
        print(f"\n💬 Answer:\n{response['answer']}")
        
    except Exception as e:
        print(f"\n⚠️ Test failed: {e}")
        
    print("\n" + "="*70)
    print("✅ GEMINI RAG SETUP COMPLETE!")
    print("="*70)
    return True

if __name__ == "__main__":
    setup_rag_gemini(reset=True)
