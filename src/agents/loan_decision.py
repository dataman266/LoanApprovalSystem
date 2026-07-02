"""Loan Decision Agent - Synthesizes analysis and makes approval decision"""

import json
from anthropic import Anthropic
from src.models.schemas import DecisionOutput
from src.logger import get_logger
from src.config import get_settings
from src.agents.decision_rules import DecisionRulesEngine, generate_decision_factors
from src.agents.mock_agents import mock_loan_decision, mock_applicant_profile, mock_financial_risk, mock_compliance_check

logger = get_logger(__name__)
settings = get_settings()

try:
    client = Anthropic(api_key=settings.anthropic_api_key) if settings.anthropic_api_key and not settings.anthropic_api_key.startswith("your_") else None
except:
    client = None


def loan_decision_agent(
    applicant_data: dict, profile_analysis: dict, financial_risk: dict, mcp_tools: list
) -> DecisionOutput:
    """
    Make final loan decision using Claude with synthesis tools.

    Args:
        applicant_data: Dict with applicant information
        profile_analysis: Result from profile agent
        financial_risk: Result from financial risk agent
        mcp_tools: List of MCP tools available

    Returns:
        DecisionOutput with decision classification and reasoning
    """

    if not client or settings.demo_mode:
        profile = mock_applicant_profile(applicant_data)
        risk = mock_financial_risk(applicant_data)
        compliance = mock_compliance_check(applicant_data)
        decision = mock_loan_decision(profile, risk, compliance, applicant_data)
        return decision

    model = settings.anthropic_model

    system_prompt = """You are a senior loan underwriting decision maker with deep expertise in credit risk assessment.
Your role is to:
1. Synthesize applicant profile and financial risk analysis
2. Apply decision rules to determine approval status
3. Calculate overall risk score and confidence level
4. Generate clear explanation for the decision
5. Identify conditions for conditional approvals

Decisions must be one of: Approved, Rejected, or Requires Manual Review

Always provide:
- Numeric risk score (0-100)
- Confidence level (0-1)
- Key decision factors (list)
- Clear explanation accessible to applicants"""

    profile_str = json.dumps(profile_analysis, indent=2)
    risk_str = json.dumps(financial_risk, indent=2)

    initial_prompt = f"""Make a final decision on the loan application for {applicant_data.get('applicant_id', 'UNKNOWN')}

APPLICANT PROFILE ANALYSIS:
{profile_str}

FINANCIAL RISK ANALYSIS:
{risk_str}

APPLICANT DETAILS:
- Requested Amount: ${applicant_data.get('loan_amount', 0):,.2f}
- Tenure: {applicant_data.get('loan_tenure_months', 60)} months
- Age: {applicant_data.get('age', 'N/A')}
- Location: {applicant_data.get('location', 'N/A')}

Use the available decision synthesis tools to:
1. Apply decision rules based on risk profile
2. Calculate confidence score in the decision
3. Generate human-readable explanation
4. Check product eligibility

Provide your final decision in JSON format with these fields:
- classification (string: Approved|Rejected|Requires Manual Review)
- risk_score (float, 0-100)
- confidence_level (float, 0-1)
- approved_loan_amount (float or null)
- key_decision_factors (list of strings)
- conditions (list of strings, can be empty)
- explanation (string, clear and applicant-friendly)
- escalation_reason (string or null, only if Requires Manual Review)"""

    messages = [{"role": "user", "content": initial_prompt}]

    while True:
        response = client.messages.create(
            model=model,
            max_tokens=2048,
            system=system_prompt,
            tools=mcp_tools,
            messages=messages,
        )

        if response.stop_reason == "tool_use":
            tool_results = []
            assistant_content = response.content

            for content_block in response.content:
                if content_block.type == "tool_use":
                    tool_result = execute_mock_tool(
                        content_block.name,
                        content_block.input,
                        applicant_data,
                        profile_analysis,
                        financial_risk,
                    )
                    tool_results.append(
                        {
                            "type": "tool_result",
                            "tool_use_id": content_block.id,
                            "content": json.dumps(tool_result),
                        }
                    )

            messages.append({"role": "assistant", "content": assistant_content})
            messages.append({"role": "user", "content": tool_results})

        else:
            return parse_decision_response(response, applicant_data)


def _extract_applicant_parameters(applicant_data: dict) -> dict:
    """Extract and convert applicant parameters to proper types"""
    return {
        "credit_score": float(applicant_data.get("credit_score", 600)),
        "annual_income": float(applicant_data.get("annual_income", 50000)),
        "existing_liabilities": float(applicant_data.get("existing_liabilities", 0)),
        "loan_amount": float(applicant_data.get("loan_amount", 50000)),
        "employment_duration": int(applicant_data.get("employment_duration_months", 12)),
        "tenure_months": int(applicant_data.get("loan_tenure_months", 60)),
        "age": int(applicant_data.get("age", 35)),
    }


