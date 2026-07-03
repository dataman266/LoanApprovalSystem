"""Streamlit chatbot UI for loan approval system"""

import streamlit as st
import requests
import json
from datetime import datetime
import uuid
from pathlib import Path
import sys

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))
from utils.report_generator import EnhancedReportGenerator

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


def _display_enhanced_report_tabs(result: dict, applicant_data: dict = None) -> None:
    """Display enhanced report with tabs for different sections"""

    # Create tabs for different report sections
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "📋 Summary",
        "📊 Analysis",
        "💡 Improvements",
        "🔄 Process",
        "❓ FAQ",
        "📚 Glossary"
    ])

    with tab1:
        st.markdown(EnhancedReportGenerator.generate_executive_summary(result, applicant_data))
        st.divider()
        st.markdown(EnhancedReportGenerator.generate_simple_explanation(result))

    with tab2:
        st.markdown(EnhancedReportGenerator.generate_detailed_factors_analysis(result))

    with tab3:
        st.markdown(EnhancedReportGenerator.generate_improvement_recommendations(result))

    with tab4:
        st.markdown(EnhancedReportGenerator.generate_process_explanation())

    with tab5:
        st.markdown(EnhancedReportGenerator.generate_faq_section())

    with tab6:
        st.markdown(EnhancedReportGenerator.generate_glossary_section())

    # Add download options
    st.divider()
    st.markdown("### 📥 Download Full Report")

    full_report = EnhancedReportGenerator.generate_complete_enhanced_report(result, applicant_data)

    col1, col2 = st.columns(2)
    with col1:
        st.download_button(
            label="📄 Download as Markdown",
            data=full_report,
            file_name=f"loan_evaluation_{applicant_data.get('applicant_id', 'report') if applicant_data else 'report'}.md",
            mime="text/markdown",
            use_container_width=True,
        )

    with col2:
        st.info("💡 Tip: Save this report for your records and share with others if needed.")


