"""
LLM Recommendation System - Main Application Entry Point
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger
import uvicorn

from backend.api.routes import recommendation_router
from backend.config.settings import settings

# Initialize FastAPI app
app = FastAPI(
    title="LLM Recommendation System",
    description="AI-powered procurement recommendation system for food industry",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS.split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(recommendation_router, prefix="/api/v1", tags=["recommendations"])


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "LLM Recommendation System",
        "version": "1.0.0"
    }


@app.get("/health")
async def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "components": {
            "api": "operational",
            "database": "operational",
            "vector_db": "operational",
            "llm": "operational"
        }
    }


if __name__ == "__main__":
    logger.info(f"Starting LLM Recommendation System on {settings.APP_HOST}:{settings.APP_PORT}")
    uvicorn.run(
        "main:app",
        host=settings.APP_HOST,
        port=settings.APP_PORT,
        reload=settings.APP_ENV == "development"
    )
