"""NotificationSystem MCP Server - Real audit and compliance"""

import uuid
from datetime import datetime
from mcp.server.fastmcp import FastMCP
from sqlalchemy import create_engine, Column, String, Text, DateTime
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from src.config import get_settings
from src.logger import get_logger

logger = get_logger(__name__)
settings = get_settings()

Base = declarative_base()
engine = create_engine(settings.database_url, pool_recycle=3600, echo=False)
Session = sessionmaker(bind=engine)


class AuditLog(Base):
    __tablename__ = "audit_logs"
    audit_log_id = Column(String(36), primary_key=True)
    application_id = Column(String(36))
    decision = Column(String(50))
    reasoning = Column(Text)
    logged_at = Column(DateTime, default=datetime.utcnow)
    immutable = Column(String(5), default="true")


class Notification(Base):
    __tablename__ = "notifications"
    notification_id = Column(String(36), primary_key=True)
    applicant_id = Column(String(36))
    decision = Column(String(50))
    channels = Column(String(200))
    sent_at = Column(DateTime, default=datetime.utcnow)


class Archive(Base):
    __tablename__ = "archives"
    archive_id = Column(String(36), primary_key=True)
    application_id = Column(String(36))
    context = Column(Text)
    archived_at = Column(DateTime, default=datetime.utcnow)
    immutable = Column(String(5), default="true")


Base.metadata.create_all(engine)
mcp = FastMCP("NotificationSystem")


@mcp.tool()
def check_regulatory_compliance(applicant_data: dict, decision: str) -> dict:
    """Check regulatory compliance"""
    flags = []

    age = applicant_data.get("age", 0)
    if age < 18:
        flags.append("Applicant below minimum age")

    credit_score = applicant_data.get("credit_score", 0)
    if decision == "Approved" and credit_score < 600:
        flags.append("Approval with low credit score requires documentation")

    location = applicant_data.get("location", "")
    if location in ["XX"]:
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
    """Create immutable audit log in database"""
    session = Session()
    try:
        log_id = str(uuid.uuid4())
        audit_log = AuditLog(
            audit_log_id=log_id,
            application_id=application_id,
            decision=decision,
            reasoning=reasoning[:500]
        )
        session.add(audit_log)
        session.commit()

        return {
            "audit_log_id": log_id,
            "application_id": application_id,
            "decision": decision,
            "logged_at": datetime.utcnow().isoformat(),
            "immutable": True,
        }
    except Exception as e:
        session.rollback()
        logger.error(f"Error creating audit log: {e}")
        return {"error": str(e), "status": "error"}
    finally:
        session.close()


@mcp.tool()
def send_notification(applicant_id: str, decision: str, channels: list) -> dict:
    """Send notification and store in database"""
    session = Session()
    try:
        supported_channels = {"dashboard": True}
        sent_channels = [c for c in channels if c in supported_channels]
        failed_channels = [c for c in channels if c not in supported_channels]

        notification = Notification(
            notification_id=str(uuid.uuid4()),
            applicant_id=applicant_id,
            decision=decision,
            channels=",".join(sent_channels)
        )
        session.add(notification)
        session.commit()

        return {
            "applicant_id": applicant_id,
            "decision": decision,
            "sent_channels": sent_channels,
            "failed_channels": failed_channels,
            "notification_sent": len(sent_channels) > 0,
            "sent_at": datetime.utcnow().isoformat(),
        }
    except Exception as e:
        session.rollback()
        logger.error(f"Error sending notification: {e}")
        return {"error": str(e), "status": "error"}
    finally:
        session.close()


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
    """Archive application context in database"""
    session = Session()
    try:
        archive_id = str(uuid.uuid4())
        archive = Archive(
            archive_id=archive_id,
            application_id=application_id,
            context=str(context)
        )
        session.add(archive)
        session.commit()

        return {
            "archive_id": archive_id,
            "application_id": application_id,
            "archived_at": datetime.utcnow().isoformat(),
            "context_size_bytes": len(str(context).encode()),
            "immutable": True,
        }
    except Exception as e:
        session.rollback()
        logger.error(f"Error archiving application: {e}")
        return {"error": str(e), "status": "error"}
    finally:
        session.close()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(mcp.app, host="0.0.0.0", port=8004)
