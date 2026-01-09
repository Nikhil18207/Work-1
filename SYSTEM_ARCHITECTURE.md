# Procurement AI - System Architecture & End-to-End Workflow

## 1. SYSTEM OVERVIEW

**Enterprise-grade LLM-powered multi-industry procurement intelligence system** with real-time analytics, rule-based constraints, RAG capabilities, and tariff analysis.

- **7 Industries** × **27 Products** × **150+ Trade Routes** = **Comprehensive Global Coverage**
- **35+ Procurement Rules** (R001-R035) with hard/soft constraints
- **Multi-Agent Orchestration** - 15+ specialized agents coordinating in 5 branches
- **Triple Data Corpus** - Structured CSVs + Unstructured Policies + Calculated Metrics

---

## 2. ENTRY POINTS & INTERFACES

### 2.1 Streamlit Web UI (`app.py`)
```
START → app.py (1,069 lines)
    ├── page: "🎯 Dashboard"
    ├── page: "📊 Spend Analysis"
    ├── page: "🎯 Supplier Coaching"
    ├── page: "📋 Rule Violations"
    ├── page: "🔄 Supplier Scorecard"
    ├── page: "🛣️ Implementation Roadmap"
    ├── page: "🌍 Global Sourcing"
    ├── page: "💰 Cost-Risk Analysis"
    └── page: "⚙️ Advanced Tools"
        ├── Leading Questions Module
        ├── Tariff Calculator
        ├── Cost & Risk Loop
        ├── Client Criteria Matching
        └── Visual Workflow Diagrams
```

### 2.2 CLI Interface (`main.py`)
```
START → main.py
    └── ConversationalAI.chat() (REPL mode)
        ├── Ask questions
        ├── Get recommendations
        ├── View rules
        └── Interactive Q&A
```

### 2.3 Quick Start (`START_HERE.py`)
- Direct entry to main system
- Minimal setup
- Full feature access

### 2.4 Global System (`START_GLOBAL_SYSTEM.py`)
- All features + advanced modes
- Full agent orchestration
- Complete workflow execution

---

## 3. CORE ARCHITECTURE LAYERS

### Layer 1: Input & Interface
```
┌─────────────────────────────────────┐
│  User Interfaces                    │
├─────────────────────────────────────┤
│  • Streamlit Web UI (app.py)        │
│  • CLI Chat (main.py)               │
│  • API Endpoints (FastAPI)          │
│  • Direct Python API                │
└─────────────────────────────────────┘
```

### Layer 2: Query Processing & Routing
```
┌─────────────────────────────────────────────────────────────┐
│  ConversationalAI (backend/conversational_ai.py - 1,043 lines)
├─────────────────────────────────────────────────────────────┤
│  INPUT PROCESSING:                                          │
│  • Parse natural language question                          │
│  • Semantic query analyzer (understands intent)             │
│  • Extract entities (products, regions, metrics)            │
│  • Generate sub-queries for each engine                     │
│                                                              │
│  INTELLIGENT ROUTING (PRIORITY ORDER):                      │
│  1. YOUR Data (CSV files - structured data)                 │
│  2. YOUR Policies (RAG - vector DB)                         │
│  3. Web Search (real-time market intelligence)              │
│  4. LLM Reasoning (GPT-4 analysis)                          │
│                                                              │
│  OUTPUT GENERATION:                                         │
│  • Combine results from all sources                         │
│  • Add full traceability (source citations)                 │
│  • Store in conversation memory                             │
│  • Return with confidence scores                            │
└─────────────────────────────────────────────────────────────┘
```

