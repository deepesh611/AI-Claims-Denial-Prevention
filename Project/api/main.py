# api/main.py

import pandas as pd
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from models import PredictRequest, PredictResponse, ClaimResult
from pipeline.rule_check import run_rule_check
from pipeline.ml_scoring import run_ml_scoring
from pipeline.shap_explainer import run_shap
from pipeline.rag import run_rag
from pipeline.agent import run_ai_agent

app = FastAPI(title="Claim Denial Prevention API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/predict", response_model=PredictResponse)
def predict(request: PredictRequest):
    try:
        claim_ids = request.claim_ids

        # Rule check
        rule_results = run_rule_check(claim_ids)
        passed       = rule_results["passed"]
        failed       = rule_results["failed"]

        # ML scoring
        if passed:
            ml_results, xgb_model, features_df = run_ml_scoring(passed)
        else:
            ml_results, xgb_model, features_df = {}, None, pd.DataFrame()

        # SHAP for high risk only
        high_risk_ids = [
            cid for cid in passed
            if ml_results.get(cid, {}).get("risk_label") == "HIGH"
        ]

        if high_risk_ids and xgb_model is not None:
            high_risk_df = features_df[
                features_df["claim_id"].isin(high_risk_ids)
            ].reset_index(drop=True)
            shap_results = run_shap(xgb_model, high_risk_df)
        else:
            shap_results = {}

        # RAG
        rag_results = run_rag(shap_results) if shap_results else {}

        # AI Agent
        ai_summaries = run_ai_agent(
            claim_ids    = claim_ids,
            passed       = passed,
            failed       = failed,
            ml_results   = ml_results,
            shap_results = shap_results,
            rag_results  = rag_results
        )

        # Build response
        results = []

        for claim_id, failures in failed.items():
            results.append(ClaimResult(
                claim_id         = claim_id,
                status           = "RULE_FAIL",
                risk_score       = None,
                risk_label       = None,
                rule_failures    = failures,
                reason_1         = None,
                reason_2         = None,
                policy_source    = None,
                policy_text      = None,
                ai_recommendation= ai_summaries.get(claim_id)
            ))

        for claim_id in passed:
            ml    = ml_results.get(claim_id, {})
            shap  = shap_results.get(claim_id, {})
            rag   = rag_results.get(claim_id, {})

            results.append(ClaimResult(
                claim_id         = claim_id,
                status           = ml.get("risk_label", "LOW"),
                risk_score       = ml.get("risk_score"),
                risk_label       = ml.get("risk_label"),
                rule_failures    = [],
                reason_1         = shap.get("reason_1"),
                reason_2         = shap.get("reason_2"),
                policy_source    = rag.get("policy_source"),
                policy_text      = rag.get("policy_text"),
                ai_recommendation= ai_summaries.get(claim_id)
            ))

        return PredictResponse(results=results)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))