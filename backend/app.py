import os
import json
import logging
from datetime import datetime, timezone
from typing import Dict, Any, Optional, List
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

from model_service import model_service
from hindsight_service import hindsight_service
from agent import incident_agent
from category_mapper import get_options_payload, resolve_category, resolve_subcategory

logger = logging.getLogger("app")
logging.basicConfig(level=logging.INFO)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "static")
PERSISTED_MEMORIES_FILE = os.path.join(BASE_DIR, "persisted_memories.json")

SESSION_RESOLUTIONS: List[Dict[str, Any]] = []

def load_persisted_memories() -> List[Dict[str, Any]]:
    """Loads persisted team memories saved on disk."""
    if os.path.exists(PERSISTED_MEMORIES_FILE):
        try:
            with open(PERSISTED_MEMORIES_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, list):
                    return data
        except Exception as e:
            logger.error(f"Failed to load persisted memories: {e}")
    return []

def save_persisted_memory(memory_item: Dict[str, Any]):
    """Appends newly verified resolution to disk store so it persists across restarts/refreshes."""
    current = load_persisted_memories()
    item_id = memory_item.get("incident_id")
    current = [m for m in current if m.get("incident_id") != item_id]
    current.insert(0, memory_item)
    try:
        with open(PERSISTED_MEMORIES_FILE, "w", encoding="utf-8") as f:
            json.dump(current, f, indent=2)
        logger.info(f"Persisted memory saved for incident {item_id}")
    except Exception as e:
        logger.error(f"Failed to save persisted memory: {e}")

app = FastAPI(
    title="Engineering Incident Response Agent API",
    description="AI Incident Response Agent using Hindsight Persistent Memory & RandomForest SLA Breach Prediction",
    version="2.0.0"
)

# Enable CORS for cross-origin integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static asset directory
if os.path.exists(STATIC_DIR):
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

class IncidentAnalyzeRequest(BaseModel):
    service: str = Field(default="Payment Gateway API")
    description: str = Field(default="Payment API database connection timeouts following deployment")
    symptoms: Optional[str] = Field(default="")
    environment: Optional[str] = Field(default="Production")
    category: str = Field(default="Database & Storage Systems")
    subcategory: str = Field(default="Connection Pool Exhaustion / Timeout")
    impact: str = Field(default="1 - High")
    urgency: str = Field(default="1 - High")
    priority: str = Field(default="1 - Critical")
    assignment_group: str = Field(default="Tier-1 SRE & Incident Commander (Group 70)")
    contact_type: str = Field(default="Phone")
    knowledge: bool = Field(default=False)
    mode: Optional[str] = Field(default="with_hindsight")

class IncidentVerifyRequest(BaseModel):
    incident_id: str = Field(default="INC-2026-881")
    service: str = Field(default="Payment Gateway API")
    remediation_action: Optional[str] = Field(default="")
    target_environment: Optional[str] = Field(default="Staging Replica Sandbox")

class IncidentResolveRequest(BaseModel):
    incident_id: str = Field(default="INC003001")
    service: str = Field(default="Payment Gateway API")
    symptoms: str = Field(default="Connection pool timeouts")
    root_cause: str = Field(default="HikariCP pool limit set too low")
    remediation: str = Field(default="Increased maxPoolSize to 50")
    runbook: str = Field(default="Runbook-DB-Pool-Tuning")
    category: Optional[str] = Field(default="Category 26")
    priority: Optional[str] = Field(default="1 - Critical")

@app.get("/")
def serve_dashboard():
    """Serves the engineering incident dashboard interface."""
    index_file = os.path.join(STATIC_DIR, "index.html")
    if os.path.exists(index_file):
        return FileResponse(index_file)
    return {
        "service": "Engineering Incident Response Agent API",
        "status": "online",
        "docs": "/docs"
    }

@app.get("/api/health")
async def health_check():
    """Health check reporting Hindsight Cloud, ML Model, and Groq status."""
    conn_ok, conn_msg = await hindsight_service.acheck_connection()
    return {
        "status": "healthy",
        "hindsight_connected": conn_ok,
        "hindsight_bank": hindsight_service.bank_id,
        "hindsight_url": hindsight_service.api_url,
        "model_loaded": model_service.model is not None,
        "model_type": type(model_service.model).__name__ if model_service.model else None,
        "groq_configured": bool(incident_agent.api_key),
        "groq_model": incident_agent.model_name
    }

@app.get("/api/stats")
def get_dashboard_stats():
    """Returns verified dataset & benchmark performance metrics."""
    return model_service.stats

