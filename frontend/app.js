const API_BASE = "http://127.0.0.1:8000";

// UI Elements
const messagesEl = document.getElementById("messages");
const sourcesEl = document.getElementById("sources-list");
const formEl = document.getElementById("chat-form");
const inputEl = document.getElementById("question-input");
const loadingEl = document.getElementById("loading-indicator");
const sendBtn = document.getElementById("send-btn");
const statusEl = document.getElementById("api-status");
const fileInput = document.getElementById("file-input");

// -----------------------------
// UTILITIES
// -----------------------------
function appendMessage(role, text) {
  const row = document.createElement("div");
  row.className = `message-row ${role}`;

  const bubble = document.createElement("div");
  bubble.className = "message-bubble";
  bubble.textContent = text;

  row.appendChild(bubble);
  messagesEl.appendChild(row);
  messagesEl.scrollTop = messagesEl.scrollHeight;
}

function renderSources(sources) {
  sourcesEl.innerHTML = "";

  sources.forEach((src, i) => {
    const [id, text, meta] = src;

    const card = document.createElement("div");
    card.className = "source-card";

    card.innerHTML = `
      <strong>Source ${i + 1}</strong><br>
      <em>${meta?.source || "unknown"}</em><br><br>
      ${text}
    `;

    sourcesEl.appendChild(card);
  });
}

// -----------------------------
// BACKEND CHECK
// -----------------------------
async function checkBackend() {
  try {
    const res = await fetch(`${API_BASE}/`);
    if (!res.ok) throw new Error();

    statusEl.textContent = "Backend Online";
    statusEl.classList.add("status-ok");
  } catch {
    statusEl.textContent = "Backend Offline";
    statusEl.classList.add("status-error");
  }
}

// -----------------------------
// SEND QUESTION TO RAG API
// -----------------------------
async function sendQuestion(question) {
  appendMessage("user", question);

  sendBtn.disabled = true;
  loadingEl.classList.remove("hidden");

  try {
    const res = await fetch(`${API_BASE}/ask`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ question }),
    });

    const data = await res.json();

    appendMessage("assistant", data.answer || "No answer returned.");
    renderSources(data.sources || []);
  } catch (err) {
    appendMessage("assistant", "Error: unable to reach backend.");
  }

  sendBtn.disabled = false;
  loadingEl.classList.add("hidden");
}

// -----------------------------
// UPLOAD DOCUMENT
// -----------------------------
function triggerFileUpload() {
  fileInput.click();
}

fileInput.addEventListener("change", async () => {
  const file = fileInput.files[0];
  if (!file) return;

  appendMessage("assistant", `Uploading ${file.name}...`);

  const formData = new FormData();
  formData.append("file", file);

  try {
    const res = await fetch(`${API_BASE}/upload`, {
      method: "POST",
      body: formData,
    });

    const data = await res.json();
    appendMessage(
      "assistant",
      `Upload complete. Inserted ${data.chunks_inserted} chunks from ${data.filename}.`
    );

    // Auto-refresh DB viewer
    loadDBDocs();
  } catch (err) {
    appendMessage("assistant", "Upload failed.");
  }
});

// -----------------------------
// FORM SUBMIT
// -----------------------------
formEl.addEventListener("submit", (e) => {
  e.preventDefault();
  const question = inputEl.value.trim();
  if (!question) return;

  inputEl.value = "";
  sendQuestion(question);
});

// -----------------------------
// DB VIEWER — DOCUMENT LIST
// -----------------------------
async function loadDBDocs() {
  const listEl = document.getElementById("db-doc-list");
  listEl.innerHTML = "Loading...";

  try {
    const res = await fetch(`${API_BASE}/db/documents`);
    const docs = await res.json();

    listEl.innerHTML = "";

    docs.forEach(doc => {
      const item = document.createElement("div");
      item.className = "db-doc-item";

      item.onclick = () => loadDocumentChunks(doc.document);

      item.innerHTML = `
        <strong>${doc.document}</strong><br>
        <span>${doc.chunks} chunks</span>
      `;

      listEl.appendChild(item);
    });
  } catch (err) {
    listEl.innerHTML = "Error loading documents.";
  }
}

// -----------------------------
// DB VIEWER — CHUNKS FOR A DOC
// -----------------------------
async function loadDocumentChunks(docName) {
  const viewer = document.getElementById("db-chunks-viewer");
  const title = document.getElementById("db-chunks-title");
  const content = document.getElementById("db-chunks-content");

  viewer.classList.remove("hidden");
  title.textContent = `Chunks for: ${docName}`;
  content.innerHTML = "Loading...";

  try {
    const res = await fetch(`${API_BASE}/db/document/${docName}`);
    const data = await res.json();

    content.innerHTML = "";

    data.chunks.forEach(chunk => {
      const card = document.createElement("div");
      card.className = "db-chunk-card";

      card.innerHTML = `
        <strong>ID:</strong> ${chunk.id}<br><br>
        <strong>Text:</strong><br>${chunk.text}<br><br>
        <strong>Metadata:</strong><br>${JSON.stringify(chunk.metadata)}
      `;

      content.appendChild(card);
    });
  } catch (err) {
    content.innerHTML = "Error loading chunks.";
  }
}

// -----------------------------
// INIT
// -----------------------------
checkBackend();
loadDBDocs();