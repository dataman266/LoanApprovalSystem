"""Streamlit chatbot UI for loan approval system"""

import streamlit as st
import requests
import json
from datetime import datetime
import uuid

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

# Track application counter for chronological IDs
if "app_counter" not in st.session_state:
    st.session_state.app_counter = 0


def generate_applicant_id() -> str:
    """Generate chronological applicant ID"""
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    st.session_state.app_counter += 1
    counter = str(st.session_state.app_counter).zfill(4)
    return f"APP-{timestamp}-{counter}"


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
    """Display color-coded decision status with detailed metrics"""
    classification = result["classification"]

    if classification == "Approved":
        st.success(f"✅ **APPLICATION APPROVED**", icon="✅")
        col1, col2, col3 = st.columns(3)
        with col1:
            loan_amount = result.get('approved_loan_amount')
            amount_text = f"${loan_amount:,.2f}" if loan_amount else "N/A"
            st.metric("Approved Loan Amount", amount_text)
        with col2:
            st.metric("Risk Score", f"{result['risk_score']:.1f}/100", delta="Low Risk")
        with col3:
            st.metric("Confidence Level", f"{result['confidence_level']:.0%}")

    elif classification == "Rejected":
        st.error(f"❌ **APPLICATION REJECTED**", icon="❌")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Risk Score", f"{result['risk_score']:.1f}/100", delta="High Risk")
        with col2:
            st.metric("Confidence Level", f"{result['confidence_level']:.0%}")
        with col3:
            st.metric("Decision", "Final")

    else:
        st.warning(f"⏳ **REQUIRES MANUAL REVIEW**", icon="⚠️")
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Risk Score", f"{result['risk_score']:.1f}/100")
        with col2:
            st.metric("Confidence Level", f"{result['confidence_level']:.0%}")


