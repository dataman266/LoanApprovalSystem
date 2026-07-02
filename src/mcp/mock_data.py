import random
from datetime import datetime, timedelta
from src.models.schemas import EmploymentType


def seed_hash(seed_str: str, min_val: int = 0, max_val: int = 100) -> int:
    """Deterministic hash-based random number from seed string"""
    hash_val = abs(hash(seed_str)) % (max_val - min_val + 1) + min_val
    return hash_val


def generate_mock_applicant(applicant_id: str) -> dict:
    """Generate deterministic mock applicant profile based on ID"""
    seed = applicant_id

    ages = [25, 28, 32, 35, 40, 45, 50, 55, 60]
    employment_types = [
        EmploymentType.EMPLOYED,
        EmploymentType.SELF_EMPLOYED,
        EmploymentType.EMPLOYED,
        EmploymentType.EMPLOYED,
    ]

    age_idx = seed_hash(seed, 0, len(ages) - 1)
    employment_idx = seed_hash(f"{seed}_emp", 0, len(employment_types) - 1)

    annual_income = 30000 + seed_hash(f"{seed}_income", 0, 150000)
    employment_duration = seed_hash(f"{seed}_duration", 0, 240)

    return {
        "id": applicant_id,
        "age": ages[age_idx],
        "employment_type": employment_types[employment_idx],
        "employment_duration_months": employment_duration,
        "annual_income": annual_income,
        "existing_liabilities": max(0, seed_hash(f"{seed}_liab", -1000, 3000)),
    }


def generate_mock_credit_history(applicant_id: str) -> dict:
    """Generate deterministic mock credit history"""
    seed = applicant_id
    credit_score = 580 + seed_hash(f"{seed}_score", 0, 270)

    late_payments = seed_hash(f"{seed}_late", 0, 5)
    delinquencies = seed_hash(f"{seed}_delin", 0, 2)
    accounts_opened = seed_hash(f"{seed}_accounts", 1, 15)

    years_history = seed_hash(f"{seed}_years", 1, 30)

    return {
        "applicant_id": applicant_id,
        "credit_score": credit_score,
        "late_payments_count": late_payments,
        "delinquencies": delinquencies,
        "accounts_opened": accounts_opened,
        "years_credit_history": years_history,
        "credit_utilization_ratio": seed_hash(f"{seed}_util", 0, 100) / 100,
    }


def generate_mock_employment_history(applicant_id: str) -> dict:
    """Generate deterministic mock employment history"""
    seed = applicant_id

    jobs = []
    num_jobs = seed_hash(f"{seed}_numjobs", 1, 6)
    total_months = 0

    for i in range(num_jobs):
        job_duration = seed_hash(f"{seed}_job{i}_duration", 6, 120)
        total_months += job_duration

        end_date = datetime.utcnow() - timedelta(days=seed_hash(f"{seed}_job{i}_end", 0, 3650))

        jobs.append(
            {
                "position": f"Job {i + 1}",
                "duration_months": job_duration,
                "end_date": end_date.isoformat(),
                "employment_type": "employed",
            }
        )

    return {
        "applicant_id": applicant_id,
        "total_employment_months": total_months,
        "number_of_jobs": num_jobs,
        "employment_history": jobs,
        "current_employment_stability": "good" if num_jobs <= 3 else "unstable",
    }


def generate_anomalies(applicant_data: dict) -> list:
    """Detect potential anomalies based on applicant data"""
    anomalies = []

    if applicant_data.get("credit_score", 0) < 620:
        anomalies.append("credit_score_below_620")

    dti = (applicant_data.get("existing_liabilities", 0) * 12) / max(
        1, applicant_data.get("annual_income", 1)
    )
    if dti > 0.60:
        anomalies.append("dti_critically_high")
    elif dti > 0.43:
        anomalies.append("dti_above_regulatory_threshold")

    employment_duration = applicant_data.get("employment_duration_months", 0)
    if employment_duration < 6:
        anomalies.append("insufficient_employment_history")

    requested_amount = applicant_data.get("loan_amount", 0)
    annual_income = applicant_data.get("annual_income", 1)
    if requested_amount > annual_income * 5:
        anomalies.append("loan_amount_exceeds_5x_income")

    return anomalies


def get_risk_thresholds() -> dict:
    """Return fixed risk thresholds and regulatory limits"""
    return {
        "dti_low_threshold": 0.36,
        "dti_medium_threshold": 0.43,
        "dti_high_threshold": 0.60,
        "credit_score_low": 620,
        "credit_score_medium": 660,
        "credit_score_high": 720,
        "min_employment_months": 6,
        "max_loan_to_income_ratio": 5.0,
        "approval_risk_threshold": 30,
        "review_risk_threshold": 75,
        "confidence_approval_threshold": 0.85,
        "confidence_review_threshold": 0.60,
    }
