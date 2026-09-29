"""
Category and Subcategory Two-Way Mapper
Translates human-friendly ITIL incident categories to authentic Kaggle ServiceNow dataset tokens
and vice-versa, ensuring users never deal with raw numeric codes.
"""

from typing import Dict, Any, List, Tuple

CATEGORY_HIERARCHY: Dict[str, Dict[str, Any]] = {
    "Database & Storage Systems": {
        "code": "Category 26",
        "description": "Relational databases, connection pools, cache clusters, and persistent storage",
        "subcategories": {
            "Connection Pool Exhaustion / Timeout": "Subcategory 174",
            "Slow Queries / Lock Contention": "Subcategory 175",
            "Storage Volume Capacity Full": "Subcategory 275",
            "Database Replication Lag / Deadlock": "Subcategory 164"
        }
    },
    "Network & Authentication Gateways": {
        "code": "Category 42",
        "description": "API gateways, ingress controllers, JWT/OAuth tokens, and SSL certificates",
        "subcategories": {
            "SSL/TLS & Auth Token Expiration": "Subcategory 223",
            "HTTP 504 / Gateway Network Timeout": "Subcategory 174",
            "Internal DNS Resolution Failure": "Subcategory 31",
            "Firewall Rule Dropping Connections": "Subcategory 29"
        }
    },
    "Application & Microservices": {
        "code": "Category 53",
        "description": "Backend services, container runtime, API controllers, and business logic",
        "subcategories": {
            "Container OOMKilled / Memory Limit Exceeded": "Subcategory 174",
            "CrashLoopBackOff / Startup Failure": "Subcategory 303",
            "Queue Backpressure / Task Starvation": "Subcategory 114",
            "Thread Pool Exhaustion / Deadlock": "Subcategory 168"
        }
    },
    "Infrastructure & Cloud Compute": {
        "code": "Category 46",
        "description": "Kubernetes worker nodes, virtual machines, hypervisors, and compute clusters",
        "subcategories": {
            "Node Resource Eviction / Disk Pressure": "Subcategory 223",
            "CPU Throttling / Sched Load Spikes": "Subcategory 174",
            "DaemonSet / Container Runtime Failure": "Subcategory 150",
            "Host Network Interface Congestion": "Subcategory 231"
        }
    },
    "External APIs & Third-Party Vendors": {
        "code": "Category 9",
        "description": "Third-party payment gateways, external SaaS integrations, and vendor webhooks",
        "subcategories": {
            "Third-Party Partner Webhook Delivery Failure": "Subcategory 164",
            "External Payment / Banking Provider Timeout": "Subcategory 174",
            "Vendor Rate Limiting / 429 Quota Exceeded": "Subcategory 202"
        }
    },
    "Security & Identity Access": {
        "code": "Category 23",
        "description": "IAM permissions, credential vaults, secrets management, and access control",
        "subcategories": {
            "IAM Role / Token Permission Denied": "Subcategory 174",
            "Vault Secrets Sync Interruption": "Subcategory 223"
        }
    },
    "Message Queuing & Streaming": {
        "code": "Category 32",
        "description": "Kafka brokers, RabbitMQ queues, pub/sub topics, and streaming workers",
        "subcategories": {
            "Consumer Group Lag Accumulation": "Subcategory 174",
            "Kafka Partition Leader Offline": "Subcategory 223"
        }
    }
}

# Reverse lookup maps
CODE_TO_CATEGORY: Dict[str, str] = {
    meta["code"]: cat_name for cat_name, meta in CATEGORY_HIERARCHY.items()
}

CODE_TO_SUBCATEGORY: Dict[Tuple[str, str], str] = {
    (meta["code"], sub_code): sub_name
    for cat_name, meta in CATEGORY_HIERARCHY.items()
    for sub_name, sub_code in meta["subcategories"].items()
}

