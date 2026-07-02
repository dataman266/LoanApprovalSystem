"""Mock agents for demo mode - instant decisions with no API calls"""
import uuid
from src.models.schemas import (
    ApplicantProfileOutput,
    FinancialRiskOutput,
    ComplianceOutput,
    DecisionOutput,
)
from src.agents.decision_rules import DecisionRulesEngine


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
    applicant_data: dict = None,
) -> DecisionOutput:
    """Generate instant mock loan decision using real decision rules"""
    if applicant_data is None:
        applicant_data = {}

    # Use the real DecisionRulesEngine to calculate risk score with actual applicant data
    risk_result = DecisionRulesEngine.calculate_risk_score(
        credit_score=applicant_data.get("credit_score", 700),
        annual_income=applicant_data.get("annual_income", 50000),
        existing_liabilities=applicant_data.get("existing_liabilities", 0),
        loan_amount=applicant_data.get("loan_amount", 25000),
        employment_duration=applicant_data.get("employment_duration_months", profile_output.employment_duration_months),
        tenure_months=applicant_data.get("loan_tenure_months", 60),
        age=applicant_data.get("age", 35),
    )

    risk_score = risk_result["risk_score"]
    confidence_level = 0.75

    # Check compliance
    compliance_ok = compliance_output.compliance_status == "compliant"

    # Apply hard rejection rules
    hard_rejection_factors = risk_result.get("hard_rejection_factors", [])
    if not compliance_ok:
        hard_rejection_factors.append("Compliance check failed")

    # Make decision using real rules
    classification, decision_reason = DecisionRulesEngine.make_decision(
        risk_score, confidence_level, hard_rejection_factors, risk_result["evaluations"]
    )

    approved_amount = applicant_data.get("loan_amount", 25000) if classification == "Approved" else None

    return DecisionOutput(
        classification=classification,
        risk_score=float(risk_score),
        confidence_level=confidence_level,
        approved_loan_amount=approved_amount,
        key_decision_factors=[
            f"Profile stability: {profile_output.income_stability_score*100:.1f}/100",
            f"Financial health: {100 - financial_output.overall_financial_risk_score:.1f}/100",
            f"Compliance: {'Approved' if compliance_ok else 'Review Required'}",
        ],
        conditions=[],
        explanation=decision_reason,
        escalation_reason=decision_reason if classification == "Requires Manual Review" else None,
    )
