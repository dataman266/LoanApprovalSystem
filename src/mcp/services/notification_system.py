"""NotificationSystem MCP Server - Compliance, notifications, and audit logging"""

import uuid
from datetime import datetime
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("NotificationSystem")


@mcp.tool()
def check_regulatory_compliance(applicant_data: dict, decision: str) -> dict:
    """
    Verify regulatory compliance for the decision.

    Args:
        applicant_data: Dict with applicant information
        decision: Decision classification (Approved, Rejected, Review)

    Returns:
        Dict with compliance status
    """
    flags = []

    # Mock compliance checks
    age = applicant_data.get("age", 0)
    if age < 18:
        flags.append("Applicant below minimum age")

    credit_score = applicant_data.get("credit_score", 0)
    if decision == "Approved" and credit_score < 600:
        flags.append("Approval with low credit score requires documentation")

    location = applicant_data.get("location", "")
    if location in ["XX"]:  # Mock restricted jurisdiction
        flags.append("Restricted jurisdiction")

    is_compliant = len(flags) == 0

    return {
        "is_compliant": is_compliant,
        "compliance_status": "compliant" if is_compliant else "requires_review",
        "flags": flags,
        "checked_at": datetime.utcnow().isoformat(),
    }


@mcp.tool()
def create_audit_log(
    application_id: str, decision: str, reasoning: str, timestamp: str
) -> dict:
    """
    Create an immutable audit log entry for the decision.

    Args:
        application_id: Unique application identifier
        decision: Final decision classification
        reasoning: Detailed reasoning for the decision
        timestamp: Decision timestamp

    Returns:
        Dict with audit log entry details
    """
    log_id = str(uuid.uuid4())

    return {
        "audit_log_id": log_id,
        "application_id": application_id,
        "decision": decision,
        "reasoning": reasoning[:500],  # Truncate for logging
        "logged_at": datetime.utcnow().isoformat(),
        "timestamp": timestamp,
        "immutable": True,
    }


@mcp.tool()
def send_notification(applicant_id: str, decision: str, channels: list) -> dict:
    """
    Send notification to applicant about the decision.
    For MVP, only in-app dashboard is supported.

    Args:
        applicant_id: Applicant identifier
        decision: Decision classification
        channels: List of notification channels (email, sms, dashboard)

    Returns:
        Dict with notification status
    """
    supported_channels = {"dashboard": True}

    sent_channels = []
    failed_channels = []

    for channel in channels:
        if channel in supported_channels:
            sent_channels.append(channel)
        else:
            failed_channels.append(channel)

    return {
        "applicant_id": applicant_id,
        "decision": decision,
        "sent_channels": sent_channels,
        "failed_channels": failed_channels,
        "notification_sent": len(sent_channels) > 0,
        "sent_at": datetime.utcnow().isoformat(),
    }


@mcp.tool()
def generate_case_id() -> dict:
    """
    Generate a unique case ID for the application.

    Returns:
        Dict with generated case ID
    """
    case_id = f"CASE-{datetime.utcnow().strftime('%Y%m%d')}-{str(uuid.uuid4())[:8].upper()}"

    return {
        "case_id": case_id,
        "generated_at": datetime.utcnow().isoformat(),
    }


@mcp.tool()
def archive_application_context(application_id: str, context: dict) -> dict:
    """
    Archive the complete application context for immutable record-keeping.

    Args:
        application_id: Application identifier
        context: Complete application context to archive

    Returns:
        Dict with archive confirmation
    """
    archive_id = str(uuid.uuid4())

    return {
        "archive_id": archive_id,
        "application_id": application_id,
        "archived_at": datetime.utcnow().isoformat(),
        "context_size_bytes": len(str(context).encode()),
        "immutable": True,
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(mcp.app, host="0.0.0.0", port=8004)
