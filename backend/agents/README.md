# 🤖 Multi-Agent Procurement Intelligence System

## Overview

This is a **multi-agent architecture** where specialized agents handle specific tasks instead of one monolithic system with complex if/else logic. Each agent is focused, testable, and maintainable.

---

## 🏗️ Architecture

### Agent Categories

#### 1️⃣ **Data Analysis Agents** (`backend/agents/data_analysis/`)
- **SpendAnalyzerAgent**: Calculates spend metrics with breakdowns
- **RegionalConcentrationAgent**: Identifies regional concentration risks
- **PatternDetectorAgent**: Detects trends, volatility, anomalies
- **ThresholdTrackerAgent**: Tracks rule violations and warnings

#### 2️⃣ **Intelligence Agents** (`backend/agents/intelligence/`)
- **WebIntelligenceAgent**: Scrapes internet for real-time market data
- **RiskScoringAgent**: Calculates comprehensive risk scores
- **RuleEngineAgent**: Evaluates specific procurement rules
- **BestPracticeAgent**: Provides industry best practices

#### 3️⃣ **Recommendation Agents** (`backend/agents/recommendations/`)
- **SavingsCalculatorAgent**: Calculates exact savings potential
- **ActionPlanGeneratorAgent**: Creates step-by-step action plans

#### 4️⃣ **Orchestrator** (`backend/agents/orchestrator.py`)
- Routes requests to appropriate agents
- Combines results from multiple agents
- Executes complex workflows

---

## 🎯 Workflows

The orchestrator supports these workflows:

### 1. **Comprehensive Analysis**
```python
orchestrator.execute_workflow(
    workflow_type='comprehensive_analysis',
    input_data={
        'client_id': 'C001',
        'category': 'Rice Bran Oil'
    }
)
```

**Agents Used**:
1. SpendAnalyzer → Get spend metrics
2. RegionalConcentration → Check regional risks
3. PatternDetector → Identify trends
4. ThresholdTracker → Check rule compliance
5. WebIntelligence → Get market prices

**Output**: Complete analysis with spend, risks, patterns, and market data

---

### 2. **Rule Evaluation**
```python
orchestrator.execute_workflow(
    workflow_type='rule_evaluation',
    input_data={
        'rule_id': 'HC001',
        'client_id': 'C001',
        'category': 'Rice Bran Oil'
    }
)
```

**Agents Used**:
1. RuleEngine → Evaluate specific rule
2. SpendAnalyzer → Get context
3. RiskScoring → Score violating suppliers
4. ActionPlanGenerator → Create fix plan
5. BestPractice → Get recommendations

**Output**: Rule status, violations, impact, action plan

---

### 3. **Savings Opportunity**
```python
orchestrator.execute_workflow(
    workflow_type='savings_opportunity',
    input_data={
        'client_id': 'C001',
        'category': 'Rice Bran Oil',
        'scenario': 'price_negotiation',
        'target_price': 1180
    }
)
```

**Agents Used**:
1. SpendAnalyzer → Current spend
2. WebIntelligence → Market prices
3. SavingsCalculator → Calculate savings
4. ActionPlanGenerator → Implementation plan
5. BestPractice → Cost optimization tips

**Output**: Exact savings amount, percentage, timeline, action plan

---

### 4. **Risk Assessment**
```python
orchestrator.execute_workflow(
    workflow_type='risk_assessment',
    input_data={
        'supplier_id': 'S001'
    }
)
```

**Agents Used**:
1. RiskScoring → Calculate risk score
2. BestPractice → Mitigation strategies

**Output**: Risk score breakdown, factors, recommendations

---

### 5. **Supplier Comparison**
```python
orchestrator.execute_workflow(
    workflow_type='supplier_comparison',
    input_data={
        'supplier_id_1': 'S001',
        'supplier_id_2': 'S002'
    }
)
```

**Agents Used**:
1. RiskScoring → Compare risk scores

**Output**: Side-by-side comparison, risk delta, recommendation

---

## 🚀 Running the System

### 1. Run the Demo
```bash
python demos/demo_multi_agent_system.py
```

This will run 5 demos showcasing all workflows.

### 2. Use Individual Agents
```python
from backend.agents.data_analysis.spend_analyzer import SpendAnalyzerAgent

agent = SpendAnalyzerAgent()
result = agent.execute({
    'client_id': 'C001',
    'category': 'Rice Bran Oil'
})

print(result['data'])
```

