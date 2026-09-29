import sys
import os
import time

# Ensure backend directory is in python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from agent import incident_agent
from hindsight_service import hindsight_service

def test_full_agent_workflow():
    print("=" * 70)
    print("STEP 3: VERIFYING AI INCIDENT RESPONSE AGENT WITH HINDSIGHT")
    print("=" * 70)

    # Incident: Payment API database timeout after deployment
    test_incident = {
        "service": "Payment Gateway API",
        "description": "Payment API returning database connection timeout errors following today's v2.4 service deployment under load.",
        "symptoms": "HTTP 504 Gateway Timeouts, latency over 10s, database connection pool acquisition failures in logs.",
        "category": "Category 26",
        "subcategory": "Subcategory 174",
        "impact": "1 - High",
        "urgency": "1 - High",
        "priority": "1 - Critical",
        "assignment_group": "Group 70",
        "contact_type": "Phone",
        "knowledge": False
    }

    # 1. TEST MODE A: WITHOUT MEMORY (Generic Chatbot)
    print("\n" + "-" * 70)
    print("1. RUNNING MODE A: WITHOUT MEMORY (GENERIC CHATBOT BASELINE)")
    print("-" * 70)
    t0 = time.time()
    res_no_mem = incident_agent.analyze_without_memory(test_incident)
    t_no_mem = time.time() - t0
    print(f"Mode A completed in {t_no_mem:.2f}s:")
    print(res_no_mem["analysis"][:400] + "...\n")

    # 2. TEST MODE B: WITH HINDSIGHT (The Real Core Agent)
    print("-" * 70)
    print("2. RUNNING MODE B: WITH HINDSIGHT (PERSISTENT MEMORY + ML SLA MODEL)")
    print("-" * 70)
    t0 = time.time()
    res_mem = incident_agent.analyze_with_hindsight(test_incident)
    t_mem = time.time() - t0
    print(f"Mode B completed in {t_mem:.2f}s:")
    print(f"RandomForest SLA Failure Risk: {res_mem['sla_failure_percentage']}% ({res_mem['risk_level']})")
    print(f"Hindsight Memories Recalled: {res_mem['recalled_memories_count']} units")
    print("\n--- AGENT CONTEXTUAL REASONING ---")
    print(res_mem["analysis"])

    # 3. TEST THE CLOSED LEARNING LOOP
    print("\n" + "-" * 70)
    print("3. TESTING CLOSED-LOOP LEARNING: RECORDING A NEW EXPERIENCE INTO HINDSIGHT")
    print("-" * 70)
    new_inc_id = "INC003001"
    new_service = "Stripe Webhook Gateway"
    new_symptoms = "All incoming payment webhook events failing with HTTP 400 Bad Request signature verification errors."
    new_cause = "EC2 instance clock drifted by 320 seconds; Stripe webhook signatures reject requests older than 300 seconds."
    new_fix = "Configured chrony NTP daemon with Amazon Time Sync Service (169.254.169.123) and resynced system clock."
    new_runbook = "Runbook-NTP-Clock-Drift-Sync"

    print(f"Recording new resolution for {new_inc_id} ({new_service})...")
    learn_res = incident_agent.resolve_and_learn(
        incident_id=new_inc_id,
        service=new_service,
        symptoms=new_symptoms,
        root_cause=new_cause,
        remediation=new_fix,
        runbook=new_runbook,
        category="Category 42",
        priority="1 - Critical"
    )
    print("Retention result:", learn_res["message"])

    # Wait 2 seconds for Hindsight indexing
    time.sleep(2)

    # 4. TEST THAT HINDSIGHT IMMEDIATELY RECALLS THE NEWLY LEARNED EXPERIENCE
    print("\n" + "-" * 70)
    print("4. VERIFYING IMMEDIATE RECALL OF THE NEWLY LEARNED EXPERIENCE")
    print("-" * 70)
    second_incident_query = "Stripe Webhook Gateway payment webhook signature verification failing"
    print(f"Querying Hindsight for: '{second_incident_query}'...")
    recall_check = hindsight_service.recall_incidents(query=second_incident_query)
    
    found_new_memory = False
    if recall_check["success"]:
        print(f"Recalled {len(recall_check['response'].results)} memory units:")
        for r in recall_check["response"].results[:3]:
            preview = r.text.replace("\n", " ")[:130] + "..."
            print(f"  - [{r.type.upper()}] {preview}")
            if "clock" in r.text.lower() or "chrony" in r.text.lower() or "stripe" in r.text.lower():
                found_new_memory = True

    print("\n" + "=" * 70)
    if found_new_memory:
        print("VERIFICATION SUCCESS: THE CLOSED MEMORY LOOP IS OPERATIONAL!")
        print("Hindsight learned the new incident fix and recalled it immediately!")
    else:
        print("Warning: Newly learned memory not in top results yet.")
    print("=" * 70)

    hindsight_service.close()

if __name__ == "__main__":
    test_full_agent_workflow()
