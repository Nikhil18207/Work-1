# Beroe Universal Procurement AI - Multi-Industry Recommendation System

## Overview

Enterprise-grade **LLM-powered procurement recommendation system** for multi-industry sourcing intelligence. Built with strict data governance, rule-based constraints, RAG capabilities, tariff analysis, and full traceability.

### Supported Industries (7 Total)
- **Food & Beverage** - 27 products including oils, grains, ingredients
- **Information Technology** - Hardware, software, cloud services, cybersecurity
- **Manufacturing** - Raw materials (steel, aluminum, copper, plastics), equipment, robotics
- **Equipment & Machinery** - Industrial equipment, manufacturing machinery, automation
- **Healthcare** - Pharmaceuticals, medical devices, medical supplies
- **Construction** - Building materials, equipment, contractors
- **Additional Categories** - Fully extensible for new industries

### Key Capabilities
- **27 Product Categories** - Comprehensive tariff coverage across all industries
- **150+ Trade Routes** - International sourcing with real tariff data (WTO/ITC verified)
- **35+ Procurement Rules** - Hard and soft constraint validation (R001-R035)
- **Global Logistics** - Lead times and costs for 85+ shipping routes
- **Trade Forecasting** - 3-year tariff and trade relationship projections

---

## Core Features

- **Three Data Corpuses**: Structured (CSV), Unstructured (policies), and Calculated/Derived data
- **35+ Procurement Rules**: Comprehensive rule book with violation detection
- **RAG (Retrieval Augmented Generation)**: Semantic search over procurement knowledge base
- **Real-Time Web Search**: Live market intelligence and supplier research
- **Confidence Scoring**: Self-aware confidence with data gap analysis
- **Full Traceability**: Complete audit trails and explainability
- **R001 Optimization Workflow**: Regional concentration violation resolution with leadership briefs

---

## Project Structure

```
Beroe Inc/
├── backend/
│   ├── agents/                     # Multi-agent orchestration
│   │   ├── base_agent.py           # Base agent class
│   │   ├── orchestrator.py         # Main agent coordinator
│   │   ├── supplier_coaching_orchestrator.py    # Coaching workflow
│   │   ├── enhanced_supplier_coaching_orchestrator.py # Advanced features
│   │   ├── data_analysis/          # Spend analysis agents
│   │   ├── intelligence/           # Tariff calculator, cost-risk
│   │   ├── incumbent_strategy/     # Incumbent supplier strategies
│   │   ├── recommendations/        # Personalized coaching
│   │   └── region_sourcing/        # Regional diversification
│   ├── engines/                    # Core processing engines
│   │   ├── data_loader.py          # Data loading & caching
│   │   ├── rule_evaluation_engine.py # 35+ rule evaluation (R001-R035)
│   │   ├── r001_optimization_workflow.py # Regional concentration fixes
│   │   ├── leadership_brief_generator.py # Executive briefs
│   │   ├── docx_exporter.py        # Word document generation
│   │   ├── llm_engine.py           # OpenAI GPT-4 integration
│   │   ├── rag_engine.py           # Semantic search over knowledge base
│   │   ├── tariff_calculator.py    # 27 products, 150+ routes (REAL DATA)
│   │   ├── web_scraper.py          # Live market intelligence
│   │   ├── semantic_search_engine.py # Query analysis
│   │   └── ... (8+ additional engines)
│   ├── conversational_ai.py        # Main chatbot orchestrator
│   ├── conversation_memory.py      # Conversation history
│   ├── api/                        # FastAPI REST endpoints
│   └── config/                     # Configuration & settings
│
├── data/
│   ├── structured/                 # 11 CSV data files
│   │   ├── spend_data.csv          # 156 transactions (2025)
│   │   ├── spend_data_multi_industry.csv # 156 transactions (2024)
│   │   ├── supplier_master.csv     # 96 suppliers, all industries
│   │   ├── client_master.csv       # 17 clients, 7 industries
│   │   ├── supplier_contracts.csv  # Contract terms
│   │   ├── rule_book.csv           # 35 procurement rules
│   │   ├── pricing_benchmarks.csv  # Market pricing
│   │   ├── industry_benchmarks.csv # Performance metrics
│   │   ├── market_pricing.csv      # Market intelligence
│   │   ├── procurement_rulebook.csv # Extended rules
│   │   └── proof_points.csv        # Customer case studies
│   ├── unstructured/               # 15 policy & intelligence documents
│   │   ├── policies/               # 7 industry-specific policies
│   │   ├── best_practices/         # 2 best practice guides
│   │   ├── company_policies/       # Company procurement policy
│   │   ├── contracts/              # 2 supplier contracts
│   │   ├── risk_assessments/       # Risk assessment reports
│   │   ├── historical_analysis/    # Performance trends
│   │   └── news/                   # Market news & intelligence
│   ├── calculated/                 # Derived data & calculations
│   └── vector_db/                  # ChromaDB vector store (RAG)
│
├── rules/
│   └── rule_book.json              # 35 business rules & constraints
├── config/
│   └── prompts/                    # LLM system prompts
├── outputs/                        # Generated coaching briefs & reports
│   ├── briefs/                     # Leadership briefs (DOCX)
│   └── reports/                    # Analysis reports
│
├── tests/                          # Test suite
├── demos/                          # Demo scripts
├── scripts/                        # Utility scripts
├── logs/                           # Application logs
│
├── app.py                          # Streamlit Web UI
├── main.py                         # CLI entry point
├── START_HERE.py                   # Quick start entry
├── START_GLOBAL_SYSTEM.py          # Full system startup
├── requirements.txt                # Python dependencies
├── README.md                       # This file
└── Beroe_Env/                      # Python virtual environment (ACTIVE)
```

