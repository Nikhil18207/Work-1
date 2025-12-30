"""
Conversational AI Demo for Supplier Coaching System
Chat naturally and get personalized supplier coaching!
"""

import sys
from pathlib import Path

root_path = Path(__file__).parent.parent
if str(root_path) not in sys.path:
    sys.path.insert(0, str(root_path))

from backend.conversational_ai import ConversationalAI


def print_banner():
    """Print welcome banner"""
    print("\n" + "=" * 80)
    print("  🤖 SUPPLIER COACHING CONVERSATIONAL AI")
    print("  Chat naturally about your supplier challenges!")
    print("=" * 80)
    print("\nExamples of what you can ask:")
    print("  • 'Analyze my Rice Bran Oil suppliers'")
    print("  • 'I want to reduce concentration risk'")
    print("  • 'Find new regions for sourcing'")
    print("  • 'Should I expand with my current suppliers?'")
    print("  • 'What are the market trends for Rice Bran Oil?'")
    print("\nType 'exit' or 'quit' to end the conversation")
    print("=" * 80 + "\n")


def main():
    """Run conversational AI demo"""
    print_banner()
    
    # Initialize conversational AI
    print("Initializing AI system...")
    ai = ConversationalAI()
    print("✓ AI ready! Start chatting...\n")
    
    # Sample questions to get started
    sample_questions = [
        "Analyze my spend for Rice Bran Oil",
        "What are my supplier concentration risks?",
        "Find new regions for sourcing Rice Bran Oil",
        "Should I expand with existing suppliers?",
        "What's the current market situation?"
    ]
    
    print("💡 Quick start - Try one of these:")
    for i, q in enumerate(sample_questions, 1):
        print(f"   {i}. {q}")
    print()
    
    # Chat loop
    conversation_count = 0
    
    while True:
        try:
            # Get user input
            user_input = input("You: ").strip()
            
            if not user_input:
                continue
            
            # Check for exit
            if user_input.lower() in ['exit', 'quit', 'bye', 'goodbye']:
                print("\n👋 Thanks for using the Supplier Coaching AI!")
                print(f"   Total questions answered: {conversation_count}")
                print("   All conversation history is saved in memory.\n")
                break
            
            # Check for quick start numbers
            if user_input.isdigit() and 1 <= int(user_input) <= len(sample_questions):
                user_input = sample_questions[int(user_input) - 1]
                print(f"You: {user_input}")
            
            # Get AI response
            print("\n🤖 AI: ", end="", flush=True)
            response = ai.answer_question(user_input)
            print(response)
            print()
            
            conversation_count += 1
            
            # Show conversation stats every 5 questions
            if conversation_count % 5 == 0:
                print(f"   📊 {conversation_count} questions answered so far")
                print()
            
        except KeyboardInterrupt:
            print("\n\n👋 Interrupted. Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ Error: {str(e)}")
            print("Please try again or type 'exit' to quit.\n")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n❌ Fatal error: {str(e)}")
        import traceback
        traceback.print_exc()
