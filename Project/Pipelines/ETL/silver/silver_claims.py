import logging
import sys
from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from py4j.protocol import Py4JJavaError
from utils import read_from_gcs, write_to_bq, write_to_gcs, BRONZE_PATH, SILVER_PATH

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

def main():
    spark = None
    try:
        spark = SparkSession.builder.appName("silver_claims").getOrCreate()
        logger.info("SparkSession started")

        df = read_from_gcs(spark, f"{BRONZE_PATH}/claims")

        if df is None or df.rdd.isEmpty():
            logger.warning("No data found in bronze claims — skipping")
            return

        logger.info(f"Read {df.count()} rows from bronze claims")

        # Quarantine
        quarantine = df.filter(
            F.col("claim_id").isNull() |
            F.col("patient_id").isNull() |
            F.col("provider_id").isNull()
        ).withColumn("quarantine_reason", F.lit("Null in mandatory field")) \
         .withColumn("quarantine_timestamp", F.current_timestamp())

        quarantine_count = quarantine.count()
        if quarantine_count > 0:
            logger.warning(f"{quarantine_count} rows quarantined due to null mandatory fields")
            write_to_bq(quarantine, "quarantine_claims")
        else:
            logger.info("No rows quarantined")

        # Filter valid rows
        df = df.filter(
            F.col("claim_id").isNotNull() &
            F.col("patient_id").isNotNull() &
            F.col("provider_id").isNotNull()
        )

        if df.rdd.isEmpty():
            logger.warning("All rows were quarantined — nothing to process")
            return

        # Fill billed_amount with median per procedure_code
        logger.info("Imputing billed_amount with median per procedure_code")
        medians = df.groupBy("procedure_code").agg(
            F.percentile_approx("billed_amount", 0.5).alias("median_per_code")
        )
        df = df.join(medians, "procedure_code", "left")
        df = df.withColumn(
            "billed_amount",
            F.coalesce(F.col("billed_amount"), F.col("median_per_code"))
        ).drop("median_per_code")

        # Global median fallback
        logger.info("Applying global median fallback for billed_amount")
        global_median = df.agg(
            F.percentile_approx("billed_amount", 0.5).alias("global_median")
        )
        df = df.crossJoin(global_median)
        df = df.withColumn(
            "billed_amount",
            F.coalesce(F.col("billed_amount"), F.col("global_median"))
        ).drop("global_median")

        # Fill nulls
        df = df.fillna({"diagnosis_code": "UNKNOWN", "procedure_code": "UNKNOWN"})

        # Deduplicate
        before_dedup = df.count()
        df = df.dropDuplicates(["claim_id"])
        after_dedup = df.count()
        if before_dedup != after_dedup:
            logger.warning(f"Dropped {before_dedup - after_dedup} duplicate claim_ids")

        # Fix types
        df = df.withColumn("date", F.to_date(F.col("date"))) \
               .withColumn("billed_amount", F.col("billed_amount").cast("double"))

        # Standardize text
        df = df.withColumn("diagnosis_code", F.upper(F.trim(F.regexp_replace("diagnosis_code", "[^a-zA-Z0-9]", "")))) \
               .withColumn("procedure_code", F.upper(F.trim(F.regexp_replace("procedure_code", "[^a-zA-Z0-9]", "")))) \
               .withColumn("claim_id", F.trim(F.col("claim_id"))) \
               .withColumn("patient_id", F.trim(F.col("patient_id"))) \
               .withColumn("provider_id", F.trim(F.col("provider_id")))

        write_to_gcs(df, f"{SILVER_PATH}/claims")
        write_to_bq(df, "silver_claims")

        logger.info(f"silver_claims done: {df.count()} rows")

    except Py4JJavaError as e:
        logger.error(f"Spark/Java error in silver_claims: {e.java_exception}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error in silver_claims: {e}", exc_info=True)
        sys.exit(1)
    finally:
        if spark:
            spark.stop()
            logger.info("SparkSession stopped")

if __name__ == "__main__":
    main()