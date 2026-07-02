from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class EmploymentType(str, Enum):
    EMPLOYED = "employed"
    SELF_EMPLOYED = "self-employed"
    UNEMPLOYED = "unemployed"
    RETIRED = "retired"
    STUDENT = "student"


class LoanApplicationRequest(BaseModel):
    applicant_id: str = Field(..., description="Unique applicant identifier")
    applicant_name: str = Field(..., description="Full name of applicant")
    age: int = Field(..., ge=18, le=100, description="Age in years")
    annual_income: float = Field(..., gt=0, description="Annual income in dollars")
    employment_type: EmploymentType = Field(..., description="Type of employment")
    employment_duration_months: int = Field(default=0, ge=0, description="Duration at current job")
    credit_score: int = Field(..., ge=300, le=850, description="Credit score (300-850)")
    existing_liabilities: float = Field(default=0, ge=0, description="Total existing monthly liabilities")
    loan_amount: float = Field(..., gt=0, description="Requested loan amount")
    loan_tenure_months: int = Field(..., gt=0, le=360, description="Loan tenure in months")
    location: str = Field(..., description="Geographic location/state")
    application_timestamp: Optional[datetime] = Field(default_factory=datetime.utcnow)


class ApplicantProfileOutput(BaseModel):
    income_stability_score: float = Field(..., ge=0, le=1, description="Income stability 0-1")
    employment_risk: str = Field(..., description="low|medium|high")
    credit_history_summary: str = Field(..., description="Summary of credit history")
    employment_duration_months: int = Field(..., description="Employment duration")
    application_completeness_flags: List[str] = Field(default_factory=list, description="Missing/incomplete fields")
    reasoning: str = Field(..., description="Explanation of profile analysis")


class FinancialRiskOutput(BaseModel):
    debt_to_income_ratio: float = Field(..., ge=0, description="DTI ratio")
    dti_risk_level: str = Field(..., description="low|medium|high|critical")
    credit_score_risk: str = Field(..., description="low|medium|high")
    loan_amount_risk: str = Field(..., description="low|medium|high")
    anomalies_detected: List[str] = Field(default_factory=list, description="Detected anomalies")
    overall_financial_risk_score: float = Field(..., ge=0, le=100, description="Overall risk 0-100")
    reasoning: str = Field(..., description="Explanation of risk analysis")


class DecisionOutput(BaseModel):
    classification: str = Field(..., description="Approved|Rejected|Requires Manual Review")
    risk_score: float = Field(..., ge=0, le=100, description="Overall risk score")
    confidence_level: float = Field(..., ge=0, le=1, description="Decision confidence")
    approved_loan_amount: Optional[float] = Field(default=None, description="If approved, loan amount")
    key_decision_factors: List[str] = Field(default_factory=list, description="Key decision factors")
    conditions: List[str] = Field(default_factory=list, description="Conditional approvals")
    explanation: str = Field(..., description="Human-readable explanation")
    escalation_reason: Optional[str] = Field(default=None, description="If manual review, why")


class ComplianceOutput(BaseModel):
    action_taken: str = Field(..., description="Approved|Rejected|Manual Review Queued")
    compliance_status: str = Field(..., description="compliant|requires_review")
    case_id: str = Field(..., description="Unique case reference")
    notification_sent: bool = Field(default=False, description="Notification sent flag")
    notification_channels: List[str] = Field(default_factory=list, description="Email, SMS, etc.")
    audit_log_entry_id: str = Field(..., description="Audit log entry ID")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Timestamp")
    summary: str = Field(..., description="Compliance summary")


class LoanApplicationState(BaseModel):
    application_id: str
    input_data: LoanApplicationRequest
    applicant_profile: Optional[ApplicantProfileOutput] = None
    financial_risk: Optional[FinancialRiskOutput] = None
    decision: Optional[DecisionOutput] = None
    compliance_check: Optional[ComplianceOutput] = None
    final_status: str = "pending"  # pending, approved, rejected, manual_review, error
    error_log: List[str] = Field(default_factory=list)
    execution_trace: List[Dict[str, Any]] = Field(default_factory=list)


class ApplicationStatusResponse(BaseModel):
    application_id: str
    status: str  # pending, completed, error
    created_at: datetime
    completed_at: Optional[datetime] = None
    result: Optional[DecisionOutput] = None
    error: Optional[str] = None


class ApplicationHistoryResponse(BaseModel):
    application_id: str
    applicant_id: str
    status: str
    created_at: datetime
    completed_at: Optional[datetime] = None
    decision: Optional[DecisionOutput] = None
    execution_trace: List[Dict[str, Any]]
