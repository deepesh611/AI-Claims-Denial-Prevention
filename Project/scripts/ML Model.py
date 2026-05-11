
!pip install xgboost
%restart_python


from pyspark.sql.functions import col, avg
import numpy as np

import os
os.environ["MLFLOW_DFS_TMP"] = "/Volumes/main/models/model"

CATALOG = "main"
SCHEMA  = "gold"




gold_claim_features = spark.table(f"{CATALOG}.{SCHEMA}.gold_claim_features")

print("gold_claim_features row count:", gold_claim_features.count())
gold_claim_features.show(5)




from pyspark.sql.functions import col

# Select only ML-relevant columns
ml_cols = [
    "billed_amount",
    "billed_vs_avg_cost",
    "high_cost_flag",
    "provider_claim_count",
    "provider_risk_score",
    "diagnosis_count",
    "claim_frequency",
    "severity_score",
    "specialty",
    "category",
    "location",
    "denial_flag"  # target
]

ml_df = gold_claim_features.select(ml_cols)

# Fill remaining nulls
ml_df = ml_df.fillna({
    "diagnosis_count"    : 0,
    "provider_risk_score": 0.0,
    "billed_vs_avg_cost" : 0.0,
    "claim_frequency"    : 0
})

print("Null check after fill:")
from pyspark.sql.functions import when, isnull, count as spark_count
ml_df.select([spark_count(when(isnull(c), c)).alias(c) for c in ml_df.columns]).show()


from pyspark.sql import Window
from pyspark.sql.functions import dense_rank

# Manually encode categorical columns using dense_rank to avoid large ML models
cat_cols = ["specialty", "category", "location"]

for c in cat_cols:
    window = Window.orderBy(c)
    ml_df = ml_df.withColumn(c + "_idx", dense_rank().over(window) - 1)

# Drop original categorical columns
ml_df = ml_df.drop(*cat_cols)

ml_df.show(3)


from pyspark.ml.feature import VectorAssembler

# Use the already-encoded ml_df from Cell 21
# Define feature columns for VectorAssembler
feature_cols = [
    "billed_amount",
    "billed_vs_avg_cost",
    "high_cost_flag",
    "provider_claim_count",
    "provider_risk_score",
    "diagnosis_count",
    "claim_frequency",
    "severity_score",
    "specialty_idx",
    "category_idx",
    "location_idx"
]

assembler = VectorAssembler(inputCols=feature_cols, outputCol="features", handleInvalid="skip")
ml_df_vectorized = assembler.transform(ml_df)

# Keep only features + target
final_df = ml_df_vectorized.select("features", "denial_flag")

# Split
train_df, test_df = final_df.randomSplit([0.7, 0.3], seed=42)

print("Train size:", train_df.count())
print("Test size:", test_df.count())




# Checking Logistic Regression Model Accuracy

import mlflow
import mlflow.spark
from pyspark.ml.classification import LogisticRegression
from pyspark.ml.evaluation import BinaryClassificationEvaluator, MulticlassClassificationEvaluator

mlflow.set_experiment("/Users/deepeshvcd6273@gmail.com/claim_denial_prediction")

with mlflow.start_run(run_name="logistic_regression"):

    lr = LogisticRegression(featuresCol="features", labelCol="denial_flag", maxIter=100)
    lr_model = lr.fit(train_df)

    predictions = lr_model.transform(test_df)

    # Evaluate
    binary_eval  = BinaryClassificationEvaluator(labelCol="denial_flag")
    multi_eval   = MulticlassClassificationEvaluator(labelCol="denial_flag", metricName="accuracy")
    precision_eval = MulticlassClassificationEvaluator(labelCol="denial_flag", metricName="weightedPrecision")
    recall_eval    = MulticlassClassificationEvaluator(labelCol="denial_flag", metricName="weightedRecall")

    roc_auc   = binary_eval.evaluate(predictions)
    accuracy  = multi_eval.evaluate(predictions)
    precision = precision_eval.evaluate(predictions)
    recall    = recall_eval.evaluate(predictions)

    # Log params + metrics
    mlflow.log_param("model", "LogisticRegression")
    mlflow.log_param("maxIter", 100)
    mlflow.log_metric("roc_auc",   roc_auc)
    mlflow.log_metric("accuracy",  accuracy)
    mlflow.log_metric("precision", precision)
    mlflow.log_metric("recall",    recall)

    # Log model
    mlflow.spark.log_model(lr_model, "lr_model")

    print(f"Logistic Regression Results:")
    print(f"  Accuracy  : {accuracy:.4f}")
    print(f"  Precision : {precision:.4f}")
    print(f"  Recall    : {recall:.4f}")
    print(f"  ROC-AUC   : {roc_auc:.4f}")




import xgboost as xgb
from sklearn.metrics import accuracy_score, precision_score, recall_score, roc_auc_score

# Retrain without leakage features
feature_cols_clean = [
    "billed_amount",
    "billed_vs_avg_cost",
    "high_cost_flag",
    "severity_score",
    "specialty_idx",
    "category_idx",
    "location_idx"
]

assembler_clean = VectorAssembler(
    inputCols=feature_cols_clean, 
    outputCol="features", 
    handleInvalid="skip"
)
ml_df_clean = assembler_clean.transform(ml_df_vectorized.drop("features"))

final_df_clean = ml_df_clean.select("features", "denial_flag")
train_clean, test_clean = final_df_clean.randomSplit([0.7, 0.3], seed=42)

