"""
Semantic Query Analyzer
Advanced natural language understanding for procurement queries
Uses LLM to understand intent, extract entities, and route to appropriate engines
"""

import os
from typing import Dict, List, Any, Optional, Tuple
from enum import Enum
import json
from dotenv import load_dotenv

load_dotenv()

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None


class QueryIntent(Enum):
    """Types of query intents"""
    DATA_ANALYSIS = "data_analysis"           # Analyze existing data (spend, suppliers, etc.)
    KNOWLEDGE_BASE = "knowledge_base"         # Query policies, contracts, best practices
    WEB_SEARCH = "web_search"                 # Find external information (suppliers, news, prices)
    RECOMMENDATION = "recommendation"         # Get procurement recommendations
    COMPARISON = "comparison"                 # Compare suppliers, products, regions
    TREND_ANALYSIS = "trend_analysis"         # Analyze trends over time
    RISK_ASSESSMENT = "risk_assessment"       # Assess risks
    COMPLIANCE_CHECK = "compliance_check"     # Check rule compliance
    GENERAL_QUESTION = "general_question"     # General procurement questions


class EntityType(Enum):
    """Types of entities in queries"""
    PRODUCT_CATEGORY = "product_category"
    SUPPLIER = "supplier"
    CLIENT = "client"
    REGION = "region"
    TIME_PERIOD = "time_period"
    METRIC = "metric"
    CERTIFICATION = "certification"
    QUANTITY = "quantity"
    PRICE = "price"


