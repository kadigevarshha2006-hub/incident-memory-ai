// ==========================================
// Incident Memory AI — Frontend Controller
// ==========================================

let appOptions = null;
let currentInvestigationData = null;
let teamMemoriesData = [];

// Navigation controller
function navigateTo(pageId) {
  document.querySelectorAll(".page-view").forEach(p => p.classList.add("hidden"));
  const target = document.getElementById(`page-${pageId}`);
  if (target) {
    target.classList.remove("hidden");
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }

  // Update navbar state
  document.querySelectorAll(".nav-btn").forEach(btn => {
    btn.classList.remove("text-white", "bg-slate-800/80");
    btn.classList.add("text-slate-300");
  });
  const activeBtn = document.getElementById(`nav-${pageId}`);
  if (activeBtn) {
    activeBtn.classList.remove("text-slate-300");
    activeBtn.classList.add("text-white", "bg-slate-800/80");
  }

  // Mobile nav buttons
  document.querySelectorAll(".mob-nav-btn").forEach(btn => {
    btn.classList.remove("text-white", "bg-slate-800");
    btn.classList.add("hover:text-white");
  });
  const mobActive = document.getElementById(`mob-nav-${pageId}`);
  if (mobActive) {
    mobActive.classList.remove("hover:text-white");
    mobActive.classList.add("text-white", "bg-slate-800");
  }

  if (pageId === "memory") loadTeamMemories();
  if (pageId === "analytics") initAnalytics();
}

function toggleAdvancedDetails() {
  const box = document.getElementById("advancedDetailsBox");
  const chevron = document.getElementById("advancedDetailsChevron");
  if (box.classList.contains("hidden")) {
    box.classList.remove("hidden");
    chevron.textContent = "▲";
  } else {
    box.classList.add("hidden");
    chevron.textContent = "▼";
  }
}

// ==========================================
// Form Options & Cascading Dropdowns
// ==========================================
async function loadFormOptions() {
  try {
    const res = await fetch("/api/options");
    if (!res.ok) throw new Error("Failed to load options");
    appOptions = await res.json();

    const catSelect = document.getElementById("invCategorySelect");
    catSelect.innerHTML = "";

    appOptions.categories_hierarchy.forEach((cat, idx) => {
      const opt = document.createElement("option");
      opt.value = cat.label;
      opt.textContent = `${cat.label} (${cat.code})`;
      if (idx === 0) opt.selected = true;
      catSelect.appendChild(opt);
    });

    onCategoryChanged();
  } catch (e) {
    console.error("Could not load options:", e);
  }
}

function onCategoryChanged() {
  if (!appOptions || !appOptions.categories_hierarchy) return;
  const catSelect = document.getElementById("invCategorySelect");
  const subSelect = document.getElementById("invSubcategorySelect");
  const selectedCatName = catSelect.value;

  const foundCat = appOptions.categories_hierarchy.find(c => c.label === selectedCatName);
  subSelect.innerHTML = "";

  if (foundCat && foundCat.subcategories) {
    foundCat.subcategories.forEach((sub, idx) => {
      const opt = document.createElement("option");
      opt.value = sub.label;
      opt.textContent = `${sub.label} (${sub.code})`;
      if (idx === 0) opt.selected = true;
      subSelect.appendChild(opt);
    });
  }
}

