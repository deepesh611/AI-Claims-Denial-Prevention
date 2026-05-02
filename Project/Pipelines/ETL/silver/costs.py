import pandas as pd
from datetime import datetime

# Read bronze
df = pd.read_csv("data/bronze/bronze_costs_raw.csv")

# Quarantine & handle missing values
mandatory_cols = ["procedure_code", "average_cost", "expected_cost"]

df_quarantine = df[df[mandatory_cols].isnull().any(axis=1)].copy()
df_quarantine["quarantine_reason"] = "Null in mandatory field"
df_quarantine["quarantine_timestamp"] = datetime.now()
df_quarantine.to_csv("data/quarantine/costs_quarantine.csv", index=False)
print(f"Costs quarantine rows: {len(df_quarantine)}")

df = df.dropna(subset=mandatory_cols)
df["region"] = df["region"].fillna("UNKNOWN")

# Remove duplicates
df = df.drop_duplicates(subset=["procedure_code"])

# Fix data types
df["average_cost"] = pd.to_numeric(df["average_cost"], errors="coerce")
df["expected_cost"] = pd.to_numeric(df["expected_cost"], errors="coerce")

# Standardize data
df["procedure_code"] = df["procedure_code"].str.replace(r"[^a-zA-Z0-9]", "", regex=True).str.upper().str.strip()
df["region"] = df["region"].str.title().str.strip()

# Save silver
df.to_csv("data/silver/silver_costs.csv", index=False)
print(f"silver_costs rows: {len(df)}")