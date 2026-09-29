# 60-Second Hackathon Video Demo Script
## Autonomous Engineering Incident Response Agent Powered by Hindsight

---

### **Video Overview**
* **Duration:** Exactly 60 Seconds
* **Target Audience:** Hackathon Judges, Engineering Leaders, SRE Teams
* **Core Value Prop:** Stateless AI agents forget past outages. Our agent predicts SLA breach risk using an authentic RandomForest model and recalls institutional incident memory from Hindsight Cloud to eliminate duplicate troubleshooting.

---

### **Second-by-Second Walkthrough**

| Timestamp | Visual (On Screen) | Voiceover Audio | Key Highlight |
| :--- | :--- | :--- | :--- |
| **0:00 - 0:10** | Open browser at `http://127.0.0.1:8000`. Show the dark-mode dashboard with KPI cards: **18,823 Historical Incidents**, **77.37% Accuracy**, and the pulsing green badge: **Hindsight Cloud: Connected**. | *"Every production outage costs thousands of dollars a minute. Yet when systems fail at 3 AM, engineers diagnose every incident from scratch because traditional AI agents have zero institutional memory."* | Problem statement & live connection status |
| **0:10 - 0:25** | Click the preset button: **`[💳 Payment API: DB Pool Outage]`**. Click **"Analyze Incident with Agent"**. The SLA Risk Gauge animates to **65.7% (Medium Risk)** and the **Recalled Memories** card populates. | *"Meet the Engineering Incident Response Agent. When an outage occurs, our authentic Scikit-Learn pipeline predicts the quantitative SLA breach risk—here, 65.7%. Simultaneously, the agent queries Hindsight Cloud, retrieving incident `INC001042` where a similar HikariCP connection exhaustion occurred."* | ML SLA prediction + Hindsight semantic recall |
| **0:25 - 0:40** | Scroll down to the **Agent Investigation & Runbook Plan**. Show the structured Markdown citing `INC001042` and recommending exact pool tuning commands. | *"Instead of generic advice, our agent grounds its plan in hard-won past post-mortems, prescribing the exact pool size configuration needed to prevent an SLA breach."* | Grounded incident commander reasoning |
| **0:40 - 0:55** | Scroll to the **Closed-Loop Learning** form. Type in a new fix (e.g., *Kafka consumer lag fixed by raising max.poll.interval.ms*). Click **"Save Resolution to Hindsight Cloud"**. Green banner confirms commitment. | *"Here is the breakthrough: The Closed Learning Loop. When our team resolves a new incident, one click commits the confirmed root cause back to Hindsight Cloud. Next time any service faces this issue, the agent recalls it instantly."* | Live retention into Hindsight Cloud (`retain()`) |
| **0:55 - 1:00** | Full screen on the dashboard header with GitHub link and Hindsight badge. | *"With Hindsight, your engineering organization never solves the same outage twice. Thank you!"* | Memorable closing punchline |

---

### **Preparation Checklist for Recording**
1. Ensure the server is running on `http://127.0.0.1:8000`.
2. Set browser zoom to 100% or 110% for crisp readability.
3. Keep the browser window full-screen (1080p or 1440p).
4. Have the 1-click preset buttons visible above the fold.
5. Practice clicking:
   - Click `[💳 Payment API: DB Pool Outage]`
   - Click `Analyze Incident with Agent`
   - Scroll down to review Recalled Memories and Agent Plan
   - Scroll to Closed-Loop Learning and click `Save Resolution to Hindsight Cloud`
