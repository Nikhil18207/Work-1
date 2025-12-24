"""
Application Settings and Configuration
"""

from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # OpenAI Configuration
    OPENAI_API_KEY: str
    OPENAI_MODEL: str = "gpt-4o"
    OPENAI_TEMPERATURE: float = 0.2
    OPENAI_MAX_TOKENS: int = 4000
    
    # Application Configuration
    APP_ENV: str = "development"
    APP_PORT: int = 8000
    APP_HOST: str = "0.0.0.0"
    LOG_LEVEL: str = "INFO"
    
    # Data Paths
    STRUCTURED_DATA_PATH: str = "./data/structured"
    UNSTRUCTURED_DATA_PATH: str = "./data/unstructured"
    CALCULATED_DATA_PATH: str = "./data/calculated"
    RULES_PATH: str = "./rules/rule_book.json"
    PROMPTS_PATH: str = "./config/prompts"
    
    # Confidence & Scoring Configuration
    MIN_CONFIDENCE_THRESHOLD: float = 0.60
    HIGH_CONFIDENCE_THRESHOLD: float = 0.85
    BASE_CONFIDENCE: float = 0.50
    
    # RAG Configuration
    VECTOR_DB_TYPE: str = "chromadb"
    CHROMA_PERSIST_DIRECTORY: str = "./data/vector_db"
    EMBEDDING_MODEL: str = "text-embedding-3-small"
    EMBEDDING_DIMENSION: int = 1536
    RAG_CHUNK_SIZE: int = 1000
    RAG_CHUNK_OVERLAP: int = 200
    RAG_TOP_K_RESULTS: int = 5
    RAG_SIMILARITY_THRESHOLD: float = 0.7
    
    # API Configuration
    RATE_LIMIT_REQUESTS: int = 100
    RATE_LIMIT_PERIOD: int = 60
    CORS_ORIGINS: str = "http://localhost:3000,http://localhost:8000"
    
    # Caching
    ENABLE_CACHE: bool = True
    CACHE_TTL_SECONDS: int = 3600
    CACHE_TYPE: str = "memory"
    
    # Monitoring
    ENABLE_MONITORING: bool = True
    ENABLE_TRACING: bool = True
    METRICS_PORT: int = 9090
    
    # Security
    API_KEY_REQUIRED: bool = False
    API_KEY: Optional[str] = None
    
    # Experimental Features
    ENABLE_EXPERIMENTAL_FEATURES: bool = True
    ENABLE_MULTI_MODEL_COMPARISON: bool = False
    ENABLE_CONFIDENCE_CALIBRATION: bool = True
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Global settings instance
settings = Settings()
