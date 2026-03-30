/**
 * charts.js — Graphiques Chart.js pour le dashboard HoneyTrap
 * Appelé depuis dashboard.html avec les données serveur
 */

const PALETTE = {
  sqli:        '#f44336',
  xss:         '#ff9800',
  brute_force: '#ce93d8',
  scan:        '#64b5f6',
  other:       '#546e7a',
  high:        '#f44336',
  medium:      '#ff9800',
  low:         '#81c784',
};

Chart.defaults.color = '#556677';
Chart.defaults.borderColor = '#1e3a4a';
Chart.defaults.font.family = "'Share Tech Mono', monospace";

function initCharts(typeData, sevData) {
  // ── Type donut ──────────────────────
  const typeCtx = document.getElementById('typeChart');
  if (typeCtx && typeData) {
    const labels = typeData.map(d => d.attack_type);
    const values = typeData.map(d => d.count);
    new Chart(typeCtx, {
      type: 'doughnut',
      data: {
        labels,
        datasets: [{
          data: values,
          backgroundColor: labels.map(l => (PALETTE[l] || '#78909c') + 'cc'),
          borderColor:     labels.map(l => PALETTE[l] || '#78909c'),
          borderWidth: 2,
        }]
      },
      options: {
        cutout: '65%',
        plugins: {
          legend: { position: 'right', labels: { font: { size: 11 }, padding: 10 } },
        }
      }
    });
  }

  // ── Severity donut ──────────────────────
  const sevCtx = document.getElementById('severityChart');
  if (sevCtx && sevData) {
    const labels = sevData.map(d => d.severity);
    const values = sevData.map(d => d.count);
    new Chart(sevCtx, {
      type: 'doughnut',
      data: {
        labels,
        datasets: [{
          data: values,
          backgroundColor: labels.map(l => (PALETTE[l] || '#78909c') + 'cc'),
          borderColor:     labels.map(l => PALETTE[l] || '#78909c'),
          borderWidth: 2,
        }]
      },
      options: {
        cutout: '65%',
        plugins: {
          legend: { position: 'right', labels: { font: { size: 11 }, padding: 10 } },
        }
      }
    });
  }

  // ── Top IPs bar chart (fetched live) ──────────────────────
  const topIpCtx = document.getElementById('topIpChart');
  if (topIpCtx) {
    fetch('/api/top-ips')
      .then(r => r.json())
      .then(data => {
        new Chart(topIpCtx, {
          type: 'bar',
          data: {
            labels: data.map(d => d.ip),
            datasets: [{
              label: 'Attaques',
              data: data.map(d => d.count),
              backgroundColor: '#00e5ff33',
              borderColor: '#00e5ff',
              borderWidth: 1,
            }]
          },
          options: {
            indexAxis: 'y',
            plugins: { legend: { display: false } },
            scales: {
              x: { grid: { color: '#1e3a4a' }, ticks: { color: '#556677' } },
              y: { grid: { color: '#1e3a4a' }, ticks: { color: '#00e5ff', font: { size: 11 } } },
            }
          }
        });
      })
      .catch(() => {});
  }
}
