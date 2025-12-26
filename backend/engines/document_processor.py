"""
Document Processor for RAG Pipeline
Handles document loading, chunking, and preprocessing for vector embeddings
"""

import os
from pathlib import Path
from typing import List, Dict, Any, Optional
import hashlib
from datetime import datetime

# Document processing
try:
    from langchain_text_splitters import RecursiveCharacterTextSplitter
except ImportError:
    from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from langchain_community.document_loaders import (
    TextLoader,
    UnstructuredMarkdownLoader,
    CSVLoader
)
from langchain_community.document_loaders import PDFMinerLoader
LANGCHAIN_AVAILABLE = True


class DocumentProcessor:
    """
    Processes documents for RAG pipeline
    - Loads various document types
    - Chunks documents intelligently
    - Adds metadata for traceability
    """
    
    def __init__(
        self,
        chunk_size: int = 1000,
        chunk_overlap: int = 200,
        data_directory: str = "./data"
    ):
        """
        Initialize document processor
        
        Args:
            chunk_size: Size of text chunks
            chunk_overlap: Overlap between chunks
            data_directory: Root data directory
        """
        if not LANGCHAIN_AVAILABLE:
            raise ImportError(
                "LangChain is required for RAG. Install with:\n"
                "pip install langchain langchain-community langchain-openai chromadb"
            )
        
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.data_directory = Path(data_directory)
        
        # Initialize text splitter
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
            separators=["\n\n", "\n", ". ", " ", ""]
        )
        
        # Document type handlers
        self.loaders = {
            '.txt': TextLoader,
            '.md': UnstructuredMarkdownLoader,
            '.pdf': PDFMinerLoader,
            '.csv': CSVLoader
        }
    
    def load_document(self, file_path: str) -> List[Document]:
        """
        Load a single document
        
        Args:
            file_path: Path to document
            
        Returns:
            List of LangChain Document objects
        """
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"Document not found: {file_path}")
        
        # Get appropriate loader
        extension = file_path.suffix.lower()
        loader_class = self.loaders.get(extension)
        
        if not loader_class:
            raise ValueError(f"Unsupported file type: {extension}")
        
        # Load document
        try:
            loader = loader_class(str(file_path))
            documents = loader.load()
            
            # Add metadata
            for doc in documents:
                doc.metadata.update({
                    'source': str(file_path),
                    'file_name': file_path.name,
                    'file_type': extension,
                    'processed_at': datetime.now().isoformat()
                })
            
            return documents
        except Exception as e:
            print(f"Error loading {file_path}: {e}")
            return []
    
    def load_directory(
        self,
        directory: str,
        recursive: bool = True,
        file_extensions: Optional[List[str]] = None
    ) -> List[Document]:
        """
        Load all documents from a directory
        
        Args:
            directory: Directory path
            recursive: Search subdirectories
            file_extensions: Filter by extensions (e.g., ['.txt', '.pdf'])
            
        Returns:
            List of all loaded documents
        """
        directory = Path(directory)
        
        if not directory.exists():
            raise FileNotFoundError(f"Directory not found: {directory}")
        
        all_documents = []
        
        # Get file pattern
        pattern = "**/*" if recursive else "*"
        
        # Process each file
        for file_path in directory.glob(pattern):
            if file_path.is_file():
                # Check extension filter
                if file_extensions and file_path.suffix.lower() not in file_extensions:
                    continue
                
                # Load document
                try:
                    documents = self.load_document(str(file_path))
                    all_documents.extend(documents)
                    print(f" Loaded: {file_path.name} ({len(documents)} chunks)")
                except Exception as e:
                    print(f" Failed: {file_path.name} - {e}")
        
        return all_documents
    
    def chunk_documents(self, documents: List[Document]) -> List[Document]:
        """
        Split documents into chunks
        
        Args:
            documents: List of documents to chunk
            
        Returns:
            List of chunked documents with metadata
        """
        chunked_docs = []
        
        for doc in documents:
            # Split document
            chunks = self.text_splitter.split_documents([doc])
            
            # Add chunk metadata
            for i, chunk in enumerate(chunks):
                chunk.metadata.update({
                    'chunk_id': i,
                    'total_chunks': len(chunks),
                    'chunk_hash': self._generate_hash(chunk.page_content)
                })
                chunked_docs.append(chunk)
        
        return chunked_docs
    
    def process_unstructured_corpus(self) -> List[Document]:
        """
        Process entire unstructured data corpus
        
        Returns:
            All processed and chunked documents
        """
        unstructured_dir = self.data_directory / "unstructured"
        
        if not unstructured_dir.exists():
            print(f"Warning: Unstructured directory not found: {unstructured_dir}")
            return []
        
        print("\n" + "="*60)
        print(" PROCESSING UNSTRUCTURED CORPUS")
        print("="*60)
        
        all_documents = []
        
        # Get all subdirectories in unstructured
        subdirs = [d.name for d in unstructured_dir.iterdir() if d.is_dir()]
        
        for subdir in subdirs:
            subdir_path = unstructured_dir / subdir
            print(f"\n Processing category: {subdir}/")
            docs = self.load_directory(
                str(subdir_path),
                recursive=True,
                file_extensions=['.txt', '.md', '.pdf']
            )
            
            # Add category metadata
            for doc in docs:
                doc.metadata['category'] = subdir
            
            all_documents.extend(docs)
            print(f"   Total: {len(docs)} documents loaded for {subdir}")
        
        if not all_documents:
            print("\n  No documents found in any subdirectory!")
            return []
            
        # Chunk all documents
        print(f"\n  Chunking {len(all_documents)} documents...")
        chunked_documents = self.chunk_documents(all_documents)
        
        print(f"\n Processing Complete!")
        print(f"   Documents: {len(all_documents)}")
        print(f"   Chunks: {len(chunked_documents)}")
        if len(all_documents) > 0:
            print(f"   Avg chunks/doc: {len(chunked_documents)/len(all_documents):.1f}")
        print("="*60 + "\n")
        
        return chunked_documents
    
    def process_structured_policies(self) -> List[Document]:
        """
        Process structured policy files (CSV) as documents
        
        Returns:
            Policy documents
        """
        structured_dir = self.data_directory / "structured"
        
        if not structured_dir.exists():
            return []
        
        print("\n Processing structured data (CSV files)...")
        
        # All structured CSV files
        policy_files = [
            'rule_book.csv',
            'procurement_rulebook.csv',
            'supplier_contracts.csv',
            'spend_data.csv',
            'supplier_master.csv',
            'client_master.csv',
            'pricing_benchmarks.csv',
            'proof_points.csv',
            'industry_benchmarks.csv',
            'market_pricing.csv'
        ]
        
        documents = []
        
        for file_name in policy_files:
            file_path = structured_dir / file_name
            if file_path.exists():
                try:
                    docs = self.load_document(str(file_path))
                    for doc in docs:
                        doc.metadata['category'] = 'structured_data'
                        doc.metadata['data_type'] = file_name.replace('.csv', '')
                    documents.extend(docs)
                    print(f"    {file_name} ({len(docs)} rows)")
                except Exception as e:
                    print(f"    {file_name}: {e}")
        
        return documents
    
    def process_calculated_data(self) -> List[Document]:
        """
        Process calculated/derived data files (CSV) as documents
        
        Returns:
            Calculated data documents
        """
        calculated_dir = self.data_directory / "calculated"
        
        if not calculated_dir.exists():
            return []
        
        print("\n Processing calculated/derived data...")
        
        # All calculated CSV files
        calculated_files = [
            'action_plan.csv',
            'calculated_metrics.csv',
            'forecasts_projections.csv',
            'historical_quarterly_trends.csv',
            'risk_register.csv',
            'scenario_planning.csv',
            'supplier_performance_history.csv'
        ]
        
        documents = []
        
        for file_name in calculated_files:
            file_path = calculated_dir / file_name
            if file_path.exists():
                try:
                    docs = self.load_document(str(file_path))
                    for doc in docs:
                        doc.metadata['category'] = 'calculated_data'
                        doc.metadata['data_type'] = file_name.replace('.csv', '')
                    documents.extend(docs)
                    print(f"    {file_name} ({len(docs)} rows)")
                except Exception as e:
                    print(f"    {file_name}: {e}")
        
        return documents
    
    def _generate_hash(self, text: str) -> str:
        """Generate unique hash for text content"""
        return hashlib.md5(text.encode()).hexdigest()[:12]
    
    def get_document_stats(self, documents: List[Document]) -> Dict[str, Any]:
        """
        Get statistics about processed documents
        
        Args:
            documents: List of documents
            
        Returns:
            Statistics dictionary
        """
        if not documents:
            return {}
        
        # Count by category
        categories = {}
        for doc in documents:
            cat = doc.metadata.get('category', 'unknown')
            categories[cat] = categories.get(cat, 0) + 1
        
        # Count by file type
        file_types = {}
        for doc in documents:
            ftype = doc.metadata.get('file_type', 'unknown')
            file_types[ftype] = file_types.get(ftype, 0) + 1
        
        # Calculate sizes
        total_chars = sum(len(doc.page_content) for doc in documents)
        avg_chunk_size = total_chars / len(documents) if documents else 0
        
        return {
            'total_documents': len(documents),
            'total_characters': total_chars,
            'average_chunk_size': int(avg_chunk_size),
            'categories': categories,
            'file_types': file_types,
            'unique_sources': len(set(doc.metadata.get('source', '') for doc in documents))
        }


if __name__ == "__main__":
    # Demo usage
    processor = DocumentProcessor(
        chunk_size=1000,
        chunk_overlap=200,
        data_directory="./data"
    )
    
    # Process unstructured corpus
    documents = processor.process_unstructured_corpus()
    
    # Get statistics
    stats = processor.get_document_stats(documents)
    
    print("\n DOCUMENT STATISTICS")
    print("="*60)
    for key, value in stats.items():
        print(f"{key}: {value}")
