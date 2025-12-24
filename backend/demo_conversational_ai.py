"""
Conversational AI Demo
Shows example conversations with the AI
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from conversational_ai import ConversationalAI


def demo_conversation():
    """Demonstrate the conversational AI with example questions"""
    
    print("=" * 80)
    print("🤖 CONVERSATIONAL AI - DEMO")
    print("=" * 80)
    print("\nInitializing AI...\n")
    
    # Initialize AI
    ai = ConversationalAI(enable_llm=False)
    
    # Example questions
    questions = [
        "What are the biggest risks?",
        "Recommend some suppliers",
        "Show me the spend breakdown",
        "Which regions are we buying from?",
        "What actions should we take?",
        "Tell me about ESG scores",
        "How long will this take?",
        "What are the business rules?"
    ]
    
    print("\n" + "=" * 80)
    print("DEMO CONVERSATION")
    print("=" * 80 + "\n")
    
    for question in questions:
        print(f"👤 You: {question}")
        print()
        
        answer = ai.answer_question(question)
        print(f"🤖 AI:\n{answer}")
        print("\n" + "-" * 80 + "\n")
    
    print("=" * 80)
    print("✅ DEMO COMPLETE!")
    print("=" * 80)
    print("\nTo start your own conversation, run:")
    print("  python backend/conversational_ai.py")
    print()


if __name__ == "__main__":
    demo_conversation()
