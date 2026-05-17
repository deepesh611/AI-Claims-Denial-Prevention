# pipeline/rule_check.py

import pandas as pd
from databricks import sql
import os

CATALOG = "main"
SCHEMA  = "gold"

def get_connection():
    return sql.connect(
        server_hostname = os.environ["DATABRICKS_HOST"],
        http_path       = os.environ["DATABRICKS_HTTP_PATH"],
        access_token    = os.environ["DATABRICKS_TOKEN"]
    )

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
        FROM {CATALOG}.{SCHEMA}.gold_claim_features
        WHERE claim_id IN ({ids_str})
    """

    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(query)
            rows = cursor.fetchall()
            cols = [d[0] for d in cursor.description]

    df = pd.DataFrame(rows, columns=cols)

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