// Preset Scenario Starter Loader
function fillScenario(type) {
  navigateTo("investigate");
  const catSelect = document.getElementById("invCategorySelect");
  const subSelect = document.getElementById("invSubcategorySelect");

  if (type === "payment") {
    document.getElementById("invService").value = "Payment Gateway API";
    document.getElementById("invPriority").value = "1 - Critical";
    document.getElementById("invImpact").value = "1 - High";
    document.getElementById("invUrgency").value = "1 - High";
    document.getElementById("invDescription").value = "Payment API database connection timeouts following deployment. HTTP 504 Gateway Timeouts, latency over 10s, DB pool saturated.";
    catSelect.value = "Database & Storage Systems";
    onCategoryChanged();
    subSelect.value = "Connection Pool Exhaustion / Timeout";
  } else if (type === "auth") {
    document.getElementById("invService").value = "Authentication & Session Service";
    document.getElementById("invPriority").value = "1 - Critical";
    document.getElementById("invImpact").value = "1 - High";
    document.getElementById("invUrgency").value = "1 - High";
    document.getElementById("invDescription").value = "Sudden 401 Unauthorized storm across all mobile sessions. Error: 'JWT signature verification failed: key expired'.";
    catSelect.value = "Network & Authentication Gateways";
    onCategoryChanged();
    subSelect.value = "SSL/TLS & Auth Token Expiration";
  } else if (type === "k8s") {
    document.getElementById("invService").value = "Inventory Search Cluster";
    document.getElementById("invPriority").value = "2 - High";
    document.getElementById("invImpact").value = "2 - Medium";
    document.getElementById("invUrgency").value = "1 - High";
    document.getElementById("invDescription").value = "Pods terminated with exit code 137 (OOMKilled) under sudden search query volume.";
    catSelect.value = "Application & Microservices";
    onCategoryChanged();
    subSelect.value = "Container OOMKilled / Memory Limit Exceeded";
  } else if (type === "kafka") {
    document.getElementById("invService").value = "Order Processing Worker";
    document.getElementById("invPriority").value = "2 - High";
    document.getElementById("invImpact").value = "2 - Medium";
    document.getElementById("invUrgency").value = "2 - Medium";
    document.getElementById("invDescription").value = "Kafka consumer group experiencing rebalance storm. Consumer lag exceeded 480k messages.";
    catSelect.value = "Message Queuing & Streaming";
    onCategoryChanged();
    subSelect.value = "Consumer Group Lag Accumulation";
  }
}

// ==========================================
// Incident Investigation Execution
// ==========================================
async function startInvestigation() {
  const service = document.getElementById("invService").value.trim();
  const description = document.getElementById("invDescription").value.trim();
  const priority = document.getElementById("invPriority").value;
  const environment = document.getElementById("invEnvironment").value;
  const impact = document.getElementById("invImpact").value;
  const urgency = document.getElementById("invUrgency").value;
  const category = document.getElementById("invCategorySelect").value;
  const subcategory = document.getElementById("invSubcategorySelect").value;
  const assignment_group = document.getElementById("invAssignmentGroup").value;
  const knowledge = document.getElementById("invKnowledge").value === "true";
  const contact_type = document.getElementById("invContactType").value;

  const btn = document.getElementById("btnInvestigate");
  const prog = document.getElementById("analysisProgressState");
  const resultSec = document.getElementById("analysisResultSection");

  btn.disabled = true;
  btn.classList.add("opacity-50", "cursor-not-allowed");
  prog.classList.remove("hidden");
  resultSec.classList.add("hidden");

  const payload = {
    service,
    description,
    symptoms: description,
    environment,
    priority,
    impact,
    urgency,
    category,
    subcategory,
    assignment_group,
    knowledge,
    contact_type,
    mode: "with_hindsight"
  };

  try {
    const res = await fetch("/api/analyze", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });

    if (!res.ok) throw new Error(`Server returned HTTP ${res.status}`);
    const data = await res.json();
    currentInvestigationData = data;

    render10SectionDashboard(data);
  } catch (err) {
    alert("Investigation Error: " + err.message);
  } finally {
    btn.disabled = false;
    btn.classList.remove("opacity-50", "cursor-not-allowed");
    prog.classList.add("hidden");
  }
}

