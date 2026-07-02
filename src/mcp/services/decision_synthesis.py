"""DecisionSynthesis MCP Server - Decision rules and synthesis"""

from mcp.server.fastmcp import FastMCP
from src.mcp.mock_data import get_risk_thresholds

mcp = FastMCP("DecisionSynthesis")


@mcp.tool()
def apply_decision_rules(
    profile_analysis: dict, financial_risk: dict, compliance_status: str
) -> dict:
    """
    Apply business rules to determine approval decision.

    Args:
        profile_analysis: Dict with applicant profile analysis
        financial_risk: Dict with financial risk analysis
        compliance_status: Compliance status string

    Returns:
        Dict with decision classification and reasoning
    """
    thresholds = get_risk_thresholds()

    if not isinstance(financial_risk, dict):
        financial_risk = {}

    risk_score = financial_risk.get("overall_financial_risk_score", 50)

    if compliance_status == "non_compliant":
        return {
            "decision": "Rejected",
            "reason": "Failed regulatory compliance check",
            "risk_score": 100,
        }

    if risk_score > thresholds["review_risk_threshold"]:
        return {
            "decision": "Requires Manual Review",
            "reason": "High risk score exceeds auto-approval threshold",
            "risk_score": risk_score,
        }

    if risk_score > thresholds["approval_risk_threshold"]:
        return {
            "decision": "Requires Manual Review",
            "reason": "Moderate risk requires manual review",
            "risk_score": risk_score,
        }

    return {
        "decision": "Approved",
        "reason": "All checks passed, risk within acceptable threshold",
        "risk_score": risk_score,
    }


@mcp.tool()
def calculate_confidence_score(evidence_set: dict) -> dict:
    """
    Calculate confidence level in the decision based on available evidence.

    Args:
        evidence_set: Dict with profile, financial, and compliance evidence

    Returns:
        Dict with confidence score and breakdown
    """
    profile_complete = evidence_set.get("profile_completeness_score", 0.5)
    financial_clarity = evidence_set.get("financial_clarity", 0.5)
    compliance_clear = evidence_set.get("compliance_clear", True)

    overall_confidence = (profile_complete + financial_clarity) / 2

    if not compliance_clear:
        overall_confidence *= 0.8

    return {
        "overall_confidence": round(min(1.0, max(0.0, overall_confidence)), 2),
        "profile_completeness": profile_complete,
        "financial_clarity": financial_clarity,
        "compliance_clear": compliance_clear,
    }


@mcp.tool()
def generate_explanation(decision_factors: dict) -> dict:
    """
    Generate human-readable explanation for the decision.

    Args:
        decision_factors: Dict with key factors influencing decision

    Returns:
        Dict with formatted explanation
    """
    factors = decision_factors.get("factors", [])
    decision = decision_factors.get("decision", "Pending")

    explanation_lines = [f"Loan application reviewed for {decision.lower()}."]

    if factors:
        explanation_lines.append("Key factors:")
        for factor in factors[:5]:
            explanation_lines.append(f"  • {factor}")

    explanation = " ".join(explanation_lines)

    return {
        "explanation": explanation,
        "factor_count": len(factors),
    }


@mcp.tool()
def get_product_eligibility(loan_amount: float, tenure_months: int, age: int) -> dict:
    """
    Determine product eligibility based on loan characteristics.

    Args:
        loan_amount: Requested loan amount
        tenure_months: Requested tenure in months
        age: Applicant age

    Returns:
        Dict with eligible products and constraints
    """
    eligible_products = []
    constraints = []

    if loan_amount <= 50000 and tenure_months <= 60:
        eligible_products.append("Personal Loan")

    if loan_amount <= 100000 and tenure_months <= 120:
        eligible_products.append("Auto Loan")

    if loan_amount <= 500000 and tenure_months <= 360:
        eligible_products.append("Home Loan")

    if age < 21:
        constraints.append("Requires co-signer (applicant under 21)")

    if age > 70:
        constraints.append("Requires shorter tenure (applicant over 70)")

    if tenure_months > 360:
        constraints.append("Tenure exceeds 30 years maximum")

    return {
        "eligible_products": eligible_products,
        "recommended_product": eligible_products[0] if eligible_products else None,
        "constraints": constraints,
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(mcp.app, host="0.0.0.0", port=8003)