### 3. Use the Orchestrator
```python
from backend.agents.orchestrator import AgentOrchestrator

orchestrator = AgentOrchestrator()

# Run a workflow
result = orchestrator.execute_workflow(
    workflow_type='comprehensive_analysis',
    input_data={'client_id': 'C001', 'category': 'Rice Bran Oil'}
)
```

---

## 📊 Example Outputs

### Comprehensive Analysis
```
📊 COMPREHENSIVE ANALYSIS SUMMARY
================================================================================

Client: C001
Category: Rice Bran Oil

💰 SPEND OVERVIEW:
   Total Spend: $2,045,000.00
   Transactions: 3
   Top Supplier: Malaya Agri Oils (65.3%)

🌍 REGIONAL CONCENTRATION:
   Risk Level: HIGH
   ⚠️ HIGH RISK: 100.0% of spend concentrated in APAC

📋 RULE COMPLIANCE:
   Violations: 0
   Warnings: 1
   Status: WARNING
```

### Savings Opportunity
```
💰 SAVINGS ANALYSIS:
   Current Spend: $2,045,000.00
   Potential Savings: $104,295.00
   Savings %: 5.1%
   Timeline: 1-3 months (moderate negotiation)
   Confidence: HIGH

📊 PRICE COMPARISON:
   Current Price: $1,240.00/ton
   Market Price: $1,180.00/ton
   Target Price: $1,180.00/ton
   Gap: $60.00/ton

📝 ACTION PLAN:
   1. Gather market intelligence and pricing data (Week 1)
   2. Analyze current spend and identify savings potential (Week 2)
   3. Prepare negotiation strategy and talking points (Week 3)
   4. Schedule and conduct supplier negotiation meeting (Week 4)
```

### Risk Assessment
```
⚠️  RISK ASSESSMENT:
   Supplier: Malaya Agri Oils
   Country: Malaysia
   Overall Risk Score: 15.8/100
   Risk Level: LOW
   ✅ Low risk supplier - suitable for strategic sourcing

📊 RISK BREAKDOWN:
   Quality Risk: 10.0
   Delivery Risk: 8.0
   Geopolitical Risk: 17.0
   Sustainability Risk: 18.0
   Lead Time Risk: 23.3

🔍 KEY RISK FACTORS (0):
   (No significant risk factors identified)
```

---

## 🎨 Benefits of Multi-Agent Architecture

### ✅ **Focused Agents**
- Each agent has ONE specific task
- Easy to understand and maintain
- No complex if/else chains

### ✅ **Composable**
- Combine agents in different workflows
- Reuse agents across scenarios
- Easy to add new agents

### ✅ **Testable**
- Test each agent independently
- Mock agent responses
- Clear input/output contracts

### ✅ **Scalable**
- Add new agents without touching existing code
- Parallel execution possible
- Easy to optimize individual agents

### ✅ **Specific, Not Generic**
- Agents provide exact numbers, not vague statements
- "Save $104,295 (5.1%)" not "potential savings"
- "Risk increased by 45%" not "HIGH RISK"

---

## 📝 Adding New Agents

1. Create new agent file in appropriate category
2. Inherit from `BaseAgent`
3. Implement `execute()` method
4. Add to orchestrator
5. Create workflow if needed

Example:
```python
from backend.agents.base_agent import BaseAgent

class MyNewAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="MyNewAgent",
            description="What this agent does"
        )
    
    def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        try:
            # Do the work
            result = self._do_something(input_data)
            
            return self._create_response(
                success=True,
                data=result,
                sources=['data_source.csv']
            )
        except Exception as e:
            return self._create_response(
                success=False,
                error=str(e)
            )
```

---

## 🔍 Agent Communication

Agents communicate through standardized response format:

```python
{
    "success": bool,
    "data": Any,  # Agent-specific output
    "error": Optional[str],
    "metadata": {
        "agent_name": str,
        "execution_time": str,
        "execution_count": int,
        "sources": List[str]
    }
}
```

---

## 📚 Documentation

- Each agent has docstrings explaining inputs and outputs
- Workflows are documented in orchestrator
- Demo script shows real examples

---

## 🎯 Next Steps

1. ✅ Core agents implemented
2. ✅ Orchestrator working
3. ✅ Demo script created
4. 🔄 Add more agents (incumbent strategy, region sourcing)
5. 🔄 Integrate with conversational AI
6. 🔄 Add API endpoints
7. 🔄 Create UI

---

**Built with ❤️ by Beroe Inc**
