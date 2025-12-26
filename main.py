import sys
import os
from pathlib import Path

root_path = Path(__file__).parent
sys.path.insert(0, str(root_path))

if "Beroe_Env" not in sys.executable:
    print("\n" + "!"*80)
    print("WARNING: YOU ARE NOT RUNNING IN THE 'Beroe_Env' VIRTUAL ENVIRONMENT!")
    print("Please run this command to start correctly:")
    print(f"   .\\Beroe_Env\\Scripts\\python {Path(__file__).name}")
    print("!"*80 + "\n")

from backend.conversational_ai import ConversationalAI

if __name__ == "__main__":
    print("\n" + "="*80)
    print("PROCUREMENT AI - CONVERSATIONAL ASSISTANT")
    print("="*80)
    print("\nACTIVE FEATURES:")
    print("   Data Analysis - Analyze your procurement data")
    print("   Web Search - Find suppliers & market intelligence")
    print("   RAG - Knowledge base queries (OpenAI)")
    print("   AI Reasoning - GPT-4 powered insights")
    print("\n" + "="*80 + "\n")
    
    ai = ConversationalAI(
        enable_llm=True,
        enable_rag=True,
        enable_web_search=True,
        llm_provider="openai"
    )
    
    print("\nTRY THESE QUESTIONS:")
    print("   - What are the risks?")
    print("   - Show me the spend breakdown")
    print("   - Find top Rice Bran Oil suppliers in India")
    print("   - Recommend suppliers")
    print("   - What's our regional distribution?")
    print("\n" + "="*80 + "\n")
    
    ai.chat()
