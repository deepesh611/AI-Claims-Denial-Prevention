import pandas as pd
from datetime import datetime

# Read bronze
df = pd.read_csv("data/bronze/bronze_diagnosis_raw.csv")

# Quarantine & handle missing values
mandatory_cols = ["diagnosis_code", "category", "severity"]

df_quarantine = df[df[mandatory_cols].isnull().any(axis=1)].copy()
df_quarantine["quarantine_reason"] = "Null in mandatory field"
df_quarantine["quarantine_timestamp"] = datetime.now()
df_quarantine.to_csv("data/quarantine/diagnosis_quarantine.csv", index=False)
print(f"Diagnosis quarantine rows: {len(df_quarantine)}")

df = df.dropna(subset=mandatory_cols)

# Remove duplicates
df = df.drop_duplicates(subset=["diagnosis_code"])

# Standardize data
df["diagnosis_code"] = df["diagnosis_code"].str.replace(r"[^a-zA-Z0-9]", "", regex=True).str.upper().str.strip()
df["category"] = df["category"].str.title().str.strip()
df["severity"] = df["severity"].str.title().str.strip()

# Save silver
df.to_csv("data/silver/silver_diagnosis.csv", index=False)
print(f"silver_diagnosis rows: {len(df)}")