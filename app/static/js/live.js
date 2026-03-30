/**
 * live.js — Rafraîchissement automatique du tableau d'attaques
 * Utilise fetch() vers /api/attacks toutes les 5 secondes (SSE-like)
 */

const REFRESH_INTERVAL = 5000; // 5 secondes

function formatDate(iso) {
  if (!iso) return '—';
  const d = new Date(iso);
  return d.toISOString().replace('T', ' ').substring(0, 19);
}

function getSeverityClass(sev) {
  return `severity-${sev || 'low'}`;
}

function renderRow(a) {
  return `
    <tr class="${getSeverityClass(a.severity)}">
      <td class="td-id">${a.id}</td>
      <td class="td-ip">${a.ip_address}</td>
      <td>${a.country || '—'}</td>
      <td><span class="badge type-${a.attack_type}">${a.attack_type}</span></td>
      <td>${a.target_service || '—'}</td>
      <td><span class="badge sev-${a.severity}">${a.severity}</span></td>
      <td class="td-time">${formatDate(a.timestamp)}</td>
    </tr>`;
}

async function refreshTable() {
  const tbody = document.querySelector('#attack-table tbody');
  const counter = document.getElementById('total-attacks');
  if (!tbody) return;

  try {
    const resp = await fetch('/api/attacks?limit=20');
    if (!resp.ok) return;
    const data = await resp.json();

    // Update counter
    if (counter) counter.textContent = data.total;

    // Re-render rows
    if (data.attacks && data.attacks.length > 0) {
      tbody.innerHTML = data.attacks.map(renderRow).join('');
    }

    // Flash live indicator
    const liveEl = document.getElementById('live-indicator');
    if (liveEl) {
      liveEl.style.color = '#00ff87';
      setTimeout(() => { liveEl.style.color = ''; }, 400);
    }
  } catch (e) {
    console.warn('[HoneyTrap] Refresh failed:', e.message);
  }
}

// Start polling only on dashboard page
if (document.getElementById('attack-table')) {
  setInterval(refreshTable, REFRESH_INTERVAL);
}
