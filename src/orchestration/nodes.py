"""LangGraph node implementations for loan approval workflow"""

from datetime import datetime
from src.orchestration.state import LoanApplicationState
from src.agents.applicant_profile import applicant_profile_agent
from src.agents.financial_risk import financial_risk_agent
from src.agents.loan_decision import loan_decision_agent
from src.agents.compliance_orchestrator import compliance_orchestrator_agent
from src.logger import get_logger

logger = get_logger(__name__)

MCP_APPLICANT_DB_TOOLS = [
    {
        "name": "get_applicant_profile",
        "description": "Get applicant profile information",
        "input_schema": {
            "type": "object",
            "properties": {"applicant_id": {"type": "string"}},
            "required": ["applicant_id"],
        },
    },
    {
        "name": "get_employment_history",
        "description": "Get employment history",
        "input_schema": {
            "type": "object",
            "properties": {"applicant_id": {"type": "string"}},
            "required": ["applicant_id"],
        },
    },
    {
        "name": "get_credit_history",
        "description": "Get credit history",
        "input_schema": {
            "type": "object",
            "properties": {"applicant_id": {"type": "string"}},
            "required": ["applicant_id"],
        },
    },
    {
        "name": "validate_application_completeness",
        "description": "Validate application completeness",
        "input_schema": {
            "type": "object",
            "properties": {"applicant_id": {"type": "string"}},
            "required": ["applicant_id"],
        },
    },
]

MCP_RISK_RULES_TOOLS = [
    {
        "name": "calculate_dti",
        "description": "Calculate debt-to-income ratio",
        "input_schema": {
            "type": "object",
            "properties": {
                "monthly_income": {"type": "number"},
                "monthly_liabilities": {"type": "number"},
            },
            "required": ["monthly_income", "monthly_liabilities"],
        },
    },
    {
        "name": "get_credit_score_risk_level",
        "description": "Get credit score risk level",
        "input_schema": {
            "type": "object",
            "properties": {"credit_score": {"type": "integer"}},
            "required": ["credit_score"],
        },
    },
    {
        "name": "calculate_loan_amount_risk",
        "description": "Calculate loan amount risk",
        "input_schema": {
            "type": "object",
            "properties": {
                "loan_amount": {"type": "number"},
                "annual_income": {"type": "number"},
                "dti_ratio": {"type": "number"},
            },
            "required": ["loan_amount", "annual_income", "dti_ratio"],
        },
    },
    {
        "name": "detect_anomalies",
        "description": "Detect anomalies in applicant data",
        "input_schema": {
            "type": "object",
            "properties": {"applicant_data": {"type": "object"}},
            "required": ["applicant_data"],
        },
    },
    {
        "name": "get_risk_thresholds_tool",
        "description": "Get risk thresholds",
        "input_schema": {"type": "object", "properties": {}},
    },
]

MCP_DECISION_SYNTHESIS_TOOLS = [
    {
        "name": "apply_decision_rules",
        "description": "Apply decision rules",
        "input_schema": {
            "type": "object",
            "properties": {
                "profile_analysis": {"type": "object"},
                "financial_risk": {"type": "object"},
                "compliance_status": {"type": "string"},
            },
            "required": ["profile_analysis", "financial_risk", "compliance_status"],
        },
    },
    {
        "name": "calculate_confidence_score",
        "description": "Calculate confidence score",
        "input_schema": {
            "type": "object",
            "properties": {"evidence_set": {"type": "object"}},
            "required": ["evidence_set"],
        },
    },
    {
        "name": "generate_explanation",
        "description": "Generate explanation",
        "input_schema": {
            "type": "object",
            "properties": {"decision_factors": {"type": "object"}},
            "required": ["decision_factors"],
        },
    },
    {
        "name": "get_product_eligibility",
        "description": "Get product eligibility",
        "input_schema": {
            "type": "object",
            "properties": {
                "loan_amount": {"type": "number"},
                "tenure_months": {"type": "integer"},
                "age": {"type": "integer"},
            },
            "required": ["loan_amount", "tenure_months", "age"],
        },
    },
]

