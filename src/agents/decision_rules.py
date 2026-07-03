"""Decision Rules Engine - Explicit rules for loan approval/rejection"""

from typing import Tuple, List, Dict, Any
from src.logger import get_logger

logger = get_logger(__name__)


class RulesConfig:
    """Centralized rules configuration"""

    CREDIT_SCORE = {
        "excellent": {"min": 750, "max": 850, "weight": 0.0},
        "very_good": {"min": 700, "max": 749, "weight": 0.05},
        "good": {"min": 660, "max": 699, "weight": 0.15},
        "fair": {"min": 640, "max": 659, "weight": 0.30},
        "poor": {"min": 620, "max": 639, "weight": 0.50},
        "very_poor": {"min": 300, "max": 619, "weight": 1.0},
    }

    DTI = {
        "excellent": {"min": 0.0, "max": 0.20, "weight": 0.0},
        "good": {"min": 0.20, "max": 0.36, "weight": 0.05},
        "acceptable": {"min": 0.36, "max": 0.43, "weight": 0.15},
        "moderate": {"min": 0.43, "max": 0.60, "weight": 0.40},
        "high": {"min": 0.60, "max": 0.80, "weight": 0.70},
        "critical": {"min": 0.80, "max": 9.99, "weight": 1.0},
    }

    EMPLOYMENT_DURATION = {
        "stable": {"min": 24, "max": 999, "weight": 0.0},
        "acceptable": {"min": 12, "max": 23, "weight": 0.10},
        "emerging": {"min": 6, "max": 11, "weight": 0.30},
        "insufficient": {"min": 0, "max": 5, "weight": 0.70},
    }

    LTI = {
        "excellent": {"min": 0.0, "max": 1.0, "weight": 0.0},
        "good": {"min": 1.0, "max": 2.0, "weight": 0.05},
        "acceptable": {"min": 2.0, "max": 3.0, "weight": 0.15},
        "moderate": {"min": 3.0, "max": 4.0, "weight": 0.30},
        "high": {"min": 4.0, "max": 5.0, "weight": 0.50},
        "excessive": {"min": 5.0, "max": 999, "weight": 1.0},
    }

    INCOME = {
        "excellent": {"min": 150000, "weight": 0.0},
        "very_good": {"min": 100000, "max": 149999, "weight": 0.05},
        "good": {"min": 75000, "max": 99999, "weight": 0.10},
        "acceptable": {"min": 50000, "max": 74999, "weight": 0.15},
        "moderate": {"min": 35000, "max": 49999, "weight": 0.25},
        "low": {"min": 20000, "max": 34999, "weight": 0.40},
        "very_low": {"min": 10000, "max": 19999, "weight": 0.60},
    }

    AGE = {
        "ideal": {"min": 30, "max": 55, "weight": 0.0},
        "acceptable": {"min": 25, "max": 65, "weight": 0.10},
        "marginal_young": {"min": 20, "max": 24, "weight": 0.30},
        "marginal_old": {"min": 66, "max": 75, "weight": 0.20},
        "problematic": {"min": 18, "max": 19, "weight": 0.50},
        "problematic_very_old": {"min": 76, "max": 100, "weight": 0.40},
    }

    LOAN_AMOUNT = {
        "conservative": {"min": 0, "max": 25000, "weight": 0.0},
        "moderate": {"min": 25001, "max": 50000, "weight": 0.05},
        "standard": {"min": 50001, "max": 100000, "weight": 0.10},
        "high": {"min": 100001, "max": 250000, "weight": 0.20},
        "very_high": {"min": 250001, "max": 1000000, "weight": 0.40},
    }

    TENURE = {
        "short": {"min": 1, "max": 24, "weight": 0.10},
        "standard": {"min": 24, "max": 60, "weight": 0.0},
        "extended": {"min": 60, "max": 120, "weight": 0.05},
        "very_extended": {"min": 120, "max": 360, "weight": 0.15},
    }


