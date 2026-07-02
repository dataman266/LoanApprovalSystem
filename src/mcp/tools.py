"""MCP Tools builder - Creates tool schemas for Claude to use with MCP client"""

from src.mcp.client import get_mcp_client

# ApplicantDB tools
APPLICANT_DB_TOOLS = [
    {
        "name": "get_applicant_profile",
        "description": "Fetch applicant demographic and profile information",
        "input_schema": {
            "type": "object",
            "properties": {"applicant_id": {"type": "string"}},
            "required": ["applicant_id"],
        },
    },
    {
        "name": "get_employment_history",
        "description": "Fetch employment history and stability indicators",
        "input_schema": {
            "type": "object",
            "properties": {"applicant_id": {"type": "string"}},
            "required": ["applicant_id"],
        },
    },
    {
        "name": "get_credit_history",
        "description": "Fetch credit history and scoring information",
        "input_schema": {
            "type": "object",
            "properties": {"applicant_id": {"type": "string"}},
            "required": ["applicant_id"],
        },
    },
    {
        "name": "validate_application_completeness",
        "description": "Validate application data completeness and flag missing/invalid fields",
        "input_schema": {
            "type": "object",
            "properties": {"applicant_id": {"type": "string"}},
            "required": ["applicant_id"],
        },
    },
]

# RiskRules tools
RISK_RULES_TOOLS = [
    {
        "name": "calculate_dti",
        "description": "Calculate debt-to-income ratio",
        "input_schema": {
            "type": "object",
            "properties": {
                "monthly_liabilities": {"type": "number"},
                "annual_income": {"type": "number"},
            },
            "required": ["monthly_liabilities", "annual_income"],
        },
    },
    {
        "name": "get_credit_score_risk_level",
        "description": "Determine credit score risk level",
        "input_schema": {
            "type": "object",
            "properties": {"credit_score": {"type": "number"}},
            "required": ["credit_score"],
        },
    },
    {
        "name": "calculate_loan_amount_risk",
        "description": "Calculate loan amount affordability risk",
        "input_schema": {
            "type": "object",
            "properties": {
                "loan_amount": {"type": "number"},
                "annual_income": {"type": "number"},
                "dti": {"type": "number"},
            },
            "required": ["loan_amount", "annual_income", "dti"],
        },
    },
    {
        "name": "detect_anomalies",
        "description": "Detect anomalies and fraud patterns in application",
        "input_schema": {
            "type": "object",
            "properties": {"applicant_data": {"type": "object"}},
            "required": ["applicant_data"],
        },
    },
    {
        "name": "get_risk_thresholds",
        "description": "Get regulatory risk thresholds and limits",
        "input_schema": {"type": "object", "properties": {}},
    },
]

# DecisionSynthesis tools
DECISION_SYNTHESIS_TOOLS = [
    {
        "name": "apply_decision_rules",
        "description": "Apply business decision rules to generate approval decision",
        "input_schema": {
            "type": "object",
            "properties": {
                "risk_score": {"type": "number"},
                "dti_ratio": {"type": "number"},
                "compliance_status": {"type": "string"},
            },
            "required": ["risk_score", "dti_ratio", "compliance_status"],
        },
    },
    {
        "name": "calculate_confidence_score",
        "description": "Calculate confidence level in the decision",
        "input_schema": {
            "type": "object",
            "properties": {"evidence_set": {"type": "object"}},
            "required": ["evidence_set"],
        },
    },
    {
        "name": "generate_explanation",
        "description": "Generate human-readable explanation for decision",
        "input_schema": {
            "type": "object",
            "properties": {"decision_factors": {"type": "object"}},
            "required": ["decision_factors"],
        },
    },
    {
        "name": "get_product_eligibility",
        "description": "Check loan product eligibility",
        "input_schema": {
            "type": "object",
            "properties": {
                "loan_amount": {"type": "number"},
                "tenure": {"type": "number"},
                "applicant_profile": {"type": "object"},
            },
            "required": ["loan_amount", "tenure", "applicant_profile"],
        },
    },
]

# NotificationSystem tools
NOTIFICATION_SYSTEM_TOOLS = [
    {
        "name": "check_regulatory_compliance",
        "description": "Check regulatory compliance status",
        "input_schema": {
            "type": "object",
            "properties": {
                "applicant_data": {"type": "object"},
                "decision": {"type": "string"},
            },
            "required": ["applicant_data", "decision"],
        },
    },
    {
        "name": "create_audit_log",
        "description": "Create audit log entry for decision",
        "input_schema": {
            "type": "object",
            "properties": {
                "application_id": {"type": "string"},
                "decision": {"type": "string"},
                "reasoning": {"type": "string"},
            },
            "required": ["application_id", "decision", "reasoning"],
        },
    },
    {
        "name": "send_notification",
        "description": "Send notification to applicant",
        "input_schema": {
            "type": "object",
            "properties": {
                "applicant_id": {"type": "string"},
                "decision": {"type": "string"},
                "channels": {"type": "array", "items": {"type": "string"}},
            },
            "required": ["applicant_id", "decision", "channels"],
        },
    },
    {
        "name": "generate_case_id",
        "description": "Generate unique case ID for application",
        "input_schema": {"type": "object", "properties": {}},
    },
]


def execute_tool(server: str, tool_name: str, tool_input: dict):
    """Execute a tool using MCP client"""
    mcp = get_mcp_client()
    return mcp.call_tool(server, tool_name, **tool_input)
