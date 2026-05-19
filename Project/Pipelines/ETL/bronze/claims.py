import sys
import logging

from pyspark.sql import SparkSession
from py4j.protocol import Py4JJavaError
from utils import read_csv_from_gcs, write_to_bq, write_to_gcs, RAW_PATH, BRONZE_PATH

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

def main():
    spark = None
    try:
        spark = SparkSession.builder.appName("bronze_claims").getOrCreate()
        logger.info("SparkSession started")

        df = read_csv_from_gcs(spark, f"{RAW_PATH}/claims.csv")

        if df is None or df.rdd.isEmpty():
            logger.warning("No data found in claims.csv — skipping write steps")
            return

        row_count = df.count()
        logger.info(f"Read {row_count} rows from claims.csv")

        write_to_gcs(df, f"{BRONZE_PATH}/claims")
        write_to_bq(df, "bronze_claims_raw")

        logger.info(f"bronze_claims done: {row_count} rows")

    except Py4JJavaError as e:
        logger.error(f"Spark/Java error in bronze_claims: {e.java_exception}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error in bronze_claims: {e}", exc_info=True)
        sys.exit(1)
    finally:
        if spark:
            spark.stop()
            logger.info("SparkSession stopped")

if __name__ == "__main__":
    main()