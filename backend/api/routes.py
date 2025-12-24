"""
API Routes for Recommendation System
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from loguru import logger

from backend.conversational_ai import ConversationalAI

recommendation_router = APIRouter()

# Initialize AI Engine (RAG will be enabled if setup_rag.py was run)
ai_assistant = ConversationalAI(
    enable_llm=True,
    enable_rag=True,
    enable_web_search=True
)


class RecommendationRequest(BaseModel):
    """Request model for procurement recommendation"""
    query: str
    client_id: Optional[str] = None
    product_category: Optional[str] = None
    quantity_kg: Optional[float] = None
    additional_context: Optional[Dict[str, Any]] = None


class ChatRequest(BaseModel):
    """Request model for AI chat"""
    message: str


class ChatResponse(BaseModel):
    """Response model for AI chat"""
    answer: str


class RecommendationResponse(BaseModel):
    """Response model for procurement recommendation"""
    recommendation: Dict[str, Any]
    confidence_score: float
    confidence_explanation: Dict[str, Any]
    pricing_analysis: Dict[str, Any]
    quality_assessment: Dict[str, Any]
    risk_assessment: Dict[str, Any]
    sustainability_assessment: Dict[str, Any]
    rule_compliance: Dict[str, Any]
    data_sources: Dict[str, List[str]]
    reasoning: str
    next_steps: List[str]
    alternative_suppliers: Optional[List[Dict[str, Any]]] = None


@recommendation_router.post("/chat", response_model=ChatResponse)
async def chat_with_ai(request: ChatRequest):
    """
    Endpoint for conversational AI chat
    Routes to RAG, Web Search, or Data Analysis as needed
    """
    try:
        answer = ai_assistant.answer_question(request.message)
        return ChatResponse(answer=answer)
    except Exception as e:
        logger.error(f"Error in chat: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@recommendation_router.post("/query-knowledge", response_model=ChatResponse)
async def query_knowledge_base(request: ChatRequest):
    """
    Specifically query the RAG knowledge base (policies, contracts, etc.)
    """
    try:
        if not ai_assistant.rag_engine:
            raise HTTPException(status_code=400, detail="RAG engine not initialized. Run setup_rag.py first.")
        
        # Use RAG directly
        result = ai_assistant.rag_engine.query(request.message)
        return ChatResponse(answer=result['answer'])
    except Exception as e:
        logger.error(f"Error querying knowledge base: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@recommendation_router.post("/recommend", response_model=RecommendationResponse)
async def get_recommendation(request: RecommendationRequest):
    """
    Generate procurement recommendation based on query
    """
    # This remains linked to the recommendation system
    # (Existing placeholder implementation)
    try:
        logger.info(f"Received recommendation request: {request.query}")
        
        return RecommendationResponse(
            recommendation={
                "supplier_id": "S001",
                "supplier_name": "Golden Sun Oils Ltd",
                "product": "Sunflower Oil",
                "quantity_kg": 50000,
                "unit_price_usd": 2.45,
                "total_cost_usd": 122500
            },
            confidence_score=0.78,
            confidence_explanation={
                "current_confidence": "78%",
                "reasoning": "Based on available data",
                "data_completeness": "85%",
                "missing_data_impact": [],
                "maximum_achievable_confidence": "92%"
            },
            pricing_analysis={
                "quoted_price": 2.45,
                "benchmark_price": 2.55,
                "price_deviation_pct": -3.9,
                "savings_vs_benchmark": 5000,
                "savings_pct": 3.9
            },
            quality_assessment={
                "quality_rating": 4.5,
                "certifications": ["ISO 22000", "RSPO", "Halal"],
                "delivery_reliability": "95%"
            },
            risk_assessment={
                "overall_risk_level": "LOW",
                "risks_identified": []
            },
            sustainability_assessment={
                "sustainability_score": 8.5,
                "certifications": ["RSPO"]
            },
            rule_compliance={
                "hard_constraints_satisfied": True,
                "soft_preferences_score": 85
            },
            data_sources={
                "structured_data": ["supplier_master.csv", "pricing_benchmarks.csv"],
                "unstructured_data": ["procurement_policy.md"],
                "calculated_data": ["savings_calculation"]
            },
            reasoning="RAG integrated. You can now use /chat for conversational queries.",
            next_steps=[
                "1. Data loading modules active",
                "2. RAG pipeline active (use /chat for policies)",
                "3. Intelligent search active (use /chat for market info)",
                "4. Rule engine loaded with 35 rules"
            ]
        )
        
    except Exception as e:
        logger.error(f"Error generating recommendation: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@recommendation_router.get("/suppliers")
async def list_suppliers():
    """List all available suppliers"""
    return {"message": "Supplier listing - implementation pending"}


@recommendation_router.get("/clients")
async def list_clients():
    """List all clients"""
    return {"message": "Client listing - implementation pending"}


@recommendation_router.get("/benchmarks/{product_category}")
async def get_benchmarks(product_category: str):
    """Get pricing benchmarks for a product category"""
    return {"message": f"Benchmarks for {product_category} - implementation pending"}
