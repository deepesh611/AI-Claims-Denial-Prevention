import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="Claim Denial Prevention System",
    page_icon="🏥",
    layout="wide",
)

# ── Styling ──────────────────────────────────────────────────────────────────
st.markdown(
    """
    <style>
        /* Page background */
        .stApp { background-color: #0d1117; }

        /* Kill Streamlit's own white backgrounds */
        section[data-testid="stSidebar"],
        .stMainBlockContainer,
        div[data-testid="stAppViewBlockContainer"],
        div[data-testid="stVerticalBlock"] { background-color: #0d1117; }

        /* Global text colour */
        html, body, .stApp, p, li, label, span,
        .stMarkdown, .stText { color: #e6edf3; }

        /* Subheaders */
        h2, h3 { color: #c9d1d9 !important; }

        /* Header */
        .app-header {
            background: linear-gradient(135deg, #0d2137 0%, #0f3460 100%);
            border: 1px solid #1f6feb;
            padding: 2rem 2.5rem 1.5rem;
            border-radius: 12px;
            margin-bottom: 2rem;
            color: #e6edf3;
        }
        .app-header h1 { margin: 0; font-size: 2rem; font-weight: 700; color: #e6edf3; }
        .app-header p  { margin: 0.4rem 0 0; font-size: 1rem; opacity: 0.85; color: #8b949e; }

        /* Claim cards */
        .claim-card {
            background: #161b22;
            border: 1px solid #30363d;
            border-radius: 12px;
            padding: 1.5rem 1.75rem;
            margin-bottom: 1.25rem;
        }
        .claim-id { font-size: 1.25rem; font-weight: 700; color: #e6edf3; margin-bottom: 0.5rem; }

        /* Status badges */
        .badge {
            display: inline-block;
            padding: 0.3rem 0.85rem;
            border-radius: 20px;
            font-size: 0.8rem;
            font-weight: 700;
            letter-spacing: 0.05em;
            text-transform: uppercase;
            margin-bottom: 0.75rem;
        }
        .badge-high  { background: #3d1a1a; color: #ff7b72; border: 1px solid #6e2626; }
        .badge-rule  { background: #2d2200; color: #e3b341; border: 1px solid #5a4000; }
        .badge-low   { background: #0d2a0d; color: #56d364; border: 1px solid #1a5c1a; }

        /* Section labels inside cards */
        .field-label { font-size: 0.78rem; font-weight: 600; color: #58a6ff; text-transform: uppercase;
                       letter-spacing: 0.06em; margin-top: 0.9rem; margin-bottom: 0.2rem; }
        .field-value { font-size: 0.95rem; color: #e6edf3; }
        .risk-score  { font-size: 1.6rem; font-weight: 700; color: #58a6ff; }

        /* Upload box */
        .upload-section {
            background: #161b22;
            border: 2px dashed #30363d;
            border-radius: 10px;
            padding: 1.5rem;
            margin-bottom: 1.5rem;
        }

        /* Streamlit file uploader & input widgets — dark */
        [data-testid="stFileUploader"] {
            background: #161b22;
            border: 1px solid #30363d;
            border-radius: 8px;
            padding: 0.5rem;
        }
        [data-testid="stFileUploader"] label,
        [data-testid="stFileUploader"] span { color: #8b949e !important; }

        /* Metric cards */
        [data-testid="stMetric"] {
            background: #161b22;
            border: 1px solid #30363d;
            border-radius: 10px;
            padding: 0.75rem 1rem;
        }
        [data-testid="stMetricLabel"] { color: #8b949e !important; }
        [data-testid="stMetricValue"]  { color: #e6edf3 !important; }

        /* Expander */
        [data-testid="stExpander"] {
            background: #0d1117;
            border: 1px solid #30363d;
            border-radius: 8px;
        }
        [data-testid="stExpander"] summary { color: #58a6ff !important; }

        /* Table */
        table { background: #161b22 !important; color: #e6edf3 !important; }
        th { background: #21262d !important; color: #8b949e !important; }
        td { color: #e6edf3 !important; border-color: #30363d !important; }

        /* Divider */
        hr.section-divider { border: none; border-top: 1px solid #30363d; margin: 2rem 0; }

        /* Info / success / error boxes */
        [data-testid="stAlert"] { background: #161b22 !important; border-color: #30363d !important; }
    </style>
    """,
    unsafe_allow_html=True,
)

