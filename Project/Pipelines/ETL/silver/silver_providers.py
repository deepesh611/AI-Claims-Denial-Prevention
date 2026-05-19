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
        spark = SparkSession.builder.appName("silver_providers").getOrCreate()
        logger.info("SparkSession started")

        df = read_from_gcs(spark, f"{BRONZE_PATH}/providers")

        if df is None or df.rdd.isEmpty():
            logger.warning("No data found in bronze providers — skipping")
            return

        logger.info(f"Read {df.count()} rows from bronze providers")

        # Quarantine
        quarantine = df.filter(
            F.col("provider_id").isNull() |
            F.col("doctor_name").isNull() |
            F.col("specialty").isNull()
        ).withColumn("quarantine_reason", F.lit("Null in mandatory field")) \
         .withColumn("quarantine_timestamp", F.current_timestamp())

        quarantine_count = quarantine.count()
        if quarantine_count > 0:
            logger.warning(f"{quarantine_count} rows quarantined due to null mandatory fields")
            write_to_bq(quarantine, "quarantine_providers")
        else:
            logger.info("No rows quarantined")

        # Filter valid rows
        df = df.filter(
            F.col("provider_id").isNotNull() &
            F.col("doctor_name").isNotNull() &
            F.col("specialty").isNotNull()
        )

        if df.rdd.isEmpty():
            logger.warning("All rows were quarantined — nothing to process")
            return

        # Fill nulls
        df = df.fillna({"location": "UNKNOWN"})

        # Deduplicate
        before_dedup = df.count()
        df = df.dropDuplicates(["provider_id"])
        after_dedup = df.count()
        if before_dedup != after_dedup:
            logger.warning(f"Dropped {before_dedup - after_dedup} duplicate provider_ids")

        # Standardize text
        df = df.withColumn("provider_id", F.trim(F.col("provider_id"))) \
               .withColumn("doctor_name", F.initcap(F.trim(F.col("doctor_name")))) \
               .withColumn("specialty", F.initcap(F.trim(F.col("specialty")))) \
               .withColumn("location", F.initcap(F.trim(F.col("location"))))

        write_to_gcs(df, f"{SILVER_PATH}/providers")
        write_to_bq(df, "silver_providers")

        logger.info(f"silver_providers done: {df.count()} rows")

    except Py4JJavaError as e:
        logger.error(f"Spark/Java error in silver_providers: {e.java_exception}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error in silver_providers: {e}", exc_info=True)
        sys.exit(1)
    finally:
        if spark:
            spark.stop()
            logger.info("SparkSession stopped")

if __name__ == "__main__":
    main()