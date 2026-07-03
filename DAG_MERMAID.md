# LangGraph DAG Visualization

## Quick View
Visit https://mermaid.live and paste the diagram below (WITHOUT the backticks)

---

## Diagram (Copy ONLY the content between the lines below)

```
---
config:
  flowchart:
    curve: linear
---
graph TD;
	__start__([Start]):::first
	validate_input(validate_input)
	profile_analysis(profile_analysis)
	financial_risk(financial_risk)
	synthesis(synthesis)
	compliance(compliance)
	__end__([End]):::last
	__start__ --> validate_input;
	validate_input --> profile_analysis;
	profile_analysis --> financial_risk;
	financial_risk --> synthesis;
	synthesis --> compliance;
	compliance --> __end__;
	classDef default fill:#f2f0ff,line-height:1.2
	classDef first fill:#e1d5ff
	classDef last fill:#bfb6fc
```

---

## Steps to View

### Option 1: Mermaid Live (Online)
1. Go to https://mermaid.live
2. Copy ONLY the diagram content above (lines 16-32)
3. Paste into editor
4. Click "Draw"

### Option 2: VS Code (Offline)
1. Install "Markdown Preview Mermaid Support" extension
2. Open this file
3. Right-click → "Open Preview" or Ctrl+Shift+V
4. Diagram renders automatically

### Option 3: Command Line
Run: `python3 scripts/visualize_dag.py`

---

## Flow Explanation

```
START
  ↓
1. validate_input
   - Validates application data format
   ↓
2. profile_analysis
   - Analyzes applicant demographics
   - Inserts data into applicants/employment_history/credit_history tables
   ↓
3. financial_risk
   - Calculates financial metrics (DTI, LTI, Risk Score)
   - Calls MCP RiskRules service
   ↓
4. synthesis
   - Synthesizes decision from profile + financial risk
   - Applies decision rules engine
   - Calls MCP DecisionSynthesis service
   ↓
5. compliance
   - Checks regulatory compliance
   - Creates audit logs
   - Calls MCP NotificationSystem service
   ↓
END (Result saved to loan_applications table)
```
