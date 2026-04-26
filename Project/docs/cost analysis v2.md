# AI-Powered Claim Denial Prevention System
## Cost-Effective Architecture Report — v2 (AWS Glue Stack)

---

## 1. Overview

This document defines the v2 cost-optimized architecture replacing Databricks with AWS Glue + EMR Serverless. The core system design, security posture, and data flow remain identical to v1. Only the data processing and compute layer changes.

Two variants are defined based on load:
- **Scenario A** — Small hospital, 10 users, 10K claims/month
- **Scenario B** — Large hospital network, 50 users, 200K claims/month

---

## 2. Architecture — Scenario A (Small Load)

### 2.1 Design Principles
- Single AZ deployment — low traffic, downtime tolerance acceptable during off-hours
- Shared EC2 instances where possible to minimize idle compute cost
- Serverless ETL — pay only when pipelines run, no idle Glue cost
- Self-hosted Vector DB — avoids managed service premium at low query volume

### 2.2 Component Stack

```
User (Billing Team — 10 users)
      ↓ HTTPS
AWS VPC (Single AZ)
  ├── Public Subnet
  │     ├── Application Load Balancer (SSL termination)
  │     └── EC2 t3.small — Streamlit Dashboard
  └── Private Subnet
        ├── AWS API Gateway (JWT verification, rate limiting)
        ├── EC2 t3.medium — FastAPI + ML Inference (shared)
        ├── AI Layer
        │     ├── XGBoost model (runs on FastAPI EC2)
        │     ├── RAG Retriever (runs on FastAPI EC2)
        │     └── AI Agent Orchestrator (runs on FastAPI EC2)
        └── Data Layer
              ├── AWS Glue — ETL pipelines (Bronze→Silver→Gold)
              ├── S3 — Parquet/Delta storage (SSE-KMS encrypted)
              ├── AWS Glue Data Catalog — table metadata
              └── S3 — Vector DB (self-hosted FAISS embeddings)

Outside VPC
  └── AWS Cognito (OAuth 2.0, JWT issuance)
  └── AWS KMS (key management)
  └── AWS CloudTrail (audit logging)
```

### 2.3 Key Design Decisions — Scenario A

**FastAPI + ML on same EC2:** At 10K claims/month and 10 users, a t3.medium handles both FastAPI requests and ML inference without contention. Separating them doubles EC2 cost unnecessarily.

**AWS Glue only (no EMR):** 10K claims/month is a light ETL workload. Glue serverless handles it comfortably. EMR adds overhead and cost not justified at this scale.

**Self-hosted FAISS on EC2:** Vector search at low query volume doesn't need a managed service. FAISS runs in-memory on the FastAPI EC2, adding negligible overhead.

**Single AZ:** Billing team works business hours only. Brief downtime during off-hours is acceptable. Multi-AZ doubles networking and instance costs.

---

## 3. Architecture — Scenario B (Large Load)

### 3.1 Design Principles
- Multi-AZ deployment — 50 users, higher downtime cost justifies redundancy
- Dedicated EC2 instances per service — avoid resource contention at scale
- Glue + EMR Serverless — heavy ETL jobs need more compute than Glue alone
- Managed Vector DB — OpenSearch handles concurrent semantic queries reliably

### 3.2 Component Stack

```
User (Billing Team — 50 users)
      ↓ HTTPS
AWS VPC (Multi-AZ)
  ├── Public Subnet
  │     ├── Application Load Balancer (SSL termination, Multi-AZ)
  │     └── EC2 t3.small — Streamlit Dashboard
  └── Private Subnet
        ├── AWS API Gateway (JWT verification, rate limiting)
        ├── EC2 Auto-Scaling Group — FastAPI (t3.large, 2-4 instances)
        ├── EC2 r5.large — ML Inference (dedicated, memory optimized)
        ├── AI Layer
        │     ├── XGBoost model (EC2 r5.large)
        │     ├── RAG Retriever (queries OpenSearch)
        │     └── AI Agent Orchestrator (EC2 r5.large)
        └── Data Layer
              ├── AWS Glue — ETL pipelines (Bronze→Silver→Gold)
              ├── EMR Serverless — heavy Spark jobs
              ├── S3 — Parquet/Delta storage (SSE-KMS encrypted)
              ├── AWS Glue Data Catalog — table metadata + access control
              └── Amazon OpenSearch Service — Vector DB (managed)

Outside VPC
  └── AWS Cognito (OAuth 2.0, JWT issuance)
  └── AWS KMS (key management)
  └── AWS CloudTrail (audit logging)
```

### 3.3 Key Design Decisions — Scenario B

**EC2 Auto-Scaling Group for FastAPI:** 50 concurrent users during business hours creates variable load. Auto-scaling ensures performance without over-provisioning 24/7.

**Dedicated r5.large for ML inference:** 200K claims/month means frequent model calls. Memory-optimized instance prevents ML workload from starving FastAPI requests.

**Glue + EMR Serverless:** 200K claims/month is a heavy ETL workload. Glue alone may throttle on large jobs. EMR Serverless handles burst processing and is still pay-per-use.

**Amazon OpenSearch for Vector DB:** At higher query volume, self-hosted FAISS becomes a bottleneck. OpenSearch provides managed scaling, HA, and fast semantic search.

