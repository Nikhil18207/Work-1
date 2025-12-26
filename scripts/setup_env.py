"""
Environment Setup Script
Creates .env file with proper configuration for Beroe Inc Supply Chain System
"""

import os
from pathlib import Path

def create_env_file():
    """Create .env file from template"""
    
    project_root = Path(__file__).parent
    env_file = project_root / '.env'
    env_example = project_root / '.env.example'
    
    # Check if .env already exists
    if env_file.exists():
        response = input("  .env file already exists. Overwrite? (y/N): ")
        if response.lower() != 'y':
            print(" Setup cancelled.")
            return
    
    print("=" * 80)
    print(" BEROE INC - SUPPLY CHAIN RECOMMENDATION SYSTEM")
    print("   Environment Setup")
    print("=" * 80)
    
    # Ask for LLM provider
    print("\n LLM CONFIGURATION")
    print("Choose your LLM provider:")
    print("  1. No LLM (Fallback mode) -  Works now, no API key needed")
    print("  2. OpenAI GPT-4 - Best quality, requires API key")
    print("  3. Google Gemini - Free tier available, requires API key")
    
    choice = input("\nEnter choice (1-3) [1]: ").strip() or "1"
    
    enable_llm = "false"
    llm_provider = "openai"
    openai_key = ""
    gemini_key = ""
    
    if choice == "2":
        enable_llm = "true"
        llm_provider = "openai"
        openai_key = input("Enter your OpenAI API key: ").strip()
    elif choice == "3":
        enable_llm = "true"
        llm_provider = "gemini"
        gemini_key = input("Enter your Gemini API key: ").strip()
    
    # Create .env content
    env_content = f"""# ============================================
# BEROE INC - SUPPLY CHAIN LLM RECOMMENDATION SYSTEM
# Environment Configuration

# Auto-generated: {Path(__file__).name}
# DO NOT COMMIT THIS FILE TO GIT

# LLM CONFIGURATION

LLM_PROVIDER={llm_provider}
ENABLE_LLM={enable_llm}

# OpenAI
OPENAI_API_KEY={openai_key}
OPENAI_MODEL=gpt-4
OPENAI_TEMPERATURE=0.7
OPENAI_MAX_TOKENS=2000

# Google Gemini
GEMINI_API_KEY={gemini_key}
GEMINI_MODEL=gemini-pro
GEMINI_TEMPERATURE=0.7

# APPLICATION CONFIGURATION

APP_ENV=development
APP_PORT=8000
APP_HOST=0.0.0.0
LOG_LEVEL=INFO

# DATA PATHS

STRUCTURED_DATA_PATH=./data/structured
UNSTRUCTURED_DATA_PATH=./data/unstructured
CALCULATED_DATA_PATH=./data/calculated
RULES_PATH=./data/structured/rule_book.csv
PROMPTS_PATH=./config/prompts

# RULE ENGINE CONFIGURATION

REGIONAL_CONCENTRATION_THRESHOLD=40.0
TAIL_SPEND_SUPPLIER_THRESHOLD=10
TAIL_SPEND_PERCENTAGE=20.0

# CONFIDENCE & SCORING

MIN_CONFIDENCE_THRESHOLD=0.60
HIGH_CONFIDENCE_THRESHOLD=0.85
BASE_CONFIDENCE=0.50

# VECTOR DATABASE

VECTOR_DB_TYPE=chromadb
CHROMA_PERSIST_DIRECTORY=./data/vector_db
EMBEDDING_MODEL=text-embedding-3-small
EMBEDDING_DIMENSION=1536

# RAG CONFIGURATION

RAG_CHUNK_SIZE=1000
RAG_CHUNK_OVERLAP=200
RAG_TOP_K_RESULTS=5
RAG_SIMILARITY_THRESHOLD=0.7

# API CONFIGURATION

RATE_LIMIT_REQUESTS=100
RATE_LIMIT_PERIOD=60
CORS_ORIGINS=http://localhost:3000,http://localhost:8000

# CACHING

ENABLE_CACHE=true
CACHE_TTL_SECONDS=3600
CACHE_TYPE=memory

# MONITORING

ENABLE_MONITORING=true
ENABLE_TRACING=true
METRICS_PORT=9090

# SECURITY

API_KEY_REQUIRED=false
API_KEY=

# EXPERIMENTAL FEATURES

ENABLE_EXPERIMENTAL_FEATURES=true
ENABLE_MULTI_MODEL_COMPARISON=false
ENABLE_CONFIDENCE_CALIBRATION=true

# SUPPLIER SELECTION WEIGHTS

ESG_SCORE_WEIGHT=0.30
PAYMENT_TERMS_WEIGHT=0.20
CAPACITY_WEIGHT=0.50
"""
    
    # Write .env file
    with open(env_file, 'w') as f:
        f.write(env_content)
    
    print("\n" + "=" * 80)
    print(" SUCCESS! .env file created")
    print("=" * 80)
    
    print(f"\n Location: {env_file}")
    print(f"\n Configuration:")
    print(f"   LLM Provider: {llm_provider}")
    print(f"   LLM Enabled: {enable_llm}")
    
    if enable_llm == "true":
        if llm_provider == "openai":
            print(f"   OpenAI Key: {' Set' if openai_key else ' Not set'}")
        else:
            print(f"   Gemini Key: {' Set' if gemini_key else ' Not set'}")
    
    print("\n NEXT STEPS:")
    print("   1. Test the system:")
    print("      python backend/demo_complete_system.py")
    print()
    if enable_llm == "false":
        print("   2. System is ready! (Using fallback mode - no API key needed)")
    else:
        print("   2. Test LLM integration:")
        print("      python backend/llm_recommendation_system.py")
    print()
    print("   3. View complete documentation:")
    print("      docs/SYSTEM_IMPLEMENTATION_COMPLETE.md")
    
    print("\n" + "=" * 80)


if __name__ == "__main__":
    create_env_file()