# ── Dummy claim data ──────────────────────────────────────────────────────────
DUMMY_CLAIMS = [
    {
        "claim_id": "CLM-2024-001",
        "status": "HIGH RISK",
        "badge_class": "badge-high",
        "risk_score": 0.92,
        "reasons": [
            "Procedure code mismatch with diagnosis",
            "Duplicate submission detected within 30 days",
            "Provider NPI flagged for prior audits",
        ],
        "policy_violated": "Policy 4.2.1 — Duplicate Claim Submission; Policy 7.3 — Procedure-Diagnosis Consistency",
        "ai_recommendation": (
            "This claim carries a very high probability of denial. The billed procedure (CPT 99215) "
            "does not align with the primary diagnosis code (Z00.00 — routine exam), and an identical "
            "claim was submitted on 2024-02-14. Recommend holding for manual clinical review and "
            "contacting the provider to supply a corrected claim with supporting documentation before "
            "resubmission."
        ),
        "detail": {
            "Patient ID": "PAT-8821",
            "Provider NPI": "1234567890",
            "Service Date": "2024-03-01",
            "Billed Amount": "$850.00",
            "CPT Code": "99215",
            "ICD-10": "Z00.00",
            "Prior Submissions": "1 (2024-02-14)",
            "Payer": "BlueCross BlueShield",
        },
    },
    {
        "claim_id": "CLM-2024-002",
        "status": "RULE FAIL",
        "badge_class": "badge-rule",
        "risk_score": 0.54,
        "reasons": [
            "Missing prior authorization for elective surgery",
            "Out-of-network provider billed at in-network rate",
        ],
        "policy_violated": "Policy 2.1 — Prior Authorization Requirements; Policy 9.4 — Network Rate Billing",
        "ai_recommendation": (
            "This claim fails two business rules but is not flagged for fraud. The elective procedure "
            "(CPT 27447 — total knee arthroplasty) requires prior authorization that is absent from the "
            "claim record. Additionally, the performing surgeon (NPI 9876543210) is out-of-network. "
            "Recommend returning the claim to the provider with a request for auth reference number and "
            "correct network-rate billing."
        ),
        "detail": {
            "Patient ID": "PAT-4456",
            "Provider NPI": "9876543210",
            "Service Date": "2024-03-05",
            "Billed Amount": "$22,400.00",
            "CPT Code": "27447",
            "ICD-10": "M17.11",
            "Prior Auth": "Not found",
            "Payer": "Aetna",
        },
    },
    {
        "claim_id": "CLM-2024-003",
        "status": "LOW RISK",
        "badge_class": "badge-low",
        "risk_score": 0.11,
        "reasons": [
            "All codes valid and consistent",
            "Provider in good standing",
        ],
        "policy_violated": "None",
        "ai_recommendation": (
            "This claim appears clean and ready for adjudication. The office visit (CPT 99213) aligns "
            "with the acute sinusitis diagnosis (J01.90), the billed amount is within expected fee "
            "schedule limits, and the provider has no audit history. Recommend auto-adjudication with "
            "standard processing."
        ),
        "detail": {
            "Patient ID": "PAT-6673",
            "Provider NPI": "1122334455",
            "Service Date": "2024-03-08",
            "Billed Amount": "$185.00",
            "CPT Code": "99213",
            "ICD-10": "J01.90",
            "Prior Auth": "Not required",
            "Payer": "United Healthcare",
        },
    },
]


def render_badge(status: str, badge_class: str) -> str:
    return f'<span class="badge {badge_class}">{status}</span>'


