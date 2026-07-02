"""pytest configuration and fixtures"""

import sys
sys.path.insert(0, '/home/ubuntu/Desktop/Assignment')

import pytest
from src.models.schemas import LoanApplicationRequest, EmploymentType
from datetime import datetime


@pytest.fixture
def sample_application_data():
    """Sample loan application for testing"""
    return LoanApplicationRequest(
        applicant_id="TEST-001",
        applicant_name="John Doe",
        age=35,
        annual_income=75000,
        employment_type=EmploymentType.EMPLOYED,
        employment_duration_months=24,
        credit_score=720,
        existing_liabilities=500,
        loan_amount=50000,
        loan_tenure_months=60,
        location="CA",
        application_timestamp=datetime.utcnow(),
    )


@pytest.fixture
def high_risk_application_data():
    """High-risk loan application for testing"""
    return LoanApplicationRequest(
        applicant_id="TEST-HIGH-RISK",
        applicant_name="Jane Smith",
        age=45,
        annual_income=35000,
        employment_type=EmploymentType.SELF_EMPLOYED,
        employment_duration_months=3,
        credit_score=580,
        existing_liabilities=2500,
        loan_amount=50000,
        loan_tenure_months=60,
        location="TX",
        application_timestamp=datetime.utcnow(),
    )


@pytest.fixture
def low_risk_application_data():
    """Low-risk loan application for testing"""
    return LoanApplicationRequest(
        applicant_id="TEST-LOW-RISK",
        applicant_name="Alice Johnson",
        age=40,
        annual_income=150000,
        employment_type=EmploymentType.EMPLOYED,
        employment_duration_months=120,
        credit_score=800,
        existing_liabilities=200,
        loan_amount=30000,
        loan_tenure_months=36,
        location="NY",
        application_timestamp=datetime.utcnow(),
    )
