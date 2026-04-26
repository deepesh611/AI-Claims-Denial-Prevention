# AI-Powered Claim Denial Prevention System
## Architecture & Cost Analysis Report — v1 (Databricks)

---

## 1. System Overview

The AI-Powered Claim Denial Prevention & Remediation System is designed to predict insurance claim denials before submission, explain the reasons, and suggest fixes. The primary users are **billing team analysts** who review claims flagged as high-risk.

---

## 2. Architecture — v1 (Databricks Stack)

### 2.1 High Level Architecture

The system follows a layered architecture deployed on AWS, with all sensitive PHI data isolated inside a private VPC.

```
User (Billing Team)
      ↓ HTTPS
AWS VPC
  ├── Public Subnet
  │     ├── Application Load Balancer (SSL termination)
  │     └── Streamlit Dashboard
  └── Private Subnet
        ├── AWS API Gateway (JWT verification, rate limiting)
        ├── FastAPI Service (RBAC enforcement)
        ├── AI Layer
        │     ├── ML Model — XGBoost (denial probability)
        │     ├── RAG Retriever (policy retrieval from Vector DB)
        │     └── AI Agent Orchestrator (fix plan generation)
        └── Data Layer (S3 + Databricks)
              ├── Bronze Delta Tables (raw data)
              ├── Silver Delta Tables (cleaned, joined)
              ├── Gold Delta Tables (ML features)
              └── Vector DB on S3 (policy embeddings)

Outside VPC
  └── AWS Cognito (OAuth 2.0 authentication, JWT issuance)
```

### 2.2 Component Breakdown

#### Authentication & Access
- **AWS Cognito** — OAuth 2.0 provider. Issues JWT tokens on login. Lives outside the VPC as a managed AWS service.
- **JWT tokens** — carry user identity, role, and expiry. Validated by API Gateway on every request without calling Cognito each time.
- **RBAC roles** — enforced at two levels: FastAPI (endpoint access) and Databricks Unity Catalog (table/row level).

| Role | Access |
|---|---|
| billing_analyst | Own claims only, masked patient IDs |
| admin | Full data access |
| auditor | Read only, no PII fields |

#### Public Subnet
- **Application Load Balancer (ALB)** — single entry point into the VPC. Handles SSL termination. All traffic is HTTPS only. Performs health checks on downstream services.
- **Streamlit Dashboard** — claims review UI for billing team. Displays risk score, denial reason, and remediation steps per claim.

#### Private Subnet
- **AWS API Gateway** — rate limiting, request throttling, JWT signature verification against Cognito.
- **FastAPI Service** — extracts role from JWT claims, enforces RBAC, scopes queries to allowed data only. Returns 403 on unauthorized access.
- **AI Agent Orchestrator** — coordinates ML Model, RAG Retriever, and AI Agent. Aggregates outputs into a single response.

#### AI Layer
- **ML Model (XGBoost)** — trained on Gold layer features. Outputs a denial probability score (0–1).
- **RAG Retriever** — retrieves relevant insurance policy rules from Vector DB using semantic search. Provides policy-backed explanation for the predicted denial.
- **AI Agent** — combines ML score + RAG output + business rules to generate a prioritized fix recommendation for the billing analyst.

#### Data Layer
- **Databricks** — runs all ETL pipelines (Bronze → Silver → Gold). Managed Spark compute. Unity Catalog for access control and data lineage.
- **Bronze Delta Tables** — raw ingested CSVs with ingestion timestamp and source file tracked. No transformations.
- **Silver Delta Tables** — cleaned, deduplicated, joined across claims, providers, diagnosis, and cost datasets.
- **Gold Delta Tables** — feature-engineered, ML-ready dataset. Includes provider risk score, diagnosis complexity, claim amount vs benchmark, claim frequency.
- **Vector DB on S3** — stores policy document embeddings for RAG retrieval.
- **S3 + AWS KMS** — all Delta tables stored on S3 with SSE-KMS encryption. Keys managed by AWS KMS. IAM roles control access — no passwords, role-based trust only.

### 2.3 Security Architecture

| Layer | Mechanism |
|---|---|
| Network | VPC isolation, no public internet access to private subnet |
| Transit | TLS 1.2+ (HTTPS) on all external traffic |
| Storage | AES-256 via SSE-KMS on all S3 data |
| Authentication | OAuth 2.0 via AWS Cognito |
| Authorization | JWT + RBAC at API layer and data layer |
| Audit | AWS CloudTrail logs all KMS key access and API calls |
| Key management | AWS KMS — automatic key rotation, IAM-based access |

---

## 3. Data Flow

1. Billing analyst logs in → Cognito issues JWT token via OAuth 2.0
2. Analyst submits claim for review via Streamlit dashboard
3. Dashboard sends REST request with JWT in header → ALB (HTTPS)
4. ALB forwards to API Gateway → JWT verified against Cognito
5. FastAPI extracts role from JWT → RBAC check applied
6. FastAPI queries Gold layer via Databricks (Unity Catalog enforces row-level access)
7. Features passed to AI Agent Orchestrator
8. Orchestrator calls ML Model (denial score) + RAG Retriever (policy rules) in parallel
9. AI Agent combines outputs → generates fix plan
10. Result returned to FastAPI → Streamlit dashboard
11. Billing analyst sees: risk score, denial reason, fix steps

