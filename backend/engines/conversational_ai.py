"""
Conversational AI Chatbot
Real-time Q&A system that fetches from data corpus
"""

import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add workspace root to path
root_path = Path(__file__).parent.parent
if str(root_path) not in sys.path:
    sys.path.insert(0, str(root_path))

from backend.engines.data_loader import DataLoader
from backend.engines.enhanced_rule_engine import EnhancedRuleEngine as RuleEngine
from backend.engines.scenario_detector import ScenarioDetector
from backend.engines.recommendation_generator import RecommendationGenerator
from backend.engines.llm_engine import LLMEngine
from backend.engines.rag_engine import RAGEngine
from backend.engines.vector_store_manager import VectorStoreManager
from backend.engines.intelligent_search_engine import IntelligentSearchEngine
from backend.engines.semantic_query_analyzer import SemanticQueryAnalyzer
from backend.engines.conversation_memory import ConversationMemory
from backend.agents.supplier_coaching_orchestrator import SupplierCoachingOrchestrator
import json


class ConversationalAI:
    """
    Real-time conversational AI that answers questions by fetching from data corpus
    Enhanced with RAG for knowledge base queries and web search for real-time data
    Uses OpenAI for LLM and embeddings
    """

    def __init__(self, enable_llm=True, enable_rag=True, enable_web_search=True):
        """Initialize the conversational AI with full capabilities"""
        print(" Initializing Conversational AI...")
        
        # Load all engines
        self.data_loader = DataLoader()
        self.rule_engine = RuleEngine()
        self.scenario_detector = ScenarioDetector()
        self.recommendation_generator = RecommendationGenerator()
        
        # Load LLM if enabled (OpenAI only)
        self.enable_llm = enable_llm
        if enable_llm:
            self.llm_engine = LLMEngine()
        else:
            self.llm_engine = None
        
        # Load RAG if enabled (OpenAI only)
        self.enable_rag = enable_rag
        if enable_rag:
            try:
                self.vector_store = VectorStoreManager(
                    persist_directory="./data/vector_db",
                    collection_name="procurement_docs",
                    provider="openai"
                )
                
                if self.vector_store.load_collection():
                    self.rag_engine = RAGEngine(
                        vector_store_manager=self.vector_store,
                        provider="openai"
                    )
                    print(f" RAG engine loaded (OpenAI)")
                else:
                    print(f"  RAG: Vector store not found")
                    self.rag_engine = None
            except Exception as e:
                print(f"  RAG initialization failed: {e}")
                self.rag_engine = None
        else:
            self.rag_engine = None
        
        # Load web search if enabled
        self.enable_web_search = enable_web_search
        if enable_web_search:
            try:
                self.web_search = IntelligentSearchEngine()
                print(" Web search enabled")
            except Exception as e:
                print(f"  Web search initialization failed: {e}")
                self.web_search = None
        else:
            self.web_search = None
        
        # Initialize semantic query analyzer for advanced understanding
        try:
            self.semantic_analyzer = SemanticQueryAnalyzer(enable_llm=enable_llm)
            print(" Semantic query analyzer enabled")
        except Exception as e:
            print(f"  Semantic analyzer initialization failed: {e}")
            self.semantic_analyzer = None
        
        # Pre-load data
        self.spend_data = self.data_loader.load_spend_data()
        self.contracts = self.data_loader.load_supplier_contracts()
        self.regional_summary = self.data_loader.get_regional_summary()
        
        # Pre-evaluate rules
        self.rule_results = self.rule_engine.evaluate_all_rules(self.spend_data)
        
        # Pre-detect scenario - analyze overall company data by default
        # Don't default to any specific category
        self.scenario = None  # Will be detected based on user's question
        
        # Initialize conversation memory
        self.memory = ConversationMemory(max_history=100)
        
        # Initialize Personalized Supplier Coaching System
        try:
            self.coaching_orchestrator = SupplierCoachingOrchestrator()
            print("✓ Personalized Coaching System enabled")
        except Exception as e:
            print(f"  Coaching system initialization failed: {e}")
            self.coaching_orchestrator = None
        
        print(" AI Ready! Ask me anything about your procurement data.\n")

    def answer_question(self, question: str) -> str:
        """
        Answer a question by intelligently routing to appropriate data source
        WITH FULL TRACEABILITY AND CONVERSATION MEMORY
        
        ENHANCED WITH SEMANTIC UNDERSTANDING:
        - Uses LLM to deeply understand query intent
        - Extracts entities (products, regions, metrics, etc.)
        - Generates optimized sub-queries for each engine
        - Routes intelligently based on query type
        
        PRIORITY: YOUR Data → YOUR Policies (RAG) → Web Search → LLM
        
        Args:
            question: User's natural language query (in ANY form!)
            
        Returns:
            AI-generated answer from YOUR data/policies first, with full traceability
        """
        q_lower = question.lower()
        
        # ========== SPECIAL COMMANDS FOR MEMORY/TRACEABILITY ==========
        
        # Show conversation history
        if q_lower in ['history', 'show history', 'conversation history']:
            return self.memory.get_conversation_summary()
        
        # Show traceability report
        if q_lower.startswith('trace'):
            parts = q_lower.split()
            if len(parts) > 1 and parts[1].isdigit():
                turn_id = int(parts[1])
                return self.memory.get_traceability_report(turn_id)
            else:
                return self.memory.get_traceability_report()
        
        # Show summary
        if q_lower in ['summary', 'show summary']:
            return self.memory.get_conversation_summary()
        
        # ========== SEMANTIC QUERY ANALYSIS (NEW!) ==========
        
        # Use semantic analyzer to understand the query deeply
        analysis = None
        if self.semantic_analyzer:
            try:
                # Get conversation context for better understanding
                context = self.memory.get_recent_context(n_turns=3) if self.memory.conversation_history else None
                
                # Analyze the query
                analysis = self.semantic_analyzer.analyze_query(question, context)
                
                # Show analysis in verbose mode (optional - can be disabled)
                if False:  # Set to True for debugging
                    print("\n" + self.semantic_analyzer.format_analysis_summary(analysis))
                
            except Exception as e:
                print(f"Semantic analysis failed: {e}")
                analysis = None
        
        # Check for similar previous questions (topic switching support)
        similar_turns = self.memory.find_similar_questions(question, threshold=0.6)
        if similar_turns and len(similar_turns) > 0:
            # User might be returning to a previous topic
            last_similar = similar_turns[-1]
            context_note = f"\n💡 *Note: This relates to your earlier question (Turn {last_similar.turn_id})*\n"
        else:
            context_note = ""
        
        # Initialize tracking variables
        detected_intent = "general"
        detected_category = None
        detected_region = None
        data_sources = []
        answer = ""
        
        # ========== USE SEMANTIC ANALYSIS FOR INTELLIGENT ROUTING ==========
        
        if analysis and analysis.get('confidence', 0) > 0.7:
            # High confidence in semantic analysis - use it!
            detected_intent = analysis.get('primary_intent', 'general')
            entities = analysis.get('entities', {})
            routing = analysis.get('routing_strategy', {})
            sub_queries = analysis.get('sub_queries', {})
            
            # Extract detected entities
            if entities.get('product_category'):
                detected_category = entities['product_category'][0] if entities['product_category'] else None
            if entities.get('region'):
                detected_region = entities['region'][0] if entities['region'] else None
            
            # Route based on semantic analysis
            if detected_intent == 'data_analysis':
                # Analyze structured data
                if detected_category:
                    answer = self._answer_about_spend(question)
                    data_sources = ["spend_data.csv", f"Category: {detected_category}"]
                elif any(word in q_lower for word in ['region', 'regional', 'geography']):
                    answer = self._answer_about_regions()
                    data_sources = ["spend_data.csv", "regional_summary"]
                else:
                    answer = self._answer_about_spend(question)
                    data_sources = ["spend_data.csv"]
            
            elif detected_intent == 'knowledge_base':
                # Query RAG knowledge base
                if self.enable_rag and self.rag_engine:
                    answer = self._answer_with_rag(sub_queries.get('rag_query', question))
                    data_sources = ["RAG Knowledge Base", "procurement_docs vector store"]
                else:
                    answer = self._answer_about_rules()
                    data_sources = ["rule_book.csv"]
            
            elif detected_intent == 'web_search':
                # Use web search
                if self.enable_web_search and self.web_search:
                    search_query = sub_queries.get('web_search_query', question)
                    answer = self._answer_with_web_search(search_query)
                    data_sources = ["Web Search (Intelligent Search Engine)"]
                else:
                    answer = "Web search not available. Try asking about your existing data."
                    data_sources = []
            
            elif detected_intent == 'recommendation':
                # Generate recommendation
                answer = self._answer_about_actions()
                data_sources = ["recommendation_engine", "rule_results", "scenario_detector"]
            
            elif detected_intent == 'comparison':
                # Compare suppliers/options
                answer = self._answer_about_suppliers()
                data_sources = ["spend_data.csv", "supplier_master.csv"]
            
            elif detected_intent == 'risk_assessment':
                # Assess risks
                answer = self._answer_about_risks()
                data_sources = ["rule_results", "risk_register.csv", "spend_data.csv"]
            
            elif detected_intent == 'compliance_check':
                # Check compliance
                answer = self._answer_about_rules()
                data_sources = ["rule_book.csv", "procurement_rulebook.csv"]
            
            else:
                # Fall through to pattern-based routing
                analysis = None
        
        # ========== FALLBACK: PATTERN-BASED ROUTING (Original Logic) ==========
        
        if not answer:  # If semantic routing didn't produce an answer
            
            # ========== CONTEXT-AWARE PARSING (Use Case Understanding) ==========
            
            # Use case → Material mapping
            use_case_materials = {
                'car': ['aluminum', 'steel', 'plastics', 'rubber', 'electronics'],
                'automobile': ['aluminum', 'steel', 'plastics', 'rubber'],
                'vehicle': ['aluminum', 'steel', 'plastics'],
                'data center': ['servers', 'network equipment', 'cooling systems'],
                'building': ['construction materials', 'steel', 'concrete', 'lumber'],
                'construction': ['construction materials', 'steel', 'concrete'],
                'hospital': ['medical devices', 'pharmaceuticals', 'medical supplies'],
                'clinic': ['medical devices', 'pharmaceuticals'],
                'software': ['cloud services', 'saas', 'software licenses'],
                'app': ['cloud services', 'saas'],
                'website': ['cloud services', 'hosting'],
                'manufacturing': ['raw materials', 'equipment', 'machinery'],
                'factory': ['equipment', 'machinery', 'raw materials']
            }
            
            # Check if question contains use case context
            detected_materials = []
            for use_case, materials in use_case_materials.items():
                if use_case in q_lower:
                    detected_materials.extend(materials)
            
            # If materials detected from use case, search for those suppliers
            if detected_materials and ('supplier' in q_lower or 'need' in q_lower or 'looking for' in q_lower or 'want' in q_lower):
                detected_intent = "supplier_search_use_case"
                # Use web search for finding suppliers based on use case
                if self.enable_web_search and self.web_search:
                    # Enhance query with detected materials
                    enhanced_query = f"Find suppliers for {', '.join(set(detected_materials[:3]))} for {question}"
                    answer = self._answer_with_web_search(enhanced_query)
                    data_sources = ["Web Search (Intelligent Search Engine)"]
                else:
                    # Search in our data for matching suppliers
                    answer = self._answer_about_suppliers_by_category(detected_materials)
                    data_sources = ["spend_data.csv", "supplier_master.csv"]
        
            # ========== PRIORITY 1: YOUR DATA (CSV Files) ==========
            
            # 1. RISK ANALYSIS - From YOUR data
            elif any(word in q_lower for word in ['risk', 'risks', 'risky', 'danger', 'threat', 'vulnerability', 'exposure']):
                detected_intent = "risk_analysis"
                answer = self._answer_about_risks()
                data_sources = ["rule_results", "risk_register.csv", "spend_data.csv"]
            
            # 2. SUPPLIER/VENDOR QUERIES - From YOUR data OR web search
            elif any(word in q_lower for word in ['supplier', 'suppliers', 'vendor', 'vendors', 'provider', 'contractor']):
                detected_intent = "supplier_analysis"
                # Detect if user is asking about specific materials/categories
                materials_keywords = ['steel', 'aluminum', 'plastic', 'rubber', 'concrete', 'lumber', 'oil', 
                                    'pharmaceutical', 'medical', 'it', 'software', 'cloud', 'hardware',
                                    'food', 'beverage', 'energy', 'construction', 'manufacturing']
                
                has_material = any(material in q_lower for material in materials_keywords)
                has_location = any(loc in q_lower for loc in ['in ', 'from ', 'usa', 'india', 'china', 'europe', 'asia', 'america', 'malaysia'])
                is_search_query = any(word in q_lower for word in ['find', 'search', 'top', 'best', 'latest', 'new', 'looking for'])
                
                # Use web search if:
                # 1. Explicitly asking to find/search, OR
                # 2. Asking about specific material + location (e.g., "steel suppliers in USA")
                # 3. Asking about specific material not in our current data
                if (is_search_query or (has_material and has_location) or (has_material and 'who' in q_lower)):
                    if self.enable_web_search and self.web_search:
                        answer = self._answer_with_web_search(question)
                        data_sources = ["Web Search (Intelligent Search Engine)"]
                        detected_intent = "supplier_search_web"
                    else:
                        # Fallback to internal data if web search not enabled or failed
                        answer = self._answer_about_suppliers()
                        data_sources = ["spend_data.csv", "supplier_master.csv", "recommendation_engine"]
                
                # Otherwise, analyze YOUR existing suppliers
                else:
                    answer = self._answer_about_suppliers()
                    data_sources = ["spend_data.csv", "supplier_master.csv", "recommendation_engine"]
            
            # 3. SPEND/COST ANALYSIS - From YOUR data
            elif any(word in q_lower for word in ['spend', 'spending', 'cost', 'costs', 'expense', 'budget', 'price', 'pricing']):
                detected_intent = "spend_analysis"
                # Try to detect specific category in question
                if 'Category' in self.spend_data.columns:
                    categories = self.spend_data['Category'].unique()
                    for category in categories:
                        # Check if category name appears in question
                        if category.lower() in q_lower:
                            detected_category = category
                            break
                answer = self._answer_about_spend(question)
                data_sources = ["spend_data.csv", "regional_summary"]
                if detected_category:
                    data_sources.append(f"spend_data.csv (filtered: {detected_category})")
            
            # 4. REGIONAL/GEOGRAPHIC ANALYSIS - From YOUR data
            elif any(word in q_lower for word in ['region', 'regional', 'geography', 'geographic', 'location', 'country', 'continent']):
                detected_intent = "regional_analysis"
                answer = self._answer_about_regions()
                data_sources = ["spend_data.csv", "regional_summary"]
            
            # 5. CATEGORY/PRODUCT ANALYSIS - From YOUR data
            elif any(word in q_lower for word in ['category', 'categories', 'product', 'products', 'item', 'commodity', 'service']):
                detected_intent = "category_analysis"
                answer = self._answer_about_categories()
                data_sources = ["spend_data.csv"]
            
            # 6. CONTRACT/AGREEMENT QUERIES - From YOUR data
            elif any(word in q_lower for word in ['contract', 'agreement', 'terms', 'conditions', 'sla', 'payment terms']):
                detected_intent = "contract_analysis"
                answer = self._answer_about_contracts()
                data_sources = ["supplier_contracts.csv"]
            
            # 6.5. BENCHMARK/INDUSTRY COMPARISON QUERIES - From YOUR data
            elif any(word in q_lower for word in ['benchmark', 'benchmarks', 'industry standard', 'industry average', 'compare to industry', 'market average', 'industry comparison']):
                detected_intent = "benchmark_analysis"
                # Try to detect category
                benchmark_category = None
                if detected_category:
                    benchmark_category = detected_category
                answer = self._answer_about_benchmarks(benchmark_category)
                data_sources = ["industry_benchmarks.csv"]
            
            # ========== PRIORITY 2: YOUR POLICIES (RAG) ==========
            
            # 7. RULES/POLICY/COMPLIANCE - From YOUR policies via RAG
            elif any(word in q_lower for word in ['rule', 'rules', 'policy', 'policies', 'compliance', 'regulation', 'guideline']):
                detected_intent = "policy_query"
                # Try RAG first for policy questions
                if self.enable_rag and self.rag_engine:
                    answer = self._answer_with_rag(question)
                    data_sources = ["RAG Knowledge Base", "procurement_docs vector store"]
                else:
                    answer = self._answer_about_rules()
                    data_sources = ["rule_book.csv", "procurement_rulebook.csv"]
            
            # 8. KNOWLEDGE BASE QUERIES - From YOUR documents via RAG
            elif self.enable_rag and self.rag_engine and any(word in q_lower for word in ['what', 'how', 'why', 'explain', 'define', 'describe', 'criteria', 'requirement', 'standard', 'procedure', 'process']):
                detected_intent = "knowledge_query"
                answer = self._answer_with_rag(question)
                data_sources = ["RAG Knowledge Base", "procurement_docs vector store"]
            
            # 9. RECOMMENDATIONS/ACTIONS - From YOUR data + rules
            elif any(word in q_lower for word in ['action', 'actions', 'recommend', 'recommendation', 'suggest', 'advice', 'should']):
                detected_intent = "recommendation"
                answer = self._answer_about_actions()
                data_sources = ["recommendation_engine", "rule_results", "scenario_detector"]
            
            # 10. ESG/SUSTAINABILITY - From YOUR data
            elif any(word in q_lower for word in ['esg', 'sustainability', 'sustainable', 'environment', 'green', 'carbon', 'ethical']):
                detected_intent = "esg_analysis"
                answer = self._answer_about_esg()
                data_sources = ["supplier_contracts.csv (ESG scores)", "recommendation_engine"]
            
            # 11. TIMELINE/DELIVERY - From YOUR data
            elif any(word in q_lower for word in ['timeline', 'delivery', 'lead time', 'schedule', 'deadline', 'when']):
                detected_intent = "timeline_query"
                answer = self._answer_about_timeline()
                data_sources = ["recommendation_engine", "supplier_master.csv (lead times)"]
            
            # ========== PRIORITY 3: WEB SEARCH (Only for external market intelligence) ==========
            
            # 12. WEB SEARCH - ONLY for explicit "find/search" queries
            elif self.enable_web_search and self.web_search and any(word in q_lower for word in ['find', 'search', 'top', 'best', 'latest', 'news', 'market', 'trend', 'forecast']):
                detected_intent = "web_search"
                answer = self._answer_with_web_search(question)
                data_sources = ["Web Search (Intelligent Search Engine)"]
            
            # ========== PRIORITY 4: LLM (Only as last resort) ==========
            
            # 13. LLM - ONLY for complex questions not covered above
            elif self.enable_llm and self.llm_engine:
                detected_intent = "llm_reasoning"
                # LLM still uses YOUR data as context
                answer = self._answer_with_llm(question)
                data_sources = ["LLM (GPT-4)", "spend_data.csv (context)", "rule_results (context)"]
            
            # 14. FINAL FALLBACK
            else:
                detected_intent = "general_help"
                answer = self._answer_general()
                data_sources = []
        
        # ========== SAVE TO MEMORY WITH FULL TRACEABILITY ==========
        
        self.memory.add_turn(
            user_question=question,
            ai_answer=answer,
            data_sources=data_sources,
            detected_intent=detected_intent,
            detected_category=detected_category,
            detected_region=detected_region,
            metadata={
                'timestamp': self.memory.conversation_history[-1].timestamp.isoformat() if self.memory.conversation_history else None,
                'has_similar_questions': len(similar_turns) > 0
            }
        )
        
        # Add context note if returning to previous topic
        if context_note:
            answer = context_note + answer
        
        # Add traceability footer
        if data_sources:
            answer += f"\n\n📊 *Data Sources: {', '.join(data_sources)}*"
        
        return answer

    def _answer_about_risks(self) -> str:
        """Answer questions about risks"""
        triggered_rules = [r for r in self.rule_results if r.triggered]
        
        if not triggered_rules:
            return " Good news! No major risks detected in your procurement data."
        
        answer = " **RISKS DETECTED:**\n\n"
        
        for rule in triggered_rules:
            answer += f"**{rule.rule_id}: {rule.rule_name}**\n"
            answer += f"- Risk Level: {rule.risk_level.value}\n"
            answer += f"- Current: {rule.actual_value:.2f} | Threshold: {rule.threshold_value}\n"
            answer += f"- Issue: {rule.details.get('description', 'N/A')}\n"
            answer += f"- Action: {rule.action_recommendation}\n\n"
        
        return answer

    def _answer_about_suppliers(self) -> str:
        """Answer questions about suppliers"""
        recommendation = self.recommendation_generator.generate_recommendation(self.scenario)
        
        answer = " **SUPPLIER RECOMMENDATIONS:**\n\n"
        
        # Current suppliers
        top_suppliers = self.spend_data.groupby(['Supplier_ID', 'Supplier_Name'])['Spend_USD'].sum()
        top_suppliers = top_suppliers.sort_values(ascending=False).head(3)
        
        answer += "**Current Top Suppliers:**\n"
        for (sid, sname), spend in top_suppliers.items():
            pct = (spend / self.spend_data['Spend_USD'].sum() * 100)
            answer += f"- {sname} ({sid}): ${spend:,.0f} ({pct:.1f}%)\n"
        
        answer += "\n**Recommended New Suppliers:**\n"
        for action in recommendation.actions:
            if action.get('type') == 'Add Alternative Supplier':
                answer += f"- {action['supplier_name']} ({action['region']})\n"
                answer += f"  ESG Score: {action['esg_score']}\n"
                answer += f"  Allocation: {action['allocation']}\n"
                answer += f"  Rationale: {action['rationale']}\n\n"
        
        return answer

    def _answer_about_spend(self, question: str = "") -> str:
        """Answer questions about spend - category-aware"""
        q_lower = question.lower()
        
        # Try to detect specific category in question
        detected_category = None
        if 'Category' in self.spend_data.columns:
            categories = self.spend_data['Category'].unique()
            for category in categories:
                # Check if category name appears in question
                if category.lower() in q_lower:
                    detected_category = category
                    break
        
        # If specific category detected, show category-specific spend
        if detected_category:
            category_data = self.spend_data[self.spend_data['Category'] == detected_category]
            
            if category_data.empty:
                return f" No spend data found for category: {detected_category}"
            
            total_category_spend = category_data['Spend_USD'].sum()
            total_overall_spend = self.spend_data['Spend_USD'].sum()
            category_pct = (total_category_spend / total_overall_spend * 100)
            
            answer = f" **SPEND ANALYSIS: {detected_category}**\n\n"
            answer += f"**Total Spend:** ${total_category_spend:,.0f} ({category_pct:.1f}% of total)\n\n"
            
            # Regional breakdown for this category
            if 'Supplier_Region' in category_data.columns:
                regional_spend = category_data.groupby('Supplier_Region')['Spend_USD'].sum().sort_values(ascending=False)
                answer += "**Regional Breakdown:**\n"
                for region, spend in regional_spend.items():
                    pct = (spend / total_category_spend * 100)
                    answer += f"- {region}: ${spend:,.0f} ({pct:.1f}%)\n"
                answer += "\n"
            
            # Top suppliers for this category
            if 'Supplier_Name' in category_data.columns:
                supplier_spend = category_data.groupby('Supplier_Name')['Spend_USD'].sum().sort_values(ascending=False).head(5)
                answer += "**Top Suppliers:**\n"
                for supplier, spend in supplier_spend.items():
                    pct = (spend / total_category_spend * 100)
                    answer += f"- {supplier}: ${spend:,.0f} ({pct:.1f}%)\n"
                answer += "\n"
            
            # Transaction details
            answer += f"**Transactions:** {len(category_data)}\n"
            answer += f"**Average Transaction:** ${category_data['Spend_USD'].mean():,.0f}\n"
            
            return answer
        
        # Otherwise, show overall spend summary
        total_spend = self.regional_summary['total_spend']
        
        answer = " **SPEND ANALYSIS:**\n\n"
        answer += f"**Total Spend:** ${total_spend:,.0f}\n\n"
        
        answer += "**Regional Breakdown:**\n"
        for region, data in sorted(self.regional_summary['regions'].items(), 
                                   key=lambda x: x[1]['spend'], reverse=True):
            answer += f"- {region}: ${data['spend']:,.0f} ({data['percentage']:.2f}%)\n"
        
        answer += f"\n**Suppliers:** {self.spend_data['Supplier_ID'].nunique()}\n"
        answer += f"**Transactions:** {len(self.spend_data)}\n"
        answer += f"**Average Transaction:** ${self.spend_data['Spend_USD'].mean():,.0f}\n"
        
        return answer

    def _answer_about_regions(self) -> str:
        """Answer questions about regions"""
        answer = " **REGIONAL DISTRIBUTION:**\n\n"
        
        for region, data in sorted(self.regional_summary['regions'].items(), 
                                   key=lambda x: x[1]['percentage'], reverse=True):
            answer += f"**{region}:**\n"
            answer += f"- Spend: ${data['spend']:,.0f} ({data['percentage']:.2f}%)\n"
            answer += f"- Transactions: {data['transaction_count']}\n"
            
            # Check if this region is problematic
            if data['percentage'] > 40:
                answer += f"-  HIGH CONCENTRATION (>{40}% threshold)\n"
            
            answer += "\n"
        
        return answer

    def _answer_about_rules(self) -> str:
        """Answer questions about rules with PERSONALIZED COACHING"""
        # Use the new Personalized Coaching System if available
        if self.coaching_orchestrator:
            try:
                # Detect category from context or use company-wide analysis
                category = None  # Default to company-wide
                
                # Check if there's a recent category mentioned in conversation
                if self.memory.conversation_history:
                    recent_context = self.memory.get_recent_context(n_turns=3)
                    # Try to extract category from recent context
                    # For now, default to None (company-wide)
                
                # Run comprehensive coaching analysis
                coaching_input = {
                    'client_id': 'C001',  # Using actual client ID from data
                    'coaching_mode': 'focused',
                    'focus_areas': ['concentration', 'quality'],
                    'tuning_mode': 'balanced'
                }
                
                # Only add category if explicitly detected
                if category:
                    coaching_input['category'] = category
                
                result = self.coaching_orchestrator.execute(coaching_input)
                
                if result['success']:
                    data = result['data']
                    
                    # Build personalized response
                    answer = "🎯 **PERSONALIZED SUPPLIER COACHING:**\n\n"
                    
                    # Current State
                    exec_summary = data['executive_summary']
                    current_state = exec_summary['current_state']
                    
                    answer += "**📊 CURRENT SITUATION:**\n"
                    answer += f"- Total Spend: {current_state['total_spend_formatted']}\n"
                    answer += f"- Active Suppliers: {current_state['supplier_count']}\n"
                    answer += f"- Risk Level: {current_state['risk_level']}\n\n"
                    
                    # Key Issues with Specific Details
                    key_issues = exec_summary['key_issues']
                    if key_issues['violations'] > 0 or key_issues['warnings'] > 0:
                        answer += "**⚠️ ISSUES DETECTED:**\n"
                        answer += f"- Violations: {key_issues['violations']}\n"
                        answer += f"- Warnings: {key_issues['warnings']}\n"
                        
                        for i, area in enumerate(key_issues['critical_areas'][:3], 1):
                            answer += f"  {i}. {area}\n"
                        answer += "\n"
                    
                    # Personalized Recommendations with Reasoning
                    recommendations = data['branches'].get('personalized_recommendations', {})
                    rec_list = recommendations.get('personalized_recommendations', [])
                    
                    if rec_list:
                        answer += "**💡 PERSONALIZED RECOMMENDATIONS:**\n\n"
                        
                        for i, rec in enumerate(rec_list[:3], 1):
                            answer += f"**{i}. [{rec['priority']}] {rec['title']}**\n"
                            answer += f"   📍 Current: {rec['current_situation']}\n"
                            answer += f"   🎯 Target: {rec['target_state']}\n"
                            answer += f"   💰 Expected Outcome: {rec['expected_outcome']}\n"
                            
                            # Show specific actions with reasoning
                            if rec.get('specific_actions'):
                                answer += f"   \n   **Action Plan:**\n"
                                for step in rec['specific_actions'][:2]:
                                    answer += f"   Step {step['step']}: {step['action']}\n"
                                    answer += f"   └─ Timeline: {step['timeline']} | Owner: {step['owner']}\n"
                            
                            # Show reasoning/rationale
                            if rec.get('rationale'):
                                answer += f"   \n   **Why This Matters:** {rec['rationale']}\n"
                            
                            answer += "\n"
                    
                    # Market Intelligence
                    market_intel = exec_summary.get('market_intelligence', {})
                    if market_intel.get('available'):
                        answer += "**📈 MARKET INTELLIGENCE:**\n"
                        for insight in market_intel.get('top_insights', [])[:2]:
                            answer += f"- {insight}\n"
                        answer += "\n"
                    
                    # Immediate Actions
                    immediate_actions = exec_summary.get('immediate_actions', [])
                    if immediate_actions:
                        answer += "**🚨 IMMEDIATE ACTIONS REQUIRED:**\n"
                        for action in immediate_actions[:3]:
                            answer += f"- [{action['priority']}] {action['action']}\n"
                            answer += f"  Timeline: {action['timeline']}\n"
                    
                    return answer
                
            except Exception as e:
                print(f"Coaching system error: {e}")
                # Fall back to old method
        
        # Fallback to old generic method if coaching system not available
        answer = " **BUSINESS RULES:**\n\n"
        
        for rule in self.rule_results:
            status = " TRIGGERED" if rule.triggered else " PASSED"
            answer += f"**{rule.rule_id}: {rule.rule_name}** - {status}\n"
            answer += f"- Threshold: {rule.threshold_value}\n"
            answer += f"- Current Value: {rule.actual_value:.2f}\n"
            answer += f"- Risk Level: {rule.risk_level.value}\n"
            answer += f"- Action: {rule.action_recommendation}\n\n"
        
        return answer

    def _answer_about_actions(self) -> str:
        """Answer questions about recommended actions"""
        recommendation = self.recommendation_generator.generate_recommendation(self.scenario)
        
        answer = " **RECOMMENDED ACTIONS:**\n\n"
        answer += f"**Strategy:** {recommendation.strategy.value.replace('_', ' ').title()}\n"
        answer += f"**Priority:** {recommendation.priority}\n"
        answer += f"**Timeline:** {recommendation.timeline}\n\n"
        
        for i, action in enumerate(recommendation.actions, 1):
            answer += f"**{i}. {action['type']}**\n"
            
            if action['type'] == 'Reduce Regional Concentration':
                answer += f"- Current: {action['current_value']}\n"
                answer += f"- Target: {action['target_value']}\n"
                answer += f"- Reallocation: {action['reallocation_required']}\n"
            
            elif action['type'] == 'Add Alternative Supplier':
                answer += f"- Supplier: {action['supplier_name']}\n"
                answer += f"- Region: {action['region']}\n"
                answer += f"- ESG Score: {action['esg_score']}\n"
                answer += f"- Allocation: {action['allocation']}\n"
            
            answer += "\n"
        
        return answer

    def _answer_about_esg(self) -> str:
        """Answer questions about ESG"""
        answer = " **ESG ANALYSIS:**\n\n"
        
        # Get suppliers with ESG scores
        esg_suppliers = self.contracts.sort_values('ESG_Score', ascending=False)
        
        answer += "**Top ESG Performers:**\n"
        for _, supplier in esg_suppliers.head(5).iterrows():
            answer += f"- {supplier['Supplier_Name']}: {supplier['ESG_Score']}/100\n"
        
        answer += f"\n**Average ESG Score:** {esg_suppliers['ESG_Score'].mean():.1f}/100\n"
        
        # Get recommendation
        recommendation = self.recommendation_generator.generate_recommendation(self.scenario)
        esg_improvement = recommendation.expected_outcomes.get('esg_score_improvement', 'N/A')
        
        answer += f"**Potential Improvement:** {esg_improvement}\n"
        
        return answer

    def _answer_about_timeline(self) -> str:
        """Answer questions about timeline"""
        recommendation = self.recommendation_generator.generate_recommendation(self.scenario)
        
        answer = "⏱ **IMPLEMENTATION TIMELINE:**\n\n"
        answer += f"**Recommended Timeline:** {recommendation.timeline}\n"
        answer += f"**Priority:** {recommendation.priority}\n\n"
        
        answer += "**Phased Approach:**\n"
        answer += "- Month 1-2: Identify and qualify alternative suppliers\n"
        answer += "- Month 3-4: Negotiate contracts and terms\n"
        answer += "- Month 5-8: Gradual volume transition\n"
        answer += "- Month 9-12: Full implementation and monitoring\n"
        
        return answer

    def _answer_about_categories(self) -> str:
        """Answer questions about product categories - Universal for any industry"""
        answer = " **CATEGORY ANALYSIS:**\n\n"
        
        # Get unique categories from spend data
        if 'Category' in self.spend_data.columns:
            category_spend = self.spend_data.groupby('Category')['Spend_USD'].agg(['sum', 'count', 'mean'])
            category_spend = category_spend.sort_values('sum', ascending=False)
            
            answer += "**Procurement Categories:**\n"
            for category, row in category_spend.iterrows():
                pct = (row['sum'] / self.spend_data['Spend_USD'].sum() * 100)
                answer += f"- {category}:\n"
                answer += f"  Total Spend: ${row['sum']:,.0f} ({pct:.1f}%)\n"
                answer += f"  Transactions: {int(row['count'])}\n"
                answer += f"  Avg Transaction: ${row['mean']:,.0f}\n\n"
        else:
            answer += "Category information not available in current data.\n"
        
        return answer

    def _answer_about_contracts(self) -> str:
        """Answer questions about contracts - Universal for any industry"""
        answer = " **CONTRACT ANALYSIS:**\n\n"
        
        if not self.contracts.empty:
            answer += f"**Total Active Contracts:** {len(self.contracts)}\n\n"
            
            # Payment terms analysis
            if 'Payment_Terms_Days' in self.contracts.columns:
                avg_payment_terms = self.contracts['Payment_Terms_Days'].mean()
                answer += f"**Average Payment Terms:** {avg_payment_terms:.0f} days\n\n"
            
            # Contract regions
            if 'Region' in self.contracts.columns:
                regions = self.contracts['Region'].value_counts()
                answer += "**Contracts by Region:**\n"
                for region, count in regions.items():
                    answer += f"- {region}: {count} contracts\n"
            
            # ESG scores
            if 'ESG_Score' in self.contracts.columns:
                avg_esg = self.contracts['ESG_Score'].mean()
                answer += f"\n**Average ESG Score:** {avg_esg:.1f}/100\n"
        else:
            answer += "No contract data available.\n"
        
        return answer
    
    def _answer_about_benchmarks(self, category: str = None) -> str:
        """Answer questions about industry benchmarks"""
        answer = " **INDUSTRY BENCHMARK ANALYSIS:**\n\n"
        
        # Get benchmark data
        benchmark_analysis = self.data_loader.get_benchmark_analysis(category)
        
        if 'error' in benchmark_analysis:
            answer += f"{benchmark_analysis['error']}\n"
            answer += "\nAvailable categories with benchmarks:\n"
            benchmarks = self.data_loader.load_industry_benchmarks()
            for cat in benchmarks['Category'].unique():
                answer += f"- {cat}\n"
            return answer
        
        answer += f"**Category:** {benchmark_analysis['category']}\n\n"
        
        # Overall performance
        if 'performance_summary' in benchmark_analysis:
            answer += f"**Overall Performance:** {benchmark_analysis['performance_summary']}\n"
            answer += f"**Average Gap:** {benchmark_analysis['overall_gap']}\n\n"
        
        # Individual metrics
        answer += "**Detailed Metrics:**\n\n"
        for metric in benchmark_analysis['metrics']:
            answer += f"**{metric['metric'].replace('_', ' ').title()}:**\n"
            answer += f"  Industry Benchmark: {metric['industry_benchmark']} {metric['unit']}\n"
            answer += f"  Our Performance: {metric['our_performance']} {metric['unit']}\n"
            answer += f"  Gap: {metric['gap']} {metric['unit']}"
            
            if 'status' in metric:
                answer += f" ({metric['status']})"
            
            answer += f"\n  Source: {metric['source']}\n"
            answer += f"  Updated: {metric['last_updated']}\n\n"
        
        return answer

    def _answer_with_llm(self, question: str) -> str:
        """Answer using LLM"""
        # Build context from data
        context = f"""
Data Summary:
- Total Spend: ${self.regional_summary['total_spend']:,.0f}
- Suppliers: {self.spend_data['Supplier_ID'].nunique()}
- Scenario: {self.scenario.details.get('pattern', 'N/A')}
- Risk Level: {self.scenario.risk_level.value}

Regional Distribution:
{json.dumps(self.regional_summary['regions'], indent=2)}

Rules Status:
{[f"{r.rule_id}: {'TRIGGERED' if r.triggered else 'PASSED'}" for r in self.rule_results]}
"""
        
        prompt = f"""You are a procurement AI assistant. Answer this question based on the data:

{context}

Question: {question}

Provide a clear, specific answer with numbers and facts from the data.
"""
        
        try:
            return self.llm_engine._generate_openai(prompt)
        except Exception as e:
            return f"LLM Error: {e}\n\nFalling back to rule-based answer..."
    
    def _answer_with_rag(self, question: str) -> str:
        """Answer using RAG (knowledge base)"""
        try:
            response = self.rag_engine.query(
                question=question,
                k=5,
                include_sources=True,
                verbose=False
            )
            
            answer = " **FROM KNOWLEDGE BASE:**\n\n"
            answer += response['answer']
            
            if response.get('sources'):
                answer += "\n\n**Sources:**\n"
                for source in response['sources'][:3]:
                    answer += f"- {source['source']} (relevance: {source['score']:.2f})\n"
            
            return answer
        except Exception as e:
            return f"RAG Error: {e}\n\nTrying alternative method..."
    
    def _answer_with_web_search(self, question: str) -> str:
        """Answer using web search"""
        try:
            # Use intelligent_search method which returns formatted results
            result = self.web_search.intelligent_search(question, max_results=5)
            
            if not result or not result.get('results'):
                return " No web results found. Try rephrasing your question."
            
            # Return the pre-formatted output from intelligent search
            return result.get('formatted_output', "No results found.")
            
        except Exception as e:
            return f"Web Search Error: {e}\n\nTrying alternative method..."

    def _answer_general(self) -> str:
        """General answer when pattern not matched"""
        capabilities = """I can help you with:

** Data Analysis:**
- Risks and issues
- Supplier recommendations
- Spend analysis (category-aware!)
- Regional distribution
- Business rules
- Recommended actions
- ESG scores
- Implementation timeline

** Knowledge Base (RAG):**
- Procurement policies
- Best practices
- Guidelines and procedures
- Supplier criteria
- Quality standards

** Live Market Intelligence:**
- Find suppliers (any country!)
- Market trends
- Industry news
- Competitive intelligence

** Memory & Traceability:**
- Type 'history' to see conversation summary
- Type 'trace' to see full traceability report
- Type 'summary' for session overview
- All answers show data sources used

Try asking:
- "What are the risks?"
- "How much did we spend on Rice Bran Oil?"
- "Find top steel suppliers in Malaysia"
- "Show me the spend breakdown"
- "history" (to see what we've discussed)
"""
        return capabilities

    def chat(self):
        """Start interactive chat session"""
        print("=" * 80)
        print(" CONVERSATIONAL AI - PROCUREMENT ASSISTANT")
        print("=" * 80)
        print("\nI'm your AI procurement assistant with:")
        print("   Access to your procurement data")
        if self.enable_rag and self.rag_engine:
            print("   Knowledge base (policies, best practices)")
        if self.enable_web_search and self.web_search:
            print("   Real-time web search")
        if self.enable_llm and self.llm_engine:
            print("   AI-powered reasoning")
        print("\nAsk me anything! Type 'exit' or 'quit' to end the conversation.\n")
        
        while True:
            try:
                # Get user input
                question = input("You: ").strip()
                
                # Check for exit
                if question.lower() in ['exit', 'quit', 'bye', 'goodbye']:
                    print("\n AI: Goodbye! Happy procurement! \n")
                    break
                
                if not question:
                    continue
                
                # Get answer
                answer = self.answer_question(question)
                
                # Print answer
                print(f"\n AI:\n{answer}\n")
                print("-" * 80 + "\n")
                
            except KeyboardInterrupt:
                print("\n\n AI: Goodbye! \n")
                break
            except Exception as e:
                print(f"\n Error: {e}\n")


# Example usage
if __name__ == "__main__":
    # Initialize AI with ALL features enabled
    ai = ConversationalAI(
        enable_llm=True,        # Enable LLM reasoning
        enable_rag=True,        # Enable knowledge base
        enable_web_search=True  # Enable web search
    )
    
    # Start chat
    ai.chat()
