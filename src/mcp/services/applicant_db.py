"""ApplicantDB MCP Server - Applicant profile and history management"""

import json
from mcp.server.fastmcp import FastMCP
from src.mcp.mock_data import (
    generate_mock_applicant,
    generate_mock_employment_history,
    generate_mock_credit_history,
)

mcp = FastMCP("ApplicantDB")


@mcp.tool()
def get_applicant_profile(applicant_id: str) -> dict:
    """
    Fetch applicant demographic and profile information.

    Args:
        applicant_id: Unique applicant identifier

    Returns:
        Dict containing applicant profile details
    """
    applicant = generate_mock_applicant(applicant_id)
    return {
        "applicant_id": applicant_id,
        "age": applicant["age"],
        "employment_type": applicant["employment_type"],
        "current_annual_income": applicant["annual_income"],
        "existing_monthly_liabilities": applicant["existing_liabilities"],
    }


@mcp.tool()
def get_employment_history(applicant_id: str) -> dict:
    """
    Fetch employment history and stability indicators.

    Args:
        applicant_id: Unique applicant identifier

    Returns:
        Dict containing employment history and stability metrics
    """
    history = generate_mock_employment_history(applicant_id)
    return {
        "applicant_id": applicant_id,
        "total_employment_months": history["total_employment_months"],
        "number_of_jobs": history["number_of_jobs"],
        "current_employment_stability": history["current_employment_stability"],
        "employment_history": history["employment_history"],
    }


@mcp.tool()
def get_credit_history(applicant_id: str) -> dict:
    """
    Fetch credit history and scoring information.

    Args:
        applicant_id: Unique applicant identifier

    Returns:
        Dict containing credit history and credit score
    """
    history = generate_mock_credit_history(applicant_id)
    return {
        "applicant_id": applicant_id,
        "credit_score": history["credit_score"],
        "late_payments_count": history["late_payments_count"],
        "delinquencies": history["delinquencies"],
        "accounts_opened": history["accounts_opened"],
        "years_credit_history": history["years_credit_history"],
        "credit_utilization_ratio": history["credit_utilization_ratio"],
    }


@mcp.tool()
def validate_application_completeness(applicant_id: str) -> dict:
    """
    Validate application data completeness and flag missing/invalid fields.

    Args:
        applicant_id: Unique applicant identifier

    Returns:
        Dict containing validation flags and completeness score
    """
    flags = []

    # Mock validation logic
    if applicant_id.startswith("incomplete_"):
        flags.append("missing_kyc_documents")
        flags.append("incomplete_income_verification")

    completeness_score = 1.0 if not flags else 0.7

    return {
        "applicant_id": applicant_id,
        "is_complete": len(flags) == 0,
        "completeness_score": completeness_score,
        "flags": flags,
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(mcp.app, host="0.0.0.0", port=8001)