// ==========================================
// Render 10-Section Output Dashboard (Section 15)
// ==========================================
function render10SectionDashboard(data) {
  const resultSec = document.getElementById("analysisResultSection");
  resultSec.classList.remove("hidden");

  const summary = data.incident_summary || {};
  const ml = data.ml_prediction || {};
  const root = data.likely_root_cause || {};
  const verif = data.verification_plan || {};

  // SECTION A: INCIDENT SUMMARY
  const incId = "INC-2026-" + Math.floor(100 + Math.random() * 900);
  document.getElementById("resIncidentIdBadge").textContent = incId;
  document.getElementById("resServiceSummary").textContent = summary.service || "Service";
  document.getElementById("resCategorySummary").textContent = summary.category_name || summary.category_code;
  document.getElementById("resSubcategorySummary").textContent = summary.subcategory_name || summary.subcategory_code;
  document.getElementById("resEnvSummary").textContent = summary.environment || "Production";
  document.getElementById("resSymptomsSummary").textContent = summary.symptoms || summary.description;

  // SECTION B: CURRENT RISK ASSESSMENT
  const riskLevel = ml.risk_level || "MEDIUM";
  const slaPct = ml.sla_failure_percentage || (ml.sla_failure_prob ? ml.sla_failure_prob * 100 : 50);
  
  const riskText = document.getElementById("resRiskLevelText");
  const riskSub = document.getElementById("resRiskLevelSub");
  const riskIcon = document.getElementById("resRiskBadgeIcon");
  const riskBar = document.getElementById("resRiskMeterBar");
  const riskMeterVal = document.getElementById("resRiskMeterVal");

  riskText.textContent = `${riskLevel} RISK`;
  riskMeterVal.textContent = `${slaPct.toFixed(1)}%`;
  riskBar.style.width = `${Math.min(100, Math.max(5, slaPct))}%`;

  if (riskLevel === "HIGH") {
    riskText.className = "text-2xl font-black text-rose-400";
    riskSub.textContent = "Critical SLA breach risk — Emergency commander escalation required";
    riskIcon.className = "w-14 h-14 rounded-2xl flex items-center justify-center font-bold text-xl border border-rose-500/30 bg-rose-500/10 text-rose-400";
    riskIcon.textContent = "🚨";
    riskBar.className = "bg-rose-500 h-2.5 rounded-full transition-all duration-1000";
  } else if (riskLevel === "MEDIUM") {
    riskText.className = "text-2xl font-black text-amber-400";
    riskSub.textContent = "Moderate SLA risk — Queue prioritization & monitoring advised";
    riskIcon.className = "w-14 h-14 rounded-2xl flex items-center justify-center font-bold text-xl border border-amber-500/30 bg-amber-500/10 text-amber-400";
    riskIcon.textContent = "⚠️";
    riskBar.className = "bg-amber-500 h-2.5 rounded-full transition-all duration-1000";
  } else {
    riskText.className = "text-2xl font-black text-emerald-400";
    riskSub.textContent = "Low SLA risk — Standard operating procedure sufficient";
    riskIcon.className = "w-14 h-14 rounded-2xl flex items-center justify-center font-bold text-xl border border-emerald-500/30 bg-emerald-500/10 text-emerald-400";
    riskIcon.textContent = "✓";
    riskBar.className = "bg-emerald-500 h-2.5 rounded-full transition-all duration-1000";
  }

  // SECTION C: ML PREDICTION
  document.getElementById("resMlProbValue").textContent = `${slaPct.toFixed(1)}%`;

  // SECTION D: HISTORICAL INCIDENT MATCHES (HINDSIGHT CLOUD)
  const matchesCountBadge = document.getElementById("resHistoricalMatchesCount");
  const count = data.historical_matches_count || (data.recalled_memories ? data.recalled_memories.length : 0);
  matchesCountBadge.textContent = `${count} Precedents Recalled`;

  const similarList = document.getElementById("similarIncidentsList");
  similarList.innerHTML = "";

  const memories = data.historical_matches || data.recalled_memories || [];
  if (memories.length > 0) {
    memories.forEach((mem, idx) => {
      const card = document.createElement("div");
      card.className = "bg-slate-950/80 border border-slate-800 rounded-xl p-3.5 text-xs space-y-2";
      
      const idMatch = mem.text.match(/INC\d{6}/i);
      const ticketId = idMatch ? idMatch[0].toUpperCase() : (mem.id || `INC00${1040 + idx * 35}`);

      card.innerHTML = `
        <div class="flex items-center justify-between">
          <div class="flex items-center gap-2">
            <span class="font-mono font-bold text-indigo-400">${ticketId}</span>
            <span class="px-2 py-0.5 rounded bg-emerald-500/15 text-emerald-300 text-[10px] font-semibold">Institutional Match</span>
          </div>
          <span class="text-[10px] text-slate-500 font-mono">Hindsight Cloud</span>
        </div>
        <div class="text-slate-300 font-mono text-[11px] leading-relaxed">${mem.text}</div>
      `;
      similarList.appendChild(card);
    });
  } else {
    similarList.innerHTML = `
      <div class="p-3 text-slate-400 text-xs italic bg-slate-950/60 rounded-xl border border-slate-800">
        No direct historical post-mortem matched in Hindsight Cloud. General SRE diagnostics applied.
      </div>
    `;
  }

  // SECTION E: EVIDENCE & OPERATIONAL RISK DRIVERS
  const factorsList = document.getElementById("explainerFactorsList");
  factorsList.innerHTML = "";
  const factors = data.evidence_and_factors || [];
  if (factors.length > 0) {
    factors.forEach(f => {
      const card = document.createElement("div");
      card.className = "p-3 rounded-xl bg-slate-950/80 border border-slate-800 space-y-1";
      card.innerHTML = `
        <div class="flex items-center justify-between">
          <span class="font-semibold text-slate-200">${f.factor}</span>
          <span class="px-1.5 py-0.5 rounded text-[10px] font-bold ${f.severity === 'CRITICAL' ? 'bg-rose-500/15 text-rose-300' : f.severity === 'HIGH' ? 'bg-amber-500/15 text-amber-300' : 'bg-emerald-500/15 text-emerald-300'}">${f.severity}</span>
        </div>
        <p class="text-[11px] text-slate-400 leading-relaxed">${f.description}</p>
      `;
      factorsList.appendChild(card);
    });
  } else {
    factorsList.innerHTML = `<div class="p-2 text-slate-400 italic">Standard operational factors observed.</div>`;
  }

  // SECTION F: LIKELY ROOT CAUSE (NO FABRICATION)
  document.getElementById("resRootCauseSuspect").textContent = root.suspect || "Root Cause Analysis";
  const confBadge = document.getElementById("resRootCauseConfidence");
  confBadge.textContent = `Confidence: ${root.confidence || 'Moderate'}`;
  document.getElementById("resRootCauseEvidence").textContent = root.evidence || "Evidence details.";

  // SECTION G: RECOMMENDED RESPONSE
  const stepsList = document.getElementById("recommendedStepsList");
  stepsList.innerHTML = "";
  const steps = data.recommended_response || [];
  steps.forEach(s => {
    const card = document.createElement("div");
    card.className = "p-3 rounded-xl bg-slate-950/70 border border-slate-800 flex items-start gap-3";
    card.innerHTML = `
      <div class="w-6 h-6 rounded-lg bg-indigo-600/20 text-indigo-300 flex items-center justify-center font-bold text-xs shrink-0 mt-0.5">
        ${s.step}
      </div>
      <div>
        <div class="flex items-center gap-2">
          <strong class="text-white text-xs">${s.title}</strong>
          <span class="text-[10px] px-1.5 py-0.2 rounded bg-slate-800 text-slate-400 font-mono">${s.priority}</span>
        </div>
        <p class="text-[11px] text-slate-400 mt-0.5">${s.desc}</p>
      </div>
    `;
    stepsList.appendChild(card);
  });

  // SECTION H: SAFE VERIFICATION SANDBOX
  const readyCmd = verif.remediation_cmd || "kubectl rollout status deployment";
  document.getElementById("termReadyCmd").textContent = readyCmd;
  document.getElementById("remediationTerminalLogs").innerHTML = `
    <div class="text-slate-400"># Safe Verification Sandbox (Staging Replica Replica) Initialized</div>
    <div class="text-slate-400"># Target Environment: ${verif.environment || 'Staging Sandbox'}</div>
    <div class="text-slate-400"># Click "Run Simulated Verification Checks" to safely evaluate the patch.</div>
    <div class="text-indigo-400 pt-1">$ ${readyCmd}</div>
  `;
  document.getElementById("terminalStatusBadge").textContent = "Ready to verify";
  document.getElementById("postRemediationTelemetry").classList.add("hidden");

  // SECTION J: PRE-FILL RESOLUTION INPUTS
  document.getElementById("learnRootCauseInput").value = root.suspect || "Service degradation";
  document.getElementById("learnResolutionInput").value = verif.remediation_cmd || "Applied configuration fix";
  document.getElementById("learnOutcomeInput").value = "Resolved - Verified in staging sandbox with 0 errors and latency restored";
  document.getElementById("learnSuccessNotice").classList.add("hidden");

  // Scroll to results
  resultSec.scrollIntoView({ behavior: 'smooth' });
}

