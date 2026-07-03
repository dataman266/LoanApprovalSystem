"""DecisionSynthesis MCP Server - Real decision rules"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, String, Float, DateTime
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
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


class DecisionRule(Base):
    __tablename__ = "decision_rules"
    rule_id = Column(String(36), primary_key=True)
    rule_name = Column(String(100), unique=True)
    threshold_value = Column(Float)
    active = Column(String(5), default="true")


class DecisionHistory(Base):
    __tablename__ = "decision_history"
    decision_id = Column(String(36), primary_key=True)
    applicant_id = Column(String(36))
    decision = Column(String(50))
    risk_score = Column(Float)
    reason = Column(String(500))
    created_at = Column(DateTime, default=datetime.utcnow)


app = FastAPI(title="DecisionSynthesis")


class ToolRequest(BaseModel):
    params: dict = {}


@app.on_event("startup")
def startup():
    try:
        Base.metadata.create_all(engine)
    except Exception as e:
        logger.error(f"DB init error: {e}")


def get_decision_thresholds_from_db() -> dict:
    session = Session()
    try:
        rules = session.query(DecisionRule).filter(DecisionRule.active == "true").all()
        return {r.rule_name: r.threshold_value for r in rules}
    finally:
        session.close()


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/decision_synthesis/apply_decision_rules")
def api_apply_decision_rules(request: ToolRequest):
    try:
        return apply_decision_rules(**request.params)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def apply_decision_rules(
    profile_analysis: dict, financial_risk: dict, compliance_status: str
) -> dict:
    """Apply decision rules from database"""
    thresholds = get_decision_thresholds_from_db()

    if not isinstance(financial_risk, dict):
        financial_risk = {}

    risk_score = financial_risk.get("overall_financial_risk_score", 50)
    review_threshold = thresholds.get("review_risk_threshold", 70)
    approval_threshold = thresholds.get("approval_risk_threshold", 50)

    if compliance_status == "non_compliant":
        return {
            "decision": "Rejected",
            "reason": "Failed regulatory compliance check",
            "risk_score": 100,
        }

    if risk_score > review_threshold:
        return {
            "decision": "Requires Manual Review",
            "reason": "High risk score exceeds auto-approval threshold",
            "risk_score": risk_score,
        }

    if risk_score > approval_threshold:
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


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8003)
