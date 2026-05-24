# 🏥 AI-Powered Claim Denial Prevention & Remediation System

An end-to-end intelligent healthcare platform designed to predict, explain, and suggest remediations for healthcare claim denials *before* they are submitted to insurance payers. The system combines rule-based validation, predictive machine learning (XGBoost), explainable AI (SHAP), dynamic policy document retrieval (RAG), and generative AI agent orchestration (GPT-4o-mini) to minimize revenue loss, reduce manual rework, and streamline medical billing operations.

---

## 🚀 Key Capabilities

1.  **Deterministic Rule Pre-Screening**: Validates claims against 9 core referential and financial integrity rules (e.g., non-empty patient/provider IDs, positive billed amounts, correct cost ratios) before executing heavy ML processing.
2.  **Predictive ML Risk Scoring**: Leverages a production-grade XGBoost binary classification model (hosted on Databricks Model Serving, with local container fallbacks) to score the probability of a claim being denied.
3.  **Explainable AI (SHAP)**: Uses XGBoost's native SHAP (Shapley Additive exPlanations) values to extract the top 2 feature contributors responsible for high-risk flags, making model decisions human-interpretable.
4.  **Retrieval-Augmented Generation (RAG)**: Generates query embeddings using OpenAI's `text-embedding-3-small` to retrieve context-specific insurance policies from a Databricks Vector Search index (`rag.embeddings.rag_chunks_index`) based on SHAP explanations.
5.  **Agentic Remediation Planning**: Synthesizes rule failures, ML risk scores, SHAP explanations, and RAG-retrieved policies via a GPT-4o-mini agent to generate a step-by-step, actionable remediation summary.
6.  **Batch & Single Claim Processing**: Dashboard allows users to submit a single claim ID or upload bulk CSV claim files for batch analysis.
7.  **Data Export Options**: Supports exporting analyzed results to local devices in CSV (Excel-compatible) or JSON formats for medical billing workflows.

---

## 🏗️ System Architecture

The platform spans three primary tiers:

*   **Frontend Dashboard (Next.js)**: Built using Next.js 16, React 19, Tailwind CSS 4, and shadcn/ui. Handles user authentication via Google OAuth (NextAuth) with a whitelisted email filter and triggers background predictive pipelines.
*   **Backend Orchestrator API (FastAPI)**: Serves the `/predict` endpoint, coordinates the AI/ML pipeline, decodes JWT payloads for HIPAA-compliant structured audit logs, and handles communication with Databricks and OpenAI.
*   **Data Lakehouse & ML Platform (Databricks + GCP)**: Utilizes a Medallion Lakehouse architecture (Bronze ➔ Silver ➔ Gold feature tables) to store clean features, register models with MLflow, and index policy files via Databricks Vector Search.

### Architecture Options & Cost Documentation
The system supports two design variants located in `Project/docs`:
*   **v1 (Databricks-Centric)**: Runs Spark-based ETLs via Delta Live Tables (DLT), model serving via MLflow endpoints, and vector search on Databricks. Detail is documented in [architecture_cost_report.md](Project/docs/architecture_cost_report.md).
*   **v2 (AWS-Native Cost Optimized)**: Designed for small-to-midsize hospitals, swapping Databricks for AWS Glue, S3 Delta Lake, EC2 model runs, and FAISS vector indices, achieving ~60% cost reduction. Detail is documented in [cost analysis v2.md](Project/docs/cost%20analysis%20v2.md).

---

## 📂 Repository Structure

