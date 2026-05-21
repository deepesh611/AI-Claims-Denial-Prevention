# AI-Powered Claim Denial Prevention & Remediation System

## 🚀 Overview
The **AI-Powered Claim Denial Prevention & Remediation System** is an end-to-end intelligent platform designed to predict, explain, and suggest remediations for healthcare claim denials before they are submitted to payers. By integrating a deterministic rule engine, machine learning, Explainable AI (SHAP), Retrieval-Augmented Generation (RAG), and Agentic AI, this system helps healthcare providers minimize revenue loss, reduce manual rework, and streamline billing operations.

## ✨ Key Features
- **Deterministic Rule Validation**: Pre-screens claims for missing data, invalid CPT/ICD crosswalks, and basic referential integrity.
- **Predictive ML Risk Scoring**: An XGBoost model evaluates claims that pass rule checks to predict the probability of denial (Low, Medium, High Risk).
- **Explainable AI (SHAP)**: Extracts human-readable justifications (feature importances) for claims flagged as High Risk.
- **Retrieval-Augmented Generation (RAG)**: Retrieves contextually relevant payer policies from a vector database based on the specific risk factors of a claim.
- **Agentic AI Orchestration**: Synthesizes rule failures, ML risk scores, SHAP explanations, and RAG-retrieved policies to generate actionable, step-by-step remediation plans.
- **Interactive Dashboard**: A modern, responsive Dash-based UI for single-claim analysis or bulk CSV uploads, visualizing risk metrics, rule failures, and AI recommendations.

## 🏗️ System Architecture
The project follows a robust architecture spanning Data Engineering, AI/ML, and Web Application layers:

1. **Data Engineering (Medallion Architecture)**:
   - **Bronze Layer**: Raw ingestion of claims, provider, diagnosis, and cost data.
   - **Silver Layer**: Data cleansing, deduplication, null imputation, and standardization.
   - **Gold Layer**: Aggregated feature tables and ML-ready datasets.
   - Managed via ETL scripts and Airflow DAGs.

2. **Backend API (FastAPI)**:
   - Orchestrates the full AI pipeline via the `/predict` endpoint.
   - Routes claims sequentially through: `rule_check` -> `ml_scoring` -> `shap_explainer` -> `rag` -> `agent`.

3. **Frontend Application (Dash by Plotly)**:
   - Provides a clean, responsive UI with dark mode support for users to upload claims and view detailed AI analysis, risk scores, and remediation steps.

## 📂 Repository Structure
```text
.
├── Project/
│   ├── api/                # FastAPI backend service
│   │   ├── main.py         # Main API application & endpoints
│   │   ├── models.py       # Pydantic models for request/response
│   │   └── pipeline/       # Core AI modules (rules, ml, shap, rag, agent)
│   ├── app/                # Dash frontend web application
│   │   └── app.py          # Main Dash application UI
│   ├── Pipelines/          # Data Engineering pipelines
│   │   ├── DAG/            # Airflow DAGs
│   │   ├── ETL/            # Extract, Transform, Load scripts
│   │   ├── ETL_DB/         # Database related ETL tasks
│   │   └── Rag Indexing/   # Vector DB indexing scripts for policies
│   ├── docs/               # Project documentation
│   ├── architectures/      # System architecture diagrams/docs
│   ├── scripts/            # Helper scripts
│   ├── mindmap.md          # Comprehensive project blueprint
│   └── week-1.md           # Phase 1 documentation
├── data/                   # Raw and processed datasets
└── db/                     # Local database/vector store files
```

## 💻 Installation & Setup

### Prerequisites
- Python 3.9+
- Pip package manager

### 1. Clone the repository
```bash
git clone <repository_url>
cd <repository_folder>
```

### 2. Set up the Python Virtual Environment
It's highly recommended to use a virtual environment to manage dependencies.
```bash
python -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate
```

### 3. Install Dependencies
**For the Backend API:**
```bash
cd Project/api
pip install -r requirements.txt
```

**For the Frontend App:**
```bash
cd ../app
pip install -r requirements.txt
```

## 🚀 Running the Application

### 1. Start the Backend API
First, start the FastAPI backend server:
```bash
cd Project/api
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```
*The API will be available at http://localhost:8000. You can view the Swagger documentation at http://localhost:8000/docs.*

### 2. Start the Frontend Dashboard
Open a new terminal window, ensure your virtual environment is activated, and run the Dash application:
```bash
cd Project/app
python app.py
```
*The Dash UI will be accessible at http://127.0.0.1:8050.*

## 🧪 Usage
1. Open the Dash UI in your browser.
2. Enter a single Claim ID (e.g., `CLM-1001`) or upload a CSV file containing multiple claims with a `claim_id` column.
3. Click **"Run AI Analysis"**.
4. Review the generated dashboard which highlights:
   - Total claims processed and risk categories
   - High Risk warnings with progress bars
   - Specific rule validation failures
   - Top risk factors derived from SHAP explanations
   - Relevant payer policies via RAG
   - Actionable AI remediation summaries for each claim