### Layer 3: Data & Knowledge Engines
```
┌────────────────────────────────────────────────────────┐
│  Data Processing Layer                                 │
├────────────────────────────────────────────────────────┤
│  DataLoader          → Loads CSVs, caches data         │
│  RuleEngine          → Evaluates 35+ procurement rules │
│  ScenarioDetector    → Identifies analysis scenarios   │
│  RuleEvaluationEngine→ R001-R035 constraint tracking  │
│  RAGEngine           → Retrieval from knowledge base   │
│  SemanticAnalyzer    → Deep query understanding        │
│  LLMEngine           → OpenAI GPT-4 integration        │
│  WebSearchEngine     → Real-time supplier research     │
│  VectorStoreManager  → ChromaDB vector embeddings      │
│  DocumentProcessor   → Chunks & indexes documents      │
└────────────────────────────────────────────────────────┘
```

### Layer 4: Multi-Agent Orchestration
```
┌──────────────────────────────────────────────────────────────────┐
│  SupplierCoachingOrchestrator (Main Coordinator)                 │
├──────────────────────────────────────────────────────────────────┤
│                                                                   │
│  BRANCH 1: Data Analysis & Quantification                        │
│  ├── SpendAnalyzerAgent          (Category spend patterns)       │
│  ├── ThresholdTrackerAgent       (Track KPI thresholds)          │
│  ├── RegionalConcentrationAgent  (Geographic risk)               │
│  └── PatternDetectorAgent        (Spend trends)                  │
│                                                                   │
│  BRANCH 2: Personalized Recommendations                          │
│  └── PersonalizedCoachAgent      (Coaching insights)             │
│                                                                   │
│  BRANCH 3: Incumbent Supplier Strategy                           │
│  └── IncumbentStrategyAgent      (Supplier optimization)         │
│                                                                   │
│  BRANCH 4: Additional Region Sourcing                            │
│  └── EnhancedRegionSourcingAgent (Geographic diversification)    │
│                                                                   │
│  BRANCH 5: System Architecture                                   │
│  ├── WebScrapingAgent            (Market intelligence)           │
│  └── ParameterTuningEngine       (System optimization)           │
│                                                                   │
│  ADVANCED MODULES (EnhancedOrchestrator):                        │
│  ├── TariffCalculatorAgent       (27 products, 150+ routes)      │
│  ├── LeadingQuestionsModule      (Information gathering)         │
│  ├── CostAndRiskLoopEngine       (Cost-risk optimization)        │
│  ├── ClientCriteriaMatchingEngine(Supplier matching)             │
│  └── VisualWorkflowGenerator     (Diagram generation)            │
│                                                                   │
└──────────────────────────────────────────────────────────────────┘
```

### Layer 5: Intelligence & Analysis Engines
```
┌─────────────────────────────────────────────────┐
│  Specialized Intelligence Engines               │
├─────────────────────────────────────────────────┤
│  LeadershipBriefGenerator    → Executive briefs │
│  ScenarioAnalyzer            → What-if analysis │
│  RecommendationGenerator     → Actionable plans │
│  SavingsCalculator           → Financial impact │
│  ActionPlanGenerator         → Implementation  │
│  ImplementationRoadmap       → Timeline & KPIs │
│  TariffCalculatorAgent       → Global tariffs │
│  ComplianceAnalyzer          → Rule validation │
│  BriefFormatter              → Output formats  │
│  DOCXExporter                → Word generation │
└─────────────────────────────────────────────────┘
```

### Layer 6: Data Corpus Management
```
┌────────────────────────────────────────────┐
│  THREE DATA CORPUSES                       │
├────────────────────────────────────────────┤
│  STRUCTURED DATA (11 CSV files)            │
│  ├── spend_data.csv               (156 rows)│
│  ├── supplier_master.csv          (96 suppliers)
│  ├── client_master.csv            (17 clients)
│  ├── rule_book.csv                (35 rules)
│  ├── supplier_contracts.csv       (contracts)
│  ├── pricing_benchmarks.csv       (market data)
│  └── + 5 more benchmark/reference │
│                                    │
│  UNSTRUCTURED DATA (15 documents) │
│  ├── policies/                    (7 industry)
│  ├── best_practices/              (2 guides)
│  ├── contracts/                   (2 samples)
│  ├── risk_assessments/            (1 report)
│  └── + more documents             │
│                                    │
│  CALCULATED/DERIVED DATA          │
│  ├── calculated_metrics.csv       (KPIs)
│  ├── forecasts_projections.csv    (3-year)
│  ├── action_plan.csv              (steps)
│  ├── scenario_planning.csv        (scenarios)
│  └── risk_register.csv            (risks)
│                                    │
│  VECTOR DATABASE                  │
│  └── vector_db/ (ChromaDB)        │
│      └── Embeddings for RAG       │
└────────────────────────────────────────────┘
```

