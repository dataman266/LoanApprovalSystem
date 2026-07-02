"""Mock agents for demo mode - instant decisions with no API calls"""
import uuid
from src.models.schemas import (
    ApplicantProfileOutput,
    FinancialRiskOutput,
    ComplianceOutput,
    DecisionOutput,
)


def mock_applicant_profile(applicant_data: dict) -> ApplicantProfileOutput:
    """Generate instant mock applicant profile"""
    age = applicant_data.get("age", 35)
    employment_duration = applicant_data.get("employment_duration_months", 0)
    credit_score = applicant_data.get("credit_score", 700)

    income_stability = min(1.0, 0.5 + (employment_duration / 12) * 0.02 + (credit_score - 600) / 1000)

    return ApplicantProfileOutput(
        income_stability_score=income_stability,
        employment_risk="low" if employment_duration > 12 else "medium",
        credit_history_summary=f"Credit score {credit_score}, {'Good' if credit_score > 700 else 'Fair'} history",
        employment_duration_months=employment_duration,
        application_completeness_flags=[] if credit_score > 650 else ["Low credit score"],
        reasoning=f"Applicant has {employment_duration} months employment, stable income profile",
    )


def mock_financial_risk(applicant_data: dict) -> FinancialRiskOutput:
    """Generate instant mock financial risk assessment"""
    annual_income = applicant_data.get("annual_income", 50000)
    loan_amount = applicant_data.get("loan_amount", 25000)
    liabilities = applicant_data.get("existing_liabilities", 0)

    monthly_payment = loan_amount / 60
    monthly_income = annual_income / 12
    dti = ((monthly_payment + liabilities) / monthly_income) * 100
    risk_score = min(95, max(20, 50 + max(0, (dti - 35)) * 0.5))

    return FinancialRiskOutput(
        debt_to_income_ratio=dti,
        dti_risk_level="low" if dti < 35 else "medium" if dti < 50 else "high",
        credit_score_risk="low" if applicant_data.get("credit_score", 700) > 700 else "medium",
        loan_amount_risk="low" if loan_amount < annual_income * 0.5 else "high",
        anomalies_detected=[],
        overall_financial_risk_score=risk_score,
        reasoning=f"DTI ratio {dti:.1f}%, loan request ${loan_amount:,.0f}, monthly income ${monthly_income:,.0f}",
    )


def mock_compliance_check(applicant_data: dict) -> ComplianceOutput:
    """Generate instant mock compliance check"""
    age = applicant_data.get("age", 35)

    violations = []
    if age < 21:
        violations.append("Applicant under legal age")

    return ComplianceOutput(
        action_taken="Approved" if not violations else "Manual Review Queued",
        compliance_status="compliant" if not violations else "requires_review",
        case_id=f"CASE-{str(uuid.uuid4())[:8].upper()}",
        notification_sent=False,
        notification_channels=[],
        audit_log_entry_id=f"AUDIT-{str(uuid.uuid4())[:8].upper()}",
        summary="Compliance check completed",
    )


def mock_loan_decision(
    profile_output: ApplicantProfileOutput,
    financial_output: FinancialRiskOutput,
    compliance_output: ComplianceOutput,
) -> DecisionOutput:
    """Generate instant mock loan decision"""
    profile_score = profile_output.income_stability_score * 100
    financial_score = 100 - financial_output.overall_financial_risk_score
    compliance_ok = compliance_output.compliance_status == "compliant"

    combined_score = (profile_score * 0.35 + financial_score * 0.50) * (1.0 if compliance_ok else 0.7)

    if combined_score > 70 and compliance_ok:
        classification = "Approved"
        approved_amount = 50000
        confidence = 0.95
    elif combined_score > 50:
        classification = "Requires Manual Review"
        approved_amount = None
        confidence = 0.65
    else:
        classification = "Rejected"
        approved_amount = None
        confidence = 0.90

    return DecisionOutput(
        classification=classification,
        risk_score=max(0, 100 - combined_score),
        confidence_level=confidence,
        approved_loan_amount=approved_amount,
        key_decision_factors=[
            f"Profile stability: {profile_score:.1f}/100",
            f"Financial health: {financial_score:.1f}/100",
            f"Compliance: {'Approved' if compliance_ok else 'Review Required'}",
        ],
        conditions=[],
        explanation="Decision based on applicant profile, financial analysis, and compliance checks.",
        escalation_reason=None if classification != "Requires Manual Review" else "Borderline case",
    )
