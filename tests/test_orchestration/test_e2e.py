"""End-to-end orchestration tests"""

import sys
sys.path.insert(0, '/home/ubuntu/Desktop/Assignment')

import pytest
from datetime import datetime
from src.models.schemas import LoanApplicationRequest, EmploymentType
from src.orchestration.graph import process_loan_application


@pytest.mark.asyncio
def test_e2e_approved_application(sample_application_data):
    """Test complete workflow for approved application"""

    app_id = "E2E-APPROVED-001"
    result = process_loan_application(
        app_id,
        sample_application_data.applicant_id,
        sample_application_data,
    )

    assert result is not None
    assert result["application_id"] == app_id
    assert result["final_status"] != "error"
    assert result["applicant_profile"] is not None
    assert result["financial_risk"] is not None
    assert result["decision"] is not None
    assert result["compliance_check"] is not None
    assert len(result["execution_trace"]) >= 5


@pytest.mark.asyncio
def test_e2e_high_risk_application(high_risk_application_data):
    """Test complete workflow for high-risk application"""

    app_id = "E2E-HIGH-RISK-001"
    result = process_loan_application(
        app_id,
        high_risk_application_data.applicant_id,
        high_risk_application_data,
    )

    assert result is not None
    assert result["final_status"] != "error"
    assert result["decision"] is not None
    # High-risk should either be rejected or require manual review
    assert result["decision"].classification in ["Rejected", "Requires Manual Review"]


@pytest.mark.asyncio
def test_e2e_low_risk_application(low_risk_application_data):
    """Test complete workflow for low-risk application"""

    app_id = "E2E-LOW-RISK-001"
    result = process_loan_application(
        app_id,
        low_risk_application_data.applicant_id,
        low_risk_application_data,
    )

    assert result is not None
    assert result["final_status"] != "error"
    assert result["decision"] is not None
    # Low-risk should likely be approved
    assert result["decision"].risk_score < 50


@pytest.mark.asyncio
def test_e2e_state_persistence():
    """Test that state is properly persisted through workflow"""

    app_data = LoanApplicationRequest(
        applicant_id="E2E-STATE-001",
        applicant_name="Test User",
        age=30,
        annual_income=60000,
        employment_type=EmploymentType.EMPLOYED,
        employment_duration_months=12,
        credit_score=700,
        existing_liabilities=300,
        loan_amount=40000,
        loan_tenure_months=60,
        location="CA",
        application_timestamp=datetime.utcnow(),
    )

    app_id = "E2E-STATE-TEST"
    result = process_loan_application(
        app_id,
        app_data.applicant_id,
        app_data,
    )

    # Verify all stages completed
    assert result["applicant_profile"] is not None
    assert result["financial_risk"] is not None
    assert result["decision"] is not None
    assert result["compliance_check"] is not None

    # Verify execution trace
    trace_nodes = [t["node"] for t in result["execution_trace"]]
    expected_nodes = ["validate_input", "profile_analysis", "financial_risk", "synthesis", "compliance"]
    for node in expected_nodes:
        assert node in trace_nodes


@pytest.mark.asyncio
def test_e2e_audit_trail():
    """Test that audit trail is complete"""

    app_data = LoanApplicationRequest(
        applicant_id="E2E-AUDIT-001",
        applicant_name="Audit Test",
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

    app_id = "E2E-AUDIT-TEST"
    result = process_loan_application(app_id, app_data.applicant_id, app_data)

    # Verify execution trace has all required elements
    for trace_entry in result["execution_trace"]:
        assert "node" in trace_entry
        assert "timestamp" in trace_entry
        assert "status" in trace_entry
        # Timestamp should be ISO format
        datetime.fromisoformat(trace_entry["timestamp"])


@pytest.mark.asyncio
def test_e2e_error_handling():
    """Test error handling in workflow"""

    # Create application with missing/invalid data
    app_data = LoanApplicationRequest(
        applicant_id="E2E-ERROR-001",
        applicant_name="Error Test",
        age=25,  # Low age
        annual_income=20000,  # Low income
        employment_type=EmploymentType.UNEMPLOYED,
        employment_duration_months=0,
        credit_score=550,  # Low score
        existing_liabilities=5000,  # High liabilities
        loan_amount=100000,  # High loan amount
        loan_tenure_months=120,
        location="XX",  # Invalid location
        application_timestamp=datetime.utcnow(),
    )

    app_id = "E2E-ERROR-TEST"
    result = process_loan_application(
        app_id,
        app_data.applicant_id,
        app_data,
    )

    # Should still complete without hard error
    assert result is not None
    assert result["decision"] is not None
    # Should have high risk or be rejected/require review
    assert result["decision"].risk_score > 50


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