### Layer 7: Output & Integration
```
┌────────────────────────────────────────────┐
│  Output Generation & Export                │
├────────────────────────────────────────────┤
│  Word Documents (.docx)                    │
│  ├── Leadership Briefs                     │
│  ├── Supplier Scorecards                   │
│  └── Implementation Roadmaps               │
│                                            │
│  JSON/CSV Exports                          │
│  ├── Coaching session data                 │
│  ├── Analysis results                      │
│  └── Action plans                          │
│                                            │
│  Streamlit Dashboard                       │
│  ├── Real-time visualizations              │
│  ├── Interactive charts                    │
│  └── Downloadable reports                  │
│                                            │
│  API Endpoints (FastAPI)                   │
│  ├── REST API for external systems         │
│  └── Real-time data access                 │
└────────────────────────────────────────────┘
```

---

## 4. COMPLETE END-TO-END WORKFLOW

### SCENARIO: User Asks "Find suppliers for Rice Bran Oil in India with best pricing"

```
╔════════════════════════════════════════════════════════════════════════════╗
║                      END-TO-END WORKFLOW DIAGRAM                           ║
╚════════════════════════════════════════════════════════════════════════════╝

STEP 1: INPUT PROCESSING
┌─────────────────────────────────────────────────────────────────┐
│ User Question: "Find suppliers for Rice Bran Oil in India       │
│                with best pricing"                               │
└─────────────────────────────────────────────────────────────────┘
                         ↓
                    app.py or main.py
                         ↓
        ┌───────────────────────────────────┐
        │ SemanticQueryAnalyzer             │
        ├───────────────────────────────────┤
        │ EXTRACT ENTITIES:                 │
        │ • Product: Rice Bran Oil          │
        │ • Region: India                   │
        │ • Metric: pricing (cost)          │
        │ • Action: Find/Rank suppliers     │
        └───────────────────────────────────┘

STEP 2: INTELLIGENT ROUTING (Priority Based)
┌──────────────────────────────────────────────────────────────────┐
│ SOURCE 1: YOUR DATA (CSV Files) - HIGHEST PRIORITY              │
│                                                                   │
│  DataLoader.load_spend_data()                                    │
│  ↓                                                                │
│  Filter: Category = 'Rice Bran Oil', Supplier_Country = 'India' │
│  ↓                                                                │
│  Results: Malaya Agri Oils, Borneo Nutrients, etc.              │
│           With prices: $1,285/MT avg                             │
│                                                                   │
│  RuleEngine.evaluate_all_rules()                                 │
│  ↓                                                                │
│  Check: R001 (Regional concentration)                            │
│         R003 (Supplier dependency)                               │
│         R012 (Pricing benchmarks)                                │
└──────────────────────────────────────────────────────────────────┘
                         ↓
┌──────────────────────────────────────────────────────────────────┐
│ SOURCE 2: YOUR POLICIES (RAG Vector DB) - HIGH PRIORITY         │
│                                                                   │
│  VectorStoreManager.search(                                      │
│    query="Rice Bran Oil supplier India pricing",                │
│    top_k=5                                                       │
│  )                                                                │
│  ↓                                                                │
│  Retrieve from policies/:                                        │
│  • master_procurement_policy.md                                  │
│  • best_practices/vegetable_oil_procurement.md                  │
│  • supplier_contracts.csv references                            │
│  ↓                                                                │
│  Results: Preferred certifications (ISO 22000, HACCP)           │
│           Payment terms (Net 60-90)                              │
│           Quality thresholds                                     │
└──────────────────────────────────────────────────────────────────┘
                         ↓
┌──────────────────────────────────────────────────────────────────┐
│ SOURCE 3: WEB SEARCH (Real-time Intelligence) - MEDIUM PRIORITY │
│                                                                   │
│  IntelligentSearchEngine.search(                                 │
│    "Rice Bran Oil suppliers India prices 2025"                 │
│  )                                                                │
│  ↓                                                                │
│  WebScrapingAgent.scrape()                                       │
│  ↓                                                                │
│  Results: Current market prices                                  │
│           New suppliers emerging                                 │
│           Trade regulations changes                              │
└──────────────────────────────────────────────────────────────────┘
                         ↓
┌──────────────────────────────────────────────────────────────────┐
│ SOURCE 4: LLM REASONING (GPT-4 Analysis) - LOW PRIORITY         │
│                                                                   │
│  LLMEngine.analyze(                                              │
│    context = [CSV data + policies + web search results],         │
│    query = original question                                     │
│  )                                                                │
│  ↓                                                                │
│  GPT-4 synthesizes all data:                                     │
│  • Ranks suppliers by quality/price/risk                         │
│  • Generates recommendations                                     │
│  • Calculates cost savings potential                             │
│  • Identifies risks                                              │
└──────────────────────────────────────────────────────────────────┘

STEP 3: SPECIALIZED AGENT EXECUTION (If Needed)
┌──────────────────────────────────────────────────────────────────┐
│ For supplier ranking, execute agents:                            │
│                                                                   │
│  SupplierCoachingOrchestrator.execute({                         │
│    'client_id': 'C001',                                          │
│    'category': 'Rice Bran Oil',                                  │
│    'region': 'India'                                             │
│  })                                                               │
│                                                                   │
│  ↓ BRANCH 1: Data Analysis                                       │
│  SpendAnalyzerAgent                                              │
│    • Historical spend: $4.2M/year                                │
│    • Volume: 3,250 MT                                            │
│    • Concentration: 93.55% APAC                                  │
│                                                                   │
│  ↓ BRANCH 4: Region Sourcing                                     │
│  EnhancedRegionSourcingAgent                                     │
│    • Alternate regions: Indonesia, Vietnam                       │
│    • New suppliers: 5-7 candidates                               │
│    • Cost delta: -8-12% vs current                               │
│                                                                   │
│  ↓ ADVANCED: Tariff Analysis                                     │
│  TariffCalculatorAgent                                           │
│    • India → USA tariff: 12.5%                                   │
│    • Logistics: $280/MT                                          │
│    • Total landed cost: $1,623/MT                                │
│    • 3-year projection: tariff stable                            │
│                                                                   │
│  ↓ ADVANCED: Criteria Matching                                   │
│  ClientCriteriaMatchingEngine                                    │
│    • ISO 22000: ✓ Malaya Agri Oils, ✓ Borneo Nutrients         │
│    • HACCP: ✓ All India suppliers                                │
│    • Capacity: 500K+ MT ✓                                        │
│    • Match Score: 92%, 88%, 85%                                  │
│                                                                   │
│  ↓ BRANCH 2: Personalized Recommendations                        │
│  PersonalizedCoachAgent                                          │
│    → Top pick: Malaya Agri Oils (92% match)                      │
│    → Backup: Borneo Nutrients (88% match)                        │
│    → Risk: Regional concentration (needs diversification)        │
│                                                                   │
│  ↓ ACTION PLAN GENERATION                                        │
│  ActionPlanGeneratorAgent                                        │
│    1. Week 1-2: RFQ to 3 India suppliers                         │
│    2. Week 3-4: Quality audits                                   │
│    3. Week 5-6: Negotiate pricing                                │
│    4. Week 7-8: Pilot 500 MT                                     │
│    5. Week 9-12: Full scale-up                                   │
│                                                                   │
└──────────────────────────────────────────────────────────────────┘

STEP 4: RESPONSE GENERATION & FORMATTING
┌──────────────────────────────────────────────────────────────────┐
│ ConversationalAI.answer_question() builds response:              │
│                                                                   │
│ • Combine results from all sources                               │
│ • Structure in natural language                                  │
│ • Add data sources & citations                                   │
│ • Include confidence scores                                      │
│ • Provide next steps/recommendations                             │
│ • Store in conversation memory                                   │
│                                                                   │
│ OUTPUT FORMAT OPTIONS:                                           │
│ 1. Console (CLI) - Formatted text                                │
│ 2. Streamlit UI - Interactive cards/tables                       │
│ 3. Word Document - Professional brief                            │
│ 4. JSON API - Structured data                                    │
│ 5. CSV Export - Spreadsheet format                               │
└──────────────────────────────────────────────────────────────────┘

STEP 5: OPTIONAL - GENERATE FORMAL OUTPUTS
┌──────────────────────────────────────────────────────────────────┐
│ If user requests full analysis:                                  │
│                                                                   │
│  LeadershipBriefGenerator.generate_both_briefs()                │
│  ├── Incumbent Concentration Brief                               │
│  │   • Current supplier dependencies                             │
│  │   • Risk assessment                                           │
│  │   • ROI projections                                           │
│  │   • Implementation timeline                                   │
│  │                                                                │
│  └── Regional Concentration Brief                                │
│      • Geographic diversification                                │
│      • New region opportunities                                  │
│      • Cost advantages                                           │
│      • Success probability                                       │
│                                                                   │
│  DOCXExporter.export()                                           │
│  → Generates professional Word documents                         │
│     with charts, tables, executive summary                       │
│                                                                   │
│  Output: coaching_session_COACHING_20251231_120000.json         │
│         (with full session data)                                 │
└──────────────────────────────────────────────────────────────────┘

STEP 6: RULE VALIDATION & COMPLIANCE CHECK
┌──────────────────────────────────────────────────────────────────┐
│ Automatic rule evaluation:                                       │
│                                                                   │
│ RuleEvaluationEngine.evaluate_all_rules()                        │
│ ├── R001: Regional Concentration                                 │
│ │   Current: 93.55% APAC → VIOLATION (>40%)                     │
│ │   Recommendation: Diversify to India/Vietnam                   │
│ │                                                                 │
│ ├── R003: Supplier Dependency                                    │
│ │   Current: 85% Malaya Agri → WARNING (>60%)                   │
│ │   Action: Add Borneo Nutrients (10-15% allocation)            │
│ │                                                                 │
│ └── R012: Pricing Threshold                                      │
│     Current: $1,285/MT vs Market: $1,310/MT → COMPLIANT         │
│     Recommendation: Negotiate down to $1,250/MT                 │
│                                                                   │
│ SaveingsCalculator.calculate()                                   │
│ → Potential savings: $78K-$156K/year                             │
└──────────────────────────────────────────────────────────────────┘

FINAL OUTPUT TO USER
┌──────────────────────────────────────────────────────────────────┐
│ TOP SUPPLIERS FOR RICE BRAN OIL IN INDIA:                        │
│                                                                   │
│ 1. 🥇 Malaya Agri Oils (92% Match)                              │
│    • Price: $1,280/MT (2% savings)                               │
│    • Quality: 4.5/5 (ISO 22000, HACCP)                           │
│    • Delivery: 14 days, 92% on-time                              │
│    • Capacity: 500K MT/year ✓                                    │
│    • Risk: Low                                                    │
│    • Action: Start RFQ immediately                               │
│                                                                   │
│ 2. 🥈 Borneo Nutrients (88% Match)                              │
│    • Price: $1,295/MT                                            │
│    • Quality: 4.3/5 (ISO 22000, HACCP)                           │
│    • Delivery: 15 days, 90% on-time                              │
│    • Capacity: 450K MT/year ✓                                    │
│    • Risk: Low-Medium                                            │
│    • Action: Pilot program (500 MT)                              │
│                                                                   │
│ 3. 🥉 Golden Sun Oils (Ukraine) (75% Match)                     │
│    • Price: $1,310/MT                                            │
│    • Quality: 4.6/5 (Organic certified)                          │
│    • Risk: Geopolitical (Europe)                                 │
│    • Action: Backup option only                                  │
│                                                                   │
│ SOURCES:                                                          │
│ • spend_data.csv (historical transactions)                       │
│ • supplier_master.csv (supplier profiles)                        │
│ • master_procurement_policy.md (policy compliance)               │
│ • Web search (current market prices, Jan 2025)                   │
│ • Tariff Calculator (landing costs)                              │
│                                                                   │
│ NEXT STEPS:                                                      │
│ 1. Confirm requirements with procurement team                    │
│ 2. Issue RFQ to Malaya Agri Oils                                 │
│ 3. Request samples for quality testing                           │
│ 4. Plan site audit in India                                      │
│ 5. Timeline: 12 weeks to full commercial agreement               │
└──────────────────────────────────────────────────────────────────┘
```