def _calculate_confidence(profile: dict) -> float:
    """Calculate confidence score based on profile"""
    profile_score = float(profile.get("income_stability_score", 0.5))
    return min(1.0, (profile_score + 0.7) / 2)


def execute_mock_tool(
    tool_name: str, tool_input: dict, applicant_data: dict, profile: dict, risk: dict
) -> dict:
    """Mock MCP tool execution using explicit decision rules"""

    if tool_name == "apply_decision_rules":
        params = _extract_applicant_parameters(applicant_data)

        risk_result = DecisionRulesEngine.calculate_risk_score(
            credit_score=params["credit_score"],
            annual_income=params["annual_income"],
            existing_liabilities=params["existing_liabilities"],
            loan_amount=params["loan_amount"],
            employment_duration=params["employment_duration"],
            tenure_months=params["tenure_months"],
            age=params["age"],
        )

        risk_score = risk_result["risk_score"]
        confidence = _calculate_confidence(profile)
        classification, decision_reason = DecisionRulesEngine.make_decision(risk_score, confidence)

        return {
            "decision": classification,
            "reason": decision_reason,
            "risk_score": risk_score,
            "confidence": confidence,
            "detail_factors": risk_result["detail_factors"],
        }

    elif tool_name == "calculate_confidence_score":
        confidence = _calculate_confidence(profile)
        return {
            "overall_confidence": confidence,
            "profile_completeness": float(profile.get("income_stability_score", 0.5)),
            "financial_clarity": 0.7,
        }

    elif tool_name == "generate_explanation":
        factors = tool_input.get("decision_factors", {}).get("factors", [])
        decision = tool_input.get("decision_factors", {}).get("decision", "Pending")
        risk_score = tool_input.get("risk_score", 50)

        lines = [
            f"Your loan application has been reviewed and the decision is: {decision.upper()}.",
            f"Risk assessment score: {risk_score}/100.",
        ]
        if factors:
            lines.append("\nKey factors influencing this decision:")
            for f in factors[:5]:
                lines.append(f"  • {f}")

        return {"explanation": " ".join(lines)}

    elif tool_name == "get_product_eligibility":
        return {
            "eligible_products": ["Personal Loan", "Auto Loan"],
            "recommended_product": "Personal Loan",
            "constraints": [],
        }

    return {"error": f"Unknown tool: {tool_name}"}


def _get_approved_loan_amount(classification: str, loan_amount: float) -> float:
    """Determine approved loan amount based on classification"""
    return loan_amount if classification == "Approved" else None


def _build_decision_explanation(risk_score: int, confidence_level: float, decision_reason: str, detail_factors: list) -> str:
    """Build human-readable decision explanation"""
    explanation = f"{decision_reason}\n\n"
    explanation += f"Risk Assessment Score: {risk_score}/100\n"
    explanation += f"Confidence Level: {confidence_level:.0%}\n\n"
    explanation += "Parameter Analysis:\n"
    for detail in detail_factors[:5]:
        explanation += f"• {detail}\n"
    return explanation


def parse_decision_response(response, applicant_data: dict) -> DecisionOutput:
    """Extract structured decision from Claude and apply explicit rules"""

    params = _extract_applicant_parameters(applicant_data)

    risk_result = DecisionRulesEngine.calculate_risk_score(
        credit_score=params["credit_score"],
        annual_income=params["annual_income"],
        existing_liabilities=params["existing_liabilities"],
        loan_amount=params["loan_amount"],
        employment_duration=params["employment_duration"],
        tenure_months=params["tenure_months"],
        age=params["age"],
    )

    risk_score = risk_result["risk_score"]
    evaluations = risk_result["evaluations"]
    hard_rejection_factors = risk_result.get("hard_rejection_factors", [])

    decision_factors = generate_decision_factors(evaluations, risk_score)

    confidence_level = 0.75
    classification, decision_reason = DecisionRulesEngine.make_decision(
        risk_score, confidence_level, hard_rejection_factors
    )

    approved_loan_amount = _get_approved_loan_amount(classification, params["loan_amount"])
    explanation = _build_decision_explanation(risk_score, confidence_level, decision_reason, risk_result["detail_factors"])

    return DecisionOutput(
        classification=classification,
        risk_score=float(risk_score),
        confidence_level=confidence_level,
        approved_loan_amount=approved_loan_amount,
        key_decision_factors=decision_factors,
        conditions=[],
        explanation=explanation,
        escalation_reason=decision_reason if classification == "Requires Manual Review" else None,
    )
