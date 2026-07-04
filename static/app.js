const messagesEl = document.getElementById("messages");
const emptyStateEl = document.getElementById("emptyState");
const textInput = document.getElementById("textInput");
const sendBtn = document.getElementById("sendBtn");
const modelSelect = document.getElementById("modelSelect");

const discordModal = document.getElementById("discordModal");
const discordBtn = document.getElementById("discordBtn");
const discordCancel = document.getElementById("discordCancel");
const discordSave = document.getElementById("discordSave");
const botTokenInput = document.getElementById("botToken");
const channelIdInput = document.getElementById("channelId");
const applicantNameInput = document.getElementById("applicantName");
const applicantEmailInput = document.getElementById("applicantEmail");

let loading = false;
let discordConfig = JSON.parse(localStorage.getItem("discordConfig") || "{}");
let applicant = JSON.parse(localStorage.getItem("applicantInfo") || "{}");

botTokenInput.value = discordConfig.botToken || "";
channelIdInput.value = discordConfig.channelId || "";
applicantNameInput.value = applicant.name || "";
applicantEmailInput.value = applicant.email || "";

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

textInput.addEventListener("keydown", (e) => {
  if (e.key === "Enter") handleSend();
});
sendBtn.addEventListener("click", () => handleSend());

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

function addReportCard(report) {
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

  card.innerHTML = `
    <h2>${escapeHtml(report.companyName || "Unknown Company")}</h2>
    ${report.website ? `<a class="website" href="${escapeAttr(report.website)}" target="_blank" rel="noreferrer">${escapeHtml(report.website)}</a>` : ""}
    <div class="report-grid">
      <div><span class="label">Phone: </span>${escapeHtml(report.phone || "N/A")}</div>
      <div><span class="label">Address: </span>${escapeHtml(report.address || "N/A")}</div>
    </div>
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

  // Fire-and-forget Discord notification if configured
  if (discordConfig.botToken && discordConfig.channelId) {
    sendToDiscord(report).catch((e) => console.warn("Discord send failed:", e));
  }
}

async function handleSend(overrideValue) {
  const query = (overrideValue ?? textInput.value).trim();
  if (!query || loading) return;

  addTextMessage("user", query);
  textInput.value = "";
  loading = true;
  sendBtn.disabled = true;
  const progressEl = addProgressMessage("Searching & crawling the web…");

  try {
    const res = await fetch("/api/research", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ input: query, model: modelSelect.value }),
    });
    const data = await res.json();
    progressEl.remove();
    if (!res.ok) throw new Error(data.error || "Something went wrong");
    addReportCard(data.result);
  } catch (err) {
    progressEl.remove();
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
  const blob = await generatePdfBlob(report);
  const buffer = await blob.arrayBuffer();
  const base64 = btoa(String.fromCharCode(...new Uint8Array(buffer)));

  await fetch("/api/discord", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      ...discordConfig,
      applicantName: applicant.name,
      applicantEmail: applicant.email,
      companyName: report.companyName,
      companyWebsite: report.website,
      pdfBase64: base64,
    }),
  });
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