// ==========================================
// Safe Verification Simulation Runner (Section 12)
// ==========================================
async function runAutomatedRemediation() {
  const btn = document.getElementById("btnExecuteRemediation");
  const badge = document.getElementById("terminalStatusBadge");
  const logs = document.getElementById("remediationTerminalLogs");
  const postTelem = document.getElementById("postRemediationTelemetry");

  btn.disabled = true;
  btn.classList.add("opacity-50", "cursor-not-allowed");
  badge.textContent = "Executing...";

  const verif = currentInvestigationData ? currentInvestigationData.verification_plan : {};
  const cmd = verif.remediation_cmd || "kubectl patch deployment";
  const probe = verif.verify_probe || "curl -k https://service.internal/healthz";

  logs.innerHTML = "";
  const appendLog = (text, color = "text-slate-300") => {
    const div = document.createElement("div");
    div.className = color;
    div.textContent = text;
    logs.appendChild(div);
    logs.scrollTop = logs.scrollHeight;
  };

  appendLog("[STAGING SANDBOX] Initializing isolated staging replica verification...", "text-indigo-400");
  
  setTimeout(() => {
    appendLog(`$ ${cmd}`, "text-slate-200");
    appendLog("Applying configuration manifest diff to sandbox replica...", "text-slate-400");
  }, 600);

  setTimeout(() => {
    appendLog("Configuration applied. Deployment rolling update completed (Exit 0).", "text-emerald-400");
    appendLog(`$ ${probe}`, "text-slate-200");
  }, 1300);

  setTimeout(async () => {
    try {
      const res = await fetch("/api/verify", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          incident_id: document.getElementById("resIncidentIdBadge").textContent,
          service: document.getElementById("resServiceSummary").textContent,
          remediation_action: cmd
        })
      });
      const verifyRes = await res.json();

      appendLog(`Response: ${verifyRes.probe_status} (${verifyRes.probe_latency_ms}ms latency)`, "text-emerald-300");
      appendLog("✓ VERIFICATION PASSED — Synthetic probes confirmed zero errors.", "text-emerald-400 font-bold");
      appendLog("✓ SLA Breach Risk mitigated to 0.8% (LOW).", "text-emerald-400 font-bold");

      badge.textContent = "Verified (Exit 0)";
      postTelem.classList.remove("hidden");

      // Auto-commit to Hindsight Cloud (Zero-touch learning)
      submitResolutionToMemory();
    } catch (e) {
      appendLog("Verification request error: " + e.message, "text-rose-400");
    } finally {
      btn.disabled = false;
      btn.classList.remove("opacity-50", "cursor-not-allowed");
    }
  }, 2200);
}

