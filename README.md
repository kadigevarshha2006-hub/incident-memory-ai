# Autonomous Engineering Incident Response Agent
### *AI Agents That Learn Using Hindsight* — Hackathon Project

[![Python 3.11+](https://img.shields.io/badge/Python-3.11%2B-blue.svg)](https://www.python.org/)
[![Hindsight Cloud](https://img.shields.io/badge/Memory_Layer-Hindsight_Cloud-indigo.svg)](https://vectorize.io)
[![Model](https://img.shields.io/badge/ML_Model-RandomForest_77.37%25-emerald.svg)](https://scikit-learn.org)
[![FastAPI](https://img.shields.io/badge/Backend-FastAPI_Async-009688.svg)](https://fastapi.tiangolo.com)
[![Groq LLM](https://img.shields.io/badge/LLM_Reasoning-Groq_Qwen3.8--27B-orange.svg)](https://groq.com)

---

## 🚀 Executive Summary

When enterprise cloud services fail at 3:00 AM, traditional on-call engineers face a critical dilemma: **every incident is diagnosed from scratch**. Stateless LLMs give generic, textbook suggestions ("check the logs", "restart the pod") without any institutional memory of previous outages, root causes, or hard-won runbooks.

The **Autonomous Engineering Incident Response Agent** solves this by uniting three core capabilities into a single operational system:

1. **Continuous Institutional Memory (Hindsight Cloud)**: Retains verified historical incident post-mortems and recalls prior fixes (e.g., HikariCP connection leaks, expired JWT signing keys, Kubernetes JVM cgroup limits) using semantic search and spreading activation.
2. **Quantitative SLA Failure Risk Prediction (Pre-trained ML)**: Employs an authentic pre-trained `RandomForestClassifier` pipeline (trained on **18,823 Kaggle ServiceNow tickets**, achieving **77.37% test accuracy**) to predict SLA breach probability within milliseconds.
3. **The Closed Learning Loop**: When an engineer resolves a novel incident, one click commits the confirmed root cause and remediation back into Hindsight Cloud (`retain()`), ensuring the organization **never solves the same outage twice**.

---

## 🏛️ System Architecture

```mermaid
flowchart TD
    subgraph UI ["Interactive Operations Dashboard (Port 8000)"]
        Presets["1-Click Test Presets\n(DB Pool, Auth Storm, K8s OOM)"]
        Intake["Incident Intake Form\n(Service, Logs, Category, Priority)"]
        Gauge["Live SLA Risk Gauge\n(RandomForest 77.37% Accuracy)"]
        MemoryList["Recalled Post-Mortems Box\n(Top Historical Context)"]
        Plan["Agent Runbook Plan\n(Markdown Incident Commander)"]
        ClosedLoop["Closed-Loop Learning Form\n(Commit Fix to Hindsight)"]
    end

    subgraph Backend ["FastAPI Async Server (backend/app.py)"]
        ModelSvc["Model Service\n(ColumnTransformer + Imputer + RandomForest)"]
        AgentCore["Incident Agent\n(Groq Qwen 3.8-27B)"]
        HindsightSvc["Hindsight Service\n(Official hindsight-client v0.10.1)"]
    end

    subgraph External ["Persistent Cloud Services"]
        HCloud[("Hindsight Cloud API\nBank: incident-response-bank")]
        GroqAPI["Groq Cloud API\n(LLM Inference)"]
    end

    Presets --> Intake
    Intake -->|POST /api/analyze| Backend
    Backend --> ModelSvc
    ModelSvc -->|Quantitative Risk %| Gauge
    Backend --> HindsightSvc
    HindsightSvc -->|arecall()| HCloud
    HCloud -->|Recalled Memories| HindsightSvc
    HindsightSvc --> MemoryList
    HindsightSvc --> AgentCore
    ModelSvc --> AgentCore
    AgentCore --> GroqAPI
    GroqAPI --> Plan
    ClosedLoop -->|POST /api/resolve| HindsightSvc
    HindsightSvc -->|aretain()| HCloud
```

---

## 📊 Authentic Machine Learning Benchmark & Ground Truth

Derived directly from the **ServiceNow Incident Management Event Log (Kaggle)**:

| Metric | Verified Ground Truth Value |
| :--- | :--- |
| **Total Event Transitions** | 109,959 rows |
| **Unique Incident Records** | 18,823 tickets |
| **SLA Met (`made_sla = True`)** | 11,115 (59.05%) |
| **SLA Breached (`made_sla = False`)** | 7,708 (40.95%) |
| **Machine Learning Model** | Scikit-Learn `RandomForestClassifier` |
| **Pipeline Size** | 189 MB (`incident_sla_model.pkl`) |
| **Test Set Accuracy** | **77.37%** |
| **Categorical Dimensions** | 45 Categories, 215 Subcategories, 68 Assignment Groups |

> [!NOTE]
> **Data Provenance**: The quantitative SLA predictions use the authentic 189 MB Scikit-Learn pipeline without synthetic mock models. Qualitative post-mortems (root causes, configuration parameters) are curated enrichments structured to reflect real enterprise incidents while preserving Kaggle categorical metadata.

---

## 🧠 Why Mode B (With Hindsight) is the Core Product

| Capability | Mode A: Generic Baseline (Without Memory) | Mode B: Powered by Hindsight (Default & Recommended) |
| :--- | :--- | :--- |
| **Root Cause Attribution** | Hallucinates generic textbook causes ("check network cables", "verify password"). | Cites specific historical post-mortems (e.g., `INC001042`: *HikariCP connection pool exhaustion*). |
| **Runbook Actionability** | "Review server logs and consult your administrator." | Provides exact commands (e.g., `ALTER SYSTEM KILL SESSION`, `-XX:MaxRAMPercentage=75.0`). |
| **SLA Risk Awareness** | Unaware of quantitative breach probabilities. | Directly conditions urgency on the 77.37% accurate RandomForest SLA risk score. |
| **Organizational Learning** | Stateless: forgets everything once the chat session closes. | **Closed Loop**: New confirmed remediations are stored in Hindsight Cloud and recalled instantly in future incidents. |

---

## ⚡ Quick Start (Local Setup in 2 Minutes)

### 1. Prerequisites
- Python 3.11, 3.12, or 3.13
- Git

### 2. Clone and Navigate
```bash
git clone https://github.com/your-repo/ai-incident-response-assistant.git
cd ai-incident-response-assistant
```

### 3. Environment Configuration (`.env`)
Create a `.env` file in the project root:
```env
HINDSIGHT_API_URL=https://api.hindsight.vectorize.io
HINDSIGHT_API_KEY=your_hindsight_api_key_here
HINDSIGHT_BANK_ID=incident-response-bank
LLM_API_KEY=your_groq_api_key_here
LLM_PROVIDER=groq
GROQ_MODEL=qwen/qwen3.8-27b
```

### 4. Install Dependencies
```bash
pip install -r backend/requirements.txt
```

### 5. Seed Historical Incident Memories into Hindsight Cloud
Populate the 20 initial curated incident post-mortems:
```bash
cd backend
python seed_hindsight.py
```
*(You will see `20/20 memories retained successfully into Hindsight Cloud`)*

### 6. Launch the Application
```bash
python -m uvicorn app:app --host 127.0.0.1 --port 8000
```
Open **[http://127.0.0.1:8000](http://127.0.0.1:8000)** in your browser.

---

## 🎯 1-Click Verification Scenarios

The web interface includes built-in 1-click test scenarios to evaluate the agent instantly:

### Scenario 1: Payment Gateway API DB Pool Outage
- **Click**: `[💳 Payment API: DB Pool Outage]`
- **SLA Breach Risk**: **65.7%** (Medium Risk)
- **Hindsight Recall**: Recalls `INC001042` — Database connection pool exhaustion due to improper HikariCP `maxPoolSize` configuration.
- **Agent Output**: Identifies the exact configuration parameter and provides mitigation runbooks to restore database connectivity before SLA breach.

### Scenario 2: Authentication & Session Service Storm
- **Click**: `[🔐 Auth Service: JWT Cert Expiry]`
- **SLA Breach Risk**: **65.7%** (Critical High-Impact Auth Outage)
- **Hindsight Recall**: Recalls `INC001150` — JWT validation errors caused by an un-rotated signing key certificate.
- **Agent Output**: Flags JWKS endpoint key rotation and session token invalidation procedures.

### Scenario 3: Kubernetes Pod OOMKilled Crash Loop
- **Click**: `[☸️ Kubernetes: OOMKilled Loop]`
- **SLA Breach Risk**: **74.7%** (High Risk)
- **Hindsight Recall**: Recalls `INC001420` / `INC005001` — JVM `-Xmx` heap exceeding Kubernetes cgroup container limits (Exit code 137).
- **Agent Output**: Prescribes `-XX:MaxRAMPercentage=75.0` container-aware JVM flags.

---

## 🔄 The Closed Learning Loop (Demonstration)

To prove that the agent truly learns from experience:

1. In the **Closed-Loop Learning** panel at the bottom of the dashboard, enter a novel incident resolution:
   - **Incident ID**: `INC006001`
   - **Service**: `Recommendation Engine Microservice`
   - **Root Cause**: `Unindexed vector similarity query causing 100% CPU lockup on MongoDB collection`
   - **Remediation**: `Added compound index db.items.createIndex({ embedding: "2dsphere", category: 1 })`
2. Click **"Save Resolution to Hindsight Cloud"**.
3. Submit a new ticket describing high CPU usage or slow queries on the recommendation service.
4. **Result**: The agent immediately recalls `INC006001` from Hindsight Cloud and recommends the MongoDB compound index fix!

---

## 📁 Repository Structure

```
ai-incident-response-assistant/
├── backend/
│   ├── app.py                      # FastAPI REST API & static dashboard server
│   ├── agent.py                    # IncidentResponseAgent (Groq + Hindsight + RandomForest)
│   ├── hindsight_service.py        # Official hindsight-client async wrapper
│   ├── model_service.py            # Scikit-Learn RandomForest pipeline loader & patch
│   ├── seed_hindsight.py           # Seeding script for Hindsight Cloud bank
│   ├── seed_memories.json          # 20 curated historical incident post-mortems
│   ├── test_agent_reasoning.py     # End-to-end automated verification script
│   ├── requirements.txt            # Python dependencies
│   ├── model/
│   │   ├── incident_sla_model.pkl  # Authentic trained RandomForest pipeline (189 MB)
│   │   ├── dashboard_stats.json    # Verified dataset stats (18,823 incidents)
│   │   └── feature_options.json    # Feature categories, subcategories, assignment groups
│   └── static/
│       ├── index.html              # Responsive Tailwind CSS operations UI
│       └── app.js                  # Frontend controllers, Chart.js telemetry, API clients
├── DEMO_SCRIPT.md                  # 60-Second Hackathon Video Demo Script
├── TECHNICAL_ARTICLE.md            # In-depth technical architecture publication
└── README.md                       # Main documentation
```

---

## 🏆 Hackathon Submission Checklist

- [x] **Theme Fit**: Autonomous agent built explicitly on **Hindsight** memory layer.
- [x] **Authentic Machine Learning**: 189 MB Scikit-Learn `RandomForestClassifier` trained on 18,823 Kaggle tickets (77.37% test accuracy).
- [x] **Real Hindsight Cloud**: Connected to live endpoint `https://api.hindsight.vectorize.io`, memory bank `incident-response-bank`.
- [x] **Closed-Loop Learning**: Demonstrable ability to retain new incident solutions and recall them in real time.
- [x] **Interactive Dashboard**: Modern dark-mode UI with live SLA gauges, Hindsight status badge, and Markdown plan generation.
- [x] **Zero Mock Fallbacks**: 100% authentic ML inferences and cloud memory queries.
