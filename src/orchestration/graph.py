"""LangGraph state graph for loan application orchestration"""

from datetime import datetime
from langgraph.graph import StateGraph
from src.orchestration.state import LoanApplicationState
from src.orchestration.nodes import (
    validate_input_node,
    profile_analysis_node,
    financial_risk_node,
    synthesis_node,
    compliance_node,
)
from src.logger import get_logger

logger = get_logger(__name__)


def create_loan_approval_graph():
    """Create the LangGraph workflow DAG for loan approval"""

    graph = StateGraph(LoanApplicationState)

    # Add nodes
    graph.add_node("validate_input", validate_input_node)
    graph.add_node("profile_analysis", profile_analysis_node)
    graph.add_node("financial_risk", financial_risk_node)
    graph.add_node("synthesis", synthesis_node)
    graph.add_node("compliance", compliance_node)

    # Set entry point
    graph.set_entry_point("validate_input")

    # Add edges (DAG structure - sequential for simplicity)
    graph.add_edge("validate_input", "profile_analysis")
    graph.add_edge("profile_analysis", "financial_risk")
    graph.add_edge("financial_risk", "synthesis")
    graph.add_edge("synthesis", "compliance")

    # Set exit point
    graph.set_finish_point("compliance")

    # Compile graph
    compiled_graph = graph.compile()

    return compiled_graph


def process_loan_application(
    application_id: str,
    applicant_id: str,
    input_data,
) -> LoanApplicationState:
    """
    Process a complete loan application through the orchestration graph.

    Args:
        application_id: Unique application identifier
        applicant_id: Applicant identifier
        input_data: LoanApplicationRequest

    Returns:
        Final LoanApplicationState with all analysis and decision
    """

    # Create initial state
    initial_state: LoanApplicationState = {
        "application_id": application_id,
        "applicant_id": applicant_id,
        "input_data": input_data,
        "applicant_profile": None,
        "financial_risk": None,
        "decision": None,
        "compliance_check": None,
        "final_status": "pending",
        "started_at": datetime.utcnow(),
        "completed_at": None,
        "error_log": [],
        "execution_trace": [],
    }

    logger.info("Starting loan application processing", application_id=application_id)

    try:
        # Create and run graph
        graph = create_loan_approval_graph()

        # Execute workflow
        result = graph.invoke(
            initial_state,
            config={"recursion_limit": 25},
        )

        logger.info(
            "Loan application processing completed",
            application_id=application_id,
            final_status=result.get("final_status"),
        )

        return result

    except Exception as e:
        logger.error(
            "Loan application processing failed",
            application_id=application_id,
            error=str(e),
        )

        initial_state["final_status"] = "error"
        initial_state["error_log"].append(f"Orchestration error: {str(e)}")
        initial_state["completed_at"] = datetime.utcnow()

        return initial_state