---

## 5. KEY COMPONENTS DETAIL

### 5.1 ConversationalAI Class (1,043 lines)
**Purpose**: Main chatbot orchestrator

**Key Methods**:
- `__init__()` - Initialize all engines
- `answer_question(question)` - Route query to appropriate sources
- `chat()` - REPL mode interaction

**Data Sources Loaded**:
- Spend data (live from CSV)
- Supplier contracts
- Regional summaries
- Pre-evaluated rules

### 5.2 SupplierCoachingOrchestrator (556 lines)
**Purpose**: Master coordinator for coaching workflow

**5 Main Branches**:
1. **Data Analysis** - Spend, thresholds, regional risk, patterns
2. **Personalized Recommendations** - Coaching insights
3. **Incumbent Strategy** - Supplier optimization
4. **Region Sourcing** - Geographic diversification
5. **System Architecture** - Parameter tuning, web scraping

**Execution Flow**:
```
execute() → Branch 1 → Branch 5 → Branch 3 → Branch 4 → Branch 2
         → Executive Summary → Action Plan → Scoring
```

### 5.3 EnhancedSupplierCoachingOrchestrator (389 lines)
**Purpose**: Extended version with advanced modules

**Additional Modules**:
- TariffCalculatorAgent - 27 products, 150+ routes, WTO/ITC data
- LeadingQuestionsModule - Structured information gathering
- CostAndRiskLoopEngine - Cost/risk optimization
- ClientCriteriaMatchingEngine - Supplier matching
- VisualWorkflowGenerator - Diagram creation