# Human-readable Impact, Urgency, Priority mappings
IMPACT_MAPPING = {
    "High (Organization / Enterprise Wide)": "1 - High",
    "Medium (Multiple Services or User Groups)": "2 - Medium",
    "Low (Isolated / Single Non-Critical Component)": "3 - Low"
}

URGENCY_MAPPING = {
    "High (Immediate Outage / Revenue Impairing)": "1 - High",
    "Medium (Degraded Performance / Workaround Active)": "2 - Medium",
    "Low (Minor Annoyance / Routine Request)": "3 - Low"
}

PRIORITY_MAPPING = {
    "Critical (P1 - Emergency Incident Response)": "1 - Critical",
    "High (P2 - Urgent Production Degradation)": "2 - High",
    "Moderate (P3 - Standard Service Disruption)": "3 - Moderate",
    "Low (P4 - Minor Operational Defect)": "4 - Low"
}

ASSIGNMENT_GROUPS = [
    {"label": "Tier-1 SRE & Incident Commander (Group 70)", "value": "Group 70"},
    {"label": "Platform Infrastructure & Cloud Ops (Group 25)", "value": "Group 25"},
    {"label": "Core Software Engineering (Group 24)", "value": "Group 24"},
    {"label": "Network & Edge Systems (Group 39)", "value": "Group 39"},
    {"label": "Security Operations & IAM (Group 18)", "value": "Group 18"}
]

def resolve_category(category_input: str) -> str:
    """Returns the dataset code (e.g. 'Category 26') from either friendly label or code."""
    if not category_input:
        return "Category 26"
    if category_input in CATEGORY_HIERARCHY:
        return CATEGORY_HIERARCHY[category_input]["code"]
    if category_input.startswith("Category "):
        return category_input
    # Search by keyword match
    c_lower = category_input.lower()
    for cat_name, meta in CATEGORY_HIERARCHY.items():
        if c_lower in cat_name.lower():
            return meta["code"]
    return "Category 26"

def resolve_subcategory(category_input: str, subcategory_input: str) -> str:
    """Returns the dataset subcategory code (e.g. 'Subcategory 174')."""
    if not subcategory_input:
        return "Subcategory 174"
    if subcategory_input.startswith("Subcategory "):
        return subcategory_input
    
    # Check in category hierarchy
    for cat_name, meta in CATEGORY_HIERARCHY.items():
        if subcategory_input in meta["subcategories"]:
            return meta["subcategories"][subcategory_input]
        for sub_name, sub_code in meta["subcategories"].items():
            if subcategory_input.lower() in sub_name.lower():
                return sub_code
    return "Subcategory 174"

def get_friendly_category_label(cat_code: str) -> str:
    """Translates 'Category 26' -> 'Database & Storage Systems'."""
    return CODE_TO_CATEGORY.get(cat_code, cat_code)

def get_friendly_subcategory_label(cat_code: str, sub_code: str) -> str:
    """Translates ('Category 26', 'Subcategory 174') -> 'Connection Pool Exhaustion / Timeout'."""
    return CODE_TO_SUBCATEGORY.get((cat_code, sub_code), sub_code)

def get_options_payload() -> Dict[str, Any]:
    """Generates user-friendly options for frontend intake form."""
    categories_list = []
    for cat_name, meta in CATEGORY_HIERARCHY.items():
        categories_list.append({
            "label": cat_name,
            "code": meta["code"],
            "description": meta["description"],
            "subcategories": [
                {"label": sub_name, "code": sub_code}
                for sub_name, sub_code in meta["subcategories"].items()
            ]
        })
        
    return {
        "categories_hierarchy": categories_list,
        "impact_options": [
            {"label": k, "value": v} for k, v in IMPACT_MAPPING.items()
        ],
        "urgency_options": [
            {"label": k, "value": v} for k, v in URGENCY_MAPPING.items()
        ],
        "priority_options": [
            {"label": k, "value": v} for k, v in PRIORITY_MAPPING.items()
        ],
        "assignment_groups": ASSIGNMENT_GROUPS
    }