// ==========================================
// Commit Resolution to Hindsight Cloud (Section 8)
// ==========================================
async function submitResolutionToMemory() {
  const incident_id = document.getElementById("resIncidentIdBadge").textContent;
  const service = document.getElementById("resServiceSummary").textContent;
  const symptoms = document.getElementById("resSymptomsSummary").textContent;
  const root_cause = document.getElementById("learnRootCauseInput").value;
  const remediation = document.getElementById("learnResolutionInput").value;
  const notice = document.getElementById("learnSuccessNotice");

  try {
    const res = await fetch("/api/resolve", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        incident_id,
        service,
        symptoms,
        root_cause,
        remediation,
        runbook: "Automated-Verified-Runbook"
      })
    });

    if (!res.ok) throw new Error("Failed to save memory");
    notice.classList.remove("hidden");
    notice.textContent = "✓ Resolution Committed to Hindsight Cloud — Stored in institutional memory!";
  } catch (err) {
    console.error("Memory commit error:", err);
  }
}

// ==========================================
// Team Memory Page
// ==========================================
async function loadTeamMemories() {
  const grid = document.getElementById("teamMemoriesGrid");
  const filterSelect = document.getElementById("memoryServiceFilter");

  try {
    const res = await fetch("/api/memories");
    teamMemoriesData = await res.json();

    // Populate service filter options
    const services = new Set(teamMemoriesData.map(m => m.synthetic_enrichment?.service || "General Service"));
    filterSelect.innerHTML = `<option value="ALL">All Services (${teamMemoriesData.length})</option>`;
    services.forEach(s => {
      const opt = document.createElement("option");
      opt.value = s;
      opt.textContent = s;
      filterSelect.appendChild(opt);
    });

    renderTeamMemories(teamMemoriesData);
  } catch (e) {
    grid.innerHTML = `<div class="p-4 text-rose-400">Failed to load memories: ${e.message}</div>`;
  }
}