### 5.4 TariffCalculatorAgent (intelligence/tariff_calculator.py)
**Purpose**: Global tariff impact analysis

**Data Coverage**:
- **27 Products**: Oils (5), IT (4), Materials (4), Equipment (4), Pharma (3), Software (2)
- **150+ Routes**: All major trading regions (US, EU, APAC, Americas, Africa)
- **Real Data**: WTO & ITC verified tariff rates
- **Logistics**: 85+ routes with shipping costs
- **Trends**: 3-year tariff projections

**Key Methods**:
- `execute()` - Calculate tariff impact for origin→destination
- `_calculate_tariff_impact()` - Base tariff calculation
- `_project_tariff_trends()` - 3-year forecast
- `_assess_tariff_risk()` - Geopolitical risk scoring

### 5.5 Leadership Brief Generator (engines/leadership_brief_generator.py)
**Purpose**: Executive-level business briefs

**Output Types**:
1. **Incumbent Concentration Brief**
   - Supplier dependency analysis
   - Risk statements
   - Target allocation
   - Cost advantage projections
   - ROI calculations

2. **Regional Concentration Brief**
   - Geographic dependency
   - Alternative region options
   - Diversification opportunities
   - Implementation timeline

---

## 6. DATA FLOW ARCHITECTURE

```
USER INPUT (Any Interface)
    ↓
SEMANTIC ANALYZER
    ├─ Extract intent
    ├─ Identify entities
    └─ Generate sub-queries
    ↓
INTELLIGENT ROUTER
    ├─ Priority 1: CSV Data (DataLoader)
    ├─ Priority 2: Policies (RAGEngine)
    ├─ Priority 3: Web Search (IntelligentSearchEngine)
    └─ Priority 4: LLM Reasoning (LLMEngine)
    ↓
CONTEXT BUILDERS
    ├─ RuleEngine → Rule violations
    ├─ ScenarioDetector → Analysis scenarios
    ├─ RecommendationGenerator → Actionable insights
    └─ TariffCalculator → Global trade impacts
    ↓
SPECIALIZED AGENTS (if needed)
    ├─ SpendAnalyzer
    ├─ SupplierCoachingOrchestrator
    ├─ TariffCalculator
    └─ ... 12+ more agents
    ↓
SYNTHESIS ENGINE
    ├─ Combine all results
    ├─ Structure response
    ├─ Add citations
    └─ Calculate confidence
    ↓
OUTPUT FORMATTER
    ├─ Console text
    ├─ Streamlit UI
    ├─ Word documents
    ├─ JSON API
    └─ CSV export
    ↓
CONVERSATION MEMORY
    └─ Store for session history
```

