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
        spark = SparkSession.builder.appName("silver_costs").getOrCreate()
        logger.info("SparkSession started")

        df = read_from_gcs(spark, f"{BRONZE_PATH}/costs")

        if df is None or df.rdd.isEmpty():
            logger.warning("No data found in bronze costs — skipping")
            return

        logger.info(f"Read {df.count()} rows from bronze costs")

        # Quarantine
        quarantine = df.filter(
            F.col("procedure_code").isNull() |
            F.col("average_cost").isNull() |
            F.col("expected_cost").isNull()
        ).withColumn("quarantine_reason", F.lit("Null in mandatory field")) \
         .withColumn("quarantine_timestamp", F.current_timestamp())

        quarantine_count = quarantine.count()
        if quarantine_count > 0:
            logger.warning(f"{quarantine_count} rows quarantined due to null mandatory fields")
            write_to_bq(quarantine, "quarantine_costs")
        else:
            logger.info("No rows quarantined")

        # Filter valid rows
        df = df.filter(
            F.col("procedure_code").isNotNull() &
            F.col("average_cost").isNotNull() &
            F.col("expected_cost").isNotNull()
        )

        if df.rdd.isEmpty():
            logger.warning("All rows were quarantined — nothing to process")
            return

        # Fill nulls
        df = df.fillna({"region": "UNKNOWN"})

        # Deduplicate
        before_dedup = df.count()
        df = df.dropDuplicates(["procedure_code"])
        after_dedup = df.count()
        if before_dedup != after_dedup:
            logger.warning(f"Dropped {before_dedup - after_dedup} duplicate procedure_codes")

        # Fix types
        df = df.withColumn("average_cost", F.col("average_cost").cast("double")) \
               .withColumn("expected_cost", F.col("expected_cost").cast("double"))

        # Standardize text
        df = df.withColumn("procedure_code", F.upper(F.trim(F.regexp_replace("procedure_code", "[^a-zA-Z0-9]", "")))) \
               .withColumn("region", F.initcap(F.trim(F.col("region"))))

        write_to_gcs(df, f"{SILVER_PATH}/costs")
        write_to_bq(df, "silver_costs")

        logger.info(f"silver_costs done: {df.count()} rows")

    except Py4JJavaError as e:
        logger.error(f"Spark/Java error in silver_costs: {e.java_exception}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error in silver_costs: {e}", exc_info=True)
        sys.exit(1)
    finally:
        if spark:
            spark.stop()
            logger.info("SparkSession stopped")

if __name__ == "__main__":
    main()