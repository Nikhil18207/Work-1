"""
Vector Store Manager for RAG Pipeline
Manages ChromaDB vector database for semantic search
"""

import os
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
import json
from datetime import datetime

# Vector database
try:
    import chromadb
    from chromadb.config import Settings
    from chromadb.utils import embedding_functions
    CHROMADB_AVAILABLE = True
except ImportError:
    CHROMADB_AVAILABLE = False
    print("Warning: ChromaDB not installed. Install with: pip install chromadb")
    chromadb = None
    Settings = None

# LangChain integration
from langchain_core.documents import Document
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings
LANGCHAIN_AVAILABLE = True

# Google imports are optional
try:
    from langchain_google_genai import GoogleGenerativeAIEmbeddings
except ImportError:
    GoogleGenerativeAIEmbeddings = None


class VectorStoreManager:
    """
    Manages vector database for RAG pipeline
    - Creates and manages ChromaDB collections
    - Generates embeddings using OpenAI
    - Performs semantic search
    - Handles persistence and updates
    """
    
    def __init__(
        self,
        persist_directory: str = "./data/vector_db",
        collection_name: str = "procurement_docs",
        embedding_model: Optional[str] = None,
        provider: str = "openai",
        api_key: Optional[str] = None
    ):
        """
        Initialize vector store manager
        
        Args:
            persist_directory: Directory to persist ChromaDB
            collection_name: Name of the collection
            embedding_model: Model name for embeddings
            provider: 'openai' or 'google'
            api_key: API key for the chosen provider
        """
        if not CHROMADB_AVAILABLE:
            raise ImportError(
                "ChromaDB is required for RAG. Install with:\n"
                "pip install chromadb"
            )
        
        if not LANGCHAIN_AVAILABLE:
            raise ImportError(
                "LangChain is required for RAG. Install with:\n"
                "pip install langchain langchain-community langchain-openai"
            )
        
        self.provider = provider.lower()
        self.persist_directory = Path(persist_directory)
        self.collection_name = collection_name
        
        # Default models
        if not embedding_model:
            if self.provider == "google":
                self.embedding_model = "models/embedding-001"
            else:
                self.embedding_model = "text-embedding-3-small"
        else:
            self.embedding_model = embedding_model
        
        # Create persist directory
        self.persist_directory.mkdir(parents=True, exist_ok=True)
        
        # Get API key
        if self.provider == "google":
            self.api_key = api_key or os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
            if not self.api_key:
                raise ValueError("Google API key required. Set GOOGLE_API_KEY environment variable.")
            
            if not GoogleGenerativeAIEmbeddings:
                raise ImportError("langchain-google-genai not installed. Install with: pip install langchain-google-genai")
            
            # Initialize Google embeddings
            self.embeddings = GoogleGenerativeAIEmbeddings(
                model=self.embedding_model,
                google_api_key=self.api_key
            )
        else:
            self.api_key = api_key or os.getenv("OPENAI_API_KEY")
            if not self.api_key:
                raise ValueError("OpenAI API key required. Set OPENAI_API_KEY environment variable.")
            
            # Initialize OpenAI embeddings
            self.embeddings = OpenAIEmbeddings(
                model=self.embedding_model,
                openai_api_key=self.api_key
            )
        
        # Initialize ChromaDB client
        self.client = chromadb.PersistentClient(
            path=str(self.persist_directory),
            settings=Settings(
                anonymized_telemetry=False,
                allow_reset=True
            )
        )
        
        # Initialize vector store
        self.vector_store = None
        self.collection = None
        
        print(f" Vector Store initialized")
        print(f"  Persist Directory: {self.persist_directory}")
        print(f"  Collection: {collection_name}")
        print(f"  Embedding Model: {embedding_model}")
    
    def create_collection(self, documents: List[Document], reset: bool = False) -> None:
        """
        Create vector store collection from documents
        
        Args:
            documents: List of documents to embed
            reset: Reset existing collection
        """
        if not documents:
            print("Warning: No documents provided")
            return
        
        print("\n" + "="*60)
        print(" CREATING VECTOR STORE")
        print("="*60)
        print(f"Documents to embed: {len(documents)}")
        print(f"Embedding model: {self.embedding_model}")
        
        # Reset if requested
        if reset and self.collection_exists():
            print("\n  Resetting existing collection...")
            self.reset_collection()
        
        # Create vector store
        print("\n Generating embeddings...")
        print("   (This may take a few minutes for large corpora)")
        
        try:
            # Use the existing client directly to avoid "different settings" error
            self.vector_store = Chroma.from_documents(
                documents=documents,
                embedding=self.embeddings,
                collection_name=self.collection_name,
                client=self.client  # Pass client directly
            )
            
            # Get collection reference
            self.collection = self.client.get_collection(self.collection_name)
            
            # Save metadata
            self._save_metadata(documents)
            
            print("\n Vector store created successfully!")
            print(f"   Total embeddings: {self.collection.count()}")
            print(f"   Persisted to: {self.persist_directory}")
            print("="*60 + "\n")
            
        except Exception as e:
            print(f"\n Error creating vector store: {e}")
            raise
    
    def load_collection(self) -> bool:
        """
        Load existing vector store collection
        
        Returns:
            True if loaded successfully
        """
        try:
            # Check if collection exists
            if not self.collection_exists():
                print(f"Collection '{self.collection_name}' does not exist")
                return False
            
            # Load vector store
            self.vector_store = Chroma(
                collection_name=self.collection_name,
                embedding_function=self.embeddings,
                client=self.client  # Use client instead of persist_directory
            )
            
            # Get collection reference
            self.collection = self.client.get_collection(self.collection_name)
            
            print(f" Loaded collection: {self.collection_name}")
            print(f"  Total embeddings: {self.collection.count()}")
            
            return True
            
        except Exception as e:
            print(f"Error loading collection: {e}")
            return False
    
    def collection_exists(self) -> bool:
        """Check if collection exists"""
        try:
            collections = self.client.list_collections()
            return any(c.name == self.collection_name for c in collections)
        except:
            return False
    
    def reset_collection(self) -> None:
        """Delete existing collection"""
        try:
            self.client.delete_collection(self.collection_name)
            print(f" Deleted collection: {self.collection_name}")
        except Exception as e:
            print(f"Error deleting collection: {e}")
    
    def add_documents(self, documents: List[Document]) -> None:
        """
        Add new documents to existing collection
        
        Args:
            documents: Documents to add
        """
        if not self.vector_store:
            print("Error: Vector store not initialized. Create or load collection first.")
            return
        
        print(f"\n Adding {len(documents)} documents to collection...")
        
        try:
            self.vector_store.add_documents(documents)
            print(f" Added successfully. Total: {self.collection.count()}")
        except Exception as e:
            print(f"Error adding documents: {e}")
    
    def similarity_search(
        self,
        query: str,
        k: int = 5,
        filter_metadata: Optional[Dict[str, Any]] = None,
        score_threshold: Optional[float] = None
    ) -> List[Tuple[Document, float]]:
        """
        Perform similarity search
        
        Args:
            query: Search query
            k: Number of results
            filter_metadata: Filter by metadata (e.g., {'category': 'policies'})
            score_threshold: Minimum similarity score (0-1)
            
        Returns:
            List of (document, score) tuples
        """
        if not self.vector_store:
            print("Error: Vector store not initialized")
            return []
        
        try:
            # Search with scores
            results = self.vector_store.similarity_search_with_score(
                query=query,
                k=k,
                filter=filter_metadata
            )
            
            # Apply score threshold if specified
            if score_threshold is not None:
                results = [(doc, score) for doc, score in results if score >= score_threshold]
            
            return results
            
        except Exception as e:
            print(f"Error during search: {e}")
            return []
    
    def semantic_search(
        self,
        query: str,
        k: int = 5,
        category: Optional[str] = None,
        verbose: bool = False
    ) -> List[Dict[str, Any]]:
        """
        Perform semantic search and return formatted results
        
        Args:
            query: Search query
            k: Number of results
            category: Filter by category
            verbose: Print detailed results
            
        Returns:
            List of result dictionaries
        """
        # Build filter
        filter_metadata = {'category': category} if category else None
        
        # Search
        results = self.similarity_search(
            query=query,
            k=k,
            filter_metadata=filter_metadata
        )
        
        # Format results
        formatted_results = []
        
        for i, (doc, score) in enumerate(results, 1):
            result = {
                'rank': i,
                'content': doc.page_content,
                'score': float(score),
                'metadata': doc.metadata,
                'source': doc.metadata.get('source', 'unknown'),
                'category': doc.metadata.get('category', 'unknown')
            }
            formatted_results.append(result)
            
            if verbose:
                print(f"\n{'='*60}")
                print(f"Result #{i} (Score: {score:.4f})")
                print(f"{'='*60}")
                print(f"Source: {result['source']}")
                print(f"Category: {result['category']}")
                print(f"\nContent:\n{doc.page_content[:300]}...")
        
        return formatted_results
    
    def get_context_for_query(
        self,
        query: str,
        k: int = 5,
        category: Optional[str] = None
    ) -> str:
        """
        Get formatted context for LLM prompt
        
        Args:
            query: Search query
            k: Number of results
            category: Filter by category
            
        Returns:
            Formatted context string
        """
        results = self.semantic_search(query, k=k, category=category)
        
        if not results:
            return "No relevant context found."
        
        # Format context
        context_parts = []
        
        for result in results:
            context_parts.append(
                f"[Source: {result['metadata'].get('file_name', 'unknown')}]\n"
                f"{result['content']}\n"
            )
        
        return "\n---\n".join(context_parts)
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get vector store statistics"""
        if not self.collection:
            return {}
        
        try:
            count = self.collection.count()
            
            # Load metadata if available
            metadata_file = self.persist_directory / f"{self.collection_name}_metadata.json"
            if metadata_file.exists():
                with open(metadata_file, 'r') as f:
                    metadata = json.load(f)
            else:
                metadata = {}
            
            return {
                'collection_name': self.collection_name,
                'total_embeddings': count,
                'embedding_model': self.embedding_model,
                'persist_directory': str(self.persist_directory),
                'created_at': metadata.get('created_at', 'unknown'),
                'document_count': metadata.get('document_count', 0),
                'categories': metadata.get('categories', {})
            }
            
        except Exception as e:
            print(f"Error getting statistics: {e}")
            return {}
    
    def _save_metadata(self, documents: List[Document]) -> None:
        """Save collection metadata"""
        # Count categories
        categories = {}
        for doc in documents:
            cat = doc.metadata.get('category', 'unknown')
            categories[cat] = categories.get(cat, 0) + 1
        
        metadata = {
            'collection_name': self.collection_name,
            'created_at': datetime.now().isoformat(),
            'document_count': len(documents),
            'embedding_count': self.collection.count() if self.collection else 0,
            'embedding_model': self.embedding_model,
            'categories': categories
        }
        
        # Save to file
        metadata_file = self.persist_directory / f"{self.collection_name}_metadata.json"
        with open(metadata_file, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        print(f" Metadata saved: {metadata_file}")


if __name__ == "__main__":
    # Demo usage
    from document_processor import DocumentProcessor
    
    print("\n VECTOR STORE DEMO\n")
    
    # Process documents
    processor = DocumentProcessor()
    documents = processor.process_unstructured_corpus()
    
    if documents:
        # Create vector store
        vector_store = VectorStoreManager(
            persist_directory="./data/vector_db",
            collection_name="procurement_docs"
        )
        
        # Create collection
        vector_store.create_collection(documents, reset=True)
        
        # Test search
        print("\n Testing semantic search...")
        results = vector_store.semantic_search(
            query="What are the supplier selection criteria?",
            k=3,
            verbose=True
        )
        
        # Show statistics
        stats = vector_store.get_statistics()
        print("\n STATISTICS")
        print("="*60)
        for key, value in stats.items():
            print(f"{key}: {value}")
