"""
🚀 QUICK START - Universal Sourcing Optimization System
Run this file to start asking questions!
"""

import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.conversational_ai import ConversationalAI


def main():
    """Start the interactive AI assistant"""
    
    print("\n" + "="*80)
    print("🚀 UNIVERSAL SOURCING OPTIMIZATION SYSTEM")
    print("="*80)
    print("\n✅ Handles ALL 35 Procurement Rules (R001-R035)")
    print("✅ Dynamic Strategy Selection")
    print("✅ Data-Driven Recommendations")
    print("✅ Natural Language Understanding")
    print("\n" + "="*80)
    
    print("\n📋 What You Can Ask:")
    print("  • 'Is my regional concentration too high?'")
    print("  • 'How can I diversify my supplier base?'")
    print("  • 'What rules am I violating?'")
    print("  • 'Show me top 3 recommendations'")
    print("  • 'What's my spend on Rice Bran Oil?'")
    print("  • ... and much more!")
    
    print("\n" + "="*80)
    print("💡 TIP: Ask in plain English - the AI understands context!")
    print("="*80 + "\n")
    
    # Initialize AI
    print("🔄 Initializing AI System...\n")
    
    try:
        ai = ConversationalAI(
            enable_llm=True,
            enable_rag=True,
            enable_web_search=True
        )
        
        print("✅ System Ready!\n")
        print("="*80)
        print("💬 START ASKING QUESTIONS")
        print("="*80)
        print("\nType 'exit' or 'quit' to end the session\n")
        
        # Start interactive chat
        ai.chat()
        
    except Exception as e:
        print(f"\n❌ Error initializing system: {e}")
        print("\n💡 Make sure you've activated the virtual environment:")
        print("   f:/Work Terminal/Beroe Inc/Beroe_Env/Scripts/Activate.ps1")
        return


if __name__ == "__main__":
    main()
