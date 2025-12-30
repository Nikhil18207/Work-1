# Universal Procurement AI - Multi-Industry Recommendation System

## Overview

Enterprise-grade **LLM-powered procurement recommendation system** that works for **ANY industry and ANY category**. Built with strict data governance, rule-based constraints, RAG capabilities, and full traceability.

### Supported Industries
- **Food & Beverage** - Vegetable oils, ingredients, packaged goods
- **IT & Technology** - Hardware, software, cloud services
- **Manufacturing** - Raw materials, equipment, components
- **Services** - Marketing, consulting, professional services
- **Healthcare** - Pharmaceuticals, medical devices, supplies
- **Construction** - Materials, equipment, contractors
- **Energy & Utilities** - Equipment, services, commodities
- **And ANY other procurement category!**

The system is **100% category-agnostic** - simply provide your data and policies, and it adapts automatically!

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
│   ├── agents/                     # Agent-based architecture
│   │   ├── data_analysis/          # Spend, threshold, regional analysis
│   │   ├── intelligence/           # Tariff, cost-risk, leading questions
│   │   ├── incumbent_strategy/     # Incumbent supplier strategies
│   │   ├── recommendations/        # Personalized coaching
│   │   └── region_sourcing/        # Regional diversification
│   ├── engines/                    # Core processing engines
│   │   ├── data_loader.py          # Data loading & caching
│   │   ├── rule_evaluation_engine.py # 35+ rule evaluation
│   │   ├── r001_optimization_workflow.py # R001 violation resolution
│   │   ├── leadership_brief_generator.py # Executive briefs
│   │   ├── docx_exporter.py        # Word document generation
│   │   ├── llm_engine.py           # OpenAI GPT-4 integration
│   │   ├── rag_engine.py           # RAG for context-aware answers
│   │   ├── tariff_calculator.py    # Cross-border tariff calculations
│   │   └── ...
│   ├── conversational_ai.py        # Main chatbot engine
│   └── conversation_memory.py      # Conversation tracking
├── data/
│   ├── structured/                 # CSV data files
│   │   ├── spend_data.csv          # 155 transactions, 15 clients
│   │   ├── supplier_master.csv     # 96 suppliers with ratings
│   │   ├── rule_book.csv           # 35 procurement rules
│   │   ├── pricing_benchmarks.csv  # Market pricing data
│   │   └── ...
│   ├── unstructured/               # Policy documents
│   │   └── policies/               # Industry-specific policies
│   └── vector_db/                  # Vector database for RAG
├── rules/
│   └── rule_book.json              # Business rules & constraints
├── outputs/                        # Generated briefs & reports
├── app.py                          # Streamlit Web UI
├── main.py                         # CLI entry point
├── requirements.txt                # Python dependencies
└── Beroe_Env/                      # Python virtual environment
```

---

## Quick Start

### Prerequisites
- Python 3.10+
- OpenAI API Key

### Installation

```bash
# Navigate to project directory
cd "f:\Work Terminal\Beroe Inc"

# Activate virtual environment
.\Beroe_Env\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
# Copy .env.example to .env and add your OPENAI_API_KEY
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

#### Option 4: R001 Optimization Workflow
```bash
.\Beroe_Env\Scripts\Activate.ps1
python backend/engines/r001_optimization_workflow.py
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
