import dlt
from pyspark.sql import functions as F

# Bronze source (different pipeline, read via fully qualified name)
BRONZE_CATALOG = "main"
BRONZE_SCHEMA = "bronze"
BRONZE_TABLE = "bronze_costs_raw"

# Pipeline config: catalog = "main", target = "silver"


# ── Quarantine table: captures rows with null mandatory fields ──
@dlt.table(
    name="quarantine_costs",
    comment="Quarantine: Costs rows with null mandatory fields"
)
def quarantine_costs():
    df = spark.read.table(f"{BRONZE_CATALOG}.{BRONZE_SCHEMA}.{BRONZE_TABLE}")
    return (
        df.filter(
            F.col("procedure_code").isNull() |
            F.col("average_cost").isNull() |
            F.col("expected_cost").isNull()
        )
        .withColumn("quarantine_reason", F.lit("Null in mandatory field"))
        .withColumn("quarantine_timestamp", F.current_timestamp())
    )


# ── Silver table: cleaned and standardized costs ──
@dlt.table(
    name="silver_costs",
    comment="Silver layer: Cleaned and standardized costs data"
)
@dlt.expect_or_drop("valid_procedure_code", "procedure_code IS NOT NULL")
@dlt.expect_or_drop("valid_average_cost", "average_cost IS NOT NULL")
@dlt.expect_or_drop("valid_expected_cost", "expected_cost IS NOT NULL")
def silver_costs():
    df = spark.read.table(f"{BRONZE_CATALOG}.{BRONZE_SCHEMA}.{BRONZE_TABLE}")

    # ── 1. Fill non-mandatory nulls ──
    df = df.fillna({"region": "UNKNOWN"})

    # ── 2. Deduplicate on procedure_code ──
    df = df.dropDuplicates(["procedure_code"])

    # ── 3. Fix data types ──
    df = (
        df.withColumn("average_cost", F.col("average_cost").cast("double"))
          .withColumn("expected_cost", F.col("expected_cost").cast("double"))
    )

    # ── 4. Standardize text fields ──
    df = (
        df.withColumn("procedure_code", F.upper(F.trim(F.regexp_replace("procedure_code", "[^a-zA-Z0-9]", ""))))
          .withColumn("region", F.initcap(F.trim(F.col("region"))))
    )

    return df
