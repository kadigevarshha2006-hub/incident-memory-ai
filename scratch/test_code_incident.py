import urllib.request
import json

payload = {
    "service": "code",
    "description": "for incident in incidents:\n    if incident['status'] == 'OPEN':\n        open_count += 1\n    create_incident('Database Slow', 'SEV3')",
    "symptoms": "Python script loop execution error",
    "category": "Category 26",
    "subcategory": "Subcategory 174",
    "impact": "3 - Low",
    "urgency": "3 - Low",
    "priority": "4 - Low",
    "assignment_group": "Group 70",
    "contact_type": "Phone",
    "knowledge": False,
    "mode": "with_hindsight"
}

req = urllib.request.Request(
    "http://127.0.0.1:8000/api/analyze",
    data=json.dumps(payload).encode("utf-8"),
    headers={"Content-Type": "application/json"}
)

try:
    with urllib.request.urlopen(req) as res:
        data = json.loads(res.read().decode())
        print("STATUS:", res.getcode())
        print("SLA RISK:", data.get("sla_failure_percentage"))
        print("RECALLED MEMORIES COUNT:", len(data.get("recalled_memories", [])))
        print("ANALYSIS PREVIEW:", data.get("analysis", "")[:200])
except Exception as e:
    print("ERROR:", e)
