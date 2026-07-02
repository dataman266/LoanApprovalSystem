"""Financial Risk Analysis Agent - Calculates DTI, credit risk, and anomalies"""

import json
from anthropic import Anthropic
from src.models.schemas import FinancialRiskOutput
from src.logger import get_logger
from src.config import get_settings

logger = get_logger(__name__)
settings = get_settings()

client = Anthropic(api_key=settings.anthropic_api_key)


def financial_risk_agent(applicant_data: dict, mcp_tools: list) -> FinancialRiskOutput:
    """
    Analyze financial risk using Claude with MCP tools.

    Args:
        applicant_data: Dict with applicant financial information
        mcp_tools: List of MCP tools available to the agent

    Returns:
        FinancialRiskOutput with risk analysis
    """

    model = settings.anthropic_model

    system_prompt = """You are a financial risk assessment expert specializing in loan underwriting.
Your role is to:
1. Calculate Debt-to-Income (DTI) ratio and assess DTI risk
2. Evaluate credit score risk level
3. Assess loan amount affordability risk
4. Detect anomalies and fraud patterns
5. Provide overall financial risk scoring (0-100)

Use the available tools to gather risk data and thresholds. Return a comprehensive
risk assessment with clear numerical scores and reasoning.

Always provide explicit reasoning for risk classifications."""

    annual_income = applicant_data.get("annual_income", 0)
    monthly_income = annual_income / 12
    monthly_liabilities = applicant_data.get("existing_liabilities", 0)
    credit_score = applicant_data.get("credit_score", 650)
    loan_amount = applicant_data.get("loan_amount", 0)

    initial_prompt = f"""Perform comprehensive financial risk analysis for applicant {applicant_data.get('applicant_id', 'UNKNOWN')}

Financial Profile:
- Annual Income: ${annual_income:,.2f}
- Monthly Income: ${monthly_income:,.2f}
- Monthly Liabilities: ${monthly_liabilities:,.2f}
- Credit Score: {credit_score}
- Requested Loan Amount: ${loan_amount:,.2f}
- Loan Tenure: {applicant_data.get('loan_tenure_months', 60)} months

Use the available tools to:
1. Calculate DTI ratio and risk level
2. Determine credit score risk level
3. Assess loan amount affordability risk
4. Detect any anomalies in the profile
5. Get current risk thresholds for context

Provide your analysis in JSON format with these fields:
- debt_to_income_ratio (float, 0-1)
- dti_risk_level (string: low|medium|high|critical)
- credit_score_risk (string: low|medium|high)
- loan_amount_risk (string: low|medium|high)
- anomalies_detected (list of strings)
- overall_financial_risk_score (float, 0-100)
- reasoning (string)"""

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
                        content_block.name, content_block.input, applicant_data
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
            return parse_risk_response(response)


def _classify_dti_risk(dti: float, thresholds: dict) -> str:
    """Classify DTI into risk category"""
    if dti <= thresholds["dti_low_threshold"]:
        return "low"
    elif dti <= thresholds["dti_medium_threshold"]:
        return "medium"
    elif dti <= thresholds["dti_high_threshold"]:
        return "high"
    return "critical"


def _classify_credit_risk(credit_score: float, thresholds: dict) -> str:
    """Classify credit score into risk category"""
    if credit_score < thresholds["credit_score_low"]:
        return "high"
    elif credit_score < thresholds["credit_score_medium"]:
        return "medium"
    return "low"


def _classify_loan_amount_risk(loan_to_income: float) -> str:
    """Classify loan-to-income ratio into risk category"""
    if loan_to_income > 5.0:
        return "high"
    elif loan_to_income > 3.0:
        return "medium"
    return "low"


def execute_mock_tool(tool_name: str, tool_input: dict, applicant_data: dict) -> dict:
    """Mock MCP tool execution for development"""

    from src.mcp.mock_data import (
        generate_anomalies,
        get_risk_thresholds,
    )

    monthly_income = applicant_data.get("annual_income", 0) / 12
    monthly_liabilities = applicant_data.get("existing_liabilities", 0)
    credit_score = applicant_data.get("credit_score", 650)
    loan_amount = applicant_data.get("loan_amount", 0)
    annual_income = applicant_data.get("annual_income", 0)
    thresholds = get_risk_thresholds()

    if tool_name == "calculate_dti":
        dti = monthly_liabilities / max(1, monthly_income)
        return {
            "dti": round(dti, 3),
            "risk_level": _classify_dti_risk(dti, thresholds),
            "monthly_income": monthly_income,
            "monthly_liabilities": monthly_liabilities,
        }

    elif tool_name == "get_credit_score_risk_level":
        return {
            "credit_score": credit_score,
            "risk_level": _classify_credit_risk(credit_score, thresholds),
            "reasoning": f"Credit score {credit_score} indicates {_classify_credit_risk(credit_score, thresholds)} risk",
        }

    elif tool_name == "calculate_loan_amount_risk":
        loan_to_income = loan_amount / max(1, annual_income)
        return {
            "loan_amount": loan_amount,
            "annual_income": annual_income,
            "loan_to_income_ratio": round(loan_to_income, 2),
            "risk_level": _classify_loan_amount_risk(loan_to_income),
        }

    elif tool_name == "detect_anomalies":
        anomalies = generate_anomalies(applicant_data)
        return {
            "anomalies_detected": anomalies,
            "anomaly_count": len(anomalies),
            "severity": "low" if len(anomalies) == 0 else "high",
        }

    elif tool_name == "get_risk_thresholds_tool":
        return thresholds

    return {"error": f"Unknown tool: {tool_name}"}


def _extract_json_from_text(text: str) -> str:
    """Extract JSON from markdown code blocks or plain text"""
    if "```json" in text:
        return text.split("```json")[1].split("```")[0].strip()
    elif "```" in text:
        return text.split("```")[1].split("```")[0].strip()
    return text


def _parse_risk_data(data: dict) -> FinancialRiskOutput:
    """Convert parsed JSON data to FinancialRiskOutput"""
    return FinancialRiskOutput(
        debt_to_income_ratio=float(data.get("debt_to_income_ratio", 0.5)),
        dti_risk_level=data.get("dti_risk_level", "medium"),
        credit_score_risk=data.get("credit_score_risk", "medium"),
        loan_amount_risk=data.get("loan_amount_risk", "medium"),
        anomalies_detected=data.get("anomalies_detected", []),
        overall_financial_risk_score=float(data.get("overall_financial_risk_score", 50)),
        reasoning=data.get("reasoning", ""),
    )


def _get_fallback_risk_output() -> FinancialRiskOutput:
    """Return fallback risk output when analysis fails"""
    return FinancialRiskOutput(
        debt_to_income_ratio=0.5,
        dti_risk_level="medium",
        credit_score_risk="medium",
        loan_amount_risk="medium",
        anomalies_detected=[],
        overall_financial_risk_score=50,
        reasoning="Analysis inconclusive",
    )


def parse_risk_response(response) -> FinancialRiskOutput:
    """Extract structured risk response from Claude"""

    for content_block in response.content:
        if hasattr(content_block, "text"):
            try:
                json_str = _extract_json_from_text(content_block.text)
                data = json.loads(json_str)
                return _parse_risk_data(data)

            except (json.JSONDecodeError, ValueError, KeyError) as e:
                logger.error("Failed to parse risk response", error=str(e))

    return _get_fallback_risk_output()
