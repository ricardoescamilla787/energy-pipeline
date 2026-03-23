const API_BASE = "http://localhost:5000";

// Estado de la app
let currentPage  = 1;
let currentSort  = { field: "period", asc: false };
let currentTotal = 0;
let currentPages = 0;


// ── Carga inicial ─────────────────────────────────────────────────────────────

window.addEventListener("DOMContentLoaded", () => {
  loadData();
  loadStats();
});


// ── Cargar datos desde /data ──────────────────────────────────────────────────

async function loadData(page = 1) {
  currentPage = page;
  showLoading(true);
  hideStates();

  const params = new URLSearchParams({
    page:  currentPage,
    limit: getLimit(),
  });

  const dateFrom  = document.getElementById("filter-from").value;
  const dateTo    = document.getElementById("filter-to").value;
  const minOutage = document.getElementById("filter-outage").value;

  if (dateFrom)  params.append("date_from",  dateFrom);
  if (dateTo)    params.append("date_to",    dateTo);
  if (minOutage) params.append("min_outage", minOutage);

  try {
    const res  = await fetch(`${API_BASE}/data?${params}`);
    const json = await res.json();

    if (!res.ok) throw new Error(json.message || "API error");

    currentTotal = json.total;
    currentPages = json.pages;

    if (json.total === 0) {
      showEmptyState(json.message || "No data found for the selected filters.");
    } else {
      renderTable(json.data);
      renderPagination(json.page, json.pages, json.total);
    }

  } catch (err) {
    showError(err.message);
  } finally {
    showLoading(false);
  }
}


// ── Cargar estadísticas desde /stats ─────────────────────────────────────────

async function loadStats() {
  try {
    const res  = await fetch(`${API_BASE}/stats`);
    const json = await res.json();

    if (!res.ok || !json.data.length) return;

    const totalRecords = json.data.reduce((s, r) => s + r.total_records, 0);
    const years        = json.data.map(r => r.year);
    const avgPct       = json.data.reduce((s, r) => s + r.avg_percent_outage, 0) / json.data.length;

    document.getElementById("stat-total").textContent = totalRecords.toLocaleString();
    document.getElementById("stat-range").textContent = `${Math.min(...years)} – ${Math.max(...years)}`;
    document.getElementById("stat-avg").textContent   = avgPct.toFixed(1) + "%";

  } catch (_) {
    // Stats son opcionales, no mostramos error si fallan
  }
}


// ── Trigger refresh ───────────────────────────────────────────────────────────

async function triggerRefresh() {
  const btn  = document.getElementById("btn-refresh");
  const icon = document.getElementById("refresh-icon");

  btn.disabled = true;
  icon.classList.add("spinning");

  try {
    const res  = await fetch(`${API_BASE}/refresh`, { method: "POST" });
    const json = await res.json();

    if (!res.ok) throw new Error(json.message || "Refresh failed");

    const { pipeline } = json;

    if (pipeline.status === "success") {
      showToast(`✓ ${pipeline.records} new records loaded (${pipeline.period_from} → ${pipeline.period_to})`, "success");
    } else if (pipeline.status === "up_to_date") {
      showToast("Data is already up to date.", "success");
    } else {
      showToast("No data returned from the API.", "error");
    }

    document.getElementById("stat-updated").textContent = new Date().toLocaleTimeString();
    loadData(1);
    loadStats();

  } catch (err) {
    showToast(`Error: ${err.message}`, "error");
  } finally {
    btn.disabled = false;
    icon.classList.remove("spinning");
  }
}


// ── Render tabla ──────────────────────────────────────────────────────────────

