"""ApplicantDB MCP Server - Real database integration"""

import json
from datetime import datetime
from typing import Optional
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, String, Integer, Float, DateTime, Text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from src.config import get_settings
from src.logger import get_logger

logger = get_logger(__name__)
settings = get_settings()

# Database setup
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


class Applicant(Base):
    __tablename__ = "applicants"
    applicant_id = Column(String(36), primary_key=True)
    age = Column(Integer)
    employment_type = Column(String(50))
    current_annual_income = Column(Float)
    existing_monthly_liabilities = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class EmploymentHistory(Base):
    __tablename__ = "employment_history"
    employment_id = Column(String(36), primary_key=True)
    applicant_id = Column(String(36))
    total_employment_months = Column(Integer)
    number_of_jobs = Column(Integer)
    current_employment_stability = Column(String(50))
    history_data = Column(Text)


class CreditHistory(Base):
    __tablename__ = "credit_history"
    credit_id = Column(String(36), primary_key=True)
    applicant_id = Column(String(36))
    credit_score = Column(Integer)
    late_payments_count = Column(Integer)
    delinquencies = Column(Integer)
    accounts_opened = Column(Integer)
    years_credit_history = Column(Float)
    credit_utilization_ratio = Column(Float)


app = FastAPI(title="ApplicantDB")

@app.on_event("startup")
def startup():
    try:
        Base.metadata.create_all(engine)
    except Exception as e:
        logger.error(f"DB init error: {e}")


def insert_applicant_data(applicant_data: dict) -> str:
    """Insert applicant data into database"""
    session = Session()
    try:
        applicant_id = applicant_data.get('applicant_id', '')

        applicant = session.query(Applicant).filter(Applicant.applicant_id == applicant_id).first()
        if not applicant:
            applicant = Applicant(
                applicant_id=applicant_id,
                age=applicant_data.get('age'),
                employment_type=applicant_data.get('employment_type', 'employed'),
                current_annual_income=applicant_data.get('annual_income', 0),
                existing_monthly_liabilities=applicant_data.get('existing_liabilities', 0)
            )
            session.add(applicant)

        emp = session.query(EmploymentHistory).filter(EmploymentHistory.applicant_id == applicant_id).first()
        if not emp:
            emp = EmploymentHistory(
                employment_id=f"EMP-{applicant_id}",
                applicant_id=applicant_id,
                total_employment_months=applicant_data.get('employment_duration_months', 0),
                number_of_jobs=1,
                current_employment_stability='stable',
                history_data=json.dumps([{'months': applicant_data.get('employment_duration_months', 0)}])
            )
            session.add(emp)

        credit = session.query(CreditHistory).filter(CreditHistory.applicant_id == applicant_id).first()
        if not credit:
            credit = CreditHistory(
                credit_id=f"CRD-{applicant_id}",
                applicant_id=applicant_id,
                credit_score=applicant_data.get('credit_score', 600),
                late_payments_count=0,
                delinquencies=0,
                accounts_opened=3,
                years_credit_history=5,
                credit_utilization_ratio=0.3
            )
            session.add(credit)

        session.flush()
        session.commit()
        return applicant_id
    except Exception as e:
        session.rollback()
        logger.error(f"Error inserting applicant data: {e}")
        raise
    finally:
        session.close()


class ToolRequest(BaseModel):
    params: dict = {}


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/applicant_db/get_applicant_profile")
def api_get_applicant_profile(request: ToolRequest):
    try:
        return get_applicant_profile(**request.params)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def get_applicant_profile(applicant_id: str) -> dict:
    """Fetch applicant profile from real database"""
    session = Session()
    try:
        applicant = session.query(Applicant).filter(Applicant.applicant_id == applicant_id).first()
        if not applicant:
            return {"error": f"Applicant {applicant_id} not found", "status": "not_found"}
        return {
            "applicant_id": applicant_id,
            "age": applicant.age,
            "employment_type": applicant.employment_type,
            "current_annual_income": applicant.current_annual_income,
            "existing_monthly_liabilities": applicant.existing_monthly_liabilities,
        }
    except Exception as e:
        logger.error(f"Error fetching applicant profile: {e}")
        return {"error": str(e), "status": "error"}
    finally:
        session.close()


@app.post("/applicant_db/get_employment_history")
def api_get_employment_history(request: ToolRequest):
    try:
        return get_employment_history(**request.params)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def get_employment_history(applicant_id: str) -> dict:
    """Fetch employment history from real database"""
    session = Session()
    try:
        emp = session.query(EmploymentHistory).filter(EmploymentHistory.applicant_id == applicant_id).first()
        if not emp:
            return {"error": f"No employment history for {applicant_id}", "status": "not_found"}
        return {
            "applicant_id": applicant_id,
            "total_employment_months": emp.total_employment_months,
            "number_of_jobs": emp.number_of_jobs,
            "current_employment_stability": emp.current_employment_stability,
            "employment_history": json.loads(emp.history_data) if emp.history_data else [],
        }
    except Exception as e:
        logger.error(f"Error fetching employment history: {e}")
        return {"error": str(e), "status": "error"}
    finally:
        session.close()


@app.post("/applicant_db/get_credit_history")
def api_get_credit_history(request: ToolRequest):
    try:
        return get_credit_history(**request.params)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def get_credit_history(applicant_id: str) -> dict:
    """Fetch credit history from real database"""
    session = Session()
    try:
        credit = session.query(CreditHistory).filter(CreditHistory.applicant_id == applicant_id).first()
        if not credit:
            return {"error": f"No credit history for {applicant_id}", "status": "not_found"}
        return {
            "applicant_id": applicant_id,
            "credit_score": credit.credit_score,
            "late_payments_count": credit.late_payments_count,
            "delinquencies": credit.delinquencies,
            "accounts_opened": credit.accounts_opened,
            "years_credit_history": credit.years_credit_history,
            "credit_utilization_ratio": credit.credit_utilization_ratio,
        }
    except Exception as e:
        logger.error(f"Error fetching credit history: {e}")
        return {"error": str(e), "status": "error"}
    finally:
        session.close()


@app.post("/applicant_db/validate_application_completeness")
def api_validate_application_completeness(request: ToolRequest):
    try:
        return validate_application_completeness(**request.params)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def validate_application_completeness(applicant_id: str) -> dict:
    """Validate application completeness in real database"""
    session = Session()
    try:
        applicant = session.query(Applicant).filter(Applicant.applicant_id == applicant_id).first()
        emp = session.query(EmploymentHistory).filter(EmploymentHistory.applicant_id == applicant_id).first()
        credit = session.query(CreditHistory).filter(CreditHistory.applicant_id == applicant_id).first()

        flags = []
        if not applicant:
            flags.append("missing_applicant_profile")
        if not emp:
            flags.append("missing_employment_history")
        if not credit:
            flags.append("missing_credit_history")

        completeness_score = (3 - len(flags)) / 3.0

        return {
            "applicant_id": applicant_id,
            "is_complete": len(flags) == 0,
            "completeness_score": completeness_score,
            "flags": flags,
        }
    except Exception as e:
        logger.error(f"Error validating application: {e}")
        return {"error": str(e), "status": "error"}
    finally:
        session.close()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