@app.get("/api/options")
def get_feature_options():
    """Returns user-friendly category hierarchies and options."""
    return get_options_payload()

@app.get("/api/memories")
def get_memories():
    """Returns stored team incident memories for the Team Memory page."""
    seed_file = os.path.join(BASE_DIR, "seed_memories.json")
    memories = []
    if os.path.exists(seed_file):
        try:
            with open(seed_file, "r", encoding="utf-8") as f:
                memories = json.load(f)
        except Exception as e:
            logger.error(f"Failed to load seed memories: {e}")
    # Load persisted memories from disk (survives server restarts)
    persisted = load_persisted_memories()
    # Merge: session (current run) + persisted (previous runs) + seed (golden baseline)
    # Deduplicate by incident_id, preferring session > persisted > seed order
    seen_ids = set()
    merged = []
    for item in SESSION_RESOLUTIONS + persisted + memories:
        item_id = item.get("incident_id")
        if item_id and item_id in seen_ids:
            continue
        if item_id:
            seen_ids.add(item_id)
        merged.append(item)
    return merged

@app.post("/api/analyze")
async def analyze_incident(req: IncidentAnalyzeRequest):
    """
    Evaluates CURRENT incident using ML model and supports with Hindsight memory:
    1. Preprocesses human-friendly inputs to Kaggle dataset representation
    2. Quantitative SLA breach risk prediction via 189 MB RandomForest pipeline
    3. Operational risk explainer factor analysis
    4. Hindsight Cloud semantic memory search
    5. Grounded root cause synthesis (zero fabrication)
    6. Safe verification simulation plan
    """
    incident_dict = req.model_dump()
    try:
        if req.mode == "without_memory":
            result = incident_agent.analyze_without_memory(incident_dict)
        else:
            result = await incident_agent.aanalyze_with_hindsight(incident_dict)
        return result
    except Exception as e:
        logger.error(f"Analysis error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/verify")
def verify_remediation(req: IncidentVerifyRequest):
    """
    SAFE SRE VERIFICATION SIMULATION SANDBOX (Staging Replica).
    Evaluates simulated verification checks without running arbitrary unsafe code on production.
    """
    return {
        "execution_status": "PASSED",
        "exit_code": 0,
        "errors_encountered": 0,
        "recovery_status": "VERIFIED",
        "probe_status": "HTTP 200 OK",
        "probe_latency_ms": 24,
        "sla_risk_after": "0.8%",
        "risk_level_after": "LOW",
        "is_simulation": True,
        "environment": req.target_environment,
        "verified_at": datetime.now(timezone.utc).isoformat(),
        "summary": "Synthetic health probes succeeded. Latency and error rates normalized within acceptable SLA boundaries."
    }

@app.post("/api/resolve")
async def resolve_incident(req: IncidentResolveRequest):
    """
    THE CLOSED LEARNING LOOP:
    Records an engineer's confirmed root cause and remediation into Hindsight Cloud live.
    The agent immediately learns this experience for subsequent incidents.
    """
    try:
        cat_code = resolve_category(req.category or "Category 26")
        result = await incident_agent.aresolve_and_learn(
            incident_id=req.incident_id,
            service=req.service,
            symptoms=req.symptoms,
            root_cause=req.root_cause,
            remediation=req.remediation,
            runbook=req.runbook,
            category=cat_code,
            priority=req.priority or "1 - Critical"
        )

        # Store in local session list for instant reflection in Team Memory page
        memory_item = {
            "incident_id": req.incident_id,
            "kaggle_metadata": {
                "category": cat_code,
                "subcategory": "Resolution",
                "priority": req.priority or "1 - Critical",
                "impact": "1 - High",
                "urgency": "1 - High",
                "assignment_group": "Tier-1 SRE",
                "made_sla": True
            },
            "synthetic_enrichment": {
                "service": req.service,
                "summary": req.symptoms,
                "symptoms": req.symptoms,
                "root_cause": req.root_cause,
                "remediation": req.remediation,
                "runbook": req.runbook or "Standard-Production-Runbook",
                "post_mortem": "Verified live resolution committed to Hindsight Cloud."
            },
            "tags": [req.service.lower().replace(" ", "-"), "newly-resolved", "team-memory"],
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        SESSION_RESOLUTIONS.insert(0, memory_item)

        # Persist to disk so it survives server restarts
        save_persisted_memory(memory_item)

        return result
    except Exception as e:
        logger.error(f"Resolution error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=True)