---

## 4. Data Sources

| File | Description |
|---|---|
| claims_1000.csv | Claim ID, patient, provider, diagnosis code, procedure code, billed amount, date |
| providers_1000.csv | Provider ID, doctor name, specialty, location |
| diagnosis.csv | Diagnosis code, category, severity |
| cost.csv | Procedure code, average cost, expected cost, region |

All files ingested generically using wildcard path patterns — scales from 1K to 1M+ rows without code changes.

---

## 5. Cost Analysis

### 5.1 Assumptions

| Parameter | Scenario A | Scenario B |
|---|---|---|
| User type | Billing team | Billing team |
| Concurrent users | 10 | 50 |
| Claims processed/month | 10,000 | 200,000 |
| Availability | Business hours (8x5) | Business hours (8x5) |
| Org type | Small hospital | Large hospital network |

### 5.2 Monthly Cost Estimate

| Service | Scenario A | Scenario B | Notes |
|---|---|---|---|
| ALB | ~$20 | ~$25 | Base + per request |
| AWS Cognito | Free | Free | Free up to 50K MAUs |
| AWS API Gateway | ~$5 | ~$30 | $3.50 per 1M requests |
| FastAPI on EC2 | ~$30 | ~$80 | t3.medium → t3.large + auto-scale |
| Databricks | ~$150 | ~$500 | Biggest cost driver |
| S3 + AWS KMS | ~$10 | ~$30 | Storage + KMS API calls |
| ML inference on EC2 | ~$15 | ~$90 | t3.medium → r5.large |
| Vector DB on S3 | ~$5 | ~$15 | Self-hosted embeddings |
| **Total** | **~$235/month** | **~$770/month** | |

### 5.3 Cost Breakdown by Category

| Category | Scenario A | Scenario B |
|---|---|---|
| Compute (EC2 + Databricks) | ~$195 (83%) | ~$670 (87%) |
| Networking (ALB + API GW) | ~$25 (11%) | ~$55 (7%) |
| Storage (S3 + KMS) | ~$15 (6%) | ~$45 (6%) |

### 5.4 Key Cost Observations

**Databricks is 60-65% of total cost** in both scenarios (~$150/month Scenario A, ~$500/month Scenario B). This is the single largest cost driver.

**Cost scales ~3x from Scenario A to B** despite a 5x increase in users and 20x increase in claims. This is because Databricks clusters can handle increased load with more workers rather than requiring a full architectural change.

**Cognito is effectively free** for both scenarios — the billing team user count falls well within the free tier.

### 5.5 Cost Optimization Opportunities

| Optimization | Potential Saving | Complexity |
|---|---|---|
| Replace Databricks with AWS Glue + EMR Serverless | ~$100-400/month | Medium |
| Auto-terminate Databricks clusters when idle | ~$50-100/month | Low |
| Use EC2 Spot instances for ML inference | ~$40-60/month | Low |
| Drop API Gateway, use ALB routing only | ~$5-30/month | Low |
| Use S3 Intelligent Tiering for cold data | ~$5-10/month | Low |

**Recommended v2 stack** (replacing Databricks with AWS Glue):

| Service | Scenario A | Scenario B |
|---|---|---|
| AWS Glue ETL | ~$20 | ~$120 |
| EC2 for ML + FastAPI | ~$45 | ~$170 |
| ALB + S3 + KMS + Cognito | ~$35 | ~$55 |
| **Total** | **~$100/month** | **~$345/month** |

Switching to Glue saves approximately **$135/month (Scenario A)** and **$425/month (Scenario B)** while maintaining the same medallion architecture and data flow.

---

## 6. Tools for Cost Monitoring

| Tool | Purpose | Cost |
|---|---|---|
| AWS Pricing Calculator | Pre-deployment estimation | Free |
| AWS Cost Explorer | Post-deployment spend tracking | Free |
| AWS Budgets | Spend alerts and thresholds | Free (first 2 budgets) |
| Databricks Cost Dashboard | DBU consumption per cluster/job | Free (built-in) |

---

## 7. Summary

| | Scenario A | Scenario B |
|---|---|---|
| Users | 10 billing analysts | 50 billing analysts |
| Claims/month | 10,000 | 200,000 |
| Monthly cost (v1 Databricks) | ~$235 | ~$770 |
| Monthly cost (v2 Glue) | ~$100 | ~$345 |
| Primary cost driver | Databricks (64%) | Databricks (65%) |
| Security standard | HIPAA-aligned | HIPAA-aligned |

The v1 Databricks architecture is production-ready and HIPAA-aligned but expensive for small-to-medium scale. Migrating the data layer to AWS Glue + EMR Serverless (v2) retains the same architecture and security posture while cutting costs by ~55-57%.