# Convert to pandas
train_pd_clean = train_clean.toPandas()
test_pd_clean  = test_clean.toPandas()

X_train_clean = np.vstack(train_pd_clean["features"].apply(lambda v: np.array(v.toArray())))
y_train_clean = train_pd_clean["denial_flag"].values
X_test_clean  = np.vstack(test_pd_clean["features"].apply(lambda v: np.array(v.toArray())))
y_test_clean  = test_pd_clean["denial_flag"].values

# Retrain
with mlflow.start_run(run_name="xgboost_no_leakage"):
    xgb_clean = xgb.XGBClassifier(
        n_estimators=100,
        max_depth=6,
        learning_rate=0.1,
        eval_metric="logloss"
    )
    xgb_clean.fit(X_train_clean, y_train_clean)

    y_pred_clean       = xgb_clean.predict(X_test_clean)
    y_pred_proba_clean = xgb_clean.predict_proba(X_test_clean)[:, 1]

    roc_auc_clean   = roc_auc_score(y_test_clean, y_pred_proba_clean)
    accuracy_clean  = accuracy_score(y_test_clean, y_pred_clean)
    precision_clean = precision_score(y_test_clean, y_pred_clean, average="weighted")
    recall_clean    = recall_score(y_test_clean, y_pred_clean, average="weighted")

    mlflow.log_param("model", "XGBoost_no_leakage")
    mlflow.log_metric("roc_auc",   roc_auc_clean)
    mlflow.log_metric("accuracy",  accuracy_clean)
    mlflow.log_metric("precision", precision_clean)
    mlflow.log_metric("recall",    recall_clean)

    print(f"XGBoost (No Leakage) Results:")
    print(f"  Accuracy  : {accuracy_clean:.4f}")
    print(f"  Precision : {precision_clean:.4f}")
    print(f"  Recall    : {recall_clean:.4f}")
    print(f"  ROC-AUC   : {roc_auc_clean:.4f}")




from mlflow.models.signature import infer_signature

# Build signature from clean model
input_example = X_test_clean[:3]
output_example = xgb_clean.predict(input_example)
signature = infer_signature(input_example, output_example)

with mlflow.start_run(run_name="xgboost_final") as run:
    mlflow.log_param("model", "XGBoost_no_leakage")
    mlflow.log_metric("roc_auc",   roc_auc_clean)
    mlflow.log_metric("accuracy",  accuracy_clean)
    mlflow.log_metric("precision", precision_clean)
    mlflow.log_metric("recall",    recall_clean)

    mlflow.xgboost.log_model(
        xgb_clean,
        "xgb_model",
        signature=signature,
        input_example=input_example
    )

    run_id = run.info.run_id
    print(f"Run ID: {run_id}")

# Register to Unity Catalog
model_uri = f"runs:/{run_id}/xgb_model"
registered_model = mlflow.register_model(
    model_uri=model_uri,
    name=f"{CATALOG}.{SCHEMA}.claim_denial_model"
)

print(f"Model registered: {registered_model.name}")
print(f"Version: {registered_model.version}")

test_claims = np.array([
    [15000.0, 2.5,  1, 3, 0, 4, 3],   # High risk — Cardiology, Heart, Hyderabad
    [20000.0, 3.8,  1, 3, 0, 2, 4],   # High risk — Cardiology, Diabetes, Mumbai
    [25000.0, 4.5,  1, 3, 0, 6, 5],   # High risk — Cardiology, Unknown, Unknown
    [3000.0,  0.8,  0, 1, 2, 5, 0],   # Low risk  — Neurology, Skin, Bangalore
    [1500.0,  0.5,  0, 1, 1, 1, 1],   # Low risk  — General, Cold, Chennai
    [4500.0,  1.0,  0, 1, 2, 3, 0],   # Low risk  — Neurology, Fever, Bangalore
    [7000.0,  1.4,  1, 2, 0, 2, 4],   # Medium    — Cardiology, Diabetes, Mumbai
    [5000.0,  1.0,  0, 1, 1, 3, 2],   # Normal    — General, Fever, Delhi
    [4200.0,  0.95, 0, 1, 2, 5, 0],   # Normal    — Neurology, Skin, Bangalore
    [3800.0,  0.9,  0, 1, 1, 1, 1],   # Normal    — General, Cold, Chennai
])

claim_labels = [
    "High risk  — Cardiology, Heart, Hyderabad",
    "High risk  — Cardiology, Diabetes, Mumbai",
    "High risk  — Cardiology, Unknown, Unknown",
    "Low risk   — Neurology, Skin, Bangalore",
    "Low risk   — General, Cold, Chennai",
    "Low risk   — Neurology, Fever, Bangalore",
    "Medium     — Cardiology, Diabetes, Mumbai",
    "Normal     — General, Fever, Delhi",
    "Normal     — Neurology, Skin, Bangalore",
    "Normal     — General, Cold, Chennai",
]

probs       = xgb_clean.predict_proba(test_claims)[:, 1]
predictions = xgb_clean.predict(test_claims)

print(f"{'#':<3} {'Description':<45} {'Prob':>6}  {'Prediction':<10} {'Risk'}")
print("-" * 85)
for i, (label, prob, pred) in enumerate(zip(claim_labels, probs, predictions)):
    risk    = "HIGH" if prob >= 0.5 else "LOW"
    outcome = "DENIED" if pred == 1 else "APPROVED"
    print(f"{i+1:<3} {label:<45} {prob:.4f}  {outcome:<10} {risk}")
