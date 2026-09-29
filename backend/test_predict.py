import os
import sys
import joblib
import pandas as pd
import json

print("Python version:", sys.version)

model_path = os.path.join(os.path.dirname(__file__), "model", "incident_sla_model.pkl")
print("Loading model from:", model_path)
model = joblib.load(model_path)
print("Model loaded successfully!")
print("Classes:", model.classes_)
print("Feature names in:", model.feature_names_in_)

# Critical test incident
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
print("Input df shape:", df.shape)
probs = model.predict_proba(df)[0]
print("Probabilities [False, True]:", probs)
sla_failure_prob = probs[0]
print(f"SLA Failure Probability: {sla_failure_prob:.4f} ({sla_failure_prob * 100:.2f}%)")
