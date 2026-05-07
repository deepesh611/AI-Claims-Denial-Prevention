import dlt
from pyspark.sql import functions as F

# Bronze source (different pipeline, read via fully qualified name)
BRONZE_CATALOG = "main"
BRONZE_SCHEMA = "bronze"
BRONZE_TABLE = "bronze_diagnosis_raw"

# Pipeline config: catalog = "main", target = "silver"


# ── Quarantine table: captures rows with null mandatory fields ──
@dlt.table(
    name="quarantine_diagnosis",
    comment="Quarantine: Diagnosis rows with null mandatory fields"
)
def quarantine_diagnosis():
    df = spark.read.table(f"{BRONZE_CATALOG}.{BRONZE_SCHEMA}.{BRONZE_TABLE}")
    return (
        df.filter(
            F.col("diagnosis_code").isNull() |
            F.col("category").isNull() |
            F.col("severity").isNull()
        )
        .withColumn("quarantine_reason", F.lit("Null in mandatory field"))
        .withColumn("quarantine_timestamp", F.current_timestamp())
    )


# ── Silver table: cleaned and standardized diagnosis ──
@dlt.table(
    name="silver_diagnosis",
    comment="Silver layer: Cleaned and standardized diagnosis data"
)
@dlt.expect_or_drop("valid_diagnosis_code", "diagnosis_code IS NOT NULL")
@dlt.expect_or_drop("valid_category", "category IS NOT NULL")
@dlt.expect_or_drop("valid_severity", "severity IS NOT NULL")
def silver_diagnosis():
    df = spark.read.table(f"{BRONZE_CATALOG}.{BRONZE_SCHEMA}.{BRONZE_TABLE}")

    # ── 1. Deduplicate on diagnosis_code ──
    df = df.dropDuplicates(["diagnosis_code"])

    # ── 2. Standardize text fields ──
    df = (
        df.withColumn("diagnosis_code", F.upper(F.trim(F.regexp_replace("diagnosis_code", "[^a-zA-Z0-9]", ""))))
          .withColumn("category", F.initcap(F.trim(F.col("category"))))
          .withColumn("severity", F.initcap(F.trim(F.col("severity"))))
    )

    return df
