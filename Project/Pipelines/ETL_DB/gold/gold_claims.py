import dlt
from pyspark.sql import functions as F
from pyspark.sql.functions import col, avg, when, round, count as spark_count, sum as spark_sum

# Silver source (different pipeline, read via fully qualified name)
SILVER_CATALOG = "main"
SILVER_SCHEMA = "silver"

# Pipeline config: catalog = "main", target = "gold"


# ── Gold Table 1: gold_claim_base ──
# Joins all silver tables into a single denormalized fact table
@dlt.table(
    name="gold_claim_base",
    comment="Gold layer: Denormalized claims table joining claims, providers, diagnosis, and costs"
)
def gold_claim_base():
    # Read silver tables and drop Auto Loader rescued data column to avoid join collisions
    claims    = spark.read.table(f"{SILVER_CATALOG}.{SILVER_SCHEMA}.silver_claims").drop("_rescued_data")
    providers = spark.read.table(f"{SILVER_CATALOG}.{SILVER_SCHEMA}.silver_providers").drop("_rescued_data")
    diagnosis = spark.read.table(f"{SILVER_CATALOG}.{SILVER_SCHEMA}.silver_diagnosis").drop("_rescued_data")
    costs     = spark.read.table(f"{SILVER_CATALOG}.{SILVER_SCHEMA}.silver_costs").drop("_rescued_data")

    # Aggregate cost by procedure_code (average across regions)
    cost_agg = costs.groupBy("procedure_code").agg(
        avg("average_cost").alias("average_cost"),
        avg("expected_cost").alias("expected_cost")
    )

    # Join all tables
    gold = claims.join(providers, on="provider_id", how="left")
    gold = gold.join(diagnosis, on="diagnosis_code", how="left")
    gold = gold.join(cost_agg, on="procedure_code", how="left")

    # Fill nulls from failed joins
    gold = gold.fillna({
        "category"      : "Unknown",
        "severity"      : "Unknown",
        "average_cost"  : 0.0,
        "expected_cost" : 0.0,
        "specialty"     : "Unknown",
        "location"      : "Unknown",
        "doctor_name"   : "Unknown"
    })

    return gold


# ── Gold Table 2: gold_claim_features ──
# Enriched table with engineered features for ML consumption
@dlt.table(
    name="gold_claim_features",
    comment="Gold layer: Feature-engineered claims table for ML model training"
)
def gold_claim_features():
    # Read from gold_claim_base (same pipeline, so use dlt.read)
    gold = dlt.read("gold_claim_base")

    # ── 1. Billed vs Average Cost Ratio & High Cost Flag ──
    gold = gold.withColumn(
        "billed_vs_avg_cost",
        round(col("billed_amount") / (col("average_cost") + 1), 2)
    ).withColumn(
        "high_cost_flag",
        when(col("billed_amount") > col("average_cost"), 1).otherwise(0)
    )

    # ── 2. Provider Statistics ──
    # Claim count and risk score per provider
    provider_stats = gold.groupBy("provider_id").agg(
        spark_count("claim_id").alias("provider_claim_count"),
        round(spark_sum("denial_flag") / spark_count("claim_id"), 4).alias("provider_risk_score")
    )
    gold = gold.join(provider_stats, on="provider_id", how="left")

    # ── 3. Diagnosis Count ──
    diagnosis_stats = gold.groupBy("diagnosis_code").agg(
        spark_count("claim_id").alias("diagnosis_count")
    )
    gold = gold.join(diagnosis_stats, on="diagnosis_code", how="left")

    # ── 4. Claim Frequency per Patient ──
    claim_freq = gold.groupBy("patient_id").agg(
        spark_count("claim_id").alias("claim_frequency")
    )
    gold = gold.join(claim_freq, on="patient_id", how="left")

    # ── 5. Severity Score ──
    gold = gold.withColumn(
        "severity_score",
        when(col("severity") == "High", 3)
        .when(col("severity") == "Medium", 2)
        .when(col("severity") == "Low", 1)
        .otherwise(0)
    )

    return gold
