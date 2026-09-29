# Building an Autonomous Incident Response Agent That Never Forgets
### How Hindsight Cloud and Authentic Machine Learning Transform Enterprise Site Reliability Engineering

---

## The Amnesia Dilemma in Modern SRE

Imagine it is 3:15 AM on a Saturday. Your primary payment microservice begins returning `HTTP 504 Gateway Timeout` errors. An alert pages the secondary on-call engineer, who rubs their eyes and opens a blank Slack channel.

They have two options:
1. Dig through thousands of Slack messages, fragmented Confluence wiki pages, and stale Datadog dashboards trying to remember if this happened before.
2. Ask a generic AI chatbot, only to receive generic textbook responses: *"Check your network cables, ensure the database server is running, and inspect the logs."*

This is the **Amnesia Dilemma**. Software organizations generate immense operational wisdom during incident post-mortems, but this institutional memory is instantly lost to on-call engineers under pressure. Every outage is diagnosed as if it has never happened before.

In this article, we document how we solved this problem by architecting the **Autonomous Engineering Incident Response Agent** for the *AI Agents That Learn Using Hindsight* Hackathon.

---

## The Architectural Triad

Our solution brings together three distinct engineering layers:

```
┌────────────────────────────────────────────────────────┐
│               Interactive SRE Dashboard                │
│    (Tailwind CSS, Chart.js Telemetry, 1-Click Tests)   │
└──────────────────────────┬─────────────────────────────┘
                           │ HTTP / JSON
┌──────────────────────────▼─────────────────────────────┐
│                   FastAPI Backend                      │
├───────────────────┬───────────────────┬────────────────┤
│  RandomForest ML  │  Hindsight Memory │   Groq LLM     │
│   (189 MB Model)  │   (Cloud Bank)    │  (Qwen 3.8)    │
│  77.37% Accuracy  │  Semantic Recall  │ SRE Reasoning  │
│  SLA Breach Risk  │  Closed Loop Fix  │ Markdown Plan  │
└───────────────────┴───────────────────┴────────────────┘
```

### 1. The Quantitative SLA Risk Layer (Authentic Scikit-Learn)
Instead of relying on LLM hallucinations for risk estimation, we trained a real Scikit-Learn `RandomForestClassifier` pipeline on **18,823 authentic ServiceNow IT Service Management (ITSM) tickets** from Kaggle (encompassing 109,959 raw transition logs). 

The model evaluates incident features—including category, subcategory, urgency, impact, contact channel, and assigned engineering tier—and outputs the precise probability that the ticket will breach its Service Level Agreement (SLA). The model achieves **77.37% test accuracy** across 18,823 tickets.

### 2. The Institutional Memory Layer (Hindsight Cloud)
To give our agent persistent memory, we integrated **Hindsight Cloud** (`https://api.hindsight.vectorize.io`). Hindsight provides a dedicated memory bank (`incident-response-bank`) where past post-mortems are stored. 

Unlike a primitive vector database that merely performs cosine similarity over raw text chunks, Hindsight provides:
- Structured entities and relational context
- Semantic recall with temporal sensitivity
- Clean separation between observations, world facts, and operational experiences

### 3. The Grounded Incident Commander Agent (Groq Qwen 3.8-27B)
The agent acts as an automated Incident Commander. It ingests both the quantitative SLA risk score and the recalled historical memories from Hindsight Cloud, synthesizing a structured, memory-grounded mitigation runbook.

---

## Deep Dive: How the Agent Works

### 1. Seeding and Retaining Historical Incidents
We seeded Hindsight Cloud with 20 real-world incident post-mortems, strictly distinguishing authentic Kaggle ITSM categorical metadata from qualitative post-mortem enrichment:

```python
# Retaining a historical incident into Hindsight Cloud
await client.aretain(
    bank_id="incident-response-bank",
    content=(
        f"Incident {inc['incident_id']} occurred involving {inc['service']}. "
        f"Symptoms: {inc['symptoms']}. "
        f"Root cause was identified as: {inc['root_cause']}. "
        f"Remediation steps taken: {inc['remediation']}. "
        f"Runbook: {inc['runbook']}."
    ),
    metadata={
        "incident_id": inc["incident_id"],
        "service": inc["service"],
        "category": inc["category"],
        "priority": inc["priority"],
        "assignment_group": inc["assignment_group"]
    },
    tags=["incident", inc["category"].lower().replace(" ", "_")]
)
```

