// GENERATED from spec/workspaces/capacity/. Do not edit by hand (D-070).
'use strict';
const QS = new URLSearchParams(location.search);
const PASS = ['now', 'enable'].filter(k => QS.get(k)).map(k => `${k}=${encodeURIComponent(QS.get(k))}`).join('&');
const apiURL = (p, extra = '') => `/api/capacity/${p}${PASS || extra ? '?' : ''}${[PASS, extra].filter(Boolean).join('&')}`;
const getJSON = (p, extra) => fetch(apiURL(p, extra)).then(r => { if (!r.ok) throw new Error(r.status); return r.json(); });
const postJSON = (p, body) => fetch(apiURL(p), { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body || {}) })
  .then(async r => ({ status: r.status, body: await r.json() }));
const esc = s => String(s ?? '').replace(/[&<>"]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
const href = p => `${p}${PASS ? '?' + PASS : ''}`;
const fmtDate = iso => iso ? new Date(iso).toLocaleDateString('en-GB', { day: 'numeric', month: 'short', year: 'numeric' }) : 'Beyond 13 months';
const fmtTime = iso => new Date(iso).toLocaleString('en-GB', { day: 'numeric', month: 'short', hour: '2-digit', minute: '2-digit', timeZoneName: 'short' });
const n0 = v => Math.round(v).toLocaleString('en-US');
const usd = v => '$' + Math.round(v).toLocaleString('en-US');
const UNIT = { compute: 'threads', memory: 'GB DRAM', storage: 'TB' };
const RES = { compute: 'Compute', memory: 'Memory', storage: 'Storage' };
const KIND = { project: 'Project', migration: 'Migration', dr: 'Disaster recovery', growth: 'Growth of new VMs' };
const QUAD = { red: 'Decide now', green: 'Good', waste: 'Waste' };
const chip = (cls, text) => `<span class="chip ${cls}">${esc(text)}</span>`;
const quadChip = g => g.in_plan ? (g.round_on_time ? chip('in_plan', 'In the plan') : chip('late', 'Too late'))
  : g.quadrant === 'green' && g.peak_warning ? chip('amber', 'Peak warning') : chip(g.quadrant, QUAD[g.quadrant]);
const page = document.body.dataset.page;
const main = document.getElementById('main');
const block = (title, q, body) => `<section class="block"><h2>${esc(title)}</h2><p class="q">${esc(q)}</p>${body}</section>`;

function nav() {
  const cur = { index: '/capacity', clusters: '/capacity/clusters', group: '/capacity/clusters', demand: '/capacity/demand', 'what-if': '/capacity/what-if', plan: '/capacity/plan', waste: '/capacity/waste' }[page];
  const link = (h, t) => `<a href="${href(h)}"${cur === h ? ' aria-current="page"' : ''}>${t}</a>`;
  document.getElementById('nav').innerHTML = `<header class="top"><span class="name">Capacity</span><nav aria-label="Capacity">${link('/capacity', 'This week')}${link('/capacity/clusters', 'Cluster groups')}${link('/capacity/demand', 'Demand')}${link('/capacity/what-if', 'What-if')}${link('/capacity/plan', 'Purchase plan')}${link('/capacity/waste', 'Waste')}</nav><span class="time" id="time"></span></header>`;
}
const stamp = iso => { document.getElementById('time').textContent = `Data as of ${fmtTime(iso)}`; };
const decideBy = g => g.decision_days != null && g.decision_days < 0 ? `overdue since ${fmtDate(g.decision_date)}` : `by ${fmtDate(g.decision_date)}`;
const groupLink = id => `<a class="link" href="${href('/capacity/group/' + id)}">${esc(id)}</a>`;

// ---------------------------------------------------------------- /capacity: this week
async function week() {
  const d = await getJSON('week'); stamp(d.now);
  const moved = d.moved.length ? d.moved.map(m => `<div class="item" data-moved="${m.group}"><strong>${groupLink(m.group)}</strong>: decision ${m.days_earlier > 0 ? `${m.days_earlier} days earlier` : `${-m.days_earlier} days later`}, now ${fmtDate(m.decision_date)}${m.causes.length ? `, because of ${m.causes.map(c => `<strong>${esc(c.id)}</strong> (${esc(KIND[c.kind] || c.kind)}${c.source ? ', ' + esc(c.source) : ''}; owner ${esc(c.owner)})`).join(', ')}` : ', because the trend changed'}.</div>`).join('')
    : '<p class="muted">No change since last week.</p>';
  const entered = d.entered_window.length ? d.entered_window.map(g => `<div class="item">${groupLink(g)} entered its decision window.</div>`).join('') : '<p class="muted">No group entered its decision window.</p>';
  const peaks = d.peak_warnings.length ? d.peak_warnings.map(g => `<div class="item" data-peak="${g.id}"><strong>${groupLink(g.id)}</strong>: the close week around ${fmtDate(g.peak_warning.date)} crosses usable ${RES[g.peak_warning.resource].toLowerCase()}; the trend does not. Borrow hosts, burst, or hold other work for that week. No purchase.</div>`).join('') : '<p class="muted">No peak warning.</p>';
  const waste = d.waste.length ? d.waste.map(g => `<div class="item">${chip('waste', 'Waste')} ${groupLink(g.id)}: ${g.remaining_percent}% of ${RES[g.tightest].toLowerCase()} remaining, run-out ${fmtDate(g.run_out_date)}.</div>`).join('') : '<p class="muted">No waste.</p>';
  main.innerHTML = `<h1>This week</h1><p class="lead">Capacity moves slowly, so the change is the news.</p>
    <div class="kpis"><div class="kpi"><div class="n">${fmtDate(d.next_round_closes)}</div><div class="l">Next procurement round closes</div></div>
    <div class="kpi"><div class="n">${d.groups_in_round.length}</div><div class="l">Groups in the round: ${d.groups_in_round.map(esc).join(', ') || 'none'}</div></div>
    <div class="kpi"><div class="n">${d.moved.length}</div><div class="l">Decision dates that moved 7 days or more</div></div>
    <div class="kpi"><div class="n">${d.peak_warnings.length}</div><div class="l">Peak warnings</div></div></div>
    ${block('Decision dates that moved', 'What changed since last week?', moved)}
    ${block('Entered the decision window', 'Which group needs a decision now?', entered)}
    ${block('Peak warnings', 'Which close week crosses usable capacity?', peaks)}
    ${block('Waste', 'Which groups hold more than they need?', waste)}`;
}

// ---------------------------------------------------------------- /capacity/clusters
function scatter(groups, horizon) {
  const W = 1000, H = 360, L = 60, B = 40, T = 16, R = 110;
  const x = d => L + (Math.min(d ?? horizon, horizon) / horizon) * (W - L - R);
  const y = p => T + (1 - Math.max(0, Math.min(100, p)) / 100) * (H - T - B);
  const fill = g => g.quadrant === 'waste' ? 'var(--waste)' : g.quadrant === 'red' || (g.in_plan && !g.round_on_time) ? 'var(--red)' : 'var(--accent)';
  const ticks = [0, 90, 180, 270, 365].map(d => `<line x1="${x(d)}" x2="${x(d)}" y1="${T}" y2="${H - B}" stroke="var(--line)"/><text x="${x(d)}" y="${H - B + 18}" text-anchor="middle" font-size="12" fill="var(--text-muted)">${d} d</text>`).join('');
  const yt = [0, 25, 50, 75, 100].map(p => `<line x1="${L}" x2="${W - R}" y1="${y(p)}" y2="${y(p)}" stroke="var(--line)"/><text x="${L - 8}" y="${y(p) + 4}" text-anchor="end" font-size="12" fill="var(--text-muted)">${p}%</text>`).join('');
  const dots = groups.map(g => `<g data-group="${g.id}" data-quadrant="${g.quadrant}" data-fill="${fill(g)}"><circle cx="${x(g.time_remaining_days)}" cy="${y(g.remaining_percent)}" r="7" fill="${fill(g)}"><title>${g.id}: ${g.remaining_percent}% remaining, ${g.time_remaining_days ?? 'more than 396'} days</title></circle>${(g.time_remaining_days ?? horizon) < horizon || g.quadrant !== 'green' ? `<text x="${x(g.time_remaining_days) + 10}" y="${y(g.remaining_percent) + 4}" font-size="11" fill="var(--text)">${g.id}</text>` : ''}</g>`).join('');
  const beyond = groups.filter(g => (g.time_remaining_days ?? horizon) >= horizon).length;
  return `<svg viewBox="0 0 ${W} ${H}" width="100%" role="img" aria-label="Capacity remaining against time remaining, one dot per cluster group">${ticks}${yt}${dots}
    <text x="${(W + L) / 2}" y="${H - 4}" text-anchor="middle" font-size="12" fill="var(--text-muted)">Time remaining (days, capped at 13 months)</text>
    <text x="${x(horizon) + 10}" y="${H - B + 18}" font-size="12" fill="var(--text-muted)">${beyond} beyond 13 months</text></svg>
    <div class="legend"><span><i style="background:var(--red)"></i>Decide soon, not in the plan</span><span><i style="background:var(--accent)"></i>In the plan, or healthy</span><span><i style="background:var(--waste)"></i>Waste</span></div>`;
}
async function clusters() {
  const d = await getJSON('groups'); stamp(d.now);
  const rows = d.groups.map(g => `<tr data-row="${g.id}"><td>${groupLink(g.id)}</td><td>${RES[g.tightest]}</td><td class="num">${g.remaining_percent}%</td>
    <td>${fmtDate(g.run_out_date)}</td><td>${g.decision_days != null && g.decision_days < 0 ? 'Overdue since ' + fmtDate(g.decision_date) : fmtDate(g.decision_date)}</td><td>${quadChip(g)}</td>
    <td>${g.closed_for_new_vms.length ? `<span class="full">Closed for new VMs</span>: ${g.closed_for_new_vms.map(c => `${esc(c.cluster)} (since ${fmtDate(c.since)})`).join(', ')}` : ''}</td></tr>`).join('');
  main.innerHTML = `<h1>Cluster groups</h1><p class="lead">One dot per cluster group, read from its tightest resource. Never a location total.</p>
    ${block('Remaining capacity against time remaining', 'Which cluster groups need a decision, and by when?', scatter(d.groups, d.horizon_days))}
    <section class="block"><table><thead><tr><th>Group</th><th>Tightest</th><th class="num">Remaining</th><th>Run-out</th><th>Decision by</th><th>Status</th><th>At the latest check</th></tr></thead><tbody>${rows}</tbody></table></section>`;
}

// ---------------------------------------------------------------- /capacity/group/{id}
function fitLast(points, n) {
  const p = points.slice(-n).map((v, i) => [i * 7 - (n - 1) * 7, v]);
  const mx = p.reduce((a, q) => a + q[0], 0) / p.length, my = p.reduce((a, q) => a + q[1], 0) / p.length;
  const sxx = p.reduce((a, q) => a + (q[0] - mx) ** 2, 0) || 1;
  const b = p.reduce((a, q) => a + (q[0] - mx) * (q[1] - my), 0) / sxx;
  return [my - b * mx, b];
}
function chart(r, nowIso) {
  const W = 420, H = 200, L = 52, B = 26, T = 10, R = 10;
  const t0 = Date.parse(r.weekly[0].t), now = Date.parse(nowIso), t1 = Date.parse(r.forecast[r.forecast.length - 1].t);
  const max = Math.max(r.usable * 1.15, ...r.forecast.map(p => p.v), ...r.weekly.map(p => p.v));
  const x = t => L + (t - t0) / (t1 - t0) * (W - L - R), y = v => T + (1 - v / max) * (H - T - B);
  const path = pts => pts.map((p, i) => `${i ? 'L' : 'M'}${x(Date.parse(p.t)).toFixed(1)},${y(p.v).toFixed(1)}`).join(' ');
  const [a, b] = fitLast(r.weekly.map(p => p.v), 14);
  const t90 = `M${x(now)},${y(a)} L${x(t1)},${y(Math.min(max, a + b * (t1 - now) / 86400000))}`;
  return `<svg viewBox="0 0 ${W} ${H}" width="100%" role="img" aria-label="Weekly peaks, forecast and usable capacity">
    <line x1="${L}" x2="${W - R}" y1="${y(r.usable)}" y2="${y(r.usable)}" stroke="var(--red)" stroke-width="2"/>
    <text x="${L + 4}" y="${y(r.usable) - 4}" font-size="11" fill="var(--red)">Usable ${n0(r.usable)}</text>
    <line x1="${x(now)}" x2="${x(now)}" y1="${T}" y2="${H - B}" stroke="var(--line)" stroke-width="2"/>
    <text x="${x(now) + 4}" y="${H - B + 16}" font-size="11" fill="var(--text-muted)">Now</text>
    <text x="${L - 6}" y="${y(0)}" text-anchor="end" font-size="11" fill="var(--text-muted)">0</text>
    <text x="${L - 6}" y="${y(max) + 10}" text-anchor="end" font-size="11" fill="var(--text-muted)">${n0(max)}</text>
    <path d="${path(r.weekly)}" fill="none" stroke="var(--text)" stroke-width="2"/>
    <path d="${path(r.forecast)}" fill="none" stroke="var(--accent-ink)" stroke-width="2" stroke-dasharray="5 4"/>
    <path d="${t90}" fill="none" stroke="var(--amber)" stroke-width="2" stroke-dasharray="2 3"/></svg>
    <div class="legend"><span><i style="background:var(--text)"></i>Weekly peaks</span><span><i style="background:var(--accent-ink)"></i>13-month forecast</span><span><i style="background:var(--amber)"></i>90-day trend</span><span><i style="background:var(--red)"></i>Usable</span></div>`;
}
async function group() {
  const id = decodeURIComponent(location.pathname.split('/').pop());
  let d;
  try { d = await getJSON('groups/' + encodeURIComponent(id)); } catch (e) { main.innerHTML = '<h1>No such group</h1>'; return; }
  stamp(d.now);
  const nowIso = d.now;
  const wf = Object.entries(d.resources).map(([k, r]) => `<div><h3>${RES[k]} (${UNIT[k]})</h3><div class="wf">
    <div><span>Total</span><span>${n0(r.waterfall.total)}</span></div><div><span>Minus HA</span><span>${n0(r.waterfall.ha)}</span></div>
    <div><span>Minus maintenance</span><span>${n0(r.waterfall.maintenance)}</span></div><div><span>Minus buffer</span><span>${n0(r.waterfall.buffer)}</span></div>
    <div class="eq"><span>Usable</span><span>${n0(r.usable)}</span></div></div></div>`).join('');
  const fc = Object.entries(d.resources).map(([k, r]) => `<div data-res="${k}"><h3>${RES[k]}</h3>${chart(r, nowIso)}
    <div class="wf"><div><span>Remaining</span><span>${r.remaining_percent}%</span></div><div><span>Run-out</span><span>${fmtDate(r.run_out_date)}</span></div>
    <div><span>Decision by</span><span>${fmtDate(r.decision_date)}</span></div><div><span>90-day trend says</span><span data-run90>${r.run_out_90d_date ? fmtDate(r.run_out_90d_date) : 'No run-out in 13 months'}</span></div></div>
    ${r.peak_cross_date ? `<div class="warn" data-peak-warning>Peak warning: the close week around ${fmtDate(r.peak_cross_date)} crosses usable; the trend does not. Borrow hosts, burst, or hold other work. No purchase.</div>` : ''}</div>`).join('');
  const reg = d.register.length ? `<table><thead><tr><th>Entry</th><th>Kind</th><th>Source</th><th>Date</th><th class="num">Threads</th><th class="num">GB</th><th class="num">TB</th><th>Owner</th></tr></thead><tbody>${d.register.map(r => `<tr><td>${esc(r.id)}</td><td>${esc(KIND[r.kind] || r.kind)}</td><td>${esc(r.source)}</td><td>${fmtDate(r.date)}</td><td class="num">${n0(r.compute_threads || 0)}</td><td class="num">${n0(r.memory_gb || 0)}</td><td class="num">${n0(r.storage_tb || 0)}</td><td>${esc(r.owner)}</td></tr>`).join('')}</tbody></table>`
    : '<p class="muted">No register entry for this group.</p>';
  main.innerHTML = `<h1>${esc(d.id)} ${quadChip(d)}</h1><p class="lead">${esc(d.location_name)}, ${d.hosts} hosts in ${d.clusters} clusters. Tightest: ${RES[d.tightest].toLowerCase()}. Decision ${decideBy(d)} (${d.lead_time_days} days lead time).
    ${d.closed_for_new_vms.length ? `<br><span class="full">Closed for new VMs</span> at the latest check: ${d.closed_for_new_vms.map(c => `${esc(c.cluster)} (since ${fmtDate(c.since)})`).join(', ')}, whatever the forecast says.` : ''}</p>
    ${block('Usable capacity', 'How does total capacity become usable capacity?', `<div class="res3">${wf}</div>`)}
    ${block('Forecast', 'When does it run out, and what does a 90-day view miss?', `<div class="res3">${fc}</div>`)}
    ${block('Demand register', 'What demand is coming that the data cannot show?', reg)}`;
}

// ---------------------------------------------------------------- /capacity/demand
async function demand(msg = '') {
  const d = await getJSON('demand'); stamp(d.now);
  const rows = d.entries.length ? `<table><thead><tr><th>Entry</th><th>Kind</th><th>Source</th><th>Group</th><th>Date</th><th class="num">Threads</th><th class="num">GB</th><th class="num">TB</th><th>Owner</th><th>Added</th></tr></thead><tbody>${d.entries.map(r => `<tr data-entry="${esc(r.id)}"><td>${esc(r.id)}</td><td>${esc(KIND[r.kind] || r.kind)}</td><td>${esc(r.source)}</td><td>${groupLink(r.group)}</td><td>${fmtDate(r.date)}</td><td class="num">${n0(r.compute_threads || 0)}</td><td class="num">${n0(r.memory_gb || 0)}</td><td class="num">${n0(r.storage_tb || 0)}</td><td>${esc(r.owner)}</td><td>${fmtDate(r.added)}</td></tr>`).join('')}</tbody></table>`
    : '<p class="muted">Nothing registered. The forecast sees only the past.</p>';
  const form = `<form class="inline" id="add"><label>Kind<select name="kind">${Object.entries(KIND).map(([k, v]) => `<option value="${k}">${v}</option>`).join('')}</select></label>
    <label>Source<input type="text" name="source" placeholder="e.g. Hyper-V"></label>
    <label>Group<select name="group">${d.groups.map(g => `<option>${esc(g)}</option>`).join('')}</select></label>
    <label>Date<input type="text" name="date" placeholder="YYYY-MM-DD" required></label>
    <label>Threads<input type="number" name="compute_threads" value="0" min="0"></label>
    <label>GB DRAM<input type="number" name="memory_gb" value="0" min="0"></label>
    <label>TB<input type="number" name="storage_tb" value="0" min="0"></label>
    <label>Owner<input type="text" name="owner" required></label>
    <button type="submit" class="act">Add</button></form><div class="msg" id="msg">${msg}</div>`;
  main.innerHTML = `<h1>Demand register</h1><p class="lead">Demand the data cannot show yet. The forecast reads each entry at once.</p>
    ${block('Register', 'What demand is coming that the data cannot show?', rows)}${block('Add an entry', 'What is coming, for which group, and when?', form)}`;
  document.getElementById('add').addEventListener('submit', async e => {
    e.preventDefault();
    const r = await postJSON('demand', Object.fromEntries(new FormData(e.target)));
    if (r.status !== 200) { document.getElementById('msg').textContent = r.body.error; return; }
    const g = r.body.group;
    await demand(`Added ${esc(r.body.entry.id)}. ${esc(g.id)}: decision ${decideBy(g)}.`);
    document.body.dataset.added = r.body.entry.id;
  });
}

// ---------------------------------------------------------------- /capacity/what-if
async function whatIf() {
  main.innerHTML = `<h1>What-if</h1><p class="lead">Change one thing and see what it does before anyone buys.</p>
    ${block('Hardware refresh', "Does replacing old hosts cover next year's growth?", `<form class="inline" id="rf"><label>Location<select name="location"><option value="ld">London</option><option value="sg">Singapore</option><option value="va">Virginia</option><option value="fr">Frankfurt</option><option value="tk">Tokyo</option></select></label>
      <label>Previous-generation hosts to replace<input type="number" name="replace" value="90" min="0"></label><label>Current-standard hosts to buy<input type="number" name="new" value="75" min="0"></label>
      <button class="act" type="submit">Show</button></form><div id="rf-out"></div>`)}
    ${block('Host specification', 'How many VMs of a class fit on a host, and how much DRAM should it have?', `<form class="inline" id="hs"><label>Class<select name="class"><option value="silver">Silver</option><option value="gold">Gold</option><option value="bronze">Bronze</option></select></label>
      <label>Cores per host<input type="number" name="cores" value="64" min="8"></label><label>Base GHz<input type="number" name="base_ghz" value="2.5" step="0.1" min="1"></label><label>DRAM per host (GB)<input type="number" name="memory_gb" value="768" min="128"></label>
      <button class="act" type="submit">Show</button></form><div id="hs-out"></div>`)}`;
  const rf = async () => {
    const q = new URLSearchParams(new FormData(document.getElementById('rf'))).toString();
    const d = await getJSON('what-if/refresh', q);
    document.getElementById('rf-out').innerHTML = `<table><thead><tr><th></th><th class="num">Before</th><th class="num">After</th></tr></thead><tbody>
      <tr><td>Threads</td><td class="num">${n0(d.before.threads)}</td><td class="num">${n0(d.after.threads)}</td></tr>
      <tr><td>DRAM (GB)</td><td class="num">${n0(d.before.memory_gb)}</td><td class="num">${n0(d.after.memory_gb)}</td></tr>
      <tr><td>Licensed cores</td><td class="num" data-cores-before>${n0(d.before.cores_licensed)}</td><td class="num" data-cores-after>${n0(d.after.cores_licensed)}</td></tr></tbody></table>
      <p>Next year's growth: ${n0(d.next_year_growth.threads)} threads and ${n0(d.next_year_growth.memory_gb)} GB. The refresh adds ${n0(d.threads_gain)} threads and ${n0(d.memory_gain_gb)} GB, with ${d.racks_saved_hosts} fewer hosts.</p>
      <div class="covers ${d.covers_next_year_growth ? 'yes' : 'no'}" data-covers="${d.covers_next_year_growth}">${d.covers_next_year_growth ? "Covers next year's growth" : "Does not cover next year's growth"}</div>
      <p class="muted">Licensed cores are always shown: VCF is licensed per core.</p>`;
  };
  const NUM = { cpu_allocation: 'CPU allocation', cpu_reservation: 'CPU reservation', cpu_utilization: 'CPU utilization', mem_allocation: 'Memory allocation', mem_reservation: 'Memory reservation', mem_utilization: 'Memory utilization' };
  const hs = async () => {
    const q = new URLSearchParams(new FormData(document.getElementById('hs'))).toString();
    const d = await getJSON('what-if/host', q);
    document.getElementById('hs-out').innerHTML = `<table><thead><tr><th>VMs per host by</th><th class="num">VMs</th></tr></thead><tbody>${Object.entries(d.numbers).map(([k, v]) => `<tr${k === d.binds ? ' class="binds"' : ''} data-n="${k}"><td>${NUM[k]}${k === d.binds ? ' (binds)' : ''}</td><td class="num">${v.toFixed(1)}</td></tr>`).join('')}</tbody></table>
      <p>A typical ${esc(d.class)} VM: ${d.planning.vcpu} vCPU, ${d.planning.gb} GB. The hypervisor keeps ${d.inputs.threads} threads and ${d.inputs.memory_gb} GB.</p>
      <div class="covers yes" data-dram="${d.matching_dram_gb}">The CPU holds ${d.cpu_vms} VMs; memory matches it at ${n0(d.matching_dram_gb)} GB DRAM per host.</div>`;
  };
  document.getElementById('rf').addEventListener('submit', async e => { e.preventDefault(); await rf(); });
  document.getElementById('hs').addEventListener('submit', async e => { e.preventDefault(); await hs(); });
  await rf(); await hs();
}

// ---------------------------------------------------------------- /capacity/plan
async function plan() {
  const d = await getJSON('plan'); stamp(d.now);
  const rows = d.rows.length ? `<table><thead><tr><th>Group</th><th>Resource</th><th class="num">Hosts</th><th>Delivery</th><th>Covered until</th><th class="num">Server</th><th class="num">VCF licence</th><th class="num">Support</th><th class="num">Total cost</th><th></th></tr></thead><tbody>
    ${d.rows.map(r => `<tr data-plan="${r.group}"><td>${groupLink(r.group)}</td><td>${RES[r.resource]}</td><td class="num">${r.hosts}</td><td>${fmtDate(r.delivery_date)}</td><td>${fmtDate(r.cover_until_date)}</td>
      <td class="num">${usd(r.lines.server)}</td><td class="num">${usd(r.lines.vcf_licence)}</td><td class="num">${usd(r.lines.support)}</td><td class="num">${usd(r.total)}</td>
      <td>${r.on_time ? chip('in_plan', 'On time') : chip('late', 'Too late: the order arrives after the group runs out')}</td></tr>`).join('')}
    <tr class="total"><td colspan="8">Round total</td><td class="num" data-total="${d.total}">${usd(d.total)}</td><td></td></tr></tbody></table>
    <p class="muted">Cost per host: server, VCF licence for ${d.host_standard.cores} cores over ${d.depreciation_years} years, and support. Host standard: ${d.host_standard.cores} cores, ${d.host_standard.threads} threads, ${d.host_standard.memory_gb} GB DRAM.</p>`
    : '<p class="muted">No group needs this round.</p>';
  main.innerHTML = `<h1>Purchase plan</h1><p class="lead">The next round closes ${fmtDate(d.next_round_closes)}. For IT Finance.</p>
    ${block('Next round', 'What do we buy in the next round, and what does it cost?', rows)}`;
}

// ---------------------------------------------------------------- /capacity/waste
async function waste() {
  const d = await getJSON('waste'); stamp(d.now);
  const rec = d.reclamation.length ? d.reclamation.map(r => `<div data-reclaim="${r.group}"><h3>${groupLink(r.group)}</h3>
    <table><thead><tr><th>Area, easiest first</th><th class="num">Count</th><th>What it frees</th><th class="num">GB DRAM</th><th class="num">TB</th></tr></thead><tbody>
    ${r.areas.map(a => `<tr><td>${esc(a.area)}</td><td class="num">${a.count ?? ''}</td><td>${esc(a.frees)}</td><td class="num">${n0(a.memory_gb)}</td><td class="num">${a.storage_tb}</td></tr>`).join('')}</tbody></table>
    <p>Reclaiming frees ${n0(r.memory_freed_gb)} GB DRAM. Memory run-out moves from ${fmtDate(r.run_out_date_before)} to ${fmtDate(r.run_out_date_after)}.</p>
    ${r.defers_next_round ? `<div class="covers yes">Moves ${esc(r.group)} out of the next round. Cost avoidance: <span data-avoid="${r.cost_avoidable}">${usd(r.cost_avoidable)}</span>.</div>` : '<p class="muted">Not enough to move the group out of the round; no cost avoidance.</p>'}</div>`).join('')
    : '<p class="muted">Nothing planted to reclaim.</p>';
  const wg = d.waste_groups.length ? d.waste_groups.map(g => `<div class="item">${chip('waste', 'Waste')} ${groupLink(g.id)}: ${g.remaining_percent}% of ${RES[g.tightest].toLowerCase()} remaining, run-out ${fmtDate(g.run_out_date)}. Move work in, or stop buying for it.</div>`).join('') : '<p class="muted">No waste.</p>';
  main.innerHTML = `<h1>Waste and reclamation</h1><p class="lead">What each area frees, said honestly.</p>
    ${block('Reclamation', 'What can we reclaim, starting where?', rec)}${block('Groups that hold too much', 'Which groups have far more than they need?', wg)}`;
}

nav();
const PAGES = { index: week, clusters, group, demand, 'what-if': whatIf, plan, waste };
PAGES[page]().then(() => { document.body.dataset.ready = '1'; })
  .catch(e => { main.innerHTML = `<p class="muted">Could not load: ${esc(e.message)}</p>`; document.body.dataset.ready = '1'; });