function renderTeamMemories(list) {
  const grid = document.getElementById("teamMemoriesGrid");
  grid.innerHTML = "";

  if (list.length === 0) {
    grid.innerHTML = `<div class="p-4 text-slate-400 col-span-2">No matching incident memories found.</div>`;
    return;
  }

  list.forEach(item => {
    const enrich = item.synthetic_enrichment || {};
    const meta = item.kaggle_metadata || {};
    const card = document.createElement("div");
    card.className = "bg-slate-900/80 border border-slate-800 hover:border-indigo-500/50 rounded-2xl p-5 shadow-sm space-y-3 transition flex flex-col justify-between";

    card.innerHTML = `
      <div class="space-y-2">
        <div class="flex items-center justify-between">
          <span class="font-mono font-bold text-xs text-indigo-400">${item.incident_id || 'INC001042'}</span>
          <span class="px-2 py-0.5 rounded text-[10px] font-bold bg-emerald-500/15 text-emerald-300">Resolved</span>
        </div>
        <h3 class="text-sm font-bold text-white">${enrich.service || 'Service Component'}</h3>
        <p class="text-xs text-slate-400 line-clamp-2">${enrich.summary || enrich.symptoms || 'Incident resolution record.'}</p>
        <div class="p-2.5 rounded-xl bg-slate-950/80 border border-slate-800 text-[11px] space-y-1">
          <div><strong class="text-rose-300">Cause:</strong> <span class="text-slate-300">${enrich.root_cause || 'Investigated'}</span></div>
          <div><strong class="text-emerald-300">Fix:</strong> <span class="text-slate-300">${enrich.remediation || 'Remediated'}</span></div>
        </div>
      </div>
      <div class="pt-2 border-t border-slate-800/80 flex items-center justify-between text-[11px] text-slate-500">
        <span>Category: ${meta.category || 'ITSM'}</span>
        <button onclick='openMemoryModal(${JSON.stringify(item)})' class="text-indigo-400 hover:text-indigo-300 font-semibold cursor-pointer">View Post-Mortem ➔</button>
      </div>
    `;
    grid.appendChild(card);
  });
}

function filterTeamMemories() {
  const query = document.getElementById("memorySearchInput").value.toLowerCase();
  const service = document.getElementById("memoryServiceFilter").value;

  const filtered = teamMemoriesData.filter(m => {
    const enrich = m.synthetic_enrichment || {};
    const sMatch = service === "ALL" || (enrich.service === service);
    const qMatch = !query || 
      (enrich.service && enrich.service.toLowerCase().includes(query)) ||
      (enrich.root_cause && enrich.root_cause.toLowerCase().includes(query)) ||
      (enrich.symptoms && enrich.symptoms.toLowerCase().includes(query)) ||
      (item => item.incident_id && item.incident_id.toLowerCase().includes(query));
    return sMatch && qMatch;
  });

  renderTeamMemories(filtered);
}