---

## 7. RULE EVALUATION SYSTEM

**35+ Procurement Rules (R001-R035)**

### Hard Constraints (Must be satisfied)
- **R001**: Regional Concentration (max 40%)
- **R003**: Supplier Dependency (max 60%)
- **R023**: Supplier Concentration Index (HHI calculation)

### Soft Preferences (Scored/ranked)
- **R012**: Pricing Benchmarks vs market
- **R015**: Quality thresholds
- **R018**: Delivery reliability targets

### Risk Assessment Rules
- **RA001-RA006**: Supply chain risk scoring
- Geopolitical risk
- Financial stability
- Sustainability metrics

---

## 8. WORKFLOW MODES & USE CASES

### Mode 1: Interactive Chat (main.py)
```
User → Q&A → AI answers from all sources → Store memory → Next Q
```

### Mode 2: Coaching Analysis (app.py)
```
User selects client → Orchestrator runs all 5 branches → Generates briefs → Export
```

### Mode 3: Rule Violation Fix
```
Rule violated → Scenario detected → Agent finds solutions → Action plan generated
```

### Mode 4: Supplier Sourcing
```
Category + region → All agents analyze → Ranking → Comparison → Recommendation
```

### Mode 5: Cost Optimization
```
Current spend → Alternatives identified → Savings calculated → Implementation plan
```

