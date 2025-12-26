"""
RAG System Demo
Demonstrates the full RAG pipeline capabilities
"""

import os
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.engines.vector_store_manager import VectorStoreManager
from backend.engines.rag_engine import RAGEngine


def demo_rag_system():
    """Demonstrate RAG system capabilities"""
    
    print("\n" + "="*70)
    print(" RAG SYSTEM DEMONSTRATION")
    print("="*70)
    
    # Initialize vector store
    print("\n Loading vector store...")
    vector_store = VectorStoreManager(
        persist_directory="./data/vector_db",
        collection_name="procurement_docs"
    )
    
    # Load collection
    if not vector_store.load_collection():
        print("\n Vector store not found!")
        print("   Run: python scripts/setup_rag.py")
        return
    
    # Show statistics
    stats = vector_store.get_statistics()
    print(f"\n Vector Store Stats:")
    print(f"   Total Embeddings: {stats.get('total_embeddings', 0)}")
    print(f"   Categories: {stats.get('categories', {})}")
    
    # Initialize RAG engine
    print("\n Initializing RAG engine...")
    rag = RAGEngine(
        vector_store_manager=vector_store,
        model="gpt-4",
        temperature=0.7
    )
    
    # Demo queries
    demo_queries = [
        {
            "question": "What are the key criteria for supplier selection?",
            "category": None,
            "k": 5
        },
        {
            "question": "How should we manage regional concentration risk?",
            "category": "policies",
            "k": 3
        },
        {
            "question": "What are the ESG requirements for suppliers?",
            "category": None,
            "k": 4
        },
        {
            "question": "How do we handle tail spend fragmentation?",
            "category": "policies",
            "k": 3
        },
        {
            "question": "What are the payment terms best practices?",
            "category": "contracts",
            "k": 3
        }
    ]
    
    print("\n" + "="*70)
    print(" RUNNING DEMO QUERIES")
    print("="*70)
    
    for i, query_config in enumerate(demo_queries, 1):
        print(f"\n{''*70}")
        print(f"Query #{i}")
        print(f"{''*70}")
        print(f" Question: {query_config['question']}")
        
        if query_config['category']:
            print(f" Category Filter: {query_config['category']}")
        
        print(f" Retrieving top {query_config['k']} documents...")
        
        # Execute query
        try:
            response = rag.query(
                question=query_config['question'],
                k=query_config['k'],
                category=query_config['category'],
                include_sources=True,
                verbose=False
            )
            
            # Display answer
            print(f"\n Answer:")
            print(f"{response['answer']}")
            
            # Display sources
            if response.get('sources'):
                print(f"\n Sources ({len(response['sources'])}):")
                for source in response['sources'][:3]:  # Show top 3
                    print(f"   {source['rank']}. {source['source']}")
                    print(f"      Category: {source['category']}")
                    print(f"      Relevance: {source['score']:.3f}")
                    print(f"      Excerpt: {source['excerpt'][:100]}...")
                    print()
            
        except Exception as e:
            print(f"\n Error: {e}")
        
        print()
    
    # Demo procurement recommendation
    print("\n" + "="*70)
    print(" PROCUREMENT RECOMMENDATION DEMO")
    print("="*70)
    
    scenario = """
    We are procuring Rice Bran Oil and currently have 85% of our spend concentrated 
    in Malaysia. This creates significant regional risk. We need to diversify our 
    supplier base while maintaining quality and cost efficiency.
    """
    
    context_data = {
        'product': 'Rice Bran Oil',
        'region': 'Malaysia',
        'issue': 'Regional concentration risk',
        'current_spend': '$2.5M',
        'concentration': '85%'
    }
    
    print(f"\n Scenario:")
    print(scenario.strip())
    
    print(f"\n Context Data:")
    for key, value in context_data.items():
        print(f"   {key}: {value}")
    
    print(f"\n Generating recommendation with RAG...")
    
    try:
        recommendation = rag.get_procurement_recommendation(
            scenario=scenario,
            context_data=context_data,
            k=5
        )
        
        print(f"\n Recommendation:")
        print(recommendation['recommendation'])
        
        print(f"\n Based on {len(recommendation['sources'])} sources:")
        for source in recommendation['sources'][:5]:
            print(f"   - {source['source']} ({source['category']})")
        
    except Exception as e:
        print(f"\n Error: {e}")
    
    # Summary
    print("\n" + "="*70)
    print(" DEMO COMPLETE")
    print("="*70)
    print("\n Key Features Demonstrated:")
    print("    Semantic search across procurement knowledge base")
    print("    Context-aware answer generation")
    print("    Source citation and traceability")
    print("    Category filtering")
    print("    Procurement-specific recommendations")
    print("\n" + "="*70 + "\n")


def demo_semantic_search():
    """Demo just the semantic search capabilities"""
    
    print("\n" + "="*70)
    print(" SEMANTIC SEARCH DEMO")
    print("="*70)
    
    # Initialize vector store
    vector_store = VectorStoreManager(
        persist_directory="./data/vector_db",
        collection_name="procurement_docs"
    )
    
    if not vector_store.load_collection():
        print("\n Vector store not found!")
        return
    
    # Test searches
    test_searches = [
        ("supplier quality requirements", None),
        ("risk management strategies", "policies"),
        ("contract payment terms", "contracts"),
        ("sustainability and ESG", None)
    ]
    
    for query, category in test_searches:
        print(f"\n{''*70}")
        print(f" Search: {query}")
        if category:
            print(f" Category: {category}")
        print(f"{''*70}")
        
        results = vector_store.semantic_search(
            query=query,
            k=3,
            category=category,
            verbose=True
        )
        
        print(f"\n Found {len(results)} results")
    
    print("\n" + "="*70 + "\n")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="RAG System Demo")
    parser.add_argument(
        "--search-only",
        action="store_true",
        help="Demo semantic search only (no LLM)"
    )
    
    args = parser.parse_args()
    
    if args.search_only:
        demo_semantic_search()
    else:
        demo_rag_system()
