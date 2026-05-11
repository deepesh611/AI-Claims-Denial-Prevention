# pipeline/ai_agent.py

import os
from openai import OpenAI

client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

def generate_summary(
    claim_id      : str,
    risk_label    : str,
    risk_score    : float = None,
    rule_failures : list  = None,
    reason_1      : str   = None,
    reason_2      : str   = None,
    policy_source : str   = None,
    policy_text   : str   = None
) -> str:

    if risk_label == "LOW":
        return "Claim passed all checks and is likely to be approved. No action required."

    if risk_label == "RULE FAIL":
        failures_text = "\n".join([f"- {f}" for f in rule_failures])
        prompt = f"""
You are a medical billing analyst. A claim has failed basic validation checks.

Claim ID: {claim_id}
Rule Failures:
{failures_text}

Write a short, clear summary (3-4 sentences) for the billing agent explaining:
1. What is wrong with this claim
2. What they need to fix before resubmitting

Be direct and specific. Do not use technical jargon.
"""

    else:  # HIGH RISK
        prompt = f"""
You are a medical billing analyst. A claim has been flagged as high risk of denial by an AI model.

Claim ID: {claim_id}
Risk Score: {risk_score}
Top Reasons:
- {reason_1}
- {reason_2 if reason_2 else "N/A"}
Policy Violated: {policy_source}
Policy Details: {policy_text}

Write a short, clear summary (3-4 sentences) for the billing agent explaining:
1. Why this claim is likely to be denied
2. Which policy it is violating
3. What specific steps they should take to fix it before submission

Be direct and specific. Do not use technical jargon.
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a helpful medical billing analyst assistant."},
            {"role": "user",   "content": prompt}
        ],
        temperature=0.3,
        max_tokens=200
    )

    return response.choices[0].message.content.strip()


def run_ai_agent(
    claim_ids    : list,
    passed       : list,
    failed       : dict,
    ml_results   : dict,
    shap_results : dict,
    rag_results  : dict
) -> dict:
    """
    Input  : all pipeline outputs
    Output : dict of claim_id -> ai_summary string
    """
    summaries = {}

    # RULE FAIL claims
    for claim_id, failures in failed.items():
        summaries[claim_id] = generate_summary(
            claim_id      = claim_id,
            risk_label    = "RULE FAIL",
            rule_failures = failures
        )

    # PASSED claims
    for claim_id in passed:
        ml         = ml_results.get(claim_id, {})
        risk_label = ml.get("risk_label", "LOW")
        risk_score = ml.get("risk_score", None)
        shap       = shap_results.get(claim_id, {})
        rag        = rag_results.get(claim_id, {})

        summaries[claim_id] = generate_summary(
            claim_id      = claim_id,
            risk_label    = risk_label,
            risk_score    = risk_score,
            reason_1      = shap.get("reason_1"),
            reason_2      = shap.get("reason_2"),
            policy_source = rag.get("policy_source"),
            policy_text   = rag.get("policy_text")
        )

    return summaries