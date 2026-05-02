import pandas as pd
from datetime import datetime

# Read bronze
df = pd.read_csv("data/bronze/bronze_providers_raw.csv")

# Quarantine & handle missing values
mandatory_cols = ["provider_id", "doctor_name", "specialty"]

df_quarantine = df[df[mandatory_cols].isnull().any(axis=1)].copy()
df_quarantine["quarantine_reason"] = "Null in mandatory field"
df_quarantine["quarantine_timestamp"] = datetime.now()
df_quarantine.to_csv("data/quarantine/providers_quarantine.csv", index=False)
print(f"Providers quarantine rows: {len(df_quarantine)}")

df = df.dropna(subset=mandatory_cols)
df["location"] = df["location"].fillna("UNKNOWN")

# Remove duplicates
df = df.drop_duplicates(subset=["provider_id"])

# Standardize data
df["provider_id"] = df["provider_id"].str.strip()
df["doctor_name"] = df["doctor_name"].str.title().str.strip()
df["specialty"] = df["specialty"].str.title().str.strip()
df["location"] = df["location"].str.title().str.strip()

# Save silver
df.to_csv("data/silver/silver_providers.csv", index=False)
print(f"silver_providers rows: {len(df)}")