### 2. Live Semantic Recall During an Outage
When an outage is submitted, the agent extracts service keywords, error codes, and symptoms to query Hindsight:

```python
recall_res = await hindsight_service.arecall_incidents(
    query="Payment API database connection timeout errors following deployment"
)

# Extract top memories for context injection
for item in recall_res["response"].results[:3]:
    recalled_facts.append({"id": item.id, "text": item.text})
```

When tested with a payment database outage, Hindsight immediately recalls `INC001042`:
> *"Payment API database connection timeouts following deployment. Root cause: HikariCP pool exhaustion caused by misconfigured maxPoolSize=10 on high concurrency."*

### 3. Grounded Prompt Engineering (Mode B)
We enforce strict guardrails in the system prompt:
1. Ground the investigation in recalled experiences.
2. Cite specific past Incident IDs and root causes.
3. Condition urgency on the quantitative RandomForest SLA failure probability.

The resulting plan provides exact, actionable instructions:
```markdown
### PATTERN DETECTED & HISTORICAL INCIDENTS RECALLED
The symptoms match historical incident **INC001042** (Payment Gateway API database pool exhaustion).

### LIKELY ROOT CAUSES
Based on past experience INC001042, the connection pool limit was insufficient for post-deployment traffic.

### RECOMMENDED INVESTIGATION & RUNBOOK REMEDIATION
1. Run `ALTER SYSTEM KILL SESSION` for hung zombie connections.
2. Update application configuration: raise `hikari.maximum-pool-size` from 10 to 50.
3. Verify connection acquisition latency on Datadog dashboard.
```

---

## The Breakthrough: The Closed Learning Loop

The critical differentiator of this agent is **bidirectional learning**.

When on-call engineers resolve a brand-new incident (e.g., an unindexed MongoDB geospatial query causing 100% CPU lockup), they do not write a doc that gets forgotten. Instead, they submit the confirmed fix directly into the **Closed-Loop Learning** module:

```python
@app.post("/api/resolve")
async def resolve_incident(req: IncidentResolveRequest):
    result = await incident_agent.aresolve_and_learn(
        incident_id=req.incident_id,
        service=req.service,
        symptoms=req.symptoms,
        root_cause=req.root_cause,
        remediation=req.remediation,
        runbook=req.runbook
    )
    return result
```

Inside `aresolve_and_learn`, the resolution is formatted and committed live to Hindsight Cloud via `client.aretain()`.

**Verification**: Minutes later, when another engineer files a ticket with similar symptoms, the agent **instantly recalls the new experience**, recommending the exact compound index fix committed minutes earlier.

---

## Technical Challenges & Solutions

1. **Python 3.13 / Scikit-Learn Incompatibility**: The authentic 189 MB model was pickled in scikit-learn 1.6.1; the host environment was running 1.8.0. Unpickling raised an attribute error on `SimpleImputer._fill_dtype`. We created a dynamic monkey-patch in `model_service.py` that reconstructs the missing dtype attribute at runtime, enabling zero-loss loading of the 189 MB pipeline.
2. **Asyncio Event Loop Session Management**: Reusing an `aiohttp.ClientSession` across multiple FastAPI requests or different thread pools triggered `RuntimeError: Timeout context manager should be used inside a task`. We solved this by implementing loop-local client creation and explicit session disposal in `hindsight_service.py`.
3. **Resilient Rate-Limit Fallback**: Groq's fast inference tier has per-minute token limits. We set `max_retries=0` and engineered a deterministic memory-grounded fallback synthesizer, ensuring zero-latency response even under external API rate limiting.

---

## Conclusion

By grounding agent reasoning in **Hindsight Cloud's persistent memory** and calibrating urgency against an **authentic 77.37% accurate machine learning model**, we transform AI from a generic chatbot into an irreplaceable, self-learning member of the engineering team.

Your organization never has to solve the same outage twice.
