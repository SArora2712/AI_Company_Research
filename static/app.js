const messagesEl = document.getElementById("messages");
const emptyStateEl = document.getElementById("emptyState");
const textInput = document.getElementById("textInput");
const sendBtn = document.getElementById("sendBtn");
const modelSelect = document.getElementById("modelSelect");
const autocompleteList = document.getElementById("autocompleteList");
const historyList = document.getElementById("historyList");
const sidebar = document.getElementById("sidebar");
const sidebarToggle = document.getElementById("sidebarToggle");
const newResearchBtn = document.getElementById("newResearchBtn");
const themeToggle = document.getElementById("themeToggle");

const discordModal = document.getElementById("discordModal");
const discordBtn = document.getElementById("discordBtn");
const discordCancel = document.getElementById("discordCancel");
const discordSave = document.getElementById("discordSave");
const botTokenInput = document.getElementById("botToken");
const channelIdInput = document.getElementById("channelId");
const applicantNameInput = document.getElementById("applicantName");
const applicantEmailInput = document.getElementById("applicantEmail");

let loading = false;
let acItems = [];
let acActiveIndex = -1;
let acDebounce = null;

let discordConfig = JSON.parse(localStorage.getItem("discordConfig") || "{}");
let applicant = JSON.parse(localStorage.getItem("applicantInfo") || "{}");
let history = JSON.parse(localStorage.getItem("researchHistory") || "[]");

botTokenInput.value = discordConfig.botToken || "";
channelIdInput.value = discordConfig.channelId || "";
applicantNameInput.value = applicant.name || "";
applicantEmailInput.value = applicant.email || "";

/* ---------------- Theme ---------------- */
const savedTheme = localStorage.getItem("theme") || "dark";
document.documentElement.setAttribute("data-theme", savedTheme);
updateThemeBtn();

themeToggle.onclick = () => {
  const current = document.documentElement.getAttribute("data-theme");
  const next = current === "dark" ? "light" : "dark";
  document.documentElement.setAttribute("data-theme", next);
  localStorage.setItem("theme", next);
  updateThemeBtn();
};

function updateThemeBtn() {
  const current = document.documentElement.getAttribute("data-theme");
  themeToggle.textContent = current === "dark" ? "🌙 Dark Mode" : "☀️ Light Mode";
}

/* ---------------- Sidebar (mobile) ---------------- */
sidebarToggle.onclick = () => sidebar.classList.toggle("open");

newResearchBtn.onclick = () => {
  messagesEl.innerHTML = "";
  messagesEl.style.display = "none";
  emptyStateEl.style.display = "flex";
  textInput.value = "";
  sidebar.classList.remove("open");
};

/* ---------------- Discord modal ---------------- */
discordBtn.onclick = () => (discordModal.style.display = "flex");
discordCancel.onclick = () => (discordModal.style.display = "none");
discordSave.onclick = () => {
  discordConfig = { botToken: botTokenInput.value.trim(), channelId: channelIdInput.value.trim() };
  applicant = { name: applicantNameInput.value.trim(), email: applicantEmailInput.value.trim() };
  localStorage.setItem("discordConfig", JSON.stringify(discordConfig));
  localStorage.setItem("applicantInfo", JSON.stringify(applicant));
  discordModal.style.display = "none";
};

document.querySelectorAll(".suggestion-chip").forEach((chip) => {
  chip.addEventListener("click", () => handleSend(chip.dataset.value));
});

/* ---------------- Autocomplete ---------------- */
textInput.addEventListener("input", () => {
  const q = textInput.value.trim();
  clearTimeout(acDebounce);
  if (!q) return hideAutocomplete();
  acDebounce = setTimeout(() => fetchSuggestions(q), 150);
});

textInput.addEventListener("keydown", (e) => {
  if (autocompleteList.style.display !== "none" && acItems.length) {
    if (e.key === "ArrowDown") {
      e.preventDefault();
      acActiveIndex = Math.min(acActiveIndex + 1, acItems.length - 1);
      renderAutocomplete();
      return;
    }
    if (e.key === "ArrowUp") {
      e.preventDefault();
      acActiveIndex = Math.max(acActiveIndex - 1, 0);
      renderAutocomplete();
      return;
    }
    if (e.key === "Enter" && acActiveIndex >= 0) {
      e.preventDefault();
      selectSuggestion(acItems[acActiveIndex]);
      return;
    }
    if (e.key === "Escape") {
      hideAutocomplete();
      return;
    }
  }
  if (e.key === "Enter") handleSend();
});

