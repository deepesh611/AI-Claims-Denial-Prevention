# AI-Powered Claim Denial Prevention & Remediation System
## Project Report

---

## Table of Contents

1. [Project Overview](#1-project-overview)
2. [System Architecture & AI Pipeline](#2-system-architecture--ai-pipeline)
3. [GCP Deployment & Cloud Services](#3-gcp-deployment--cloud-services)
4. [Databricks Pipelines, Endpoints & Services](#4-databricks-pipelines-endpoints--services)
5. [Cost Analysis: Databricks vs. GCP-Native](#5-cost-analysis-databricks-vs-gcp-native)
6. [Data Engineering — Medallion Architecture](#6-data-engineering--medallion-architecture)
7. [HIPAA Compliance Posture](#7-hipaa-compliance-posture)

---

## 1. Project Overview

The AI-Powered Claim Denial Prevention & Remediation System is a pre-submission insurance claims intelligence platform designed to predict, explain, and remediate healthcare claim denials before they are submitted to insurance payers. In the modern healthcare environment, claim denials are a massive source of revenue leakage and administrative overhead, requiring billing staff to manually review thousands of complex records. This system automates and simplifies that review by integrating a five-stage AI engine directly into the billing workflow: it executes rule-based validation, runs an ML risk-scoring model, identifies top risk drivers via SHAP explainability, performs semantic search to retrieve matching insurance policies (RAG), and generates a step-by-step remediation plan through a large language model. This entire automated pipeline is triggered via a single API call when billing analysts submit claim IDs or upload claim batches via an interactive web dashboard.

Deployed as containerized services on Google Cloud Platform (GCP) Cloud Run, the system utilizes Databricks on GCP as its secure backend data lakehouse and ML serving environment. By leveraging a high-performance, serverless SQL Warehouse for rule execution and model feature retrieval, and Unity Catalog for data governance, the platform ensures data security and role-based access. Claims are evaluated pre-submission, which empowers hospital billing teams to correct formatting issues, policy conflicts, and coding errors dynamically, reducing claim cycle times and accelerating reimbursement.

### Five-Stage AI Core

| Stage | Engine | Output |
|---|---|---|
| 1. Rule Validation | Databricks SQL query + Python logic | Pass / Fail (with specific failure reasons) |
| 2. ML Risk Scoring | XGBoost (Databricks Model Serving) | Denial probability (0–1), risk label (High/Low) |
| 3. SHAP Explainability | XGBoost native SHAP values | Top 2 risk factors per claim |
| 4. RAG Policy Retrieval | Local embeddings + Databricks Vector Search | Relevant policy clause + source document |
| 5. AI Agent Remediation | Locally hosted LLM / Agent Orchestration | Step-by-step fix recommendation |

---

## 2. System Architecture & AI Pipeline

### High-Level Flow

```
  ┌─────────────────────────────┐
  │   Billing Analyst (Browser) │
  └──────────────┬──────────────┘
                 │ HTTPS
                 ▼
  ┌──────────────────────────────┐
  │   Next.js Dashboard          │  ← GCP Cloud Run (Frontend)
  │   (Google OAuth via NextAuth)│
  └──────────────┬───────────────┘
                 │ POST /predict
                 ▼
  ┌──────────────────────────────┐
  │   FastAPI Backend            │  ← GCP Cloud Run (API)
  │   (Orchestrator + Audit Log) │
  └──────────────┬───────────────┘
                 │
    ┌─────────────┼─────────────────────────────────┐
    │             │                                  │
    ▼             ▼                                  ▼
┌────────┐  ┌──────────┐  ┌──────────┐  ┌────────────────┐
│ Rule   │  │ XGBoost  │  │ SHAP     │  │ RAG + Agent    │
│ Check  │  │ Scoring  │  │ Explainer│  │ (Embeddings +  │
│        │  │          │  │          │  │  Vector Search) │
└───┬────┘  └────┬─────┘  └────┬─────┘  └───────┬────────┘
    │            │              │                 │
    └────────────┴──────────────┴─────────────────┘
                        │
               Databricks on GCP
          (SQL Warehouse · Model Serving
           Unity Catalog · Vector Search)
```

### Pipeline Rules (Conditional Execution)

Not every stage runs for every claim:

- **Rule Check** runs on all submitted claims.
- **ML Scoring** runs only on claims that *pass* rule validation.
- **SHAP Explainer** runs only on claims scored as *High Risk* by the ML model.
- **RAG Retrieval** runs only on claims that have SHAP results.
- **AI Agent** runs on *all* claims, synthesizing whatever data is available for each.

This conditional design avoids unnecessary compute: a claim that fails basic rules never touches the ML model, and a low-risk claim never queries the vector database.

---

## 3. GCP Deployment & Cloud Services

### Services Used

| GCP Service | Role in This Project |
|---|---|
| **Cloud Run** | Hosts both the FastAPI backend (port 8080) and the Next.js frontend (port 3000) as serverless, stateless containers. |
| **Artifact Registry** | Stores the Docker images built from the API and frontend Dockerfiles. |
| **Cloud Storage (GCS)** | Stores raw CSV data files, schemas, and policy documents in a secure bucket (`ai-claims-denial-data`). |
| **Google OAuth (via NextAuth)** | Authenticates users through Google sign-in. The frontend enforces a strict analyst email whitelist via environment variables. |
| **Databricks on GCP** | Hosting environment for the data pipelines, delta tables, machine learning model registry, ML serving endpoint, and vector search. |

### Container Architecture

- **Backend** (`Project/api/Dockerfile`): Built using a lightweight Python image (`python:3.11-slim`) to run the FastAPI server, connecting to Databricks SQL Warehouse and Model Serving.
- **Frontend** (`Project/frontend/Dockerfile`): Built using a multi-stage Node build (`node:22-alpine`) utilizing Next.js standalone output mode for a highly optimized production footprint.

---

## 4. Databricks Pipelines, Endpoints & Services

The entire data, ML, and retrieval backend is consolidated on **Databricks on GCP**.

### 4.1 Unity Catalog — Schema & Tables

| Catalog.Schema | Table | Layer | Description |
|---|---|---|---|
| `main.bronze` | `bronze_claims` | Bronze | Raw claims with ingestion timestamp |
| `main.bronze` | `bronze_providers` | Bronze | Raw provider reference data |
| `main.bronze` | `bronze_diagnosis` | Bronze | Raw diagnosis codes |
| `main.bronze` | `bronze_costs` | Bronze | Raw procedure cost benchmarks |
| `main.silver` | `silver_claims` | Silver | Cleaned, deduplicated, imputed claims |
| `main.silver` | `silver_providers` | Silver | Standardized provider records |
| `main.silver` | `silver_diagnosis` | Silver | Standardized diagnosis codes |
| `main.silver` | `silver_costs` | Silver | Cleaned cost benchmarks |
| `main.gold` | `gold_claim_features` | Gold | Joined, feature-engineered ML-ready table |

### 4.2 Delta Live Tables (DLT) Pipeline & Jobs Compute

Data ingestion and feature preparation run directly on Databricks Spark clusters. A parallel implementation of the ETL exists as Databricks DLT notebooks in `Pipelines/ETL_DB/` containing built-in quality enforcement via `@dlt.expect_or_drop` decorators:

| Expectation | Table | Rule |
|---|---|---|
| `valid_claim_id` | silver_claims | `claim_id IS NOT NULL` |
| `valid_billed_amount` | silver_claims | `billed_amount > 0` |
| `valid_procedure_code` | silver_costs | `procedure_code IS NOT NULL` |
| `valid_diagnosis_code` | silver_diagnosis | `diagnosis_code IS NOT NULL` |

### 4.3 Model Serving Endpoint

| Property | Value |
|---|---|
| Endpoint name | `claim-denial-endpoint` |
| Model path | `models:/models.claims_denial.claim_denial_model/champion` |
| Model type | XGBoost binary classifier |
| Features (7) | `billed_amount`, `billed_vs_avg_cost`, `high_cost_flag`, `severity_score`, `specialty_idx`, `category_idx`, `location_idx` |
| Threshold | ≥ 0.5 → **High Risk**, < 0.5 → **Low Risk** |
| Fallback | If the serving endpoint is unreachable, the API loads the model locally from MLflow. |

### 4.4 Vector Search Index

| Property | Value |
|---|---|
| Index name | `rag.embeddings.rag_chunks_index` |
| Source documents | Insurance policy PDFs (billing, coding, fraud, severity, provider rules) |
| Chunking | 1000 characters, 200 character overlap |
| Embedding model | Self-hosted/local vector embedding engine |
| Retrieval | Top-1 most similar policy chunk per SHAP query |
| Columns returned | `source` (PDF filename), `text` (chunk content) |

### 4.5 SQL Warehouse

The backend API connects to a serverless Databricks SQL Warehouse to query the Gold feature table (`main.gold.gold_claim_features`) for rule validation and ML feature extraction.

### 4.6 MLflow Model Registry

Models are trained in Databricks notebooks (`scripts/ML Model.py`), logged to MLflow with metrics and signatures, and registered to Unity Catalog. The serving endpoint pulls from the `champion` alias.

---

## 5. Cost Analysis: Databricks vs. GCP-Native

This section estimates the monthly running costs of the current Databricks-first deployment and compares it with a proposed GCP-native replacement.

### 5.1 Key Assumptions

- **Locally Hosted AI Models**: The machine learning risk scoring (XGBoost), SHAP explainer, embeddings model, and LLM agent are run on dedicated cloud instances or self-hosted GPU endpoints rather than using external pay-per-token API endpoints. This converts variable LLM API billing into flat infrastructure compute.
- **Operating Hours**: The billing team operates on a standard business schedule (8 hours/day, 5 days/week, ~176 hours/month). Interactive instances and endpoints are configured to scale down or pause when idle.
- **Batch Processing**: Users supply claim IDs via CSV or manual entry. The backend retrieves pre-computed features from the Databricks Gold feature table using the SQL Warehouse, avoiding real-time feature engineering.
- **Regional Colocation**: All resources reside within the same GCP region to ensure zero cross-region data egress charges.

### 5.2 Load Scenarios

| Parameter | Scenario A (Small Hospital) | Scenario B (Large Hospital Network) |
|---|---|---|
| Concurrent users | 10 billing analysts | 50 billing analysts |
| Claims processed/month | 10,000 | 200,000 |
| Availability | Business hours (8×5) | Business hours (8×5) |

### 5.3 Current Stack — Databricks on GCP (Estimated Monthly Cost)

In the current stack, Databricks Spark jobs and Delta Live Tables handle all ETL pipelines and orchestrations.

| Service | Scenario A | Scenario B | Notes |
|---|---|---|---|
| Cloud Run (API + Frontend) | ~$30 | ~$80 | Scales to zero when idle |
| Databricks SQL Warehouse | ~$60 | ~$200 | Per-query serverless SQL compute |
| Databricks DLT / Jobs Compute | ~$65 | ~$200 | Spark ETL clusters and jobs orchestration |
| Databricks Model Serving | ~$25 | ~$80 | Per-request inference serving |
| Databricks Vector Search | ~$15 | ~$50 | Vector embedding index queries |
| GCS Storage | ~$5 | ~$15 | Raw data CSVs + Delta table storage |
| Locally Hosted LLM / Embeddings | ~$40 | ~$150 | Dedicated GPU/CPU instance compute |
| **Total** | **~$240/month** | **~$775/month** | |

> Databricks-specific services (SQL Warehouse + Jobs/DLT + Model Serving + Vector Search) account for **~$165/month (68%)** in Scenario A and **~$530/month (68%)** in Scenario B.

### 5.4 Proposed Stack — GCP-Native Replacement

This alternative architecture replaces the Databricks layer with native Google Cloud services:

| Databricks Service | GCP-Native Replacement | Rationale |
|---|---|---|
| SQL Warehouse | **BigQuery** | Serverless SQL engine with on-demand pricing and no idle cluster costs. |
| DLT / Jobs Compute | **Dataproc Serverless** + **GCP Workflows** | Run Spark jobs on-demand and orchestrate via serverless workflows. |
| Model Serving | **Vertex AI Prediction** | Managed model serving with auto-scaling to zero for XGBoost. |
| Vector Search | **Vertex AI Vector Search** | Serverless approximate nearest neighbor (ANN) vector database. |
| Unity Catalog | **BigQuery Datasets + IAM** | Dataset-level permissions and Google Cloud IAM roles. |

### 5.5 GCP-Native Estimated Monthly Cost

| Service | Scenario A | Scenario B | Notes |
|---|---|---|---|
| Cloud Run (API + Frontend) | ~$30 | ~$80 | Unchanged |
| BigQuery (queries + storage) | ~$15 | ~$60 | On-demand query pricing |
| Dataproc Serverless (ETL) | ~$20 | ~$70 | On-demand PySpark execution |
| GCP Workflows | ~$1 | ~$5 | Serverless step execution orchestration |
| Vertex AI Prediction | ~$15 | ~$50 | Serverless XGBoost inference hosting |
| Vertex AI Vector Search | ~$10 | ~$40 | Vector database hosting |
| GCS Storage | ~$5 | ~$15 | Unchanged |
| Locally Hosted LLM / Embeddings | ~$40 | ~$150 | Unchanged (same compute endpoints) |
| **Total** | **~$136/month** | **~$470/month** | |

### 5.6 Savings Summary

| | Scenario A | Scenario B |
|---|---|---|
| Databricks stack | ~$240/month | ~$775/month |
| GCP-native stack | ~$136/month | ~$470/month |
| **Monthly saving** | **~$104/month** | **~$305/month** |
| **Annual saving** | **~$1,248/year** | **~$3,660/year** |
| **Reduction** | **~43%** | **~39%** |

### 5.7 Trade-offs

| Advantage of Databricks | Advantage of GCP-Native |
|---|---|
| **Unified Workspace**: Single platform for collaborative notebooks, ETL pipelines, and ML experiments. | **Lower Cost**: Avoids Databricks licensing markup (DBUs) and cluster compute overhead. |
| **Delta Live Tables**: Built-in data quality metrics, expectations, and lineage out of the box. | **Zero Maintenance**: BigQuery and Dataproc Serverless require no cluster management. |
| **Unity Catalog**: Fine-grained data access control across SQL, Python, and ML artifacts. | **Native Integration**: Seamless security, deployment, and billing within a single GCP ecosystem. |

---

## 6. Data Engineering — Medallion Architecture

### Bronze Layer (Raw Ingestion)

Ingests raw CSV sources from GCS with no transformations; an `ingestion_timestamp` is appended:

- `claims.csv`: claim_id, patient_id, provider_id, diagnosis_code, procedure_code, billed_amount, date
- `providers.csv`: provider_id, doctor_name, specialty, location
- `diagnosis.csv`: diagnosis_code, category, severity
- `cost.csv`: procedure_code, average_cost, expected_cost, region

### Silver Layer (Cleaning & Standardization)

- Null values imputed: `billed_amount` to column median; `diagnosis_code`/`procedure_code` to `"UNKNOWN"`; costs to median; categories to `"UNKNOWN"`.
- Cleaned string fields (trimmed, uppercased).
- Duplicate rows removed.

### Gold Layer (Feature Engineering)

Joins claims, providers, diagnosis, and cost tables to construct feature records:

- `billed_vs_avg_cost` (`billed_amount / average_cost`)
- `high_cost_flag` (`1` if `billed_amount > expected_cost`, else `0`)
- `severity_score` (Ordinal encoding: LOW=1, MEDIUM=2, HIGH=3, CRITICAL=4)
- Provider risk scores, patient claim frequencies, and diagnosis volumes.

---

## 7. HIPAA Compliance Posture

The platform is designed to handle sensitive healthcare data in compliance with the HIPAA Security and Privacy Rules. This posture is maintained through several architectural and programmatic safeguards:

- **Secure Identity & Access Control**: NextAuth.js integrates Google OAuth 2.0 with a strict, server-managed email whitelist (`ALLOWED_EMAILS`). Users who are not pre-authorized billing analysts are blocked before any data is queried. Role-based access control (RBAC) is enforced at the API routing layer.
- **Protected Health Information (PHI) Minimization**: The frontend application does not accept or transmit patient identifiers (such as names, SSNs, or contact info) in API payloads. Users enter claim IDs; the backend queries the internal secure gold database for features, minimizing the surface area of public-facing PHI.
- **Encrypted Data Lifecycle**:
  - *In Transit*: All client-to-API and service-to-service communications are encrypted using TLS 1.2+ (HTTPS).
  - *At Rest*: Data stored in Google Cloud Storage and Databricks Delta tables is encrypted using AES-256 server-side encryption.
- **Immutable Transaction Audit Trails**: Every transaction processed by the `/predict` API is captured in structured JSON format. Audit records contain timestamps, analyst identifiers, client IP addresses, claims reviewed, and system operations. These logs are preserved in a secure, write-once storage location to support compliance auditing.
- **Granular Data Governance**: Databricks Unity Catalog governs data access. Data analysts and services are restricted to specific tables, rows, or columns according to the principle of least privilege, preventing unauthorized data leakage.

---

*Report finalized on 2026-05-24.*
