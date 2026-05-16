import numpy as np
import pandas as pd
import xgboost as xgb

FEATURE_REASON_MAP = {
    "billed_amount": "Billed amount is unusually high",
    "billed_vs_avg_cost": "Billed amount significantly exceeds average cost",
    "high_cost_flag": "Claim is flagged as high cost",
    "severity_score": "Severity level of the condition is high",
    "specialty_idx": "Specialty type is associated with higher denial rate",
    "category_idx": "Claim category has elevated risk",
    "location_idx": "Provider location shows elevated risk pattern"
}

FEATURE_COLS = [
    "billed_amount",
    "billed_vs_avg_cost",
    "high_cost_flag",
    "severity_score",
    "specialty_idx",
    "category_idx",
    "location_idx"
]


def run_shap(xgb_model, df: pd.DataFrame):

    X = df[FEATURE_COLS]

    # Convert to DMatrix
    dmatrix = xgb.DMatrix(X, feature_names=FEATURE_COLS)

    # Use native XGBoost SHAP contributions
    # This avoids SHAP's broken base_score parser
    shap_values = xgb_model.get_booster().predict(
        dmatrix,
        pred_contribs=True
    )

    # Last column is bias term -> remove it
    shap_values = shap_values[:, :-1]

    results = {}

    for i, row in df.reset_index(drop=True).iterrows():

        scored = {
            FEATURE_COLS[j]: abs(shap_values[i][j])
            for j in range(len(FEATURE_COLS))
        }

        top_features = sorted(
            scored,
            key=scored.get,
            reverse=True
        )[:2]

        reasons = [
            FEATURE_REASON_MAP[f]
            for f in top_features
        ]

        results[row["claim_id"]] = {
            "reason_1": reasons[0] if len(reasons) > 0 else None,
            "reason_2": reasons[1] if len(reasons) > 1 else None
        }

    return results