---

## 9. DEPLOYMENT ARCHITECTURE

```
┌─────────────────────────────────────────────────┐
│             Virtual Environment                 │
│            (Beroe_Env - Python 3.10)            │
└─────────────────────────────────────────────────┘
                      ↓
    ┌─────────────────┬─────────────────┐
    ↓                 ↓                   ↓
 app.py          main.py              FastAPI
 (Streamlit)     (CLI Chat)           (Endpoints)
    ↓                 ↓                   ↓
    └─────────────────┴─────────────────┘
              ↓
    ┌────────────────────────────────┐
    │  Backend Core System            │
    │  (/backend/)                    │
    ├────────────────────────────────┤
    │  • conversational_ai.py         │
    │  • agents/ (15+ agents)         │
    │  • engines/ (10+ engines)       │
    └────────────────────────────────┘
              ↓
    ┌────────────────────────────────┐
    │  Data & Configuration           │
    ├────────────────────────────────┤
    │  • data/structured/ (11 CSVs)  │
    │  • data/unstructured/ (15 docs)│
    │  • data/vector_db/ (ChromaDB)  │
    │  • data/calculated/ (metrics)  │
    │  • rules/ (rule_book.json)     │
    └────────────────────────────────┘
              ↓
    ┌────────────────────────────────┐
    │  External Services              │
    ├────────────────────────────────┤
    │  • OpenAI GPT-4 API             │
    │  • Web Search API               │
    │  • ChromaDB Vector Store        │
    └────────────────────────────────┘
```

