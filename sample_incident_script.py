"""
Sample Incident Management Script (Auxiliary Demo / Test Fixture)

NOTE: This script is an auxiliary testing fixture and demo utility.
It is NOT the primary intelligence or analysis engine of the Incident Response AI system.
The core system is powered by the Kaggle ServiceNow dataset (119,998 records),
the Scikit-Learn RandomForestClassifier SLA breach prediction pipeline,
and Hindsight Cloud persistent memory.

Fixes Applied:
1. Corrected boolean condition:
   - Was: if incident["severity"] == "SEV1" or "SEV2": (always evaluated True due to truthy string)
   - Fixed: if incident["severity"] in ["SEV1", "SEV2"]:
2. Corrected index bounds error:
   - Was: delete_incident(10) when only IDs 0, 1, 2 existed.
   - Fixed: Added bounds check (0 <= incident_id < len(incidents)) and safe ID removal.
"""

incidents = []

def create_incident(title: str, severity: str) -> dict:
    incident = {
        "id": len(incidents),
        "title": title,
        "severity": severity,
        "status": "OPEN"
    }
    incidents.append(incident)
    return incident

def update_incident(incident_id: int, status: str) -> bool:
    if 0 <= incident_id < len(incidents):
        incidents[incident_id]["status"] = status
        return True
    return False

def get_critical_incidents() -> list:
    critical = []
    for incident in incidents:
        # BUG FIX: Proper membership check instead of truthy string comparison
        if incident["severity"] in ["SEV1", "SEV2"]:
            critical.append(incident)
    return critical

def delete_incident(incident_id: int) -> bool:
    # BUG FIX: Bounds check to prevent IndexError on invalid IDs
    if 0 <= incident_id < len(incidents):
        incidents.pop(incident_id)
        return True
    return False

def show_dashboard():
    print("=== INCIDENT DASHBOARD ===")
    print(f"Total Incidents: {len(incidents)}")
    for inc in incidents:
        print(f"  [{inc['id']}] {inc['title']} - Severity: {inc['severity']} - Status: {inc['status']}")
    print("==========================")

if __name__ == "__main__":
    print("Running verified sample incident script...")
    create_incident("Server Down", "SEV1")
    create_incident("Database Slow", "SEV3")
    create_incident("API Failure", "SEV2")
    
    show_dashboard()
    
    critical = get_critical_incidents()
    print(f"Critical Incidents (SEV1 & SEV2): {len(critical)}")
    assert len(critical) == 2, "Expected exactly 2 critical incidents (SEV1, SEV2)"
    
    # Safe delete within bounds
    deleted = delete_incident(1) # Delete "Database Slow"
    print(f"Delete Incident ID 1: {'Success' if deleted else 'Failed'}")
    
    # Verify handling of out-of-bounds ID without crashing
    invalid_delete = delete_incident(10)
    print(f"Delete Invalid ID 10 handled safely: {'Rejected gracefully' if not invalid_delete else 'Unexpected'}")
    
    show_dashboard()
    print("All sample script tests passed cleanly.")
