// PeakSense Dashboard - Custom Lovelace Card
// Add to your dashboard as custom card type: peaksense-dashboard

class PeakSenseDashboard extends HTMLElement {
  setConfig(config) {
    this.config = config;
    this.render();
  }

  getCardSize() {
    return 10;
  }

  render() {
    if (!this.shadowRoot) {
      this.attachShadow({ mode: 'open' });
    }

    this.shadowRoot.innerHTML = `
      <style>
        :host {
          --primary-color: #a78bfa;
          --secondary-color: #1c1f2b;
          --border-color: #2a2d3a;
        }

        .card {
          background: var(--card-background-color, #111318);
          color: var(--primary-text-color, #e4e6f0);
          border-radius: 12px;
          padding: 20px;
          font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
        }

        h1 {
          margin: 0 0 8px 0;
          font-size: 1.4rem;
          font-weight: 600;
          display: flex;
          align-items: center;
          gap: 8px;
        }

        .subtitle {
          color: #888;
          font-size: 0.85rem;
          margin-bottom: 24px;
        }

        .stats-grid {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
          gap: 12px;
          margin-bottom: 24px;
        }

        .stat-card {
          background: var(--secondary-color);
          border: 1px solid var(--border-color);
          border-radius: 12px;
          padding: 16px;
        }

        .stat-label {
          font-size: 0.75rem;
          color: #888;
          text-transform: uppercase;
          letter-spacing: 0.06em;
          margin-bottom: 6px;
        }

        .stat-value {
          font-size: 1.6rem;
          font-weight: 700;
          color: var(--primary-color);
        }

        .stat-unit {
          font-size: 0.8rem;
          color: #888;
          margin-left: 2px;
        }

        .section-title {
          font-size: 0.8rem;
          font-weight: 600;
          text-transform: uppercase;
          letter-spacing: 0.08em;
          color: #888;
          margin: 20px 0 10px 0;
        }

        .button-group {
          display: flex;
          gap: 8px;
          margin-bottom: 16px;
          flex-wrap: wrap;
        }

        button {
          background: var(--primary-color);
          color: #111;
          border: none;
          border-radius: 8px;
          padding: 8px 16px;
          font-size: 0.9rem;
          font-weight: 600;
          cursor: pointer;
          transition: background 0.15s;
        }

        button:hover {
          background: #c4b5fd;
        }

        button.secondary {
          background: var(--secondary-color);
          color: var(--primary-color);
          border: 1px solid var(--border-color);
        }

        button.secondary:hover {
          background: #2a2d3a;
        }

        .table-wrap {
          background: var(--secondary-color);
          border: 1px solid var(--border-color);
          border-radius: 12px;
          overflow: hidden;
          margin-bottom: 20px;
        }

        table {
          width: 100%;
          border-collapse: collapse;
          font-size: 0.88rem;
        }

        thead th {
          text-align: left;
          padding: 12px;
          font-size: 0.75rem;
          font-weight: 600;
          text-transform: uppercase;
          letter-spacing: 0.06em;
          color: #666;
          border-bottom: 1px solid var(--border-color);
        }

        tbody tr {
          border-bottom: 1px solid #0a0d15;
          transition: background 0.15s;
        }

        tbody tr:hover {
          background: #1c1f2b;
        }

        td {
          padding: 10px 12px;
          vertical-align: middle;
        }

        .peak-badge {
          display: inline-block;
          background: #2d1f4a;
          color: var(--primary-color);
          border-radius: 6px;
          padding: 4px 10px;
          font-weight: 700;
          font-size: 0.9rem;
        }

        .label-input {
          background: transparent;
          border: 1px solid var(--border-color);
          border-radius: 6px;
          color: #e4e6f0;
          padding: 6px 8px;
          font-size: 0.85rem;
          width: 100%;
          max-width: 150px;
          transition: border-color 0.15s;
        }

        .label-input:focus {
          outline: none;
          border-color: var(--primary-color);
          background: #1c1f2b;
        }

        .label-input.unlabeled {
          color: #666;
          font-style: italic;
        }

        .time-cell {
          color: #888;
          font-size: 0.8rem;
          white-space: nowrap;
        }

        .loading {
          text-align: center;
          padding: 40px 20px;
          color: #666;
        }

        .error {
          background: #2d1515;
          border: 1px solid #5a2020;
          color: #f87171;
          border-radius: 8px;
          padding: 12px 16px;
          margin-bottom: 16px;
          font-size: 0.85rem;
        }

        .empty-state {
          text-align: center;
          padding: 40px 20px;
          color: #555;
        }

        .empty-state-icon {
          font-size: 2rem;
          margin-bottom: 8px;
        }
      </style>

      <div class="card">
        <h1>⚡ PeakSense</h1>
        <p class="subtitle">Detecteer en label stroompieken automatisch</p>

        <div id="error" class="error" style="display:none;"></div>

        <!-- Stats -->
        <div class="stats-grid">
          <div class="stat-card">
            <div class="stat-label">Totaal pieken</div>
            <div class="stat-value" id="statTotal">—</div>
          </div>
          <div class="stat-card">
            <div class="stat-label">Onbenoemd</div>
            <div class="stat-value" id="statUnlabeled">—</div>
          </div>
          <div class="stat-card">
            <div class="stat-label">Hoogste piek</div>
            <div class="stat-value" id="statPeak">—<span class="stat-unit">W</span></div>
          </div>
          <div class="stat-card">
            <div class="stat-label">Gem. duur</div>
            <div class="stat-value" id="statDuration">—<span class="stat-unit">s</span></div>
          </div>
        </div>

        <!-- Test buttons -->
        <div class="section-title">Test & Debug</div>
        <div class="button-group">
          <button onclick="window.peakSenseCard.testPeak(900)">📊 Test 900W</button>
          <button onclick="window.peakSenseCard.testPeak(1200)">📊 Test 1200W</button>
          <button onclick="window.peakSenseCard.testPeak(1500)">📊 Test 1500W</button>
          <button class="secondary" onclick="window.peakSenseCard.loadEvents()">↻ Verversen</button>
        </div>

        <!-- Table -->
        <div class="section-title">Recente pieken</div>
        <div id="loading" class="loading">⏳ Laden...</div>
        <div class="table-wrap" id="tableWrap" style="display:none;">
          <table>
            <thead>
              <tr>
                <th>#</th>
                <th>Tijdstip</th>
                <th>Piek</th>
                <th>Gem.</th>
                <th>Duur</th>
                <th>Label</th>
              </tr>
            </thead>
            <tbody id="eventsBody">
            </tbody>
          </table>
        </div>
      </div>
    `;

    window.peakSenseCard = this;
    this.hass = null;
    this.loadEvents();
  }

