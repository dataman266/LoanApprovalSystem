# 📋 Loan Approval Decision Rules Engine

## Overview

The system now uses **explicit, rule-based decision logic** to evaluate every parameter of a loan application and make deterministic Approved/Rejected/Manual Review decisions.

---

## ⚙️ Rule Categories & Thresholds

### 1️⃣ **CREDIT SCORE RULES** (Excellent to Very Poor)

The credit score determines an applicant's historical ability to manage credit.

| Category | Score Range | Weight | Risk Level | Notes |
|----------|-------------|--------|-----------|-------|
| **Excellent** | 750-850 | 0.0 | Very Low | Prime borrower, approved-eligible |
| **Very Good** | 700-749 | 0.05 | Low | Strong credit history |
| **Good** | 660-699 | 0.15 | Low-Moderate | Acceptable credit profile |
| **Fair** | 620-659 | 0.30 | Moderate | Some credit concerns |
| **Poor** | 580-619 | 0.50 | High | Significant credit issues |
| **Very Poor** | 300-579 | 1.0 | Very High | Rejection candidate |

**Decision Impact:**
- ✅ **750+**: Positive factor for approval
- ⚠️ **620-749**: Manageable with good other factors
- ❌ **Below 620**: High-risk indicator

---

### 2️⃣ **DEBT-TO-INCOME RATIO (DTI)**

DTI = (Monthly Liabilities × 12) / Annual Income

This ratio shows what percentage of income is already committed to debt.

| Category | DTI Range | Weight | Risk Level | Regulatory Status |
|----------|-----------|--------|-----------|------------------|
| **Excellent** | 0-20% | 0.0 | Very Low | Gold standard |
| **Good** | 20-36% | 0.05 | Low | Regulatory preference |
| **Acceptable** | 36-43% | 0.15 | Low-Moderate | At regulatory limit |
| **Moderate** | 43-60% | 0.40 | Moderate | Above safe threshold |
| **High** | 60-80% | 0.70 | High | Risky, unstable |
| **Critical** | 80%+ | 1.0 | Very High | **REJECTION** |

**Decision Impact:**
- ✅ **Below 43%**: Generally approvable
- ⚠️ **43-60%**: Requires other strong factors
- ❌ **60%+**: Rejection indicator

**Example Calculations:**
```
Alice: $200/month liabilities ÷ ($150,000/12) = 1.6% DTI → Excellent ✅
Bob: $500/month liabilities ÷ ($75,000/12) = 8% DTI → Excellent ✅
Charlie: $2,500/month liabilities ÷ ($35,000/12) = 85.7% DTI → CRITICAL ❌
```

---

### 3️⃣ **EMPLOYMENT DURATION**

Stability of current employment and income source.

| Category | Duration | Weight | Risk Level | Notes |
|----------|----------|--------|-----------|-------|
| **Stable** | 24+ months | 0.0 | Very Low | Proven income stability |
| **Acceptable** | 12-23 months | 0.10 | Low | Reasonable tenure |
| **Emerging** | 6-11 months | 0.30 | Moderate | Relatively new job |
| **Insufficient** | 0-5 months | 0.70 | High | Too new, income unproven |

**Decision Impact:**
- ✅ **24+ months**: Approved factor
- ⚠️ **6-23 months**: Acceptable but adds risk
- ❌ **Less than 6 months**: Rejection factor

---

### 4️⃣ **LOAN-TO-INCOME RATIO (LTI)**

LTI = Loan Amount / Annual Income

Shows what multiple of annual income the loan represents.

| Category | LTI Range | Weight | Risk Level | Notes |
|----------|-----------|--------|-----------|-------|
| **Excellent** | 0-1.0x | 0.0 | Very Low | Conservative loan |
| **Good** | 1.0-2.0x | 0.05 | Low | Reasonable leverage |
| **Acceptable** | 2.0-3.0x | 0.15 | Low-Moderate | Moderate leverage |
| **Moderate** | 3.0-4.0x | 0.30 | Moderate | Higher risk |
| **High** | 4.0-5.0x | 0.50 | High | Very high leverage |
| **Excessive** | 5.0x+ | 1.0 | Very High | **REJECTION** |

