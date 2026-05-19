import logging
import sys
from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark.sql.functions import col, avg, when, round, count as spark_count, sum as spark_sum
from py4j.protocol import Py4JJavaError
from utils import read_from_gcs, write_to_bq, SILVER_PATH

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

def main():
    spark = None
    try:
        spark = SparkSession.builder.appName("gold_claims").getOrCreate()
        logger.info("SparkSession started")

        # Read silver tables
        claims    = read_from_gcs(spark, f"{SILVER_PATH}/claims")
        providers = read_from_gcs(spark, f"{SILVER_PATH}/providers")
        diagnosis = read_from_gcs(spark, f"{SILVER_PATH}/diagnosis")
        costs     = read_from_gcs(spark, f"{SILVER_PATH}/costs")

        for name, df in [("claims", claims), ("providers", providers),
                         ("diagnosis", diagnosis), ("costs", costs)]:
            if df is None or df.rdd.isEmpty():
                logger.error(f"Silver table '{name}' is empty or missing — cannot build gold layer")
                sys.exit(1)

        logger.info(f"Read silver tables — claims: {claims.count()} rows, "
                    f"providers: {providers.count()} rows, "
                    f"diagnosis: {diagnosis.count()} rows, "
                    f"costs: {costs.count()} rows")

        # Aggregate costs
        logger.info("Aggregating costs by procedure_code")
        cost_agg = costs.groupBy("procedure_code").agg(
            avg("average_cost").alias("average_cost"),
            avg("expected_cost").alias("expected_cost")
        )

        # Join all tables
        logger.info("Joining silver tables")
        gold = claims.join(providers, on="provider_id", how="left") \
                     .join(diagnosis, on="diagnosis_code", how="left") \
                     .join(cost_agg, on="procedure_code", how="left")

        # Fill nulls
        gold = gold.fillna({
            "category"     : "Unknown",
            "severity"     : "Unknown",
            "average_cost" : 0.0,
            "expected_cost": 0.0,
            "specialty"    : "Unknown",
            "location"     : "Unknown",
            "doctor_name"  : "Unknown"
        })

        # Feature engineering
        logger.info("Engineering features")
        gold = gold.withColumn(
            "billed_vs_avg_cost",
            round(col("billed_amount") / (col("average_cost") + 1), 2)
        ).withColumn(
            "high_cost_flag",
            when(col("billed_amount") > col("average_cost"), 1).otherwise(0)
        )

        # Provider stats
        logger.info("Computing provider stats")
        provider_stats = gold.groupBy("provider_id").agg(
            spark_count("claim_id").alias("provider_claim_count"),
            round(spark_sum("denial_flag") / spark_count("claim_id"), 4).alias("provider_risk_score")
        )
        gold = gold.join(provider_stats, on="provider_id", how="left")

        # Diagnosis count
        logger.info("Computing diagnosis counts")
        diagnosis_stats = gold.groupBy("diagnosis_code").agg(
            spark_count("claim_id").alias("diagnosis_count")
        )
        gold = gold.join(diagnosis_stats, on="diagnosis_code", how="left")

        # Claim frequency
        logger.info("Computing claim frequency per patient")
        claim_freq = gold.groupBy("patient_id").agg(
            spark_count("claim_id").alias("claim_frequency")
        )
        gold = gold.join(claim_freq, on="patient_id", how="left")

        # Severity score
        gold = gold.withColumn(
            "severity_score",
            when(col("severity") == "High", 3)
            .when(col("severity") == "Medium", 2)
            .when(col("severity") == "Low", 1)
            .otherwise(0)
        )

        if gold.rdd.isEmpty():
            logger.error("Gold DataFrame is empty after joins — skipping write")
            sys.exit(1)

        row_count = gold.count()
        write_to_bq(gold, "gold_claim_features")
        logger.info(f"gold_claims done: {row_count} rows")

    except Py4JJavaError as e:
        logger.error(f"Spark/Java error in gold_claims: {e.java_exception}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error in gold_claims: {e}", exc_info=True)
        sys.exit(1)
    finally:
        if spark:
            spark.stop()
            logger.info("SparkSession stopped")

if __name__ == "__main__":
    main()