def _display_detailed_evaluation(result: dict) -> None:
    """Display detailed evaluation report with professional formatting"""

    # Main Header
    st.markdown("""
    <div style='background-color: #f0f2f6; padding: 20px; border-radius: 10px; margin-bottom: 20px;'>
        <h2 style='margin: 0; color: #262730;'>📋 DETAILED EVALUATION REPORT</h2>
    </div>
    """, unsafe_allow_html=True)

    # ========== DECISION SUMMARY SECTION ==========
    st.markdown("### 🎯 DECISION SUMMARY")
    st.markdown("---")

    explanation = result.get("explanation", "No explanation available")
    classification = result["classification"]

    if classification == "Rejected":
        st.markdown(f"""
        <div style='background-color: #ffebee; padding: 15px; border-left: 4px solid #f44336; border-radius: 5px; margin-bottom: 20px;'>
            <h4 style='color: #c62828; margin-top: 0;'>❌ APPLICATION REJECTED</h4>
            <p style='color: #333; font-size: 16px; line-height: 1.6;'>{explanation}</p>
        </div>
        """, unsafe_allow_html=True)
    elif classification == "Approved":
        st.markdown(f"""
        <div style='background-color: #e8f5e9; padding: 15px; border-left: 4px solid #4caf50; border-radius: 5px; margin-bottom: 20px;'>
            <h4 style='color: #2e7d32; margin-top: 0;'>✅ APPLICATION APPROVED</h4>
            <p style='color: #333; font-size: 16px; line-height: 1.6;'>{explanation}</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div style='background-color: #fff3e0; padding: 15px; border-left: 4px solid #ff9800; border-radius: 5px; margin-bottom: 20px;'>
            <h4 style='color: #e65100; margin-top: 0;'>⏳ UNDER REVIEW</h4>
            <p style='color: #333; font-size: 16px; line-height: 1.6;'>{explanation}</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("")  # Spacing

    # ========== RISK METRICS SECTION ==========
    st.markdown("### 📊 RISK METRICS")
    st.markdown("---")

    risk_score = result.get('risk_score', 0)
    confidence = result.get('confidence_level', 0)

    if risk_score < 25:
        risk_level = "🟢 Very Low Risk"
        risk_color = "#4caf50"
    elif risk_score < 50:
        risk_level = "🟡 Low-Moderate Risk"
        risk_color = "#8bc34a"
    elif risk_score < 75:
        risk_level = "🟠 Moderate-High Risk"
        risk_color = "#ff9800"
    else:
        risk_level = "🔴 High Risk"
        risk_color = "#f44336"

    # Display metrics in a nice format
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"""
        <div style='background-color: {risk_color}20; padding: 15px; border-radius: 8px; text-align: center;'>
            <p style='margin: 0; font-size: 12px; color: #666;'>RISK SCORE</p>
            <h3 style='margin: 8px 0; color: {risk_color};'>{risk_score:.1f}/100</h3>
            <p style='margin: 0; font-size: 12px; color: #666;'>{risk_level}</p>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div style='background-color: #2196f320; padding: 15px; border-radius: 8px; text-align: center;'>
            <p style='margin: 0; font-size: 12px; color: #666;'>CONFIDENCE LEVEL</p>
            <h3 style='margin: 8px 0; color: #2196f3;'>{confidence:.0%}</h3>
            <p style='margin: 0; font-size: 12px; color: #666;'>Decision Confidence</p>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        decision_color = "#4caf50" if classification == "Approved" else "#f44336"
        st.markdown(f"""
        <div style='background-color: {decision_color}20; padding: 15px; border-radius: 8px; text-align: center;'>
            <p style='margin: 0; font-size: 12px; color: #666;'>DECISION STATUS</p>
            <h3 style='margin: 8px 0; color: {decision_color};'>{classification.upper()}</h3>
            <p style='margin: 0; font-size: 12px; color: #666;'>Final Decision</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("")  # Spacing

    # ========== KEY FACTORS SECTION ==========
    if result.get("key_decision_factors"):
        st.markdown("### ✓ KEY DECISION FACTORS")
        st.markdown("---")

        factors = result.get("key_decision_factors", [])
        for i, factor in enumerate(factors, 1):
            st.markdown(f"""
            <div style='background-color: #f5f5f5; padding: 12px; margin-bottom: 10px; border-radius: 5px; border-left: 3px solid #2196f3;'>
                <p style='margin: 0; color: #333;'><strong>{i}.</strong> {factor}</p>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("")  # Spacing

    # ========== CONDITIONS SECTION ==========
    if result.get("conditions"):
        st.markdown("### 📋 APPROVAL CONDITIONS")
        st.markdown("---")

        conditions = result.get("conditions", [])
        for condition in conditions:
            st.markdown(f"""
            <div style='background-color: #e3f2fd; padding: 12px; margin-bottom: 10px; border-radius: 5px; border-left: 3px solid #1976d2;'>
                <p style='margin: 0; color: #333;'>🔹 {condition}</p>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("")  # Spacing

    # ========== ESCALATION REASON SECTION ==========
    if result.get("escalation_reason"):
        st.markdown("### ⚠️ ESCALATION REASON")
        st.markdown("---")

        st.markdown(f"""
        <div style='background-color: #fff3e0; padding: 15px; border-radius: 5px; border-left: 4px solid #ff9800;'>
            <p style='margin: 0; color: #e65100; font-size: 14px;'>{result.get("escalation_reason")}</p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("")  # Spacing

    # ========== FOOTER ==========
    st.markdown("""
    <div style='background-color: #f0f2f6; padding: 15px; border-radius: 10px; margin-top: 30px; text-align: center;'>
        <p style='margin: 0; color: #666; font-size: 12px;'>
            This decision was generated by Claude AI Loan Processing System
            <br>Decision ID: <strong>AUTOMATED</strong> | Status: <strong>FINAL</strong>
        </p>
    </div>
    """, unsafe_allow_html=True)


def display_decision(application_data: dict) -> None:
    """Display decision and detailed reasoning"""
    if not application_data or not application_data.get("result"):
        st.warning("⏳ Decision not yet available. Please check back in a moment...")
        return

    result = application_data["result"]
    _display_decision_status(result)
    st.divider()
    _display_detailed_evaluation(result)


def _create_application_form() -> dict:
    """Create and return loan application form with user inputs"""
    st.info("💡 Applicant ID will be auto-generated after submission")

    col1, col2 = st.columns(2)

    with col1:
        applicant_name = st.text_input("Full Name", placeholder="John Doe")
        age = st.number_input("Age", min_value=18, max_value=100, value=35)
        annual_income = st.number_input("Annual Income ($)", min_value=10000, value=75000, step=5000)
        credit_score = st.number_input("Credit Score", min_value=300, max_value=850, value=720)

    with col2:
        existing_liabilities = st.number_input("Monthly Liabilities ($)", min_value=0, value=500, step=100)
        employment_duration = st.number_input("Employment Duration (months)", min_value=0, max_value=600, value=24)
        location = st.text_input("Location (State)", value="CA", max_chars=2)
        loan_amount = st.number_input("Requested Loan Amount ($)", min_value=1000, value=50000, step=1000)

    loan_tenure = st.number_input("Loan Tenure (months)", min_value=1, max_value=360, value=60)

    # Generate applicant ID automatically
    applicant_id = generate_applicant_id()

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