document.addEventListener("click", (e) => {
  if (!e.target.closest(".autocomplete-wrap")) hideAutocomplete();
});

sendBtn.addEventListener("click", () => handleSend());

async function fetchSuggestions(query) {
  try {
    const res = await fetch(`/api/suggestions?q=${encodeURIComponent(query)}`);
    const data = await res.json();
    acItems = data.results || [];
    acActiveIndex = -1;
    renderAutocomplete();
  } catch (e) {
    hideAutocomplete();
  }
}

function renderAutocomplete() {
  if (!acItems.length) return hideAutocomplete();
  autocompleteList.style.display = "block";
  autocompleteList.innerHTML = acItems
    .map(
      (item, i) => `
      <div class="ac-item ${i === acActiveIndex ? "active" : ""}" data-index="${i}">
        <div>
          <div class="ac-name">${escapeHtml(item.name)}</div>
          <div class="ac-domain">${escapeHtml(item.domain)}</div>
        </div>
        <div class="ac-category">${escapeHtml(item.category)}</div>
      </div>`
    )
    .join("");

  autocompleteList.querySelectorAll(".ac-item").forEach((el) => {
    el.addEventListener("click", () => selectSuggestion(acItems[Number(el.dataset.index)]));
  });
}

function selectSuggestion(item) {
  hideAutocomplete();
  handleSend(item.domain);
}

function hideAutocomplete() {
  autocompleteList.style.display = "none";
  autocompleteList.innerHTML = "";
  acItems = [];
  acActiveIndex = -1;
}

/* ---------------- Chat rendering ---------------- */
function showMessages() {
  emptyStateEl.style.display = "none";
  messagesEl.style.display = "flex";
}

function scrollToBottom() {
  messagesEl.scrollTo({ top: messagesEl.scrollHeight, behavior: "smooth" });
}

function addTextMessage(role, content) {
  showMessages();
  const div = document.createElement("div");
  div.className = `msg ${role}`;
  div.textContent = content;
  messagesEl.appendChild(div);
  scrollToBottom();
  return div;
}

function addProgressMessage(text) {
  showMessages();
  const div = document.createElement("div");
  div.className = "msg ai progress";
  div.innerHTML = `<div class="spinner"></div> <span>${text}</span>`;
  messagesEl.appendChild(div);
  scrollToBottom();
  return div;
}

function gaugeCircle(value, id) {
  const v = Math.max(0, Math.min(100, Number(value) || 0));
  const r = 30;
  const c = 2 * Math.PI * r;
  const offset = c * (1 - v / 100);
  return `
    <div class="gauge-ring">
      <svg width="76" height="76" viewBox="0 0 76 76">
        <circle class="ring-bg" cx="38" cy="38" r="${r}"></circle>
        <circle class="ring-fg" id="${id}" cx="38" cy="38" r="${r}"
          stroke-dasharray="${c}" stroke-dashoffset="${c}"></circle>
      </svg>
      <div class="gauge-value">${v}</div>
    </div>`;
}

