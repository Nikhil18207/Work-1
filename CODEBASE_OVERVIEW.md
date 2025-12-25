# 🧠 Complete Codebase Overview - LLM Recommendation System

## 📋 Table of Contents
1. [System Architecture](#system-architecture)
2. [Core Components](#core-components)
3. [Data Architecture](#data-architecture)
4. [Engine Modules](#engine-modules)
5. [API & Interfaces](#api--interfaces)
6. [Workflows & Usage](#workflows--usage)
7. [Configuration & Setup](#configuration--setup)
8. [Key Features](#key-features)

---

## 🏗️ System Architecture

### High-Level Overview
This is an **enterprise-grade LLM-powered procurement recommendation system** built for food procurement decisions, specifically focusing on vegetable oils and food items. The system combines:

- **Rule-Based Governance**: 35+ comprehensive procurement rules
- **RAG (Retrieval Augmented Generation)**: Semantic search over procurement knowledge base
- **Real-Time Web Search**: Live market intelligence and supplier research
- **Data-Driven Analysis**: Three-tier data corpus (Structured, Unstructured, Calculated)
- **Full Traceability**: Complete audit trails and explainability

### Technology Stack
- **Backend**: Python 3.10+, FastAPI
- **LLM Providers**: OpenAI (GPT-4) / Google Gemini
- **Vector Database**: ChromaDB
- **Document Processing**: LangChain
- **Data Processing**: Pandas, NumPy
- **Web Search**: Serper API / Google Custom Search

---

## 🔧 Core Components

### 1. **Conversational AI** (`backend/conversational_ai.py`)
**Purpose**: Main interface for user interaction - real-time Q&A system

**Key Features**:
- Pattern-based question routing
- Multi-source answer generation (Data, RAG, Web Search, LLM)
- Interactive chat interface
- Context-aware responses

**Main Methods**:
```python
answer_question(question: str) -> str
  ├─ _answer_about_risks()
  ├─ _answer_about_suppliers()
  ├─ _answer_about_spend()
  ├─ _answer_about_regions()
  ├─ _answer_with_rag(question)
  ├─ _answer_with_web_search(question)
  └─ _answer_with_llm(question)
```

**Question Patterns Handled**:
- Risks & risk assessment
- Supplier information
- Spend analysis & breakdown
- Regional distribution
- Rules & compliance
- Recommended actions
- ESG & sustainability
- Timeline & delivery
- General queries (via RAG/LLM)

---

### 2. **LLM Recommendation System** (`backend/llm_recommendation_system.py`)
**Purpose**: Core recommendation engine with LLM integration

**Key Features**:
- Multi-provider LLM support (OpenAI/Gemini)
- Natural language explanations
- Confidence scoring
- Web search integration
- RAG-powered recommendations

**Main Methods**:
```python
get_recommendation(category, client_id, include_llm_explanation)
ask_question(category, question)
analyze_category(category)
analyze_supplier(supplier_id)
get_regional_analysis()
search_supplier_news(supplier_name, region)
search_market_intelligence(product_category, region)
search_top_suppliers(product_category, region)
query_knowledge_base(question, k, category)
get_rag_recommendation(scenario, context_data, k)
semantic_search(query, k, category)
```

---

## 📊 Data Architecture

### Three-Tier Data Corpus

#### 1. **Structured Data** (`data/structured/`)
CSV files containing quantitative, tabular data:

| File | Description | Key Columns |
|------|-------------|-------------|
| `client_master.csv` | Client information & requirements | client_id, client_name, industry, region, certifications_required |
| `spend_data.csv` | Historical procurement transactions | Client_ID, Category, Supplier_ID, Transaction_Date, Spend_USD |
| `supplier_master.csv` | Supplier capabilities & details | supplier_id, supplier_name, region, certifications, quality_rating |
| `pricing_benchmarks.csv` | Market pricing benchmarks | product, region, benchmark_price, volatility_index |
| `proof_points.csv` | Historical performance data | supplier_id, metric, value, date |
| `rule_book.csv` | Business rules (35+ rules) | Rule_ID, Rule_Name, Threshold_Value, Risk_Level |

**Sample Data Flow**:
```
Client C001 → Rice Bran Oil → 85% spend in Malaysia (S001-S004)
                            → 15% diversified (S005-S024 across regions)
```

#### 2. **Unstructured Data** (`data/unstructured/`)
Document-based qualitative information:

```
unstructured/
├── policies/
│   ├── comprehensive_procurement_policy.md
│   └── supplier_selection_guidelines.md
├── contracts/
│   ├── master_supplier_agreement.md
│   └── payment_terms_template.md
├── best_practices/
│   └── procurement_best_practices.md
├── company_policies/
│   └── company_procurement_rules.md
├── risk_assessments/
│   └── regional_risk_analysis.md
├── historical_analysis/
│   └── spend_analysis_2023.md
└── news/
    └── market_updates.md
```

**RAG Processing**:
1. Documents loaded via `DocumentProcessor`
2. Chunked into 1000-char segments (200-char overlap)
3. Embedded using OpenAI/Gemini embeddings
4. Stored in ChromaDB vector database
5. Retrieved via semantic search

#### 3. **Calculated/Derived Data** (`data/calculated/`)
Generated from structured data + rules:

| File | Description | Generated From |
|------|-------------|----------------|
| `risk_register.csv` | Risk assessments | Rule engine + spend data |
| `savings_calculations.csv` | Cost savings analysis | Pricing benchmarks + spend |
| `compliance_flags.csv` | Rule violations | Rule book + supplier data |

---

## ⚙️ Engine Modules

### 1. **RAG Engine** (`backend/engines/rag_engine.py`)
**Purpose**: Retrieval Augmented Generation for context-aware recommendations

**Architecture**:
```
User Query
    ↓
Vector Search (ChromaDB)
    ↓
Retrieve Top-K Documents (k=5)
    ↓
Format Context
    ↓
LLM Generation (GPT-4/Gemini)
    ↓
Answer + Sources
```

**Key Methods**:
```python
query(question, k=5, category=None, include_sources=True)
get_procurement_recommendation(scenario, context_data, k=5)
_generate_answer(question, context, verbose=False)
```

**Prompt Structure**:
```
CONTEXT: [Retrieved documents from vector DB]
QUESTION: [User question]
INSTRUCTIONS: Answer based on context, cite sources
```

---

### 2. **Vector Store Manager** (`backend/engines/vector_store_manager.py`)
**Purpose**: Manages ChromaDB vector database for semantic search

**Features**:
- Collection creation & management
- Document embedding (OpenAI/Gemini)
- Similarity search with filtering
- Metadata tracking
- Persistence

**Key Methods**:
```python
create_collection(documents, reset=False)
load_collection()
add_documents(documents)
similarity_search(query, k=5, filter_metadata=None)
semantic_search(query, k=5, category=None)
get_context_for_query(query, k=5)
get_statistics()
```

**Vector DB Structure**:
```
Collection: procurement_docs
├── Embeddings: OpenAI text-embedding-ada-002 (1536 dims)
├── Metadata: {category, source, chunk_id, timestamp}
└── Persistence: ./data/vector_db/
```

---

### 3. **Document Processor** (`backend/engines/document_processor.py`)
**Purpose**: Loads, chunks, and preprocesses documents for RAG

**Supported Formats**:
- Markdown (.md)
- PDF (.pdf)
- Text (.txt)
- CSV (.csv)

**Processing Pipeline**:
```
Load Documents
    ↓
Add Metadata (source, category, timestamp)
    ↓
Chunk Text (1000 chars, 200 overlap)
    ↓
Generate Hash (for deduplication)
    ↓
Return LangChain Documents
```

**Key Methods**:
```python
load_document(file_path)
load_directory(directory, recursive=True)
chunk_documents(documents)
process_unstructured_corpus()
process_structured_policies()
get_document_stats(documents)
```

---

### 4. **Enhanced Rule Engine** (`backend/engines/enhanced_rule_engine.py`)
**Purpose**: Implements 35+ business rules for procurement

**Rule Categories**:
1. **Regional Concentration** (R001): Flags if >70% spend in one region
2. **Tail Spend Fragmentation** (R002): Identifies suppliers with <5% spend
3. **Quality Requirements** (R003-R010)
4. **Pricing Thresholds** (R011-R015)
5. **Sustainability** (R016-R020)
6. **Compliance** (R021-R030)
7. **Risk Assessment** (R031-R035)

**Rule Evaluation**:
```python
evaluate_all_rules(spend_data) -> List[RuleResult]
evaluate_regional_concentration(spend_data)
evaluate_tail_spend_fragmentation(spend_data)
get_triggered_rules(results)
get_highest_risk(results)
```

**Rule Structure**:
```python
RuleResult:
  - rule_id: str
  - rule_name: str
  - triggered: bool
  - risk_level: RiskLevel (CRITICAL/HIGH/MEDIUM/LOW)
  - actual_value: float
  - threshold_value: float
  - action_recommendation: str
```

---

### 5. **Data Loader** (`backend/engines/data_loader.py`)
**Purpose**: Loads and caches all structured data sources

**Cached Data**:
- Spend data
- Supplier contracts
- Rule book
- Client master
- Supplier master
- Pricing benchmarks

**Key Methods**:
```python
load_spend_data(force_reload=False)
load_supplier_contracts(force_reload=False)
load_rule_book(force_reload=False)
load_client_master(force_reload=False)
load_supplier_master(force_reload=False)
load_pricing_benchmarks(force_reload=False)
get_supplier_summary(supplier_id)
get_regional_summary()
get_category_summary(category)
clear_cache()
```

---

### 6. **Web Search Engine** (`backend/engines/web_search_engine.py`)
**Purpose**: Fetches real-time market intelligence from the web

**Supported Providers**:
- Serper API (recommended, 2500 queries/month free)
- Google Custom Search API (100 queries/day free)
- Fallback (helpful messages when no API available)

**Search Types**:
```python
search_supplier_news(supplier_name, region, max_results=5)
search_market_intelligence(product_category, region, max_results=5)
search_top_suppliers(product_category, region, max_results=10)
search_price_trends(product_category, region, max_results=5)
search_regulatory_updates(region, product_category, max_results=5)
```

**Response Format**:
```python
{
  "title": str,
  "snippet": str,
  "link": str,
  "date": str,
  "source": str
}
```

---

### 7. **LLM Engine** (`backend/engines/llm_engine.py`)
**Purpose**: Abstraction layer for multiple LLM providers

**Supported Providers**:
- OpenAI (GPT-4, GPT-3.5-turbo)
- Google Gemini (gemini-pro)

**Key Methods**:
```python
generate(prompt, max_tokens=1000, temperature=0.7)
generate_structured(prompt, schema)
count_tokens(text)
```

---

### 8. **Confidence Calculator** (`backend/engines/confidence_calculator.py`)
**Purpose**: Calculates dynamic confidence scores for recommendations

**Confidence Formula**:
```
confidence = base_confidence (50%)
           + SUM(rule_satisfaction_boosts)
           + SUM(data_completeness_boosts)
           - SUM(risk_penalties)
           - SUM(data_gap_penalties)
```

**Data Gap Analysis**:
- Identifies missing critical data points
- Quantifies impact on confidence
- Suggests questions to ask for improvement

---

### 9. **Intelligent Search Engine** (`backend/engines/intelligent_search_engine.py`)
**Purpose**: Routes queries to appropriate search method (data/RAG/web)

**Query Classification**:
- Data queries → DataLoader
- Knowledge queries → RAG Engine
- Real-time queries → Web Search
- Complex queries → LLM reasoning

---

## 🌐 API & Interfaces

### FastAPI Backend (`backend/main.py`)
```python
from fastapi import FastAPI
from backend.api.routes import recommendation_router

app = FastAPI(title="Procurement AI API")
app.include_router(recommendation_router, prefix="/api/v1")

# Endpoints:
# POST /api/v1/chat
# POST /api/v1/query-knowledge
# POST /api/v1/recommend
# GET  /api/v1/suppliers
# GET  /api/v1/clients
# GET  /api/v1/benchmarks/{category}
```

### API Routes (`backend/api/routes.py`)

#### 1. **Chat Endpoint**
```python
POST /api/v1/chat
Request: { "message": "What are the risks?" }
Response: { "answer": "..." }
```

#### 2. **Knowledge Base Query**
```python
POST /api/v1/query-knowledge
Request: { "message": "What are supplier selection criteria?" }
Response: { "answer": "...", "sources": [...] }
```

#### 3. **Recommendation Endpoint**
```python
POST /api/v1/recommend
Request: {
  "query": "Recommend supplier for 50,000 liters sunflower oil",
  "client_id": "C001",
  "product_category": "Sunflower Oil"
}
Response: {
  "recommendation": {...},
  "confidence_score": 0.78,
  "pricing_analysis": {...},
  "risk_assessment": {...},
  "reasoning": "...",
  "next_steps": [...]
}
```

---

## 🔄 Workflows & Usage

### Setup Workflow

#### 1. **Environment Setup**
```bash
# Create virtual environment
python -m venv Beroe_Env
.\Beroe_Env\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your API keys
```

#### 2. **RAG Setup** (One-time)
```bash
# Setup RAG with OpenAI
python scripts/setup_rag.py

# OR setup RAG with Gemini
python scripts/setup_rag_gemini.py
```

**What this does**:
1. Loads all unstructured documents
2. Chunks documents (1000 chars, 200 overlap)
3. Generates embeddings
4. Creates ChromaDB collection
5. Persists to `./data/vector_db/`

#### 3. **Run the System**

**Option A: Conversational AI (Recommended)**
```bash
python main.py
```
Features: Data Analysis + Web Search + RAG + LLM

**Option B: Quick Start (No RAG)**
```bash
python quick_start.py
```
Features: Data Analysis + Web Search + LLM

**Option C: API Server**
```bash
cd backend
python main.py
# API available at http://localhost:8000
# Docs at http://localhost:8000/docs
```

---

### Usage Examples

#### Example 1: Risk Analysis
```
User: "What are the risks?"

System:
  1. Detects "risk" pattern
  2. Calls _answer_about_risks()
  3. Loads spend data via DataLoader
  4. Runs rule engine (evaluate_all_rules)
  5. Formats triggered rules
  6. Returns risk summary
```

#### Example 2: Supplier Research
```
User: "Find top Rice Bran Oil suppliers in India"

System:
  1. Detects "find" + "supplier" pattern
  2. Calls _answer_with_web_search()
  3. WebSearchEngine.search_top_suppliers("Rice Bran Oil", "India")
  4. Fetches from Serper/Google API
  5. Formats results
  6. Returns supplier list with links
```

#### Example 3: Policy Question
```
User: "What are the key criteria for supplier selection?"

System:
  1. Detects knowledge-based question
  2. Calls _answer_with_rag()
  3. RAGEngine.query("supplier selection criteria")
  4. Vector search in ChromaDB
  5. Retrieves relevant policy documents
  6. LLM generates answer with sources
  7. Returns answer + citations
```

#### Example 4: Spend Analysis
```
User: "Show me the spend breakdown"

System:
  1. Detects "spend" pattern
  2. Calls _answer_about_spend()
  3. DataLoader.get_category_summary()
  4. Calculates totals, averages, distributions
  5. Formats as readable text
  6. Returns spend analysis
```

---

## 🛠️ Configuration & Setup

### Environment Variables (`.env`)
```bash
# LLM Providers
OPENAI_API_KEY=sk-...
GEMINI_API_KEY=...

# Web Search
SERPER_API_KEY=...
GOOGLE_SEARCH_API_KEY=...
```

### Rule Book (`rules/rule_book.json`)
```json
{
  "rule_book_version": "1.0",
  "hard_constraints": {
    "rules": [
      {
        "rule_id": "HC001",
        "category": "food_safety",
        "name": "Mandatory Food Safety Certification",
        "condition": "supplier.certifications MUST contain 'ISO 22000' OR 'HACCP'",
        "penalty_if_violated": "REJECT_RECOMMENDATION"
      }
    ]
  },
  "soft_preferences": {
    "rules": [
      {
        "rule_id": "SP001",
        "category": "sustainability",
        "name": "High Sustainability Score",
        "condition": "supplier.sustainability_score >= 8.0",
        "weight": 15,
        "confidence_boost": 0.08
      }
    ]
  },
  "risk_assessment_rules": {...},
  "data_completeness_rules": {...},
  "escalation_rules": {...}
}
```

### Prompts (`config/prompts/`)
- `system_prompt.txt`: Base system instructions
- `recommendation_prompt.txt`: Recommendation generation template
- `rag_prompt.txt`: RAG query template

---

## ✨ Key Features

### 1. **Multi-Source Intelligence**
- **Structured Data**: CSV files for quantitative analysis
- **Unstructured Data**: Documents for qualitative insights
- **Web Search**: Real-time market intelligence
- **LLM Reasoning**: AI-powered synthesis

### 2. **RAG Pipeline**
- Semantic search over 20+ procurement documents
- Context-aware answer generation
- Source citation and traceability
- Category filtering (policies, contracts, best practices)

### 3. **Rule-Based Governance**
- 35+ comprehensive procurement rules
- Hard constraints (must satisfy)
- Soft preferences (scoring/ranking)
- Risk assessment rules
- Data completeness rules
- Escalation triggers

### 4. **Confidence Scoring**
- Dynamic confidence calculation
- Data gap analysis
- Missing data impact quantification
- Potential confidence improvement suggestions

### 5. **Full Traceability**
- Structured data IDs used
- Document chunk references
- Rules applied
- Prompt hash
- Model version
- Confidence breakdown

### 6. **Conversational Interface**
- Natural language queries
- Pattern-based routing
- Multi-turn conversations
- Context retention

### 7. **Web Search Integration**
- Supplier news monitoring
- Market intelligence gathering
- Price trend analysis
- Regulatory updates
- Top supplier discovery

---

## 📁 Project Structure Summary

```
Beroe Inc/
├── backend/
│   ├── api/
│   │   ├── __init__.py
│   │   └── routes.py                    # FastAPI endpoints
│   ├── engines/
│   │   ├── confidence_calculator.py     # Confidence scoring
│   │   ├── data_loader.py               # Structured data loading
│   │   ├── document_processor.py        # Document chunking
│   │   ├── enhanced_rule_engine.py      # 35+ business rules
│   │   ├── intelligent_search_engine.py # Query routing
│   │   ├── llm_engine.py                # LLM abstraction
│   │   ├── rag_engine.py                # RAG pipeline
│   │   ├── recommendation_generator.py  # Recommendation logic
│   │   ├── rule_engine.py               # Basic rule engine
│   │   ├── scenario_detector.py         # Query classification
│   │   ├── vector_store_manager.py      # ChromaDB management
│   │   └── web_search_engine.py         # Web search
│   ├── conversational_ai.py             # Main chat interface
│   ├── llm_recommendation_system.py     # Core recommendation system
│   └── main.py                          # FastAPI app
├── data/
│   ├── structured/                      # CSV files
│   │   ├── client_master.csv
│   │   ├── spend_data.csv
│   │   ├── supplier_master.csv
│   │   ├── pricing_benchmarks.csv
│   │   └── rule_book.csv
│   ├── unstructured/                    # Documents
│   │   ├── policies/
│   │   ├── contracts/
│   │   ├── best_practices/
│   │   └── news/
│   ├── calculated/                      # Derived data
│   │   └── risk_register.csv
│   └── vector_db/                       # ChromaDB persistence
├── rules/
│   └── rule_book.json                   # Business rules
├── config/
│   └── prompts/                         # LLM prompts
├── scripts/
│   ├── setup_rag.py                     # RAG setup (OpenAI)
│   ├── setup_rag_gemini.py              # RAG setup (Gemini)
│   └── setup_env.py                     # Environment setup
├── demos/
│   ├── demo_rag.py                      # RAG demo
│   ├── demo_conversational_ai.py        # Chat demo
│   └── demo_intelligent_search.py       # Search demo
├── tests/                               # Unit tests
├── main.py                              # Main entry point
├── quick_start.py                       # Quick start (no RAG)
├── requirements.txt                     # Dependencies
├── .env.example                         # Environment template
└── README.md                            # Documentation
```

---

## 🎯 Data Flow Diagram

```
User Query
    ↓
┌─────────────────────────────────────┐
│   Conversational AI                 │
│   (Pattern Detection)               │
└─────────────────────────────────────┘
    ↓
    ├─→ Risk Query? → Rule Engine → Spend Data
    ├─→ Supplier Query? → Data Loader → Supplier Master
    ├─→ Spend Query? → Data Loader → Spend Data
    ├─→ Region Query? → Data Loader → Regional Summary
    ├─→ Knowledge Query? → RAG Engine → Vector DB → LLM
    ├─→ Web Query? → Web Search Engine → Serper/Google API
    └─→ General Query? → LLM Engine → GPT-4/Gemini
    ↓
Formatted Response
    ↓
User
```

---

## 🔐 Security & Best Practices

### API Key Management
- Store in `.env` file (never commit)
- Use environment variables
- Rotate keys regularly

### Data Privacy
- No PII in logs
- Sanitize user inputs
- Secure API endpoints

### Error Handling
- Graceful degradation
- Fallback mechanisms
- Comprehensive logging

---

## 📈 Performance Optimization

### Caching
- DataLoader caches all CSV files
- Vector store persistence
- LLM response caching (future)

### Chunking Strategy
- 1000 chars per chunk
- 200 char overlap
- Preserves context

### Vector Search
- Top-K retrieval (k=5 default)
- Category filtering
- Score thresholding

---

## 🚀 Future Enhancements

1. **Admin UI**: Web interface for system management
2. **Advanced Analytics**: Dashboards and visualizations
3. **Multi-tenancy**: Support multiple clients
4. **Workflow Automation**: Automated procurement workflows
5. **Integration**: ERP/SAP connectors
6. **Advanced RAG**: Hybrid search, reranking
7. **Fine-tuning**: Custom LLM models
8. **Real-time Monitoring**: System health dashboards

---

## 📞 Support & Contact

For questions or issues:
- Review this documentation
- Check demo files in `demos/`
- Review test files in `tests/`
- Contact: Beroe Inc - Procurement Intelligence Platform

---

**Last Updated**: December 25, 2024
**Version**: 1.0
**Author**: Beroe Inc Development Team
