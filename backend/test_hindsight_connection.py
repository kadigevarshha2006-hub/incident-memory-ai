import sys
import os

# Ensure backend directory is in path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from hindsight_service import hindsight_service

def run_tests():
    print("=" * 60)
    print("STEP 1: HINDSIGHT REAL CONNECTION & MEMORY OPERATION TEST")
    print("=" * 60)
    
    print(f"\n[Config Check]")
    print(f"HINDSIGHT_API_URL: '{hindsight_service.api_url}'")
    has_key = bool(hindsight_service.api_key and hindsight_service.api_key != "placeholder_hindsight_api_key")
    print(f"HINDSIGHT_API_KEY Configured: {has_key}")
    print(f"Target Memory Bank ID: '{hindsight_service.bank_id}'")

    # 1. Connection Check
    print("\n--- 1. Testing Hindsight Server Connectivity ---")
    conn_ok, conn_msg = hindsight_service.check_connection()
    print(f"Connection Status: {'SUCCESS' if conn_ok else 'FAILED'}")
    print(f"Details: {conn_msg}")

    # 2. Minimal Retain Test
    print("\n--- 2. Testing Minimal retain() Operation ---")
    test_content = (
        "[KAGGLE AUTHENTIC METADATA]\n"
        "Incident ID: INC001042 | Category: Category 26 | Priority: 1 - Critical\n\n"
        "[SYNTHETIC / DEMO ENRICHMENT]\n"
        "Service: Payment Gateway API\n"
        "Symptoms: Database connection timeout errors following deployment\n"
        "Verified Root Cause: HikariCP connection pool exhausted due to default maxPoolSize=10\n"
        "Remediation Applied: Adjusted maxPoolSize to 50 and connectionTimeout to 30000ms"
    )
    test_metadata = {
        "incident_id": "INC001042",
        "category": "Category 26",
        "priority": "1 - Critical",
        "provenance": "Kaggle + Synthetic Demo Enrichment"
    }
    test_tags = ["payment-api", "database", "Category 26", "Critical"]

    retain_res = hindsight_service.retain_incident(
        content=test_content,
        metadata=test_metadata,
        tags=test_tags
    )
    
    if retain_res["success"]:
        print("retain() Status: SUCCESS")
        print(f"Response: {retain_res['response']}")
    else:
        print("retain() Status: FAILED (Expected with placeholder credentials)")
        print(f"Error: {retain_res['error']}")

    # 3. Minimal Recall Test
    print("\n--- 3. Testing Minimal recall() Operation ---")
    test_query = "Payment Gateway database connection timeout"
    recall_res = hindsight_service.recall_incidents(query=test_query)

    if recall_res["success"]:
        print("recall() Status: SUCCESS")
        print(f"Response: {recall_res['response']}")
    else:
        print("recall() Status: FAILED (Expected with placeholder credentials)")
        print(f"Error: {recall_res['error']}")

    print("\n" + "=" * 60)
    print("TEST EXECUTION COMPLETE")
    print("=" * 60)
    
    hindsight_service.close()

if __name__ == "__main__":
    run_tests()
