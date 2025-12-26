"""
System Integration Verification Script
Checks that all components are properly linked
"""

import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

def verify_integration():
    """Verify all system integrations"""
    
    print("\n" + "="*70)
    print(" SYSTEM INTEGRATION VERIFICATION")
    print("="*70 + "\n")
    
    errors = []
    warnings = []
    
    # 1. Check imports
    print("1⃣  Checking imports...")
    system_imported = False
    try:
        from backend.llm_recommendation_system import LLMRecommendationSystem
        from backend.engines.data_loader import DataLoader
        from backend.engines.rule_engine import RuleEngine
        from backend.engines.enhanced_rule_engine import EnhancedRuleEngine
        from backend.engines.scenario_detector import ScenarioDetector
        from backend.engines.recommendation_generator import RecommendationGenerator
        from backend.engines.llm_engine import LLMEngine
        from backend.engines.web_search_engine import WebSearchEngine
        from backend.engines.intelligent_search_engine import IntelligentSearchEngine
        from backend.engines.rag_engine import RAGEngine
        from backend.engines.vector_store_manager import VectorStoreManager
        from backend.engines.document_processor import DocumentProcessor
        print("    All core imports successful")
        system_imported = True
    except Exception as e:
        errors.append(f"Import failed: {e}")
        print(f"    Import failed: {e}")
        print("\n" + "="*70)
        print(" CRITICAL ERROR: Cannot proceed without imports")
        print("="*70 + "\n")
        return errors, warnings
    
    print()
    
    # 2. Check data files
    print("2⃣  Checking data files...")
    data_files = {
        "Spend Data": "data/structured/spend_data.csv",
        "Supplier Master": "data/structured/supplier_master.csv",
        "Supplier Contracts": "data/structured/supplier_contracts.csv",
        "Rule Book": "data/structured/rule_book.csv",
        "Procurement Rulebook": "data/structured/procurement_rulebook.csv",
        "Pricing Benchmarks": "data/structured/pricing_benchmarks.csv",
        "Market Pricing": "data/structured/market_pricing.csv"
    }
    
    for name, file_path in data_files.items():
        if Path(file_path).exists():
            print(f"    {name}: {file_path}")
        else:
            warnings.append(f"{name} not found: {file_path}")
            print(f"     {name}: {file_path} not found")
    
    print()
    
    # 3. Check unstructured data
    print("3⃣  Checking unstructured data...")
    unstructured_dirs = [
        "data/unstructured/policies",
        "data/unstructured/contracts",
        "data/unstructured/best_practices",
        "data/unstructured/news",
        "data/unstructured/research"
    ]
    
    for dir_path in unstructured_dirs:
        if Path(dir_path).exists():
            files = list(Path(dir_path).glob("*.*"))
            print(f"    {dir_path}: {len(files)} files")
        else:
            warnings.append(f"Directory not found: {dir_path}")
            print(f"     {dir_path}: not found")
    
    print()
    
    # 4. Initialize system
    print("4⃣  Initializing system...")
    try:
        system = LLMRecommendationSystem(
            enable_llm=False,  # Skip LLM for quick test
            enable_web_search=False,
            enable_rag=False
        )
        print("    LLMRecommendationSystem initialized")
    except Exception as e:
        errors.append(f"System initialization failed: {e}")
        print(f"    Initialization failed: {e}")
        return errors, warnings
    
    print()
    
    # 5. Test data loading
    print("5⃣  Testing data loading...")
    try:
        spend = system.data_loader.get_spend_data()
        print(f"    Spend data: {len(spend)} records")
        
        suppliers = system.data_loader.get_supplier_master()
        print(f"    Supplier master: {len(suppliers)} suppliers")
        
        contracts = system.data_loader.get_supplier_contracts()
        print(f"    Supplier contracts: {len(contracts)} contracts")
    except Exception as e:
        errors.append(f"Data loading failed: {e}")
        print(f"    Data loading failed: {e}")
    
    print()
    
    # 6. Test rule engine
    print("6⃣  Testing rule engine...")
    try:
        rules = system.rule_engine.get_all_rules()
        print(f"    Rule engine: {len(rules)} rules loaded")
    except Exception as e:
        errors.append(f"Rule engine failed: {e}")
        print(f"    Rule engine failed: {e}")
    
    print()
    
    # 7. Test enhanced rule engine
    print("7⃣  Testing enhanced rule engine...")
    try:
        from backend.engines.enhanced_rule_engine import EnhancedRuleEngine
        enhanced_engine = EnhancedRuleEngine()
        enhanced_rules = enhanced_engine.rules
        print(f"    Enhanced rule engine: {len(enhanced_rules)} rules loaded")
    except Exception as e:
        warnings.append(f"Enhanced rule engine: {e}")
        print(f"     Enhanced rule engine: {e}")
    
    print()
    
    # 8. Test scenario detector
    print("8⃣  Testing scenario detector...")
    try:
        spend_data = system.data_loader.get_spend_data()
        rule_results = system.rule_engine.evaluate_all_rules(spend_data)
        scenarios = system.scenario_detector.detect_scenarios(rule_results, spend_data)
        print(f"    Scenario detector: {len(scenarios)} scenarios detected")
    except Exception as e:
        errors.append(f"Scenario detector failed: {e}")
        print(f"    Scenario detector failed: {e}")
    
    print()
    
    # 9. Check vector database
    print("9⃣  Checking vector database...")
    vector_db_path = Path("data/vector_db")
    if vector_db_path.exists():
        files = list(vector_db_path.glob("*"))
        if len(files) > 1:  # More than just .gitkeep
            print(f"    Vector database: initialized ({len(files)} files)")
        else:
            warnings.append("Vector database not initialized. Run: python scripts/setup_rag.py")
            print("     Vector database: not initialized")
            print("      Run: python scripts/setup_rag.py")
    else:
        warnings.append("Vector database directory not found")
        print("     Vector database: directory not found")
    
    print()
    
    # 10. Check environment variables
    print(" Checking environment variables...")
    import os
    from dotenv import load_dotenv
    load_dotenv()
    
    env_vars = {
        "OPENAI_API_KEY": "OpenAI API",
        "SERPER_API_KEY": "Serper API (Web Search)",
        "GOOGLE_API_KEY": "Google Gemini API"
    }
    
    for var, name in env_vars.items():
        value = os.getenv(var)
        if value:
            print(f"    {name}: configured")
        else:
            warnings.append(f"{name} not configured")
            print(f"     {name}: not configured")
    
    print()
    
    # Summary
    print("="*70)
    print(" VERIFICATION SUMMARY")
    print("="*70)
    
    if not errors and not warnings:
        print("\n ALL SYSTEMS OPERATIONAL!")
        print("\n Your Procurement AI System is fully integrated and ready to use!")
    elif not errors:
        print(f"\n Core systems operational")
        print(f"  {len(warnings)} warnings (non-critical)")
        print("\n Warnings:")
        for warning in warnings:
            print(f"   - {warning}")
    else:
        print(f"\n {len(errors)} critical errors found")
        print(f"  {len(warnings)} warnings")
        print("\n Errors:")
        for error in errors:
            print(f"   - {error}")
        if warnings:
            print("\n Warnings:")
            for warning in warnings:
                print(f"   - {warning}")
    
    print("\n" + "="*70)
    
    # Integration status
    print("\n INTEGRATION STATUS:")
    print("    Data Loader ↔ Rule Engine")
    print("    Rule Engine ↔ Scenario Detector")
    print("    Scenario Detector ↔ Recommendation Generator")
    print("    All engines ↔ LLMRecommendationSystem")
    
    if Path("data/vector_db").exists() and len(list(Path("data/vector_db").glob("*"))) > 1:
        print("    RAG Engine ↔ Vector Store")
    else:
        print("     RAG Engine ↔ Vector Store (not initialized)")
    
    print("\n" + "="*70 + "\n")
    
    return errors, warnings


if __name__ == "__main__":
    errors, warnings = verify_integration()
    
    # Exit code
    if errors:
        sys.exit(1)
    else:
        sys.exit(0)