MCP_NOTIFICATION_TOOLS = [
    {
        "name": "check_regulatory_compliance",
        "description": "Check regulatory compliance",
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
        "description": "Create audit log entry",
        "input_schema": {
            "type": "object",
            "properties": {
                "application_id": {"type": "string"},
                "decision": {"type": "string"},
                "reasoning": {"type": "string"},
                "timestamp": {"type": "string"},
            },
            "required": ["application_id", "decision", "reasoning", "timestamp"],
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
        "description": "Generate case ID",
        "input_schema": {"type": "object", "properties": {}},
    },
    {
        "name": "archive_application_context",
        "description": "Archive application context",
        "input_schema": {
            "type": "object",
            "properties": {
                "application_id": {"type": "string"},
                "context": {"type": "object"},
            },
            "required": ["application_id", "context"],
        },
    },
]


def _add_execution_trace(state: LoanApplicationState, node_name: str, status: str = "completed") -> None:
    """Record node execution in trace"""
    state["execution_trace"].append({
        "node": node_name,
        "timestamp": datetime.utcnow().isoformat(),
        "status": status,
    })


def validate_input_node(state: LoanApplicationState) -> LoanApplicationState:
    """Validate input data"""
    logger.info("Validating input", application_id=state["application_id"])
    _add_execution_trace(state, "validate_input")
    return state


def profile_analysis_node(state: LoanApplicationState) -> LoanApplicationState:
    """Run applicant profile analysis"""
    logger.info("Starting profile analysis", application_id=state["application_id"])

    try:
        input_dict = state["input_data"].model_dump()
        profile_result = applicant_profile_agent(input_dict, MCP_APPLICANT_DB_TOOLS)
        state["applicant_profile"] = profile_result
        _add_execution_trace(state, "profile_analysis")

        logger.info(
            "Profile analysis completed",
            application_id=state["application_id"],
            employment_risk=profile_result.employment_risk,
        )

    except Exception as e:
        logger.error("Profile analysis failed", error=str(e))
        state["error_log"].append(f"Profile analysis error: {str(e)}")
        state["final_status"] = "error"

    return state


def financial_risk_node(state: LoanApplicationState) -> LoanApplicationState:
    """Run financial risk analysis"""
    logger.info("Starting financial risk analysis", application_id=state["application_id"])

    try:
        input_dict = state["input_data"].model_dump()
        risk_result = financial_risk_agent(input_dict, MCP_RISK_RULES_TOOLS)
        state["financial_risk"] = risk_result
        _add_execution_trace(state, "financial_risk")

        logger.info(
            "Financial risk analysis completed",
            application_id=state["application_id"],
            risk_score=risk_result.overall_financial_risk_score,
        )

    except Exception as e:
        logger.error("Financial risk analysis failed", error=str(e))
        state["error_log"].append(f"Financial risk error: {str(e)}")
        state["final_status"] = "error"

    return state


def _extract_model_dict(model_obj) -> dict:
    """Convert Pydantic model to dict or return empty dict if None"""
    return model_obj.model_dump() if model_obj else {}


def synthesis_node(state: LoanApplicationState) -> LoanApplicationState:
    """Run loan decision synthesis"""
    logger.info("Starting decision synthesis", application_id=state["application_id"])

    if state["final_status"] == "error":
        logger.warning("Skipping synthesis due to prior errors")
        return state

    try:
        input_dict = state["input_data"].model_dump()
        profile_dict = _extract_model_dict(state["applicant_profile"])
        risk_dict = _extract_model_dict(state["financial_risk"])

        decision_result = loan_decision_agent(
            input_dict, profile_dict, risk_dict, MCP_DECISION_SYNTHESIS_TOOLS
        )

        state["decision"] = decision_result
        _add_execution_trace(state, "synthesis")

        logger.info(
            "Decision synthesis completed",
            application_id=state["application_id"],
            classification=decision_result.classification,
        )

    except Exception as e:
        logger.error("Decision synthesis failed", error=str(e))
        state["error_log"].append(f"Synthesis error: {str(e)}")
        state["final_status"] = "error"

    return state


def compliance_node(state: LoanApplicationState) -> LoanApplicationState:
    """Run compliance check and orchestrate actions"""
    logger.info("Starting compliance check", application_id=state["application_id"])

    if state["final_status"] == "error":
        logger.warning("Skipping compliance due to prior errors")
        return state

    try:
        input_dict = state["input_data"].model_dump()
        decision_dict = _extract_model_dict(state["decision"])

        compliance_result = compliance_orchestrator_agent(
            state["application_id"],
            state["applicant_id"],
            input_dict,
            decision_dict,
            MCP_NOTIFICATION_TOOLS,
        )

        state["compliance_check"] = compliance_result
        state["final_status"] = decision_dict.get("classification", "manual_review").lower()
        state["completed_at"] = datetime.utcnow()
        _add_execution_trace(state, "compliance")

        logger.info(
            "Compliance check completed",
            application_id=state["application_id"],
            action_taken=compliance_result.action_taken,
        )

    except Exception as e:
        logger.error("Compliance check failed", error=str(e))
        state["error_log"].append(f"Compliance error: {str(e)}")
        state["final_status"] = "error"

    return state
