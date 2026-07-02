"""RiskRulesDB MCP Server - Real database risk rules"""

from mcp.server.fastmcp import FastMCP
from sqlalchemy import create_engine, Column, String, Float
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from src.config import get_settings
from src.logger import get_logger

logger = get_logger(__name__)
settings = get_settings()

Base = declarative_base()
engine = create_engine(settings.database_url, pool_recycle=3600, echo=False)
Session = sessionmaker(bind=engine)


class RiskThreshold(Base):
    __tablename__ = "risk_thresholds"
    threshold_id = Column(String(36), primary_key=True)
    threshold_name = Column(String(100), unique=True)
    threshold_value = Column(Float)


Base.metadata.create_all(engine)
mcp = FastMCP("RiskRulesDB")


def get_risk_thresholds_from_db() -> dict:
    session = Session()
    try:
        thresholds = session.query(RiskThreshold).all()
        return {t.threshold_name: t.threshold_value for t in thresholds}
    finally:
        session.close()


@mcp.tool()
def calculate_dti(monthly_income: float, monthly_liabilities: float) -> dict:
    """Calculate DTI ratio using real database thresholds"""
    if monthly_income <= 0:
        return {"error": "Invalid income", "dti": None}

    dti = monthly_liabilities / monthly_income
    thresholds = get_risk_thresholds_from_db()

    dti_low = thresholds.get("dti_low_threshold", 0.36)
    dti_medium = thresholds.get("dti_medium_threshold", 0.50)
    dti_high = thresholds.get("dti_high_threshold", 0.70)

    if dti <= dti_low:
        risk_level = "low"
    elif dti <= dti_medium:
        risk_level = "medium"
    elif dti <= dti_high:
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
    """Determine credit score risk level from database thresholds"""
    thresholds = get_risk_thresholds_from_db()

    cs_low = int(thresholds.get("credit_score_low", 580))
    cs_medium = int(thresholds.get("credit_score_medium", 620))
    cs_high = int(thresholds.get("credit_score_high", 740))

    if credit_score < cs_low:
        risk_level = "high"
        reasoning = "Credit score below minimum threshold"
    elif credit_score < cs_medium:
        risk_level = "medium"
        reasoning = "Credit score indicates moderate risk"
    elif credit_score < cs_high:
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
    """Calculate loan amount risk from real thresholds"""
    thresholds = get_risk_thresholds_from_db()

    loan_to_income = loan_amount / max(1, annual_income)
    dti_high = thresholds.get("dti_high_threshold", 0.70)
    max_lti = thresholds.get("max_loan_to_income_ratio", 5.0)

    if dti_ratio > dti_high:
        risk_level = "high"
    elif loan_to_income > max_lti:
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
    """Detect anomalies in applicant data"""
    anomalies = []

    if applicant_data.get("income", 0) <= 0:
        anomalies.append("invalid_income")
    if applicant_data.get("age", 0) < 18 or applicant_data.get("age", 0) > 120:
        anomalies.append("invalid_age")
    if applicant_data.get("credit_score", 0) < 300 or applicant_data.get("credit_score", 0) > 850:
        anomalies.append("invalid_credit_score")
    if applicant_data.get("liabilities", 0) > applicant_data.get("income", 1):
        anomalies.append("high_liabilities_to_income")

    severity = "low" if len(anomalies) == 0 else "medium" if len(anomalies) <= 2 else "high"

    return {
        "anomalies_detected": anomalies,
        "anomaly_count": len(anomalies),
        "severity": severity,
        "requires_investigation": len(anomalies) > 0,
    }


@mcp.tool()
def get_risk_thresholds_tool() -> dict:
    """Get risk thresholds from database"""
    return get_risk_thresholds_from_db()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(mcp.app, host="0.0.0.0", port=8002)
