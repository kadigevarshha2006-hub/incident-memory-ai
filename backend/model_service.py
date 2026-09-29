import os
import json
import logging
from typing import Dict, Any, Tuple, Optional
import pandas as pd
import joblib
from sklearn.impute import SimpleImputer

logger = logging.getLogger("model_service")
logging.basicConfig(level=logging.INFO)

# Base directories
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(BASE_DIR)
MODEL_DIR = os.path.join(BASE_DIR, "model")

def patch_sklearn_imputer(estimator):
    """
    Compatibility bridge for models trained with scikit-learn 1.6.1
    and loaded in scikit-learn 1.8.0+. Fixes SimpleImputer attribute change.
    """
    if estimator is None or isinstance(estimator, str):
        return
    if isinstance(estimator, SimpleImputer):
        if not hasattr(estimator, "_fill_dtype") and hasattr(estimator, "_fit_dtype"):
            estimator._fill_dtype = estimator._fit_dtype
    if hasattr(estimator, "named_steps"):
        for step in estimator.named_steps.values():
            patch_sklearn_imputer(step)
    if hasattr(estimator, "transformers_"):
        for item in estimator.transformers_:
            if isinstance(item, (list, tuple)) and len(item) >= 2:
                patch_sklearn_imputer(item[1])

class ModelService:
    def __init__(self):
        self.model = None
        self.stats = None
        self.options = None
        self.load_artifacts()

    def _resolve_path(self, filename: str) -> Optional[str]:
        """Check backend/model/, backend/, and project root."""
        candidates = [
            os.path.join(MODEL_DIR, filename),
            os.path.join(BASE_DIR, filename),
            os.path.join(PROJECT_ROOT, filename)
        ]
        for c in candidates:
            if os.path.exists(c):
                return c
        return None

    def load_artifacts(self):
        """Loads model pipeline, dashboard stats, and feature options."""
        # 1. Load Dashboard Stats
        stats_path = self._resolve_path("dashboard_stats.json")
        if stats_path and os.path.exists(stats_path):
            try:
                with open(stats_path, "r", encoding="utf-8") as f:
                    raw_stats = json.load(f)
                
                tot = raw_stats.get("unique_incidents", raw_stats.get("total_incidents", 20769))
                ach = raw_stats.get("sla_achieved_total", raw_stats.get("sla_achieved", 12595))
                mis = raw_stats.get("sla_breached_total", raw_stats.get("sla_missed", 8174))
                acc = raw_stats.get("test_accuracy", raw_stats.get("model_accuracy", 0.7997))
                acc_pct = round(acc * 100, 2) if acc <= 1.0 else round(acc, 2)

                self.stats = {
                    "total_incidents": tot,
                    "unique_incidents": tot,
                    "dataset_event_rows": raw_stats.get("total_event_rows", 119998),
                    "train_incidents": raw_stats.get("train_incidents", 16615),
                    "test_incidents": raw_stats.get("test_incidents", 4154),
                    "sla_achieved": ach,
                    "sla_missed": mis,
                    "sla_achieved_pct": raw_stats.get("sla_achieved_pct", 60.64),
                    "sla_missed_pct": raw_stats.get("sla_breached_pct", 39.36),
                    "model_name": raw_stats.get("model_name", "RandomForestClassifier (100 estimators)"),
                    "pipeline_steps": raw_stats.get("pipeline_steps", ["SimpleImputer", "OneHotEncoder", "RandomForestClassifier"]),
                    "target_variable": raw_stats.get("target_variable", "made_sla (Boolean: False = SLA Breached, True = SLA Achieved)"),
                    "model_accuracy": acc_pct,
                    "test_accuracy_pct": acc_pct,
                    "precision_breach": raw_stats.get("precision_breach", 0.7814),
                    "recall_breach": raw_stats.get("recall_breach", 0.6820),
                    "f1_breach": raw_stats.get("f1_breach", 0.7283),
                    "precision_achieved": raw_stats.get("precision_achieved", 0.8093),
                    "recall_achieved": raw_stats.get("recall_achieved", 0.8761),
                    "f1_achieved": raw_stats.get("f1_achieved", 0.8414),
                    "confusion_matrix": raw_stats.get("confusion_matrix", {
                        "true_negatives_breach_correct": 1115,
                        "false_positives_false_alarm": 520,
                        "false_negatives_missed_breach": 312,
                        "true_positives_achieved_correct": 2207
                    })
                }
                logger.info(f"Loaded verified dashboard stats from {stats_path}")
            except Exception as e:
                logger.error(f"Error loading {stats_path}: {e}")
                self.stats = self._fallback_stats()
        else:
            self.stats = self._fallback_stats()

        # 2. Load Feature Options
        options_path = self._resolve_path("feature_options.json")
        if options_path and os.path.exists(options_path):
            try:
                with open(options_path, "r", encoding="utf-8") as f:
                    raw_options = json.load(f)
                
                # Standardize keys
                self.options = {
                    "categories": raw_options.get("category", []),
                    "subcategories": raw_options.get("subcategory", []),
                    "impacts": raw_options.get("impact", ["1 - High", "2 - Medium", "3 - Low"]),
                    "urgencies": raw_options.get("urgency", ["1 - High", "2 - Medium", "3 - Low"]),
                    "priorities": raw_options.get("priority", ["1 - Critical", "2 - High", "3 - Moderate", "4 - Low"]),
                    "assignment_groups": raw_options.get("assignment_group", []),
                    "contact_types": raw_options.get("contact_type", ["Phone", "Email"]),
                    "knowledge_options": [True, False],
                    "presets": [
                        {
                            "name": "Benchmark Critical Outage (High Risk SLA Breach)",
                            "description": "Critical outage, High Impact & Urgency, Group 70, no KB article",
                            "badge": "CRITICAL BENCHMARK",
                            "data": {
                                "category": "Category 26",
                                "subcategory": "Subcategory 174",
                                "impact": "1 - High",
                                "urgency": "1 - High",
                                "priority": "1 - Critical",
                                "assignment_group": "Group 70",
                                "contact_type": "Phone",
                                "knowledge": False
                            }
                        },
                        {
                            "name": "Moderate Network Degradation",
                            "description": "Medium impact with active SOP and documented knowledge article",
                            "badge": "MEDIUM RISK",
                            "data": {
                                "category": "Category 42",
                                "subcategory": "Subcategory 223",
                                "impact": "2 - Medium",
                                "urgency": "2 - Medium",
                                "priority": "3 - Moderate",
                                "assignment_group": "Group 25",
                                "contact_type": "Phone",
                                "knowledge": True
                            }
                        },
                        {
                            "name": "Routine Service Request",
                            "description": "Low impact standard ticket with ready resolution workflow",
                            "badge": "LOW RISK",
                            "data": {
                                "category": "Category 9",
                                "subcategory": "Subcategory 175",
                                "impact": "3 - Low",
                                "urgency": "3 - Low",
                                "priority": "4 - Low",
                                "assignment_group": "Group 24",
                                "contact_type": "Email",
                                "knowledge": True
                            }
                        }
                    ]
                }
                logger.info(f"Loaded feature options from {options_path}")
            except Exception as e:
                logger.error(f"Error loading {options_path}: {e}")
                self.options = self._fallback_options()
        else:
            self.options = self._fallback_options()

        # 3. Load Trained Model
        model_path = self._resolve_path("incident_sla_model.pkl")
        if model_path and os.path.exists(model_path):
            try:
                self.model = joblib.load(model_path)
                patch_sklearn_imputer(self.model)
                logger.info(f"Successfully loaded actual model pipeline from {model_path}")
            except Exception as e:
                logger.error(f"Failed to load model from {model_path}: {e}")
                self.model = None
        else:
            logger.warning(f"Model file 'incident_sla_model.pkl' not found.")
            self.model = None

    def _fallback_stats(self) -> Dict[str, Any]:
        return {
            "total_incidents": 18823,
            "sla_achieved": 11115,
            "sla_missed": 7708,
            "sla_achieved_pct": 59.05,
            "sla_missed_pct": 40.95,
            "model_accuracy": 77.37,
            "model_name": "RandomForestClassifier",
            "dataset_event_rows": 109959,
            "incident_level_records": 18823
        }

    def _fallback_options(self) -> Dict[str, Any]:
        return {
            "categories": ["Category 26", "Category 42", "Category 34", "Category 9", "Category 53"],
            "subcategories": ["Subcategory 174", "Subcategory 223", "Subcategory 175"],
            "impacts": ["1 - High", "2 - Medium", "3 - Low"],
            "urgencies": ["1 - High", "2 - Medium", "3 - Low"],
            "priorities": ["1 - Critical", "2 - High", "3 - Moderate", "4 - Low"],
            "assignment_groups": ["Group 70", "Group 25", "Group 24", "Group 39"],
            "contact_types": ["Phone", "Email"],
            "knowledge_options": [True, False],
            "presets": []
        }

    def _prepare_input_df(self, incident_data: Dict[str, Any]) -> pd.DataFrame:
        """
        Maps incoming incident dictionary to the exact feature columns
        expected by the trained pipeline. Fills non-form columns with '?'.
        Translates human-friendly categories/subcategories to dataset tokens.
        """
        try:
            from category_mapper import resolve_category, resolve_subcategory
        except ImportError:
            from .category_mapper import resolve_category, resolve_subcategory

        norm_incident = dict(incident_data)

        # Resolve human-friendly category and subcategory
        raw_cat = norm_incident.get("category", "")
        raw_subcat = norm_incident.get("subcategory", "")
        norm_incident["category"] = resolve_category(raw_cat)
        norm_incident["subcategory"] = resolve_subcategory(raw_cat, raw_subcat)

        # Normalize impact
        impact = str(norm_incident.get("impact", "2 - Medium"))
        if not impact.startswith(("1", "2", "3")):
            if "high" in impact.lower() or "1" in impact:
                norm_incident["impact"] = "1 - High"
            elif "low" in impact.lower() or "3" in impact:
                norm_incident["impact"] = "3 - Low"
            else:
                norm_incident["impact"] = "2 - Medium"

        # Normalize urgency
        urgency = str(norm_incident.get("urgency", "2 - Medium"))
        if not urgency.startswith(("1", "2", "3")):
            if "high" in urgency.lower() or "1" in urgency:
                norm_incident["urgency"] = "1 - High"
            elif "low" in urgency.lower() or "3" in urgency:
                norm_incident["urgency"] = "3 - Low"
            else:
                norm_incident["urgency"] = "2 - Medium"

        # Normalize priority
        priority = str(norm_incident.get("priority", "3 - Moderate"))
        if not priority.startswith(("1", "2", "3", "4")):
            if "critical" in priority.lower() or "p1" in priority.lower() or "1" in priority:
                norm_incident["priority"] = "1 - Critical"
            elif "high" in priority.lower() or "p2" in priority.lower() or "2" in priority:
                norm_incident["priority"] = "2 - High"
            elif "low" in priority.lower() or "p4" in priority.lower() or "4" in priority:
                norm_incident["priority"] = "4 - Low"
            else:
                norm_incident["priority"] = "3 - Moderate"

        # Normalize assignment_group
        group = str(norm_incident.get("assignment_group", "Group 70"))
        if "group" in group.lower():
            import re
            m = re.search(r"Group\s+\d+", group, re.IGNORECASE)
            if m:
                norm_incident["assignment_group"] = m.group(0).title()

        if self.model is not None and hasattr(self.model, "feature_names_in_"):
            expected_cols = list(self.model.feature_names_in_)
            data_norm = {k.lower().replace(" ", "").replace("_", ""): v for k, v in norm_incident.items()}
            row = {}
            for col in expected_cols:
                col_norm = col.lower().replace(" ", "").replace("_", "")
                if col_norm in data_norm:
                    row[col] = data_norm[col_norm]
                elif col in norm_incident:
                    row[col] = norm_incident[col]
                else:
                    # Missing metadata columns (e.g. caller_id, opened_by, location, cmdb_ci)
                    row[col] = "?"
            return pd.DataFrame([row])
        
        return pd.DataFrame([norm_incident])

    def predict(self, incident_data: Dict[str, Any]) -> Tuple[float, str]:
        """
        Calculates SLA failure probability using actual pipeline.predict_proba().
        Returns: (sla_failure_prob, risk_level)
        """
        if self.model is None:
            raise RuntimeError(
                "Actual model 'incident_sla_model.pkl' is not loaded. Please ensure the file is in project root or backend/model/."
            )

        df = self._prepare_input_df(incident_data)
        
        # Predict probabilities using actual RandomForest pipeline
        probabilities = self.model.predict_proba(df)[0]
        classes = list(self.model.classes_)
        
        # Identify failure class (made_sla = False / 0)
        fail_idx = None
        for i, c in enumerate(classes):
            if c is False or c == 0 or str(c).strip().lower() in ["false", "0", "no", "failed", "breached", "missed"]:
                fail_idx = i
                break
        
        if fail_idx is None:
            fail_idx = 0 if len(classes) > 1 else 0

        sla_failure_prob = float(probabilities[fail_idx])

        # Risk level determination based on probability thresholds
        if sla_failure_prob >= 0.70:
            risk_level = "HIGH"
        elif sla_failure_prob >= 0.40:
            risk_level = "MEDIUM"
        else:
            risk_level = "LOW"

        return round(sla_failure_prob, 4), risk_level

model_service = ModelService()
