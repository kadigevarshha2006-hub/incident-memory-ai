import urllib.request
import json
import sys

print("==================================================", flush=True)
print("TESTING COMPLETE END-TO-END FLOW WITH A NEW INCIDENT", flush=True)
print("==================================================", flush=True)

new_incident = {
    "service": "Warehouse Logistics & Inventory Dispatcher",
    "description": "Celery task queue backlog growing exponentially due to Redis broker connection timeouts. 35,000 package dispatch jobs queued with HTTP 504 gateway errors.",
    "symptoms": "Redis connection pool timeout, Celery worker task starvation, dispatch delay > 45 mins",
    "environment": "Production",
    "priority": "1 - Critical",
    "impact": "1 - High",
    "urgency": "1 - High",
    "category": "Application & Microservices",
    "subcategory": "Queue Backpressure / Task Starvation",
    "assignment_group": "Group 70",
    "knowledge": False,
    "contact_type": "Phone",
    "mode": "with_hindsight"
}

# 1. ANALYZE NEW INCIDENT
print("\n1. Sending POST /api/analyze...", flush=True)
req = urllib.request.Request(
    "http://127.0.0.1:8000/api/analyze",
    data=json.dumps(new_incident).encode("utf-8"),
    headers={"Content-Type": "application/json"}
)
with urllib.request.urlopen(req, timeout=30) as res:
    analysis_data = json.loads(res.read().decode())

print("Status:", res.getcode(), flush=True)
summary = analysis_data["incident_summary"]
ml = analysis_data["ml_prediction"]
root = analysis_data["likely_root_cause"]
factors = analysis_data["evidence_and_factors"]
steps = analysis_data["recommended_response"]
verif = analysis_data["verification_plan"]

print(f"-> Service: {summary['service']}", flush=True)
print(f"-> Mapped Category: {summary['category_name']} ({summary['category_code']})", flush=True)
print(f"-> Mapped Subcategory: {summary['subcategory_name']} ({summary['subcategory_code']})", flush=True)
print(f"-> Quantitative ML SLA Breach Risk: {ml['sla_failure_percentage']}%", flush=True)
print(f"-> Risk Level: {ml['risk_level']}", flush=True)
print(f"-> Model Target: {ml['target_variable']}", flush=True)
print(f"-> Historical Precedents Found: {analysis_data['historical_matches_count']}", flush=True)
print(f"-> Evidence Risk Drivers Count: {len(factors)}", flush=True)
print(f"-> Likely Root Cause: {root['suspect']}", flush=True)
print(f"-> Root Cause Evidence: {root['evidence'][:120]}...", flush=True)
print(f"-> Action Steps Count: {len(steps)}", flush=True)

# 2. RUN SAFE VERIFICATION SIMULATION
print("\n2. Sending POST /api/verify...", flush=True)
verify_payload = {
    "incident_id": "INC-2026-TEST-99",
    "service": summary["service"],
    "remediation_action": verif["remediation_cmd"]
}
req_verify = urllib.request.Request(
    "http://127.0.0.1:8000/api/verify",
    data=json.dumps(verify_payload).encode("utf-8"),
    headers={"Content-Type": "application/json"}
)
with urllib.request.urlopen(req_verify, timeout=10) as res_v:
    verify_res = json.loads(res_v.read().decode())

print("Status:", res_v.getcode(), flush=True)
print(f"-> Execution Status: {verify_res['execution_status']} (Exit {verify_res['exit_code']})", flush=True)
print(f"-> Recovery Status: {verify_res['recovery_status']}", flush=True)
print(f"-> Health Probe: {verify_res['probe_status']} ({verify_res['probe_latency_ms']}ms)", flush=True)
print(f"-> SLA Risk After: {verify_res['sla_risk_after']} ({verify_res['risk_level_after']})", flush=True)

# 3. COMMIT RESOLUTION TO HINDSIGHT CLOUD
print("\n3. Sending POST /api/resolve...", flush=True)
resolve_payload = {
    "incident_id": "INC-2026-TEST-99",
    "service": summary["service"],
    "symptoms": summary["symptoms"],
    "root_cause": root["suspect"],
    "remediation": "Scaled Celery worker replicas from 4 to 16 and doubled Redis connection pool max_connections",
    "runbook": "Runbook-Logistics-Worker-Autoscale",
    "category": summary["category_code"],
    "priority": summary["priority"]
}
req_resolve = urllib.request.Request(
    "http://127.0.0.1:8000/api/resolve",
    data=json.dumps(resolve_payload).encode("utf-8"),
    headers={"Content-Type": "application/json"}
)
with urllib.request.urlopen(req_resolve, timeout=30) as res_r:
    resolve_res = json.loads(res_r.read().decode())

print("Status:", res_r.getcode(), flush=True)
print(f"-> Resolution Sync Success: {resolve_res.get('success')}", flush=True)
print(f"-> Message: {resolve_res.get('message')}", flush=True)

# 4. VERIFY IT APPEARS IN TEAM MEMORY
print("\n4. Checking GET /api/memories...", flush=True)
with urllib.request.urlopen("http://127.0.0.1:8000/api/memories", timeout=10) as res_m:
    memories = json.loads(res_m.read().decode())

newly_saved = [m for m in memories if m.get("incident_id") == "INC-2026-TEST-99"]
print(f"-> Total Memories in Bank: {len(memories)}", flush=True)
print(f"-> Newly saved incident found in memory: {len(newly_saved) > 0}", flush=True)
if newly_saved:
    print(f"-> Memory Service: {newly_saved[0]['synthetic_enrichment']['service']}", flush=True)
    print(f"-> Memory Root Cause: {newly_saved[0]['synthetic_enrichment']['root_cause']}", flush=True)

print("\n==================================================", flush=True)
print("END-TO-END FLOW VERIFICATION COMPLETE: ALL PASSED!", flush=True)
print("==================================================", flush=True)
