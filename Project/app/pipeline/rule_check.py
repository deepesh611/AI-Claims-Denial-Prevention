# pipeline/rule_check_bq.py  (GCP BigQuery version)

import pandas as pd
import os
from google.cloud import bigquery

PROJECT = os.environ.get("GCP_PROJECT_ID", "ai-claims-denial-prediction")
DATASET  = "gold"

def get_client():
    return bigquery.Client(project=PROJECT)

def run_rule_check(claim_ids: list):

    ids_str = ", ".join([f"'{cid}'" for cid in claim_ids])

    query = f"""
        SELECT
            claim_id,
            patient_id,
            provider_id,
            diagnosis_code,
            procedure_code,
            billed_amount,
            average_cost,
            expected_cost,
            billed_vs_avg_cost,
            date
        FROM `{PROJECT}.{DATASET}.gold_claim_features`
        WHERE claim_id IN ({ids_str})
    """

    client = get_client()
    query_job = client.query(query)
    df = query_job.to_dataframe()

    # Claims not found
    found_ids = df["claim_id"].tolist()
    not_found = [cid for cid in claim_ids if cid not in found_ids]

    passed = []
    failed = {}

    for _, row in df.iterrows():
        failures = []

        if pd.isnull(row["patient_id"]) or row["patient_id"] == "":
            failures.append("patient_id is missing")

        if pd.isnull(row["provider_id"]) or row["provider_id"] == "":
            failures.append("provider_id is missing")

        if pd.isnull(row["diagnosis_code"]) or row["diagnosis_code"] == "":
            failures.append("diagnosis_code is missing")

        if pd.isnull(row["procedure_code"]) or row["procedure_code"] == "UNKNOWN":
            failures.append("procedure_code is missing or UNKNOWN")

        if pd.isnull(row["billed_amount"]) or row["billed_amount"] <= 0:
            failures.append("billed_amount must be greater than 0")

        if pd.isnull(row["average_cost"]) or row["average_cost"] <= 0:
            failures.append("average_cost is 0 or missing")

        if pd.isnull(row["expected_cost"]) or row["expected_cost"] <= 0:
            failures.append("expected_cost is 0 or missing")

        if pd.isnull(row["billed_vs_avg_cost"]) or row["billed_vs_avg_cost"] <= 0:
            failures.append("billed_vs_avg_cost is invalid")

        if pd.isnull(row["date"]):
            failures.append("date is missing")

        if failures:
            failed[row["claim_id"]] = failures
        else:
            passed.append(row["claim_id"])

    for cid in not_found:
        failed[cid] = ["claim_id not found in system"]

    return {"passed": passed, "failed": failed}
