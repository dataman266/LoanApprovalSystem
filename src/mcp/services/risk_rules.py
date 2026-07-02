"""RiskRulesDB MCP Server - Financial risk analysis and compliance rules"""

from mcp.server.fastmcp import FastMCP
from src.mcp.mock_data import get_risk_thresholds, generate_anomalies

mcp = FastMCP("RiskRulesDB")


@mcp.tool()
def calculate_dti(monthly_income: float, monthly_liabilities: float) -> dict:
    """
    Calculate Debt-to-Income (DTI) ratio.

    Args:
        monthly_income: Monthly income in dollars
        monthly_liabilities: Monthly debt obligations in dollars

    Returns:
        Dict with DTI ratio and risk assessment
    """
    if monthly_income <= 0:
        return {
            "error": "Invalid income",
            "dti": None,
        }

    dti = monthly_liabilities / monthly_income
    thresholds = get_risk_thresholds()

    if dti <= thresholds["dti_low_threshold"]:
        risk_level = "low"
    elif dti <= thresholds["dti_medium_threshold"]:
        risk_level = "medium"
    elif dti <= thresholds["dti_high_threshold"]:
        risk_level = "high"
    else:
        risk_level = "critical"

    return {
        "dti": round(dti, 3),
        "risk_level": risk_level,
        "monthly_income": monthly_income,
        "monthly_liabilities": monthly_liabilities,
    }


@mcp.tool()
def get_credit_score_risk_level(credit_score: int) -> dict:
    """
    Determine credit score risk level.

    Args:
        credit_score: Credit score (300-850)

    Returns:
        Dict with risk level and reasoning
    """
    thresholds = get_risk_thresholds()

    if credit_score < thresholds["credit_score_low"]:
        risk_level = "high"
        reasoning = "Credit score below minimum threshold for auto-approval"
    elif credit_score < thresholds["credit_score_medium"]:
        risk_level = "medium"
        reasoning = "Credit score indicates moderate risk"
    elif credit_score < thresholds["credit_score_high"]:
        risk_level = "medium"
        reasoning = "Credit score indicates acceptable risk"
    else:
        risk_level = "low"
        reasoning = "Excellent credit score"

    return {
        "credit_score": credit_score,
        "risk_level": risk_level,
        "reasoning": reasoning,
    }


@mcp.tool()
def calculate_loan_amount_risk(
    loan_amount: float, annual_income: float, dti_ratio: float
) -> dict:
    """
    Calculate affordability risk based on loan amount relative to income and DTI.

    Args:
        loan_amount: Requested loan amount
        annual_income: Annual income
        dti_ratio: Current debt-to-income ratio

    Returns:
        Dict with loan amount risk assessment
    """
    thresholds = get_risk_thresholds()

    loan_to_income = loan_amount / max(1, annual_income)

    if dti_ratio > thresholds["dti_high_threshold"]:
        risk_level = "high"
    elif loan_to_income > thresholds["max_loan_to_income_ratio"]:
        risk_level = "high"
    elif loan_to_income > 3.0:
        risk_level = "medium"
    else:
        risk_level = "low"

    return {
        "loan_amount": loan_amount,
        "annual_income": annual_income,
        "loan_to_income_ratio": round(loan_to_income, 2),
        "risk_level": risk_level,
    }


@mcp.tool()
def detect_anomalies(applicant_data: dict) -> dict:
    """
    Detect potential fraud or unusual patterns in applicant data.

    Args:
        applicant_data: Dict with applicant financial data

    Returns:
        Dict with detected anomalies
    """
    anomalies = generate_anomalies(applicant_data)

    severity = "low" if len(anomalies) == 0 else "medium" if len(anomalies) <= 2 else "high"

    return {
        "anomalies_detected": anomalies,
        "anomaly_count": len(anomalies),
        "severity": severity,
        "requires_investigation": len(anomalies) > 0,
    }


@mcp.tool()
def get_risk_thresholds_tool() -> dict:
    """
    Get the current risk thresholds and regulatory limits.

    Returns:
        Dict with all risk thresholds and regulatory limits
    """
    return get_risk_thresholds()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(mcp.app, host="0.0.0.0", port=8002)