function renderTable(records) {
  const tbody = document.getElementById("table-body");

  if (!records.length) {
    showEmptyState("No records match the current filters.");
    return;
  }

  // Ordenar en el cliente si se hizo click en columna
  const sorted = [...records].sort((a, b) => {
    const va = a[currentSort.field];
    const vb = b[currentSort.field];
    if (va < vb) return currentSort.asc ? -1 :  1;
    if (va > vb) return currentSort.asc ?  1 : -1;
    return 0;
  });

  tbody.innerHTML = sorted.map(row => `
    <tr>
      <td>${row.period}</td>
      <td>${Number(row.capacity).toLocaleString()}</td>
      <td>${Number(row.outage).toLocaleString()}</td>
      <td>${renderBadge(row.percent_outage)}</td>
    </tr>
  `).join("");

  document.getElementById("table-wrapper").classList.remove("hidden");
  updateSortIcons();
}


function renderBadge(pct) {
  const val = parseFloat(pct).toFixed(1);
  let cls = "badge-low";
  if (pct >= 10) cls = "badge-high";
  else if (pct >= 5) cls = "badge-mid";
  return `<span class="badge ${cls}">${val}%</span>`;
}


// ── Paginación ────────────────────────────────────────────────────────────────

function renderPagination(page, pages, total) {
  const el = document.getElementById("pagination");
  if (pages <= 1) { el.innerHTML = ""; return; }

  const limit = getLimit();
  const from  = ((page - 1) * limit) + 1;
  const to    = Math.min(page * limit, total);

  let html = `
    <button class="page-btn" onclick="loadData(1)"        ${page === 1     ? "disabled" : ""}>«</button>
    <button class="page-btn" onclick="loadData(${page-1})" ${page === 1     ? "disabled" : ""}>‹</button>
    <span class="page-info">${from}–${to} of ${total.toLocaleString()}</span>
    <button class="page-btn" onclick="loadData(${page+1})" ${page === pages ? "disabled" : ""}>›</button>
    <button class="page-btn" onclick="loadData(${pages})" ${page === pages ? "disabled" : ""}>»</button>
  `;
  el.innerHTML = html;
}


// ── Sorting ───────────────────────────────────────────────────────────────────

function sortBy(field) {
  if (currentSort.field === field) {
    currentSort.asc = !currentSort.asc;
  } else {
    currentSort = { field, asc: true };
  }
  loadData(currentPage);
}

function updateSortIcons() {
  document.querySelectorAll("th.sortable").forEach(th => {
    th.classList.remove("active");
    th.querySelector(".sort-icon").textContent = "↕";
  });
  const fields = ["period", "capacity", "outage", "percent_outage"];
  const idx    = fields.indexOf(currentSort.field);
  if (idx >= 0) {
    const headers = document.querySelectorAll("th.sortable");
    headers[idx].classList.add("active");
    headers[idx].querySelector(".sort-icon").textContent = currentSort.asc ? "↑" : "↓";
  }
}


// ── Filtros ───────────────────────────────────────────────────────────────────

function applyFilters() {
  loadData(1);
}

function clearFilters() {
  document.getElementById("filter-from").value   = "";
  document.getElementById("filter-to").value     = "";
  document.getElementById("filter-outage").value = "";
  document.getElementById("filter-limit").value  = "50";
  loadData(1);
}

function getLimit() {
  return parseInt(document.getElementById("filter-limit").value) || 50;
}


// ── UI helpers ────────────────────────────────────────────────────────────────

function showLoading(visible) {
  document.getElementById("loading").classList.toggle("hidden", !visible);
}

function hideStates() {
  document.getElementById("error-state").classList.add("hidden");
  document.getElementById("empty-state").classList.add("hidden");
  document.getElementById("table-wrapper").classList.add("hidden");
  document.getElementById("pagination").innerHTML = "";
}

function showError(msg) {
  document.getElementById("error-msg").textContent = msg;
  document.getElementById("error-state").classList.remove("hidden");
}

function showEmptyState(msg) {
  document.getElementById("empty-state").querySelector("p").innerHTML =
    msg || "No data available.";
  document.getElementById("empty-state").classList.remove("hidden");
}

function showToast(msg, type = "success") {
  const toast = document.getElementById("toast");
  toast.textContent = msg;
  toast.className   = `toast ${type}`;
  toast.classList.remove("hidden");
  setTimeout(() => toast.classList.add("hidden"), 4000);
}
