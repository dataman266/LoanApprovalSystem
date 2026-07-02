"""Streamlit chatbot UI for loan approval system"""

import streamlit as st
import requests
import json
from datetime import datetime

st.set_page_config(
    page_title="Loan Approval System",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.title("💰 Loan Approval System")
st.markdown("### Multi-Agent AI-Powered Loan Decision Engine")

API_URL = "http://localhost:8000/api/v1"

# Initialize session state
if "submitted_applications" not in st.session_state:
    st.session_state.submitted_applications = []


def _handle_api_error(error_type: str, error: Exception) -> None:
    """Display appropriate error message based on exception type"""
    if isinstance(error, requests.exceptions.ConnectionError):
        st.error("Cannot connect to API server. Make sure it's running on port 8000.")
    else:
        st.error(f"{error_type}: {str(error)}")


def submit_application(form_data: dict) -> str:
    """Submit loan application to API and return application ID"""
    try:
        response = requests.post(
            f"{API_URL}/applications",
            json=form_data,
            timeout=60,
        )

        if response.status_code == 200:
            return response.json().get("application_id")

        st.error(f"API error: {response.text}")
        return None

    except Exception as e:
        _handle_api_error("Error submitting application", e)
        return None


def get_application_status(application_id: str) -> dict:
    """Get application status from API"""
    try:
        response = requests.get(
            f"{API_URL}/applications/{application_id}",
            timeout=10,
        )
        return response.json() if response.status_code == 200 else None

    except Exception as e:
        st.warning(f"Could not fetch status: {str(e)}")
        return None


def _display_decision_status(result: dict) -> None:
    """Display color-coded decision status"""
    classification = result["classification"]

    if classification == "Approved":
        st.success(f"✅ **APPROVED**", icon="✅")
        col1, col2 = st.columns(2)
        with col1:
            loan_amount = result.get('approved_loan_amount')
            amount_text = f"${loan_amount:,.2f}" if loan_amount else "TBD"
            st.metric("Approved Loan Amount", amount_text)
        with col2:
            st.metric("Risk Score", f"{result['risk_score']:.1f}/100")

    elif classification == "Rejected":
        st.error(f"❌ **REJECTED**", icon="❌")
        st.metric("Risk Score", f"{result['risk_score']:.1f}/100")

    else:
        st.warning(f"⏳ **REQUIRES MANUAL REVIEW**", icon="⚠️")
        st.metric("Risk Score", f"{result['risk_score']:.1f}/100")
        if result.get("escalation_reason"):
            st.info(f"**Reason:** {result['escalation_reason']}")


def _display_decision_details(result: dict) -> None:
    """Display decision explanation and supporting details"""
    st.subheader("Decision Explanation")
    st.write(result.get("explanation", "No explanation available"))

    if result.get("key_decision_factors"):
        st.subheader("Key Decision Factors")
        for factor in result["key_decision_factors"]:
            st.write(f"• {factor}")

    if result.get("conditions"):
        st.subheader("Conditions")
        for condition in result["conditions"]:
            st.write(f"• {condition}")

    st.metric("Confidence Level", f"{result['confidence_level']:.0%}")


def display_decision(application_data: dict) -> None:
    """Display decision and reasoning"""
    if not application_data or not application_data.get("result"):
        st.warning("Decision not yet available. Please check back in a moment.")
        return

    result = application_data["result"]
    _display_decision_status(result)
    _display_decision_details(result)


def _create_application_form() -> dict:
    """Create and return loan application form with user inputs"""
    col1, col2 = st.columns(2)

    with col1:
        applicant_id = st.text_input("Applicant ID", value=f"APP-{datetime.now().strftime('%Y%m%d%H%M%S')}")
        applicant_name = st.text_input("Full Name", placeholder="John Doe")
        age = st.number_input("Age", min_value=18, max_value=100, value=35)
        annual_income = st.number_input("Annual Income ($)", min_value=10000, value=75000, step=5000)

    with col2:
        credit_score = st.number_input("Credit Score", min_value=300, max_value=850, value=720)
        existing_liabilities = st.number_input("Monthly Liabilities ($)", min_value=0, value=500, step=100)
        employment_duration = st.number_input("Employment Duration (months)", min_value=0, max_value=600, value=24)
        location = st.text_input("Location (State)", value="CA", max_chars=2)

    col1, col2 = st.columns(2)
    with col1:
        loan_amount = st.number_input("Requested Loan Amount ($)", min_value=1000, value=50000, step=1000)
    with col2:
        loan_tenure = st.number_input("Loan Tenure (months)", min_value=1, max_value=360, value=60)

    return {
        "applicant_id": applicant_id,
        "applicant_name": applicant_name,
        "age": age,
        "employment_type": "employed",
        "employment_duration_months": employment_duration,
        "annual_income": annual_income,
        "credit_score": credit_score,
        "existing_liabilities": existing_liabilities,
        "loan_amount": loan_amount,
        "loan_tenure_months": loan_tenure,
        "location": location,
    }


def _process_submitted_application(application_id: str) -> None:
    """Process and display submitted application result"""
    st.session_state.submitted_applications.append(application_id)
    st.success(f"✅ Application submitted successfully!")
    st.info(f"**Application ID:** `{application_id}`")

    st.subheader("Application Status")
    with st.spinner("Fetching decision..."):
        app_data = get_application_status(application_id)
        if app_data:
            display_decision(app_data)


def _display_application_history_item(app_id: str) -> None:
    """Display single application history item in expander"""
    app_data = get_application_status(app_id)
    if not app_data:
        st.write("Unable to fetch status")
        return

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Status", app_data["status"])
    with col2:
        st.metric("Created", app_data["created_at"][:10])
    with col3:
        if app_data["completed_at"]:
            st.metric("Completed", app_data["completed_at"][:10])

    if app_data["result"]:
        st.write(f"**Decision:** {app_data['result']['classification']}")
        st.write(f"**Risk Score:** {app_data['result']['risk_score']:.1f}/100")


# Sidebar for navigation
page = st.sidebar.radio(
    "Navigation",
    ["📝 Submit Application", "📊 Check Status", "📋 History"],
    index=0,
)


if page == "📝 Submit Application":
    st.header("New Loan Application")

    with st.form("loan_application_form"):
        form_data = _create_application_form()
        submitted = st.form_submit_button("Submit Application", use_container_width=True)

        if submitted:
            with st.spinner("Processing application..."):
                application_id = submit_application(form_data)

            if application_id:
                _process_submitted_application(application_id)

elif page == "📊 Check Status":
    st.header("Check Application Status")

    application_id = st.text_input(
        "Enter Application ID",
        placeholder="APP-202406301234567",
    )

    if application_id:
        if st.button("Check Status", use_container_width=True):
            with st.spinner("Fetching status..."):
                app_data = get_application_status(application_id)

            if app_data:
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Status", app_data["status"].upper())
                with col2:
                    st.metric("Created", app_data["created_at"])

                st.divider()
                display_decision(app_data)

                if app_data.get("error"):
                    st.error(f"**Error:** {app_data['error']}")
            else:
                st.error("Application not found or unable to retrieve status.")

elif page == "📋 History":
    st.header("Application History")

    if st.session_state.submitted_applications:
        st.write("Recently submitted applications:")

        for app_id in st.session_state.submitted_applications[-10:]:
            with st.expander(f"📄 {app_id}"):
                if st.button("Refresh", key=f"refresh_{app_id}"):
                    pass
                _display_application_history_item(app_id)
    else:
        st.info("No applications submitted yet. Go to 'Submit Application' to get started!")

# Footer
st.divider()
st.markdown(
    """
    <div style="text-align: center; color: gray; font-size: 0.8em;">
    🔐 Loan Approval System v0.1.0 | Powered by Claude & LangGraph
    </div>
    """,
    unsafe_allow_html=True,
)
