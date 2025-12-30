"""
Visual Workflow Diagram Generator
Generates visual representations of coaching workflow and decisions
Creates Mermaid diagrams, flowcharts, and ASCII representations
"""

import sys
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime

root_path = Path(__file__).parent.parent.parent.parent
if str(root_path) not in sys.path:
    sys.path.insert(0, str(root_path))

from backend.agents.base_agent import BaseAgent


class VisualWorkflowDiagramGenerator(BaseAgent):
    """
    Generates visual representations of the coaching system workflow
    Creates multiple formats: ASCII, Mermaid, HTML
    """
    
    def __init__(self):
        super().__init__(
            name="VisualWorkflowDiagram",
            description="Generates visual workflow diagrams and decision flowcharts"
        )
    
    def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate visual workflows
        
        Input:
            - diagram_type: str - 'full_system', 'analysis_flow', 'decision_tree', 'coaching_loop'
            - format: str - 'ascii', 'mermaid', 'html', 'all'
            - include_decisions: bool - include decision points
            - coaching_session: Dict - optional session data for actual workflow
        """
        try:
            diagram_type = input_data.get('diagram_type', 'full_system')
            format_type = input_data.get('format', 'mermaid')
            include_decisions = input_data.get('include_decisions', True)
            coaching_session = input_data.get('coaching_session')
            
            diagram_id = f"DIAGRAM_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            self._log(f"[{diagram_id}] Generating {diagram_type} diagram in {format_type} format")
            
            # Generate diagrams based on type
            diagrams = {}
            
            if diagram_type in ['full_system', 'all']:
                diagrams['full_system'] = self._generate_full_system_diagram(format_type, include_decisions)
            
            if diagram_type in ['analysis_flow', 'all']:
                diagrams['analysis_flow'] = self._generate_analysis_flow_diagram(format_type, include_decisions)
            
            if diagram_type in ['decision_tree', 'all']:
                diagrams['decision_tree'] = self._generate_decision_tree_diagram(format_type, include_decisions)
            
            if diagram_type in ['coaching_loop', 'all']:
                diagrams['coaching_loop'] = self._generate_coaching_loop_diagram(format_type, include_decisions)
            
            if coaching_session:
                diagrams['session_flow'] = self._generate_session_flow_diagram(coaching_session, format_type)
            
            result = {
                'diagram_id': diagram_id,
                'timestamp': datetime.now().isoformat(),
                'diagram_type': diagram_type,
                'format': format_type,
                'diagrams': diagrams,
                'export_urls': self._generate_export_urls(diagram_id, diagrams),
                'documentation': self._generate_documentation(diagram_type)
            }
            
            self._log(f"[{diagram_id}] Diagram generation complete")
            
            return self._create_response(
                success=True,
                data=result
            )
            
        except Exception as e:
            self._log(f"Error generating diagram: {str(e)}", "ERROR")
            return self._create_response(
                success=False,
                error=str(e)
            )
    
    def _generate_full_system_diagram(self, format_type: str, include_decisions: bool) -> Dict:
        """Generate full system architecture diagram"""
        
        mermaid_diagram = """graph TD
    A["🎯 CLIENT REQUEST"] --> B["📋 Leading Questions Module"]
    B --> C["🔍 Data Analysis & Quantification"]
    
    C --> D["Regional Concentration Check<br/>R001 Violation?"]
    D -->|Yes| E["✅ Collect Additional Info"]
    D -->|No| F["Proceed to Next Analysis"]
    
    E --> G["📊 Branch 1: Data Analysis<br/>- Spend Analyzer<br/>- Regional Concentration<br/>- Pattern Detector<br/>- Threshold Tracker"]
    
    F --> H["🏭 Branch 3: Incumbent Strategy<br/>- Supplier Screening<br/>- Capability Assessment<br/>- 30% Rule Validation<br/>- Constraint Checker"]
    
    H --> I["🌍 Branch 4: Region Sourcing<br/>- New Region ID<br/>- Supplier Evaluation<br/>- Cost Calculator<br/>- Tariff Analysis"]
    
    I --> J["💡 Branch 2: Recommendations<br/>- Personalized Coaching<br/>- Action Plans<br/>- Best Practices"]
    
    J --> K["🎯 Branch 5: System Architecture<br/>- Parameter Tuning<br/>- Web Scraping<br/>- Real-time Data<br/>- AI Optimization"]
    
    K --> L["✅ RESULTS<br/>- Executive Summary<br/>- Recommendations<br/>- Risk Assessment<br/>- Cost Impact"]
    
    style A fill:#e1f5ff
    style L fill:#c8e6c9
    style D fill:#fff9c4
    style E fill:#ffe0b2
    style G fill:#f3e5f5
    style H fill:#e0f2f1
    style I fill:#fce4ec
    style J fill:#e8f5e9
    style K fill:#f1f8e9"""
        
        ascii_diagram = self._generate_full_system_ascii()
        
        if format_type == 'mermaid' or format_type == 'all':
            return {'mermaid': mermaid_diagram, 'ascii': ascii_diagram}
        elif format_type == 'ascii':
            return {'ascii': ascii_diagram}
        else:
            return {'mermaid': mermaid_diagram}
    
    def _generate_full_system_ascii(self) -> str:
        """Generate ASCII representation of full system"""
        return """
╔════════════════════════════════════════════════════════════════════════════════╗
║                   PERSONALIZED SUPPLIER COACHING SYSTEM                        ║
╚════════════════════════════════════════════════════════════════════════════════╝

                                 🎯 CLIENT
                                    ↓
                        ┌───────────────────────┐
                        │ Leading Questions     │
                        │ - Source Country?     │
                        │ - Target Country?     │
                        │ - Volume?             │
                        │ - Quality Needs?      │
                        └───────────────────────┘
                                    ↓
                    ┌───────────────────────────────┐
                    │  DATA COLLECTION & ANALYSIS   │
                    └───────────────────────────────┘
                                    ↓
            ┌─────────────────────────┬──────────────────────────┐
            ↓                         ↓                          ↓
      ┌──────────────┐        ┌──────────────┐        ┌──────────────┐
      │ SPEND DATA   │        │ SUPPLIER DB  │        │ TARIFF DB    │
      └──────────────┘        └──────────────┘        └──────────────┘
            ↓                         ↓                          ↓
            └─────────────────────────┬──────────────────────────┘
                                    ↓
        ╔═══════════════════════════════════════════════════╗
        ║    5 MAIN BRANCHES OF ANALYSIS                    ║
        ╚═══════════════════════════════════════════════════╝
            ↓
    ┌───────┴───────┬───────────┬──────────┬─────────────┐
    ↓               ↓           ↓          ↓             ↓
┌────────────┐  ┌────────┐  ┌────────┐  ┌────────┐  ┌───────────┐
│ DATA       │  │INCUMBT │  │REGION  │  │RECOM   │  │ARCHITECTURE│
│ANALYSIS   │  │STRATEGY│  │SOURCING│  │MENDTNS │  │SYSTEM      │
└────────────┘  └────────┘  └────────┘  └────────┘  └───────────┘
    ↓               ↓           ↓          ↓             ↓
  METRICS      SCREENING    IDENTIFY   COACHING     TUNING+
  PATTERNS     VALIDATION   REGIONS    ACTIONS      SCRAPING
    ↓               ↓           ↓          ↓             ↓
    └───────────────┴───────────┴──────────┴─────────────┘
                            ↓
        ╔════════════════════════════════════════════╗
        ║        COST & RISK LOOP OPTIMIZATION       ║
        ║  (Up to 50 iterations until constraints)   ║
        ╚════════════════════════════════════════════╝
                            ↓
                ┌─────────────────────────┐
                │ CONSTRAINT VALIDATION   │
                │ - Max 30% per supplier  │
                │ - Max 40% per region    │
                │ - Quality requirements  │
                │ - Lead times            │
                │ - All 35+ business rules│
                └─────────────────────────┘
                            ↓
            ╔════════════════════════════╗
            ║  ✅ FEASIBLE SOLUTIONS     ║
            ║  - Optimal                 ║
            ║  - Alternative 1           ║
            ║  - Alternative 2           ║
            ║  - Alternative 3           ║
            ╚════════════════════════════╝
                            ↓
                ┌─────────────────────────┐
                │  EXECUTIVE SUMMARY      │
                │  ACTION PLAN            │
                │  RISK ASSESSMENT        │
                │  RECOMMENDATIONS        │
                └─────────────────────────┘
                            ↓
                        🎯 RESULTS
"""
    
    def _generate_analysis_flow_diagram(self, format_type: str, include_decisions: bool) -> Dict:
        """Generate data analysis flow diagram"""
        
        mermaid_diagram = """graph LR
    A["Raw Spend Data"] --> B["Clean & Filter"]
    B --> C["Spend Analysis<br/>by Supplier"]
    C --> D["Regional<br/>Concentration"]
    D --> E{R001<br/>Violation?}
    E -->|Yes| F["Calculate<br/>Impact"]
    E -->|No| G["Low Risk"]
    F --> H["Identify<br/>Patterns"]
    H --> I["Threshold<br/>Tracking"]
    I --> J["Risk<br/>Metrics"]
    J --> K["Data Ready<br/>for Next Branch"]
    G --> K
    
    style A fill:#e3f2fd
    style E fill:#fff9c4
    style K fill:#c8e6c9"""
        
        ascii_diagram = """
        DATA PIPELINE
        ──────────────
        
        Raw Data → Clean → Analysis → Patterns → Thresholds
           ↓        ↓         ↓         ↓           ↓
         Spend    Filter  Metrics   Identify    Track
         Data             Regional   Specific    Breaches
                      Concentration  Issues
"""
        
        if format_type == 'mermaid' or format_type == 'all':
            return {'mermaid': mermaid_diagram, 'ascii': ascii_diagram}
        else:
            return {'ascii': ascii_diagram}
    
    def _generate_decision_tree_diagram(self, format_type: str, include_decisions: bool) -> Dict:
        """Generate decision tree"""
        
        mermaid_diagram = """graph TD
    A["Regional<br/>Concentration?"] -->|> 40%| B["RISK<br/>DETECTED"]
    A -->|≤ 40%| C["Monitor"]
    B --> D["Which Region<br/>Over-concentrated?"]
    D --> E["Supplier<br/>Concentration?"]
    E -->|> 30%| F["CONSTRAINT<br/>VIOLATION"]
    E -->|≤ 30%| G["Acceptable"]
    F --> H["Options?"]
    H -->|Expand Incumbent| I["Expansion<br/>Potential?"]
    H -->|New Regions| J["Region<br/>Alternatives?"]
    I -->|Yes| K["Recommend<br/>Expansion"]
    I -->|No| L["Find New<br/>Suppliers"]
    J --> M["Tariff<br/>Impact?"]
    M -->|High| N["Assess Trade-off"]
    M -->|Low| O["Recommend<br/>New Region"]
    
    style B fill:#ffcdd2
    style F fill:#ffcdd2
    style K fill:#c8e6c9
    style O fill:#c8e6c9"""
        
        ascii_diagram = """
        DECISION TREE
        ─────────────
        
        Is regional concentration > 40%?
            ├─ YES → Is supplier concentration > 30%?
            │         ├─ YES → VIOLATION! Can we expand incumbent?
            │         │         ├─ YES → Recommend expansion
            │         │         └─ NO → Find new suppliers
            │         └─ NO → Acceptable
            └─ NO → Continue monitoring
"""
        
        if format_type == 'mermaid' or format_type == 'all':
            return {'mermaid': mermaid_diagram, 'ascii': ascii_diagram}
        else:
            return {'ascii': ascii_diagram}
    
    def _generate_coaching_loop_diagram(self, format_type: str, include_decisions: bool) -> Dict:
        """Generate coaching feedback loop"""
        
        mermaid_diagram = """graph TD
    A["Initial<br/>Recommendation"] --> B["Calculate<br/>Cost & Risk"]
    B --> C["Check<br/>Constraints"]
    C --> D{All<br/>Constraints<br/>Met?}
    D -->|NO| E["Identify<br/>Violations"]
    E --> F["Suggest<br/>Adjustments"]
    F --> G["Apply<br/>Changes"]
    G --> H["Iteration<br/>Counter"]
    H --> I{Converged<br/>or Max<br/>Iterations?}
    I -->|NO| B
    I -->|YES| J["Generate<br/>3-5 Options"]
    D -->|YES| J
    J --> K["Present to<br/>User"]
    K --> L{User<br/>Accepts?}
    L -->|Modify| M["Adjust<br/>Parameters"]
    L -->|YES| N["Finalize<br/>Recommendation"]
    M --> B
    L -->|Needs Info| O["Ask More<br/>Questions"]
    O --> B
    
    style D fill:#fff9c4
    style I fill:#fff9c4
    style L fill:#fff9c4
    style N fill:#c8e6c9"""
        
        ascii_diagram = """
        COACHING LOOP (Up to 50 iterations)
        ────────────────────────────────
        
        ┌─────────────────────────────────────────┐
        │                                         │
        │  1. Calculate Cost & Risk               │
        │  2. Validate Constraints                │
        │  3. Identify Violations (if any)        │
        │  4. Suggest Adjustments                 │
        │  5. Generate New Allocation             │
        │                                         │
        │  Loop until:                            │
        │  • All constraints satisfied OR         │
        │  • Max 50 iterations reached            │
        │                                         │
        └─────────────────────────────────────────┘
                         ↓
        Present to User: 3-5 Feasible Options
                         ↓
                  User Provides Feedback
                         ↓
              Refine & Generate Next Iteration
"""
        
        if format_type == 'mermaid' or format_type == 'all':
            return {'mermaid': mermaid_diagram, 'ascii': ascii_diagram}
        else:
            return {'ascii': ascii_diagram}
    
    def _generate_session_flow_diagram(self, coaching_session: Dict, format_type: str) -> Dict:
        """Generate diagram for actual coaching session"""
        
        branches = coaching_session.get('branches', {})
        
        # Build dynamic diagram from session data
        mermaid_lines = ["graph TD", f"    A[\"Session: {coaching_session.get('session_id')}\"]"]
        node_id = 65  # ASCII 'A'
        
        # Add each branch executed
        branch_order = ['data_analysis', 'incumbent_strategy', 'region_sourcing', 'personalized_recommendations']
        
        for i, branch in enumerate(branch_order):
            if branch in branches:
                node_id += 1
                prev_char = chr(node_id - 1)
                curr_char = chr(node_id)
                
                branch_label = branch.replace('_', ' ').title()
                mermaid_lines.append(f"    {prev_char} --> {curr_char}[\"{branch_label}\"]")
        
        mermaid_lines.append(f"    {chr(node_id)} --> Z[\"Results Generated\"]")
        
        mermaid_diagram = "\n".join(mermaid_lines)
        
        ascii_diagram = f"""
        SESSION FLOW: {coaching_session.get('session_id')}
        ──────────────────────────────────────
        
        START
          ↓
        Analysis: {branches.get('data_analysis', {}).get('status', 'N/A')}
          ↓
        Incumbent Strategy: {branches.get('incumbent_strategy', {}).get('status', 'N/A')}
          ↓
        Region Sourcing: {branches.get('region_sourcing', {}).get('status', 'N/A')}
          ↓
        Recommendations: {branches.get('personalized_recommendations', {}).get('status', 'N/A')}
          ↓
        ✅ COMPLETE
"""
        
        if format_type == 'mermaid' or format_type == 'all':
            return {'mermaid': mermaid_diagram, 'ascii': ascii_diagram}
        else:
            return {'ascii': ascii_diagram}
    
    def _generate_export_urls(self, diagram_id: str, diagrams: Dict) -> Dict:
        """Generate export URLs for diagrams"""
        
        return {
            'mermaid_live': f"https://mermaid.live/",
            'export_pdf': f"/api/diagrams/{diagram_id}/export/pdf",
            'export_png': f"/api/diagrams/{diagram_id}/export/png",
            'export_svg': f"/api/diagrams/{diagram_id}/export/svg",
            'export_ascii': f"/api/diagrams/{diagram_id}/export/ascii",
        }
    
    def _generate_documentation(self, diagram_type: str) -> str:
        """Generate documentation for diagram"""
        
        docs = {
            'full_system': """
FULL SYSTEM DIAGRAM
This diagram shows the complete flow of the Personalized Supplier Coaching System:
1. User submits coaching request with initial parameters
2. System asks Leading Questions to gather critical information
3. Five main branches execute in parallel/sequence
4. Results are synthesized into personalized recommendations
            """,
            'analysis_flow': """
DATA ANALYSIS FLOW
Shows how raw data is processed and analyzed:
1. Raw spend data is cleaned and filtered
2. Analyzed by supplier and region
3. Concentration metrics calculated
4. Patterns and thresholds identified
            """,
            'decision_tree': """
DECISION TREE
Shows key decision points in the coaching logic:
1. Check regional concentration
2. Check supplier concentration
3. Make recommendations based on results
4. Offer expansion or new region options
            """,
            'coaching_loop': """
COACHING LOOP & OPTIMIZATION
Shows the iterative optimization process:
1. Generate initial allocation
2. Calculate cost and risk
3. Check constraints (max 30% per supplier, etc.)
4. Loop until feasible solution found or max iterations
5. Present 3-5 options to user
            """
        }
        
        return docs.get(diagram_type, "Diagram documentation")
