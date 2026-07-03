"""Streamlit page for displaying enhanced detailed evaluation reports"""

import streamlit as st
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.report_generator import EnhancedReportGenerator

st.set_page_config(
    page_title="Detailed Evaluation Report",
    page_icon="📊",
    layout="wide",
)

st.title("📊 DETAILED EVALUATION REPORT")
st.markdown("### Plain-Language Loan Application Analysis")


def main():
    """Main function for the detailed report page"""

    # Check if we have result data from session state
    if "current_result" not in st.session_state:
        st.info("ℹ️ No active application. Please submit an application first to view the detailed report.")
        return

    result = st.session_state.get("current_result", {})
    applicant_data = st.session_state.get("current_applicant", {})

    # Generate the enhanced report
    full_report = EnhancedReportGenerator.generate_complete_enhanced_report(result, applicant_data)

    # Display sections with tabs for easier navigation
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📋 Summary",
        "📊 Detailed Analysis",
        "💡 Recommendations",
        "📚 FAQ & Process",
        "📄 Full Report"
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
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(EnhancedReportGenerator.generate_process_explanation())
        with col2:
            st.markdown(EnhancedReportGenerator.generate_faq_section())

    with tab5:
        # Display full report
        st.markdown(full_report)

        # Download button for full report
        st.divider()
        col1, col2, col3 = st.columns([1, 1, 1])

        with col1:
            st.download_button(
                label="📥 Download as Markdown",
                data=full_report,
                file_name=f"loan_evaluation_{st.session_state.get('current_app_id', 'report')}.md",
                mime="text/markdown",
                use_container_width=True,
            )

        with col2:
            # Generate HTML version
            html_report = f"""
            <html>
            <head>
                <meta charset="utf-8">
                <title>Loan Evaluation Report</title>
                <style>
                    body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; margin: 40px; }}
                    h1 {{ color: #1976d2; border-bottom: 3px solid #1976d2; padding-bottom: 10px; }}
                    h2 {{ color: #1976d2; margin-top: 30px; }}
                    h3 {{ color: #424242; }}
                    .success {{ background-color: #e8f5e9; border-left: 4px solid #4caf50; padding: 15px; margin: 10px 0; }}
                    .error {{ background-color: #ffebee; border-left: 4px solid #f44336; padding: 15px; margin: 10px 0; }}
                    .warning {{ background-color: #fff3e0; border-left: 4px solid #ff9800; padding: 15px; margin: 10px 0; }}
                    .info {{ background-color: #e3f2fd; border-left: 4px solid #2196f3; padding: 15px; margin: 10px 0; }}
                    code {{ background-color: #f5f5f5; padding: 2px 6px; border-radius: 3px; }}
                    pre {{ background-color: #f5f5f5; padding: 15px; border-radius: 5px; overflow-x: auto; }}
                    ul {{ margin: 10px 0; padding-left: 20px; }}
                    li {{ margin: 5px 0; }}
                </style>
            </head>
            <body>
            """

            # Convert markdown to simple HTML
            for line in full_report.split('\n'):
                if line.startswith('# '):
                    html_report += f"<h1>{line[2:]}</h1>"
                elif line.startswith('## '):
                    html_report += f"<h2>{line[3:]}</h2>"
                elif line.startswith('### '):
                    html_report += f"<h3>{line[4:]}</h3>"
                elif line.startswith('- '):
                    html_report += f"<li>{line[2:]}</li>"
                elif line.startswith('✅'):
                    html_report += f"<div class='success'>{line}</div>"
                elif line.startswith('❌'):
                    html_report += f"<div class='error'>{line}</div>"
                elif line.startswith('⚠️'):
                    html_report += f"<div class='warning'>{line}</div>"
                elif line.strip():
                    html_report += f"<p>{line}</p>"

            html_report += """
            </body>
            </html>
            """

            st.download_button(
                label="📥 Download as HTML",
                data=html_report,
                file_name=f"loan_evaluation_{st.session_state.get('current_app_id', 'report')}.html",
                mime="text/html",
                use_container_width=True,
            )

        with col3:
            st.info("Reports can be saved and shared with others for review.")


if __name__ == "__main__":
    main()