class DecisionRulesEngine:
    """Loan approval decision engine with explicit rules"""

    @staticmethod
    def _evaluate_parameter(
        value: float, rules: Dict[str, Any], param_name: str, format_str: str = "{}"
    ) -> Tuple[str, float, str]:
        """Generic parameter evaluation against rule ranges"""
        for category, rule_range in rules.items():
            min_val = rule_range.get("min", 0)
            max_val = rule_range.get("max", float("inf"))

            if min_val <= value <= max_val:
                max_display = (
                    format_str.format(max_val)
                    if max_val != float("inf")
                    else "unlimited"
                )
                min_display = format_str.format(min_val)
                reason = (
                    f"{param_name} {format_str.format(value)} in {category} "
                    f"range [{min_display}-{max_display}]"
                )
                return category, rule_range["weight"], reason

        return "unknown", 0.5, f"{param_name} outside standard ranges"

    @staticmethod
    def evaluate_credit_score(credit_score: float) -> Tuple[str, float, str]:
        """Evaluate credit score against rules"""
        return DecisionRulesEngine._evaluate_parameter(
            credit_score, RulesConfig.CREDIT_SCORE, "Credit score", "{:.0f}"
        )

    @staticmethod
    def evaluate_dti(existing_liabilities: float, annual_income: float) -> Tuple[str, float, str]:
        """Evaluate Debt-to-Income ratio against rules"""
        if annual_income <= 0:
            return "invalid_income", 1.0, "Annual income is zero or negative"

        dti = (existing_liabilities * 12) / annual_income
        return DecisionRulesEngine._evaluate_parameter(
            dti, RulesConfig.DTI, "DTI ratio", "{:.2%}"
        )

    @staticmethod
    def evaluate_employment_duration(months: int) -> Tuple[str, float, str]:
        """Evaluate employment duration against rules"""
        return DecisionRulesEngine._evaluate_parameter(
            months, RulesConfig.EMPLOYMENT_DURATION, "Employment duration", "{:.0f} months"
        )

    @staticmethod
    def evaluate_lti(loan_amount: float, annual_income: float) -> Tuple[str, float, str]:
        """Evaluate Loan-to-Income ratio against rules"""
        if annual_income <= 0:
            return "invalid_income", 1.0, "Annual income is zero or negative"

        lti = loan_amount / annual_income
        return DecisionRulesEngine._evaluate_parameter(
            lti, RulesConfig.LTI, "LTI ratio", "{:.2f}x"
        )

    @staticmethod
    def evaluate_income(annual_income: float) -> Tuple[str, float, str]:
        """Evaluate annual income against rules"""
        return DecisionRulesEngine._evaluate_parameter(
            annual_income, RulesConfig.INCOME, "Annual income", "${:,.0f}"
        )

    @staticmethod
    def evaluate_age(age: int) -> Tuple[str, float, str]:
        """Evaluate applicant age against rules"""
        return DecisionRulesEngine._evaluate_parameter(
            age, RulesConfig.AGE, "Age", "{:.0f}"
        )

    @staticmethod
    def evaluate_loan_amount(loan_amount: float) -> Tuple[str, float, str]:
        """Evaluate loan amount against rules"""
        return DecisionRulesEngine._evaluate_parameter(
            loan_amount, RulesConfig.LOAN_AMOUNT, "Loan amount", "${:,.0f}"
        )

    @staticmethod
    def evaluate_tenure(tenure_months: int) -> Tuple[str, float, str]:
        """Evaluate loan tenure against rules"""
        return DecisionRulesEngine._evaluate_parameter(
            tenure_months, RulesConfig.TENURE, "Tenure", "{:.0f} months"
        )

    @staticmethod
    def calculate_risk_score(
        credit_score: float,
        annual_income: float,
        existing_liabilities: float,
        loan_amount: float,
        employment_duration: int,
        tenure_months: int,
        age: int,
    ) -> Dict:
        """Calculate overall risk score by evaluating all parameters"""
        evaluations = {
            "credit_score": DecisionRulesEngine.evaluate_credit_score(credit_score),
            "dti": DecisionRulesEngine.evaluate_dti(existing_liabilities, annual_income),
            "employment": DecisionRulesEngine.evaluate_employment_duration(employment_duration),
            "lti": DecisionRulesEngine.evaluate_lti(loan_amount, annual_income),
            "income": DecisionRulesEngine.evaluate_income(annual_income),
            "age": DecisionRulesEngine.evaluate_age(age),
            "loan_amount": DecisionRulesEngine.evaluate_loan_amount(loan_amount),
            "tenure": DecisionRulesEngine.evaluate_tenure(tenure_months),
        }

        total_weight = sum(cat[1] for cat in evaluations.values())
        average_weight = total_weight / len(evaluations)
        risk_score = int(average_weight * 100)
        risk_score = max(0, min(100, risk_score))

        detail_factors = [
            f"[{name.upper()}] {cat}: {reason}"
            for name, (cat, _, reason) in evaluations.items()
        ]

        hard_rejection_factors = DecisionRulesEngine._check_hard_rejections(
            credit_score, evaluations
        )

        return {
            "risk_score": risk_score,
            "evaluations": evaluations,
            "detail_factors": detail_factors,
            "average_weight": average_weight,
            "hard_rejection_factors": hard_rejection_factors,
        }

    @staticmethod
    def _check_hard_rejections(
        credit_score: float, evaluations: Dict
    ) -> List[str]:
        """Check for hard rejection criteria"""
        factors = []

        if credit_score < 620:
            factors.append("Credit score < 620 (poor)")
        if evaluations["dti"][0] == "critical":
            factors.append("DTI ratio ≥ 60%")
        if evaluations["dti"][0] == "high":
            factors.append("DTI ratio ≥ 50%")
        if evaluations["employment"][0] == "insufficient":
            factors.append("Employment duration < 6 months")
        if evaluations["lti"][0] == "excessive":
            factors.append("LTI ratio > 5.0x")

        return factors

    @staticmethod
    def make_decision(
        risk_score: float, confidence: float, hard_rejection_factors: List[str] = None, evaluations: Dict = None
    ) -> Tuple[str, str]:
        """Make final LLM-powered decision based on risk score and evaluation details.
        All decisions are made by Claude - no manual review escalation."""
        if hard_rejection_factors is None:
            hard_rejection_factors = []

        # Hard rejection criteria - automatic rejection
        if hard_rejection_factors:
            reasons = "\n• ".join(hard_rejection_factors)
            return "Rejected", f"Application rejected due to the following critical factors:\n• {reasons}"

        if risk_score >= 85:
            return "Rejected", f"Application rejected: Risk score is critically high at {risk_score}/100, exceeding maximum acceptable threshold of 85."

        if risk_score >= 75:
            return "Rejected", f"Application rejected: Risk score of {risk_score}/100 is too high for approval. The applicant profile indicates significant financial or credit risk."

        # Poor/very poor credit: Rejected
        if evaluations:
            credit_eval = evaluations.get("credit_score", ("unknown", 0))
            if credit_eval[0] in ["very_poor"]:
                credit_score_val = credit_eval[2] if len(credit_eval) > 2 else "below 600"
                return "Rejected", f"Application rejected: {credit_score_val}. A credit score below 620 does not meet minimum lending standards. Applicants should work on improving credit history before reapplying."

            if credit_eval[0] == "poor":
                credit_score_val = credit_eval[2] if len(credit_eval) > 2 else "620-639"
                return "Rejected", f"Application rejected: {credit_score_val}. The credit score is in the poor range (620-639), indicating payment history or high credit utilization concerns. Please improve your credit profile and reapply."

        # Low risk: approve
        if risk_score < 25:
            return "Approved", f"✓ Application approved! Your risk score of {risk_score}/100 is very low, indicating strong financial stability and creditworthiness. Congratulations!"

        # Moderate risk: approve if confidence is adequate
        if risk_score < 50 and confidence >= 0.65:
            return "Approved", f"✓ Application approved! Despite moderate risk factors ({risk_score}/100), your profile demonstrates sufficient financial strength and stability for loan approval."

        # Higher risk: still approve if LLM confidence is high
        if risk_score < 70 and confidence >= 0.75:
            return "Approved", f"✓ Application approved! Although your risk profile shows elevated factors ({risk_score}/100), the overall assessment with high confidence ({confidence:.0%}) supports approval."

        # Default: reject if risk is too high
        return "Rejected", f"Application rejected: Risk score of {risk_score}/100 exceeds the approval threshold. Multiple risk factors in your profile (credit, income, debt levels, or employment) require improvement before reapplication."


