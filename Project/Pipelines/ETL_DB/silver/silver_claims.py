import dlt
from pyspark.sql import functions as F

# Bronze source (different pipeline, read via fully qualified name)
BRONZE_CATALOG = "main"
BRONZE_SCHEMA = "bronze"
BRONZE_TABLE = "bronze_claims_raw"

# Pipeline config: catalog = "main", target = "silver"


# ── Quarantine table: captures rows with null mandatory fields ──
@dlt.table(
    name="quarantine_claims",
    comment="Quarantine: Claims rows with null mandatory fields"
)
def quarantine_claims():
    df = spark.read.table(f"{BRONZE_CATALOG}.{BRONZE_SCHEMA}.{BRONZE_TABLE}")
    return (
        df.filter(
            F.col("claim_id").isNull() |
            F.col("patient_id").isNull() |
            F.col("provider_id").isNull()
        )
        .withColumn("quarantine_reason", F.lit("Null in mandatory field"))
        .withColumn("quarantine_timestamp", F.current_timestamp())
    )


# ── Silver table: cleaned and standardized claims ──
@dlt.table(
    name="silver_claims",
    comment="Silver layer: Cleaned, deduplicated, and standardized claims data"
)
@dlt.expect_or_drop("valid_claim_id", "claim_id IS NOT NULL")
@dlt.expect_or_drop("valid_patient_id", "patient_id IS NOT NULL")
@dlt.expect_or_drop("valid_provider_id", "provider_id IS NOT NULL")
def silver_claims():
    df = spark.read.table(f"{BRONZE_CATALOG}.{BRONZE_SCHEMA}.{BRONZE_TABLE}")

    # ── 1. Fill billed_amount with median per procedure_code ──
    medians_per_code = df.groupBy("procedure_code").agg(
        F.percentile_approx("billed_amount", 0.5).alias("median_per_code")
    )
    df = df.join(medians_per_code, "procedure_code", "left")
    df = df.withColumn(
        "billed_amount",
        F.coalesce(F.col("billed_amount"), F.col("median_per_code"))
    ).drop("median_per_code")

    # ── 2. Global median fallback for remaining nulls ──
    global_median_df = df.agg(
        F.percentile_approx("billed_amount", 0.5).alias("global_median")
    )
    df = df.crossJoin(global_median_df)
    df = df.withColumn(
        "billed_amount",
        F.coalesce(F.col("billed_amount"), F.col("global_median"))
    ).drop("global_median")

    # ── 3. Fill non-mandatory nulls ──
    df = df.fillna({"diagnosis_code": "UNKNOWN", "procedure_code": "UNKNOWN"})

    # ── 4. Deduplicate on claim_id ──
    df = df.dropDuplicates(["claim_id"])

    # ── 5. Fix data types ──
    df = (
        df.withColumn("date", F.to_date(F.col("date")))
          .withColumn("billed_amount", F.col("billed_amount").cast("double"))
    )

    # ── 6. Standardize text fields ──
    df = (
        df.withColumn("diagnosis_code", F.upper(F.trim(F.regexp_replace("diagnosis_code", "[^a-zA-Z0-9]", ""))))
          .withColumn("procedure_code", F.upper(F.trim(F.regexp_replace("procedure_code", "[^a-zA-Z0-9]", ""))))
          .withColumn("claim_id", F.trim(F.col("claim_id")))
          .withColumn("patient_id", F.trim(F.col("patient_id")))
          .withColumn("provider_id", F.trim(F.col("provider_id")))
    )

    return df
