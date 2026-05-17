# pipeline/ml_scoring_bq.py  (GCP BigQuery version)

import pandas as pd
import numpy as np
import os
from google.cloud import bigquery

PROJECT  = os.environ.get("GCP_PROJECT_ID", "your-gcp-project-id")
DATASET  = "gold"

def get_client():
    return bigquery.Client(project=PROJECT)

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
        FROM `{PROJECT}.{DATASET}.gold_claim_features`
        WHERE claim_id IN ({ids_str})
    """
    client = get_client()
    query_job = client.query(query)
    return query_job.to_dataframe()

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
    model_uri = f"models:/{PROJECT}.{DATASET}.claim_denial_model/1"
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
