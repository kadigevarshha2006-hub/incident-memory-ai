import os
import sys
import json
import time
from typing import Dict, Any

# Ensure backend directory is in python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from hindsight_service import hindsight_service

def format_memory_content(item: Dict[str, Any]) -> str:
    km = item["kaggle_metadata"]
    se = item["synthetic_enrichment"]
    
    sla_str = "Met (made_sla = True)" if km.get("made_sla") else "Breached (made_sla = False)"
    
    content = (
        f"[KAGGLE AUTHENTIC METADATA]\n"
        f"Incident ID: {item['incident_id']}\n"
        f"Category: {km.get('category')} | Subcategory: {km.get('subcategory')}\n"
        f"Priority: {km.get('priority')} | Impact: {km.get('impact')} | Urgency: {km.get('urgency')}\n"
        f"Assignment Group: {km.get('assignment_group')} | Contact Type: {km.get('contact_type')}\n"
        f"Historical SLA Status: {sla_str}\n\n"
        f"[SYNTHETIC / DEMO ENRICHMENT]\n"
        f"Service: {se.get('service')}\n"
        f"Summary: {se.get('summary')}\n"
        f"Symptoms: {se.get('symptoms')}\n"
        f"Root Cause: {se.get('root_cause')}\n"
        f"Remediation: {se.get('remediation')}\n"
        f"Runbook: {se.get('runbook')}\n"
        f"Post-Mortem: {se.get('post_mortem')}"
    )
    return content

def seed_memories():
    seed_file = os.path.join(os.path.dirname(__file__), "seed_memories.json")
    if not os.path.exists(seed_file):
        print(f"Error: Seed file '{seed_file}' not found.")
        return

    with open(seed_file, "r", encoding="utf-8") as f:
        incidents = json.load(f)

    print("=" * 65)
    print(f"STEP 2: SEEDING {len(incidents)} CURATED MEMORIES INTO HINDSIGHT CLOUD")
    print(f"Bank ID: '{hindsight_service.bank_id}'")
    print("=" * 65)

    success_count = 0
    fail_count = 0

    for idx, inc in enumerate(incidents, 1):
        inc_id = inc["incident_id"]
        service_name = inc["synthetic_enrichment"]["service"]
        content = format_memory_content(inc)
        
        metadata = {
            "incident_id": inc_id,
            "category": inc["kaggle_metadata"].get("category", ""),
            "priority": inc["kaggle_metadata"].get("priority", ""),
            "service": service_name,
            "provenance": "Kaggle Authentic + Synthetic Demo Enrichment"
        }
        tags = inc.get("tags", [])

        print(f"[{idx}/{len(incidents)}] Retaining {inc_id} ({service_name})...", end=" ", flush=True)
        res = hindsight_service.retain_incident(
            content=content,
            metadata=metadata,
            tags=tags
        )

        if res["success"]:
            print("OK [Retained]")
            success_count += 1
        else:
            print(f"FAILED ({res['error']})")
            fail_count += 1

        # Brief pause to respect API pacing
        time.sleep(0.4)

    print("\n" + "=" * 65)
    print(f"SEEDING COMPLETE: {success_count} succeeded, {fail_count} failed")
    print("=" * 65)

    # Multi-Domain Recall Verification
    print("\n--- Running Multi-Scenario Recall Verification ---")
    test_queries = [
        "Payment API database connection pool exhausted timeout",
        "JWT signature expired 401 unauthorized errors",
        "Kubernetes pod OOMKilled exit code 137 memory limit"
    ]

    for q in test_queries:
        print(f"\nQuery: '{q}'")
        recall_res = hindsight_service.recall_incidents(query=q)
        if recall_res["success"]:
            results = recall_res["response"].results
            print(f"  Recalled {len(results)} memory units:")
            for r in results[:2]:  # Show top 2
                preview = r.text.replace("\n", " ")[:120] + "..." if len(r.text) > 120 else r.text
                print(f"  - [{r.type.upper()}] {preview}")
        else:
            print(f"  Recall error: {recall_res['error']}")

    hindsight_service.close()

if __name__ == "__main__":
    seed_memories()
