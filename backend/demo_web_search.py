"""
Web Search Demo
Demonstrates real-time market intelligence fetching
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from llm_recommendation_system import LLMRecommendationSystem


def main():
    print("=" * 80)
    print("🌐 WEB SEARCH DEMO - Real-Time Market Intelligence")
    print("=" * 80)
    
    # Initialize system with web search enabled
    system = LLMRecommendationSystem(
        llm_provider="openai",
        enable_llm=True,
        enable_web_search=True
    )
    
    # Example 1: Search for top suppliers in India
    print("\n\n📍 EXAMPLE 1: Top Rice Bran Oil Suppliers in India")
    print("-" * 80)
    result = system.search_top_suppliers("Rice Bran Oil", "India")
    print(result['formatted_output'])
    
    # Example 2: Search for supplier news
    print("\n\n📰 EXAMPLE 2: News about EuroSeed GmbH")
    print("-" * 80)
    result = system.search_supplier_news("EuroSeed GmbH", region="Germany")
    print(result['formatted_output'])
    
    # Example 3: Search for market intelligence
    print("\n\n📊 EXAMPLE 3: Rice Bran Oil Market Intelligence")
    print("-" * 80)
    result = system.search_market_intelligence("Rice Bran Oil", region="APAC")
    print(result['formatted_output'])
    
    # Example 4: Search for top suppliers in UK
    print("\n\n🇬🇧 EXAMPLE 4: Top Vegetable Oil Suppliers in UK")
    print("-" * 80)
    result = system.search_top_suppliers("Vegetable Oil", "UK")
    print(result['formatted_output'])
    
    # Example 5: Search for regulatory updates
    print("\n\n⚖️ EXAMPLE 5: Malaysia Export Regulations")
    print("-" * 80)
    result = system.search_regulatory_updates("Malaysia", product_category="Palm Oil")
    print(result['formatted_output'])
    
    print("\n\n" + "=" * 80)
    print("✅ WEB SEARCH DEMO COMPLETE!")
    print("=" * 80)
    print("\n📝 NOTE: To enable web search, add one of these to your .env file:")
    print("   SERPER_API_KEY=your_key_here  (Get free key at https://serper.dev/)")
    print("   or")
    print("   GOOGLE_SEARCH_API_KEY=your_key_here")
    print("   GOOGLE_SEARCH_CX=your_cx_here")


if __name__ == "__main__":
    main()
