"""
Web Search Engine
Fetches real-time market intelligence, news, and supplier information from the web
"""

import os
import requests
from typing import Dict, List, Any, Optional
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()


class WebSearchEngine:
    """
    Web Search Engine for real-time market intelligence
    Fetches news, supplier information, and market updates
    """

    def __init__(self):
        """Initialize web search engine"""
        # Google Custom Search API (free tier: 100 queries/day)
        self.google_api_key = os.getenv('GOOGLE_SEARCH_API_KEY', '')
        self.google_cx = os.getenv('GOOGLE_SEARCH_CX', '')
        
        # Serper API (alternative, better for news)
        self.serper_api_key = os.getenv('SERPER_API_KEY', '')
        
        # Determine which search provider to use
        self.search_provider = self._determine_provider()

    def _determine_provider(self) -> str:
        """Determine which search provider to use based on available API keys"""
        if self.serper_api_key:
            return 'serper'
        elif self.google_api_key and self.google_cx:
            return 'google'
        else:
            return 'none'

    def search_supplier_news(
        self,
        supplier_name: str,
        region: Optional[str] = None,
        max_results: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Search for news about a specific supplier
        
        Args:
            supplier_name: Name of the supplier
            region: Optional region filter
            max_results: Maximum number of results
            
        Returns:
            List of news articles with title, snippet, link, date
        """
        query = f"{supplier_name} supplier news"
        if region:
            query += f" {region}"
        
        return self._search(query, max_results, search_type='news')

    def search_market_intelligence(
        self,
        product_category: str,
        region: Optional[str] = None,
        max_results: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Search for market intelligence about a product category
        
        Args:
            product_category: Product category (e.g., "Rice Bran Oil")
            region: Optional region filter
            max_results: Maximum number of results
            
        Returns:
            List of market intelligence articles
        """
        query = f"{product_category} market news price trends"
        if region:
            query += f" {region}"
        
        return self._search(query, max_results, search_type='news')

    def search_top_suppliers(
        self,
        product_category: str,
        region: str,
        max_results: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Search for top suppliers of a product in a region
        
        Args:
            product_category: Product category
            region: Region to search in
            max_results: Maximum number of results
            
        Returns:
            List of supplier information
        """
        query = f"top {product_category} suppliers {region}"
        
        return self._search(query, max_results, search_type='general')

    def search_price_trends(
        self,
        product_category: str,
        region: Optional[str] = None,
        max_results: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Search for price trends and forecasts
        
        Args:
            product_category: Product category
            region: Optional region filter
            max_results: Maximum number of results
            
        Returns:
            List of price trend articles
        """
        query = f"{product_category} price forecast trends 2024"
        if region:
            query += f" {region}"
        
        return self._search(query, max_results, search_type='news')

    def search_regulatory_updates(
        self,
        region: str,
        product_category: Optional[str] = None,
        max_results: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Search for regulatory updates affecting procurement
        
        Args:
            region: Region to search for regulations
            product_category: Optional product category
            max_results: Maximum number of results
            
        Returns:
            List of regulatory update articles
        """
        query = f"{region} export import regulations"
        if product_category:
            query += f" {product_category}"
        
        return self._search(query, max_results, search_type='news')

    def _search(
        self,
        query: str,
        max_results: int = 5,
        search_type: str = 'general'
    ) -> List[Dict[str, Any]]:
        """
        Perform web search using available provider
        
        Args:
            query: Search query
            max_results: Maximum results to return
            search_type: 'general' or 'news'
            
        Returns:
            List of search results
        """
        if self.search_provider == 'serper':
            return self._search_serper(query, max_results, search_type)
        elif self.search_provider == 'google':
            return self._search_google(query, max_results, search_type)
        else:
            return self._search_fallback(query)

    def _search_serper(
        self,
        query: str,
        max_results: int,
        search_type: str
    ) -> List[Dict[str, Any]]:
        """
        Search using Serper API (recommended for news)
        
        API: https://serper.dev/
        Free tier: 2,500 queries/month
        """
        try:
            url = "https://google.serper.dev/search"
            
            payload = {
                "q": query,
                "num": max_results
            }
            
            if search_type == 'news':
                url = "https://google.serper.dev/news"
            
            headers = {
                'X-API-KEY': self.serper_api_key,
                'Content-Type': 'application/json'
            }
            
            response = requests.post(url, json=payload, headers=headers, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            results = []
            items = data.get('news', []) if search_type == 'news' else data.get('organic', [])
            
            for item in items[:max_results]:
                results.append({
                    'title': item.get('title', ''),
                    'snippet': item.get('snippet', ''),
                    'link': item.get('link', ''),
                    'date': item.get('date', datetime.now().strftime('%Y-%m-%d')),
                    'source': item.get('source', 'Unknown'),
                    'search_engine': 'serper'
                })
            
            return results
            
        except Exception as e:
            print(f"⚠️ Serper search failed: {e}")
            return self._search_fallback(query)

    def _search_google(
        self,
        query: str,
        max_results: int,
        search_type: str
    ) -> List[Dict[str, Any]]:
        """
        Search using Google Custom Search API
        
        Free tier: 100 queries/day
        Setup: https://developers.google.com/custom-search/v1/overview
        """
        try:
            url = "https://www.googleapis.com/customsearch/v1"
            
            params = {
                'key': self.google_api_key,
                'cx': self.google_cx,
                'q': query,
                'num': min(max_results, 10)  # Google max is 10
            }
            
            if search_type == 'news':
                params['sort'] = 'date'
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            results = []
            for item in data.get('items', [])[:max_results]:
                results.append({
                    'title': item.get('title', ''),
                    'snippet': item.get('snippet', ''),
                    'link': item.get('link', ''),
                    'date': datetime.now().strftime('%Y-%m-%d'),
                    'source': item.get('displayLink', 'Unknown'),
                    'search_engine': 'google'
                })
            
            return results
            
        except Exception as e:
            print(f"⚠️ Google search failed: {e}")
            return self._search_fallback(query)

    def _search_fallback(self, query: str) -> List[Dict[str, Any]]:
        """
        Fallback when no search API is available
        Returns helpful message
        """
        return [{
            'title': 'Web Search Not Configured',
            'snippet': f'To enable real-time web search for "{query}", please configure either:\n'
                      '1. Serper API (recommended): Get free API key at https://serper.dev/\n'
                      '2. Google Custom Search: Set up at https://developers.google.com/custom-search/v1/overview\n\n'
                      'Add to .env file:\n'
                      'SERPER_API_KEY=your_key_here\n'
                      'or\n'
                      'GOOGLE_SEARCH_API_KEY=your_key_here\n'
                      'GOOGLE_SEARCH_CX=your_cx_here',
            'link': 'https://serper.dev/',
            'date': datetime.now().strftime('%Y-%m-%d'),
            'source': 'System',
            'search_engine': 'none'
        }]

    def format_search_results(
        self,
        results: List[Dict[str, Any]],
        query: str
    ) -> str:
        """
        Format search results as readable text
        
        Args:
            results: List of search results
            query: Original search query
            
        Returns:
            Formatted text output
        """
        if not results:
            return f"No results found for: {query}"
        
        output = f"🔍 Web Search Results for: {query}\n"
        output += "=" * 80 + "\n\n"
        
        for i, result in enumerate(results, 1):
            output += f"{i}. {result['title']}\n"
            output += f"   Source: {result['source']} | Date: {result['date']}\n"
            output += f"   {result['snippet']}\n"
            output += f"   Link: {result['link']}\n\n"
        
        return output


# Example usage
if __name__ == "__main__":
    search_engine = WebSearchEngine()
    
    print("=" * 80)
    print("WEB SEARCH ENGINE TEST")
    print("=" * 80)
    
    # Test 1: Search for supplier news
    print("\n1. SUPPLIER NEWS: EuroSeed GmbH")
    print("-" * 80)
    results = search_engine.search_supplier_news("EuroSeed GmbH", region="Germany")
    print(search_engine.format_search_results(results, "EuroSeed GmbH supplier news"))
    
    # Test 2: Search for top suppliers
    print("\n2. TOP SUPPLIERS: Rice Bran Oil in India")
    print("-" * 80)
    results = search_engine.search_top_suppliers("Rice Bran Oil", "India")
    print(search_engine.format_search_results(results, "Top Rice Bran Oil suppliers India"))
    
    # Test 3: Search for market intelligence
    print("\n3. MARKET INTELLIGENCE: Rice Bran Oil")
    print("-" * 80)
    results = search_engine.search_market_intelligence("Rice Bran Oil")
    print(search_engine.format_search_results(results, "Rice Bran Oil market intelligence"))
    
    # Test 4: Search for price trends
    print("\n4. PRICE TRENDS: Vegetable Oil")
    print("-" * 80)
    results = search_engine.search_price_trends("Vegetable Oil", region="APAC")
    print(search_engine.format_search_results(results, "Vegetable Oil price trends APAC"))
    
    # Test 5: Search for regulatory updates
    print("\n5. REGULATORY UPDATES: Malaysia")
    print("-" * 80)
    results = search_engine.search_regulatory_updates("Malaysia", product_category="Palm Oil")
    print(search_engine.format_search_results(results, "Malaysia Palm Oil regulations"))
