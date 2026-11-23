// GENERATED. Shared helpers for /noc pages. Do not edit by hand (D-070).
'use strict';
const QS = new URLSearchParams(location.search);
const PASS = ['now', 'enable'].filter(k => QS.get(k)).map(k => `${k}=${encodeURIComponent(QS.get(k))}`).join('&');
const apiURL = p => `/api/noc/${p}${PASS ? '?' + PASS : ''}`;
const getJSON = p => fetch(apiURL(p)).then(r => { if (!r.ok) throw new Error(r.status); return r.json(); });
const postJSON = (p, body) => fetch(apiURL(p), { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body || {}) })
  .then(async r => ({ status: r.status, body: await r.json().catch(() => ({})) }));
const esc = s => String(s ?? '').replace(/[&<>"]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
const LABEL = { up: 'Availability', fast: 'Performance', safe: 'Security', changed: 'Volatility', set_right: 'Configuration', capacity: 'Capacity' };
const STATUS = { green: 'Good', amber: 'Watch', red: 'Act now', no_data: 'No data', orange: 'By end of day' };
const SCREENS = ['up', 'fast', 'safe', 'changed', 'set_right', 'capacity'];
const chip = s => `<span class="chip ${s}">${STATUS[s] || s}</span>`;
// Viewer's time zone, with the zone named (spec README, rule 8).
const fmtTime = iso => new Date(iso).toLocaleTimeString('en-GB', { hour: '2-digit', minute: '2-digit', timeZoneName: 'short' });
const fmtHM = iso => new Date(iso).toLocaleTimeString('en-GB', { hour: '2-digit', minute: '2-digit' });
const num = n => Number(n).toLocaleString('en-US');
const RES = { compute: 'Compute', memory: 'Memory', storage: 'Storage' };
const ago = iso => { const m = Math.round((Date.parse(QS.get('now') || new Date().toISOString()) - Date.parse(iso)) / 60000); return m < 60 ? `${m} min ago` : `${Math.floor(m / 60)} h ${m % 60} min ago`; };
const CHANGE = { created: 'Created', deleted: 'Deleted', powered_off: 'Powered off', moved: 'Moved', resized: 'Resized' };
const UP = { vms_down_unplanned: 'VMs down, not planned', hosts_not_responding: 'Hosts not responding', clusters_lost_ha: 'Clusters without HA spare', management_down: 'Management not answering', datastores_unreachable: 'Datastores unreachable' };
const SAFE = { ssh_or_shell_enabled: 'Hosts with SSH or shell on', lockdown_off: 'Hosts with lockdown mode off', certificates_expired: 'Certificates expired', root_logins_open: 'Root logins not explained' };
function navBar(current) {
  const link = (href, text) => `<a href="${href}${PASS ? '?' + PASS : ''}"${current === href ? ' aria-current="page"' : ''}>${text}</a>`;
  return `<header class="top"><span class="name">NOC</span><nav aria-label="NOC">${link('/noc', 'Screens')}${link('/noc/alerts', 'Alerts')}${link('/noc/shift', 'Shift')}${link('/noc/wall', 'Wall view')}</nav><span class="time" id="time"></span></header>`;
}
