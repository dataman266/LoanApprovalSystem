from sqlalchemy import Column, String, Float, Integer, DateTime, JSON, Boolean
from sqlalchemy.orm import declarative_base
from datetime import datetime

Base = declarative_base()


class LoanApplication(Base):
    __tablename__ = "loan_applications"

    id = Column(String(255), primary_key=True, index=True)
    applicant_id = Column(String(255), index=True, nullable=False)
    applicant_name = Column(String(255), nullable=False)

    # Input data (stored as JSON)
    input_data = Column(JSON, nullable=False)

    # Analysis results
    applicant_profile = Column(JSON, nullable=True)
    financial_risk = Column(JSON, nullable=True)
    decision = Column(JSON, nullable=True)
    compliance_check = Column(JSON, nullable=True)

    # Status tracking
    status = Column(String(50), nullable=False, default="pending")  # pending, completed, error
    final_decision_status = Column(String(50), nullable=True)  # approved, rejected, manual_review

    # Audit trail
    execution_trace = Column(JSON, nullable=True, default=[])
    error_log = Column(JSON, nullable=True, default=[])

    # Timestamps
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)

    def __repr__(self):
        return f"<LoanApplication(id={self.id}, status={self.status}, decision={self.final_decision_status})>"
