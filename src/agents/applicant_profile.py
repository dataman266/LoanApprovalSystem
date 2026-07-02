"""Applicant Profile Agent - Analyzes applicant demographics and employment stability"""

import json
from anthropic import Anthropic
from src.models.schemas import ApplicantProfileOutput
from src.logger import get_logger
from src.config import get_settings

logger = get_logger(__name__)
settings = get_settings()

client = Anthropic(api_key=settings.anthropic_api_key)


def applicant_profile_agent(applicant_data: dict, mcp_tools: list) -> ApplicantProfileOutput:
    """
    Analyze applicant profile using Claude with MCP tools.

    Args:
        applicant_data: Dict with applicant information
        mcp_tools: List of MCP tools available to the agent

    Returns:
        ApplicantProfileOutput with analysis results
    """

    model = settings.anthropic_model

    system_prompt = """You are a loan approval expert agent specializing in applicant profile analysis.
Your role is to:
1. Analyze applicant demographics (age, employment type, income stability)
2. Assess employment risk and duration
3. Review credit history patterns
4. Flag missing or incomplete application data
5. Provide a comprehensive profile assessment with risk indicators

Use the available tools to gather information about the applicant. Return a structured analysis
focusing on income stability, employment risk, and application completeness.

Always provide clear reasoning for your assessments."""

    initial_prompt = f"""Analyze the applicant profile for applicant ID: {applicant_data.get('applicant_id', 'UNKNOWN')}

Applicant Details:
- Name: {applicant_data.get('applicant_name', 'N/A')}
- Age: {applicant_data.get('age', 'N/A')}
- Employment Type: {applicant_data.get('employment_type', 'N/A')}
- Annual Income: ${applicant_data.get('annual_income', 0):,.2f}
- Employment Duration: {applicant_data.get('employment_duration_months', 0)} months
- Credit Score: {applicant_data.get('credit_score', 'N/A')}

Use the available tools to:
1. Get detailed applicant profile
2. Review employment history
3. Check credit history
4. Validate application completeness

Provide your analysis in JSON format with these fields:
- income_stability_score (0-1)
- employment_risk (low|medium|high)
- credit_history_summary (string)
- employment_duration_months (int)
- application_completeness_flags (list)
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
                    # Mock tool execution (replace with actual MCP client call)
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
            # End of agent execution
            return parse_profile_response(response)


def _get_reference_applicant_data(applicant_id: str) -> dict:
    """Retrieve reference applicant data from database if available"""
    try:
        from src.database import get_db
        from src.models.database import LoanApplication
        import json

        db = next(get_db())
        ref = db.query(LoanApplication).filter(LoanApplication.id == applicant_id).first()

        if ref and ref.status == "reference":
            data = json.loads(ref.input_data) if isinstance(ref.input_data, str) else ref.input_data
            return {
                "applicant_id": applicant_id,
                "age": data["age"],
                "employment_type": data["employment_type"],
                "current_annual_income": data["annual_income"],
                "existing_monthly_liabilities": data["existing_liabilities"],
            }
    except Exception:
        pass

    return None


def _get_applicant_profile(applicant_id: str) -> dict:
    """Get applicant profile from reference data or mock"""
    from src.mcp.mock_data import generate_mock_applicant

    ref_data = _get_reference_applicant_data(applicant_id)
    if ref_data:
        return ref_data

    profile = generate_mock_applicant(applicant_id)
    return {
        "applicant_id": applicant_id,
        "age": profile["age"],
        "employment_type": profile["employment_type"],
        "current_annual_income": profile["annual_income"],
        "existing_monthly_liabilities": profile["existing_liabilities"],
    }


def execute_mock_tool(tool_name: str, tool_input: dict, applicant_data: dict) -> dict:
    """Execute mock MCP tool with database-first fallback to mock data"""

    from src.mcp.mock_data import (
        generate_mock_employment_history,
        generate_mock_credit_history,
    )

    applicant_id = applicant_data.get("applicant_id", "UNKNOWN")

    if tool_name == "get_applicant_profile":
        return _get_applicant_profile(applicant_id)

    elif tool_name == "get_employment_history":
        history = generate_mock_employment_history(applicant_id)
        return {
            "applicant_id": applicant_id,
            "total_employment_months": history["total_employment_months"],
            "number_of_jobs": history["number_of_jobs"],
            "current_employment_stability": history["current_employment_stability"],
        }

    elif tool_name == "get_credit_history":
        history = generate_mock_credit_history(applicant_id)
        return {
            "applicant_id": applicant_id,
            "credit_score": history["credit_score"],
            "late_payments_count": history["late_payments_count"],
            "years_credit_history": history["years_credit_history"],
        }

    elif tool_name == "validate_application_completeness":
        return {
            "applicant_id": applicant_id,
            "is_complete": True,
            "completeness_score": 1.0,
            "flags": [],
        }

    return {"error": f"Unknown tool: {tool_name}"}


def _extract_json_from_text(text: str) -> str:
    """Extract JSON from markdown code blocks or plain text"""
    if "```json" in text:
        return text.split("```json")[1].split("```")[0].strip()
    elif "```" in text:
        return text.split("```")[1].split("```")[0].strip()
    return text


def _parse_profile_data(data: dict) -> ApplicantProfileOutput:
    """Convert parsed JSON data to ApplicantProfileOutput"""
    return ApplicantProfileOutput(
        income_stability_score=float(data.get("income_stability_score", 0.5)),
        employment_risk=data.get("employment_risk", "medium"),
        credit_history_summary=data.get("credit_history_summary", ""),
        employment_duration_months=int(data.get("employment_duration_months", 0)),
        application_completeness_flags=data.get("application_completeness_flags", []),
        reasoning=data.get("reasoning", ""),
    )


def _get_fallback_profile() -> ApplicantProfileOutput:
    """Return fallback profile when analysis fails"""
    return ApplicantProfileOutput(
        income_stability_score=0.5,
        employment_risk="medium",
        credit_history_summary="Analysis inconclusive",
        employment_duration_months=0,
        application_completeness_flags=["analysis_failed"],
        reasoning="Agent failed to generate structured response",
    )


def parse_profile_response(response) -> ApplicantProfileOutput:
    """Extract structured response from Claude"""

    for content_block in response.content:
        if hasattr(content_block, "text"):
            try:
                json_str = _extract_json_from_text(content_block.text)
                data = json.loads(json_str)
                return _parse_profile_data(data)

            except (json.JSONDecodeError, ValueError, KeyError) as e:
                logger.error("Failed to parse profile response", error=str(e))

    return _get_fallback_profile()