---

## Tariff Calculator - Global Trade Coverage

**Status**: ✅ FULLY IMPLEMENTED & VERIFIED

### Product Coverage (27 Products)
**Edible Oils** (5): Rice Bran Oil, Palm Oil, Sunflower Oil, Olive Oil, Soybean Oil
**IT Hardware** (4): Laptops, Servers, Network Equipment, Cybersecurity Solutions
**Manufacturing Raw Materials** (4): Steel, Aluminum, Copper, Plastics
**Manufacturing Equipment** (4): Manufacturing Equipment, Industrial Machinery, Robotics, Factory Automation
**Pharmaceuticals & Medical** (3): Pharmaceuticals, Medical Devices, Medical Supplies
**Software & Cloud** (2): Software Licenses, Cloud Services

### Trade Coverage
- **150+ International Routes**: US, EU, APAC, Americas, Africa
- **Real Tariff Data**: WTO/ITC sourced tariff rates
- **Logistics Costs**: 85+ routes with shipping costs by category
- **Lead Times**: 14-45 days depending on route/product
- **Trade Forecasts**: 3-year projections for tariff changes & relationships

---

## Quick Start

### Prerequisites
- Python 3.10+
- OpenAI API Key (GPT-4 recommended)
- Windows PowerShell or equivalent terminal

### Installation

```bash
# 1. Navigate to project
cd "f:\Work Terminal\Beroe Inc"

# 2. Activate virtual environment
.\Beroe_Env\Scripts\Activate.ps1

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set OpenAI API Key
$env:OPENAI_API_KEY = "your-key-here"

# 5. Run the system
python START_HERE.py
```

### Alternative Startup Options
```bash
# Full web UI (Streamlit)
streamlit run app.py

# CLI entry point
python main.py

# Full system with all features
python START_GLOBAL_SYSTEM.py
```
```

### Running the System

#### Option 1: Streamlit Web UI
```bash
.\Beroe_Env\Scripts\Activate.ps1
streamlit run app.py
```
Access at: http://localhost:8501

#### Option 2: Command Line
```bash
.\Beroe_Env\Scripts\Activate.ps1
python main.py
```

#### Option 3: Conversational AI Demo
```bash
.\Beroe_Env\Scripts\Activate.ps1
python backend/demo_conversational_ai.py
```

#### Option 4: Multi-Agent Orchestration
```bash
.\Beroe_Env\Scripts\Activate.ps1
python backend/demo_multi_agent_system.py
```

---

## Key Components

### 1. Rule Evaluation Engine
Evaluates 35+ procurement rules:
- **R001**: Regional Concentration (max 40% per region)
- **R002**: Tail Spend Fragmentation
- **R003**: Single Supplier Dependency (max 60%)
- **R023**: Supplier Concentration Index (HHI)
- Plus 31 more rules for ESG, quality, delivery, contracts, etc.

### 2. R001 Optimization Workflow
Complete workflow for resolving regional concentration violations:
1. Detect R001 violation
2. Identify alternate regions (Branch A)
3. Identify incumbent suppliers (Branch B)
4. Iterative rule validation
5. Generate Leadership Briefs (Word documents)

### 3. Conversational AI
Real-time Q&A with intelligent routing:
- **Priority 1**: YOUR Data (CSV files)
- **Priority 2**: YOUR Policies (RAG)
- **Priority 3**: Web Search (market intelligence)
- **Priority 4**: LLM (GPT-4 reasoning)

### 4. Leadership Brief Generator
Generates two executive-level briefs:
- **Incumbent Concentration Brief**: Supplier dependency analysis
- **Regional Concentration Brief**: Geographic diversification analysis

---

## Data Corpuses

### Structured Data (CSV)
| File | Description |
|------|-------------|
| `spend_data.csv` | 155 transactions across 15 clients and multiple industries |
| `supplier_master.csv` | 96 suppliers with quality ratings, certifications |
| `rule_book.csv` | 35 procurement rules with thresholds |
| `pricing_benchmarks.csv` | Market pricing by region |
| `industry_benchmarks.csv` | Performance comparisons |
| `client_master.csv` | Client information and requirements |

### Unstructured Data
- Procurement policies for various industries
- Best practices documents
- Contract templates
- Risk assessments

### Rules (rule_book.json)
- Hard Constraints (HC001-HC008): Must be satisfied
- Soft Preferences (SP001-SP007): Scored/ranked
- Risk Assessment Rules (RA001-RA006)
- Data Completeness Rules
- Escalation Triggers

---

## Configuration

### Environment Variables (.env)
```
OPENAI_API_KEY=your_openai_api_key
```

### Prompts
System prompts are in `config/prompts/`

---

## Example Queries

```
"What's our total spend on Rice Bran Oil?"
"Show me regional concentration risks"
"Which suppliers have the highest quality ratings?"
"What are the R001 violations for client C001?"
"Generate a diversification recommendation"
"Find suppliers in India for vegetable oils"
"What's the tariff rate from Malaysia to USA?"
```

---

## Output Examples

### Leadership Brief (Word Document)
The system generates professional Word documents with:
- Current state analysis
- Risk statements
- Target allocation recommendations
- Cost advantage projections
- Strategic outcomes
- Next steps

---

## Technology Stack

- **Python 3.10+**
- **OpenAI API** (GPT-4 for reasoning, embeddings for RAG)
- **Pandas** for data manipulation
- **Streamlit** for web UI
- **Plotly** for visualizations
- **python-docx** for Word document generation
- **Chromadb** for vector storage

---

## License
MIT License

## Author
Beroe Inc - Procurement Intelligence Platform
