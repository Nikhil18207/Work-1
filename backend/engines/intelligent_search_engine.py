"""
Intelligent Search Engine
Aggressive, region-specific search for detailed procurement queries
Handles questions like: "Top 3 suppliers of Rice Bran Oil in Malaysia"
"""

import os
import requests
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
from dotenv import load_dotenv
import re

load_dotenv()


class IntelligentSearchEngine:
    """
    Intelligent Search Engine for hyper-specific procurement queries
    - Region-aware (country, state, city level)
    - Multi-strategy search (tries multiple query variations)
    - Aggressive result extraction
    - Handles very specific questions
    """

    def __init__(self):
        """Initialize intelligent search engine"""
        # API keys
        self.serper_api_key = os.getenv('SERPER_API_KEY', '')
        self.google_api_key = os.getenv('GOOGLE_SEARCH_API_KEY', '')
        self.google_cx = os.getenv('GOOGLE_SEARCH_CX', '')
        
        # Determine provider
        self.search_provider = self._determine_provider()
        
        # Note: We don't hardcode regions - Google Search understands ALL countries,
        # states, cities globally. This makes the system truly universal.

    def _determine_provider(self) -> str:
        """Determine which search provider to use"""
        if self.serper_api_key:
            return 'serper'
        elif self.google_api_key and self.google_cx:
            return 'google'
        else:
            return 'none'

    def intelligent_search(
        self,
        query: str,
        max_results: int = 10
    ) -> Dict[str, Any]:
        """
        Intelligent search that understands natural language queries
        
        Examples:
        - "Top 3 suppliers of Rice Bran Oil in Malaysia"
        - "Best Vegetable Oil manufacturers in Mumbai, India"
        - "Leading Palm Oil exporters in Indonesia"
        - "Rice Bran Oil suppliers in Penang, Malaysia"
        
        Args:
            query: Natural language query
            max_results: Maximum results to return
            
        Returns:
            Dictionary with parsed query, search results, and formatted output
        """
        # Parse the query
        parsed = self._parse_query(query)
        
        # Generate multiple search strategies
        search_queries = self._generate_search_strategies(parsed)
        
        # Execute searches with multiple strategies
        all_results = []
        for search_query in search_queries[:3]:  # Try top 3 strategies
            results = self._execute_search(search_query, max_results)
            all_results.extend(results)
        
        # Deduplicate and rank results
        unique_results = self._deduplicate_results(all_results)
        ranked_results = self._rank_results(unique_results, parsed)
        
        # Extract specific information
        extracted_info = self._extract_supplier_info(ranked_results, parsed)
        
        return {
            'status': 'success',
            'original_query': query,
            'parsed_query': parsed,
            'search_strategies': search_queries,
            'results': ranked_results[:max_results],
            'extracted_suppliers': extracted_info,
            'formatted_output': self._format_intelligent_output(
                query, parsed, ranked_results[:max_results], extracted_info
            )
        }

    def _parse_query(self, query: str) -> Dict[str, Any]:
        """
        Parse natural language query to extract key information
        
        Extracts:
        - Product/commodity
        - Region (country, state, city)
        - Number requested (top 3, top 5, etc.)
        - Query type (suppliers, manufacturers, exporters, etc.)
        """
        query_lower = query.lower()
        
        # Extract number (top 3, top 5, etc.)
        number_match = re.search(r'top\s+(\d+)', query_lower)
        number = int(number_match.group(1)) if number_match else 10
        
        # Extract region
        region = self._extract_region(query)
        
        # Extract product/commodity
        product = self._extract_product(query)
        
        # Extract query type
        query_type = self._extract_query_type(query_lower)
        
        return {
            'product': product,
            'region': region,
            'number': number,
            'query_type': query_type,
            'original': query
        }

    def _extract_region(self, query: str) -> Dict[str, str]:
        """
        Extract region information from query
        Works universally for ANY country, state, or city globally
        Google Search understands all regions automatically
        """
        query_lower = query.lower()
        
        # Common region patterns - works for ANY location
        region_patterns = [
            r'in\s+([A-Z][A-Za-z\s,]+?)(?:\s+(?:for|of|with|and|or|top|best|leading)|\s*$)',  # "in Malaysia", "in Mumbai, India"
            r'from\s+([A-Z][A-Za-z\s,]+?)(?:\s+(?:for|of|with|and|or|top|best|leading)|\s*$)',  # "from India"
            r'at\s+([A-Z][A-Za-z\s,]+?)(?:\s+(?:for|of|with|and|or|top|best|leading)|\s*$)',  # "at Mumbai"
        ]
        
        for pattern in region_patterns:
            match = re.search(pattern, query)
            if match:
                location = match.group(1).strip()
                # Clean up common trailing words
                location = re.sub(r'\s+(for|of|with|and|or)$', '', location, flags=re.IGNORECASE)
                return {
                    'country': location,
                    'specific_location': location,
                    'found': True
                }
        
        return {'country': 'Global', 'specific_location': None, 'found': False}

    def _extract_product(self, query: str) -> str:
        """Extract product/commodity from query"""
        # Common product patterns
        product_keywords = [
            'rice bran oil', 'vegetable oil', 'palm oil', 'sunflower oil',
            'soybean oil', 'canola oil', 'olive oil', 'coconut oil',
            'corn oil', 'peanut oil', 'sesame oil', 'mustard oil',
            'oil', 'grain', 'wheat', 'rice', 'corn', 'soybean',
            'spices', 'sugar', 'salt', 'flour'
        ]
        
        query_lower = query.lower()
        for product in sorted(product_keywords, key=len, reverse=True):
            if product in query_lower:
                return product.title()
        
        # If no specific product found, try to extract noun phrases
        words = query.split()
        for i, word in enumerate(words):
            if word.lower() in ['of', 'for']:
                if i + 1 < len(words):
                    # Take next 1-3 words as product
                    product_words = words[i+1:min(i+4, len(words))]
                    # Stop at prepositions
                    stop_words = ['in', 'at', 'from', 'to', 'for']
                    product_words = [w for w in product_words if w.lower() not in stop_words]
                    if product_words:
                        return ' '.join(product_words)
        
        return 'Product'

    def _extract_query_type(self, query_lower: str) -> str:
        """Extract type of query (suppliers, manufacturers, etc.)"""
        if 'supplier' in query_lower:
            return 'suppliers'
        elif 'manufacturer' in query_lower or 'producer' in query_lower:
            return 'manufacturers'
        elif 'exporter' in query_lower:
            return 'exporters'
        elif 'distributor' in query_lower:
            return 'distributors'
        elif 'vendor' in query_lower:
            return 'vendors'
        else:
            return 'suppliers'

    def _generate_search_strategies(self, parsed: Dict[str, Any]) -> List[str]:
        """
        Generate multiple search query variations for better results
        
        Strategies:
        1. Exact match: "top rice bran oil suppliers in Malaysia"
        2. Industry specific: "rice bran oil manufacturers Malaysia industry"
        3. B2B focused: "rice bran oil suppliers Malaysia B2B wholesale"
        4. Company listing: "rice bran oil companies Malaysia list"
        5. Regional specific: "Malaysia rice bran oil exporters directory"
        """
        product = parsed['product']
        region = parsed['region']['specific_location'] or parsed['region']['country']
        query_type = parsed['query_type']
        number = parsed['number']
        
        strategies = []
        
        # Strategy 1: Direct query
        strategies.append(f"top {number} {product} {query_type} in {region}")
        
        # Strategy 2: Industry directory
        strategies.append(f"{product} {query_type} {region} industry directory")
        
        # Strategy 3: B2B focused
        strategies.append(f"{product} {query_type} {region} B2B wholesale manufacturers")
        
        # Strategy 4: Company listing
        strategies.append(f"{product} companies {region} list exporters")
        
        # Strategy 5: Market leaders
        strategies.append(f"leading {product} {query_type} {region} market share")
        
        # Strategy 6: Regional specific
        strategies.append(f"{region} {product} {query_type} exporters producers")
        
        # Strategy 7: Trade-focused
        strategies.append(f"{product} {query_type} {region} trade export import")
        
        return strategies

    def _execute_search(self, query: str, max_results: int) -> List[Dict[str, Any]]:
        """Execute search using available provider"""
        if self.search_provider == 'serper':
            return self._search_serper(query, max_results)
        elif self.search_provider == 'google':
            return self._search_google(query, max_results)
        else:
            return []

    def _search_serper(self, query: str, max_results: int) -> List[Dict[str, Any]]:
        """Search using Serper API"""
        try:
            url = "https://google.serper.dev/search"
            payload = {"q": query, "num": max_results}
            headers = {
                'X-API-KEY': self.serper_api_key,
                'Content-Type': 'application/json'
            }
            
            response = requests.post(url, json=payload, headers=headers, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            results = []
            for item in data.get('organic', [])[:max_results]:
                results.append({
                    'title': item.get('title', ''),
                    'snippet': item.get('snippet', ''),
                    'link': item.get('link', ''),
                    'date': datetime.now().strftime('%Y-%m-%d'),
                    'source': item.get('source', 'Unknown'),
                    'search_engine': 'serper',
                    'query': query
                })
            
            return results
        except Exception as e:
            print(f"⚠️ Serper search failed: {e}")
            return []

    def _search_google(self, query: str, max_results: int) -> List[Dict[str, Any]]:
        """Search using Google Custom Search API"""
        try:
            url = "https://www.googleapis.com/customsearch/v1"
            params = {
                'key': self.google_api_key,
                'cx': self.google_cx,
                'q': query,
                'num': min(max_results, 10)
            }
            
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
                    'search_engine': 'google',
                    'query': query
                })
            
            return results
        except Exception as e:
            print(f"⚠️ Google search failed: {e}")
            return []

    def _deduplicate_results(self, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove duplicate results based on URL"""
        seen_urls = set()
        unique_results = []
        
        for result in results:
            url = result.get('link', '')
            if url and url not in seen_urls:
                seen_urls.add(url)
                unique_results.append(result)
        
        return unique_results

    def _rank_results(
        self,
        results: List[Dict[str, Any]],
        parsed: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Rank results based on relevance to query"""
        product = parsed['product'].lower()
        region = parsed['region']['specific_location'] or parsed['region']['country']
        region_lower = region.lower()
        
        for result in results:
            score = 0
            title_lower = result['title'].lower()
            snippet_lower = result['snippet'].lower()
            
            # Product mention in title (high weight)
            if product in title_lower:
                score += 10
            # Product mention in snippet
            if product in snippet_lower:
                score += 5
            
            # Region mention in title (high weight)
            if region_lower in title_lower:
                score += 10
            # Region mention in snippet
            if region_lower in snippet_lower:
                score += 5
            
            # Keywords indicating supplier/manufacturer
            supplier_keywords = ['supplier', 'manufacturer', 'exporter', 'producer', 'company', 'industry']
            for keyword in supplier_keywords:
                if keyword in title_lower:
                    score += 3
                if keyword in snippet_lower:
                    score += 2
            
            # B2B indicators
            b2b_keywords = ['b2b', 'wholesale', 'trade', 'directory', 'list']
            for keyword in b2b_keywords:
                if keyword in title_lower or keyword in snippet_lower:
                    score += 2
            
            result['relevance_score'] = score
        
        # Sort by relevance score
        return sorted(results, key=lambda x: x.get('relevance_score', 0), reverse=True)

    def _extract_supplier_info(
        self,
        results: List[Dict[str, Any]],
        parsed: Dict[str, Any]
    ) -> List[Dict[str, str]]:
        """Extract specific supplier names and information from results"""
        suppliers = []
        
        for result in results[:10]:  # Check top 10 results
            # Extract company names from title and snippet
            text = f"{result['title']} {result['snippet']}"
            
            # Pattern: Company names often appear with keywords
            patterns = [
                r'([A-Z][A-Za-z\s&]+(?:Ltd|Limited|Inc|Corp|Co|GmbH|BV|Sdn Bhd|Pte Ltd))',
                r'([A-Z][A-Za-z\s&]{3,30})\s+(?:is|are|offers|provides|supplies)',
            ]
            
            for pattern in patterns:
                matches = re.findall(pattern, text)
                for match in matches:
                    company_name = match.strip()
                    if len(company_name) > 3 and company_name not in [s['name'] for s in suppliers]:
                        suppliers.append({
                            'name': company_name,
                            'source': result['link'],
                            'snippet': result['snippet'][:200]
                        })
        
        return suppliers[:parsed['number']]

    def _format_intelligent_output(
        self,
        query: str,
        parsed: Dict[str, Any],
        results: List[Dict[str, Any]],
        extracted_suppliers: List[Dict[str, str]]
    ) -> str:
        """Format output in a readable way"""
        output = f"🔍 Intelligent Search Results for: {query}\n"
        output += "=" * 80 + "\n\n"
        
        # Show parsed query
        output += f"📊 Query Analysis:\n"
        output += f"   Product: {parsed['product']}\n"
        output += f"   Region: {parsed['region']['specific_location'] or parsed['region']['country']}\n"
        output += f"   Looking for: Top {parsed['number']} {parsed['query_type']}\n\n"
        
        # Show extracted suppliers
        if extracted_suppliers:
            output += f"🏢 Extracted Suppliers:\n"
            output += "-" * 80 + "\n"
            for i, supplier in enumerate(extracted_suppliers, 1):
                output += f"{i}. {supplier['name']}\n"
                output += f"   Source: {supplier['source']}\n"
                output += f"   Info: {supplier['snippet']}\n\n"
        
        # Show search results
        output += f"📰 Detailed Search Results ({len(results)} found):\n"
        output += "-" * 80 + "\n"
        for i, result in enumerate(results[:10], 1):
            output += f"{i}. {result['title']}\n"
            output += f"   Relevance Score: {result.get('relevance_score', 0)}/30\n"
            output += f"   Source: {result['source']}\n"
            output += f"   {result['snippet']}\n"
            output += f"   Link: {result['link']}\n\n"
        
        return output


# Example usage
if __name__ == "__main__":
    engine = IntelligentSearchEngine()
    
    print("=" * 80)
    print("🧠 INTELLIGENT SEARCH ENGINE TEST")
    print("=" * 80)
    
    # Test queries
    test_queries = [
        "Top 3 suppliers of Rice Bran Oil in Malaysia",
        "Best Vegetable Oil manufacturers in Mumbai, India",
        "Leading Palm Oil exporters in Indonesia",
        "Top 5 Sunflower Oil suppliers in Ukraine",
        "Rice Bran Oil suppliers in Penang, Malaysia",
        "Olive Oil manufacturers in Spain",
        "Top Coconut Oil exporters in Philippines",
        "Soybean Oil suppliers in Brazil",
        "Canola Oil manufacturers in Canada",
        "Palm Oil suppliers in Thailand"
    ]
    
    for query in test_queries[:3]:  # Test first 3
        print(f"\n\n{'='*80}")
        print(f"Query: {query}")
        print('='*80)
        
        result = engine.intelligent_search(query, max_results=5)
        print(result['formatted_output'])
