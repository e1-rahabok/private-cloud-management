// GENERATED from spec/workspaces/l2/ (frame, monitor, troubleshoot, case, improve, rules, calendar). Do not edit by hand (D-070).
'use strict';
const QS = new URLSearchParams(location.search);
const PASS = ['now', 'enable'].filter(k => QS.get(k)).map(k => `${k}=${encodeURIComponent(QS.get(k))}`).join('&');
const qjoin = (...xs) => xs.filter(Boolean).join('&');
const apiURL = (p, extra = '') => { const q = qjoin(PASS, extra); return `/api/l2/${p}${q ? '?' + q : ''}`; };
const getJSON = (p, extra) => fetch(apiURL(p, extra)).then(r => { if (!r.ok) throw new Error(r.status); return r.json(); });
const postJSON = (p, body) => fetch(apiURL(p), { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body || {}) })
  .then(async r => ({ status: r.status, body: await r.json() }));
const esc = s => String(s ?? '').replace(/[&<>"]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
const enc = encodeURIComponent;
const fmtTime = iso => new Date(iso).toLocaleString('en-GB', { day: 'numeric', month: 'short', hour: '2-digit', minute: '2-digit', timeZoneName: 'short' });
const fmtDay = iso => new Date(iso).toLocaleDateString('en-GB', { day: 'numeric', month: 'short', year: 'numeric' });
const n0 = v => Number(v).toLocaleString('en-US');
const STATUS = { green: 'Good', amber: 'Watch', red: 'Act now', no_data: 'No data' };
const chip = s => `<span class="chip ${s}">${STATUS[s] || esc(s)}</span>`;
const PILLARS = ['availability', 'performance', 'capacity', 'security', 'configuration', 'inventory'];
const PNAME = { summary: 'Summary', availability: 'Availability', performance: 'Performance', capacity: 'Capacity', security: 'Security', configuration: 'Configuration', inventory: 'Inventory' };
const WINDOWS = [['1h', '1 hour'], ['24h', '24 hours'], ['7d', '7 days'], ['30d', '30 days'], ['1y', '1 year']];
const KIND = { estate: 'Estate', region: 'Region', location: 'Location', vcf_instance: 'VCF instance', workload_domain: 'Workload domain', cluster: 'Cluster', host: 'ESXi host', vm: 'VM', guest_os: 'Guest OS', datastore: 'Datastore', virtual_disk: 'Virtual disk', distributed_switch: 'Distributed switch', port_group: 'Port group', vnic: 'vNIC', class_of_service: 'Class of service', resource_pool: 'Resource pool' };
const TRIGGER = { complaint: 'Complaint', escalation: 'Escalation from L1', finding: 'Monitoring finding' };
const GROUP = { correct_it: 'Correct it', update_it: 'Update it', simplify_it: 'Simplify it', optimize_it: 'Optimize it' };
const DETECTION = { new_check_rule: 'New check rule', new_alert: 'New alert', new_sop: 'New SOP for L1', sop_updated: 'SOP updated', none_with_reason: 'None, with a reason' };
const LAYER = { guest_os: 'Guest OS', vm: 'VM', host: 'Host', cluster: 'Cluster', storage: 'Storage', network: 'Network', change: 'Change', event: 'Event' };
const STEP = { contention: 'Contention', consumption: 'Consumption', configuration: 'Configuration', known_bug: 'Known bug', log: 'Log', saturation: 'Saturation' };
const VERDICT = { clear: ['green', 'Clear'], waiting: ['red', 'Waiting'], not_read: ['no_data', 'Not read'] };
const GROUP_BY = [['', 'No grouping'], ['host_model', 'Host model'], ['esxi_build', 'ESXi build'], ['firmware', 'Firmware'], ['class_of_service', 'Class of service'], ['environment', 'Environment'], ['guest_os', 'Guest OS'], ['tools_version', 'VMware Tools version'], ['vcpu_band', 'vCPUs']];
const main = document.getElementById('main');

// ---------------------------------------------------------------- the address (frame.md, Addresses)
function parseRoute() {
  const seg = location.pathname.replace(/\/+$/, '').split('/').slice(2).map(decodeURIComponent);
  const win = QS.get('window');
  const r = { activity: seg[0] || 'monitor', view: 'compute', object: 'estate', pillar: 'summary', window: win, group: QS.get('group') || '', cls: QS.get('class') || '', at: QS.get('at') || '' };
  if (r.activity === 'monitor' || r.activity === 'improve') {
    r.view = seg[1] || 'compute'; r.object = seg[2] || 'estate'; r.pillar = seg[3] || 'summary';
    r.window = win || (r.activity === 'improve' ? '30d' : '24h');
  } else if (r.activity === 'troubleshoot') {
    if (seg[1] === 'case') r.caseId = seg[2];
    else if (seg[1] === 'new') r.newComplaint = true;
    else { r.view = seg[1] || 'compute'; r.object = seg[2] || 'estate'; }
  }
  return r;
}
let R = parseRoute();
if (location.pathname.replace(/\/+$/, '') === '/l2') {
  history.replaceState(null, '', `/l2/monitor/compute/estate/summary${PASS ? '?' + PASS : ''}`);
  R = parseRoute();
}
const remember = () => { try { sessionStorage.setItem('l2.last', JSON.stringify({ view: R.view, object: R.object, window: R.window })); } catch (e) { /* per-viewer convenience only */ } };
const recall = () => { try { return JSON.parse(sessionStorage.getItem('l2.last') || 'null'); } catch (e) { return null; } };
function url(o = {}) {
  const x = { ...R, ...o };
  const keepWin = x.window && x.activity !== 'troubleshoot' ? `window=${x.window}` : '';
  const perfTab = x.activity === 'monitor' && x.pillar === 'performance';
  const grp = x.group && perfTab ? `group=${enc(x.group)}` : '';
  const cls = x.cls && perfTab ? `class=${enc(x.cls)}` : '';
  // A selected time belongs to one object, window and class: changing any of them goes back to the worst time.
  const moved = ['activity', 'view', 'object', 'pillar', 'window', 'cls'].some(k => k in o && o[k] !== R[k]);
  const at = perfTab && ('at' in o ? o.at : moved ? '' : x.at);
  const q = qjoin(PASS, keepWin, grp, cls, at ? `at=${enc(at)}` : '');
  let p;
  if (x.activity === 'monitor' || x.activity === 'improve') p = `/l2/${x.activity}/${x.view}/${enc(x.object)}/${x.pillar}`;
  else if (x.activity === 'troubleshoot') p = x.caseId ? `/l2/troubleshoot/case/${enc(x.caseId)}` : x.newComplaint ? `/l2/troubleshoot/new` : `/l2/troubleshoot/${x.view}/${enc(x.object)}`;
  else p = `/l2/${x.activity}`;
  return p + (q ? '?' + q : '');
}
const objURL = (id, view) => url({ object: id, view: view || R.view, caseId: undefined, newComplaint: undefined, activity: ['monitor', 'improve', 'troubleshoot'].includes(R.activity) ? R.activity : 'monitor', pillar: R.pillar || 'summary', window: R.window || '24h' });
const complaintURL = vm => { const u = url({ activity: 'troubleshoot', newComplaint: true, caseId: undefined }); return vm ? `${u}${u.includes('?') ? '&' : '?'}vm=${enc(vm)}` : u; };
const objLink = (id, name, view) => `<a class="link" href="${objURL(id, view)}">${esc(name || id)}</a>`;

// ---------------------------------------------------------------- top bar (frame.md, Top bar)
async function topBar(openCases) {
  const last = recall() || { view: 'compute', object: 'estate', window: '24h' };
  const base = ['monitor', 'improve', 'troubleshoot'].includes(R.activity) && !R.caseId && !R.newComplaint ? { view: R.view, object: R.object } : { view: last.view, object: last.object };
  const a = (act, label, extra = '') => {
    const href = url({ activity: act, ...base, caseId: undefined, newComplaint: undefined, pillar: R.pillar && R.pillar !== 'summary' && act !== 'troubleshoot' ? R.pillar : 'summary',
      window: act === 'troubleshoot' ? undefined : (R.activity === act ? R.window : (act === 'improve' ? '30d' : (R.activity === 'monitor' ? R.window : last.window || '24h'))) });
    return `<a href="${href}"${R.activity === act ? ' aria-current="page"' : ''}>${label}${extra}</a>`;
  };
  const u = (act, label) => `<a href="${url({ activity: act })}"${R.activity === act ? ' aria-current="page"' : ''}>${label}</a>`;
  document.getElementById('top').innerHTML = `<span class="name">L2 Platform</span>
    <nav class="acts" aria-label="Activities">${a('monitor', 'Monitor')}${a('troubleshoot', 'Troubleshoot', openCases ? `<span class="count" aria-label="${openCases} open cases">${openCases}</span>` : '')}${a('improve', 'Improve')}</nav>
    <nav class="utils" aria-label="Utilities">${u('rules', 'Rules')}${u('calendar', 'Calendar')}</nav>`;
}

// ---------------------------------------------------------------- inventory tree (frame.md, Inventory tree)
const TREE_HIDDEN = new Set(['host', 'resource_pool', 'vm', 'guest_os', 'virtual_disk', 'vnic']);
const treeQ = node => `view=${R.view}&node=${enc(node)}&activity=${['improve', 'troubleshoot'].includes(R.activity) ? R.activity : 'monitor'}&pillar=${R.pillar || 'summary'}&window=${R.window || '24h'}`;
function treeItems(rows, openPath, levels, selected) {
  return rows.map(r => {
    const open = openPath.includes(r.id) && levels[r.id];
    return `<li data-node="${esc(r.id)}"><div class="item"><button type="button" class="caret" aria-label="Expand ${esc(r.name)}" aria-expanded="${open ? 'true' : 'false'}"${r.expandable ? '' : ' hidden'}>${open ? '▾' : '▸'}</button>
      <a class="node" href="${objURL(r.id)}"${r.id === selected ? ' aria-current="true"' : ''} title="${esc(r.name)}"><span class="dot ${r.status}" aria-label="${STATUS[r.status] || r.status}"></span><span class="nm">${esc(r.name)}</span>${r.open_cases ? `<span class="badge" title="Open cases">${r.open_cases}</span>` : ''}</a></div>
      ${open ? `<ul>${treeItems(levels[r.id], openPath, levels, selected)}</ul>` : ''}</li>`;
  }).join('');
}
async function tree() {
  const box = document.getElementById('tree');
  const first = await getJSON('tree', treeQ(R.object));
  if (first.node.view !== R.view) R.view = first.node.view;
  const path = first.node.path.map(p => p.id);
  const visible = path.filter((id, i) => i === 0 || !TREE_HIDDEN.has(first.node.path[i].kind) || (R.view === 'management' && first.node.path[i].kind === 'vm'));
  const selected = visible[visible.length - 1];
  const levels = {};
  const ids = visible.filter(id => id !== R.object);
  const got = await Promise.all(ids.map(id => getJSON('tree', treeQ(id)).catch(() => null)));
  ids.forEach((id, i) => { if (got[i]) levels[id] = got[i].children; });
  if (!TREE_HIDDEN.has(first.node.kind) || R.object === 'estate') levels[R.object] = first.children;
  const root = levels.estate || [];
  box.innerHTML = `<label for="view">View</label><select id="view">${first.views.map(v => `<option value="${v.id}"${v.id === R.view ? ' selected' : ''}>${esc(v.name)}</option>`).join('')}</select>
    <label for="find">Search</label><input id="find" type="text" placeholder="Name of any object" autocomplete="off"><ul class="results" id="results"></ul>
    <ul><li data-node="estate"><div class="item"><span class="caret" hidden></span><a class="node" href="${objURL('estate')}"${selected === 'estate' ? ' aria-current="true"' : ''}><span class="dot ${['red', 'amber', 'no_data'].find(s => root.some(r => r.status === s)) || 'green'}"></span><span class="nm">ACME estate</span>${first.open_cases && R.object === 'estate' ? `<span class="badge">${first.open_cases}</span>` : ''}</a></div>
    <ul>${treeItems(root, visible, levels, selected)}</ul></li></ul>`;
  document.getElementById('view').addEventListener('change', e => { location.href = url({ view: e.target.value, object: 'estate', caseId: undefined, newComplaint: undefined, activity: ['monitor', 'improve', 'troubleshoot'].includes(R.activity) ? R.activity : 'monitor', pillar: R.pillar || 'summary' }); });
  let t;
  document.getElementById('find').addEventListener('input', e => {
    clearTimeout(t);
    t = setTimeout(async () => {
      const res = await getJSON('search', `q=${enc(e.target.value)}`).catch(() => []);
      document.getElementById('results').innerHTML = res.map(x => `<li><a href="${objURL(x.id, x.view)}">${esc(x.name)} <span class="muted">${esc(KIND[x.kind] || x.kind)}${x.path.length ? ' · ' + esc(x.path.slice(-2).join(' › ')) : ''}</span></a></li>`).join('');
    }, 200);
  });
  box.addEventListener('click', async e => {
    const b = e.target.closest('button.caret');
    if (!b) return;
    const li = b.closest('li');
    const sub = li.querySelector(':scope > ul');
    if (sub) { sub.remove(); b.textContent = '▸'; b.setAttribute('aria-expanded', 'false'); return; }
    const d = await getJSON('tree', treeQ(li.dataset.node));
    li.insertAdjacentHTML('beforeend', `<ul>${treeItems(d.children, [], {}, selected)}</ul>`);
    b.textContent = '▾'; b.setAttribute('aria-expanded', 'true');
  });
  return first;
}

// ---------------------------------------------------------------- shared pieces
function objHead(o, windowFixed) {
  const crumbs = o.path.slice(0, -1).map(p => `<a href="${objURL(p.id, o.view)}">${esc(p.name)}</a>`).join(' › ');
  const win = windowFixed ? `<div class="windows fixed">${esc(windowFixed)}</div>`
    : `<nav class="windows" aria-label="Window">${WINDOWS.map(([w, l]) => `<a href="${url({ window: w })}"${w === R.window ? ' aria-current="true"' : ''}>${l}</a>`).join('')}</nav>`;
  return `<div class="objhead"><div><div class="crumbs">${crumbs || '&nbsp;'}</div><div class="kind">${esc(KIND[o.kind] || o.kind)}</div><h1>${esc(o.name)}</h1></div>${win}</div>`;
}
const runLine = r => `<p class="runline">${r.kind === 'baseline' ? esc(r.review) : `${r.kind === 'daily' ? 'Daily' : 'Weekly'} check, ${esc(r.region)}: ran ${fmtTime(r.started_at)} to ${fmtTime(r.finished_at)}. ${esc(r.review)}`}</p>`;
function tabs(statuses) {
  return `<nav class="tabs" aria-label="Pillars">${['summary', ...PILLARS].map(p => `<a href="${url({ pillar: p })}"${p === R.pillar ? ' aria-current="true"' : ''}>${statuses && statuses[p] ? `<span class="dot ${statuses[p]}"></span>` : ''}${PNAME[p]}</a>`).join('')}</nav>`;
}
const spark = (pts, key = 'v') => {
  if (!pts || pts.length < 2) return '';
  const vals = pts.map(p => p[key]); const hi = Math.max(...vals), lo = Math.min(...vals); const r = (hi - lo) || 1;
  const xy = vals.map((v, i) => `${(i / (vals.length - 1) * 100).toFixed(1)},${(44 - (v - lo) / r * 40).toFixed(1)}`).join(' ');
  return `<svg class="spark" viewBox="0 0 100 48" preserveAspectRatio="none" aria-hidden="true"><polyline points="${xy}" vector-effect="non-scaling-stroke"/></svg>`;
};
const bars = (vals, fromMin) => { const hi = Math.max(...vals), lo = fromMin ? Math.min(...vals) - (hi - Math.min(...vals)) * 0.25 : 0; const r = (hi - lo) || 1;
  return `<div class="bars" aria-hidden="true">${vals.map(v => `<span style="height:${Math.max(4, 100 * (v - lo) / r)}%"></span>`).join('')}</div>`; };

function findingRow(f) {
  const p = f.proposal;
  const prop = p ? `<div class="proposal"><strong>Proposed fix:</strong> ${esc(p.reason)} ${p.state === 'waiting'
    ? `<button type="button" class="act" data-approve="${p.id}">Approve</button> <button type="button" class="act secondary" data-reject="${p.id}">Reject</button>`
    : p.state === 'ran_automatically' ? `<strong>Ran automatically</strong> under ${esc(p.accountable)}. No approval: the policy decided.`
    : `<strong>${esc(p.state)}</strong> by ${esc(p.decided_by)}${p.rejection_reason ? `: ${esc(p.rejection_reason)}` : ''}`}</div>` : '';
  const go = f.outcome === 'problem'
    ? (f.case ? `<a class="link" href="${url({ activity: 'troubleshoot', caseId: f.case })}">Open the case</a>` : `<button type="button" class="act" data-trouble="${f.id}">Troubleshoot this</button>`)
    : `<a class="link" href="${url({ activity: 'improve', object: f.object, view: 'compute', pillar: f.pillar, window: '30d' })}">Improve this</a>`;
  const ev = f.evidence && f.evidence.nightly ? `${bars(f.evidence.nightly, true)}<div class="muted">Last 7 nights, ${esc(f.evidence.unit)}: ${f.evidence.nightly.join(', ')}</div>` : '';
  return `<div class="finding" data-finding="${f.id}">${chip(f.severity)}<div><div class="chain">${PNAME[f.pillar]} · ${f.window === '7d' ? 'weekly check' : 'daily check'}${f.kind ? ' · ' + esc(f.kind.replaceAll('_', ' ')) : ''} · ${f.path.slice(1).map(esc).join(' › ')}</div>
    <strong>${esc(f.object_name)}</strong>: ${esc(f.summary)}${ev}
    ${f.explained_by ? `<div class="explained">Explained by the calendar: ${esc(f.explained_by.note)}</div>` : ''}${prop}
    <div class="acts">${go}<button type="button" class="act secondary" data-explain="${f.id}">Explain this finding</button><span class="muted" data-out="${f.id}"></span></div></div></div>`;
}
function wireFindings(reload) {
  main.querySelectorAll('[data-approve]').forEach(b => b.addEventListener('click', async () => { await postJSON(`proposals/${b.dataset.approve}/approve`); reload('Approved.'); }));
  main.querySelectorAll('[data-reject]').forEach(b => b.addEventListener('click', async () => {
    const reason = prompt('Why reject? The reason tells L2 which rule is wrong.');
    const r = await postJSON(`proposals/${b.dataset.reject}/reject`, { reason }); reload(r.status === 200 ? 'Rejected, with the reason recorded.' : r.body.error);
  }));
  main.querySelectorAll('[data-trouble]').forEach(b => b.addEventListener('click', async () => {
    const r = await postJSON('cases', { trigger: 'finding', finding: b.dataset.trouble });
    if (r.status === 200) location.href = url({ activity: 'troubleshoot', caseId: r.body.id }); else reload(r.body.error);
  }));
  main.querySelectorAll('[data-explain]').forEach(b => b.addEventListener('click', async () => {
    const out = main.querySelector(`[data-out="${b.dataset.explain}"]`); out.textContent = 'Agent E2 is reading…';
    const r = await postJSON(`findings/${b.dataset.explain}/agent`, {});
    out.textContent = r.body.text || r.body.error; document.body.dataset.explained = r.body.source || 'error';
  }));
}

// ---------------------------------------------------------------- Monitor (monitor.md)
async function monitor(msg = '') {
  remember();
  if (R.pillar === 'summary') {
    const d = await getJSON(`monitor/${R.view}/${enc(R.object)}/summary`, `window=${R.window}`);
    const st = Object.fromEntries(d.pillars.map(p => [p.pillar, p.status]));
    const rows = d.pillars.map(p => `<tr data-pillar="${p.pillar}"><td>${chip(p.status)}</td><td><a href="${url({ pillar: p.pillar })}">${PNAME[p.pillar]}</a></td><td>${esc(p.headline)}</td><td class="num">${p.findings}</td></tr>`).join('');
    let year = '';
    if (d.measures) {
      const b = d.measures, BL = { urgent_alerts: 'Urgent alerts', repeated_escalations: 'Repeated problems', found_by_check_percent: 'Found by a check first (%)', diagnose_known_minutes: 'Minutes to diagnose a known problem', slipped_alerts: 'Alerts that slipped through' };
      year = `<h2>Twelve months: the L2 measures</h2><div class="cards">${Object.entries(BL).map(([k, l]) => `<div class="card"><h3>${l}</h3>${bars(b[k])}<div class="muted">${b.months[0]} to ${b.months[11]}: ${b[k][0]} to ${b[k][11]}</div></div>`).join('')}</div>
        <h2>Repeated problems</h2><table class="data"><thead><tr><th>Problem</th><th class="num">Last 12 months</th><th>Loop</th></tr></thead><tbody>${d.repeated_problems.map(r => `<tr data-rep="${r.type}"><td>${esc(r.title)}</td><td class="num">${r.last_12m}</td><td>${r.loop_closed ? `<span class="chip green">Loop closed</span> ${esc(r.closed_by)}` : '<span class="chip amber">Still open</span> No check rule or SOP yet'}</td></tr>`).join('')}</tbody></table>`;
    }
    main.innerHTML = objHead(d.object) + `${runLine(d.run)}` + tabs(st) + `<div class="msg" role="status">${esc(msg)}</div>
      ${d.stale ? '<p class="why">No data from this location\'s VCF Operations. Shown grey, never green.</p>' : ''}
      <table class="data pillars"><thead><tr><th>Status</th><th>Pillar</th><th>Now</th><th class="num">Findings</th></tr></thead><tbody>${rows}</tbody></table>
      <h2>Findings, worst first</h2>${d.findings.length ? d.findings.map(findingRow).join('') : '<p>Nothing needs you under this object.</p>'}
      ${d.slipped_alerts.length ? `<h2>Alerts that slipped through</h2><ul>${d.slipped_alerts.map(s => `<li>${esc(s.object)}: ${esc(s.title)}, ${fmtTime(s.raised)}. No finding predicted it. ${esc(s.would_have_caught_it || '')} <a class="link" href="${url({ activity: 'rules' })}">Change the check rule</a></li>`).join('')}</ul>` : ''}
      ${year}`;
    wireFindings(monitor);
    return;
  }
  const d = await getJSON(`monitor/${R.view}/${enc(R.object)}/${R.pillar}`, qjoin(`window=${R.window}`, R.group ? `group_by=${R.group}` : '',
    R.pillar === 'performance' && R.cls ? `class=${enc(R.cls)}` : '', R.pillar === 'performance' && R.at ? `at=${enc(R.at)}` : ''));
  const head = objHead(d.object) + `${runLine(d.run)}` + tabs({ [R.pillar]: d.status }) + `<div class="msg" role="status">${esc(msg)}</div>`;
  const c = d.content;
  let body = '';
  if (R.pillar === 'performance' && d.perf) {
    body += perfTab(d.perf, d);
  } else if (R.pillar === 'performance') {
    const ice = c.iceberg;
    const unit = d.trend.length && d.trend[0].unit ? d.trend[0].unit : 'score';
    body += `<div class="cards"><div class="card ${d.status}"><h3>This object ${chip(d.status)}</h3><div class="big2">${d.score ?? '–'}</div><div class="muted">Over ${R.window}${d.score_now !== null && R.window !== '1h' ? `; last hour ${d.score_now}` : ''}</div></div>
      <div class="card"><h3>Trend</h3>${spark(d.trend)}<div class="muted">${unit === 'score' ? 'Score over the window' : 'Clusters outside green over the window'}</div></div>
      <div class="card ${d.outside_green ? 'amber' : 'green'}"><h3>Children outside green</h3><div class="big2">${d.outside_green} <span class="muted" style="font-size:16px">of ${d.children_total}</span></div></div>
      ${ice ? `<div class="card" data-iceberg><h3>Just above the line</h3><div class="big2">${n0(ice.near_line)}</div><div class="muted">VMs between ${ice.near_line_from} and ${ice.near_line_to}, ${esc(ice.direction)} over 7 days; ${n0(ice.below_green)} below green, of ${n0(ice.vms)}</div>${bars(ice.trend_7_days)}</div>` : ''}</div>`;
    body += groupBy(d);
    if (d.realms) {
      const realm = (name, r) => `<div class="card ${r.status}"><h3>${name} ${chip(r.status)}</h3>${Object.entries(r).filter(([k]) => k !== 'status').map(([k, v]) => `<div class="row"><span>${esc(k.replaceAll('_', ' '))}</span><span>${v}</span></div>`).join('')}</div>`;
      body += `<h2>VM and Guest OS, side by side</h2><div class="cols2">${realm('VM', d.realms.vm)}${realm('Guest OS', d.realms.guest_os)}</div>
        <p><a class="link" href="${complaintURL(R.object)}">Log a complaint about this VM</a></p>`;
    }
    body += childrenTable(d);
  } else if (R.pillar === 'availability') {
    body += `<p>${esc(c.headline)}</p>${c.events.length ? `<table class="data"><thead><tr><th>When</th><th>Object</th><th>What</th><th>Counted</th></tr></thead><tbody>${c.events.map(e => `<tr><td>${fmtTime(e.at)}</td><td>${objLink(e.object)}</td><td>${esc(e.text)}</td><td>${e.counted ? '<span class="chip amber">Counted</span>' : '<span class="chip green">Not counted</span>'}</td></tr>`).join('')}</tbody></table>` : ''}
      <p class="muted">Hosts not connected: ${c.hosts_not_connected}. HA restarts: ${c.ha_restarts}.</p>` + childrenTable(d);
  } else if (R.pillar === 'capacity') {
    body += `<p>${esc(c.headline)} <span class="muted">Today, not the forecast: the forecast and purchase dates are the Capacity workspace's.</span></p>
      ${c.clusters && c.clusters.length ? `<table class="data"><thead><tr><th>Cluster</th><th>Class</th><th class="num">CPU average</th><th class="num">CPU 95th</th><th class="num">Memory average</th><th class="num">Memory 95th</th><th class="num">Imbalance</th><th></th></tr></thead><tbody>
      ${c.clusters.slice(0, 120).map(r => `<tr data-cluster="${r.cluster}"><td>${objLink(r.cluster)}</td><td>${esc(r.class)}</td><td class="num">${r.cpu_average}%</td><td class="num">${r.cpu_p95}%</td><td class="num">${r.memory_average}%</td><td class="num">${r.memory_p95}%</td><td class="num">${r.imbalance}</td><td>${r.full_now ? '<span class="chip red">Full now: VMs waiting</span>' : r.memory_p95 >= 90 ? '<span class="chip amber">Memory above 90%</span>' : ''}</td></tr>`).join('')}</tbody></table>` : '<p class="muted">No cluster under this object.</p>'}`;
  } else if (R.pillar === 'security') {
    body += `<p>${esc(c.headline)}</p><div class="cols2"><div class="card ${c.ssh_hosts.length ? 'red' : 'green'}"><h3>SSH or ESXi Shell on, outside a window</h3>${c.ssh_hosts.length ? c.ssh_hosts.map(h => `<div class="row"><span>${objLink(h.id)}</span><span>${esc(h.cluster)}</span></div>`).join('') : '<p class="muted">None.</p>'}</div>
      <div class="card ${c.certificates.length ? 'amber' : 'green'}"><h3>Certificates near expiry</h3>${c.certificates.length ? c.certificates.map(x => `<div class="row"><span>${esc(x.summary)}</span></div>`).join('') : '<p class="muted">None.</p>'}</div></div>
      <p class="muted">Lockdown mode off: ${c.lockdown_off}. Root logins: ${c.root_logins}. A suspected breach goes to the security team with its evidence.</p>`;
  } else if (R.pillar === 'configuration') {
    body += `<p>${esc(c.headline)}</p>${c.drift.length ? `<table class="data"><thead><tr><th>Group</th><th>Object</th><th>Setting</th><th>Actual</th><th>Standard</th></tr></thead><tbody>${c.drift.map(i => `<tr><td>${GROUP[i.group]}</td><td>${esc(i.object)}</td><td>${esc(i.setting_label)}</td><td>${esc(i.actual)}</td><td>${esc(i.standard)} <span class="muted">(v${i.standard_version})</span></td></tr>`).join('')}</tbody></table>
      <p><a class="link" href="${url({ activity: 'improve', pillar: 'configuration', window: '30d' })}">Correct, update or simplify in Improve</a></p>` : '<p class="muted">No drift under this object.</p>'}
      <div class="cols2"><div><h2>ESXi builds in use</h2><table class="data"><tbody>${c.esxi_builds.map(([b, n]) => `<tr><td>${esc(b)}</td><td class="num">${n0(n)} hosts</td></tr>`).join('') || '<tr><td class="muted">No host under this object.</td></tr>'}</tbody></table></div>
      <div><h2>VMware Tools versions in use</h2><table class="data"><tbody>${c.tools_versions.map(([b, n]) => `<tr><td>${esc(b)}</td><td class="num">${n0(n)} VMs</td></tr>`).join('')}</tbody></table></div></div>`;
  } else if (R.pillar === 'inventory') {
    const EXPL = { pcm_action: 'PCM action record', change_window: 'Approved change window', request: 'Self-service request', drs: 'DRS', l2_expected: 'Expected, recorded by L2' };
    body += `<div class="cards">${Object.entries(c.counts).map(([k, v]) => `<div class="card"><h3>${esc(k.charAt(0).toUpperCase() + k.slice(1))}</h3><div class="big2">${n0(v)}</div></div>`).join('')}<div class="card"><h3>VMs in ${c.days} days</h3><div class="big2">+${n0(c.change.created)} −${n0(c.change.deleted)}</div></div></div>
      <h2>Unexplained changes</h2>${c.unexplained.length ? c.unexplained.map(x => `<div class="finding" data-change="${x.id}"><span class="chip red">Unexplained</span><div><strong>${esc(x.object)}</strong>: ${esc(x.detail)}<div class="chain">${fmtTime(x.at)} · by ${esc(x.by)} through ${esc(x.via)} · ${esc(x.environment)}${x.class ? ', ' + esc(x.class) : ''}</div>
        <div class="muted">No PCM action, change window, request or DRS explains it.</div><form class="inline expect" data-c="${x.id}"><label>Why was it expected?<input type="text" name="reason" size="40"></label><button class="act secondary" type="submit">This was expected</button></form></div></div>`).join('') : '<p class="muted">Every change in this window is explained.</p>'}
      ${c.expected_by_l2.length ? `<h2>Expected, recorded by L2</h2><ul>${c.expected_by_l2.map(x => `<li data-expected="${x.id}">${esc(x.object)}: ${esc(x.detail)}. ${esc(x.expected.reason)} (${esc(x.expected.by)})</li>`).join('')}</ul>` : ''}
      <h2>Explained changes, counted</h2><table class="data"><tbody>${Object.entries(c.explained_by_type).map(([t, by]) => `<tr><td>${esc(t.replaceAll('_', ' '))}</td><td>${Object.entries(by).map(([e, n]) => `${n0(n)} by ${EXPL[e]}`).join('; ')}</td></tr>`).join('')}</tbody></table>
      <h2>Distribution across children</h2><table class="data"><tbody>${c.distribution.map(x => `<tr><td>${objLink(x.id, x.name)}</td><td>${esc(KIND[x.kind] || x.kind)}</td><td class="num">${n0(x.vms)} VMs</td></tr>`).join('')}</tbody></table>`;
  }
  body += `<h2>Findings: ${PNAME[R.pillar]}</h2>${d.findings.length ? d.findings.map(findingRow).join('') : '<p class="muted">Nothing needs you under this object.</p>'}`;
  main.innerHTML = head + (d.stale ? '<p class="why">No data from this location\'s VCF Operations. Shown grey, never green.</p>' : '') + body;
  const g = document.getElementById('grp');
  if (g) g.addEventListener('change', () => { location.href = url({ group: g.value }); });
  if (d.perf) wireCharts(d.perf);
  main.querySelectorAll('form.expect').forEach(fm => fm.addEventListener('submit', async e => {
    e.preventDefault();
    const r = await postJSON(`inventory/${fm.dataset.c}/expected`, Object.fromEntries(new FormData(fm)));
    await monitor(r.status === 200 ? 'Recorded as expected.' : r.body.error); document.body.dataset.expected = String(r.status);
  }));
  wireFindings(monitor);
}
// ---------------------------------------------------------------- Performance above the cluster: VM, then Cluster (monitor.md)
const CLASS_NAME = { gold: 'Gold', silver: 'Silver', bronze: 'Bronze', all: 'All classes' };
const BAND_NAME = { green: 'Green', yellow: 'Yellow', orange: 'Orange', red: 'Red' };
const perfBand = v => v == null ? 'no_data' : v >= 75 ? 'green' : v >= 50 ? 'yellow' : v >= 25 ? 'orange' : 'red';
const riskBand = v => v == null ? 'no_data' : perfBand(100 - v);
const statusOfBand = b => ({ green: 'green', yellow: 'amber', orange: 'red', red: 'red' }[b] || 'no_data');
const fmtPoint = (iso, minutes) => new Date(iso).toLocaleString('en-GB', minutes >= 1440 ? { day: 'numeric', month: 'short' } : { day: 'numeric', month: 'short', hour: '2-digit', minute: '2-digit' });
const fmtTick = (iso, minutes, span) => new Date(iso).toLocaleString('en-GB', span > 2 * 86400000 ? { day: 'numeric', month: 'short' } : { hour: '2-digit', minute: '2-digit' });
const fmtDur = m => m >= 60 ? `${Math.floor(m / 60)} h${m % 60 ? ` ${m % 60} min` : ''}` : `${m} min`;
const CHARTS = {};

// One chart, one axis. series: [{ key, label, dash, color (fixed) or band (function of value) }].
function lineChart(id, pts, series, o) {
  CHARTS[id] = { pts, series, o };
  const W = 1000, H = 240, L = 48, Rt = 140, T = 12, B = 30, iw = W - L - Rt, ih = H - T - B, n = pts.length;
  const max = o.max ?? Math.max(4, ...pts.flatMap(p => series.map(s => p[s.key] ?? 0))) * 1.1;
  const x = i => L + (n === 1 ? iw / 2 : i / (n - 1) * iw), y = v => T + ih - v / max * ih;
  const ticks = o.max === 100 ? [0, 25, 50, 75, 100] : [0, Math.round(max / 2), Math.round(max)];
  const span = new Date(pts[n - 1].t) - new Date(pts[0].t);
  const xt = [0, 1, 2, 3, 4, 5, 6].map(k => Math.round(k * (n - 1) / 6));
  let svg = `<svg class="lc" viewBox="0 0 ${W} ${H}" role="img" aria-label="${esc(o.label)}" data-chart="${id}">`;
  if (o.bands) svg += o.bands.map(([lo, hi, b]) => `<text x="${W - 8}" y="${y((lo + hi) / 2) + 4}" text-anchor="end" class="bandlbl">${BAND_NAME[b]}</text>`).join('');
  svg += ticks.map(v => `<line class="grid" x1="${L}" x2="${W - Rt}" y1="${y(v)}" y2="${y(v)}"/><text class="axis" x="${L - 8}" y="${y(v) + 4}" text-anchor="end">${o.max === 100 ? v + '%' : n0(v)}</text>`).join('');
  svg += xt.map(i => `<text class="axis" x="${x(i)}" y="${H - 8}" text-anchor="middle">${esc(fmtTick(pts[i].t, o.minutes, span))}</text>`).join('');
  for (const s of series) {
    let segs = '';
    for (let i = 1; i < n; i++) {
      const a = pts[i - 1][s.key], b = pts[i][s.key];
      if (a == null || b == null) continue;
      const col = s.band ? `var(--band-${s.band(s.worse(a, b))})` : s.color;
      segs += `<line x1="${x(i - 1).toFixed(1)}" y1="${y(a).toFixed(1)}" x2="${x(i).toFixed(1)}" y2="${y(b).toFixed(1)}" stroke="${col}"${s.dash ? ' stroke-dasharray="7 5"' : ''}/>`;
    }
    svg += `<g class="series" data-series="${s.key}">${segs}</g>`;
  }
  // Direct labels at the right end, pushed apart when the lines end close together.
  const ends = series.map(s => ({ s, v: pts[n - 1][s.key] })).filter(e => e.v != null).map(e => ({ ...e, y: y(e.v) + 4 })).sort((a, b) => a.y - b.y);
  for (let i = 1; i < ends.length; i++) if (ends[i].y - ends[i - 1].y < 15) ends[i].y = ends[i - 1].y + 15;
  svg += ends.map(e => `<text class="direct" x="${W - Rt + 8}" y="${e.y}">${esc(e.s.short)}</text>`).join('');
  if (o.selected != null) svg += `<line class="sel" x1="${x(o.selected)}" x2="${x(o.selected)}" y1="${T}" y2="${T + ih}"/>`;
  svg += `<line class="cross" x1="0" x2="0" y1="${T}" y2="${T + ih}" visibility="hidden"/><rect class="hit" x="${L}" y="${T}" width="${iw}" height="${ih}"/></svg>`;
  const legend = `<div class="legend">${series.map(s => `<span><svg width="28" height="10" aria-hidden="true"><line x1="0" x2="28" y1="5" y2="5" stroke="${s.color || 'var(--text)'}" stroke-width="2.5"${s.dash ? ' stroke-dasharray="7 5"' : ''}/></svg>${esc(s.label)}</span>`).join('')}
    ${o.bands ? `<span class="muted">Line color is the band of the value.</span>` : ''}<span class="muted">Click a time to see it below.</span></div>`;
  return `<div class="chart" data-chartbox="${id}">${legend}<div class="plot">${svg}<div class="tip" hidden></div></div></div>`;
}
function wireCharts(p) {
  for (const box of main.querySelectorAll('[data-chartbox]')) {
    const { pts, series, o } = CHARTS[box.dataset.chartbox];
    const svg = box.querySelector('svg.lc'), hit = svg.querySelector('rect.hit'), cross = svg.querySelector('line.cross'), tip = box.querySelector('.tip');
    const idx = ev => { const r = hit.getBoundingClientRect(); return Math.max(0, Math.min(pts.length - 1, Math.round((ev.clientX - r.left) / r.width * (pts.length - 1)))); };
    hit.addEventListener('mousemove', ev => {
      const i = idx(ev), r = hit.getBoundingClientRect(), sr = svg.getBoundingClientRect();
      const xv = +hit.getAttribute('x') + i / Math.max(1, pts.length - 1) * +hit.getAttribute('width');
      cross.setAttribute('x1', xv); cross.setAttribute('x2', xv); cross.setAttribute('visibility', 'visible');
      tip.innerHTML = `<strong>${esc(fmtPoint(pts[i].t, o.minutes))}</strong>${series.map(s => `<div>${esc(s.label)}: <strong>${pts[i][s.key] ?? '–'}${o.max === 100 ? '%' : ''}</strong>${s.who && pts[i][s.who] ? ` ${esc(pts[i][s.who])}` : ''}${s.band && pts[i][s.key] != null ? ` (${BAND_NAME[s.band(pts[i][s.key])]})` : ''}</div>`).join('')}`;
      tip.hidden = false;
      const left = ev.clientX - sr.left;
      tip.style.left = `${Math.min(left + 14, sr.width - tip.offsetWidth - 4)}px`; tip.style.top = `${ev.clientY - sr.top + 12}px`;
    });
    hit.addEventListener('mouseleave', () => { cross.setAttribute('visibility', 'hidden'); tip.hidden = true; });
    hit.addEventListener('click', ev => { location.href = url({ at: pts[idx(ev)].t }); });
  }
  main.querySelectorAll('[data-cls]').forEach(a => a.addEventListener('click', ev => { ev.preventDefault(); location.href = url({ cls: a.dataset.cls }); }));
}
function groupBy(d, note = '') {
  let h = `<div class="toolbar"><label for="grp">Group by</label><select id="grp">${GROUP_BY.map(([k, l]) => `<option value="${k}"${k === R.group ? ' selected' : ''}>${l}</option>`).join('')}</select>${note}</div>`;
  if (d.group_by) {
      h += `<table class="data" data-groupby="${d.group_by.attribute}"><thead><tr><th>${esc(GROUP_BY.find(g => g[0] === d.group_by.attribute)[1])}</th>${d.group_by.rows[0] && 'hosts' in d.group_by.rows[0] ? '<th class="num">Hosts</th>' : ''}<th class="num">VMs</th><th class="num">Below green</th><th class="num">Just above the line</th><th class="num">Wider than their host's NUMA node</th><th class="num">Worst</th><th>Status</th></tr></thead><tbody>
        ${d.group_by.rows.map(r => `<tr data-group="${esc(r.value)}"><td>${esc(r.value)}</td>${'hosts' in r ? `<td class="num">${n0(r.hosts)}</td>` : ''}<td class="num">${n0(r.vms)}</td><td class="num">${n0(r.below_green)}</td><td class="num">${n0(r.near_line)}</td><td class="num">${n0(r.wider_than_numa_node)}</td><td class="num">${r.worst}</td><td>${chip(r.status)}</td></tr>`).join('')}</tbody></table>`;
    }
  return h;
}
function perfTab(p, d) {
  const cls = CLASS_NAME[p.class], m = p.point_minutes, sel = p.selected, C = p.consumer, P = p.provider;
  const when = fmtPoint(sel.t, m);
  const filter = `<div class="toolbar"><span class="lbl">Class of service</span><nav class="windows" aria-label="Class of service">${p.classes.map(k => `<a href="${url({ cls: k })}" data-cls="${k}"${k === p.class ? ' aria-current="true"' : ''}>${CLASS_NAME[k]}</a>`).join('')}</nav>
    ${sel.default ? '' : `<a class="link" href="${url({ at: '' })}">Back to the worst time</a>`}</div>
    ${p.stale_locations.length ? `<p class="why">No data from ${esc(p.stale_locations.join(', '))}. Left out, never counted as green.</p>` : ''}`;
  // VM
  const vmChart = lineChart('vm', C.points, [
    { key: 'below_green', label: 'VMs below green at that time', short: 'At that time', color: 'var(--series-1)' },
    { key: 'different', label: 'Different VMs hit since the window started', short: 'Different', color: 'var(--series-2)', dash: true }],
    { label: `${cls} VMs hit over the window`, minutes: m, selected: sel.default ? null : sel.index });
  const vmRows = C.worst_vms.map(v => `<tr data-vm="${esc(v.vm)}"><td>${objLink(v.vm)}</td><td class="num">${v.vm_performance}</td><td>${chip(v.status)}</td><td>${esc(fmtPoint(v.at, 5))}</td><td>${objLink(v.cluster)}</td><td>${esc(v.location)}</td><td class="num">${n0(v.together)}</td></tr>`).join('');
  let vm = `<section class="persp" data-section="vm"><h2>VM <span class="muted">consumer</span></h2>
    <p>${C.vms ? `${n0(C.different)} different ${esc(cls)} VMs were below green in the window, of ${n0(C.vms)}. Never more than ${n0(C.most_at_once)} at once, at ${esc(fmtPoint(C.most_at, m))}.` : `No ${esc(cls)} VM under this object.`}
    ${C.vms ? ` ${n0(C.near_line)} sit just above the line (75 to 80) over the window.` : ''}</p>
    ${C.vms ? vmChart : ''}
    <h3>${sel.default ? 'Worst VMs in the window' : `VMs below green at ${esc(when)}`} <span class="muted">${n0(C.worst_vms_total)} in all${C.worst_vms_total > C.worst_vms.length ? `, the worst ${C.worst_vms.length} shown` : ''}</span></h3>
    ${C.worst_vms.length ? `<table class="data" data-worst-vms><thead><tr><th>VM</th><th class="num">VM Performance</th><th>Status</th><th>Time</th><th>Cluster</th><th>Location</th><th class="num">Other VMs hit in the same 5 minutes</th></tr></thead><tbody>${vmRows}</tbody></table>
    <p class="muted">The same time on many rows: something common hit them. Different times: one cluster, or one VM.</p>` : `<p class="muted">No ${esc(cls)} VM was below green${sel.default ? ' in the window' : ' at that time'}.</p>`}
    ${groupBy(d, '<span class="muted">every class, every VM under this object</span>')}</section>`;
  // Cluster
  const minutesOut = key => P.performance.filter(x => x[key] != null && x[key] < 75).length * m;
  const low = P.performance.reduce((a, x) => x.worst != null && (a == null || x.worst < a.worst) ? x : a, null);
  const outW = minutesOut('worst'), outP = minutesOut('percentile');
  const perfLine = !P.clusters ? `No ${esc(cls)} cluster under this object.`
    : !outW ? `Every ${esc(cls)} cluster stayed green.`
    : `Lowest: ${low.worst}% at ${esc(fmtPoint(low.t, m))}, ${esc(low.worst_cluster)}; the 5th percentile then ${low.percentile}%. The worst cluster was out of green for ${fmtDur(outW)}. ${outP ? `The 5th percentile was out of green for ${fmtDur(outP)}: wide at those times.` : 'The 5th percentile stayed green: narrow, a few clusters or one.'}`;
  const rNow = P.risk[P.risk.length - 1];
  const riskLine = !P.clusters ? '' : `Highest now: ${rNow.worst}% (${BAND_NAME[riskBand(rNow.worst)]}), ${esc(rNow.worst_cluster)}. The 95th percentile now: ${rNow.percentile}% (${BAND_NAME[riskBand(rNow.percentile)]}).`;
  const perfBands = [[75, 100, 'green'], [50, 75, 'yellow'], [25, 50, 'orange'], [0, 25, 'red']];
  const riskBands = [[0, 25, 'green'], [25, 50, 'yellow'], [50, 75, 'orange'], [75, 100, 'red']];
  const minOf = (a, b) => Math.min(a, b), maxOf = (a, b) => Math.max(a, b);
  const perfChart = lineChart('perf', P.performance, [
    { key: 'worst', who: 'worst_cluster', label: 'Worst Cluster Performance', short: 'Worst', band: perfBand, worse: minOf },
    { key: 'percentile', label: `${P.percentile.performance}th percentile`, short: `${P.percentile.performance}th pct`, band: perfBand, worse: minOf, dash: true }],
    { label: 'Actual slowness: Cluster Performance, 0 to 100%', max: 100, minutes: m, bands: perfBands, selected: sel.index });
  const riskChart = lineChart('risk', P.risk, [
    { key: 'worst', who: 'worst_cluster', label: 'Highest Cluster Risk', short: 'Highest', band: riskBand, worse: maxOf },
    { key: 'percentile', label: `${P.percentile.risk}th percentile`, short: `${P.percentile.risk}th pct`, band: riskBand, worse: maxOf, dash: true }],
    { label: 'Potential slowness: Cluster Risk, 0 to 100%', max: 100, minutes: m, bands: riskBands, selected: sel.index });
  const bchip = (v, b) => `<span class="chip ${statusOfBand(b)}">${v}%</span>`;
  const atRows = p.clusters_at.map(r => `<tr data-cluster-at="${esc(r.cluster)}"><td>${objLink(r.cluster)}</td><td>${esc(r.location)}</td><td>${esc(CLASS_NAME[r.class_of_service] || r.class_of_service)}</td><td class="num">${bchip(r.performance, r.performance_band)}</td><td class="num">${bchip(r.risk, r.risk_band)}</td><td class="num">${n0(r.vms_hit)}</td><td class="num">${n0(r.different_vms_hit)}</td></tr>`).join('');
  const cl = `<section class="persp" data-section="cluster"><h2>Cluster <span class="muted">provider</span></h2>
    ${P.clusters ? `<h3>Actual slowness</h3><p data-perf-line>${perfLine}</p>${perfChart}
    <h3>Potential slowness</h3><p data-risk-line>${riskLine}</p>${riskChart}
    <h3 data-at="${esc(sel.t)}">Clusters at ${esc(when)} <span class="muted">${sel.default ? 'the worst point of the window' : 'the time you picked'}; worst first</span></h3>
    <table class="data" data-clusters-at><thead><tr><th>Cluster</th><th>Location</th><th>Class</th><th class="num">Performance</th><th class="num">Risk</th><th class="num">VMs below green then</th><th class="num">Different VMs hit in the window</th></tr></thead><tbody>${atRows}</tbody></table>`
    : `<p class="muted">No ${esc(cls)} cluster under this object.</p>`}</section>`;
  return filter + vm + cl;
}
function childrenTable(d) {
  if (!d.children.length) return '';
  const extra = d.children[0].kind === 'host' ? ['Host model', 'ESXi build', 'VMs'] : d.children[0].kind === 'vm' ? ['vCPU', 'Class', 'Environment'] : [];
  return `<h2>Children, worst first</h2><table class="data" data-children><thead><tr><th>Name</th><th>Kind</th><th class="num">Over ${R.window}</th>${R.window !== '1h' ? '<th class="num">Last hour</th>' : ''}<th>Status</th><th class="num">Alerts</th>${extra.map(x => `<th>${x}</th>`).join('')}</tr></thead><tbody>
    ${d.children.map(r => `<tr data-child="${esc(r.id)}"><td>${objLink(r.id, r.name)}</td><td>${esc(KIND[r.kind] || r.kind)}</td><td class="num">${r.score ?? '–'}</td>${R.window !== '1h' ? `<td class="num">${r.score_now ?? '–'}</td>` : ''}<td>${chip(r.status)}</td><td class="num">${r.alerts.red ? `<span class="chip red">${r.alerts.red} red</span>` : ''}${r.alerts.orange ? ` <span class="chip amber">${r.alerts.orange} orange</span>` : ''}</td>
      ${r.kind === 'host' ? `<td>${esc(r.host_model)}</td><td>${esc(r.esxi_build)}</td><td>${r.running_vms}</td>` : r.kind === 'vm' ? `<td>${r.vcpu}</td><td>${esc(r.class_of_service)}</td><td>${esc(r.environment.replace('_', '-'))}</td>` : ''}</tr>`).join('')}</tbody></table>
    ${d.children_truncated ? `<p class="muted">${n0(d.children_truncated)} more, all better than the ones above. Search finds any of them.</p>` : ''}`;
}

// ---------------------------------------------------------------- Troubleshoot (troubleshoot.md, case.md)
async function troubleshoot(msg = '') {
  if (R.newComplaint) return complaintForm();
  if (R.caseId) return casePage(msg);
  remember();
  const [list, t] = await Promise.all([getJSON('cases', `object=${enc(R.object)}`), getJSON('tree', treeQ(R.object))]);
  const vmish = ['vm', 'guest_os'].includes(t.node.kind);
  main.innerHTML = objHead(t.node, 'No window: each case has its own') + `<div class="toolbar"><h2 style="margin:0">Cases under ${esc(t.node.name)}</h2><span style="flex:1"></span>
    <a class="act" style="text-decoration:none;display:inline-block;padding:8px 16px;border-radius:999px;background:var(--text);color:#fff;font-weight:700" href="${complaintURL(vmish ? R.object : '')}" data-log>Log complaint</a></div>
    <div class="msg" role="status">${esc(msg)}</div>
    ${list.length ? `<table class="data" data-cases><thead><tr><th>Trigger</th><th>Case</th><th>Object</th><th>Opened</th><th>Chain so far</th><th>State</th></tr></thead><tbody>
    ${list.map(c => `<tr data-case="${c.id}"><td><span class="chip ${c.trigger === 'escalation' ? 'amber' : c.trigger === 'finding' ? 'blue' : 'no_data'}">${TRIGGER[c.trigger]}</span></td><td><a href="${url({ caseId: c.id })}">${esc(c.title)}</a><div class="muted">${esc(c.symptom)}</div></td>
      <td>${objLink(c.object)}<div class="muted">${c.path.slice(1, -1).map(esc).join(' › ')}</div></td><td>${fmtTime(c.opened_at)}<div class="muted">by ${esc(c.opened_by)}</div></td>
      <td>${c.links.confirmed} confirmed, ${c.links.proposed} proposed, ${c.links.ruled_out} ruled out</td><td>${c.state === 'open' ? '<span class="chip red">Open</span>' : '<span class="chip green">Closed</span>'}</td></tr>`).join('')}</tbody></table>`
      : '<p>No open case under this object.</p>'}`;
}

async function complaintForm(msg = '') {
  const vm = QS.get('vm') || '';
  main.innerHTML = `<h1>Log complaint</h1><p class="muted">A complaint names a VM or its Guest OS. A complaint about an application is logged against its VMs.</p>
    <form class="stack" id="cf"><label>VM<input type="text" name="vm" value="${esc(vm)}" list="vms" autocomplete="off" required></label><datalist id="vms"></datalist>
    <label>Who complained<input type="text" name="requester" required></label><label>Through whom (optional)<input type="text" name="via"></label>
    <label>Symptom<select name="symptom"><option value="slow">Slow</option><option value="down">Down</option></select></label>
    <label>Since<input type="datetime-local" name="since" required></label><label>Fine until (optional)<input type="datetime-local" name="fine_until"></label>
    <label>What they already checked, one per line (optional)<textarea name="already_checked"></textarea></label>
    <div><button type="submit" class="act">Open the case</button></div><div class="msg" role="status" id="cfmsg">${esc(msg)}</div></form>`;
  const now = QS.get('now') ? new Date(QS.get('now')) : new Date();
  const local = d => { const z = new Date(d.getTime() - d.getTimezoneOffset() * 60000); return z.toISOString().slice(0, 16); };
  const f = document.getElementById('cf');
  f.elements.since.value = local(new Date(now.getTime() - 65 * 60000));
  f.elements.vm.addEventListener('input', async e => {
    const res = await getJSON('search', `q=${enc(e.target.value)}`).catch(() => []);
    document.getElementById('vms').innerHTML = res.filter(x => x.kind === 'vm').map(x => `<option value="${esc(x.id)}">`).join('');
  });
  f.addEventListener('submit', async e => {
    e.preventDefault();
    const body = Object.fromEntries(new FormData(f));
    const iso = v => v ? new Date(v).toISOString() : '';
    body.since = iso(body.since); body.fine_until = iso(body.fine_until);
    const r = await postJSON('cases', { trigger: 'complaint', ...body });
    if (r.status === 200) location.href = url({ caseId: r.body.id, newComplaint: undefined });
    else { document.getElementById('cfmsg').textContent = r.body.error; document.body.dataset.complaint = String(r.status); }
  });
}

function chainTree(links, effect, open) {
  const kids = links.filter(l => l.effect === effect);
  if (!kids.length) return '';
  return `<ul class="links">${kids.map(l => `<li><div class="clink ${l.state}" data-link="${l.id}">
    <div class="cause">${esc(l.cause)}</div>
    <div class="meta">${objLink(l.object)} · ${LAYER[l.layer] || esc(l.layer)} · ${STEP[l.step] || esc(l.step)} · proposed by Agent E2, flow ${esc(l.flow)} · <span class="chip ${l.kind === 'main' ? 'blue' : 'no_data'}">${l.kind === 'main' ? 'Main' : 'Contributing'}</span></div>
    <ul>${l.evidence.map(x => `<li>${esc(x)}</li>`).join('')}</ul>
    <div class="acts">${l.state === 'proposed' && open ? `<button type="button" class="act" data-confirm="${l.id}">Confirm</button><button type="button" class="act secondary" data-ruleout="${l.id}">Rule out</button>`
      : l.state === 'confirmed' ? `<span class="chip green">Confirmed</span> <span class="muted">by ${esc(l.decided_by)}</span>`
      : l.state === 'ruled_out' ? `<span class="chip no_data">Ruled out</span> <span class="muted">by ${esc(l.decided_by)}: ${esc(l.reason)}</span>` : '<span class="chip amber">Proposed</span>'}</div></div>
    ${chainTree(links, l.id, open)}</li>`).join('')}</ul>`;
}

async function casePage(msg = '') {
  const d = await getJSON(`cases/${enc(R.caseId)}`).catch(() => null);
  if (!d) { main.innerHTML = '<h1>No such case</h1>'; return; }
  const open = d.state === 'open';
  const head = `<div class="objhead"><div><div class="crumbs">${d.path.slice(0, -1).map(p => esc(p)).join(' › ')}</div><div class="kind">Case · ${TRIGGER[d.trigger]}</div><h1>${esc(d.title)}</h1>
    <div class="muted">${objLink(d.object)} · ${esc(d.symptom)} · opened ${fmtTime(d.opened_at)} by ${esc(d.opened_by)} · ${open ? '<span class="chip red">Open</span>' : '<span class="chip green">Closed</span>'}</div></div>
    <div class="windows fixed">Case window: ${fmtTime(d.window_from)} to now</div></div>`;
  let started = '';
  if (d.complaint) {
    const c = d.complaint;
    started = `<div class="panel"><h2 style="margin-top:0">What started it: a complaint</h2><div class="row"><strong>${esc(c.requester)}</strong>${c.via ? `, through ${esc(c.via)}` : ''}: ${esc(d.symptom)} since ${fmtTime(c.since)}; fine until ${fmtTime(c.fine_until)}.</div>
      ${c.already_checked && c.already_checked.length ? `<p class="muted">They already checked:</p><ul>${c.already_checked.map(x => `<li>${esc(x)}</li>`).join('')}</ul><p class="muted">What they checked is the start of the evidence, not the end.</p>` : ''}</div>`;
  } else if (d.escalation) {
    const e = d.escalation;
    const vic = (e.victims || []).map(v => `<tr><td>${objLink(v.vm)}</td><td>VM Performance ${v.vm_performance}</td><td>CPU Ready ${v.cpu_ready_percent}%</td><td>Co-stop ${v.co_stop_percent}%</td></tr>`).join('');
    const vil = (e.villains || []).map(v => `<tr><td>${objLink(v.vm)}</td><td>${v.class}, ${v.environment}</td><td>CPU usage ${v.cpu_usage_percent}% of ${v.vcpu} vCPU</td><td>CPU Ready ${v.cpu_ready_percent}%</td></tr>`).join('');
    started = `<div class="panel"><h2 style="margin-top:0">What started it: an escalation from L1</h2><p class="muted">Escalated by ${esc(e.by)} to ${esc(e.route)}. The evidence L1 gathered arrived with it.</p>
      ${e.users ? `<p>${esc(e.users)}</p>` : ''}<h3>SOP steps run by L1</h3><ul>${(e.sop_steps || []).map(s => `<li>${esc(s.text)} <span class="muted">${esc(s.result)}</span></li>`).join('')}</ul>
      <h3>What L1 already did</h3>${(e.l1_actions || []).length ? `<ul>${e.l1_actions.map(a => `<li>${esc(a.action.replaceAll('_', ' '))} on ${esc(a.target)} by ${esc(a.by)}: ${esc(a.after)}</li>`).join('')}</ul>` : '<p class="muted">Nothing.</p>'}
      ${vil ? `<h3>Villains</h3><table class="data"><tbody>${vil}</tbody></table>` : ''}${vic ? `<h3>Victims</h3><table class="data"><tbody>${vic}</tbody></table>` : ''}
      <div class="toolbar">${d.accepted ? `<span class="chip ${d.accepted.state === 'accepted' ? 'green' : 'amber'}">${d.accepted.state === 'accepted' ? 'Accepted' : 'Rejected'}</span> <span class="muted">by ${esc(d.accepted.by)}${d.accepted.reason ? ': ' + esc(d.accepted.reason) : ''}</span>`
        : `<button type="button" class="act" data-accept>Accept</button><button type="button" class="act secondary" data-rejectesc>Reject, with a reason</button>`}</div></div>`;
  } else if (d.finding_detail) {
    const f = d.finding_detail;
    started = `<div class="panel"><h2 style="margin-top:0">What started it: a monitoring finding</h2><p>${esc(f.summary)}</p>
      ${f.evidence && f.evidence.nightly ? `${bars(f.evidence.nightly, true)}<div class="muted">Last 7 nights, ${esc(f.evidence.unit)}: ${f.evidence.nightly.join(', ')}</div>` : ''}
      <p><a class="link" href="${url({ activity: 'monitor', caseId: undefined, object: f.object, view: 'compute', pillar: f.pillar, window: f.window, group: f.evidence && f.evidence.group_by ? f.evidence.group_by : '' })}">See it in Monitor</a></p></div>`;
  }
  const realm = (name, r) => `<div class="card ${r.status}"><h3>${name} ${chip(r.status)}</h3>${Object.entries(r).filter(([k]) => k !== 'status').map(([k, v]) => `<div class="row"><span>${esc(k.replaceAll('_', ' '))}</span><span>${v}</span></div>`).join('')}</div>`;
  const tl = d.timeline.map(e => { const before = e.at < d.window_from;
    return `<li class="${before ? 'before' : ''}"><span>${fmtTime(e.at)}</span><span class="k">${esc(e.kind.replaceAll('_', ' '))}</span><span><strong>${esc(e.object)}</strong>: ${esc(e.text)}${e.explained_by ? ` <span class="muted">· explained by ${esc(e.explained_by.replaceAll('_', ' '))}</span>` : ''}</span></li>`; });
  const wi = d.timeline.findIndex(e => e.at >= d.window_from);
  if (wi >= 0) tl.splice(wi, 0, `<li class="mark">Case window starts: ${fmtTime(d.window_from)}</li>`);
  const we = d.who_else;
  main.innerHTML = head + `<div class="msg" role="status">${esc(msg)}</div>` + started + `
    <h2>Chain of causes</h2><div class="chainroot">Symptom: ${esc(d.title)}</div>
    ${d.chain.length ? chainTree(d.chain, 'symptom', open) : '<p class="muted">Nothing proposed yet. Ask Agent E2 to propose the first link.</p>'}
    ${open ? `<div class="toolbar"><button type="button" class="act" id="propose"${d.more_to_propose ? '' : ' disabled'}>Propose the next link</button><span class="muted">${d.more_to_propose ? `Agent E2 follows its flows: ${d.chain.length} of the links it can propose so far.` : 'Agent E2 has nothing more to propose from its flows.'}</span></div>` : ''}
    ${d.realms ? `<h2>VM and Guest OS, side by side</h2><div class="cols2">${realm('VM', d.realms.vm)}${realm('Guest OS', d.realms.guest_os)}</div>` : ''}
    <h2>Layers</h2><table class="data" data-layers><tbody>${d.layers.map(l => `<tr><td>${LAYER[l.layer]}</td><td><span class="chip ${VERDICT[l.verdict][0]}">${VERDICT[l.verdict][1]}</span></td><td>${esc(l.values)}</td></tr>`).join('')}</tbody></table>
    ${d.hand_over ? `<div class="conclusion" data-handover>${esc(d.hand_over)}</div>` : ''}
    <h2>Timeline</h2><ul class="timeline">${tl.join('')}</ul>
    <h2>Who else</h2>${we && we.count ? `<p>${n0(we.count)} object${we.count === 1 ? '' : 's'} share it: ${esc(we.test)}.</p><p>${we.objects.map(o => objLink(o)).join(', ')}</p><p><a class="link" href="${url({ activity: 'rules', caseId: undefined })}">Add a check rule</a></p>` : '<p class="muted">No other object shows this symptom.</p>'}
    <h2>Agent E2</h2><form class="inline" id="ask"><label>Question<input type="text" name="question" size="60" value="Is the VMware platform the cause? What should I check next?"></label><button type="submit" class="act">Ask Agent E2 why</button><button type="button" class="act secondary" id="draft">Draft the root cause analysis</button></form>
    <div class="draft" id="answer" aria-live="polite"><span class="muted">Agent E2 reads the knowledge base and the facts of this case. It explains and drafts; you decide.</span></div>
    <h2>Close</h2>${d.closure ? `<p data-closed><strong>Closed</strong> by ${esc(d.closure.by)}: ${esc(d.closure.root_cause)}. Fix: ${esc(d.closure.corrective_action)}. Detection: ${esc(DETECTION[d.closure.detection])}, ${esc(d.closure.detection_note)}</p>`
      : `<form class="stack" id="close"><label>Root cause<input type="text" name="root_cause" value="${esc(d.root_cause_prefill)}"></label><label>Corrective action<input type="text" name="corrective_action"></label>
      <label>Detection<select name="detection"><option value="">Choose</option>${d.detections.map(x => `<option value="${x}">${DETECTION[x]}</option>`).join('')}</select></label><label>Detection note<input type="text" name="detection_note"></label>
      <div class="toolbar"><label style="flex:1">A log message to detect it? Count it on healthy objects first<input type="text" id="logmsg" placeholder="Log message"></label><button type="button" class="act secondary" id="validate">Validate</button><span id="valout" class="muted"></span></div>
      <div><button type="submit" class="act">Close the case</button></div></form>
      <p class="muted">A suspected breach is not a case: hand the logs, events and configuration of the window to the security team.</p>`}`;
  const reload = m => casePage(m);
  const p = document.getElementById('propose');
  if (p) p.addEventListener('click', async () => { p.disabled = true; const r = await postJSON(`cases/${enc(d.id)}/propose`, {}); reload(r.body.link ? `Agent E2 proposed: ${r.body.link.cause}` : r.body.message); });
  main.querySelectorAll('[data-confirm]').forEach(b => b.addEventListener('click', async () => { const r = await postJSON(`cases/${enc(d.id)}/links/${b.dataset.confirm}/confirm`, {}); reload(r.status === 200 ? 'Confirmed.' : r.body.error); }));
  main.querySelectorAll('[data-ruleout]').forEach(b => b.addEventListener('click', async () => {
    const reason = prompt('Why rule it out? The link stays visible, with your reason.');
    const r = await postJSON(`cases/${enc(d.id)}/links/${b.dataset.ruleout}/rule-out`, { reason }); reload(r.status === 200 ? 'Ruled out, with the reason recorded.' : r.body.error);
  }));
  const acc = main.querySelector('[data-accept]');
  if (acc) acc.addEventListener('click', async () => { const r = await postJSON(`cases/${enc(d.id)}/accept`, {}); reload(r.status === 200 ? 'Accepted.' : r.body.error); });
  const rej = main.querySelector('[data-rejectesc]');
  if (rej) rej.addEventListener('click', async () => { const reason = prompt('What is missing? A rejected escalation points to a gap in the SOP.'); const r = await postJSON(`cases/${enc(d.id)}/reject`, { reason }); reload(r.status === 200 ? 'Rejected, with the reason recorded.' : r.body.error); });
  document.getElementById('ask').addEventListener('submit', async ev => {
    ev.preventDefault();
    const box = document.getElementById('answer'); box.innerHTML = '<span class="muted">Agent E2 is reading the knowledge base…</span>';
    const r = await postJSON(`cases/${enc(d.id)}/ask`, { question: ev.target.elements.question.value });
    box.innerHTML = r.body.source !== 'service' ? '<p class="why">The Agent E2 service is not available.</p>'
      : `<div>${esc(r.body.content).replace(/\n/g, '<br>')}</div><p class="muted">Knowledge files read: ${r.body.files_read.map(esc).join(', ')}</p><p class="muted">Model: ${esc(r.body.model)} · asked by ${esc(r.body.record.actor_human)} · recorded in the action history</p>`;
    document.body.dataset.ask = r.body.source;
  });
  document.getElementById('draft').addEventListener('click', async () => {
    const box = document.getElementById('answer'); box.innerHTML = '<span class="muted">Agent E2 is drafting…</span>';
    const r = await postJSON(`cases/${enc(d.id)}/draft`, {});
    box.innerHTML = (r.body.source !== 'model' ? '<p class="why">Agent E2 is not available, or used words not allowed here. Showing the fixed template.</p>' : '') + `<p>${esc(r.body.text)}</p><p class="muted">Model: ${esc(r.body.model)} · asked by ${esc(r.body.record.actor_human)} · recorded in the action history</p>`;
    document.body.dataset.agent = r.body.source;
  });
  const v = document.getElementById('validate');
  if (v) v.addEventListener('click', async () => {
    const r = await getJSON('log-validation', `message=${enc(document.getElementById('logmsg').value)}`);
    document.getElementById('valout').textContent = `Seen ${n0(r.healthy_count_5_days)} times on healthy objects in 5 working days. ${r.noise ? 'Noise: do not alert on it.' : 'Rare enough to detect.'}`;
  });
  const cf = document.getElementById('close');
  if (cf) cf.addEventListener('submit', async ev => {
    ev.preventDefault();
    const r = await postJSON(`cases/${enc(d.id)}/close`, Object.fromEntries(new FormData(cf)));
    reload(r.status === 200 ? 'Closed with a cause, a fix and a detection decision. The detection waits in Rules.' : r.body.error);
  });
}

// ---------------------------------------------------------------- Improve (improve.md)
async function improve(msg = '') {
  remember();
  const d = await getJSON(`improve/${R.view}/${enc(R.object)}/${R.pillar}`, `window=${R.window}`);
  const st = Object.fromEntries(d.pillars.map(p => [p.pillar, p.opportunities + p.risks ? 'amber' : 'green']));
  const opp = o => `<div class="finding" data-opportunity="${o.id}"><span class="chip amber">${PNAME[o.pillar]}</span><div><div class="chain">${esc(o.object_name)} · ${esc(o.size)}</div><strong>${esc(o.what)}</strong><div class="muted">${esc(o.why)}</div>
    ${o.proposal ? `<div class="proposal"><strong>Proposed fix:</strong> ${esc(o.proposal.reason)} ${o.proposal.state === 'waiting' ? `<button type="button" class="act" data-approve="${o.proposal.id}">Approve</button> <button type="button" class="act secondary" data-reject="${o.proposal.id}">Reject</button>`
      : o.proposal.state === 'ran_automatically' ? `<strong>Ran automatically</strong> under ${esc(o.proposal.accountable)}. No approval: the policy decided.` : `<strong>${esc(o.proposal.state)}</strong> by ${esc(o.proposal.decided_by)}${o.proposal.rejection_reason ? `: ${esc(o.proposal.rejection_reason)}` : ''}`}</div>` : ''}</div></div>`;
  let body = '';
  if (R.pillar === 'summary') {
    body += `<table class="data pillars"><thead><tr><th>Pillar</th><th class="num">Opportunities</th><th class="num">Risks found by the checks</th></tr></thead><tbody>${d.pillars.map(p => `<tr><td><a href="${url({ pillar: p.pillar })}">${PNAME[p.pillar]}</a></td><td class="num">${p.opportunities}</td><td class="num">${p.risks}</td></tr>`).join('')}</tbody></table>`;
    if (d.decisions) {
      const DS = { done: ['green', 'Done'], open: ['no_data', 'Open'], overdue: ['red', 'Overdue'] };
      body += `<h2>Decision register</h2><p class="muted">The monthly review opens here, then Monitor at the estate with the 1-year window.</p>${d.decisions.length ? `<table class="data"><thead><tr><th>Decision</th><th>Owner</th><th>Due</th><th>State</th><th></th></tr></thead><tbody>${d.decisions.map(x => `<tr data-decision="${x.id}"><td>${esc(x.what)}</td><td>${esc(x.owner)}</td><td>${fmtDay(x.due)}</td>
        <td><span class="chip ${DS[x.state][0]}">${DS[x.state][1]}</span></td><td>${x.done ? `<span class="muted">by ${esc(x.done.by)}, ${fmtDay(x.done.at)}</span>` : `<button type="button" class="act secondary" data-done="${x.id}">Mark done</button>`}</td></tr>`).join('')}</tbody></table>` : '<p class="muted">No decision is open.</p>'}
        <form class="inline" id="dec"><label>Decision<input type="text" name="what" size="40"></label><label>Owner<input type="text" name="owner"></label><label>Due<input type="text" name="due" placeholder="YYYY-MM-DD"></label><button class="act" type="submit">Record</button></form>`;
    }
    body += `<h2>Opportunities, largest first</h2>${d.opportunities.length ? d.opportunities.map(opp).join('') : '<p class="muted">Nothing to improve under this object.</p>'}`;
  } else if (R.pillar === 'configuration') {
    body += Object.entries(d.configuration).map(([g, items]) => `<h2>${GROUP[g]}</h2>` + (items.length ? `<table class="data"><thead><tr><th>Object</th><th>Setting</th><th>Actual</th><th>Standard</th><th></th></tr></thead><tbody>${items.map(i => `<tr data-config="${i.id}">
      <td>${esc(i.object)}</td><td>${esc(i.setting_label || i.setting)}</td><td>${esc(i.actual)}</td><td>${esc(i.standard)} <span class="muted">(v${i.standard_version})</span></td>
      <td>${i.decision ? esc(i.decision.replaceAll('_', ' ')) : `<button type="button" class="act" data-fix="${i.id}" data-choice="fix_the_setting">Fix the setting</button> <button type="button" class="act secondary" data-fix="${i.id}" data-choice="fix_the_standard">Fix the standard</button>`}</td></tr>`).join('')}</tbody></table>`
      : `<p class="muted">Nothing to ${GROUP[g].toLowerCase().replace(' it', '')}.</p>`)).join('');
  } else {
    body += `<h2>Opportunities, largest first</h2>${d.opportunities.length ? d.opportunities.map(opp).join('') : '<p class="muted">Nothing to improve under this object.</p>'}`;
  }
  body += d.findings.length ? `<h2>Risks the checks found</h2>${d.findings.map(findingRow).join('')}` : '';
  main.innerHTML = objHead(d.object) + `<p class="runline">Framed in capacity: what it frees, how far it moves the next purchase decision.</p>` + tabs(st) + `<div class="msg" role="status">${esc(msg)}</div>` + body;
  wireFindings(improve);
  main.querySelectorAll('[data-fix]').forEach(b => b.addEventListener('click', async () => {
    const r = await postJSON(`configuration/${b.dataset.fix}/decide`, { choice: b.dataset.choice });
    improve(r.body.proposal ? 'A proposal now waits for approval.' : r.body.standard_version ? `Standard updated to version ${r.body.standard_version}.` : r.body.error);
  }));
  main.querySelectorAll('[data-done]').forEach(b => b.addEventListener('click', async () => { const r = await postJSON(`decisions/${b.dataset.done}/done`, {}); improve(r.status === 200 ? 'Marked done.' : r.body.error); }));
  const dec = document.getElementById('dec');
  if (dec) dec.addEventListener('submit', async e => {
    e.preventDefault();
    const r = await postJSON('decisions', Object.fromEntries(new FormData(dec)));
    await improve(r.status === 200 ? `Recorded as ${r.body.id}.` : r.body.error); document.body.dataset.decision = String(r.status);
  });
}

// ---------------------------------------------------------------- Rules (rules.md)
async function rules(msg = '') {
  const [drafts, th, pol] = await Promise.all([getJSON('rules/drafts'), getJSON('thresholds'), getJSON('policies')]);
  main.innerHTML = `<h1>Rules</h1><p class="muted">What L1 and PCM run. Every threshold is replayed before it ships; every policy change is replayed and owned.</p><div class="msg" role="status">${esc(msg)}</div>
    <h2>Detections from closed cases</h2>${drafts.length ? `<table class="data"><thead><tr><th>Case</th><th>Detection</th><th>Note</th><th>Closed by</th><th>State</th></tr></thead><tbody>${drafts.map(x => `<tr><td><a href="${url({ activity: 'troubleshoot', caseId: x.case })}">${esc(x.title)}</a></td><td>${esc(DETECTION[x.detection])}</td><td>${esc(x.note)}</td><td>${esc(x.closed_by)}</td><td>${esc(x.state)}</td></tr>`).join('')}</tbody></table>` : '<p class="muted">No detection waits.</p>'}
    <h2>Thresholds</h2>` + th.map(t => `<section class="panel"><h3>${esc(t.metric)} ${esc(t.operator)} ${t.value} <span class="muted">(version ${t.version})</span></h3>
      <form class="inline" data-t="${t.id}"><label>New value<input type="number" name="value" value="${t.value}" step="1"></label><button type="submit" class="act secondary">Replay</button>
      <button type="button" class="act" data-publish="${t.id}" disabled>Publish</button></form><div id="r-${t.id}"></div></section>`).join('')
    + `<h2>Action policies</h2><p class="muted">What runs automatically, and within which guardrails. The record is evidence, never a gate.</p>
    <table class="data"><thead><tr><th>Action type</th><th>Tier</th><th>Guardrails</th><th>Version and owner</th><th>Record (evidence)</th><th></th></tr></thead><tbody>
    ${pol.map(p => `<tr data-policy="${p.action_type}"><td>${esc(p.action_type.replaceAll('_', ' '))}</td><td>${esc(p.tier)}</td>
      <td>${Object.entries(p.guardrails).map(([k, v]) => `${esc(k.replaceAll('_', ' '))}: ${esc(v)}`).join('<br>')}</td>
      <td>v${p.version}, ${esc(p.owner)}</td><td>${p.record.approvals} approved, ${p.record.rejections} rejected, ${p.record.rollbacks} rolled back</td>
      <td><button type="button" class="act secondary" data-propose="${p.action_type}">Propose a policy change</button></td></tr>`).join('')}</tbody></table><div id="policy-form"></div>`;
  main.querySelectorAll('form[data-t]').forEach(f => f.addEventListener('submit', async ev => {
    ev.preventDefault();
    const v = f.elements.value.value;
    const r = await getJSON(`thresholds/${f.dataset.t}/replay`, `value=${enc(v)}`);
    const max = Math.max(1, ...r.per_day.flatMap(x => [x.current, x.new]));
    document.getElementById('r-' + f.dataset.t).innerHTML = `<p>Over ${r.days} days: <strong>${r.total_current}</strong> alerts at the current value, <strong>${r.total_new}</strong> at ${r.new_value}.</p>
      <div class="bars" aria-label="Alerts per day, current then new">${r.per_day.map(x => `<span style="height:${100 * x.current / max}%"></span><span class="new" style="height:${100 * x.new / max}%"></span>`).join('')}</div>
      <p class="muted">Teal: current value. Amber: new value. An alert that fires every day teaches the NOC to ignore it.</p>`;
    const pub = f.querySelector('[data-publish]'); pub.disabled = false; pub.dataset.value = v; document.body.dataset.replayed = '1';
  }));
  main.querySelectorAll('[data-publish]').forEach(b => b.addEventListener('click', async () => {
    const r = await postJSON(`thresholds/${b.dataset.publish}/publish`, { value: b.dataset.value, reason: 'Replayed before publishing' });
    rules(r.status === 200 ? `Published as version ${r.body.version}.` : r.body.error);
  }));
  main.querySelectorAll('[data-propose]').forEach(b => b.addEventListener('click', () => policyForm(pol.find(p => p.action_type === b.dataset.propose))));
}
function policyForm(p) {
  const g = p.guardrails;
  const box = document.getElementById('policy-form');
  const num = k => (k in g) ? `<label>${esc(k.replaceAll('_', ' '))}<input type="number" name="${k}" value="${g[k]}"></label>` : '';
  const flag = k => (k in g) ? `<label>${esc(k.replaceAll('_', ' '))}<select name="${k}"><option value="true"${g[k] === true ? ' selected' : ''}>yes</option><option value="false"${g[k] === false ? ' selected' : ''}>no</option></select></label>` : '';
  box.innerHTML = `<section class="panel"><h3>Propose a policy change: ${esc(p.action_type.replaceAll('_', ' '))} (now v${p.version}, ${esc(p.tier)})</h3>
    <form class="inline" id="pf"><label>Tier<select name="tier">${['automatic', 'approval', 'never'].map(t => `<option${t === p.tier ? ' selected' : ''}>${t}</option>`).join('')}</select></label>
    ${num('max_vms_per_cluster_per_hour')}${flag('same_class_of_service_only')}${flag('not_in_close_week')}
    <button type="submit" class="act secondary">Replay</button><label>Reason<input type="text" name="reason" size="40"></label>
    <button type="button" class="act" id="publish" disabled>Publish</button></form><div id="replay"></div></section>`;
  const read = () => {
    const f = document.getElementById('pf'); const gr = { ...g };
    ['max_vms_per_cluster_per_hour'].forEach(k => { if (f.elements[k]) gr[k] = Number(f.elements[k].value); });
    ['same_class_of_service_only', 'not_in_close_week'].forEach(k => { if (f.elements[k]) gr[k] = f.elements[k].value === 'true'; });
    return { tier: f.elements.tier.value, guardrails: gr };
  };
  document.getElementById('pf').addEventListener('submit', async ev => {
    ev.preventDefault();
    const r = await postJSON(`policies/${p.action_type}/replay`, read());
    const s = Object.entries(r.body.stopped || {}).map(([k, v]) => `${v} stopped by ${esc(k.replaceAll('_', ' '))}`).join('; ') || 'none stopped';
    document.getElementById('replay').innerHTML = `<p>Replayed over the last ${r.body.runs} runs: <strong>${r.body.would_run_automatically}</strong> would have run automatically; ${s}.</p>`;
    document.getElementById('publish').disabled = false; document.body.dataset.policyReplayed = '1';
  });
  document.getElementById('publish').addEventListener('click', async () => {
    const f = document.getElementById('pf');
    const r = await postJSON(`policies/${p.action_type}/publish`, { ...read(), reason: f.elements.reason.value });
    rules(r.status === 200 ? `Published v${r.body.version}, owner ${r.body.owner}.${r.body.ran_automatically.length ? ' Ran automatically under it: ' + r.body.ran_automatically.join(', ') + '.' : ''}` : r.body.error);
  });
}

// ---------------------------------------------------------------- Calendar (calendar.md)
async function calendar(msg = '') {
  const list = await getJSON('calendar');
  main.innerHTML = `<h1>Calendar</h1><p class="muted">Business context. Monitor reads these entries before it judges; cases show them on their timeline.</p>
    ${list.length ? `<table class="data"><thead><tr><th>Kind</th><th>Location</th><th>Starts</th><th>Note</th><th>Added by</th></tr></thead><tbody>${list.map(c => `<tr><td>${esc(c.kind.replaceAll('_', ' '))}</td><td>${esc(c.location || 'All')}</td><td>${fmtTime(c.starts_at)}</td><td>${esc(c.note)}</td><td>${esc(c.added_by)}</td></tr>`).join('')}</tbody></table>`
      : '<p>Nothing on the calendar. The checks judge without business context.</p>'}
    <h2>Add an entry</h2><form class="inline" id="add"><label>Kind<select name="kind"><option value="month_end_close">Month-end close</option><option value="quarter_end_close">Quarter-end close</option><option value="payday">Payday</option><option value="migration">Migration</option><option value="dr_test">DR test</option><option value="maintenance_window">Maintenance window</option><option value="other">Other</option></select></label>
    <label>Location<select name="location"><option value="">All</option><option value="sg">Singapore</option><option value="va">Virginia</option><option value="fr">Frankfurt</option><option value="tk">Tokyo</option><option value="ld">London</option></select></label>
    <label>Start<input type="datetime-local" name="starts_at"></label><label>End<input type="datetime-local" name="ends_at"></label><label>Note<input type="text" name="note"></label><button type="submit" class="act">Add</button></form>
    <div class="msg" role="status">${esc(msg)}</div>`;
  document.getElementById('add').addEventListener('submit', async ev => {
    ev.preventDefault();
    const r = await postJSON('calendar', Object.fromEntries(new FormData(ev.target)));
    calendar(r.status === 200 ? 'Added. The next check reads it.' : r.body.error);
  });
}

// ---------------------------------------------------------------- start
(async () => {
  const RUN = { monitor, troubleshoot, improve, rules, calendar };
  try {
    const counts = getJSON('cases').then(l => l.filter(c => c.state === 'open').length).catch(() => 0);
    if (R.caseId) { const c = await getJSON(`cases/${enc(R.caseId)}`).catch(() => null); if (c) R.object = c.object; }
    const treeDone = tree().catch(() => { document.getElementById('tree').innerHTML = '<p class="muted">Could not load the tree.</p>'; });
    await Promise.all([topBar(await counts), (RUN[R.activity] || monitor)()]);
    await treeDone;
    document.body.dataset.ready = '1';
  } catch (e) {
    main.innerHTML = '<p>Could not load data. Try again later.</p>'; document.body.dataset.ready = 'error';
  }
})();
