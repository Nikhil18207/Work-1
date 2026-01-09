# Beroe Procurement AI - Multi-Industry Sourcing Intelligence

## Overview

Enterprise-grade **AI-powered procurement recommendation system** for multi-industry sourcing intelligence. Features a minimalistic Streamlit UI, automated leadership brief generation, and comprehensive rule-based analysis.

### Data Coverage
- **10 Industry Sectors** - Food & Beverages, IT, Manufacturing, Healthcare, Energy, Construction, Logistics, Professional Services, Facilities, HR
- **41 Categories** - Across all sectors
- **140 SubCategories** - Granular product/service classification
- **893 Suppliers** - Global supplier database across 5 regions
- **2,289 Transactions** - $1.53B total spend data
- **5 Geographic Regions** - Americas, Europe, APAC, Middle East, Africa
- **34 Procurement Rules** - Comprehensive rule validation with conflict-aware orchestration (R001-R035, excluding R033)

---

## Quick Start

### Prerequisites
- Python 3.10+
- OpenAI API Key (optional, for LLM features)

### Installation

```bash
# 1. Navigate to project
cd "f:\Work Terminal\Beroe Inc"

# 2. Activate virtual environment
.\Beroe_Env\Scripts\Activate.ps1

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set OpenAI API Key (optional)
$env:OPENAI_API_KEY = "your-key-here"

# 5. Run the Streamlit UI
streamlit run app.py
```

Access at: **http://localhost:8501**

---

## Features

### Streamlit Web UI (app.py)
Simple 2-tab interface:

**Tab 1: Use System Data**
- Cascading dropdowns: Sector → Category → SubCategory
- Preview spend metrics, suppliers, countries
- Generate Leadership Briefs (DOCX)

**Tab 2: Upload Your Data**
- Upload custom spend_data.csv
- Validate required columns
- Generate briefs from your data

### Leadership Brief Generator
Generates two executive-level DOCX documents:

**1. Incumbent Concentration Brief**
- Supplier concentration analysis
- Dominant supplier identification
- Share reduction recommendations
- Cost advantage projections
- Risk matrix (Supply Chain, Geographic, Diversity)
- ROI projections
- Implementation timeline

**2. Regional Concentration Brief**
- Geographic spend distribution
- Regional dependency analysis
- Diversification targets
- Cost advantage drivers

### ⚡ NEW: Conflict-Aware Rule Orchestration
Intelligent rule conflict detection and resolution:

**Features:**
- **Automatic Conflict Detection** - Identifies when fixing one rule might break another
- **4-Tier Priority System** - Critical (1-5) → High Risk (6-15) → Medium (16-25) → Strategic (26-34)
- **Smart Action Plans** - Step-by-step resolution strategies that consider dependencies
- **29 Conflict Mappings** - Comprehensive coverage of rule interactions

**Example Conflicts Resolved:**
- R001 ↔ R003: Diversification Paradox (add suppliers in different regions simultaneously)
- R009 ↔ R014: Payment vs Currency (hedge currency before extending payment terms)
- R015 ↔ R005: Diversity vs ESG (find diverse suppliers with high ESG scores)

**See:** `SYSTEM_UPDATE_CONFLICT_RESOLUTION.md` for full documentation

---

## Project Structure

