"""
Web Intelligence Agent
Internet scraping for real-time market data, prices, supplier info
"""

import sys
from pathlib import Path
from typing import Dict, Any, Optional
import os
from dotenv import load_dotenv

load_dotenv()

root_path = Path(__file__).parent.parent.parent.parent
if str(root_path) not in sys.path:
    sys.path.insert(0, str(root_path))

from backend.agents.base_agent import BaseAgent
from backend.engines.web_search_engine import WebSearchEngine


class WebIntelligenceAgent(BaseAgent):
    """
    Agent for web scraping and real-time intelligence
    
    Input:
        - query_type: str ('market_price', 'supplier_search', 'supplier_news', 'market_intelligence')
        - product: str (product category)
        - region: str (optional)
        - supplier_name: str (optional, for supplier-specific queries)
        
    Output:
        - results: List[Dict] (search results)
        - market_price: Dict (if query_type='market_price')
        - summary: str
    """
    
    def __init__(self):
        super().__init__(
            name="WebIntelligence",
            description="Scrapes internet for real-time market data and intelligence"
        )
        self.web_search = WebSearchEngine()
    
    def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute web intelligence gathering
        """
        try:
            query_type = input_data.get('query_type', 'market_intelligence')
            product = input_data.get('product', '')
            region = input_data.get('region', '')
            supplier_name = input_data.get('supplier_name', '')
            
            self._log(f"Web intelligence: {query_type} for {product} in {region}")
            
            if query_type == 'market_price':
                return self._get_market_price(product, region)
            elif query_type == 'supplier_search':
                return self._search_suppliers(product, region)
            elif query_type == 'supplier_news':
                return self._get_supplier_news(supplier_name, region)
            elif query_type == 'market_intelligence':
                return self._get_market_intelligence(product, region)
            else:
                return self._create_response(
                    success=False,
                    error=f"Unknown query_type: {query_type}"
                )
                
        except Exception as e:
            self._log(f"Error in web intelligence: {str(e)}", "ERROR")
            return self._create_response(
                success=False,
                error=str(e)
            )
    
    def _get_market_price(self, product: str, region: str) -> Dict[str, Any]:
        """Get current market price for a product"""
        try:
            # Search for market prices
            query = f"{product} market price {region} 2024" if region else f"{product} market price 2024"
            results = self.web_search.search(query)
            
            # Parse results for price information
            price_data = {
                'product': product,
                'region': region or 'Global',
                'search_results': results.get('organic_results', [])[:5],
                'sources': [r.get('link', '') for r in results.get('organic_results', [])[:5]]
            }
            
            # Try to extract price from results
            price_mentions = []
            for result in results.get('organic_results', [])[:10]:
                snippet = result.get('snippet', '').lower()
                # Look for price patterns (simplified)
                if any(currency in snippet for currency in ['$', 'usd', 'price']):
                    price_mentions.append({
                        'source': result.get('title', ''),
                        'snippet': result.get('snippet', ''),
                        'link': result.get('link', '')
                    })
            
            price_data['price_mentions'] = price_mentions[:3]
            
            summary = f"Found {len(price_mentions)} price references for {product}"
            if region:
                summary += f" in {region}"
            
            self._log(f"Market price search complete: {len(price_mentions)} mentions found")
            
            return self._create_response(
                success=True,
                data=price_data,
                sources=price_data['sources']
            )
            
        except Exception as e:
            self._log(f"Error getting market price: {str(e)}", "ERROR")
            return self._create_response(
                success=False,
                error=str(e)
            )
    
    def _search_suppliers(self, product: str, region: str) -> Dict[str, Any]:
        """Search for suppliers"""
        try:
            query = f"top {product} suppliers {region}" if region else f"top {product} suppliers"
            results = self.web_search.search(query)
            
            suppliers_found = []
            for result in results.get('organic_results', [])[:10]:
                suppliers_found.append({
                    'name': result.get('title', ''),
                    'description': result.get('snippet', ''),
                    'link': result.get('link', ''),
                    'source': result.get('source', '')
                })
            
            supplier_data = {
                'product': product,
                'region': region or 'Global',
                'suppliers_found': suppliers_found,
                'total_results': len(suppliers_found)
            }
            
            self._log(f"Supplier search complete: {len(suppliers_found)} suppliers found")
            
            return self._create_response(
                success=True,
                data=supplier_data,
                sources=[s['link'] for s in suppliers_found]
            )
            
        except Exception as e:
            self._log(f"Error searching suppliers: {str(e)}", "ERROR")
            return self._create_response(
                success=False,
                error=str(e)
            )
    
    def _get_supplier_news(self, supplier_name: str, region: str) -> Dict[str, Any]:
        """Get news about a specific supplier"""
        try:
            query = f"{supplier_name} news {region}" if region else f"{supplier_name} news"
            results = self.web_search.search(query)
            
            news_items = []
            for result in results.get('organic_results', [])[:5]:
                news_items.append({
                    'title': result.get('title', ''),
                    'snippet': result.get('snippet', ''),
                    'link': result.get('link', ''),
                    'date': result.get('date', 'Recent')
                })
            
            news_data = {
                'supplier': supplier_name,
                'region': region or 'Global',
                'news_items': news_items,
                'total_items': len(news_items)
            }
            
            self._log(f"Supplier news search complete: {len(news_items)} items found")
            
            return self._create_response(
                success=True,
                data=news_data,
                sources=[n['link'] for n in news_items]
            )
            
        except Exception as e:
            self._log(f"Error getting supplier news: {str(e)}", "ERROR")
            return self._create_response(
                success=False,
                error=str(e)
            )
    
    def _get_market_intelligence(self, product: str, region: str) -> Dict[str, Any]:
        """Get general market intelligence"""
        try:
            query = f"{product} market trends {region} 2024" if region else f"{product} market trends 2024"
            results = self.web_search.search(query)
            
            intelligence = []
            for result in results.get('organic_results', [])[:8]:
                intelligence.append({
                    'title': result.get('title', ''),
                    'snippet': result.get('snippet', ''),
                    'link': result.get('link', ''),
                    'relevance': 'high' if product.lower() in result.get('snippet', '').lower() else 'medium'
                })
            
            intel_data = {
                'product': product,
                'region': region or 'Global',
                'intelligence': intelligence,
                'total_insights': len(intelligence)
            }
            
            self._log(f"Market intelligence search complete: {len(intelligence)} insights found")
            
            return self._create_response(
                success=True,
                data=intel_data,
                sources=[i['link'] for i in intelligence]
            )
            
        except Exception as e:
            self._log(f"Error getting market intelligence: {str(e)}", "ERROR")
            return self._create_response(
                success=False,
                error=str(e)
            )
