# pipeline/ml_scoring.py

import pandas as pd
import numpy as np
import os
from databricks import sql

CATALOG = "main"
SCHEMA  = "gold"

def get_connection():
    return sql.connect(
        server_hostname = os.environ["DATABRICKS_HOST"],
        http_path       = os.environ["DATABRICKS_HTTP_PATH"],
        access_token    = os.environ["DATABRICKS_TOKEN"]
    )

def get_claims_data(claim_ids: list):
    ids_str = ", ".join([f"'{cid}'" for cid in claim_ids])
    query = f"""
        SELECT
            claim_id,
            billed_amount,
            billed_vs_avg_cost,
            high_cost_flag,
            severity_score,
            specialty,
            category,
            location
        FROM {CATALOG}.{SCHEMA}.gold_claim_features
        WHERE claim_id IN ({ids_str})
    """
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(query)
            rows = cursor.fetchall()
            cols = [d[0] for d in cursor.description]

    return pd.DataFrame(rows, columns=cols)

def encode_categoricals(df: pd.DataFrame):
    cat_cols = ["specialty", "category", "location"]
    for c in cat_cols:
        df[c + "_idx"] = df[c].astype("category").cat.codes
    return df

def run_ml_scoring(claim_ids: list):
    """
    Input  : list of claim_ids that passed rule check
    Output : dict of claim_id -> {risk_score, risk_label}
    """
    import mlflow
    import mlflow.xgboost
    import requests
    import logging

    logger = logging.getLogger(__name__)

    # 1. Load the model registry settings for SHAP local analysis
    # We load from 'l.claim_denial_model' (champion or version 1)
    mlflow.set_registry_uri("databricks-uc")
    try:
        model_uri = "models:/models.claims_denial.claim_denial_model/champion"
        xgb_model = mlflow.xgboost.load_model(model_uri)
    except Exception:
        model_uri = "models:/models.claims_denial.claim_denial_model/1"
        xgb_model = mlflow.xgboost.load_model(model_uri)

    df = get_claims_data(claim_ids)
    df = encode_categoricals(df)

    feature_cols = [
        "billed_amount", "billed_vs_avg_cost", "high_cost_flag",
        "severity_score", "specialty_idx", "category_idx", "location_idx"
    ]

    X = df[feature_cols].values

    # 2. Communicate with the Model Serving endpoint in GCP Databricks
    token = os.environ["DATABRICKS_TOKEN"]
    url = os.environ.get(
        "DATABRICKS_MODEL_SERVING_URL",
        f"{os.environ['DATABRICKS_HOST'].rstrip('/')}/api/2.0/serving-endpoints/claim-denial-endpoint/invocations"
    )
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    payload = {
        "dataframe_split": {
            "columns": feature_cols,
            "data": X.tolist()
        }
    }

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=10)
        response.raise_for_status()
        predictions_raw = response.json().get("predictions", [])
    except Exception as e:
        logger.error(f"Error querying model serving endpoint ({url}): {e}. Falling back to local model.")
        # Fallback to local model if serving endpoint is not ready / fails
        predictions_raw = xgb_model.predict_proba(X)[:, 1].tolist()

    # 3. Parse predictions / probabilities robustly
    probs = []
    predictions = []
    for p in predictions_raw:
        if isinstance(p, list):
            # e.g. [prob_class_0, prob_class_1]
            prob = float(p[1]) if len(p) >= 2 else float(p[0])
            probs.append(prob)
            predictions.append(1 if prob >= 0.5 else 0)
        elif isinstance(p, dict):
            # e.g. {"probabilities": [0.85, 0.15]}
            if "probabilities" in p:
                prob = float(p["probabilities"][1])
            elif "prediction" in p:
                prob = float(p["prediction"])
            else:
                prob = float(next(iter(p.values())))
            probs.append(prob)
            predictions.append(1 if prob >= 0.5 else 0)
        else:
            # scalar float or label
            val = float(p)
            probs.append(val)
            predictions.append(1 if val >= 0.5 else 0)

    results = {}
    for i, row in df.iterrows():
        results[row["claim_id"]] = {
            "risk_score": round(float(probs[i]), 4),
            "risk_label": "HIGH" if predictions[i] == 1 else "LOW"
        }

    return results, xgb_model, df