def render_claim_card(claim: dict) -> None:
    with st.container():
        st.markdown('<div class="claim-card">', unsafe_allow_html=True)

        # Claim ID + badge
        st.markdown(f'<div class="claim-id">🗂 {claim["claim_id"]}</div>', unsafe_allow_html=True)
        st.markdown(render_badge(claim["status"], claim["badge_class"]), unsafe_allow_html=True)

        col1, col2 = st.columns([1, 3])

        with col1:
            st.markdown('<div class="field-label">Risk Score</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="risk-score">{claim["risk_score"]:.2f}</div>', unsafe_allow_html=True)

        with col2:
            st.markdown('<div class="field-label">Reasons</div>', unsafe_allow_html=True)
            reasons_html = "".join(f"<li>{r}</li>" for r in claim["reasons"])
            st.markdown(f'<ul style="margin:0;padding-left:1.2rem;">{reasons_html}</ul>', unsafe_allow_html=True)

        st.markdown('<div class="field-label">Policy Violated</div>', unsafe_allow_html=True)
        st.markdown(f'<em>{claim["policy_violated"]}</em>', unsafe_allow_html=True)

        st.markdown('<div class="field-label">AI Recommendation</div>', unsafe_allow_html=True)
        st.markdown(f'<p style="margin:0;line-height:1.6;">{claim["ai_recommendation"]}</p>', unsafe_allow_html=True)

        with st.expander("🔍 View Full Detail"):
            detail_df = pd.DataFrame(
                list(claim["detail"].items()), columns=["Field", "Value"]
            )
            st.table(detail_df)

        st.markdown("</div>", unsafe_allow_html=True)


# ── App layout ────────────────────────────────────────────────────────────────
st.markdown(
    """
    <div class="app-header">
        <h1>🏥 Claim Denial Prevention System</h1>
        <p>Upload claims for risk analysis</p>
    </div>
    """,
    unsafe_allow_html=True,
)

# Input section
st.subheader("📂 Upload Claims File")
uploaded_file = st.file_uploader(
    "Upload a CSV file with a `claim_id` column",
    type=["csv"],
    help="The CSV must contain a column named 'claim_id'.",
)

claims_to_show = None

if uploaded_file is not None:
    try:
        df = pd.read_csv(uploaded_file)
        if "claim_id" not in df.columns:
            st.error("❌ The uploaded CSV does not contain a `claim_id` column. Please check your file.")
        else:
            st.success(f"✅ File uploaded successfully — {len(df)} claim(s) found.")
            st.markdown("**Preview of uploaded claims:**")
            st.dataframe(df[["claim_id"]], use_container_width=True, hide_index=True)

            if st.button("▶ Run Analysis", type="primary", use_container_width=True):
                claims_to_show = DUMMY_CLAIMS

    except Exception as e:
        st.error(f"❌ Could not read the file: {e}")
else:
    st.info("No file uploaded yet. Using sample data — click **Run Analysis** to see results.")
    if st.button("▶ Run Analysis (Sample Data)", type="primary", use_container_width=True):
        claims_to_show = DUMMY_CLAIMS

# Output section
if claims_to_show:
    st.markdown('<hr class="section-divider">', unsafe_allow_html=True)
    st.subheader(f"📋 Analysis Results — {len(claims_to_show)} Claim(s)")

    summary_cols = st.columns(3)
    high  = sum(1 for c in claims_to_show if c["status"] == "HIGH RISK")
    rule  = sum(1 for c in claims_to_show if c["status"] == "RULE FAIL")
    low   = sum(1 for c in claims_to_show if c["status"] == "LOW RISK")

    with summary_cols[0]:
        st.metric("🔴 HIGH RISK", high)
    with summary_cols[1]:
        st.metric("🟡 RULE FAIL", rule)
    with summary_cols[2]:
        st.metric("🟢 LOW RISK", low)

    st.markdown("<br>", unsafe_allow_html=True)

    for claim in claims_to_show:
        render_claim_card(claim)