```text
.
├── Assignment/                  # HIPAA compliance studies and demos
│   ├── Implementation-1/        # HTML/CSS/JS browser demo of the HIPAA Privacy Rule
│   │   └── HIPAA_Privacy_Rule_Demo_Guide.md
│   ├── Implementation-2/        # Python Jupyter Notebook demo of HIPAA Security Rules
│   │   └── HIPAA_Privacy_Rule_Demo.ipynb
│   ├── Privacy Rule.md          # Privacy compliance scenario definitions
│   ├── Security Rule.md         # Security compliance scenario definitions
│   ├── hipaa.md                 # Foundational HIPAA rule overview
│   └── hipaa_implementation.md  # Core plan for HIPAA technical safeguards
├── Project/                     # Primary application code
│   ├── api/                     # FastAPI backend orchestration service
│   │   ├── pipeline/            # Sequential AI pipeline stages
│   │   │   ├── agent.py         # GPT-4o-mini remediation agent
│   │   │   ├── ml_scoring.py    # Production XGBoost (serving + fallback local model)
│   │   │   ├── ml_scoring_db.py # Local fallback model-only scoring module
│   │   │   ├── rag.py           # Embeddings generation and vector search query client
│   │   │   ├── rule_check.py    # Rule validation against Databricks SQL tables
│   │   │   ├── rule_check_db.py # Duplicate backup of rule checker
│   │   │   └── shap_explainer.py# Native XGBoost SHAP contributor extractor
│   │   ├── Dockerfile           # Backend containerization for GCP Cloud Run
│   │   ├── main.py              # API application entry point, routing, and audit logs
│   │   ├── models.py            # Pydantic validation models for request/response
│   │   └── requirements.txt     # Python requirements (uvicorn, fastapi, xgboost, etc.)
│   ├── architectures/           # High-Level (HLA) and Low-Level (LLA) diagrams
│   ├── docs/                    # Technical designs, prompt libraries, and notebooks
│   │   ├── architecture_cost_report.md # Databricks GCP deployment and cost analysis
│   │   ├── cost analysis v2.md         # AWS Glue/FAISS alternative cost analysis
│   │   ├── diag_prompts.md             # Visual diagram prompts for Lucidchart
│   │   └── notebook_explanation.md     # Cell-by-cell walkthrough of training code
│   ├── frontend/                # Next.js frontend dashboard
│   │   ├── app/                 # Next.js App Router (layout, logins, styles)
│   │   ├── components/          # React layout and 57 custom shadcn/ui components
│   │   │   └── dashboard/       # 6 specialized dashboard components
│   │   ├── hooks/               # Custom mobile and toast React hooks
│   │   ├── lib/                 # Tailwind class merges and typescript types
│   │   ├── Dockerfile           # Standalone multi-stage production Docker build
│   │   ├── proxy.ts             # NextAuth middleware route proxy config
│   │   ├── components.json      # shadcn configuration
│   │   └── tsconfig.json        # TypeScript configuration
│   ├── Pipelines/               # Data engineering pipelines
│   │   ├── DAG/                 # Airflow workflow DAGs
│   │   │   └── claims_etl_dag.py# Dataproc Serverless Airflow orchestrator script
│   │   ├── ETL/                 # Manual PySpark ETL scripts (Bronze/Silver/Gold)
│   │   ├── ETL_DB/              # Databricks Delta Live Tables (DLT) implementations
│   │   ├── Rag Indexing/        # Document loaders and vector search indexers
│   │   │   ├── rag_index.py     # UC Volumes indexing script
│   │   │   └── rag_index_gcs.py # Google Cloud Storage indexing script
│   │   └── workflow.yaml        # Pipeline workflow definitions
│   ├── scripts/                 # Model building and testing scripts
│   │   ├── ML Model.py          # End-to-end ML training notebook (LR vs XGBoost)
│   │   ├── explainer.ipynb.ipynb# Jupyter notebook verifying SHAP values
│   │   ├── setup.ipynb.ipynb    # MLflow project tracking setup notebook
│   │   └── testbook.ipynb.ipynb # Basic ML model smoke test notebook
│   ├── Detailed_Project_Document.docx # Detailed project document
│   ├── mindmap.md               # Visual directory map and module layout
│   └── week-1.md                # Phase 1 initialization plan
├── data/                        # Datasets (Medallion layers)
│   ├── bronze/                  # Raw CSV files with intentional null values
│   ├── silver/                  # Cleaned CSV files (imputations applied)
│   ├── gold/                    # Target local gold folder (generated dynamically)
│   ├── policies/                # 6 Insurance policy PDF rules for RAG context
│   ├── quarantine/              # CSV records rejected due to validation errors
│   ├── synthetic/               # ~5K rows labeled claim dataset (used to train ML)
│   └── test.csv                 # 12-row smoke test dataset
├── assumptions.md               # Core assumptions of the project
└── README.md                    # Root project documentation (this file)
```

