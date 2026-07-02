#!/usr/bin/env python3
"""Seed sample applicant data into database for AI agents to reference"""

import sys
import json
sys.path.insert(0, '/home/ubuntu/Desktop/Assignment')

from src.database import get_db, init_db
from src.models.database import LoanApplication

SAMPLE_APPLICANTS = {
    "APP-001": {
        "name": "Alice Johnson",
        "age": 40,
        "employment_duration": 120,
        "income": 150000,
        "credit_score": 800,
        "liabilities": 200,
    },
    "APP-002": {
        "name": "Bob Wilson",
        "age": 35,
        "employment_duration": 24,
        "income": 75000,
        "credit_score": 720,
        "liabilities": 500,
    },
    "APP-003": {
        "name": "Charlie Brown",
        "age": 28,
        "employment_duration": 3,
        "income": 35000,
        "credit_score": 580,
        "liabilities": 2500,
    },
}


def _create_applicant_input_data(app_id: str, applicant_data: dict) -> str:
    """Create standardized input data for reference applicant"""
    return json.dumps({
        "applicant_id": app_id,
        "applicant_name": applicant_data["name"],
        "age": applicant_data["age"],
        "employment_type": "employed",
        "employment_duration_months": applicant_data["employment_duration"],
        "annual_income": applicant_data["income"],
        "credit_score": applicant_data["credit_score"],
        "existing_liabilities": applicant_data["liabilities"],
        "loan_amount": 50000,
        "loan_tenure_months": 60,
        "location": "CA"
    })


def _create_reference_application(app_id: str, applicant_data: dict) -> LoanApplication:
    """Create reference application record"""
    return LoanApplication(
        id=app_id,
        applicant_id=app_id,
        applicant_name=applicant_data["name"],
        input_data=_create_applicant_input_data(app_id, applicant_data),
        status="reference",
        final_decision_status="reference_data"
    )


def seed_data():
    init_db()
    db = next(get_db())

    print("Seeding sample applicant data...")
    for app_id, data in SAMPLE_APPLICANTS.items():
        app = _create_reference_application(app_id, data)
        db.add(app)

    db.commit()
    print("✅ Sample data seeded successfully")


if __name__ == "__main__":
    seed_data()
