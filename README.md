# 🏥 AI-Powered Claim Denial Prevention & Remediation System

An end-to-end intelligent healthcare platform designed to predict, explain, and suggest remediations for healthcare claim denials *before* they are submitted to payers. By integrating a deterministic rule validation engine, machine learning, Explainable AI (SHAP), Retrieval-Augmented Generation (RAG), and Agentic LLM synthesis, this system helps healthcare providers minimize revenue loss, reduce manual rework, and streamline billing operations.

---

## 🚀 Key Features

*   **Deterministic Rule Validation**: Pre-screens claims for missing data, invalid fields, and basic referential integrity.
*   **Predictive ML Risk Scoring**: An XGBoost model evaluates claims that pass rule checks to predict the probability of denial (Low vs. High Risk).
*   **Explainable AI (SHAP)**: Extracts human-readable justifications (feature importances) using native XGBoost SHAP values for claims flagged as High Risk.
*   **Retrieval-Augmented Generation (RAG)**: Dynamically queries insurance and billing policy documents from a vector search database based on the specific risk factors of a claim.
*   **Agentic AI Remediation**: Synthesizes rule failures, ML risk scores, SHAP explanations, and RAG policies to generate actionable, step-by-step remediation plans using GPT-4o-mini.
*   **Interactive Dashboard**: A modern, responsive Next.js dashboard featuring Google OAuth, real-time single-claim/batch CSV analysis, summary metrics, and result exporting.
*   **Export Options**: Export analysis results directly to your device in CSV (Excel-compatible) or JSON formats for medical billing workflows.

---

## 🏗️ System Architecture

The platform spans across three integrated layers:

```
                  ┌──────────────────────────────┐
                  │      Next.js Frontend        │
                  │ (Tailwind 4 + shadcn/ui + JS)│
                  └──────────────┬───────────────┘
                                 │ POST /predict
                                 ▼
                  ┌──────────────────────────────┐
                  │       FastAPI Backend        │
                  │   (Orchestrator Service)     │
                  └──────────────┬───────────────┘
                                 │
     ┌───────────────────────────┼───────────────────────────┐
     ▼                           ▼                           ▼
┌──────────────┐          ┌──────────────┐            ┌──────────────┐
│  Rule Check  │          │  ML Scoring  │            │ RAG & Agent  │
│ (Databricks  │          │ (XGBoost on  │            │ (OpenAI Embs │
│  SQL query)  │          │ Databricks)  │            │ + Vector DB) │
└──────────────┘          └──────────────┘            └──────────────┘
```

1.  **Data Engineering (Medallion & Delta Lake)**:
    *   **Bronze**: Ingestion of raw claims, providers, diagnosis, and cost data.
    *   **Silver**: Data cleansing, duplicate removal, and median imputation.
    *   **Gold**: Feature engineering and joined ready-to-train datasets (`gold_claim_features`).
    *   *Orchestrated via Apache Airflow and Databricks Delta Live Tables (DLT).*
2.  **AI & ML Service Layer (FastAPI)**:
    *   Sequential processing flow: `rule_check` ➔ `ml_scoring` ➔ `shap_explainer` ➔ `rag` ➔ `agent`.
    *   Supports local machine learning fallbacks if Databricks Model Serving is unavailable.
3.  **Frontend Dashboard (Next.js)**:
    *   Interactive claim submission, real-time loading states, visual risk gauges, and responsive data export options.

---

## 📂 Repository Structure

```text
.
├── Assignment/               # HIPAA compliance study resources and web/notebook demos
├── Project/
│   ├── api/                  # FastAPI backend server
│   │   ├── pipeline/         # Core AI modules (rules, ML, SHAP, RAG, agent)
│   │   ├── main.py           # Application endpoints and pipeline orchestration
│   │   ├── models.py         # Pydantic request/response validation schemas
│   │   └── Dockerfile        # Docker setup for FastAPI cloud deployment
│   ├── frontend/             # Next.js frontend application (shadcn/ui + Tailwind 4)
│   │   ├── app/              # App Router pages and authentication routing
│   │   ├── components/       # Dashboard and ui elements (57+ custom shadcn files)
│   │   ├── lib/              # Shared utilities and types
│   │   └── Dockerfile        # Multi-stage production build for standalone Next.js
│   ├── Pipelines/            # ETL (Airflow DAGs, manual PySpark, DLT) & RAG Indexing
│   └── scripts/              # Training scripts for XGBoost model
├── data/                     # Medallion layer sample datasets (Bronze, Silver, Policies)
└── README.md                 # This file
```

---

## 💻 Installation & Setup

### Prerequisites
*   Python 3.9+
*   Node.js 18.0+
*   npm or pnpm

### 1. Backend FastAPI Setup

Navigate to the API folder, set up a Python virtual environment, and install dependencies:

```bash
cd Project/api
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

Create a `.env` file in `Project/api` with your credentials:

```ini
DATABRICKS_HOST=your-databricks-host
DATABRICKS_TOKEN=dapi...
DATABRICKS_HTTP_PATH=...
OPENAI_API_KEY=sk-proj-...
DATABRICKS_MODEL_SERVING_URL=...
DATABRICKS_VECTOR_SEARCH_URL=...
```

### 2. Frontend Next.js Setup

Navigate to the frontend folder and install node packages:

```bash
cd ../frontend
npm install
# or
pnpm install
```

Create a `.env.production` or `.env.local` file in `Project/frontend`:

```ini
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXTAUTH_URL=http://localhost:3000
NEXTAUTH_SECRET=your-nextauth-secret
GOOGLE_CLIENT_ID=your-google-oauth-client-id
GOOGLE_CLIENT_SECRET=your-google-oauth-client-secret
ALLOWED_EMAILS=comma,separated,whitelisted,emails
```

---

## 🚀 Running the Application

### 1. Start the Backend API

From the `Project/api` folder:

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```
*The backend service will run at [http://localhost:8000](http://localhost:8000). You can browse the interactive Swagger docs at [http://localhost:8000/docs](http://localhost:8000/docs).*

### 2. Start the Frontend Dashboard

From the `Project/frontend` folder:

```bash
npm run dev
# or
pnpm dev
```
*The web dashboard will run at [http://localhost:3000](http://localhost:3000).*

---

## 🧪 Usage Instructions

1.  **Sign In**: Open the web application and sign in using Google OAuth (or bypass in local development mode).
2.  **Submit Claims**:
    *   **Single Claim**: Enter a valid claim ID (e.g., `CLM-1001`) into the text field.
    *   **Batch Claims**: Drag and drop a CSV file containing a list of claim IDs under a `claim_id` column.
3.  **Analyze**: Click **Run Analysis** to execute the pipeline.
4.  **Review Findings**:
    *   **Summary Cards**: Instantly view the distribution of low-risk, high-risk, and failed validation claims.
    *   **Detailed Cards**: Drill down on rule violations, XGBoost risk scores, SHAP reasons (why the claim is at risk), RAG-retrieved policies, and the step-by-step GPT-4o-mini remediation summaries.
5.  **Export Results**: Click **Export Results** and choose **CSV** or **JSON** to download the analysis outcomes to your device.