---

## 💻 Tech Stack Summary

*   **Frontend**: Next.js 16.2.6 (App Router), React 19.2.4, Tailwind CSS 4.2.0, shadcn/ui, NextAuth.js 4.24.14 (Google OAuth).
*   **Backend**: FastAPI, Pydantic, Uvicorn, Pandas, NumPy, XGBoost, Scikit-Learn, MLflow.
*   **Orchestration & Data Platforms**: GCP Dataproc Serverless, Apache Airflow, Databricks Delta Live Tables, Delta Lake, Unity Catalog, OpenAI API (`text-embedding-3-small`, `gpt-4o-mini`).

---

## 🛠️ Installation & Configuration

### 1. API Backend Setup

Navigate to the API folder, activate your virtual environment, and install package dependencies:

```bash
cd Project/api
python -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate
pip install -r requirements.txt
```

Create a `.env` configuration file in `Project/api` containing your service tokens:

```ini
DATABRICKS_HOST=https://<your-databricks-workspace-url>
DATABRICKS_TOKEN=dapi...
DATABRICKS_HTTP_PATH=/sql/1.0/warehouses/...
OPENAI_API_KEY=sk-proj-...
DATABRICKS_MODEL_SERVING_URL=https://.../serving-endpoints/claim-denial-endpoint/invocations
DATABRICKS_VECTOR_SEARCH_URL=https://.../vector-search-index/rag.embeddings.rag_chunks_index
```

### 2. Frontend Next.js Setup

Navigate to the frontend directory, install package dependencies, and create a `.env.production` or `.env.local` file:

```bash
cd ../frontend
npm install --legacy-peer-deps
# or
pnpm install
```

Set up your environment variables:

```ini
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXTAUTH_URL=http://localhost:3000
NEXTAUTH_SECRET=your-32-character-secret
GOOGLE_CLIENT_ID=your-google-oauth-client-id
GOOGLE_CLIENT_SECRET=your-google-oauth-client-secret
ALLOWED_EMAILS=comma,separated,whitelisted,user,emails
```

---

## 🚀 Running the Platform

### 1. Start the API Service

Ensure your virtual environment is active in the `Project/api` folder:

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```
*Browse API endpoints and interactive Swagger schemas at [http://localhost:8000/docs](http://localhost:8000/docs).*

### 2. Start the Frontend App

From the `Project/frontend` folder:

```bash
npm run dev
# or
pnpm dev
```
*Access the interactive portal at [http://localhost:3000](http://localhost:3000).*

---

## 🧪 Operational Workflow

1.  **Authentication**: Securely sign in through Google OAuth. If running locally, next-auth handles whitelisting or falls back to a development session when credentials are blank.
2.  **Submit Claims**:
    *   **Single Input**: Type or paste a claim ID (e.g., `CLM-1001`) to analyze a single record.
    *   **Batch CSV Input**: Upload a `.csv` file. The frontend parses the file, checking for a `claim_id` column header (as assumed in [assumptions.md](assumptions.md)).
3.  **Run Analysis**: Click **Run AI Analysis** to dispatch requests to the backend.
4.  **Explore Analysis Details**:
    *   **Overall Metrics**: Visualize claims distribution across low-risk, high-risk, and failed categories.
    *   **Rule Failures**: Inspect claims that failed deterministic validations.
    *   **ML & SHAP Insights**: Examine high-risk claims showing exact percentages of denial probability along with the top 2 risk attributes extracted via SHAP.
    *   **RAG Policy Context**: Review relevant insurance clause excerpts dynamically fetched from policy docs.
    *   **AI Remediation Plans**: Read step-by-step suggestions generated by the LLM agent to correct and re-submit claims.
5.  **Export Results**: Export the completed batch logs to your local machine as **CSV** or **JSON** for billing system integration.
