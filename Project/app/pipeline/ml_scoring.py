# pipeline/ml_scoring.py
import os
import pandas as pd
import numpy as np
import xgboost as xgb
from google.cloud import bigquery, storage

PROJECT = os.environ.get("GCP_PROJECT_ID", "ai-claims-denial-prediction")
BUCKET  = os.environ.get("GCS_BUCKET", "ai-claims-denial-data")
DATASET = "gold"

def get_bq_client():
    return bigquery.Client(project=PROJECT)

def get_gcs_client():
    return storage.Client()

def load_model():
    client = get_gcs_client()
    bucket = client.bucket(BUCKET)
    blob   = bucket.blob("models/model.ubj")
    blob.download_to_filename("/tmp/model.ubj")
    model  = xgb.XGBClassifier()
    model.load_model("/tmp/model.ubj")
    return model

def get_claims_data(claim_ids: list):
    ids_str   = ", ".join([f"'{cid}'" for cid in claim_ids])
    query     = f"""
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
    client    = get_bq_client()
    return client.query(query).to_dataframe()

def encode_categoricals(df: pd.DataFrame):
    for c in ["specialty", "category", "location"]:
        df[c + "_idx"] = df[c].astype("category").cat.codes
    return df

def run_ml_scoring(claim_ids: list):
    xgb_model = load_model()
    df        = get_claims_data(claim_ids)
    df        = encode_categoricals(df)
    df        = df.reset_index(drop=True)

    feature_cols = [
        "billed_amount", "billed_vs_avg_cost", "high_cost_flag",
        "severity_score", "specialty_idx", "category_idx", "location_idx"
    ]

    X           = df[feature_cols].values
    probs       = xgb_model.predict_proba(X)[:, 1]
    predictions = (probs >= 0.5).astype(int)

    results = {}
    for i, row in df.iterrows():
        results[row["claim_id"]] = {
            "risk_score": round(float(probs[i]), 4),
            "risk_label": "HIGH" if predictions[i] == 1 else "LOW"
        }

    return results, xgb_model, df