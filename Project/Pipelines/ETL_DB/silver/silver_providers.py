import dlt
from pyspark.sql import functions as F

# Bronze source (different pipeline, read via fully qualified name)
BRONZE_CATALOG = "main"
BRONZE_SCHEMA = "bronze"
BRONZE_TABLE = "bronze_providers_raw"

# Pipeline config: catalog = "main", target = "silver"


# ── Quarantine table: captures rows with null mandatory fields ──
@dlt.table(
    name="quarantine_providers",
    comment="Quarantine: Providers rows with null mandatory fields"
)
def quarantine_providers():
    df = spark.read.table(f"{BRONZE_CATALOG}.{BRONZE_SCHEMA}.{BRONZE_TABLE}")
    return (
        df.filter(
            F.col("provider_id").isNull() |
            F.col("doctor_name").isNull() |
            F.col("specialty").isNull()
        )
        .withColumn("quarantine_reason", F.lit("Null in mandatory field"))
        .withColumn("quarantine_timestamp", F.current_timestamp())
    )


# ── Silver table: cleaned and standardized providers ──
@dlt.table(
    name="silver_providers",
    comment="Silver layer: Cleaned and standardized providers data"
)
@dlt.expect_or_drop("valid_provider_id", "provider_id IS NOT NULL")
@dlt.expect_or_drop("valid_doctor_name", "doctor_name IS NOT NULL")
@dlt.expect_or_drop("valid_specialty", "specialty IS NOT NULL")
def silver_providers():
    df = spark.read.table(f"{BRONZE_CATALOG}.{BRONZE_SCHEMA}.{BRONZE_TABLE}")

    # ── 1. Fill non-mandatory nulls ──
    df = df.fillna({"location": "UNKNOWN"})

    # ── 2. Deduplicate on provider_id ──
    df = df.dropDuplicates(["provider_id"])

    # ── 3. Standardize text fields ──
    df = (
        df.withColumn("provider_id", F.trim(F.col("provider_id")))
          .withColumn("doctor_name", F.initcap(F.trim(F.col("doctor_name"))))
          .withColumn("specialty", F.initcap(F.trim(F.col("specialty"))))
          .withColumn("location", F.initcap(F.trim(F.col("location"))))
    )

    return df