function addReportCard(report, cached) {
  showMessages();
  const card = document.createElement("div");
  card.className = "report-card";

  const productsHtml = (report.products || [])
    .map((p) => `<span class="pill">${escapeHtml(p)}</span>`)
    .join("");

  const painHtml = (report.painPoints || [])
    .map((p) => `<li>${escapeHtml(p)}</li>`)
    .join("");

  const compHtml = (report.competitors || [])
    .map(
      (c) =>
        `<li>${escapeHtml(c.name)} ${
          c.website ? `<a href="${escapeAttr(c.website)}" target="_blank" rel="noreferrer">(${escapeHtml(c.website)})</a>` : ""
        }</li>`
    )
    .join("");

  const insight = report.insight || {};
  const hasInsight =
    insight.overallScore !== undefined ||
    insight.marketPosition !== undefined ||
    insight.digitalPresence !== undefined ||
    insight.growthPotential !== undefined;

  const gaugeUid = Math.random().toString(36).slice(2, 8);
  const insightHtml = hasInsight
    ? `
    <div class="section-title">AI Insight Score</div>
    <div class="insight-box">
      ${insight.insightSummary ? `<div class="insight-summary">${escapeHtml(insight.insightSummary)}</div>` : ""}
      <div class="gauge-grid">
        <div class="gauge">${gaugeCircle(insight.overallScore, `g-overall-${gaugeUid}`)}<div class="gauge-label">Overall</div></div>
        <div class="gauge">${gaugeCircle(insight.marketPosition, `g-market-${gaugeUid}`)}<div class="gauge-label">Market Position</div></div>
        <div class="gauge">${gaugeCircle(insight.digitalPresence, `g-digital-${gaugeUid}`)}<div class="gauge-label">Digital Presence</div></div>
        <div class="gauge">${gaugeCircle(insight.growthPotential, `g-growth-${gaugeUid}`)}<div class="gauge-label">Growth Potential</div></div>
      </div>
    </div>`
    : "";

  card.innerHTML = `
    <h2>${escapeHtml(report.companyName || "Unknown Company")}${cached ? '<span class="cached-badge">⚡ from cache</span>' : ""}</h2>
    ${report.website ? `<a class="website" href="${escapeAttr(report.website)}" target="_blank" rel="noreferrer">${escapeHtml(report.website)}</a>` : ""}
    <div class="report-grid">
      <div><span class="label">Phone: </span>${escapeHtml(report.phone || "N/A")}</div>
      <div><span class="label">Address: </span>${escapeHtml(report.address || "N/A")}</div>
    </div>
    ${insightHtml}
    ${report.summary ? `<div class="section-title">Summary</div><p style="font-size:13.5px;line-height:1.6;">${escapeHtml(report.summary)}</p>` : ""}
    ${productsHtml ? `<div class="section-title">Products / Services</div><div class="pill-list">${productsHtml}</div>` : ""}
    ${painHtml ? `<div class="section-title">AI-Generated Pain Points</div><ul class="pain-list">${painHtml}</ul>` : ""}
    ${compHtml ? `<div class="section-title">Competitors</div><ul class="comp-list">${compHtml}</ul>` : ""}
  `;

  const downloadBtn = document.createElement("button");
  downloadBtn.className = "download-btn";
  downloadBtn.textContent = "⬇ Download PDF Report";
  downloadBtn.onclick = () => handleDownload(report, downloadBtn);
  card.appendChild(downloadBtn);

  messagesEl.appendChild(card);
  scrollToBottom();

  // Animate gauges in on next frame (so the CSS transition actually plays)
  requestAnimationFrame(() => {
    requestAnimationFrame(() => {
      const r = 30;
      const c = 2 * Math.PI * r;
      const setRing = (id, value) => {
        const el = document.getElementById(id);
        if (!el) return;
        const v = Math.max(0, Math.min(100, Number(value) || 0));
        el.style.strokeDashoffset = c * (1 - v / 100);
      };
      setRing(`g-overall-${gaugeUid}`, insight.overallScore);
      setRing(`g-market-${gaugeUid}`, insight.marketPosition);
      setRing(`g-digital-${gaugeUid}`, insight.digitalPresence);
      setRing(`g-growth-${gaugeUid}`, insight.growthPotential);
    });
  });

  addToHistory(report);

  // Fire-and-forget Discord notification if configured
  if (discordConfig.botToken && discordConfig.channelId) {
    sendToDiscord(report).catch((e) => console.warn("Discord send failed:", e));
  }
}

/* ---------------- History sidebar ---------------- */
function addToHistory(report) {
  const entry = {
    id: Date.now().toString(36),
    timestamp: Date.now(),
    companyName: report.companyName || "Unknown",
    overallScore: report.insight?.overallScore,
    report: report
  };

  history = history.filter(h => h.companyName.toLowerCase() !== entry.companyName.toLowerCase());
  history.unshift(entry);
  history = history.slice(0, 12);
  localStorage.setItem("researchHistory", JSON.stringify(history));
  renderHistory();
}

