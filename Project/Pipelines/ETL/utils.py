import logging
from py4j.protocol import Py4JJavaError

GCS_BUCKET  = "ai-claims-denial-data"
BQ_PROJECT  = "ai-claims-denial-prediction"
BQ_DATASET  = "claims_data"

RAW_PATH    = f"gs://{GCS_BUCKET}/raw"
BRONZE_PATH = f"gs://{GCS_BUCKET}/bronze"
SILVER_PATH = f"gs://{GCS_BUCKET}/silver"

logger = logging.getLogger(__name__)

def write_to_bq(df, table_name, mode="overwrite"):
    try:
        df.write \
            .format("bigquery") \
            .option("table", f"{BQ_PROJECT}.{BQ_DATASET}.{table_name}") \
            .option("temporaryGcsBucket", GCS_BUCKET) \
            .mode(mode) \
            .save()
        logger.info(f"Successfully wrote to BQ table: {table_name}")
    except Py4JJavaError as e:
        logger.error(f"BQ write failed for table '{table_name}': {e.java_exception}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error writing to BQ table '{table_name}': {e}")
        raise


def write_to_gcs(df, path, fmt="parquet", mode="overwrite"):
    try:
        df.write.mode(mode).format(fmt).save(path)
        logger.info(f"Successfully wrote {fmt} to GCS: {path}")
    except Py4JJavaError as e:
        logger.error(f"GCS write failed at '{path}': {e.java_exception}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error writing to GCS at '{path}': {e}")
        raise


def read_from_gcs(spark, path, fmt="parquet"):
    try:
        df = spark.read.format(fmt).load(path)
        logger.info(f"Successfully read {fmt} from GCS: {path}")
        return df
    except Py4JJavaError as e:
        logger.error(f"GCS read failed at '{path}': {e.java_exception}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error reading from GCS at '{path}': {e}")
        raise


def read_csv_from_gcs(spark, path):
    try:
        df = spark.read \
            .option("header", True) \
            .option("inferSchema", True) \
            .csv(path)
        logger.info(f"Successfully read CSV from GCS: {path}")
        return df
    except Py4JJavaError as e:
        logger.error(f"CSV read failed at '{path}': {e.java_exception}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error reading CSV at '{path}': {e}")
        raise