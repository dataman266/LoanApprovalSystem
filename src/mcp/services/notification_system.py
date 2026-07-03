"""NotificationSystem MCP Server - Real audit and compliance"""

import uuid
from datetime import datetime
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, String, Text, DateTime
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from src.config import get_settings
from src.logger import get_logger

logger = get_logger(__name__)
settings = get_settings()

Base = declarative_base()
connect_args = {}
if "sqlite" in settings.database_url:
    connect_args = {"check_same_thread": False}

engine = create_engine(
    settings.database_url,
    pool_pre_ping=True if "mysql" in settings.database_url else False,
    pool_recycle=3600,
    echo=False,
    connect_args=connect_args
)
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


app = FastAPI(title="NotificationSystem")


class ToolRequest(BaseModel):
    params: dict = {}


@app.on_event("startup")
def startup():
    try:
        Base.metadata.create_all(engine)
    except Exception as e:
        logger.error(f"DB init error: {e}")


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/notification_system/check_regulatory_compliance")
def api_check_regulatory_compliance(request: ToolRequest):
    try:
        return check_regulatory_compliance(**request.params)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


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


@app.post("/notification_system/create_audit_log")
def api_create_audit_log(request: ToolRequest):
    try:
        return create_audit_log(**request.params)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


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


@app.post("/notification_system/send_notification")
def api_send_notification(request: ToolRequest):
    try:
        return send_notification(**request.params)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


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


@app.post("/notification_system/archive_application_context")
def api_archive_application_context(request: ToolRequest):
    try:
        return archive_application_context(**request.params)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


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
    uvicorn.run(app, host="0.0.0.0", port=8004)