function renderHistory() {
  if (!history.length) {
    historyList.innerHTML = `<div class="history-empty">Your researched companies will appear here.</div>`;
    return;
  }

  historyList.innerHTML = history.map(h => `
    <div class="history-item" data-id="${h.id}">
      <div class="h-main">
        <span class="h-name">${escapeHtml(h.companyName)}</span>
        ${h.overallScore ? `<span class="h-score">${h.overallScore}</span>` : ''}
      </div>
      <button class="h-remove" data-remove="${h.id}" title="Remove">✕</button>
    </div>
  `).join("");

  historyList.querySelectorAll(".history-item").forEach(el => {
    el.addEventListener("click", (e) => {
      if (e.target.classList.contains("h-remove")) return;
      const entry = history.find(h => h.id === el.dataset.id);
      if (entry) {
        messagesEl.innerHTML = "";
        addTextMessage("user", entry.companyName);
        addReportCard(entry.report, true);
      }
    });
  });

  historyList.querySelectorAll(".h-remove").forEach(btn => {
    btn.addEventListener("click", (e) => {
      e.stopPropagation();
      history = history.filter(h => h.id !== btn.dataset.remove);
      localStorage.setItem("researchHistory", JSON.stringify(history));
      renderHistory();
    });
  });
}
 
renderHistory();

/* ---------------- Research flow ---------------- */
async function handleSend(overrideValue) {
  const query = (overrideValue ?? textInput.value).trim();
  if (!query || loading) return;

  hideAutocomplete();
  addTextMessage("user", query);
  textInput.value = "";
  loading = true;
  sendBtn.disabled = true;

  const steps = [
    "Searching with Serper.dev...",
    "Finding official website...",
    "Crawling key pages...",
    "Analyzing with AI...",
    "Researching competitors...",
    "Generating report & PDF..."
  ];

  let progressEl = addProgressMessage(steps[0]);
  let stepIndex = 0;

  // Faster step updates
  const progressInterval = setInterval(() => {
    stepIndex++;
    if (stepIndex < steps.length && progressEl) {
      progressEl.innerHTML = `<div class="spinner"></div> <span>${steps[stepIndex]}</span>`;
    } else {
      clearInterval(progressInterval);
    }
  }, 550);   // Faster than before

  try {
    const res = await fetch("/api/research", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ input: query, model: modelSelect.value }),
    });

    clearInterval(progressInterval);
    if (progressEl) progressEl.remove();

    const data = await res.json();
    if (!res.ok) throw new Error(data.error || "Research failed");

    addReportCard(data.result, !!data.cached);
  } catch (err) {
    clearInterval(progressInterval);
    if (progressEl) progressEl.remove();
    addTextMessage("ai", `⚠️ ${err.message}`);
  } finally {
    loading = false;
    sendBtn.disabled = false;
  }
}

async function generatePdfBlob(report) {
  const res = await fetch("/api/pdf", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(report),
  });
  if (!res.ok) throw new Error("PDF generation failed");
  return res.blob();
}

async function handleDownload(report, btn) {
  const original = btn.textContent;
  btn.disabled = true;
  btn.textContent = "Generating…";
  try {
    const blob = await generatePdfBlob(report);
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `${(report.companyName || "company").replace(/[^a-z0-9]/gi, "_")}_report.pdf`;
    a.click();
    URL.revokeObjectURL(url);
  } catch (e) {
    alert(e.message);
  } finally {
    btn.disabled = false;
    btn.textContent = original;
  }
}

async function sendToDiscord(report) {
  if (!discordConfig.botToken || !discordConfig.channelId) return;

  try {
    const blob = await generatePdfBlob(report);
    const buffer = await blob.arrayBuffer();
    const base64 = btoa(String.fromCharCode(...new Uint8Array(buffer)));

    const res = await fetch("/api/discord", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        botToken: discordConfig.botToken,
        channelId: discordConfig.channelId,
        applicantName: applicant.name || "N/A",
        applicantEmail: applicant.email || "N/A",
        companyName: report.companyName,
        companyWebsite: report.website,
        pdfBase64: base64,
      }),
    });

    const data = await res.json();
    if (!data.ok) console.warn("Discord send failed:", data);
  } catch (e) {
    console.warn("Discord notification failed:", e);
  }
}

function escapeHtml(str) {
  if (str === undefined || str === null) return "";
  return String(str)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;");
}
function escapeAttr(str) {
  return escapeHtml(str).replace(/"/g, "&quot;");
}
