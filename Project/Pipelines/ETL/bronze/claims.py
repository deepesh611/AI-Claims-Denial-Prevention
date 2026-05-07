import dlt

# Configuration variables - Unity Catalog Volume
SOURCE_CATALOG = "data"
SOURCE_SCHEMA = "data"
SOURCE_VOLUME = "files"

# Target table name (catalog & schema are set in the DLT pipeline config)
TARGET_TABLE = "bronze_claims_raw"
VOLUME_PATH = f"/Volumes/{SOURCE_CATALOG}/{SOURCE_SCHEMA}/{SOURCE_VOLUME}"

@dlt.table(
    name=TARGET_TABLE,
    comment="Bronze layer: Consolidated claims data from CSV files"
)
def create_bronze_table():
    return (
        spark.readStream
        .format("cloudFiles")
        .option("cloudFiles.format", "csv")
        .option("header", "true")
        .option("cloudFiles.inferColumnTypes", "true") # Tells Auto Loader to infer schema
        .load(f"{VOLUME_PATH}/*claims*.csv")
    )