class SemanticQueryAnalyzer:
    """
    Advanced semantic query analyzer that:
    1. Understands natural language queries in any form
    2. Extracts intent, entities, and context
    3. Routes to appropriate engines
    4. Generates optimized sub-queries for each engine
    """
    
    def __init__(self, enable_llm: bool = True):
        """
        Initialize semantic query analyzer
        
        Args:
            enable_llm: Use LLM for advanced understanding
        """
        self.enable_llm = enable_llm
        self.client = None
        
        if enable_llm and OpenAI:
            api_key = os.getenv("OPENAI_API_KEY")
            if api_key:
                self.client = OpenAI(api_key=api_key)
    
    def analyze_query(self, query: str, conversation_context: Optional[str] = None) -> Dict[str, Any]:
        """
        Analyze query to understand intent, entities, and routing
        
        Args:
            query: User's natural language query
            conversation_context: Previous conversation context
            
        Returns:
            Analysis with intent, entities, routing strategy, and sub-queries
        """
        if self.client and self.enable_llm:
            return self._analyze_with_llm(query, conversation_context)
        else:
            return self._analyze_with_patterns(query)
    
    def _analyze_with_llm(self, query: str, conversation_context: Optional[str] = None) -> Dict[str, Any]:
        """
        Use LLM for deep semantic understanding
        """
        system_prompt = """You are a semantic query analyzer for a procurement AI system.

Your job is to analyze user queries and extract:
1. PRIMARY INTENT - What the user wants to do
2. ENTITIES - Key information (products, suppliers, regions, metrics, etc.)
3. ROUTING STRATEGY - Which data sources to use
4. SUB-QUERIES - Optimized queries for each engine

AVAILABLE DATA SOURCES:
- STRUCTURED DATA: CSV files with spend data, supplier info, client data, pricing benchmarks
- RAG/KNOWLEDGE BASE: Policies, contracts, best practices, historical documents
- WEB SEARCH: Real-time supplier search, market intelligence, news, price trends

QUERY INTENTS:
- data_analysis: Analyze existing data (e.g., "What's our spend?", "Show supplier breakdown")
- knowledge_base: Query policies/contracts (e.g., "What are our quality requirements?")
- web_search: Find external info (e.g., "Find suppliers in India", "Latest oil prices")
- recommendation: Get recommendations (e.g., "Recommend a supplier for...")
- comparison: Compare options (e.g., "Compare suppliers A vs B")
- trend_analysis: Analyze trends (e.g., "How has spend changed?")
- risk_assessment: Assess risks (e.g., "What are the risks?")
- compliance_check: Check compliance (e.g., "Does this meet our rules?")

ENTITY TYPES:
- product_category: Rice Bran Oil, IT Hardware, Cloud Services, etc.
- supplier: Supplier names or IDs
- client: Client names or IDs
- region: Countries, states, cities (Malaysia, India, Mumbai, APAC, etc.)
- time_period: Dates, months, quarters, years
- metric: Spend, savings, quality, delivery, sustainability, etc.
- certification: ISO 22000, HACCP, RSPO, etc.
- quantity: Amounts (50000 kg, 100 units, etc.)
- price: Price values or ranges

RESPOND IN JSON FORMAT:
{
  "primary_intent": "data_analysis|knowledge_base|web_search|recommendation|comparison|trend_analysis|risk_assessment|compliance_check",
  "confidence": 0.95,
  "entities": {
    "product_category": ["Rice Bran Oil"],
    "region": ["Malaysia"],
    "metric": ["spend", "total"],
    "time_period": ["2024"],
    "supplier": [],
    "client": [],
    "certification": [],
    "quantity": [],
    "price": []
  },
  "routing_strategy": {
    "use_structured_data": true,
    "use_rag": false,
    "use_web_search": false,
    "priority_order": ["structured_data"]
  },
  "sub_queries": {
    "structured_data_query": "Filter spend_data.csv by Category='Rice Bran Oil' and sum Spend_USD",
    "rag_query": null,
    "web_search_query": null
  },
  "query_type": "aggregation|filter|search|recommendation|comparison",
  "expected_answer_type": "numeric|list|explanation|recommendation",
  "context_needed": ["spend_data", "supplier_master"],
  "reasoning": "User wants total spend for Rice Bran Oil. This requires analyzing structured spend data."
}

EXAMPLES:

Query: "What's our total spend on Rice Bran Oil?"
{
  "primary_intent": "data_analysis",
  "confidence": 0.98,
  "entities": {
    "product_category": ["Rice Bran Oil"],
    "metric": ["spend", "total"]
  },
  "routing_strategy": {
    "use_structured_data": true,
    "use_rag": false,
    "use_web_search": false,
    "priority_order": ["structured_data"]
  },
  "sub_queries": {
    "structured_data_query": "Sum all Spend_USD where Category='Rice Bran Oil'",
    "rag_query": null,
    "web_search_query": null
  },
  "query_type": "aggregation",
  "expected_answer_type": "numeric",
  "reasoning": "Direct data aggregation query"
}

Query: "Find top Rice Bran Oil suppliers in Malaysia"
{
  "primary_intent": "web_search",
  "confidence": 0.95,
  "entities": {
    "product_category": ["Rice Bran Oil"],
    "region": ["Malaysia"]
  },
  "routing_strategy": {
    "use_structured_data": true,
    "use_rag": false,
    "use_web_search": true,
    "priority_order": ["web_search", "structured_data"]
  },
  "sub_queries": {
    "structured_data_query": "Filter supplier_master.csv by product_category='Edible Oils' AND country='Malaysia'",
    "rag_query": null,
    "web_search_query": "top rice bran oil suppliers Malaysia manufacturers exporters"
  },
  "query_type": "search",
  "expected_answer_type": "list",
  "reasoning": "External supplier search with internal data validation"
}

Query: "What are our quality requirements for food suppliers?"
{
  "primary_intent": "knowledge_base",
  "confidence": 0.97,
  "entities": {
    "product_category": ["Food"],
    "metric": ["quality requirements"]
  },
  "routing_strategy": {
    "use_structured_data": false,
    "use_rag": true,
    "use_web_search": false,
    "priority_order": ["rag"]
  },
  "sub_queries": {
    "structured_data_query": null,
    "rag_query": "quality requirements food suppliers certifications standards",
    "web_search_query": null
  },
  "query_type": "search",
  "expected_answer_type": "explanation",
  "reasoning": "Policy/requirements query from knowledge base"
}

Query: "Recommend a supplier for 50000 kg sunflower oil"
{
  "primary_intent": "recommendation",
  "confidence": 0.99,
  "entities": {
    "product_category": ["Sunflower Oil"],
    "quantity": ["50000 kg"]
  },
  "routing_strategy": {
    "use_structured_data": true,
    "use_rag": true,
    "use_web_search": false,
    "priority_order": ["structured_data", "rag"]
  },
  "sub_queries": {
    "structured_data_query": "Find suppliers with product_category='Edible Oils', evaluate quality, pricing, delivery",
    "rag_query": "supplier selection criteria quality certifications",
    "web_search_query": null
  },
  "query_type": "recommendation",
  "expected_answer_type": "recommendation",
  "reasoning": "Recommendation requires data analysis + policy compliance"
}

Now analyze the user's query."""

        user_message = f"Query: {query}"
        if conversation_context:
            user_message += f"\n\nConversation Context:\n{conversation_context}"
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ],
                temperature=0.1,
                response_format={"type": "json_object"}
            )
            
            analysis = json.loads(response.choices[0].message.content)
            
            # Add original query
            analysis["original_query"] = query
            
            return analysis
            
        except Exception as e:
            print(f"LLM analysis failed: {e}")
            return self._analyze_with_patterns(query)
    
    def _analyze_with_patterns(self, query: str) -> Dict[str, Any]:
        """
        Fallback pattern-based analysis
        """
        query_lower = query.lower()
        
        # Detect intent
        intent = QueryIntent.DATA_ANALYSIS
        if any(word in query_lower for word in ["find", "search", "top", "best", "suppliers in"]):
            intent = QueryIntent.WEB_SEARCH
        elif any(word in query_lower for word in ["policy", "requirement", "rule", "contract", "compliance"]):
            intent = QueryIntent.KNOWLEDGE_BASE
        elif any(word in query_lower for word in ["recommend", "suggest", "should i"]):
            intent = QueryIntent.RECOMMENDATION
        elif any(word in query_lower for word in ["compare", "vs", "versus", "difference"]):
            intent = QueryIntent.COMPARISON
        elif any(word in query_lower for word in ["risk", "risky", "danger", "concern"]):
            intent = QueryIntent.RISK_ASSESSMENT
        
        # Extract basic entities
        entities = {
            "product_category": [],
            "region": [],
            "metric": [],
            "supplier": [],
            "client": [],
            "time_period": [],
            "certification": [],
            "quantity": [],
            "price": []
        }
        
        # Simple pattern matching for common categories
        categories = ["rice bran oil", "sunflower oil", "palm oil", "it hardware", "cloud services"]
        for cat in categories:
            if cat in query_lower:
                entities["product_category"].append(cat.title())
        
        # Detect metrics
        metrics = ["spend", "cost", "price", "quality", "delivery", "sustainability", "risk"]
        for metric in metrics:
            if metric in query_lower:
                entities["metric"].append(metric)
        
        return {
            "original_query": query,
            "primary_intent": intent.value,
            "confidence": 0.7,
            "entities": entities,
            "routing_strategy": {
                "use_structured_data": intent in [QueryIntent.DATA_ANALYSIS, QueryIntent.RECOMMENDATION],
                "use_rag": intent in [QueryIntent.KNOWLEDGE_BASE, QueryIntent.COMPLIANCE_CHECK],
                "use_web_search": intent == QueryIntent.WEB_SEARCH,
                "priority_order": ["structured_data"]
            },
            "sub_queries": {
                "structured_data_query": query,
                "rag_query": query if intent == QueryIntent.KNOWLEDGE_BASE else None,
                "web_search_query": query if intent == QueryIntent.WEB_SEARCH else None
            },
            "query_type": "general",
            "expected_answer_type": "explanation",
            "context_needed": [],
            "reasoning": "Pattern-based analysis (LLM not available)"
        }
    
    def generate_execution_plan(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate detailed execution plan based on analysis
        
        Args:
            analysis: Query analysis result
            
        Returns:
            Execution plan with steps and engine calls
        """
        plan = {
            "steps": [],
            "parallel_execution": [],
            "sequential_execution": [],
            "expected_output": analysis.get("expected_answer_type", "explanation")
        }
        
        routing = analysis.get("routing_strategy", {})
        sub_queries = analysis.get("sub_queries", {})
        
        # Build execution steps
        if routing.get("use_structured_data"):
            plan["steps"].append({
                "step": 1,
                "engine": "data_loader",
                "action": "load_and_analyze",
                "query": sub_queries.get("structured_data_query"),
                "priority": "high"
            })
        
        if routing.get("use_rag"):
            plan["steps"].append({
                "step": 2,
                "engine": "rag_engine",
                "action": "semantic_search",
                "query": sub_queries.get("rag_query"),
                "priority": "medium"
            })
        
        if routing.get("use_web_search"):
            plan["steps"].append({
                "step": 3,
                "engine": "intelligent_search_engine",
                "action": "web_search",
                "query": sub_queries.get("web_search_query"),
                "priority": "medium"
            })
        
        # Determine parallel vs sequential
        if len(plan["steps"]) > 1:
            # RAG and Web Search can run in parallel
            plan["parallel_execution"] = [s for s in plan["steps"] if s["engine"] in ["rag_engine", "intelligent_search_engine"]]
            plan["sequential_execution"] = [s for s in plan["steps"] if s["engine"] == "data_loader"]
        else:
            plan["sequential_execution"] = plan["steps"]
        
        return plan
    
    def format_analysis_summary(self, analysis: Dict[str, Any]) -> str:
        """
        Format analysis as human-readable summary
        """
        lines = []
        lines.append("=" * 70)
        lines.append("SEMANTIC QUERY ANALYSIS")
        lines.append("=" * 70)
        lines.append(f"\nOriginal Query: {analysis.get('original_query', 'N/A')}")
        lines.append(f"\nPrimary Intent: {analysis.get('primary_intent', 'N/A').upper()}")
        lines.append(f"Confidence: {analysis.get('confidence', 0) * 100:.1f}%")
        
        # Entities
        entities = analysis.get('entities', {})
        if any(entities.values()):
            lines.append("\nExtracted Entities:")
            for entity_type, values in entities.items():
                if values:
                    lines.append(f"  • {entity_type}: {', '.join(map(str, values))}")
        
        # Routing
        routing = analysis.get('routing_strategy', {})
        lines.append("\nRouting Strategy:")
        lines.append(f"  • Structured Data: {'✓' if routing.get('use_structured_data') else '✗'}")
        lines.append(f"  • Knowledge Base (RAG): {'✓' if routing.get('use_rag') else '✗'}")
        lines.append(f"  • Web Search: {'✓' if routing.get('use_web_search') else '✗'}")
        
        # Sub-queries
        sub_queries = analysis.get('sub_queries', {})
        if any(sub_queries.values()):
            lines.append("\nGenerated Sub-Queries:")
            for engine, query in sub_queries.items():
                if query:
                    lines.append(f"  • {engine}: {query}")
        
        # Reasoning
        if analysis.get('reasoning'):
            lines.append(f"\nReasoning: {analysis['reasoning']}")
        
        lines.append("=" * 70)
        
        return "\n".join(lines)


# Example usage
if __name__ == "__main__":
    analyzer = SemanticQueryAnalyzer(enable_llm=True)
    
    test_queries = [
        "What's our total spend on Rice Bran Oil?",
        "Find me the top 5 suppliers of sunflower oil in Malaysia",
        "What are our quality requirements for food suppliers?",
        "Recommend a supplier for 50000 kg of palm oil",
        "Compare suppliers S001 and S002",
        "What are the risks with our current supplier concentration?",
        "Show me spend breakdown by region",
        "Latest market prices for vegetable oils in Asia"
    ]
    
    for query in test_queries:
        print("\n" + "=" * 70)
        print(f"QUERY: {query}")
        print("=" * 70)
        
        analysis = analyzer.analyze_query(query)
        print(analyzer.format_analysis_summary(analysis))
        
        plan = analyzer.generate_execution_plan(analysis)
        print(f"\nExecution Plan: {len(plan['steps'])} steps")
        for step in plan['steps']:
            print(f"  {step['step']}. {step['engine']} - {step['action']}")
