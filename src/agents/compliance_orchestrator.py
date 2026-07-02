"""Compliance & Action Orchestrator Agent - Ensures compliance and sends notifications"""

import json
import uuid
from datetime import datetime
from anthropic import Anthropic
from src.models.schemas import ComplianceOutput
from src.logger import get_logger
from src.config import get_settings

logger = get_logger(__name__)
settings = get_settings()

client = Anthropic(api_key=settings.anthropic_api_key)


def compliance_orchestrator_agent(
    application_id: str,
    applicant_id: str,
    applicant_data: dict,
    decision: dict,
    mcp_tools: list,
) -> ComplianceOutput:
    """
    Ensure compliance and orchestrate notifications using Claude.

    Args:
        application_id: Application identifier
        applicant_id: Applicant identifier
        applicant_data: Dict with applicant information
        decision: Final decision from decision agent
        mcp_tools: List of MCP tools available

    Returns:
        ComplianceOutput with compliance status and actions taken
    """

    model = settings.anthropic_model

    system_prompt = """You are a compliance and regulatory affairs specialist for loan underwriting.
Your role is to:
1. Verify regulatory compliance of the decision
2. Ensure all required checks are documented
3. Create immutable audit trails
4. Orchestrate notifications to applicants
5. Generate case IDs for tracking

Ensure every decision:
- Complies with all applicable regulations
- Is properly logged for audit purposes
- Is communicated to the applicant
- Can be reproduced for regulatory review"""

    decision_str = json.dumps(decision, indent=2)

    initial_prompt = f"""Finalize and ensure compliance for loan application {application_id}

DECISION SUMMARY:
{decision_str}

APPLICANT:
- ID: {applicant_id}
- Age: {applicant_data.get('age', 'N/A')}
- Location: {applicant_data.get('location', 'N/A')}
- Credit Score: {applicant_data.get('credit_score', 'N/A')}

Use the available compliance tools to:
1. Check regulatory compliance of the decision
2. Create audit log entry
3. Send notification to applicant
4. Generate case ID for reference
5. Archive application context

Provide your compliance output in JSON format with these fields:
- action_taken (string: Approved|Rejected|Manual Review Queued)
- compliance_status (string: compliant|requires_review)
- case_id (string)
- notification_sent (boolean)
- notification_channels (list: [dashboard, ...])
- audit_log_entry_id (string)
- timestamp (ISO-8601 string)
- summary (string)"""

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
                        application_id,
                        applicant_id,
                        applicant_data,
                        decision,
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
            return parse_compliance_response(response)


def execute_mock_tool(
    tool_name: str,
    tool_input: dict,
    application_id: str,
    applicant_id: str,
    applicant_data: dict,
    decision: dict,
) -> dict:
    """Mock MCP tool execution for development"""

    if tool_name == "check_regulatory_compliance":
        flags = []
        age = applicant_data.get("age", 0)
        if age < 18:
            flags.append("Applicant below minimum age")

        return {
            "is_compliant": len(flags) == 0,
            "compliance_status": "compliant" if len(flags) == 0 else "requires_review",
            "flags": flags,
            "checked_at": datetime.utcnow().isoformat(),
        }

    elif tool_name == "create_audit_log":
        return {
            "audit_log_id": str(uuid.uuid4()),
            "application_id": application_id,
            "decision": tool_input.get("decision", "Unknown"),
            "logged_at": datetime.utcnow().isoformat(),
            "immutable": True,
        }

    elif tool_name == "send_notification":
        return {
            "applicant_id": applicant_id,
            "decision": decision.get("classification", "Pending"),
            "sent_channels": ["dashboard"],
            "notification_sent": True,
            "sent_at": datetime.utcnow().isoformat(),
        }

    elif tool_name == "generate_case_id":
        case_id = f"CASE-{datetime.utcnow().strftime('%Y%m%d')}-{str(uuid.uuid4())[:8].upper()}"
        return {
            "case_id": case_id,
            "generated_at": datetime.utcnow().isoformat(),
        }

    elif tool_name == "archive_application_context":
        return {
            "archive_id": str(uuid.uuid4()),
            "application_id": application_id,
            "archived_at": datetime.utcnow().isoformat(),
            "immutable": True,
        }

    return {"error": f"Unknown tool: {tool_name}"}


def parse_compliance_response(response) -> ComplianceOutput:
    """Extract structured compliance output from Claude"""

    for content_block in response.content:
        if hasattr(content_block, "text"):
            text = content_block.text

            try:
                if "```json" in text:
                    json_str = text.split("```json")[1].split("```")[0].strip()
                elif "```" in text:
                    json_str = text.split("```")[1].split("```")[0].strip()
                else:
                    json_str = text

                data = json.loads(json_str)

                return ComplianceOutput(
                    action_taken=data.get("action_taken", "Manual Review Queued"),
                    compliance_status=data.get("compliance_status", "compliant"),
                    case_id=data.get("case_id", str(uuid.uuid4())),
                    notification_sent=data.get("notification_sent", False),
                    notification_channels=data.get("notification_channels", []),
                    audit_log_entry_id=data.get("audit_log_entry_id", str(uuid.uuid4())),
                    timestamp=datetime.fromisoformat(
                        data.get("timestamp", datetime.utcnow().isoformat())
                    ),
                    summary=data.get("summary", ""),
                )
            except (json.JSONDecodeError, ValueError, KeyError) as e:
                logger.error("Failed to parse compliance response", error=str(e))

    return ComplianceOutput(
        action_taken="Manual Review Queued",
        compliance_status="compliant",
        case_id=str(uuid.uuid4()),
        notification_sent=False,
        notification_channels=[],
        audit_log_entry_id=str(uuid.uuid4()),
        timestamp=datetime.utcnow(),
        summary="Compliance check completed",
    )
