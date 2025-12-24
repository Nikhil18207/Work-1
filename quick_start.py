"""
Quick Start - Conversational AI
Start chatting without RAG setup (uses data + web search + LLM)
"""

import sys
from pathlib import Path

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.conversational_ai import ConversationalAI

if __name__ == "__main__":
    print("\n" + "="*80)
    print("🚀 QUICK START - CONVERSATIONAL AI")
    print("="*80)
    print("\nStarting with:")
    print("  ✅ Data Analysis (your CSV files)")
    print("  ✅ Web Search (live market intelligence)")
    print("  ✅ LLM Reasoning (AI-powered)")
    print("  ⚠️  RAG disabled (run setup_rag.py to enable)")
    print("\n" + "="*80 + "\n")
    
    # Initialize without RAG for quick start
    ai = ConversationalAI(
        enable_llm=True,
        enable_rag=False,        # Disable RAG for now
        enable_web_search=True
    )
    
    # Start chat
    ai.chat()