def generate_decision_factors(evaluations: Dict, risk_score: int) -> List[str]:
    """Generate human-readable decision factors from evaluations"""
    factors = []

    credit_weight = evaluations.get("credit_score", ("unknown", 0.5))[1]
    dti_weight = evaluations.get("dti", ("unknown", 0.5))[1]
    emp_weight = evaluations.get("employment", ("unknown", 0.5))[1]
    lti_weight = evaluations.get("lti", ("unknown", 0.5))[1]

    if credit_weight <= 0.1:
        factors.append("Excellent credit history and score")
    if dti_weight <= 0.1:
        factors.append("Healthy debt-to-income ratio")
    if emp_weight <= 0.1:
        factors.append("Stable long-term employment")
    if lti_weight <= 0.1:
        factors.append("Conservative loan-to-income ratio")

    if credit_weight >= 0.5:
        factors.append(f"Credit score risk: {evaluations['credit_score'][0]}")
    if dti_weight >= 0.4:
        factors.append(f"DTI risk: {evaluations['dti'][0]}")
    if emp_weight >= 0.3:
        factors.append(f"Employment stability risk: {evaluations['employment'][0]}")
    if lti_weight >= 0.5:
        factors.append(f"Loan-to-income risk: {evaluations['lti'][0]}")

    if risk_score >= 75:
        factors.append("Overall risk profile: HIGH")
    elif risk_score >= 50:
        factors.append("Overall risk profile: MODERATE")
    elif risk_score >= 25:
        factors.append("Overall risk profile: LOW-MODERATE")
    else:
        factors.append("Overall risk profile: LOW")

    return factors if factors else ["Analysis inconclusive - manual review recommended"]
