import sys
import os
import joblib
import pandas as pd
from sklearn.impute import SimpleImputer

print("1. Loading model...", flush=True)
model_path = os.path.join(os.path.dirname(__file__), "model", "incident_sla_model.pkl")
model = joblib.load(model_path)
print("2. Model loaded successfully!", flush=True)

def patch_imputer(est):
    if est is None or isinstance(est, str):
        return
    if isinstance(est, SimpleImputer):
        if not hasattr(est, "_fill_dtype") and hasattr(est, "_fit_dtype"):
            est._fill_dtype = est._fit_dtype
            print("Patched SimpleImputer _fill_dtype to:", est._fill_dtype, flush=True)
    if hasattr(est, "named_steps"):
        for step in est.named_steps.values():
            patch_imputer(step)
    if hasattr(est, "transformers_"):
        for item in est.transformers_:
            if isinstance(item, (list, tuple)) and len(item) >= 2:
                patch_imputer(item[1])

print("3. Patching model...", flush=True)
patch_imputer(model)
print("4. Model patched!", flush=True)

test_input = {
    "caller_id": "?",
    "opened_by": "?",
    "contact_type": "Phone",
    "location": "?",
    "category": "Category 26",
    "subcategory": "Subcategory 174",
    "u_symptom": "?",
    "cmdb_ci": "?",
    "impact": "1 - High",
    "urgency": "1 - High",
    "priority": "1 - Critical",
    "assignment_group": "Group 70",
    "assigned_to": "?",
    "knowledge": False
}

df = pd.DataFrame([test_input])
print("5. Running predict_proba...", flush=True)
probs = model.predict_proba(df)[0]
print("6. Classes:", model.classes_, flush=True)
print("7. Probabilities:", probs, flush=True)
sla_failure_prob = probs[0]
print(f"8. SLA Failure Probability: {sla_failure_prob:.4f} ({sla_failure_prob * 100:.2f}%)", flush=True)