  setHass(hass) {
    this.hass = hass;
  }

  async loadEvents() {
    try {
      document.getElementById('error').style.display = 'none';
      document.getElementById('loading').style.display = 'block';
      document.getElementById('tableWrap').style.display = 'none';

      const response = await fetch('/api/peaksense/events', {
        headers: {
          'Authorization': `Bearer ${this.hass?.auth?.accessToken || ''}`,
          'Content-Type': 'application/json'
        }
      });

      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      
      const events = await response.json();
      this.renderEvents(events);
      
      document.getElementById('loading').style.display = 'none';
      document.getElementById('tableWrap').style.display = 'block';
    } catch (error) {
      document.getElementById('error').textContent = '⚠️ Kon pieken niet laden: ' + error.message;
      document.getElementById('error').style.display = 'block';
      document.getElementById('loading').style.display = 'none';
    }
  }

  renderEvents(events) {
    // Stats
    document.getElementById('statTotal').textContent = events.length;
    const unlabeled = events.filter(e => !e.label || e.label === 'unknown').length;
    document.getElementById('statUnlabeled').textContent = unlabeled;
    
    const peak = events.length ? Math.max(...events.map(e => e.peak)) : 0;
    document.getElementById('statPeak').textContent = peak;
    
    const avgDur = events.length
      ? Math.round(events.reduce((s, e) => s + (e.duration || 0), 0) / events.length)
      : 0;
    document.getElementById('statDuration').textContent = avgDur;

    // Table
    const tbody = document.getElementById('eventsBody');
    if (!events.length) {
      tbody.innerHTML = `<tr><td colspan="6"><div class="empty-state">
        <div class="empty-state-icon">📊</div>
        Nog geen pieken gedetecteerd.
      </div></td></tr>`;
      return;
    }

    tbody.innerHTML = events.map(ev => {
      const start = ev.start ? new Date(ev.start).toLocaleString('nl-BE') : '—';
      const isUnlabeled = !ev.label || ev.label === 'unknown';
      const labelVal = isUnlabeled ? '' : ev.label;

      return `<tr>
        <td style="color:#555;font-size:0.78rem">${ev.id}</td>
        <td class="time-cell">${start}</td>
        <td><span class="peak-badge">${ev.peak} W</span></td>
        <td style="color:#aaa">${ev.avg} W</td>
        <td style="color:#666">${ev.duration}s</td>
        <td>
          <input
            type="text"
            class="label-input ${isUnlabeled ? 'unlabeled' : ''}"
            placeholder="Benoem..."
            value="${labelVal}"
            data-id="${ev.id}"
            onchange="window.peakSenseCard.saveLabel(this)"
            onkeydown="if(event.key==='Enter') window.peakSenseCard.saveLabel(this)"
          />
        </td>
      </tr>`;
    }).join('');
  }

  async saveLabel(input) {
    const id = input.dataset.id;
    const label = input.value.trim();
    if (!label) return;

    try {
      const response = await this.hass.callService('peaksense', 'label_event', {
        event_id: parseInt(id),
        label: label
      });
      
      input.classList.remove('unlabeled');
      input.style.background = '#2d1f4a';
      setTimeout(() => {
        input.style.background = 'transparent';
      }, 500);
    } catch (error) {
      document.getElementById('error').textContent = '⚠️ Opslaan mislukt: ' + error.message;
      document.getElementById('error').style.display = 'block';
    }
  }

  async testPeak(value) {
    try {
      await this.hass.callService('peaksense', 'update', {
        value: value
      });
      setTimeout(() => this.loadEvents(), 500);
    } catch (error) {
      document.getElementById('error').textContent = '⚠️ Test mislukt: ' + error.message;
      document.getElementById('error').style.display = 'block';
    }
  }
}

customElements.define('peaksense-dashboard', PeakSenseDashboard);

window.customCards = window.customCards || [];
window.customCards.push({
  type: 'peaksense-dashboard',
  name: 'PeakSense Dashboard',
  description: 'Dashboard voor PeakSense pieken'
});
