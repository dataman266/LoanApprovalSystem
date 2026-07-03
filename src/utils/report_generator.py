"""Enhanced report generator for creating detailed, accessible evaluation reports"""

from typing import Dict, List, Any, Optional
from datetime import datetime
import json


class EnhancedReportGenerator:
    """Generates comprehensive, non-technical evaluation reports"""

    # Plain language explanations for technical terms
    GLOSSARY = {
        "credit_score": "A numerical rating (300-850) that reflects your borrowing history and reliability in repaying debts. Higher scores indicate better creditworthiness.",
        "dti_ratio": "Debt-to-Income ratio - the percentage of your monthly income that goes toward paying existing debts. Lower is better (under 43% is ideal).",
        "employment_duration": "How long you've been working at your current job. Longer employment shows stability.",
        "lti_ratio": "Loan-to-Income ratio - the requested loan amount compared to your annual income. Lower ratios are less risky.",
        "risk_score": "A comprehensive score (0-100) that represents the overall financial risk of approving your loan. Lower scores are better.",
        "confidence_level": "How certain our AI system is about the decision, expressed as a percentage. Higher confidence means more reliable decision.",
        "approved_loan_amount": "The maximum amount we're willing to lend you.",
    }

    @staticmethod
    def generate_executive_summary(result: Dict[str, Any], applicant_data: Optional[Dict] = None) -> str:
        """Generate a plain-language executive summary"""
        classification = result.get("classification", "Unknown")
        risk_score = result.get("risk_score", 0)
        confidence = result.get("confidence_level", 0)

        summary_lines = [
            "## 📋 EXECUTIVE SUMMARY (Easy to Understand)",
            "",
            "### What This Report Means",
            "This is a comprehensive evaluation of your loan application. We analyzed your financial",
            "situation using multiple factors to determine if we can approve your loan request.",
            "This report explains our decision in plain, easy-to-understand language.",
            "",
        ]

        # Decision statement
        if classification == "Approved":
            summary_lines.extend([
                "### ✅ DECISION: APPLICATION APPROVED",
                "",
                f"**Great news!** Your loan application has been **APPROVED**.",
                f"We reviewed your financial profile and determined that you meet our lending criteria.",
                f"You have demonstrated good financial responsibility and ability to repay the loan.",
                "",
            ])
        elif classification == "Rejected":
            summary_lines.extend([
                "### ❌ DECISION: APPLICATION REJECTED",
                "",
                f"**We're sorry.** Your loan application has been **NOT APPROVED** at this time.",
                f"Based on our financial analysis, your application does not currently meet our lending requirements.",
                f"This does not mean you'll never qualify - financial situations change over time.",
                "",
            ])
        else:
            summary_lines.extend([
                "### ⏳ DECISION: REQUIRES ADDITIONAL REVIEW",
                "",
                f"Your application requires additional review by our lending specialists.",
                f"This is not a final decision and doesn't mean automatic approval or rejection.",
                "",
            ])

        # Key metrics in simple terms
        summary_lines.extend([
            "### Your Financial Health Snapshot",
            "",
            f"- **Decision Confidence:** {confidence:.0%}",
            f"  (This means we're {confidence:.0%} certain about our decision)",
            "",
            f"- **Overall Risk Score:** {risk_score:.1f} out of 100",
            f"  (Lower scores = lower risk = better for us to lend)",
            "",
        ])

        return "\n".join(summary_lines)

    @staticmethod
    def generate_simple_explanation(result: Dict[str, Any]) -> str:
        """Generate simple explanation of why the decision was made"""
        explanation = result.get("explanation", "")
        risk_score = result.get("risk_score", 0)
        classification = result.get("classification", "")

        lines = [
            "## 🎯 WHY WE MADE THIS DECISION",
            "",
            "### The Human Explanation",
            "",
        ]

        if not explanation:
            lines.append("_No specific explanation was provided for this decision._")
        else:
            lines.append(explanation)

        lines.extend([
            "",
            "### What This Score Means",
            "",
        ])

        if risk_score < 25:
            lines.extend([
                "**Risk Score: Very Low Risk** 🟢",
                "",
                "Your financial profile looks excellent! You have:",
                "- Strong credit history with on-time payments",
                "- Stable employment",
                "- Good income relative to your debts",
                "- A healthy financial situation overall",
                "",
                "This means we have confidence you can repay the loan successfully.",
            ])
        elif risk_score < 50:
            lines.extend([
                "**Risk Score: Low-Moderate Risk** 🟡",
                "",
                "Your financial profile looks good! You have:",
                "- Decent credit history",
                "- Generally stable employment",
                "- Reasonable income-to-debt ratio",
                "- Some positive financial indicators",
                "",
                "This means we believe you can manage the loan payments.",
            ])
        elif risk_score < 75:
            lines.extend([
                "**Risk Score: Moderate-High Risk** 🟠",
                "",
                "Your financial profile has some concerns:",
                "- Credit history needs improvement",
                "- Debt levels are relatively high compared to income",
                "- Employment might be less stable",
                "- Various factors create more uncertainty",
                "",
                "This means there's more risk, which affects our lending decision.",
            ])
        else:
            lines.extend([
                "**Risk Score: High Risk** 🔴",
                "",
                "Your financial profile shows significant challenges:",
                "- Low credit score reflecting payment issues",
                "- High debt relative to income",
                "- Unstable employment history",
                "- Multiple financial risk factors",
                "",
                "This means lending to you carries substantial risk of non-repayment.",
            ])

        return "\n".join(lines)

    @staticmethod
    def generate_detailed_factors_analysis(result: Dict[str, Any]) -> str:
        """Generate detailed but understandable analysis of decision factors"""
        lines = [
            "## 📊 DETAILED BREAKDOWN OF EACH FACTOR",
            "",
            "### What We Looked At",
            "",
            "We evaluated 8 major financial indicators. Here's what each one means and why it matters:",
            "",
        ]

        factors_explanations = {
            "Credit Score": {
                "description": "Your payment history and borrowing behavior",
                "why_matters": "Shows if you've repaid past loans on time. Banks trust people with good payment history.",
                "good_sign": "Score above 700 (excellent)",
                "concern": "Score below 620 (we worry about repayment)",
            },
            "Debt-to-Income Ratio": {
                "description": "How much of your income goes to existing debts",
                "why_matters": "If you're already spending too much on debt payments, you may struggle with a new loan.",
                "good_sign": "Below 36% (conservative lending standard)",
                "concern": "Above 50% (not enough income left for new loan)",
            },
            "Employment Duration": {
                "description": "How long you've been working at your current job",
                "why_matters": "Stable employment means stable income to repay the loan.",
                "good_sign": "More than 2 years at current job (shows stability)",
                "concern": "Less than 6 months (we worry about job loss)",
            },
            "Loan-to-Income Ratio": {
                "description": "Loan amount compared to your yearly income",
                "why_matters": "Shows if the loan size is reasonable relative to what you earn.",
                "good_sign": "Under 20% (loan is small relative to income)",
                "concern": "Over 50% (loan is very large for your income)",
            },
            "Annual Income": {
                "description": "Your total yearly earnings",
                "why_matters": "Higher income gives you more money for loan payments.",
                "good_sign": "Stable and consistently documented income",
                "concern": "Very low income makes loan repayment difficult",
            },
            "Age": {
                "description": "Your age at time of application",
                "why_matters": "Age helps estimate how long you'll be employed and able to pay.",
                "good_sign": "25-55 years old (traditional lending age range)",
                "concern": "Very young or very close to retirement",
            },
            "Requested Loan Amount": {
                "description": "How much money you're asking to borrow",
                "why_matters": "Larger loans are riskier. We prefer reasonable amounts we can afford to lose.",
                "good_sign": "Conservative amount relative to income",
                "concern": "Loan amount seems excessive for your income",
            },
            "Loan Tenure": {
                "description": "How long you have to repay the loan (months)",
                "why_matters": "Longer repayment periods mean lower monthly payments, but more interest overall.",
                "good_sign": "3-7 year terms are standard",
                "concern": "Very short terms = high monthly payments",
            },
        }

        for factor_name, explanation in factors_explanations.items():
            lines.extend([
                f"### 🔹 {factor_name}",
                "",
                f"**What it is:** {explanation['description']}",
                "",
                f"**Why it matters:** {explanation['why_matters']}",
                "",
                f"✅ **Good sign:** {explanation['good_sign']}",
                "",
                f"⚠️ **Concern:** {explanation['concern']}",
                "",
            ])

        return "\n".join(lines)

    @staticmethod
    def generate_improvement_recommendations(result: Dict[str, Any]) -> str:
        """Generate personalized recommendations for improvement"""
        classification = result.get("classification", "")
        risk_score = result.get("risk_score", 0)

        lines = [
            "## 💡 HOW TO IMPROVE YOUR CHANCES NEXT TIME",
            "",
        ]

        if classification == "Approved":
            lines.extend([
                "### ✅ You Were Approved!",
                "",
                "Great! Here's what to do next:",
                "",
                "1. **Review the Loan Agreement**",
                "   - Read all terms carefully before signing",
                "   - Make sure you understand the interest rate and monthly payment",
                "",
                "2. **Plan Your Payments**",
                "   - Set up automatic payments to never miss a payment",
                "   - Missing payments will damage your credit",
                "",
                "3. **Maintain Good Financial Health**",
                "   - Keep paying all bills on time",
                "   - Don't take on more debt while repaying this loan",
                "   - Keep your job stable if possible",
                "",
                "4. **Track Your Progress**",
                "   - Monitor your loan account regularly",
                "   - Check your credit score improvement as you make payments",
                "",
            ])
        else:
            lines.extend([
                "### ❌ Not Approved Yet?",
                "",
                "Don't worry - here's how to improve and reapply successfully:",
                "",
                "#### If Your Credit Score Was Low:",
                "- ✅ Pay ALL bills on time (this is most important!)",
                "- ✅ Pay down credit card balances to under 30% of limit",
                "- ✅ Don't close old credit accounts (they help your history)",
                "- ⏱️ Wait at least 3-6 months for improvements to show",
                "",
                "#### If Your Debt Was Too High:",
                "- ✅ Focus on paying down existing debts",
                "- ✅ Avoid taking on new credit (credit cards, loans, etc.)",
                "- ✅ Create a budget to reduce expenses",
                "- ⏱️ Even 10-15% debt reduction can help significantly",
                "",
                "#### If Your Income Was Considered Low:",
                "- ✅ Pursue a raise at your current job",
                "- ✅ Add a second income source or side job",
                "- ✅ Include spouse's income if married and filing taxes jointly",
                "- ✅ Document all income sources properly",
                "",
                "#### If Your Employment Was Unstable:",
                "- ✅ Stay at your current job for at least 2 years",
                "- ✅ Build a consistent work history",
                "- ✅ Document length of employment clearly",
                "",
                "#### General Tips for Next Time:",
                "- ✅ Request a smaller loan amount",
                "- ✅ Extend the loan tenure to lower monthly payments",
                "- ✅ Reapply in 6-12 months with improved metrics",
                "- ✅ Consider getting a co-signer with better credit",
                "",
                f"**Estimated Timeline:** With focused effort, you could reapply in 6-12 months.",
                "",
            ])

        return "\n".join(lines)

    @staticmethod
    def generate_glossary_section() -> str:
        """Generate a glossary for technical terms used in the report"""
        lines = [
            "## 📚 GLOSSARY - UNDERSTANDING THE TERMS",
            "",
            "Confused by financial terminology? Here are simple explanations:",
            "",
        ]

        for term, explanation in EnhancedReportGenerator.GLOSSARY.items():
            formatted_term = term.replace("_", " ").title()
            lines.extend([
                f"### {formatted_term}",
                f"{explanation}",
                "",
            ])

        return "\n".join(lines)

    @staticmethod
    def generate_faq_section() -> str:
        """Generate frequently asked questions"""
        lines = [
            "## ❓ FREQUENTLY ASKED QUESTIONS",
            "",
        ]

        faqs = [
            {
                "question": "How was my risk score calculated?",
                "answer": "We analyzed 8 financial factors: credit score, debt level, employment stability, "
                         "income, age, loan amount, and loan tenure. Each factor was weighted based on how "
                         "important it is for predicting loan repayment success. The final score ranges from "
                         "0 (very safe) to 100 (very risky)."
            },
            {
                "question": "Can I improve my score and reapply?",
                "answer": "Absolutely! Most applicants can improve their score by paying down debts, "
                         "improving their credit score, or finding more stable employment. We recommend "
                         "reapplying after 6-12 months of showing improvement."
            },
            {
                "question": "Why does my credit score matter so much?",
                "answer": "Credit score is the best predictor we have of whether someone will repay a loan. "
                         "It reflects your entire payment history - whether you've paid bills on time, how much "
                         "debt you carry, and how responsible you've been with credit."
            },
            {
                "question": "What if I disagree with the decision?",
                "answer": "You can appeal the decision by contacting our loan department with additional "
                         "documentation. We'll have a human specialist review your case and additional information "
                         "you can provide."
            },
            {
                "question": "How long will my loan take to process?",
                "answer": "If approved: 3-5 business days for funding. If rejected: You can reapply after "
                         "improving your financial situation (typically 6-12 months)."
            },
            {
                "question": "Is this decision final?",
                "answer": "Our automated decision is based on financial metrics. For Approved decisions, it's "
                         "final pending documentation review. For Rejected decisions, you can appeal or reapply "
                         "with improved financials."
            },
        ]

        for faq in faqs:
            lines.extend([
                f"### Q: {faq['question']}",
                f"**A:** {faq['answer']}",
                "",
            ])

        return "\n".join(lines)

    @staticmethod
    def generate_process_explanation() -> str:
        """Generate explanation of how the loan approval process works"""
        lines = [
            "## 🔄 HOW THE LOAN APPROVAL PROCESS WORKS",
            "",
            "### Step 1: Application Submission",
            "You provide us with your financial information (income, debts, credit score, employment, etc.)",
            "",
            "### Step 2: Automated Analysis",
            "Our AI system analyzes your information against 8 key financial factors:",
            "- Your credit history and score",
            "- Current debt obligations",
            "- Income stability and amount",
            "- Employment duration",
            "- The loan size relative to your income",
            "- Your age and loan tenure",
            "",
            "### Step 3: Risk Scoring",
            "The system calculates an overall risk score (0-100):",
            "- **0-25:** Very Low Risk → Usually Approved",
            "- **25-50:** Low-Moderate Risk → Usually Approved",
            "- **50-75:** Moderate-High Risk → May be Approved or Rejected",
            "- **75-100:** High Risk → Usually Rejected",
            "",
            "### Step 4: Decision",
            "Based on your risk score and our lending criteria, we either:",
            "- ✅ **Approve** your loan (and determine the amount)",
            "- ❌ **Reject** your loan (you can reapply later)",
            "- ⏳ **Request Additional Review** (for borderline cases)",
            "",
            "### Step 5: Communication",
            "We send you this detailed report explaining our decision and next steps.",
            "",
        ]

        return "\n".join(lines)

    @staticmethod
    def generate_complete_enhanced_report(result: Dict[str, Any],
                                         applicant_data: Optional[Dict] = None) -> str:
        """Generate a complete, comprehensive, easy-to-understand report"""

        report_parts = [
            "# 📊 COMPREHENSIVE LOAN EVALUATION REPORT",
            "",
            f"**Generated:** {datetime.now().strftime('%B %d, %Y at %I:%M %p')}",
            "",
            "---",
            "",
        ]

        # Add each section
        report_parts.append(EnhancedReportGenerator.generate_executive_summary(result, applicant_data))
        report_parts.append("---\n")

        report_parts.append(EnhancedReportGenerator.generate_simple_explanation(result))
        report_parts.append("---\n")

        report_parts.append(EnhancedReportGenerator.generate_detailed_factors_analysis(result))
        report_parts.append("---\n")

        report_parts.append(EnhancedReportGenerator.generate_improvement_recommendations(result))
        report_parts.append("---\n")

        report_parts.append(EnhancedReportGenerator.generate_process_explanation())
        report_parts.append("---\n")

        report_parts.append(EnhancedReportGenerator.generate_faq_section())
        report_parts.append("---\n")

        report_parts.append(EnhancedReportGenerator.generate_glossary_section())
        report_parts.append("---\n")

        # Footer
        report_parts.extend([
            "## 📝 REPORT FOOTER",
            "",
            "### Important Information",
            "",
            "This report represents an automated AI-driven analysis of your loan application. "
            "While our system is highly accurate, all decisions are subject to manual review and final approval.",
            "",
            "Your financial information has been processed securely and will not be shared with third parties "
            "without your consent.",
            "",
            "### Next Steps",
            "",
            "- **If Approved:** Check your email for loan agreement and funding instructions",
            "- **If Rejected:** Review the improvement recommendations and consider reapplying in 6-12 months",
            "- **Questions?** Contact our support team at support@loanapproval.com or call 1-800-LOANS-NOW",
            "",
            f"**Report Generated:** {datetime.now().isoformat()}",
            f"**System:** Claude AI Loan Approval System v1.0",
        ])

        return "\n".join(report_parts)