```
Beroe Inc/
├── app.py                          # Streamlit Web UI (main entry)
├── main.py                         # CLI entry point
├── requirements.txt
├── Beroe_Env/                      # Python virtual environment
│
├── backend/
│   ├── engines/                    # Core processing engines
│   │   ├── leadership_brief_generator.py  # Brief generation
│   │   ├── docx_exporter.py              # DOCX export
│   │   ├── data_loader.py                # Data loading & caching
│   │   ├── rule_evaluation_engine.py     # 34 rule validation
│   │   ├── rule_orchestrator.py          # NEW: Conflict-aware rule resolution
│   │   ├── r001_optimization_workflow.py # Regional optimization
│   │   ├── conversational_ai.py          # Chatbot orchestrator
│   │   ├── llm_engine.py                 # OpenAI GPT-4 integration
│   │   ├── rag_engine.py                 # Semantic search
│   │   └── ...
│   ├── agents/                     # Multi-agent orchestration
│   ├── api/                        # FastAPI REST endpoints
│   └── config/                     # Configuration & settings
│
├── data/
│   ├── structured/                 # CSV data files
│   │   ├── spend_data.csv          # 2,289 transactions, 893 suppliers
│   │   ├── supplier_master.csv     # Supplier database
│   │   ├── supplier_contracts.csv  # Contract terms
│   │   ├── rule_book.csv           # 34 procurement rules (R001-R035, excluding R033)
│   │   ├── rule_dependency_matrix.csv  # NEW: 29 rule conflict mappings
│   │   ├── industry_taxonomy.csv   # Sector/Category hierarchy
│   │   ├── industry_benchmarks.csv # Performance metrics
│   │   └── ...
│   ├── unstructured/               # Policy documents
│   │   ├── policies/               # Industry-specific policies
│   │   ├── best_practices/         # Best practice guides
│   │   ├── market_intelligence/    # Market analysis
│   │   └── risk_assessments/       # Risk reports
│   └── calculated/                 # Derived data

├── rules/
│   └── rule_book.json              # 34 business rules (legacy)
├── outputs/
│   └── briefs/                     # Generated DOCX briefs
├── scripts/                        # Utility scripts
└── tests/                          # Test suite
```

---

## Data Schema

### spend_data.csv (Required Columns)
```
Client_ID, Sector, Category, SubCategory, Supplier_ID, Supplier_Name,
Supplier_Country, Supplier_Region, Transaction_Date, Spend_USD,
Quality_Rating (optional), Delivery_Rating (optional)
```

### Industry Hierarchy
```
Sector (10)
└── Category (41)
    └── SubCategory (140)
```

**Example:**
- Food & Beverages → Edible Oils → Rice Bran Oil
- Information Technology → Hardware → Laptops
- Healthcare & Life Sciences → Pharmaceuticals → Branded Drugs

---

## Procurement Rules (35 Total)

| Rule | Name | Threshold | Risk Level |
|------|------|-----------|------------|
| R001 | Regional Concentration | >40% in single region | Critical |
| R003 | Single Supplier Dependency | >60% with single supplier | Critical |
| R005 | ESG Compliance Score | <60 | High |
| R007 | Quality Rejection Rate | >5% | High |
| R008 | Delivery Performance | <85% on-time | High |
| R010 | Supplier Financial Risk | Debt/Equity >2.5 | Critical |
| R023 | Supplier Concentration Index | HHI >2500 | High |
| R024 | Geopolitical Risk Exposure | >40% high-risk regions | Critical |
| ... | ... | ... | ... |

---

## API Usage

### Generate Briefs Programmatically
```python
from backend.engines.leadership_brief_generator import LeadershipBriefGenerator
from backend.engines.docx_exporter import DOCXExporter

# Initialize
generator = LeadershipBriefGenerator()
exporter = DOCXExporter()

# Generate briefs for a subcategory
briefs = generator.generate_both_briefs("C001", "Rice Bran Oil")

# Export to DOCX
results = exporter.export_both_briefs(briefs)
print(f"Incumbent Brief: {results['incumbent_docx']}")
print(f"Regional Brief: {results['regional_docx']}")
```

### Use Custom Data
```python
from backend.engines.data_loader import DataLoader
import pandas as pd

# Load your data
custom_df = pd.read_csv("your_spend_data.csv")

# Create loader with custom data
loader = DataLoader()
loader.set_spend_data(custom_df)

# Generate with custom data
generator = LeadershipBriefGenerator(data_loader=loader)
briefs = generator.generate_both_briefs("YOUR_CLIENT", "Your SubCategory")
```

---

## Technology Stack

- **Python 3.10+**
- **Streamlit** - Web UI
- **Pandas** - Data manipulation
- **python-docx** - DOCX generation
- **Plotly** - Visualizations
- **OpenAI API** - GPT-4 (optional, for LLM features)
- **ChromaDB** - Vector storage (RAG)

---

## Scripts

| Script | Purpose |
|--------|---------|
| `scripts/generate_briefs.py` | Batch generate briefs |
| `scripts/update_structured_data.py` | Update CSV data |
| `scripts/generate_unstructured_data.py` | Generate policy docs |
| `scripts/verify_all_briefs.py` | Verify brief generation |

---

## License
MIT License

## Author
Beroe Inc - Procurement Intelligence Platform
