"""LangGraph state definitions for loan application workflow"""

from typing import TypedDict, Optional, List, Dict, Any
from datetime import datetime
from src.models.schemas import (
    LoanApplicationRequest,
    ApplicantProfileOutput,
    FinancialRiskOutput,
    DecisionOutput,
    ComplianceOutput,
)


class LoanApplicationState(TypedDict):
    """Complete state for a loan application workflow"""

    # Core identifiers
    application_id: str
    applicant_id: str

    # Input
    input_data: LoanApplicationRequest

    # Analysis results
    applicant_profile: Optional[ApplicantProfileOutput]
    financial_risk: Optional[FinancialRiskOutput]
    decision: Optional[DecisionOutput]
    compliance_check: Optional[ComplianceOutput]

    # Status & metadata
    final_status: str  # pending, approved, rejected, manual_review, error
    started_at: datetime
    completed_at: Optional[datetime]

    # Audit & debugging
    error_log: List[str]
    execution_trace: List[Dict[str, Any]]
