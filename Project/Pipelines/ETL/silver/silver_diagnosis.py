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
        spark = SparkSession.builder.appName("silver_diagnosis").getOrCreate()
        logger.info("SparkSession started")

        df = read_from_gcs(spark, f"{BRONZE_PATH}/diagnosis")

        if df is None or df.rdd.isEmpty():
            logger.warning("No data found in bronze diagnosis — skipping")
            return

        logger.info(f"Read {df.count()} rows from bronze diagnosis")

        # Quarantine
        quarantine = df.filter(
            F.col("diagnosis_code").isNull() |
            F.col("category").isNull() |
            F.col("severity").isNull()
        ).withColumn("quarantine_reason", F.lit("Null in mandatory field")) \
         .withColumn("quarantine_timestamp", F.current_timestamp())

        quarantine_count = quarantine.count()
        if quarantine_count > 0:
            logger.warning(f"{quarantine_count} rows quarantined due to null mandatory fields")
            write_to_bq(quarantine, "quarantine_diagnosis")
        else:
            logger.info("No rows quarantined")

        # Filter valid rows
        df = df.filter(
            F.col("diagnosis_code").isNotNull() &
            F.col("category").isNotNull() &
            F.col("severity").isNotNull()
        )

        if df.rdd.isEmpty():
            logger.warning("All rows were quarantined — nothing to process")
            return

        # Deduplicate
        before_dedup = df.count()
        df = df.dropDuplicates(["diagnosis_code"])
        after_dedup = df.count()
        if before_dedup != after_dedup:
            logger.warning(f"Dropped {before_dedup - after_dedup} duplicate diagnosis_codes")

        # Standardize text
        df = df.withColumn("diagnosis_code", F.upper(F.trim(F.regexp_replace("diagnosis_code", "[^a-zA-Z0-9]", "")))) \
               .withColumn("category", F.initcap(F.trim(F.col("category")))) \
               .withColumn("severity", F.initcap(F.trim(F.col("severity"))))

        write_to_gcs(df, f"{SILVER_PATH}/diagnosis")
        write_to_bq(df, "silver_diagnosis")

        logger.info(f"silver_diagnosis done: {df.count()} rows")

    except Py4JJavaError as e:
        logger.error(f"Spark/Java error in silver_diagnosis: {e.java_exception}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error in silver_diagnosis: {e}", exc_info=True)
        sys.exit(1)
    finally:
        if spark:
            spark.stop()
            logger.info("SparkSession stopped")

if __name__ == "__main__":
    main()