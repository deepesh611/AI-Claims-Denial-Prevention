import dlt

# Configuration variables - update these as needed
SOURCE_CATALOG = "data"
SOURCE_SCHEMA = "default"

TARGET_CATALOG = "bronze_catalog"
TARGET_SCHEMA = "bronze_schema"
TARGET_TABLE = "bronze_diagnosis"

# Create the target streaming table
dlt.create_streaming_table(
    name=f"{TARGET_CATALOG}.{TARGET_SCHEMA}.{TARGET_TABLE}",
    comment="Bronze layer: Consolidated diagnosis data from all tables with 'diagnosis' in the name"
)

# Get list of tables with "diagnosis" in the name
tables_with_diagnosis = [
    table.tableName 
    for table in spark.sql(f"SHOW TABLES IN {SOURCE_CATALOG}.{SOURCE_SCHEMA}").collect()
    if "diagnosis" in table.tableName.lower()
]

# Create an append flow for each table with "diagnosis" in the name
for table_name in tables_with_diagnosis:
    # Create a unique function for each append flow
    flow_name = f"append_{table_name}"
    
    @dlt.append_flow(
        target=f"{TARGET_CATALOG}.{TARGET_SCHEMA}.{TARGET_TABLE}",
        name=flow_name,
        comment=f"Append data from {SOURCE_CATALOG}.{SOURCE_SCHEMA}.{table_name}"
    )
    def create_append_flow(tbl=table_name):
        return (
            spark.readStream
            .table(f"{SOURCE_CATALOG}.{SOURCE_SCHEMA}.{tbl}")
        )