def _display_detailed_evaluation(result: dict) -> None:
    """Display detailed evaluation report with comprehensive textual information"""

    # Main Header
    st.markdown("""
    <div style='background-color: #f0f2f6; padding: 20px; border-radius: 10px; margin-bottom: 20px;'>
        <h2 style='margin: 0; color: #262730;'>📋 DETAILED EVALUATION REPORT</h2>
        <p style='margin: 5px 0 0 0; color: #666; font-size: 14px;'>
            Comprehensive Loan Application Analysis & Decision Summary
        </p>
    </div>
    """, unsafe_allow_html=True)

    # ========== DECISION SUMMARY SECTION ==========
    st.markdown("### 🎯 EXECUTIVE DECISION SUMMARY")
    st.markdown("---")

    explanation = result.get("explanation", "No explanation available")
    classification = result["classification"]
    risk_score = result.get('risk_score', 0)

    if classification == "Rejected":
        st.markdown(f"""
        <div style='background-color: #ffebee; padding: 20px; border-left: 4px solid #f44336; border-radius: 5px; margin-bottom: 20px;'>
            <h4 style='color: #c62828; margin-top: 0;'>❌ APPLICATION REJECTED</h4>
            <p style='color: #333; font-size: 15px; line-height: 1.8;'>{explanation}</p>
            <p style='color: #666; font-size: 14px; font-style: italic; margin: 10px 0 0 0;'>
                This application does not meet our lending criteria at this time. We recommend addressing the identified concerns and reapplying in the future.
            </p>
        </div>
        """, unsafe_allow_html=True)
    elif classification == "Approved":
        st.markdown(f"""
        <div style='background-color: #e8f5e9; padding: 20px; border-left: 4px solid #4caf50; border-radius: 5px; margin-bottom: 20px;'>
            <h4 style='color: #2e7d32; margin-top: 0;'>✅ APPLICATION APPROVED</h4>
            <p style='color: #333; font-size: 15px; line-height: 1.8;'>{explanation}</p>
            <p style='color: #666; font-size: 14px; font-style: italic; margin: 10px 0 0 0;'>
                Your application has been approved based on strong financial metrics and creditworthiness indicators.
            </p>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div style='background-color: #fff3e0; padding: 20px; border-left: 4px solid #ff9800; border-radius: 5px; margin-bottom: 20px;'>
            <h4 style='color: #e65100; margin-top: 0;'>⏳ UNDER REVIEW</h4>
            <p style='color: #333; font-size: 15px; line-height: 1.8;'>{explanation}</p>
            <p style='color: #666; font-size: 14px; font-style: italic; margin: 10px 0 0 0;'>
                This application requires additional consideration and may be reviewed by our lending specialists.
            </p>
        </div>
        """, unsafe_allow_html=True)

    # ========== DETAILED ANALYSIS SECTION ==========
    st.markdown("### 📊 COMPREHENSIVE FINANCIAL ANALYSIS")
    st.markdown("---")

    st.markdown("")  # Spacing

    # Generate detailed analytical paragraphs
    st.markdown("""
    Our comprehensive evaluation analyzed multiple key financial indicators to assess your creditworthiness and ability to repay the requested loan. The following sections detail each aspect of the analysis:
    """)

    st.markdown("""
    **Risk Assessment Overview:**
    Our decision is based on a sophisticated evaluation algorithm that considers 8 major financial parameters:
    credit score, debt-to-income ratio, employment duration, loan-to-income ratio, annual income level,
    applicant age, requested loan amount, and proposed loan tenure. Each factor is weighted according to
    industry standards and lending best practices to calculate an overall risk score.
    """)

    st.markdown("---")

    # ========== RISK METRICS SECTION ==========
    st.markdown("### 📊 RISK METRICS & SCORING DETAILS")
    st.markdown("---")

    risk_score = result.get('risk_score', 0)
    confidence = result.get('confidence_level', 0)

    if risk_score < 25:
        risk_level = "🟢 Very Low Risk"
        risk_color = "#4caf50"
        risk_interpretation = "Excellent creditworthiness with minimal lending risk."
    elif risk_score < 50:
        risk_level = "🟡 Low-Moderate Risk"
        risk_color = "#8bc34a"
        risk_interpretation = "Good creditworthiness with manageable lending risk."
    elif risk_score < 75:
        risk_level = "🟠 Moderate-High Risk"
        risk_color = "#ff9800"
        risk_interpretation = "Fair creditworthiness with elevated lending risk factors."
    else:
        risk_level = "🔴 High Risk"
        risk_color = "#f44336"
        risk_interpretation = "Poor creditworthiness with significant lending risk."

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

    # Add detailed interpretation
    st.markdown(f"""
    **Risk Profile Interpretation:**

    Your risk score of **{risk_score:.1f}/100** indicates a **{risk_level}** profile. {risk_interpretation}
    The confidence level of **{confidence:.0%}** reflects our certainty in this assessment based on the analyzed data.
    """)

    st.markdown("---")

    # ========== KEY FACTORS SECTION ==========
    if result.get("key_decision_factors"):
        st.markdown("### ✓ DETAILED ANALYSIS OF KEY DECISION FACTORS")
        st.markdown("---")

        st.markdown("""
        The following factors were evaluated in detail during our analysis. Each factor plays a crucial role
        in determining your overall creditworthiness and ability to successfully manage and repay the requested loan.
        """)

        factors = result.get("key_decision_factors", [])
        for i, factor in enumerate(factors, 1):
            st.markdown(f"""
            <div style='background-color: #f5f5f5; padding: 15px; margin-bottom: 12px; border-radius: 5px; border-left: 3px solid #2196f3;'>
                <p style='margin: 0; color: #1976d2; font-weight: bold;'>Factor {i}: {factor}</p>
                <p style='margin: 8px 0 0 0; color: #666; font-size: 14px;'>
                    This metric assesses your financial profile and lending risk based on industry standards.
                </p>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("""
        **Explanation of Key Factors:**
        - **Profile Stability:** Measures the stability of your employment and income based on tenure and history
        - **Financial Health:** Assesses your overall financial situation considering income vs. debt levels
        - **Compliance Status:** Ensures all regulatory and compliance requirements are met
        - **Credit Evaluation:** Reviews your credit history, payment patterns, and credit utilization
        - **Income Analysis:** Evaluates annual income level against industry benchmarks
        - **Employment Risk:** Assesses the stability and duration of your current employment
        - **Risk Profile:** Overall assessment of your financial health across all evaluated parameters
        """)

        st.markdown("---")

    # ========== CONDITIONS SECTION ==========
    if result.get("conditions"):
        st.markdown("### 📋 SPECIAL APPROVAL CONDITIONS & REQUIREMENTS")
        st.markdown("---")

        st.markdown("""
        Your approval is subject to the following conditions that must be met:
        """)

        conditions = result.get("conditions", [])
        for condition in conditions:
            st.markdown(f"""
            <div style='background-color: #e3f2fd; padding: 15px; margin-bottom: 10px; border-radius: 5px; border-left: 3px solid #1976d2;'>
                <p style='margin: 0; color: #333;'>🔹 {condition}</p>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("")  # Spacing

    # ========== RECOMMENDATIONS SECTION ==========
    st.markdown("### 💡 RECOMMENDATIONS & NEXT STEPS")
    st.markdown("---")

    if classification == "Approved":
        st.markdown(f"""
        **Congratulations!** Your application has been approved. Here are your next steps:

        1. **Loan Documentation**: Review and sign the loan agreement and promissory note
        2. **Verification**: Provide final verification of employment and income
        3. **Funding Timeline**: Funds will be disbursed within 3-5 business days
        4. **Loan Management**: Set up automatic payments to ensure timely repayment
        5. **Account Access**: Access your loan account through our online portal

        Your approved loan amount is **${result.get('approved_loan_amount', 'TBD'):,.2f}** with a risk score of **{risk_score:.1f}/100**.
        """)
    else:
        st.markdown("""
        **Application Status**: Your application was not approved at this time.

        **How to Improve Your Application:**
        1. **Improve Credit Score**: Reduce outstanding debts and pay all bills on time
        2. **Increase Income**: Provide additional income sources or documentation
        3. **Reduce Liabilities**: Pay down existing debts to improve debt-to-income ratio
        4. **Employment Stability**: Maintain current employment for at least 6 months
        5. **Reapply Later**: Once conditions improve, feel free to reapply

        We encourage you to address these concerns and reapply in 6-12 months.
        """)

    st.markdown("---")

    # ========== ESCALATION REASON SECTION ==========
    if result.get("escalation_reason"):
        st.markdown("### ⚠️ IMPORTANT NOTICE")
        st.markdown("---")

        st.markdown(f"""
        <div style='background-color: #fff3e0; padding: 15px; border-radius: 5px; border-left: 4px solid #ff9800;'>
            <p style='margin: 0; color: #e65100; font-size: 15px;'><strong>Note:</strong> {result.get("escalation_reason")}</p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("")  # Spacing

    # ========== FOOTER ==========
    st.markdown("""
    <div style='background-color: #f0f2f6; padding: 20px; border-radius: 10px; margin-top: 30px;'>
        <p style='margin: 0; color: #666; font-size: 13px; line-height: 1.6;'>
            <strong>Report Summary:</strong><br>
            This comprehensive evaluation was generated by our Claude AI Loan Processing System, which analyzes
            multiple financial indicators to provide an accurate and fair assessment of your creditworthiness.
            The decision is final and based on our lending criteria and industry standards.
            <br><br>
            <strong>Decision ID:</strong> AUTOMATED | <strong>Status:</strong> FINAL | <strong>Confidence:</strong> {result.get('confidence_level', 0):.0%}
        </p>
    </div>
    """, unsafe_allow_html=True)


def _display_application_summary(application_data: dict) -> None:
    """Display application summary info"""
    if application_data and application_data.get("created_at"):
        col1, col2, col3 = st.columns(3)
        with col1:
            st.text(f"📅 Submitted: {application_data['created_at'][:10]}")
        with col2:
            status_text = "✅ Completed" if application_data.get("completed_at") else "⏳ Processing"
            st.text(f"{status_text}")
        with col3:
            st.text(f"🔔 Status: {application_data['status'].upper()}")


def display_decision(application_data: dict, use_enhanced_report: bool = True) -> None:
    """Display decision and detailed reasoning"""
    if not application_data or not application_data.get("result"):
        st.warning("⏳ Decision not yet available. Please check back in a moment...")
        return

    # Show application summary first
    _display_application_summary(application_data)
    st.markdown("---")

    result = application_data["result"]
    _display_decision_status(result)
    st.divider()

    # Use enhanced report if requested, otherwise use original
    if use_enhanced_report:
        _display_enhanced_report_tabs(result, application_data)
    else:
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


# Sidebar for navigation and settings
page = st.sidebar.radio(
    "Navigation",
    ["📝 Submit Application", "📊 Check Status", "📋 History"],
    index=0,
)

# Settings
with st.sidebar.expander("⚙️ Settings"):
    report_style = st.radio(
        "Report Display Style",
        ["📚 Enhanced (Plain Language)", "📊 Original (Technical)"],
        help="Choose how you want the report to be displayed",
    )
    use_enhanced = report_style == "📚 Enhanced (Plain Language)"
    st.session_state.use_enhanced_report = use_enhanced


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
                use_enhanced = st.session_state.get("use_enhanced_report", True)
                display_decision(app_data, use_enhanced_report=use_enhanced)

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
