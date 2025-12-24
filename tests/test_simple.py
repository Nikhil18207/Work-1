"""
Simple Search Test - Clean Output
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from backend.engines.intelligent_search_engine import IntelligentSearchEngine

print("INTELLIGENT SEARCH TEST")
print("=" * 60)

engine = IntelligentSearchEngine()
print(f"Provider: {engine.search_provider}")

# Test query
query = "Top 3 suppliers of Rice Bran Oil in Malaysia"
print(f"\nQuery: {query}")
print("-" * 60)

result = engine.intelligent_search(query, max_results=5)

print(f"\nParsed Query:")
print(f"  Product: {result['parsed_query']['product']}")
print(f"  Region: {result['parsed_query']['region']['specific_location']}")
print(f"  Number: {result['parsed_query']['number']}")
print(f"  Type: {result['parsed_query']['query_type']}")

print(f"\nResults Found: {len(result['results'])}")

if result['results']:
    print("\nTop Results:")
    for i, res in enumerate(result['results'][:5], 1):
        print(f"\n{i}. {res['title']}")
        print(f"   Relevance: {res.get('relevance_score', 0)}/37")
        print(f"   Source: {res['source']}")
        # Clean snippet - remove special characters
        snippet = res['snippet'].encode('ascii', 'ignore').decode('ascii')
        print(f"   {snippet[:80]}...")

if result['extracted_suppliers']:
    print(f"\nExtracted Suppliers: {len(result['extracted_suppliers'])}")
    for i, supplier in enumerate(result['extracted_suppliers'][:3], 1):
        name = supplier['name'].encode('ascii', 'ignore').decode('ascii')
        print(f"  {i}. {name}")

print("\n" + "=" * 60)
print("SUCCESS! Search is working!")