---

## 10. SYSTEM CAPABILITIES SUMMARY

| Capability | Detail |
|-----------|--------|
| **Industries** | 7 (Food, IT, Manufacturing, Equipment, Healthcare, Construction, Energy) |
| **Products** | 27 with real tariff data |
| **Trade Routes** | 150+ international routes |
| **Procurement Rules** | 35 (R001-R035) with hard/soft constraints |
| **Agents** | 15+ specialized agents in 5 branches |
| **Engines** | 10+ processing engines |
| **Data Sources** | 3 corpuses: Structured + Unstructured + Calculated |
| **Knowledge Base** | 15 policy/intelligence documents |
| **Vector DB** | ChromaDB with OpenAI embeddings |
| **LLM** | OpenAI GPT-4 (reasoning, embeddings) |
| **Output Formats** | Streamlit UI, CLI, Word docs, JSON, CSV, API |
| **Rule Validation** | Real-time constraint checking |
| **Traceability** | Full source citations for all answers |
| **Response Time** | <2 seconds for data queries, 5-10s for full analysis |

---

## 11. EXAMPLE COMPLETE REQUEST FLOW

**USER REQUEST**: "Show me the risk of our Rice Bran Oil supply and give me recommendations"

```
INPUT
├─ Interface: Streamlit "Supplier Coaching" page
├─ Client: C001 (Global Foods Corp)
├─ Category: Rice Bran Oil
└─ Analysis type: Full coaching

PROCESSING
├─ Step 1: Query processed by ConversationalAI
├─ Step 2: Entities extracted: Product, Client, Analysis type
├─ Step 3: Route to Coaching Orchestrator
├─ Step 4: Execute 5-branch analysis
│   ├─ Branch 1: Spend analysis
│   │   • Total: $4.2M/year
│   │   • Suppliers: 2 (Malaya Agri, Borneo)
│   │   • Concentration: 93.55% APAC
│   │
│   ├─ Branch 5: Tariff analysis
│   │   • Current route: Malaysia→USA
│   │   • Tariff: 12.5%
│   │   • Logistics: $280/MT
│   │
│   ├─ Branch 3: Incumbent strategy
│   │   • Malaya Agri: 85% dependency
│   │   • Risk: HIGH
│   │   • Mitigation: Diversify
│   │
│   ├─ Branch 4: Regional sourcing
│   │   • New options: Indonesia, Vietnam, India
│   │   • Cost benefit: -8-12%
│   │
│   └─ Branch 2: Recommendations
│       • Diversify to 3+ suppliers
│       • Reduce APAC to <40%
│       • Pilot with Indonesia
│
├─ Step 5: Rule evaluation
│   • R001 violation: 93.55% > 40%
│   • R003 violation: 85% > 60%
│
├─ Step 6: Generate outputs
│   • Leadership brief (incumbent concentration)
│   • Action plan (8-week implementation)
│   • Scenario analysis (optimistic/pessimistic)
│   • Savings calculator: $156K-$312K/year
│
└─ Step 7: Export (Word, JSON, CSV)

OUTPUT
├─ Streamlit dashboard with charts
├─ Word document "Incumbent_Concentration_Brief.docx"
├─ JSON session data
└─ Action plan with timelines
```

---

## CONCLUSION

This system represents an **enterprise-grade, production-ready procurement AI** with:
- ✅ Real data integration across 3 corpuses
- ✅ Advanced multi-agent orchestration
- ✅ Global tariff & trade analysis
- ✅ Rule-based compliance checking
- ✅ RAG for policy retrieval
- ✅ LLM reasoning for insights
- ✅ Multiple output formats
- ✅ Full traceability & explainability

**Ready for deployment across any organization's procurement needs.**
