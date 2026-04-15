# 📄 WEEK 1 – PRODUCT DOCUMENT
**Project**: AI-Powered Claim Denial Prevention & Remediation System

## 🎯 1. Week 1 Goal (Simple Language)
In Week 1, your goal is:
👉 **Understand the problem + load data + create base system**

You are NOT building AI yet.
You are preparing the foundation for the full system.

## 🧠 2. Problem Understanding (Very Simple)
**In real life:**
- Doctor treats patient
- Billing team creates claim
- Insurance may approve or deny

**❌ Problem:**
Many claims get denied because:
- missing data
- wrong codes
- incorrect billing

**👉 This causes:**
- delay in payment
- extra work
- revenue loss

## 🚀 3. What You Are Building (Final Vision)
You are building a system that:
`Claim comes → System checks → Predicts risk → Explains reason → Suggests fix → User corrects → Claim gets approved`


## 📦 4. Week 1 Scope (What YOU will do)
**In Week 1, you will:**
- ✅ Understand problem
- ✅ Identify datasets
- ✅ Load raw data
- ✅ Create Bronze tables
- ✅ Analyze data (basic)

**❌ You will NOT:**
- build ML model
- build RAG
- build agent

## 📥 5. INPUT (What You Need)
You need the following data:

**📊 Dataset 1: Claims Data**
Contains:
- claim_id
- patient_id
- provider_id
- diagnosis_code
- procedure_code
- billed_amount
- date
> 👉 This is your main dataset

**👨‍⚕️ Dataset 2: Provider Data**
Contains:
- provider_id
- doctor name
- specialty
- location
> 👉 Used to understand who created claim

**🧬 Dataset 3: Diagnosis Data**
Contains:
- diagnosis_code
- category
- severity
> 👉 Used to understand medical reason

**💰 Dataset 4: Cost Data**
Contains:
- average cost
- expected cost
- region cost
> 👉 Used to detect high billing

**📄 Dataset 5: Policy Docs (Optional for Week 1)**
Contains:
- rules
- policies
> 👉 Used later for RAG

## ⚙️ 6. PROCESS (What You Will Do)

**Step 1: Create Project Structure**
Create folders / notebooks:
- `01_ingestion`
- `02_bronze_tables`
- `03_profiling`
- `04_docs`

**Step 2: Load Raw Data**
Load datasets into system (Databricks / Python):
*Example:*
```python
df = spark.read.csv("claims.csv", header=True, inferSchema=True)
```

**Step 3: Create Bronze Layer**
Bronze = raw data (no changes)
Create tables:
- `bronze_claims_raw`
- `bronze_provider_raw`
- `bronze_diagnosis_raw`
- `bronze_cost_raw`

> 👉 **Important:**
> Do NOT clean data here
> Store as it is

**Step 4: Add Basic Columns**
Add:
- `ingestion_time`
- `source_file`

**Step 5: Basic Data Check (Profiling)**
Check:
- total rows
- missing values
- duplicates
- incorrect values

*Example:*
```python
df.describe()
df.isNull().sum()
```

**Step 6: Understand Data**
Answer these:
- Is `claim_id` unique?
- Are amounts correct?
- Are codes missing?
- Are providers linked properly?

## 📤 7. OUTPUT (What You Must Deliver)
By end of Week 1, you must have:

**📄 Output 1: Problem Document**
Write:
- What is problem
- Who is user
- What system will do

**📊 Output 2: Dataset Summary**
Table like:

| Dataset | Purpose |
|---------|---------|
| Claims | Main data |
| Provider | Who created claim |
| Diagnosis | Medical reason |
| Cost | Compare billing |

**🗄 Output 3: Bronze Tables**
You must create:
- `bronze_claims_raw`
- `bronze_provider_raw`
- `bronze_diagnosis_raw`
- `bronze_cost_raw`

**📈 Output 4: Profiling Report**
Example:
- 10% missing diagnosis
- duplicate providers found
- some claims have abnormal cost

**🧠 Output 5: Architecture Draft**
Draw simple flow:
`Data → Bronze → (Future: Silver → Gold → ML → RAG → Agent)`

## 🎯 8. Expected Final Output (Simple View)
After Week 1:
`Input Data → Stored in Bronze → Data understood`


## 🧪 9. Testing (Basic)
Check:
- Data loaded correctly
- No missing files
- Tables created
- Row count matches

## ⚠️ 10. Common Mistakes
- ❌ Cleaning data in Bronze
- ❌ Skipping profiling
- ❌ Not understanding columns
- ❌ Jumping to ML

## 🧩 11. Week 1 Success Criteria
You are successful if:
- ✅ Data is loaded
- ✅ Bronze tables exist
- ✅ You understand data
- ✅ You know problem clearly
- ✅ Architecture draft ready

## 🧠 FINAL SIMPLE SUMMARY
👉 Week 1 = Understand + Load + Store + Analyze
`Understand Problem → Collect Data → Load Data → Store in Bronze → Analyze Data → Prepare Architecture`