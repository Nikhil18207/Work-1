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
from backend.engines.rule_engine import RuleEngine
from backend.engines.scenario_detector import ScenarioDetector
from backend.engines.recommendation_generator import RecommendationGenerator
from backend.engines.llm_engine import LLMEngine, LLMProvider
from backend.engines.rag_engine import RAGEngine
from backend.engines.vector_store_manager import VectorStoreManager
from backend.engines.intelligent_search_engine import IntelligentSearchEngine
import json


class ConversationalAI:
    """
    Real-time conversational AI that answers questions by fetching from data corpus
    Enhanced with RAG for knowledge base queries and web search for real-time data
    """

    def __init__(self, enable_llm=True, enable_rag=True, enable_web_search=True, llm_provider="openai"):
        """Initialize the conversational AI with full capabilities"""
        print(" Initializing Conversational AI...")
        
        # Load all engines
        self.data_loader = DataLoader()
        self.rule_engine = RuleEngine()
        self.scenario_detector = ScenarioDetector()
        self.recommendation_generator = RecommendationGenerator()
        
        # Load LLM if enabled
        self.enable_llm = enable_llm
        if enable_llm:
            provider = LLMProvider.OPENAI if llm_provider.lower() == "openai" else LLMProvider.GEMINI
            self.llm_engine = LLMEngine(provider=provider)
        else:
            self.llm_engine = None
        
        # Load RAG if enabled
        self.enable_rag = enable_rag
        if enable_rag:
            try:
                # Use provider-specific directories and collection names
                if llm_provider.lower() == "google":
                    persist_dir = "./data/vector_db_gemini"
                    collection = "procurement_docs_gemini"
                    provider = "google"
                else:
                    persist_dir = "./data/vector_db"
                    collection = "procurement_docs"
                    provider = "openai"
                
                self.vector_store = VectorStoreManager(
                    persist_directory=persist_dir,
                    collection_name=collection,
                    provider=provider
                )
                
                if self.vector_store.load_collection():
                    self.rag_engine = RAGEngine(
                        vector_store_manager=self.vector_store,
                        provider=provider
                    )
                    print(f" RAG engine loaded ({provider})")
                else:
                    print(f"  RAG: Vector store not found for {provider}")
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
        
        # Pre-load data
        self.spend_data = self.data_loader.load_spend_data()
        self.contracts = self.data_loader.load_supplier_contracts()
        self.regional_summary = self.data_loader.get_regional_summary()
        
        # Pre-evaluate rules
        self.rule_results = self.rule_engine.evaluate_all_rules(self.spend_data)
        
        # Pre-detect scenario
        self.scenario = self.scenario_detector.detect_scenario("Rice Bran Oil", self.spend_data)
        
        print(" AI Ready! Ask me anything about your procurement data.\n")

    def answer_question(self, question: str) -> str:
        """
        Answer a question by intelligently routing to appropriate data source
        PRIORITY: YOUR Data → YOUR Policies (RAG) → Web Search → LLM
        
        Args:
            question: User's question
            
        Returns:
            AI-generated answer from YOUR data/policies first
        """
        q_lower = question.lower()
        
        # ========== CONTEXT-AWARE PARSING (Use Case Understanding) ==========
        # Extract actual procurement need from use case descriptions
        
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
            # Use web search for finding suppliers based on use case
            if self.enable_web_search and self.web_search:
                # Enhance query with detected materials
                enhanced_query = f"Find suppliers for {', '.join(set(detected_materials[:3]))} for {question}"
                return self._answer_with_web_search(enhanced_query)
            else:
                # Search in our data for matching suppliers
                return self._answer_about_suppliers_by_category(detected_materials)
        
        # ========== PRIORITY 1: YOUR DATA (CSV Files) ==========
        
        # 1. RISK ANALYSIS - From YOUR data
        if any(word in q_lower for word in ['risk', 'risks', 'risky', 'danger', 'threat', 'vulnerability', 'exposure']):
            return self._answer_about_risks()
        
        # 2. SUPPLIER/VENDOR QUERIES - From YOUR data OR web search
        elif any(word in q_lower for word in ['supplier', 'suppliers', 'vendor', 'vendors', 'provider', 'contractor']):
            # Detect if user is asking about specific materials/categories
            materials_keywords = ['steel', 'aluminum', 'plastic', 'rubber', 'concrete', 'lumber', 'oil', 
                                'pharmaceutical', 'medical', 'it', 'software', 'cloud', 'hardware',
                                'food', 'beverage', 'energy', 'construction', 'manufacturing']
            
            has_material = any(material in q_lower for material in materials_keywords)
            has_location = any(loc in q_lower for loc in ['in ', 'from ', 'usa', 'india', 'china', 'europe', 'asia', 'america'])
            is_search_query = any(word in q_lower for word in ['find', 'search', 'top', 'best', 'latest', 'new', 'looking for'])
            
            # Use web search if:
            # 1. Explicitly asking to find/search, OR
            # 2. Asking about specific material + location (e.g., "steel suppliers in USA")
            # 3. Asking about specific material not in our current data
            if (is_search_query or (has_material and has_location) or (has_material and 'who' in q_lower)):
                if self.enable_web_search and self.web_search:
                    return self._answer_with_web_search(question)
            
            # Otherwise, analyze YOUR existing suppliers
            return self._answer_about_suppliers()
        
        # 3. SPEND/COST ANALYSIS - From YOUR data
        elif any(word in q_lower for word in ['spend', 'spending', 'cost', 'costs', 'expense', 'budget', 'price', 'pricing']):
            return self._answer_about_spend()
        
        # 4. REGIONAL/GEOGRAPHIC ANALYSIS - From YOUR data
        elif any(word in q_lower for word in ['region', 'regional', 'geography', 'geographic', 'location', 'country', 'continent']):
            return self._answer_about_regions()
        
        # 5. CATEGORY/PRODUCT ANALYSIS - From YOUR data
        elif any(word in q_lower for word in ['category', 'categories', 'product', 'products', 'item', 'commodity', 'service']):
            return self._answer_about_categories()
        
        # 6. CONTRACT/AGREEMENT QUERIES - From YOUR data
        elif any(word in q_lower for word in ['contract', 'agreement', 'terms', 'conditions', 'sla', 'payment terms']):
            return self._answer_about_contracts()
        
        # ========== PRIORITY 2: YOUR POLICIES (RAG) ==========
        
        # 7. RULES/POLICY/COMPLIANCE - From YOUR policies via RAG
        elif any(word in q_lower for word in ['rule', 'rules', 'policy', 'policies', 'compliance', 'regulation', 'guideline']):
            # Try RAG first for policy questions
            if self.enable_rag and self.rag_engine:
                return self._answer_with_rag(question)
            else:
                return self._answer_about_rules()
        
        # 8. KNOWLEDGE BASE QUERIES - From YOUR documents via RAG
        elif self.enable_rag and self.rag_engine and any(word in q_lower for word in ['what', 'how', 'why', 'explain', 'define', 'describe', 'criteria', 'requirement', 'standard', 'procedure', 'process']):
            return self._answer_with_rag(question)
        
        # 9. RECOMMENDATIONS/ACTIONS - From YOUR data + rules
        elif any(word in q_lower for word in ['action', 'actions', 'recommend', 'recommendation', 'suggest', 'advice', 'should']):
            return self._answer_about_actions()
        
        # 10. ESG/SUSTAINABILITY - From YOUR data
        elif any(word in q_lower for word in ['esg', 'sustainability', 'sustainable', 'environment', 'green', 'carbon', 'ethical']):
            return self._answer_about_esg()
        
        # 11. TIMELINE/DELIVERY - From YOUR data
        elif any(word in q_lower for word in ['timeline', 'delivery', 'lead time', 'schedule', 'deadline', 'when']):
            return self._answer_about_timeline()
        
        # ========== PRIORITY 3: WEB SEARCH (Only for external market intelligence) ==========
        
        # 12. WEB SEARCH - ONLY for explicit "find/search" queries
        elif self.enable_web_search and self.web_search and any(word in q_lower for word in ['find', 'search', 'top', 'best', 'latest', 'news', 'market', 'trend', 'forecast']):
            return self._answer_with_web_search(question)
        
        # ========== PRIORITY 4: LLM (Only as last resort) ==========
        
        # 13. LLM - ONLY for complex questions not covered above
        elif self.enable_llm and self.llm_engine:
            # LLM still uses YOUR data as context
            return self._answer_with_llm(question)
        
        # 14. FINAL FALLBACK
        else:
            return self._answer_general()

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

    def _answer_about_spend(self) -> str:
        """Answer questions about spend"""
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
        """Answer questions about rules"""
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
            if self.llm_engine.provider == LLMProvider.OPENAI:
                return self.llm_engine._generate_openai(prompt)
            else:
                return self.llm_engine._generate_gemini(prompt)
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
- Spend analysis
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
- Find suppliers
- Market trends
- Industry news
- Competitive intelligence

Try asking:
- "What are the risks?"
- "What is our supplier selection policy?"
- "Find top Rice Bran Oil suppliers in India"
- "Show me the spend breakdown"
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