**Decision Impact:**
- ✅ **Below 2.0x**: Strong approval factor
- ⚠️ **2.0-4.0x**: Depends on other factors
- ❌ **5.0x+**: Rejection indicator

**Example Calculations:**
```
Alice: $30,000 ÷ $150,000 = 0.2x LTI → Excellent ✅
Bob: $50,000 ÷ $75,000 = 0.67x LTI → Excellent ✅
Charlie: $50,000 ÷ $35,000 = 1.43x LTI → Good (only positive factor)
```

---

### 5️⃣ **ANNUAL INCOME**

Gross annual income determines borrowing capacity.

| Category | Income | Weight | Risk Level |
|----------|--------|--------|-----------|
| **Excellent** | $150,000+ | 0.0 | Very Low |
| **Very Good** | $100,000-$149,999 | 0.05 | Low |
| **Good** | $75,000-$99,999 | 0.10 | Low |
| **Acceptable** | $50,000-$74,999 | 0.15 | Low-Moderate |
| **Moderate** | $35,000-$49,999 | 0.25 | Moderate |
| **Low** | $20,000-$34,999 | 0.40 | High |
| **Very Low** | $10,000-$19,999 | 0.60 | Very High |

---

### 6️⃣ **AGE RULES**

Age affects loan repayment timeline and risk profile.

| Category | Age Range | Weight | Notes |
|----------|-----------|--------|-------|
| **Ideal** | 30-55 | 0.0 | Prime lending years |
| **Acceptable** | 25-65 | 0.10 | Reasonable range |
| **Marginal (Young)** | 20-24 | 0.30 | Near minimum age |
| **Marginal (Old)** | 66-75 | 0.20 | Approaching retirement |
| **Problematic (Young)** | 18-19 | 0.50 | Very new to credit |
| **Problematic (Old)** | 76-100 | 0.40 | Risk of income loss |

---

### 7️⃣ **LOAN AMOUNT**

Absolute loan size affects default risk.

| Category | Amount | Weight |
|----------|--------|--------|
| **Conservative** | $0-$25,000 | 0.0 |
| **Moderate** | $25,001-$50,000 | 0.05 |
| **Standard** | $50,001-$100,000 | 0.10 |
| **High** | $100,001-$250,000 | 0.20 |
| **Very High** | $250,001-$1,000,000 | 0.40 |

---

### 8️⃣ **LOAN TENURE (Repayment Period)**

Longer tenures spread payments but extend commitment.

| Category | Tenure | Weight | Notes |
|----------|--------|--------|-------|
| **Short** | 1-24 months | 0.10 | Higher monthly payment |
| **Standard** | 24-60 months | 0.0 | Typical/optimal |
| **Extended** | 60-120 months | 0.05 | Manageable payments |
| **Very Extended** | 120-360 months | 0.15 | Long commitment |

---

## 🎯 DECISION LOGIC

### **Risk Score Calculation**

```
Risk Score (0-100) = Average of all parameter weights × 100

Where each weight is determined by rule category match
```

**Example:**
```
Alice (40, employed 120mo, $150k, credit 800, $30k loan):
- Credit: 800 (Excellent) → 0.0
- DTI: 1.6% (Excellent) → 0.0
- Employment: 120mo (Stable) → 0.0
- LTI: 0.2x (Excellent) → 0.0
- Income: $150k (Excellent) → 0.0
- Age: 40 (Ideal) → 0.0
- Tenure: 36mo (Standard) → 0.0

Average Weight = 0 / 7 = 0.0 = Risk Score: 0/100 ✅ APPROVED
```

```
Charlie (28, employed 3mo, $35k, credit 580, $50k loan):
- Credit: 580 (Very Poor) → 1.0
- DTI: 85.7% (Critical) → 1.0
- Employment: 3mo (Insufficient) → 0.7
- LTI: 1.43x (Good) → 0.05
- Income: $35k (Low) → 0.4
- Age: 28 (Acceptable) → 0.1
- Tenure: 60mo (Standard) → 0.0

Average Weight = 3.25 / 7 = 0.464 = Risk Score: 46/100 ⚠️
BUT DTI > 60% + Credit < 620 = HARD REJECTION ❌
```

