import pandas as pd
import numpy as np
from datetime import datetime

# Read bronze
df = pd.read_csv("data/bronze/bronze_claims_raw.csv")

# Quarantine & handle missing values
mandatory_cols = ["claim_id", "patient_id", "provider_id"]

df_quarantine = df[df[mandatory_cols].isnull().any(axis=1)].copy()
df_quarantine["quarantine_reason"] = "Null in mandatory field"
df_quarantine["quarantine_timestamp"] = datetime.now()
df_quarantine.to_csv("data/quarantine/claims_quarantine.csv", index=False)
print(f"Claims quarantine rows: {len(df_quarantine)}")

df = df.dropna(subset=mandatory_cols)

# Fill billed_amount with median per procedure_code
df["billed_amount"] = df.groupby("procedure_code")["billed_amount"].transform(
    lambda x: x.fillna(x.median())
)

# Global median fallback
global_median = df["billed_amount"].median()
df["billed_amount"] = df["billed_amount"].fillna(global_median)

# Fill non-mandatory nulls
df["diagnosis_code"] = df["diagnosis_code"].fillna("UNKNOWN")
df["procedure_code"] = df["procedure_code"].fillna("UNKNOWN")

# Remove duplicates
df = df.drop_duplicates(subset=["claim_id"])

# Fix data types
df["date"] = pd.to_datetime(df["date"], errors="coerce")
df["billed_amount"] = pd.to_numeric(df["billed_amount"], errors="coerce")

# Standardize data
df["diagnosis_code"] = df["diagnosis_code"].str.replace(r"[^a-zA-Z0-9]", "", regex=True).str.upper().str.strip()
df["procedure_code"] = df["procedure_code"].str.replace(r"[^a-zA-Z0-9]", "", regex=True).str.upper().str.strip()
df["claim_id"] = df["claim_id"].str.strip()
df["patient_id"] = df["patient_id"].str.strip()
df["provider_id"] = df["provider_id"].str.strip()

# Save silver
df.to_csv("data/silver/silver_claims.csv", index=False)
print(f"silver_claims rows: {len(df)}")