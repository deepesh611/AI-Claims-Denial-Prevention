# api/main.py

import pandas as pd
import logging
import json
import time
import base64
from typing import Optional, List
from fastapi import FastAPI, HTTPException, Request, Header
from fastapi.middleware.cors import CORSMiddleware

from models import PredictRequest, PredictResponse, ClaimResult
from pipeline.rule_check import run_rule_check
from pipeline.ml_scoring import run_ml_scoring
from pipeline.shap_explainer import run_shap
from pipeline.rag import run_rag
from pipeline.agent import run_ai_agent

# Configure security audit logging
logger = logging.getLogger("security_audit")
logger.setLevel(logging.INFO)
logger.propagate = False  # Avoid double logging if root logger is already configured

class JsonFormatter(logging.Formatter):
    def format(self, record):
        log_data = {
            "timestamp": self.formatTime(record, self.datefmt),
            "level": record.levelname,
            "message": record.getMessage()
        }
        if hasattr(record, "audit_data"):
            log_data.update(record.audit_data)
        return json.dumps(log_data)

# Clear existing handlers to prevent duplicates during reloads
if logger.hasHandlers():
    logger.handlers.clear()

handler = logging.StreamHandler()
handler.setFormatter(JsonFormatter())
logger.addHandler(handler)

def decode_jwt_payload(token: str) -> Optional[dict]:
    try:
        if token.startswith("Bearer "):
            token = token[7:]
        parts = token.split(".")
        if len(parts) != 3:
            return None
        payload_b64 = parts[1]
        # Pad payload if necessary for base64 decoding
        payload_b64 += "=" * ((4 - len(payload_b64) % 4) % 4)
        decoded_bytes = base64.urlsafe_b64decode(payload_b64)
        return json.loads(decoded_bytes.decode("utf-8"))
    except Exception:
        return None

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
def predict(
    request: PredictRequest,
    fastapi_request: Request,
    authorization: Optional[str] = Header(None)
):
    start_time = time.time()

    # Extract client IP (handling GCP Cloud Run proxies)
    x_forwarded_for = fastapi_request.headers.get("x-forwarded-for")
    if x_forwarded_for:
        client_ip = x_forwarded_for.split(",")[0].strip()
    else:
        client_ip = fastapi_request.client.host if fastapi_request.client else "unknown"

    # Decode Google OAuth JWT token
    user_info = None
    auth_status = "missing"
    if authorization:
        user_info = decode_jwt_payload(authorization)
        if user_info:
            auth_status = "authenticated"
        else:
            auth_status = "invalid_token"

    # Audit log on request entry
    entry_audit = {
        "event": "SECURITY_AUDIT_REQUEST",
        "client_ip": client_ip,
        "auth_status": auth_status,
        "user_email": user_info.get("email") if user_info else None,
        "user_id": user_info.get("sub") if user_info else None,
        "user_name": user_info.get("name") if user_info else None,
        "claim_count": len(request.claim_ids),
        "claim_ids": request.claim_ids,
        "request_type": "multiple" if len(request.claim_ids) > 1 else "single"
    }
    logger.info("Prediction request received", extra={"audit_data": entry_audit})

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
                status           = "rule_fail",
                risk_score       = None,
                risk_label       = None,
                risk_level       = "rule_fail",
                rule_failures    = failures,
                reason_1         = None,
                reason_2         = None,
                policy_violated  = None,
                policy_text      = None,
                risk_reasons     = failures,
                ai_recommendation= ai_summaries.get(claim_id)
            ))

        for claim_id in passed:
            ml    = ml_results.get(claim_id, {})
            shap  = shap_results.get(claim_id, {})
            rag   = rag_results.get(claim_id, {})
            risk_label = ml.get("risk_label", "LOW")

            results.append(ClaimResult(
                claim_id         = claim_id,
                status           = risk_label.lower(),
                risk_score       = ml.get("risk_score"),
                risk_label       = risk_label,
                risk_level       = risk_label.lower(),
                rule_failures    = [],
                reason_1         = shap.get("reason_1"),
                reason_2         = shap.get("reason_2"),
                policy_violated  = rag.get("policy_source"),
                policy_text      = rag.get("policy_text"),
                risk_reasons     = [r for r in [shap.get("reason_1"), shap.get("reason_2")] if r],
                ai_recommendation= ai_summaries.get(claim_id)
            ))

        # Count metrics for audit logging
        rule_fail_count = len(failed)
        high_risk_count = len(high_risk_ids)
        medium_risk_count = sum(1 for cid in passed if ml_results.get(cid, {}).get("risk_label") == "MEDIUM")
        low_risk_count = sum(1 for cid in passed if ml_results.get(cid, {}).get("risk_label") == "LOW")

        latency_ms = int((time.time() - start_time) * 1000)

        # Audit log on response success
        exit_audit = {
            "event": "SECURITY_AUDIT_RESPONSE",
            "client_ip": client_ip,
            "auth_status": auth_status,
            "user_email": user_info.get("email") if user_info else None,
            "user_id": user_info.get("sub") if user_info else None,
            "user_name": user_info.get("name") if user_info else None,
            "claim_count": len(claim_ids),
            "status": "success",
            "latency_ms": latency_ms,
            "metrics": {
                "rule_fail_count": rule_fail_count,
                "high_risk_count": high_risk_count,
                "medium_risk_count": medium_risk_count,
                "low_risk_count": low_risk_count
            }
        }
        logger.info("Prediction request processed successfully", extra={"audit_data": exit_audit})

        return PredictResponse(results=results)

    except Exception as e:
        latency_ms = int((time.time() - start_time) * 1000)

        # Audit log on response failure
        exit_audit = {
            "event": "SECURITY_AUDIT_RESPONSE",
            "client_ip": client_ip,
            "auth_status": auth_status,
            "user_email": user_info.get("email") if user_info else None,
            "user_id": user_info.get("sub") if user_info else None,
            "user_name": user_info.get("name") if user_info else None,
            "claim_count": len(request.claim_ids),
            "status": "error",
            "error_detail": str(e),
            "latency_ms": latency_ms
        }
        logger.error(f"Prediction request failed: {str(e)}", extra={"audit_data": exit_audit})

        raise HTTPException(status_code=500, detail=str(e))