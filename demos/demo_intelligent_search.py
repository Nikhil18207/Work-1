"""
Intelligent Search Demo
Demonstrates hyper-specific, region-aware procurement search
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.engines.intelligent_search_engine import IntelligentSearchEngine


def main():
    print("=" * 80)
    print("🧠 INTELLIGENT PROCUREMENT SEARCH - DEMO")
    print("=" * 80)
    print("\nThis demo shows aggressive, region-specific search capabilities")
    print("that can answer very detailed procurement questions.\n")
    
    # Initialize intelligent search engine
    engine = IntelligentSearchEngine()
    
    # Test queries - Very specific, region-aware
    test_queries = [
        # Malaysia specific
        "Top 3 suppliers of Rice Bran Oil in Malaysia",
        "Best Palm Oil manufacturers in Penang, Malaysia",
        
        # India specific
        "Leading Vegetable Oil suppliers in Mumbai, India",
        "Top 5 Rice Bran Oil exporters in Chennai, India",
        
        # UK specific
        "Top Vegetable Oil suppliers in UK",
        "Best Sunflower Oil manufacturers in London",
        
        # Other regions
        "Leading Palm Oil exporters in Indonesia",
        "Top Coconut Oil suppliers in Philippines",
        "Best Olive Oil manufacturers in Spain",
        "Top Soybean Oil suppliers in Brazil",
    ]
    
    print("\n📋 DEMO QUERIES:")
    print("-" * 80)
    for i, query in enumerate(test_queries, 1):
        print(f"{i}. {query}")
    
    print("\n\n" + "=" * 80)
    print("EXECUTING INTELLIGENT SEARCHES...")
    print("=" * 80)
    
    # Execute searches
    for i, query in enumerate(test_queries[:3], 1):  # Demo first 3
        print(f"\n\n{'#' * 80}")
        print(f"QUERY {i}: {query}")
        print('#' * 80)
        
        result = engine.intelligent_search(query, max_results=5)
        
        if result['status'] == 'success':
            print(result['formatted_output'])
        else:
            print(f"❌ Search failed: {result.get('message', 'Unknown error')}")
    
    print("\n\n" + "=" * 80)
    print("✅ INTELLIGENT SEARCH DEMO COMPLETE!")
    print("=" * 80)
    print("\n💡 KEY FEATURES DEMONSTRATED:")
    print("   ✅ Region-specific search (country, state, city level)")
    print("   ✅ Multi-strategy search (tries 7 different query variations)")
    print("   ✅ Intelligent query parsing (extracts product, region, number)")
    print("   ✅ Relevance ranking (scores results based on query match)")
    print("   ✅ Supplier extraction (finds company names automatically)")
    print("   ✅ Works for ANY region globally")
    
    print("\n\n📝 TO ENABLE:")
    print("   Add to .env file:")
    print("   SERPER_API_KEY=your_key_here  (Get free at https://serper.dev/)")
    print("   or")
    print("   GOOGLE_SEARCH_API_KEY=your_key_here")
    print("   GOOGLE_SEARCH_CX=your_cx_here")
    
    print("\n\n🌍 SUPPORTED REGIONS:")
    print("   ✅ Malaysia, India, UK, USA, Germany, China, Indonesia")
    print("   ✅ Thailand, Vietnam, Singapore, Japan, Australia")
    print("   ✅ Spain, France, Italy, Brazil, Mexico, Canada")
    print("   ✅ UAE, Saudi Arabia, Egypt, South Africa, Kenya")
    print("   ✅ And 20+ more countries with city-level support!")


if __name__ == "__main__":
    main()
