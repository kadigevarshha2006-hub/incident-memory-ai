from typing import Dict, Any, List

class IncidentExplainer:
    """
    Independent explainer and prescriptive recommendation engine.
    Analyzes ticket metadata against ITSM operational heuristics to explain
    SLA risk factors and prescribe actionable mitigation steps without
    altering the core ML estimator.
    """

    def explain(self, incident: Dict[str, Any], failure_prob: float, risk_level: str) -> Dict[str, Any]:
        risk_factors = []
        recommendations = []

        impact = str(incident.get("impact", "")).lower()
        urgency = str(incident.get("urgency", "")).lower()
        priority = str(incident.get("priority", "")).lower()
        knowledge = incident.get("knowledge", False)
        group = str(incident.get("assignment_group", ""))
        contact = str(incident.get("contact_type", "")).lower()
        category = str(incident.get("category", ""))

        # 1. Evaluate Urgency & Priority SLA Windows
        if "1" in urgency or "high" in urgency or "critical" in priority:
            risk_factors.append({
                "factor": "Compressed SLA Target Window",
                "severity": "CRITICAL",
                "impact_direction": "INCREASES_RISK",
                "description": f"Incident classified as {incident.get('priority', 'Critical')} with High Urgency. The allowable resolution window is tightly constrained."
            })
        elif "2" in urgency or "medium" in urgency:
            risk_factors.append({
                "factor": "Standard Priority Window",
                "severity": "MODERATE",
                "impact_direction": "NEUTRAL",
                "description": "Standard response window allocated. Requires timely assignment to prevent queue backlog."
            })

        # 2. Evaluate Knowledge Base Availability
        if not knowledge:
            risk_factors.append({
                "factor": "Missing Knowledge Base Article",
                "severity": "HIGH",
                "impact_direction": "INCREASES_RISK",
                "description": "No pre-existing standard operating procedure (SOP) or KB article is attached. Triage requires manual investigation, increasing mean time to resolve (MTTR)."
            })
        else:
            risk_factors.append({
                "factor": "Verified Knowledge Base Linked",
                "severity": "LOW",
                "impact_direction": "DECREASES_RISK",
                "description": "Documented knowledge article is available for the technician, streamlining initial diagnostic verification."
            })

        # 3. Evaluate Assignment Group Queue Profile
        if any(hot_group in group for hot_group in ["Group 70", "Group 24", "Group 25", "Tier 3"]):
            risk_factors.append({
                "factor": "Specialized Queue Workload",
                "severity": "HIGH" if risk_level == "HIGH" else "MODERATE",
                "impact_direction": "INCREASES_RISK",
                "description": f"Assignment to {group} involves specialized domain engineering with higher WIP queue depth."
            })

        # 4. Evaluate Intake Channel
        if "phone" in contact:
            risk_factors.append({
                "factor": "Direct Outage Contact Channel",
                "severity": "MODERATE",
                "impact_direction": "INCREASES_RISK",
                "description": "Phone-originated incidents typically indicate active service degradation with active user impact."
            })

        # 5. Formulate Prescriptive Recommendations based on Risk Level & Factors
        if risk_level == "HIGH":
            recommendations.append({
                "priority": "P1 - IMMEDIATE",
                "title": "Trigger Incident Commander & On-Call Page",
                "action": f"Auto-escalate to primary and secondary on-call engineers in {group}. Notify Incident Management bridge.",
                "type": "Escalation"
            })
            if not knowledge:
                recommendations.append({
                    "priority": "P2 - MITIGATION",
                    "title": "Dispatch Emergency Diagnostic Checklist",
                    "action": f"Since no KB article is linked for {category}, dispatch diagnostic capture scripts to isolate root cause immediately.",
                    "type": "Resolution Acceleration"
                })
            recommendations.append({
                "priority": "P2 - MONITORING",
                "title": "Set 30-Minute SLA Watchdog",
                "action": "Set automated threshold notification at 50% SLA elapsed time. Pre-alert service owners if diagnostic isn't complete.",
                "type": "SLA Protection"
            })
        elif risk_level == "MEDIUM":
            recommendations.append({
                "priority": "P2 - PROACTIVE",
                "title": "Queue Prioritization & Triage Review",
                "action": f"Promote ticket in {group} queue. Team lead should confirm ownership within 45 minutes.",
                "type": "Triage"
            })
            if not knowledge:
                recommendations.append({
                    "priority": "P3 - SUPPORT",
                    "title": "Search Historical Incident Solutions",
                    "action": f"Query closed incidents matching category '{category}' to attach similar resolution patterns.",
                    "type": "Knowledge"
                })
            recommendations.append({
                "priority": "P3 - MONITORING",
                "title": "60-Minute Progress Checkpoint",
                "action": "Trigger automated alert to shift lead if ticket state remains 'New' or 'Assigned' after 60 minutes.",
                "type": "SLA Protection"
            })
        else: # LOW risk
            recommendations.append({
                "priority": "P3 - STANDARD",
                "title": "Proceed with Standard Queue Flow",
                "action": f"Route through standard FIFO queue for {group}. Expected resolution well within SLA margin.",
                "type": "Standard Operations"
            })
            recommendations.append({
                "priority": "P4 - VERIFICATION",
                "title": "Automated Requester Acknowledgment",
                "action": "Send confirmation to requester with expected service window and standard self-service portal link.",
                "type": "Communication"
            })

        return {
            "risk_factors": risk_factors,
            "recommendations": recommendations,
            "summary": self._generate_summary(risk_level, failure_prob, knowledge, priority)
        }

    def _generate_summary(self, risk_level: str, failure_prob: float, knowledge: bool, priority: str) -> str:
        prob_pct = f"{failure_prob * 100:.1f}%"
        if risk_level == "HIGH":
            kb_note = " compounded by the absence of a documented resolution runbook" if not knowledge else ""
            return f"Incident exhibits high SLA breach risk ({prob_pct}){kb_note}. Urgent operational intervention and queue escalation are advised."
        elif risk_level == "MEDIUM":
            return f"Incident presents moderate SLA breach probability ({prob_pct}). Active queue monitoring and timely engineer pickup recommended."
        else:
            return f"Incident is within healthy operational parameters ({prob_pct} breach risk). Standard operating procedure suffices."

incident_explainer = IncidentExplainer()
