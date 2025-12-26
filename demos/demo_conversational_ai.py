"""
Conversational AI Demo
Shows the full conversational capabilities with RAG and web search
"""

import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.conversational_ai import ConversationalAI


def demo_conversational_ai():
    """Demonstrate conversational AI capabilities"""
    
    print("\n" + "="*80)
    print(" CONVERSATIONAL AI DEMONSTRATION")
    print("="*80)
    print("\nThis demo shows the AI answering different types of questions:")
    print("  1. Data-specific questions (from your CSV files)")
    print("  2. Knowledge base questions (from policies/documents)")
    print("  3. Market intelligence (from web search)")
    print("\n" + "="*80 + "\n")
    
    # Initialize AI with all features
    print("Initializing Conversational AI...\n")
    ai = ConversationalAI(
        enable_llm=True,
        enable_rag=True,
        enable_web_search=True
    )
    
    # Demo questions
    demo_questions = [
        # Data-specific questions
        {
            "category": " Data Analysis",
            "questions": [
                "What are the risks?",
                "Show me the spend breakdown",
                "Tell me about regional distribution"
            ]
        },
        # Knowledge base questions
        {
            "category": " Knowledge Base (RAG)",
            "questions": [
                "What is our supplier selection policy?",
                "What are the quality requirements?",
                "What are the ESG criteria?"
            ]
        },
        # Market intelligence questions
        {
            "category": " Live Market Intelligence",
            "questions": [
                "Find top Rice Bran Oil suppliers in India",
                "What's the latest news about palm oil market?",
                "Search for sustainable packaging suppliers"
            ]
        }
    ]
    
    # Run demo
    for category_info in demo_questions:
        print("\n" + "="*80)
        print(f"{category_info['category']}")
        print("="*80)
        
        for question in category_info['questions']:
            print(f"\n{''*80}")
            print(f" You: {question}")
            print(f"{''*80}")
            
            try:
                answer = ai.answer_question(question)
                print(f"\n AI:\n{answer}")
            except Exception as e:
                print(f"\n Error: {e}")
            
            print()
    
    # Interactive mode
    print("\n" + "="*80)
    print(" INTERACTIVE MODE")
    print("="*80)
    print("\nNow you can ask your own questions!")
    print("The AI will automatically route to the best source (data/RAG/web).\n")
    
    # Start interactive chat
    ai.chat()


if __name__ == "__main__":
    demo_conversational_ai()