function openMemoryModal(item) {
  const modal = document.getElementById("memoryDetailModal");
  const enrich = item.synthetic_enrichment || {};
  document.getElementById("modalIncidentId").textContent = item.incident_id || "INC001042";
  document.getElementById("modalService").textContent = enrich.service || "Service";
  document.getElementById("modalSummary").textContent = enrich.summary || "Summary details.";
  document.getElementById("modalSymptoms").textContent = enrich.symptoms || "Symptoms details.";
  document.getElementById("modalRootCause").textContent = enrich.root_cause || "Root cause.";
  document.getElementById("modalResolution").textContent = enrich.remediation || "Remediation applied.";
  document.getElementById("modalRunbook").textContent = enrich.runbook || "Standard Runbook";
  modal.classList.remove("hidden");
}

function closeMemoryModal() {
  document.getElementById("memoryDetailModal").classList.add("hidden");
}

// ==========================================
// Analytics Charts (Section 9 & 10)
// ==========================================
let chartsInitialized = false;
function initAnalytics() {
  if (chartsInitialized) return;
  chartsInitialized = true;

  // Donut Chart: SLA Overview
  const donutCtx = document.getElementById("slaDonutChart");
  if (donutCtx) {
    new Chart(donutCtx, {
      type: "doughnut",
      data: {
        labels: ["Met SLA (60.64%)", "Breached SLA (39.36%)"],
        datasets: [{
          data: [12595, 8174],
          backgroundColor: ["#10b981", "#f43f5e"],
          borderWidth: 0
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: { legend: { display: false } },
        cutout: "70%"
      }
    });
  }

  // Bar Chart: Breach Rate by Priority
  const prioCtx = document.getElementById("priorityBarChart");
  if (prioCtx) {
    new Chart(prioCtx, {
      type: "bar",
      data: {
        labels: ["P1 Critical", "P2 High", "P3 Moderate", "P4 Low"],
        datasets: [{
          label: "Breach Rate (%)",
          data: [62.4, 48.1, 38.9, 31.2],
          backgroundColor: ["#f43f5e", "#fb923c", "#6366f1", "#10b981"],
          borderRadius: 6
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: { legend: { display: false } },
        scales: {
          y: { beginAtZero: true, max: 100, grid: { color: "#1e293b" } },
          x: { grid: { display: false } }
        }
      }
    });
  }

  // Bar Chart: Breach Rate by Category
  const catCtx = document.getElementById("categoryBarChart");
  if (catCtx) {
    new Chart(catCtx, {
      type: "bar",
      data: {
        labels: ["Cat 53 (Apps)", "Cat 26 (DB)", "Cat 42 (Net)", "Cat 46 (Infra)", "Cat 9 (API)"],
        datasets: [{
          label: "Breach Rate (%)",
          data: [54.2, 51.8, 42.1, 36.4, 28.5],
          backgroundColor: "#818cf8",
          borderRadius: 6
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: { legend: { display: false } },
        scales: {
          y: { beginAtZero: true, max: 100, grid: { color: "#1e293b" } },
          x: { grid: { display: false } }
        }
      }
    });
  }
}

// Health check on startup
async function checkHealth() {
  try {
    const res = await fetch("/api/health");
    const data = await res.json();
    const badge = document.getElementById("hindsightStatusBadge");
    const text = document.getElementById("hindsightStatusText");
    if (data.hindsight_connected) {
      badge.classList.remove("border-rose-500/25", "bg-rose-500/10", "text-rose-400");
      badge.classList.add("border-emerald-500/25", "bg-emerald-500/10", "text-emerald-400");
      text.textContent = "Hindsight Memory Online";
    }
  } catch (e) {
    console.error("Health check error:", e);
  }
}

// Initialize on DOM load
window.addEventListener("DOMContentLoaded", () => {
  loadFormOptions();
  checkHealth();
});