**Multi-AZ:** 50 users across a hospital network means downtime has real operational impact. Multi-AZ ALB + EC2 ensures continuity.

---

## 4. Component Comparison — v1 vs v2

| Component | v1 (Databricks) | v2 Scenario A | v2 Scenario B |
|---|---|---|---|
| ETL engine | Databricks | AWS Glue | Glue + EMR Serverless |
| Table format | Delta (Databricks) | Parquet on S3 | Parquet on S3 |
| Metadata catalog | Unity Catalog | Glue Data Catalog | Glue Data Catalog |
| ML compute | Databricks cluster | EC2 t3.medium (shared) | EC2 r5.large (dedicated) |
| Streamlit | Databricks | EC2 t3.small | EC2 t3.small |
| Vector DB | S3 (self-hosted) | FAISS on EC2 | Amazon OpenSearch |
| Deployment | Single AZ | Single AZ | Multi-AZ |
| Access control | Unity Catalog RBAC | IAM + Glue catalog | IAM + Glue catalog |

---

## 5. Security — Unchanged from v1

| Layer | Mechanism |
|---|---|
| Network | VPC isolation, private subnet has no internet access |
| Transit | TLS 1.2+ (HTTPS) on all external traffic |
| Storage | SSE-KMS on all S3 data |
| Authentication | OAuth 2.0 via AWS Cognito |
| Authorization | JWT + RBAC at API and data layer |
| Audit | AWS CloudTrail |
| Key management | AWS KMS, automatic key rotation |

---

## 6. Cost Analysis — v2

### 6.1 Scenario A Monthly Estimate (10 users, 10K claims/month)

| Service | Cost | Notes |
|---|---|---|
| ALB | ~$20 | Base + per LCU |
| AWS Cognito | Free | Under 50K MAU free tier |
| API Gateway | ~$5 | Low request volume |
| EC2 t3.small (Streamlit) | ~$15 | ~$0.0208/hr, 8x5 only |
| EC2 t3.medium (FastAPI + ML) | ~$25 | ~$0.0416/hr, 8x5 only |
| AWS Glue ETL | ~$20 | Pay per DPU-hour, ~$0.44/DPU-hr |
| S3 + KMS | ~$10 | Storage + KMS API calls |
| FAISS on EC2 (shared) | $0 | Runs on FastAPI EC2 |
| CloudTrail | Free | Management events free |
| **Total** | **~$95/month** | |

### 6.2 Scenario B Monthly Estimate (50 users, 200K claims/month)

| Service | Cost | Notes |
|---|---|---|
| ALB (Multi-AZ) | ~$30 | Higher LCU usage |
| AWS Cognito | Free | Under 50K MAU free tier |
| API Gateway | ~$30 | Higher request volume |
| EC2 t3.small (Streamlit) | ~$15 | |
| EC2 t3.large Auto-Scaling (FastAPI) | ~$100 | 2-4 instances during business hours |
| EC2 r5.large (ML inference) | ~$90 | Memory optimized |
| AWS Glue ETL | ~$80 | More DPU hours at scale |
| EMR Serverless | ~$60 | Heavy Spark jobs only |
| S3 + KMS | ~$30 | More storage + API calls |
| Amazon OpenSearch | ~$80 | Managed vector search |
| CloudTrail | Free | |
| **Total** | **~$515/month** | |

### 6.3 v1 vs v2 Cost Comparison

| | Scenario A | Scenario B |
|---|---|---|
| v1 Databricks | ~$235/month | ~$770/month |
| v2 Glue stack | ~$95/month | ~$515/month |
| **Monthly saving** | **~$140/month** | **~$255/month** |
| **Annual saving** | **~$1,680/year** | **~$3,060/year** |

### 6.4 Cost Breakdown by Category — v2

**Scenario A:**

| Category | Cost | % |
|---|---|---|
| Compute (EC2) | ~$40 | 42% |
| ETL (Glue) | ~$20 | 21% |
| Networking (ALB + API GW) | ~$25 | 26% |
| Storage (S3 + KMS) | ~$10 | 11% |

**Scenario B:**

| Category | Cost | % |
|---|---|---|
| Compute (EC2) | ~$205 | 40% |
| ETL (Glue + EMR) | ~$140 | 27% |
| Networking (ALB + API GW) | ~$60 | 12% |
| Storage + OpenSearch | ~$110 | 21% |

---

## 7. Cost Monitoring Tools

| Tool | Purpose | Cost |
|---|---|---|
| AWS Pricing Calculator | Pre-deployment estimation | Free |
| AWS Cost Explorer | Post-deployment tracking | Free |
| AWS Budgets | Spend alerts | Free (first 2 budgets) |
| Infracost | Terraform-based cost estimation | Free (open source) |

---

## 8. Summary

| | Scenario A | Scenario B |
|---|---|---|
| Users | 10 billing analysts | 50 billing analysts |
| Claims/month | 10,000 | 200,000 |
| Availability | 8x5, Single AZ | 8x5, Multi-AZ |
| ETL engine | AWS Glue | Glue + EMR Serverless |
| Vector DB | FAISS on EC2 | Amazon OpenSearch |
| Monthly cost | ~$95 | ~$515 |
| Saving vs v1 | ~$140/month | ~$255/month |
| Security standard | HIPAA-aligned | HIPAA-aligned |

---
