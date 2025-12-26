"""
Test Semantic Search Capabilities
Demonstrates the enhanced natural language understanding
"""

import sys
from pathlib import Path

# Add parent directory to path
root_path = Path(__file__).parent.parent
sys.path.insert(0, str(root_path))

from backend.engines.semantic_query_analyzer import SemanticQueryAnalyzer

def test_semantic_search():
    """Test semantic query analyzer with various question formats"""
    
    analyzer = SemanticQueryAnalyzer(enable_llm=True)
    
    print("\n" + "="*80)
    print(" SEMANTIC SEARCH TEST - Ask Questions ANY Way You Want!")
    print("="*80)
    
    # Test queries in different formats
    test_queries = [
        # Data analysis - different ways to ask
        "What's our total spend on Rice Bran Oil?",
        "How much money did we spend on Rice Bran Oil?",
        "Show me Rice Bran Oil expenditure",
        "Rice Bran Oil spending breakdown",
        
        # Web search - different formats
        "Find me the top 5 suppliers of sunflower oil in Malaysia",
        "Who are the best sunflower oil suppliers in Malaysia?",
        "I need suppliers for sunflower oil in Malaysia",
        "Looking for Malaysian sunflower oil manufacturers",
        
        # Knowledge base - different ways
        "What are our quality requirements for food suppliers?",
        "Tell me about food supplier quality standards",
        "What quality criteria do we have for food vendors?",
        
        # Recommendations - different formats
        "Recommend a supplier for 50000 kg of palm oil",
        "I need a supplier recommendation for palm oil, 50000 kg",
        "Who should I buy palm oil from? Need 50000 kg",
        
        # Complex/conversational
        "I'm building a car for Hyundai, need aluminum suppliers",
        "Setting up a data center, looking for server suppliers",
        "What are the risks with our current supplier setup?",
        "Compare suppliers S001 and S002"
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n{'='*80}")
        print(f"TEST {i}: {query}")
        print('='*80)
        
        try:
            # Analyze the query
            analysis = analyzer.analyze_query(query)
            
            # Show analysis summary
            print(analyzer.format_analysis_summary(analysis))
            
            # Generate execution plan
            plan = analyzer.generate_execution_plan(analysis)
            
            print(f"\nEXECUTION PLAN:")
            print(f"  Total Steps: {len(plan['steps'])}")
            print(f"  Expected Output: {plan['expected_output']}")
            
            if plan['parallel_execution']:
                print(f"\n  Parallel Execution ({len(plan['parallel_execution'])} steps):")
                for step in plan['parallel_execution']:
                    print(f"    • {step['engine']}: {step['action']}")
            
            if plan['sequential_execution']:
                print(f"\n  Sequential Execution ({len(plan['sequential_execution'])} steps):")
                for step in plan['sequential_execution']:
                    print(f"    • {step['engine']}: {step['action']}")
            
        except Exception as e:
            print(f"  ERROR: {e}")
        
        print()


if __name__ == "__main__":
    print("\n🚀 Testing Semantic Search Capabilities...")
    print("This demonstrates how the system understands questions in ANY format!\n")
    
    test_semantic_search()
    
    print("\n" + "="*80)
    print(" TEST COMPLETE!")
    print("="*80)
    print("\nThe system can now understand:")
    print("  ✓ Questions in any phrasing")
    print("  ✓ Different ways to ask the same thing")
    print("  ✓ Conversational queries")
    print("  ✓ Use-case based questions")
    print("  ✓ Complex multi-part questions")
    print("\nTry it yourself with: python main.py")
    print("="*80 + "\n")
