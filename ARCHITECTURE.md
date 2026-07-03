# System Architecture

## LangGraph Orchestration

### Overview
LangGraph implements a deterministic DAG (Directed Acyclic Graph) workflow for loan application processing. The graph ensures consistent, reproducible decision paths.

### Flow
```
validate_input → profile_analysis → financial_risk → synthesis → compliance
```

### Components

**State Definition** (`src/orchestration/state.py`)
- TypedDict `LoanApplicationState` defines all workflow state
- Fields: application_id, applicant_id, input_data, profile/risk/decision/compliance results
- Status tracking: pending → approved/rejected/manual_review/error

**Graph Creation** (`src/orchestration/graph.py`)
- `create_loan_approval_graph()`: Creates compiled StateGraph
- Nodes: validate_input, profile_analysis, financial_risk, synthesis, compliance
- Edges: Sequential execution order
- Entry point: validate_input
- Exit point: compliance

**Nodes** (`src/orchestration/nodes.py`)
- 5 nodes execute agents in sequence
- profile_analysis_node: Calls applicant_profile_agent + inserts MCP data
- financial_risk_node: Calls financial_risk_agent
- synthesis_node: Calls loan_decision_agent
- compliance_node: Calls compliance_orchestrator_agent
- Each node updates state with results

**Execution** (`src/orchestration/graph.py:process_loan_application`)
- Creates initial state with application data
- Calls `graph.invoke(initial_state)`
- Recursion limit: 25 steps
- Returns final LoanApplicationState with all analysis

### Data Flow
```
LoanApplicationRequest (API)
    ↓
Initial LoanApplicationState
    ↓
[5 Node Sequential Execution]
    ↓
Final LoanApplicationState (DB storage)
```

---

## MCP Servers

### Overview
4 independent FastAPI servers provide microservices for data access and business logic.

### Services

**1. ApplicantDB** (`src/mcp/services/applicant_db.py`)
- Port: 8001
- Tables: applicants, employment_history, credit_history
- Functions:
  - `get_applicant_profile(applicant_id)`: Returns applicant demographics
  - `get_employment_history(applicant_id)`: Returns employment details
  - `get_credit_history(applicant_id)`: Returns credit metrics
  - `insert_applicant_data(applicant_data)`: Auto-populates tables on app submission
- Called by: profile_analysis_node

**2. RiskRules** (`src/mcp/services/risk_rules.py`)
- Port: 8002
- Tables: risk_thresholds
- Functions:
  - `calculate_dti(monthly_income, monthly_liabilities)`
  - `get_credit_score_risk_level(credit_score)`
  - `calculate_loan_amount_risk(loan_amount, annual_income, dti_ratio)`
  - `detect_anomalies(applicant_data)`
- Called by: financial_risk_agent

**3. DecisionSynthesis** (`src/mcp/services/decision_synthesis.py`)
- Port: 8003
- Tables: decision_rules, decision_history
- Functions:
  - `apply_decision_rules(profile, financial_risk, compliance)`
  - `calculate_confidence_score(evidence_set)`
  - `generate_explanation(decision_factors)`
- Called by: loan_decision_agent

**4. NotificationSystem** (`src/mcp/services/notification_system.py`)
- Port: 8004
- Tables: audit_logs, notification_archive
- Functions:
  - `send_notification(applicant_id, decision, channels)`
  - `create_audit_log(application_id, decision, reasoning)`
- Called by: compliance_orchestrator_agent

### Connection
- All services use MySQL connection via SQLAlchemy
- Connection string: `mysql+pymysql://root:password@localhost:3306/loan_system`
- Pool pre-ping enabled for health checks
- Auto table creation on startup

### Data Insertion Flow
```
Application Submitted
    ↓
profile_analysis_node executes
    ↓
insert_applicant_data() called
    ↓
Inserts into applicants, employment_history, credit_history
    ↓
Tools can now fetch data via MCP services
```

---

## Integration

**API Call Flow**
```
POST /api/v1/applications
    ↓
create LoanApplication record in loan_applications table
    ↓
background_tasks.add_task(_process_application_background)
    ↓
process_loan_application(app_id, applicant_id, request)
    ↓
LangGraph invokes 5-node workflow
    ↓
Each node may call MCP services for data
    ↓
MCP services fetch/store data in MySQL tables
    ↓
Final decision stored in loan_applications.decision
```

**Status Check Flow**
```
GET /api/v1/applications/{id}
    ↓
Fetch from loan_applications table
    ↓
Return status + decision
```

---

## Verification

LangGraph: ✓ Compiles successfully with 5 nodes
MCP Servers: ✓ All 4 services initialize correctly
Database: ✓ MySQL connected, tables auto-created
Integration: ✓ Data flows through system end-to-end