---

## ✅ DECISION CLASSIFICATIONS

### **APPROVED**
**Criteria:**
- Risk Score < 30 AND Confidence ≥ 80%
- OR Risk Score < 25 (regardless of confidence)

**Example:** Alice (Risk: 0, Confidence: 85%) → **APPROVED** ✅

### **REJECTED**
**Criteria:**
- Risk Score ≥ 75 (HARD RULE)
- OR Risk Score ≥ 85 (CRITICAL)
- OR DTI ≥ 60%
- OR Credit Score < 580
- OR Employment < 3 months

**Example:** Charlie (Risk: 46, DTI: 85.7%) → **REJECTED** ❌

### **REQUIRES MANUAL REVIEW**
**Criteria:**
- Risk Score 30-74 AND Confidence ≥ 70%
- OR Confidence < 60% (insufficient certainty)
- OR mixed positive/negative factors

**Example:** Bob (Risk: 50, Confidence: 75%) → **REQUIRES MANUAL REVIEW** ⏳

---

## 📊 EXAMPLE DECISIONS

### **Test Case 1: Alice Johnson (Excellent Profile)**

**Input:**
```
Age: 40
Annual Income: $150,000
Credit Score: 800
Employment: 120 months (10 years)
Monthly Liabilities: $200
Loan Amount: $30,000
Tenure: 36 months
```

**Rule Evaluations:**
```
✅ Credit Score (800): Excellent [750-850] → Weight 0.0
✅ DTI (1.6%): Excellent [0-20%] → Weight 0.0
✅ Employment (120mo): Stable [24+] → Weight 0.0
✅ LTI (0.2x): Excellent [0-1.0x] → Weight 0.0
✅ Income ($150k): Excellent [150k+] → Weight 0.0
✅ Age (40): Ideal [30-55] → Weight 0.0
✅ Tenure (36mo): Standard [24-60] → Weight 0.0

Risk Score: 0/100 (Average: 0%)
Confidence: 85%
```

**Decision:** ✅ **APPROVED**
- Risk score is 0 (perfect profile)
- All parameters in excellent/ideal range
- High confidence in decision

---

### **Test Case 2: Bob Wilson (Good Profile)**

**Input:**
```
Age: 35
Annual Income: $75,000
Credit Score: 720
Employment: 24 months (2 years)
Monthly Liabilities: $500
Loan Amount: $50,000
Tenure: 60 months
```

**Rule Evaluations:**
```
✅ Credit Score (720): Very Good [700-749] → Weight 0.05
✅ DTI (8%): Excellent [0-20%] → Weight 0.0
✅ Employment (24mo): Stable [24+] → Weight 0.0
✅ LTI (0.67x): Excellent [0-1.0x] → Weight 0.0
✅ Income ($75k): Good [75-99k] → Weight 0.10
✅ Age (35): Ideal [30-55] → Weight 0.0
✅ Tenure (60mo): Standard [24-60] → Weight 0.0

Risk Score: 2/100 (Average: 2.1%)
Confidence: 80%
```

**Decision:** ✅ **APPROVED**
- Very low risk score (2/100)
- High confidence (80%)
- Strong income stability with reasonable DTI

---

### **Test Case 3: Charlie Brown (High Risk)**

**Input:**
```
Age: 28
Annual Income: $35,000
Credit Score: 580
Employment: 3 months
Monthly Liabilities: $2,500
Loan Amount: $50,000
Tenure: 60 months
```

**Rule Evaluations:**
```
❌ Credit Score (580): Very Poor [300-579] → Weight 1.0 (REJECTION)
❌ DTI (85.7%): Critical [80%+] → Weight 1.0 (HARD RULE)
❌ Employment (3mo): Insufficient [0-5mo] → Weight 0.7
⚠️ LTI (1.43x): Good [1.0-2.0x] → Weight 0.05 (ONLY POSITIVE)
⚠️ Income ($35k): Low [35-49k] → Weight 0.4
✅ Age (28): Acceptable [25-65] → Weight 0.10
✅ Tenure (60mo): Standard [24-60] → Weight 0.0

Risk Score: 46/100 (Average: 46%)
Confidence: 45%
```

