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

    mlflow.set_registry_uri("databricks-uc")
    model_uri = f"models:/{CATALOG}.{SCHEMA}.claim_denial_model/1"
    xgb_model = mlflow.xgboost.load_model(model_uri)

    df = get_claims_data(claim_ids)
    df = encode_categoricals(df)

    feature_cols = [
        "billed_amount", "billed_vs_avg_cost", "high_cost_flag",
        "severity_score", "specialty_idx", "category_idx", "location_idx"
    ]

    X = df[feature_cols].values
    probs       = xgb_model.predict_proba(X)[:, 1]
    predictions = (probs >= 0.5).astype(int)

    results = {}
    for i, row in df.iterrows():
        results[row["claim_id"]] = {
            "risk_score": round(float(probs[i]), 4),
            "risk_label": "HIGH" if predictions[i] == 1 else "LOW"
        }

    return results, xgb_model, df