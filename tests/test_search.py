"""
Test actual search functionality
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from backend.engines.intelligent_search_engine import IntelligentSearchEngine

print("=" * 80)
print("TESTING INTELLIGENT SEARCH ENGINE")
print("=" * 80)

engine = IntelligentSearchEngine()

print(f"\nSearch Provider: {engine.search_provider}")
print(f"Serper API Key: {' Configured' if engine.serper_api_key else ' Missing'}")

print("\n" + "=" * 80)
print("TESTING SEARCH: Top 3 suppliers of Rice Bran Oil in Malaysia")
print("=" * 80)

try:
    result = engine.intelligent_search(
        "Top 3 suppliers of Rice Bran Oil in Malaysia",
        max_results=5
    )
    
    print(f"\nStatus: {result['status']}")
    print(f"Results found: {len(result['results'])}")
    
    if result['results']:
        print("\n SEARCH SUCCESSFUL!")
        print("\nTop 3 Results:")
        for i, res in enumerate(result['results'][:3], 1):
            print(f"\n{i}. {res['title']}")
            print(f"   Score: {res.get('relevance_score', 0)}")
            print(f"   {res['snippet'][:100]}...")
    else:
        print("\n No results returned")
        print("This might mean:")
        print("  1. API key is invalid")
        print("  2. API quota exceeded")
        print("  3. Network issue")
        
except Exception as e:
    print(f"\n ERROR: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 80)
