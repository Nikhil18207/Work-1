# 🧠 Universal Procurement AI - Multi-Industry Recommendation System

## Overview
Enterprise-grade **LLM-powered procurement recommendation system** that works for **ANY industry and ANY category**. Built with strict data governance, rule-based constraints, RAG capabilities, and full traceability.

### 🌐 Supported Industries
- ✅ **Food & Beverage** - Vegetable oils, ingredients, packaged goods
- ✅ **IT & Technology** - Hardware, software, cloud services
- ✅ **Manufacturing** - Raw materials, equipment, components
- ✅ **Services** - Marketing, consulting, professional services
- ✅ **Healthcare** - Pharmaceuticals, medical devices, supplies
- ✅ **Construction** - Materials, equipment, contractors
- ✅ **Energy & Utilities** - Equipment, services, commodities
- ✅ **And ANY other procurement category!**

The system is **100% category-agnostic** - simply provide your data and policies, and it adapts automatically!

## 🎯 Core Features
- **Three Data Corpuses**: Structured, Unstructured, and Calculated/Derived data
- **Rule-Based Governance**: 35+ comprehensive procurement rules
- **RAG (Retrieval Augmented Generation)**: Semantic search over procurement knowledge base
- **Real-Time Web Search**: Live market intelligence and supplier research
- **Confidence Scoring**: Self-aware confidence with data gap analysis
- **Full Traceability**: Complete audit trails and explainability
- **Experimental Benchmarking**: Test different inputs/outputs

## 📁 Project Structure

```
llm-recommendation-system/
├── data/
│   ├── structured/          # Structured data corpus (CSV files)
│   ├── unstructured/        # Unstructured data corpus (documents)
│   └── calculated/          # Derived/calculated data (generated)
├── rules/                   # Business rules and constraints
├── backend/                 # Backend application code
├── config/                  # Configuration and prompts
└── docs/                    # Documentation
```

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- OpenAI API Key
- Node.js 18+ (optional, for frontend)

### Installation
```bash
# Clone the repository
git clone <repo-url>
cd llm-recommendation-system

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Add your OPENAI_API_KEY to .env
```

### Running the System
```bash
# Setup RAG pipeline (first time only)
python scripts/setup_rag.py

# Start the backend
cd backend
python main.py

# The API will be available at http://localhost:8000
# API docs at http://localhost:8000/docs
```

## 📊 Data Corpuses

### 1. Structured Data
- **client_master.csv**: Client information and requirements
- **spend_data.csv**: Historical procurement spend data
- **pricing_benchmarks.csv**: Market pricing benchmarks
- **supplier_master.csv**: Supplier information and capabilities

### 2. Unstructured Data
- **Contracts**: Supplier agreements and terms
- **Policies**: Company procurement policies
- **Best Practices**: Industry standards and guidelines

### 3. Calculated/Derived Data
- Savings calculations
- Risk scores
- Compliance flags
- KPIs and variance analysis

## 🎯 Use Cases

### Example: Vegetable Oil Procurement
```
Input: "Recommend supplier for 50,000 liters of sunflower oil"

Output:
- Recommendation: Supplier X
- Confidence: 78%
- Savings: 12% vs current spend
- Missing Data: Quality certifications (+15% confidence if provided)
- Reasoning: Based on pricing benchmarks, spend history, and compliance rules
```

## 🔧 Configuration

### Rule Book
Business rules are defined in `rules/rule_book.json`:
- Hard constraints (must satisfy)
- Soft preferences (nice to have)
- Compliance requirements
- Risk thresholds

### Prompts
Prompt templates are in `config/prompts/`:
- System prompts
- Few-shot examples
- Output schemas

## 📈 Confidence Scoring

The system provides dynamic confidence scores:
- Current confidence based on available data
- Missing data impact analysis
- Potential confidence increase with additional data
- Business impact explanation

## 🔍 Traceability

Every recommendation includes:
- Structured data IDs used
- Document chunk references
- Rules applied
- Prompt hash
- Model version
- Confidence breakdown

## 🧪 Experimentation

Test different scenarios:
```bash
python experiments/run_benchmark.py --scenario vegetable_oil
```

## 📝 License
MIT License

## 👥 Contributors
Beroe Inc - Procurement Intelligence Platform
