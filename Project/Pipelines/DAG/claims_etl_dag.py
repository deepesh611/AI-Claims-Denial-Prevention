from airflow import DAG
from airflow.models.baseoperator import chain
from airflow.providers.google.cloud.operators.dataproc import DataprocCreateBatchOperator
from airflow.providers.google.cloud.sensors.gcs import GCSObjectExistenceSensor
from datetime import datetime
from datetime import timedelta

# ── Config ────────────────────────────────────────────────────────────────────
PROJECT_ID   = "ai-claims-denial-prediction"
REGION       = "us-central1"
GCS_BUCKET   = "ai-claims-denial-data"
SCRIPTS_PATH = f"gs://{GCS_BUCKET}/ETL"
UTILS        = f"gs://{GCS_BUCKET}/ETL/utils.py"

DEFAULT_ARGS = {
    "owner"           : "airflow",
    "retries"         : 2,
    "retry_delay"     : timedelta(minutes=5),
    "depends_on_past" : False,
}

def make_batch(batch_id, script):
    return {
        "pyspark_batch": {
            "main_python_file_uri": f"{SCRIPTS_PATH}/{script}",
            "python_file_uris"    : [UTILS],
        },
        "runtime_config": {"version": "2.0"},
        "environment_config": {
            "execution_config": {
                "service_account": "277993454-compute@developer.gserviceaccount.com"
            }
        }
    }

# ── DAG ───────────────────────────────────────────────────────────────────────
with DAG(
    dag_id             = "claims_etl_pipeline",
    default_args       = DEFAULT_ARGS,
    start_date         = datetime(2024, 1, 1),
    schedule           = None,
    catchup            = False,
    tags               = ["etl", "claims"],
) as dag:

    # ── GCS Sensors (wait for files to land) ──────────────────────────────────
    wait_claims = GCSObjectExistenceSensor(
        task_id    = "wait_claims",
        bucket     = GCS_BUCKET,
        object     = "raw/claims.csv",
        timeout    = 3600,
        poke_interval = 60,
    )

    wait_providers = GCSObjectExistenceSensor(
        task_id   = "wait_providers",
        bucket    = GCS_BUCKET,
        object    = "raw/providers.csv",
        timeout   = 3600,
        poke_interval = 60,
    )

    wait_diagnosis = GCSObjectExistenceSensor(
        task_id   = "wait_diagnosis",
        bucket    = GCS_BUCKET,
        object    = "raw/diagnosis.csv",
        timeout   = 3600,
        poke_interval = 60,
    )

    wait_costs = GCSObjectExistenceSensor(
        task_id   = "wait_costs",
        bucket    = GCS_BUCKET,
        object    = "raw/costs.csv",
        timeout   = 3600,
        poke_interval = 60,
    )

    # ── Bronze (parallel) ─────────────────────────────────────────────────────
    bronze_claims = DataprocCreateBatchOperator(
        task_id    = "bronze_claims",
        project_id = PROJECT_ID,
        region     = REGION,
        batch_id   = "bronze-claims-{{ds_nodash}}-{{ts_nodash}}",
        batch      = make_batch("bronze-claims", "bronze/bronze_claims.py"),
    )

    bronze_providers = DataprocCreateBatchOperator(
        task_id    = "bronze_providers",
        project_id = PROJECT_ID,
        region     = REGION,
        batch_id   = "bronze-providers-{{ds_nodash}}-{{ts_nodash}}",
        batch      = make_batch("bronze-providers", "bronze/bronze_providers.py"),
    )

    bronze_diagnosis = DataprocCreateBatchOperator(
        task_id    = "bronze_diagnosis",
        project_id = PROJECT_ID,
        region     = REGION,
        batch_id   = "bronze-diagnosis-{{ds_nodash}}-{{ts_nodash}}",
        batch      = make_batch("bronze-diagnosis", "bronze/bronze_diagnosis.py"),
    )

    bronze_costs = DataprocCreateBatchOperator(
        task_id    = "bronze_costs",
        project_id = PROJECT_ID,
        region     = REGION,
        batch_id   = "bronze-costs-{{ds_nodash}}-{{ts_nodash}}",
        batch      = make_batch("bronze-costs", "bronze/bronze_costs.py"),
    )

    # ── Silver (parallel, after all bronze) ───────────────────────────────────
    silver_claims = DataprocCreateBatchOperator(
        task_id    = "silver_claims",
        project_id = PROJECT_ID,
        region     = REGION,
        batch_id   = "silver-claims-{{ds_nodash}}-{{ts_nodash}}",
        batch      = make_batch("silver-claims", "silver/silver_claims.py"),
    )

    silver_providers = DataprocCreateBatchOperator(
        task_id    = "silver_providers",
        project_id = PROJECT_ID,
        region     = REGION,
        batch_id   = "silver-providers-{{ds_nodash}}-{{ts_nodash}}",
        batch      = make_batch("silver-providers", "silver/silver_providers.py"),
    )

    silver_diagnosis = DataprocCreateBatchOperator(
        task_id    = "silver_diagnosis",
        project_id = PROJECT_ID,
        region     = REGION,
        batch_id   = "silver-diagnosis-{{ds_nodash}}-{{ts_nodash}}",
        batch      = make_batch("silver-diagnosis", "silver/silver_diagnosis.py"),
    )

    silver_costs = DataprocCreateBatchOperator(
        task_id    = "silver_costs",
        project_id = PROJECT_ID,
        region     = REGION,
        batch_id   = "silver-costs-{{ds_nodash}}-{{ts_nodash}}",
        batch      = make_batch("silver-costs", "silver/silver_costs.py"),
    )

    # ── Gold ──────────────────────────────────────────────────────────────────
    gold_claims = DataprocCreateBatchOperator(
        task_id    = "gold_claims",
        project_id = PROJECT_ID,
        region     = REGION,
        batch_id   = "gold-claims-{{ds_nodash}}-{{ts_nodash}}",
        batch      = make_batch("gold-claims", "gold/gold_claims.py"),
    )

    # ── Dependencies ──────────────────────────────────────────────────────────
    wait_claims    >> bronze_claims
    wait_providers >> bronze_providers
    wait_diagnosis >> bronze_diagnosis
    wait_costs     >> bronze_costs

    chain(
        [bronze_claims, bronze_providers, bronze_diagnosis, bronze_costs],
        [silver_claims, silver_providers, silver_diagnosis, silver_costs],
        gold_claims,
    )