**Decision:** ❌ **REJECTED**
- Hard rejection rules triggered:
  - DTI ≥ 60% (85.7%)
  - Credit Score < 580 (exactly 580)
  - Employment < 6 months (3 months)
  - Low confidence (45%)

**Explanation:**
```
"Risk score critically high (46/100) with multiple rejection factors:
- Debt-to-income ratio of 85.7% is unsustainable
- Credit score of 580 indicates significant credit issues
- Employment duration of only 3 months is too new to verify income stability"
```

---

## 🔑 KEY DECISION FACTORS

The system generates human-readable factors for each decision:

**Positive Factors:**
- "Excellent credit history and score"
- "Healthy debt-to-income ratio"
- "Stable long-term employment"
- "Conservative loan-to-income ratio"

**Risk Factors:**
- "Credit score risk: [category]"
- "DTI risk: [category]"
- "Employment stability risk: [category]"
- "Loan-to-income risk: [category]"

**Overall Risk Profile:**
- "LOW" (Risk Score: 0-25)
- "LOW-MODERATE" (Risk Score: 25-50)
- "MODERATE" (Risk Score: 50-75)
- "HIGH" (Risk Score: 75-100)

---

## 📈 CONFIDENCE LEVELS

Confidence represents how certain the system is in the decision:

- **85-100%**: Very Confident → Safe to approve/reject
- **70-85%**: Confident → Reasonable decision
- **60-70%**: Moderately Confident → Some ambiguity
- **Below 60%**: Low Confidence → Manual review needed

---

## 🛡️ HARD REJECTION RULES

These rules **cannot be overridden** by other positive factors:

1. **Credit Score < 580** → REJECTED
2. **DTI ≥ 60%** → REJECTED
3. **Risk Score ≥ 75** → REJECTED
4. **Risk Score ≥ 85** → REJECTED (CRITICAL)
5. **Employment < 3 months** → REJECTED
6. **LTI > 5.0x** → REJECTED

---

## 🔄 Testing the Rules

**To verify the rules work correctly:**

1. **Submit Alice (all excellent)** → Should be **APPROVED** ✅
2. **Submit Bob (all good)** → Should be **APPROVED** ✅
3. **Submit Charlie (mixed, high risk)** → Should be **REJECTED** ❌

Each test confirms the rules are working as designed.

---

## 📝 How Decisions Are Made

**Flow Diagram:**

```
Applicant Submits Application
         ↓
Extract 8 Parameters:
├─ Credit Score
├─ DTI Ratio
├─ Employment Duration
├─ Loan-to-Income Ratio
├─ Income Level
├─ Age
├─ Loan Amount
└─ Tenure
         ↓
Evaluate Each Against Rules
         ↓
Calculate Average Weight
         ↓
Convert to Risk Score (0-100)
         ↓
Check HARD REJECTION Rules
├─ If ANY triggered → REJECTED ❌
└─ Else Continue
         ↓
Apply Decision Logic
├─ If Risk < 30 & Confidence ≥ 80% → APPROVED ✅
├─ Elif Risk < 25 → APPROVED ✅
├─ Elif Risk ≥ 75 → REJECTED ❌
└─ Else → REQUIRES MANUAL REVIEW ⏳
         ↓
Generate Explanation
         ↓
Return Decision to Applicant
```

---

## 💡 Key Insights

1. **DTI is the strongest predictor** - Single most important factor
2. **Credit score matters greatly** - Historical repayment behavior
3. **Employment stability** - Income must be proven/stable
4. **Income level** - Supports overall repayment capacity
5. **No single perfect metric** - Holistic evaluation needed

---

## 📞 Questions?

Refer to [APP_NAVIGATION_GUIDE.md](APP_NAVIGATION_GUIDE.md) for how to test the system with these rules.

