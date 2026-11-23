// GENERATED from spec/workspaces/l2/ (frame, monitor, troubleshoot, case, improve, rules, calendar). Do not edit by hand (D-070).
// Agent E2: frame.md, Agent E2 mark and Agent E2 panel (D-097).
'use strict';
let QS = new URLSearchParams(location.search);
const passOf = q => ['now', 'enable'].filter(k => q.get(k)).map(k => `${k}=${encodeURIComponent(q.get(k))}`).join('&');
let PASS = passOf(QS);
const qjoin = (...xs) => xs.filter(Boolean).join('&');
const apiURL = (p, extra = '') => { const q = qjoin(PASS, extra); return `/api/l2/${p}${q ? '?' + q : ''}`; };
// One signal per navigation: a slow answer for the page we left must never overwrite the page we are on. The tree and the top bar pass null.
let SIG = null;
const getJSON = (p, extra, sig = SIG) => fetch(apiURL(p, extra), { signal: sig }).then(r => { if (!r.ok) throw new Error(r.status); return r.json(); });
const postJSON = (p, body) => { STATUS_CACHE.clear(); return fetch(apiURL(p), { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body || {}) })
  .then(async r => ({ status: r.status, body: await r.json().catch(() => ({})) })); };
const STATUS_CACHE = new Map();
const esc = s => String(s ?? '').replace(/[&<>"]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
const enc = encodeURIComponent;
const fmtTime = iso => new Date(iso).toLocaleString('en-GB', { day: 'numeric', month: 'short', hour: '2-digit', minute: '2-digit', timeZoneName: 'short' });
const fmtDay = iso => new Date(iso).toLocaleDateString('en-GB', { day: 'numeric', month: 'short', year: 'numeric' });
const n0 = v => Number(v).toLocaleString('en-US');
const STATUS = { green: 'Good', amber: 'Watch', red: 'Act now', no_data: 'No data' };
const chip = s => `<span class="chip ${s}">${STATUS[s] || esc(s)}</span>`;
const PILLARS = ['availability', 'performance', 'capacity', 'security', 'configuration', 'inventory'];
const PNAME = { summary: 'Summary', availability: 'Availability', performance: 'Performance', capacity: 'Capacity', security: 'Security', configuration: 'Configuration', inventory: 'Inventory' };
const WINDOWS = [['1h', 'Last hour'], ['24h', 'Last 24 hours'], ['7d', 'Last 7 days'], ['30d', 'Last 30 days'], ['1y', 'Last year']];
const KIND = { estate: 'Estate', region: 'Region', location: 'Location', vcf_instance: 'VCF instance', workload_domain: 'vCenter Server', cluster: 'Cluster', host: 'ESXi host', vm: 'VM', guest_os: 'Guest OS', datastore: 'Datastore', virtual_disk: 'Virtual disk', distributed_switch: 'Distributed switch', port_group: 'Port group', vnic: 'vNIC', class_of_service: 'Class of service', resource_pool: 'Resource pool' };
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
const landing = () => {
  if (location.pathname.replace(/\/+$/, '') === '/l2') {
    history.replaceState(null, '', `/l2/monitor/compute/estate/summary${PASS ? '?' + PASS : ''}`);
    R = parseRoute();
  }
};
landing();
const remember = () => { try { sessionStorage.setItem('l2.last', JSON.stringify({ view: R.view, object: R.object, window: R.window })); } catch (e) { /* per-viewer convenience only */ } };
const recall = () => { try { return JSON.parse(sessionStorage.getItem('l2.last') || 'null'); } catch (e) { return null; } };
function url(o = {}) {
  const x = { ...R, ...o };
  const keepWin = x.window && x.activity !== 'troubleshoot' ? `window=${x.window}` : '';
  const perfTab = x.activity === 'monitor' && x.pillar === 'performance';
  const clsTab = x.activity === 'monitor' && ['performance', 'capacity'].includes(x.pillar);
  const grp = x.group && perfTab ? `group=${enc(x.group)}` : '';
  const cls = x.cls && clsTab ? `class=${enc(x.cls)}` : '';
  // A selected time belongs to one object, window and class: changing any of them goes back to the worst time.
  const moved = ['activity', 'view', 'object', 'pillar', 'window', 'cls'].some(k => k in o && o[k] !== R[k]);
  const at = clsTab && ('at' in o ? o.at : moved ? '' : x.at);
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
    <nav class="utils" aria-label="Utilities">${e2TopMark()}${u('rules', 'Rules')}${u('calendar', 'Calendar')}</nav>`;
}

// ---------------------------------------------------------------- inventory tree (frame.md, Inventory tree)
const TREE_HIDDEN = new Set(['resource_pool', 'vm', 'guest_os', 'virtual_disk', 'vnic']);
// vCenter's own object icons, drawn small. Inventory shows what an object is, not how it is doing: no status dot here.
const IC = (d, extra = '') => `<svg class="ico" viewBox="0 0 16 16" width="16" height="16" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="1.2" stroke-linejoin="round" stroke-linecap="round">${d}${extra}</svg>`;
const ICONS = {
  estate: IC('<circle cx="8" cy="8" r="6"/><path d="M2 8h12M8 2c2 2 2 10 0 12M8 2c-2 2-2 10 0 12"/>'),
  region: IC('<path d="M1.5 4.5h4.5l1.5 1.5h7v7.5h-13z"/>'),
  location: IC('<path d="M2.5 14V6.5L8 3l5.5 3.5V14zM1.5 14h13"/><path d="M5.5 8.5h1.5M9 8.5h1.5M5.5 11h1.5M9 11h1.5"/>'),
  workload_domain: IC('<rect x="2" y="2" width="12" height="9" rx="1"/><path d="M5 14h6M8 11v3"/><path d="M5 6.5l1.2 1.2L9 5"/>'),
  vcf_instance: IC('<rect x="2" y="2" width="12" height="9" rx="1"/><path d="M5 14h6M8 11v3"/>'),
  cluster: IC('<rect x="2" y="2.5" width="12" height="3.5" rx=".6"/><rect x="2" y="7" width="12" height="3.5" rx=".6"/><path d="M4 4.3h1.5M4 8.8h1.5"/><path d="M1 12.5h14"/><path d="M3.5 12.5v1.5M8 12.5v1.5M12.5 12.5v1.5"/>'),
  host: IC('<rect x="2.5" y="2" width="11" height="12" rx="1"/><path d="M2.5 6h11M2.5 10h11M5 4h1.5M5 8h1.5M5 12h1.5"/><circle cx="11" cy="12" r=".5" fill="currentColor"/>'),
  resource_pool: IC('<circle cx="8" cy="8" r="6" stroke-dasharray="2 1.6"/><circle cx="8" cy="8" r="2.5"/>'),
  vm: IC('<path d="M8 1.8l5.5 3v6.4l-5.5 3-5.5-3V4.8z"/><path d="M2.7 4.9L8 8l5.3-3.1M8 8v6"/>'),
  guest_os: IC('<rect x="2" y="3" width="12" height="9" rx="1"/><path d="M4.5 6l2 1.6-2 1.6M8 9.5h3"/>'),
  datastore: IC('<ellipse cx="8" cy="4" rx="5.5" ry="2"/><path d="M2.5 4v8c0 1.1 2.5 2 5.5 2s5.5-.9 5.5-2V4M2.5 8c0 1.1 2.5 2 5.5 2s5.5-.9 5.5-2"/>'),
  virtual_disk: IC('<rect x="2" y="3" width="12" height="10" rx="1"/><circle cx="8" cy="8" r="2.5"/>'),
  distributed_switch: IC('<rect x="1.5" y="5" width="13" height="6" rx="1"/><path d="M4 8h.01M6.5 8h.01M9 8h.01M11.5 8h.01"/><path d="M4 5V3M12 5V3"/>'),
  port_group: IC('<circle cx="4" cy="8" r="1.6"/><circle cx="12" cy="4" r="1.6"/><circle cx="12" cy="12" r="1.6"/><path d="M5.5 7.3l5-2.6M5.5 8.7l5 2.6"/>'),
  vnic: IC('<rect x="2.5" y="4" width="11" height="7" rx="1"/><path d="M5 11v2M8 11v2M11 11v2M5 6.5v1.5M8 6.5v1.5M11 6.5v1.5"/>'),
  class_of_service: IC('<path d="M8 1.8l1.9 4 4.3.6-3.1 3 .8 4.3L8 11.6l-3.9 2.1.8-4.3-3.1-3 4.3-.6z"/>'),
  appliance: IC('<rect x="2" y="3" width="12" height="10" rx="1"/><path d="M5 6.5h6M5 9.5h3"/>'),
};
const icon = kind => `<span class="ic k-${esc(kind)}" title="${esc(KIND[kind] || kind)}">${ICONS[kind] || ICONS.vm}</span>`;
const treeQ = node => `view=${R.view}&node=${enc(node)}&activity=${['improve', 'troubleshoot'].includes(R.activity) ? R.activity : 'monitor'}&pillar=${R.pillar || 'summary'}&window=${R.window || '24h'}`;
function treeItems(rows, openPath, levels, selected) {
  return rows.map(r => {
    const open = openPath.includes(r.id) && levels[r.id];
    return `<li data-node="${esc(r.id)}"><div class="item"><button type="button" class="caret" aria-label="Expand ${esc(r.name)}" aria-expanded="${open ? 'true' : 'false'}"${r.expandable ? '' : ' hidden'}>${open ? '▾' : '▸'}</button>
      <a class="node" data-obj="${esc(r.id)}" href="${objURL(r.id)}"${r.id === selected ? ' aria-current="true"' : ''} title="${esc(r.name)}">${icon(r.kind)}<span class="nm">${esc(r.name)}</span>${r.open_cases ? `<span class="badge" title="Open cases">${r.open_cases}</span>` : ''}</a></div>
      ${open ? `<ul>${treeItems(levels[r.id], openPath, levels, selected)}</ul>` : ''}</li>`;
  }).join('');
}
const getTree = q => getJSON('tree', q, null);
let TREE = null; // { view, object, selected } of the tree now on screen
async function tree() {
  const box = document.getElementById('tree');
  const first = await getTree(treeQ(R.object));
  if (first.node.view !== R.view) R.view = first.node.view;
  const path = first.node.path.map(p => p.id);
  const visible = path.filter((id, i) => { const k = first.node.path[i].kind; return i === 0 || (!TREE_HIDDEN.has(k) || (R.view === 'management' && k === 'vm')) && !(R.view === 'compute' && k === 'vcf_instance'); });
  const selected = visible[visible.length - 1];
  const levels = {};
  const ids = visible.filter(id => id !== R.object);
  const got = await Promise.all(ids.map(id => getTree(treeQ(id)).catch(() => null)));
  ids.forEach((id, i) => { if (got[i]) levels[id] = got[i].children; });
  if (!TREE_HIDDEN.has(first.node.kind) || R.object === 'estate') levels[R.object] = first.children;
  const root = levels.estate || [];
  box.innerHTML = `<label for="view">View</label><select id="view">${first.views.map(v => `<option value="${v.id}"${v.id === R.view ? ' selected' : ''}>${esc(v.name)}</option>`).join('')}</select>
    <label for="find">Search</label><input id="find" type="text" placeholder="Name of any object" autocomplete="off"><ul class="results" id="results"></ul>
    <ul><li data-node="estate"><div class="item"><span class="caret" hidden></span><a class="node" data-obj="estate" href="${objURL('estate')}"${selected === 'estate' ? ' aria-current="true"' : ''}>${icon('estate')}<span class="nm">ACME estate</span>${first.open_cases && R.object === 'estate' ? `<span class="badge">${first.open_cases}</span>` : ''}</a></div>
    <ul>${treeItems(root, visible, levels, selected)}</ul></li></ul>`;
  TREE = { view: R.view, object: R.object, selected };
  document.getElementById('view').addEventListener('change', e => { go(url({ view: e.target.value, object: 'estate', caseId: undefined, newComplaint: undefined, activity: ['monitor', 'improve', 'troubleshoot'].includes(R.activity) ? R.activity : 'monitor', pillar: R.pillar || 'summary' })); });
  let t;
  document.getElementById('find').addEventListener('input', e => {
    clearTimeout(t);
    t = setTimeout(async () => {
      const res = await getJSON('search', `q=${enc(e.target.value)}`).catch(() => []);
      document.getElementById('results').innerHTML = res.map(x => `<li><a data-obj="${esc(x.id)}" data-view="${esc(x.view)}" href="${objURL(x.id, x.view)}">${esc(x.name)} <span class="muted">${esc(KIND[x.kind] || x.kind)}${x.path.length ? ' · ' + esc(x.path.slice(-2).join(' › ')) : ''}</span></a></li>`).join('');
    }, 200);
  });
  return first;
}
// The tree is built once. A click on a caret opens a level; a click on a node is a navigation (below). Wired once, not on every rebuild.
document.getElementById('tree').addEventListener('click', async e => {
  const b = e.target.closest('button.caret');
  if (!b) return;
  const li = b.closest('li');
  const sub = li.querySelector(':scope > ul');
  if (sub) { sub.remove(); b.textContent = '▸'; b.setAttribute('aria-expanded', 'false'); return; }
  const d = await getTree(treeQ(li.dataset.node));
  li.insertAdjacentHTML('beforeend', `<ul>${treeItems(d.children, [], {}, TREE && TREE.selected)}</ul>`);
  b.textContent = '▾'; b.setAttribute('aria-expanded', 'true');
});
// After a navigation the tree is kept: only the highlight moves and the links read the new pillar and window. It is rebuilt only when the object is not on it.
async function syncTree() {
  const box = document.getElementById('tree');
  if (!TREE || TREE.view !== R.view) { await tree(); return; }
  if (TREE.object !== R.object) {
    const sel = [...box.querySelectorAll('a.node[data-obj]')].find(a => a.dataset.obj === R.object);
    if (!sel) { await tree(); return; }
    box.querySelectorAll('a.node[aria-current]').forEach(a => a.removeAttribute('aria-current'));
    sel.setAttribute('aria-current', 'true'); TREE.object = R.object; TREE.selected = R.object;
  }
  box.querySelectorAll('a.node[data-obj]').forEach(a => { a.href = objURL(a.dataset.obj); });
}

// ---------------------------------------------------------------- shared pieces
const KIND_ICON_HEAD = ['cluster', 'host', 'vm'];
function objHead(o, windowFixed) {
  const crumbs = o.path.slice(0, -1).map(p => `<a href="${objURL(p.id, o.view)}">${esc(p.name)}</a>`).join(' › ');
  const cur = WINDOWS.find(([w]) => w === R.window) || WINDOWS[1];
  const win = windowFixed ? `<div class="windows fixed">${esc(windowFixed)}</div>`
    : `<div class="winpick"><button type="button" class="winbtn" id="winbtn" aria-haspopup="listbox" aria-expanded="false" aria-controls="winlist" aria-label="Time window: ${esc(cur[1])}"><span class="lbl">${esc(cur[1])}</span><span class="car" aria-hidden="true">▾</span></button>
      <ul class="winlist" id="winlist" role="listbox" aria-label="Time window" hidden>${WINDOWS.map(([w, l]) => `<li role="none"><a role="option" tabindex="-1" href="${url({ window: w })}" data-w="${w}" aria-selected="${w === cur[0]}">${l}</a></li>`).join('')}</ul></div>`;
  const kindName = esc(KIND[o.kind] || o.kind);
  // Cluster, ESXi host, VM: an icon beside the name names the type on hover or focus, no type line (frame.md, Object header).
  const title = KIND_ICON_HEAD.includes(o.kind)
    ? `<div class="objname" data-kind="${kindName}" data-tip="${kindName}" tabindex="0"><span class="ic k-${esc(o.kind)}" role="img" aria-label="${kindName}">${ICONS[o.kind]}</span><h1>${esc(o.name)}</h1></div>`
    : `<div class="kind">${kindName}</div><h1>${esc(o.name)}</h1>`;
  return `<div class="objhead"><div><div class="crumbs">${crumbs || '&nbsp;'}</div>${title}</div>${win}</div>`;
}
const CONSUMER_KINDS = ['vm', 'guest_os', 'virtual_disk', 'vnic'];
// The tabs are the titles of the panel under them: the selected tab and the panel are one shape (frame.md, Tabs).
function tabbed(statuses, kind, inner) {
  const list = PILLARS.filter(p => !(p === 'inventory' && CONSUMER_KINDS.includes(kind)));
  return `<div class="tabbed"><nav class="tabs" role="tablist" aria-label="Pillars">${['summary', ...list].map(p => { const on = p === R.pillar;
    return `<a role="tab" id="tab-${p}" data-pillar="${p}" href="${url({ pillar: p })}" aria-selected="${on}" aria-controls="panel" tabindex="${on ? 0 : -1}">${PNAME[p]}</a>`; }).join('')}</nav>
    <section class="tabpanel" id="panel" role="tabpanel" aria-labelledby="tab-${R.pillar}" tabindex="-1">${inner}</section></div>`;
}
// Tabs carry no status dot: one dot cannot summarise a pillar. One read of the Summary per object and window, kept until something is written.
async function pillarStatuses(first) {
  if (first) { const k = `${R.view}|${R.object}|${R.window}|${PASS}`; STATUS_CACHE.set(k, first); return first; }
  const k = `${R.view}|${R.object}|${R.window}|${PASS}`;
  if (STATUS_CACHE.has(k)) return STATUS_CACHE.get(k);
  const d = await getJSON(`monitor/${R.view}/${enc(R.object)}/summary`, `window=${R.window}`);
  const st = Object.fromEntries(d.pillars.map(p => [p.pillar, p.status]));
  STATUS_CACHE.set(k, st); return st;
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
    <div class="acts">${go}</div></div>${e2mark({ kind: 'finding', finding: f.id }, 'this finding', { name: f.object_name })}</div>`;
}
function wireFindings(reload) {
  main.querySelectorAll('[data-approve]').forEach(b => b.addEventListener('click', async () => { await postJSON(`proposals/${b.dataset.approve}/approve`); reload('Approved.'); }));
  main.querySelectorAll('[data-reject]').forEach(b => b.addEventListener('click', async () => {
    const reason = prompt('Why reject? The reason tells L2 which rule is wrong.');
    const r = await postJSON(`proposals/${b.dataset.reject}/reject`, { reason }); reload(r.status === 200 ? 'Rejected, with the reason recorded.' : r.body.error);
  }));
  main.querySelectorAll('[data-trouble]').forEach(b => b.addEventListener('click', async () => {
    const r = await postJSON('cases', { trigger: 'finding', finding: b.dataset.trouble });
    if (r.status === 200) go(url({ activity: 'troubleshoot', caseId: r.body.id })); else reload(r.body.error);
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
    pillarStatuses(st);
    main.innerHTML = objHead(d.object) + tabbed(st, d.object.kind, `<div class="msg" role="status">${esc(msg)}</div>
      ${d.stale ? '<p class="why">No data from this location\'s VCF Operations. Shown grey, never green.</p>' : ''}
      <table class="data pillars"><thead><tr><th>Status</th><th>Pillar</th><th>Now</th><th class="num">Findings</th></tr></thead><tbody>${rows}</tbody></table>
      <h2>Findings, worst first</h2>${d.findings.length ? d.findings.map(findingRow).join('') : '<p>Nothing needs you under this object.</p>'}
      ${d.slipped_alerts.length ? `<h2>Alerts that slipped through</h2><ul>${d.slipped_alerts.map(s => `<li>${esc(s.object)}: ${esc(s.title)}, ${fmtTime(s.raised)}. No finding predicted it. ${esc(s.would_have_caught_it || '')} <a class="link" href="${url({ activity: 'rules' })}">Change the check rule</a></li>`).join('')}</ul>` : ''}
      ${year}`);
    wireFindings(monitor);
    return;
  }
  const [d, st] = await Promise.all([getJSON(`monitor/${R.view}/${enc(R.object)}/${R.pillar}`, qjoin(`window=${R.window}`, R.group ? `group_by=${R.group}` : '',
    ['performance', 'capacity'].includes(R.pillar) && R.cls ? `class=${enc(R.cls)}` : '', ['performance', 'capacity'].includes(R.pillar) && R.at ? `at=${enc(R.at)}` : '')), pillarStatuses().catch(() => ({}))]);
  const head = `<div class="msg" role="status">${esc(msg)}</div>`;
  const c = d.content;
  let body = '';
  if (R.pillar === 'performance' && d.perf) {
    body += perfTab(d.perf, d);
  } else if (R.pillar === 'performance' && d.layers) {
    body += layersView(d) + `<p><a class="link" href="${complaintURL(R.object)}">Log a complaint about this VM</a></p>` + childrenTable(d);
  } else if (R.pillar === 'performance') {
    body += objectKpis(d);
    body += groupBy(d);
    body += childrenTable(d);
  } else if (R.pillar === 'availability') {
    body += `<p>${esc(c.headline)}</p>${c.events.length ? `<table class="data"><thead><tr><th>When</th><th>Object</th><th>What</th><th>Counted</th></tr></thead><tbody>${c.events.map(e => `<tr><td>${fmtTime(e.at)}</td><td>${objLink(e.object)}</td><td>${esc(e.text)}</td><td>${e.counted ? '<span class="chip amber">Counted</span>' : '<span class="chip green">Not counted</span>'}</td></tr>`).join('')}</tbody></table>` : ''}
      <p class="muted">Hosts not connected: ${c.hosts_not_connected}. HA restarts: ${c.ha_restarts}.</p>` + childrenTable(d);
  } else if (R.pillar === 'capacity') {
    body += capacityTab(d.capacity, d);
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
  // Outside the 24-hour window a closed cluster's finding is the daily one: no repeat, a link to it (monitor.md, Capacity findings).
  const capClosed = R.pillar === 'capacity' && d.capacity ? (d.capacity.kind === 'cluster' ? (d.capacity.check && d.capacity.check.state === 'closed' ? [d.capacity.cluster] : [])
    : d.capacity.kind === 'group' ? d.capacity.closed.now_clusters : []) : [];
  const dailyLink = !['24h', '1h'].includes(R.window) && capClosed.length ? `<p data-daily-finding>${capClosed.map(x => esc(x)).join(', ')} closed for new VMs at the latest check: a finding of the daily check. <a class="link" href="${url({ window: '24h' })}">See it in the last 24 hours</a></p>` : '';
  const contentionShown = R.pillar === 'capacity' && d.capacity && (d.capacity.contention_now || (d.capacity.clusters_at || []).some(r => r.contention_now));
  body += `<h2>Findings: ${PNAME[R.pillar]}</h2>${dailyLink}${d.findings.length ? d.findings.map(findingRow).join('') : dailyLink ? '' : contentionShown
    ? `<p class="muted">No capacity finding. The contention now is a performance problem: see the <a class="link" href="${url({ pillar: 'performance', cls: undefined })}">Performance tab</a> and the NOC's incident.</p>`
    : '<p class="muted">Nothing needs you under this object.</p>'}`;
  main.innerHTML = objHead(d.object) + tabbed({ ...st, [R.pillar]: d.status }, d.object.kind, head + (d.stale ? '<p class="why">No data from this location\'s VCF Operations. Shown grey, never green.</p>' : '') + body);
  const g = document.getElementById('grp');
  if (g) g.addEventListener('change', () => go(url({ group: g.value })));
  if (d.perf || d.layers || d.kpis || d.capacity) wireCharts();
  main.querySelectorAll('[data-why-toggle]').forEach(b => b.addEventListener('click', () => {
    const open = b.getAttribute('aria-expanded') !== 'true';
    b.setAttribute('aria-expanded', String(open)); document.getElementById(b.getAttribute('aria-controls')).hidden = !open;
  }));
  main.querySelectorAll('form.expect').forEach(fm => fm.addEventListener('submit', async e => {
    e.preventDefault();
    const r = await postJSON(`inventory/${fm.dataset.c}/expected`, Object.fromEntries(new FormData(fm)));
    await monitor(r.status === 200 ? 'Recorded as expected.' : r.body.error); document.body.dataset.expected = String(r.status);
  }));
  wireFindings(monitor);
}
// ---------------------------------------------------------------- Performance above the cluster: VM, then Cluster (monitor.md)
const CLASS_NAME = { gold: 'Gold', silver: 'Silver', bronze: 'Bronze', all: 'All classes' };
const perfBand = v => v == null ? 'no_data' : v >= 75 ? 'green' : v >= 50 ? 'yellow' : v >= 25 ? 'orange' : 'red';
const riskBand = v => v == null ? 'no_data' : perfBand(100 - v);
const statusOfBand = b => ({ green: 'green', yellow: 'amber', orange: 'red', red: 'red' }[b] || 'no_data');
const fmtPoint = (iso, minutes) => new Date(iso).toLocaleString('en-GB', minutes >= 1440 ? { day: 'numeric', month: 'short' } : { day: 'numeric', month: 'short', hour: '2-digit', minute: '2-digit' });
// Axis times people say aloud: "2 pm", "6 pm", "19 Oct". Ticks sit on round hours or days, never on 2:10.
const clock = d => `${d.getHours() % 12 || 12}${d.getMinutes() ? ':' + String(d.getMinutes()).padStart(2, '0') : ''} ${d.getHours() < 12 ? 'am' : 'pm'}`;
const dayName = d => d.toLocaleString('en-GB', { day: 'numeric', month: 'short' });
const humanPoint = (iso, minutes) => { const d = new Date(iso); return minutes >= 1440 ? dayName(d) : `${dayName(d)}, ${clock(d)}`; };
function niceTicks(t0, tn, max) {
  const MIN = 60000, H = 3600000, D = 86400000, span = tn - t0;
  const steps = span > 2 * D ? [D, 2 * D, 3 * D, 7 * D, 14 * D, 30 * D] : [5 * MIN, 10 * MIN, 15 * MIN, 30 * MIN, H, 2 * H, 3 * H, 4 * H, 6 * H, 12 * H];
  const step = steps.find(x => span / x <= max) || steps[steps.length - 1];
  const d = new Date(t0), out = [];
  if (step >= D) { d.setHours(0, 0, 0, 0); if (d.getTime() < t0) d.setDate(d.getDate() + 1); }
  else if (step >= H) { d.setMinutes(0, 0, 0); while (d.getTime() < t0 || d.getHours() % (step / H)) d.setHours(d.getHours() + 1); }
  else { d.setSeconds(0, 0); while (d.getTime() < t0 || d.getMinutes() % (step / MIN)) d.setMinutes(d.getMinutes() + 1); }
  while (d.getTime() <= tn && out.length < 40) {
    out.push({ t: d.getTime(), label: step >= D || (!d.getHours() && !d.getMinutes()) ? dayName(d) : clock(d) });
    if (step >= D) d.setDate(d.getDate() + step / D); else if (step >= H) d.setHours(d.getHours() + step / H); else d.setMinutes(d.getMinutes() + step / MIN);
  }
  return out;
}
const fmtDur = m => m >= 60 ? `${Math.floor(m / 60)} h${m % 60 ? ` ${m % 60} min` : ''}` : `${m} min`;
const CHARTS = {};

// One chart, one axis. series: [{ key, label, dash, color (fixed) or band (function of value) }].
// The SVG is drawn at the width it is shown at, so a 12px label is 12px on screen whatever the column width.
const seriesColor = (s, v) => s.band ? `var(--band-${s.band(v)})` : s.color;
function chartSvg(id, W) {
  const { pts, series, o } = CHARTS[id];
  const H = o.height ?? 240, L = o.left ?? 56, Rt = (o.nodirect || o.bands) ? 16 : 140, T = 12, B = 32, iw = W - L - Rt, ih = H - T - B, n = pts.length;
  const fmt = o.fmt || ((v) => o.max === 100 ? v + '%' : n0(v));
  const max = o.max ?? Math.max(4, ...pts.flatMap(p => series.map(s => p[s.key] ?? 0))) * 1.1;
  // o.edges: five ascending values, the foot of the axis, the three band limits and the top. Each band gets a quarter of the
  // height, so green, yellow, orange and red are as tall on every chart; inside a band the scale is linear. A value past the ends sits on them.
  const E = o.edges, quarter = ih / 4;
  const yEdge = v => { const c = Math.min(Math.max(v, E[0]), E[4]); let k = 0; while (k < 3 && c > E[k + 1]) k++; return T + ih - (k + (E[k + 1] === E[k] ? 0 : (c - E[k]) / (E[k + 1] - E[k]))) * quarter; };
  const x = i => L + (n === 1 ? iw / 2 : i / (n - 1) * iw), y = E ? yEdge : v => T + ih - v / max * ih;
  const ticks = E ? E : o.ticks ?? (o.max === 100 ? [0, 25, 50, 75, 100] : [0, Math.round(max / 2), Math.round(max)]);
  const t0 = new Date(pts[0].t).getTime(), tn = new Date(pts[n - 1].t).getTime();
  const xt = niceTicks(t0, tn, Math.max(3, Math.floor(iw / 85))), xAt = t => L + (tn === t0 ? iw / 2 : (t - t0) / (tn - t0) * iw);
  CHARTS[id].g = { x, y, L, T, iw, ih };
  const f = v => v.toFixed(1);
  let svg = `<svg class="lc" viewBox="0 0 ${W} ${H}" width="${W}" height="${H}" role="img" aria-label="${esc(o.label)}" data-chart="${id}">`;
  const area = series.filter(s => !s.dash && !s.band);
  if (area.length) svg += `<defs><linearGradient id="fg-${id}" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#fff" stop-opacity=".9"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient>
    <mask id="fm-${id}" maskUnits="userSpaceOnUse" x="${L}" y="${T}" width="${iw}" height="${ih}"><rect x="${L}" y="${T}" width="${iw}" height="${ih}" fill="url(#fg-${id})"/></mask></defs>`;
  // The four bands are tinted zones behind the line, so no band names are written on the chart.
  if (E) svg += `<g class="zones">${o.edgeBands.map((b, k) => `<rect x="${L}" y="${f(T + ih - (k + 1) * quarter)}" width="${iw}" height="${f(quarter)}" fill="var(--band-${b})"/>`).join('')}</g>`;
  else if (o.bands) svg += `<g class="zones">${o.bands.map(([lo, hi, b]) => `<rect x="${L}" y="${f(y(hi))}" width="${iw}" height="${f(y(lo) - y(hi))}" fill="var(--band-${b})"/>`).join('')}</g>`;
  svg += xt.map(k => `<line class="vgrid" x1="${f(xAt(k.t))}" x2="${f(xAt(k.t))}" y1="${T}" y2="${T + ih}"/>`).join('');
  svg += ticks.map(v => `<line class="grid" x1="${L}" x2="${W - Rt}" y1="${f(y(v))}" y2="${f(y(v))}"/><line class="tick" x1="${L - 5}" x2="${L}" y1="${f(y(v))}" y2="${f(y(v))}"/><text class="axis" x="${L - 10}" y="${f(y(v) + 4)}" text-anchor="end">${fmt(v, true)}</text>`).join('');
  svg += `<line class="axisline" x1="${L}" x2="${L}" y1="${T}" y2="${T + ih}"/><line class="axisline" x1="${L}" x2="${W - Rt}" y1="${T + ih}" y2="${T + ih}"/>`;
  svg += xt.map(k => `<line class="tick" x1="${f(xAt(k.t))}" x2="${f(xAt(k.t))}" y1="${T + ih}" y2="${T + ih + 5}"/><text class="axis" x="${f(xAt(k.t))}" y="${H - 6}" text-anchor="middle">${esc(k.label)}</text>`).join('');
  const base = y(0);
  for (const s of series) {
    // Each point holds the worst value inside its interval, so the line steps: flat across the interval, then a rise or fall.
    let line = '', fill = '', path = '', open = false;
    for (let i = 1; i < n; i++) {
      const a = pts[i - 1][s.key], b = pts[i][s.key];
      if (a == null) { open = false; continue; }
      const xa = x(i - 1), xb = x(i), ya = y(a);
      if (s.band) {
        line += `<line x1="${f(xa)}" y1="${f(ya)}" x2="${f(xb)}" y2="${f(ya)}" stroke="${seriesColor(s, a)}"/>`;
        if (b != null) line += `<line x1="${f(xb)}" y1="${f(ya)}" x2="${f(xb)}" y2="${f(y(b))}" stroke="${seriesColor(s, s.worse(a, b))}"/>`;
      } else {
        path += `${open ? '' : `M${f(xa)} ${f(ya)}`}H${f(xb)}${b != null ? `V${f(y(b))}` : ''}`;
        if (b == null) open = false; else open = true;
      }
    }
    if (!s.band) {
      line = `<path d="${path}" fill="none" stroke="${s.color}"/>`;
      if (!s.dash) {
        let d = '', run = null;
        for (let i = 0; i <= n; i++) {
          const v = i < n ? pts[i][s.key] : null;
          if (v != null && run == null) { run = i; d += `M${f(x(i))} ${f(base)}`; }
          if (v != null) { d += `V${f(y(v))}`; if (i + 1 < n && pts[i + 1][s.key] != null) d += `H${f(x(i + 1))}`; }
          if ((v == null || i === n - 1) && run != null) { d += `V${f(base)}Z`; run = null; }
        }
        fill = `<path d="${d}" fill="${s.color}" stroke="none"/>`;
      }
    }
    if (fill) svg += `<g class="area" mask="url(#fm-${id})">${fill}</g>`;
    svg += `<g class="series${s.dash ? ' dashed' : ''}" data-series="${s.key}">${line}</g>`;
  }
  // Direct labels at the right end, pushed apart when the lines end close together.
  for (const r of o.refs || []) svg += `<line class="ref" x1="${L}" x2="${W - Rt}" y1="${f(y(r.value))}" y2="${f(y(r.value))}"/>`;
  const ends = series.map(s => ({ s, v: pts[n - 1][s.key] })).filter(e => e.v != null).map(e => ({ ...e, y: y(e.v) + 4 })).sort((a, b) => a.y - b.y);
  for (let i = 1; i < ends.length; i++) if (ends[i].y - ends[i - 1].y < 15) ends[i].y = ends[i - 1].y + 15;
  if (!o.nodirect && !o.bands) svg += ends.map(e => `<text class="direct" x="${W - Rt + 8}" y="${f(e.y)}">${esc(e.s.short)}</text>`).join('');
  if (o.selected != null) svg += `<line class="sel" x1="${f(x(o.selected))}" x2="${f(x(o.selected))}" y1="${T}" y2="${T + ih}"/>`;
  svg += `<line class="cross" x1="0" x2="0" y1="${T}" y2="${T + ih}" visibility="hidden"/><g class="dots">${series.map(() => '<circle r="4" visibility="hidden"/>').join('')}</g><rect class="hit" x="${L}" y="${T}" width="${iw}" height="${ih}"/></svg>`;
  return svg;
}
function lineChart(id, pts, series, o) {
  CHARTS[id] = { pts, series, o };
  const swatch = (c, dash) => `<svg width="18" height="8" aria-hidden="true"><line x1="1" x2="17" y1="4" y2="4" stroke="${c}" stroke-width="2" stroke-linecap="round"${dash ? ' stroke-dasharray="4 4"' : ''}/></svg>`;
  const legend = `<div class="legend">${series.map(s => `<span>${swatch(s.color || 'var(--text-muted)', s.dash)}${esc(s.label)}</span>`).join('')}
    ${(o.refs || []).map(r => `<span><svg width="18" height="8" aria-hidden="true"><line x1="1" x2="17" y1="4" y2="4" stroke="var(--text-muted)" stroke-width="1.5" stroke-dasharray="2 3"/></svg>${esc(r.label)}</span>`).join('')}
    ${o.bands ? `<span class="muted">Line color is the band of the value.</span>` : ''}${o.noclick ? '' : '<span class="muted">Click a time to see it below.</span>'}</div>`;
  return `<div class="chart" data-chartbox="${id}">${o.nolegend ? '' : legend}<div class="plot">${chartSvg(id, o.width ?? 1000)}<div class="tip" hidden></div></div></div>`;
}
function mountChart(box) {
  const id = box.dataset.chartbox, C = CHARTS[id], { pts, series, o } = C, plot = box.querySelector('.plot'), tip = box.querySelector('.tip');
  const W = Math.max(300, Math.round(plot.clientWidth) || (o.width ?? 1000));
  plot.querySelector('svg.lc').outerHTML = chartSvg(id, W);
  const svg = plot.querySelector('svg.lc'), hit = svg.querySelector('rect.hit'), cross = svg.querySelector('line.cross'), dots = [...svg.querySelectorAll('.dots circle')];
  const { x, y } = C.g, vf = o.fmt || (v => o.max === 100 ? v + '%' : v);
  const idx = ev => { const r = hit.getBoundingClientRect(); return Math.max(0, Math.min(pts.length - 1, Math.round((ev.clientX - r.left) / r.width * (pts.length - 1)))); };
  hit.addEventListener('mousemove', ev => {
    const i = idx(ev), sr = svg.getBoundingClientRect(), xv = x(i);
    cross.setAttribute('x1', xv); cross.setAttribute('x2', xv); cross.setAttribute('visibility', 'visible');
    series.forEach((s, k) => { const v = pts[i][s.key]; if (v == null) return dots[k].setAttribute('visibility', 'hidden'); dots[k].setAttribute('cx', xv); dots[k].setAttribute('cy', y(v)); dots[k].setAttribute('stroke', seriesColor(s, v)); dots[k].setAttribute('visibility', 'visible'); });
    tip.innerHTML = `<div class="when">${esc(humanPoint(pts[i].t, o.minutes))}</div>${series.map(s => { const v = pts[i][s.key]; return `<div class="row"><i style="background:${v == null ? 'var(--text-muted)' : seriesColor(s, v)}"></i><span>${esc(s.label)}</span><strong>${v == null ? '–' : vf(v)}</strong>${s.who && pts[i][s.who] ? `<span class="who">${esc(pts[i][s.who])}</span>` : ''}</div>`; }).join('')}`;
    tip.hidden = false;
    const left = ev.clientX - sr.left + 14;
    tip.style.left = `${left + tip.offsetWidth > sr.width ? Math.max(0, ev.clientX - sr.left - tip.offsetWidth - 14) : left}px`; tip.style.top = `${Math.max(0, ev.clientY - sr.top - tip.offsetHeight - 10)}px`;
  });
  hit.addEventListener('mouseleave', () => { cross.setAttribute('visibility', 'hidden'); dots.forEach(d => d.setAttribute('visibility', 'hidden')); tip.hidden = true; });
  if (!o.noclick) hit.addEventListener('click', ev => go(url({ at: pts[idx(ev)].t })));
}
let chartResize = null;
function wireCharts() {
  const all = () => main.querySelectorAll('[data-chartbox]');
  main.querySelectorAll('details.kpi-details').forEach(el => el.addEventListener('toggle', () => {
    el.open ? OPEN_DETAILS.add(el.dataset.detailsId) : OPEN_DETAILS.delete(el.dataset.detailsId);
    if (el.open) el.querySelectorAll('[data-chartbox]').forEach(b => mountChart(b));  // a chart in a closed fold has no width
  }));
  all().forEach(mountChart);
  if (chartResize) return;
  let last = window.innerWidth, timer;
  chartResize = () => { if (window.innerWidth === last) return; last = window.innerWidth; clearTimeout(timer); timer = setTimeout(() => all().forEach(b => { if (CHARTS[b.dataset.chartbox]) mountChart(b); }), 120); };
  window.addEventListener('resize', chartResize);
}
function groupBy(d, note = '') {
  let h = `<div class="toolbar"><label for="grp">Group by</label><select id="grp">${GROUP_BY.map(([k, l]) => `<option value="${k}"${k === R.group ? ' selected' : ''}>${l}</option>`).join('')}</select>${note}</div>`;
  if (d.group_by) {
      h += `<table class="data" data-groupby="${d.group_by.attribute}"><thead><tr><th>${esc(GROUP_BY.find(g => g[0] === d.group_by.attribute)[1])}</th>${d.group_by.rows[0] && 'hosts' in d.group_by.rows[0] ? '<th class="num">Hosts</th>' : ''}<th class="num">VMs</th><th class="num">Below green</th><th class="num">Just above the line</th><th class="num">Wider than their host's NUMA node</th><th class="num">Worst</th><th>Status</th></tr></thead><tbody>
        ${d.group_by.rows.map(r => `<tr data-group="${esc(r.value)}"><td>${esc(r.value)}</td>${'hosts' in r ? `<td class="num">${n0(r.hosts)}</td>` : ''}<td class="num">${n0(r.vms)}</td><td class="num">${n0(r.below_green)}</td><td class="num">${n0(r.near_line)}</td><td class="num">${n0(r.wider_than_numa_node)}</td><td class="num">${r.worst}</td><td>${chip(r.status)}</td></tr>`).join('')}</tbody></table>`;
    }
  return h;
}
// ---------------------------------------------------------------- a VM's two layers (monitor.md, Performance tab on a VM; l2.realms)
// The unit follows the number: the data carries it with its own space (" ms", "%", "/s"). The name never holds it.
const niceMax = v => { if (!(v > 0)) return 1; const p = 10 ** Math.floor(Math.log10(v)), f = v / p; return (f <= 1 ? 1 : f <= 2 ? 2 : f <= 5 ? 5 : 10) * p; };
// A percentage above 0 that shows as 0 is not exactly 0: it shows 0.0+% (0.00+% at two decimals), never a plain 0%.
const tinyPct = decimals => `0.${'0'.repeat(decimals)}+%`;
const withUnit = (v, m, tick) => {
  if (v == null) return '–';
  if (!tick && m.whole && m.unit === '%') return pct(v);  // whole percent (D-101, D-116); pct() is defined with the Capacity tab
  if (!tick && m.unit === '%' && m.decimals > 0 && Number(v) > 0 && Number(v).toFixed(m.decimals) === (0).toFixed(m.decimals)) return tinyPct(m.decimals);
  return `${Number(v).toLocaleString('en-US', tick ? { maximumFractionDigits: 2 } : { minimumFractionDigits: m.decimals, maximumFractionDigits: m.decimals })}${tick && m.unit !== '%' ? '' : m.unit}`;
};
// In the figures on the left a unit that is words ("per vCPU", "ms") is set small and light, so every metric reads alike.
const figure = (v, m) => { if (v == null) return '–'; const t = withUnit(v, m); return m.unit && m.unit !== '%' && t.endsWith(m.unit) ? `${esc(t.slice(0, -m.unit.length))}<span class="u">${esc(m.unit)}</span>` : esc(t); };
// A figure with bands carries the band of its value: a tinted pill with dark text (6.2:1 or better) and a bar in the band
// color. The band's name is not written: the color already says it (tokens.md, Band figures; D-100, D-104).
// A KPI on the 0 to 100% scale uses the SP5 bands; a metric with band_ends (upper end of green, yellow, orange) uses those. A value on an end stays in the lower band.
// A higher-is-better counter (Free Memory) has lower limits: green from the first end up, then yellow, orange, red below the last.
const endBand = (v, ends, better) => v == null ? 'no_data' : ['green', 'yellow', 'orange'].find((_, i) => better === 'higher' ? v >= ends[i] : v <= ends[i]) || 'red';
const bandOf = (v, m) => v == null ? null : m.band_ends ? endBand(v, m.band_ends, m.better) : !m.scale ? null : m.better === 'lower' ? riskBand(v) : perfBand(v);
const bandFig = (v, m, text) => { const b = bandOf(v, m); return b && b !== 'no_data' ? `<span class="bv ${b}" data-band="${b}">${text}</span>` : text; };
const LAYER_NOTE = { guest_os: 'Runs on top of the Virtual Motherboard.', virtual_motherboard: 'The VM\'s virtual hardware, under the Guest OS.' };
// Whole percent (D-101, D-116): a KPI, a part of Consumption on the Capacity tab, and a part under a cluster or ESXi KPI whose band ends are all whole
// numbers. A part with a fractional end (0.5%, 0.25%) keeps its decimals: they are the band's own scale. A VM's counters keep theirs.
const wholePct = (m, layer) => m.unit === '%' && (!!m.scale || layer === 'part' || (layer === 'object' && !!m.band_ends && m.band_ends.every(Number.isInteger)));
function metricBlock(m, layer, askKpi = false) {
  m = { ...m, whole: wholePct(m, layer) };
  const score = !!m.scale;
  const hiV = Math.max(...m.points.map(p => p.v));
  const top = score ? 100 : m.unit === '%' && hiV > 50 && hiV <= 100 ? 100 : niceMax(hiV * 1.1);  // a percentage near full reads on 0 to 100%, never 200%
  const fmt = (v, tick) => withUnit(v, m, tick);
  const hiw = m.better === 'lower';
  // A counter with band_ends is drawn like a KPI: tinted zones behind the line, the line in the band of its value (D-108).
  // The four bands are equally tall on every such chart (edges), whatever their width in the metric's own unit.
  const ends = !score && m.band_ends ? m.band_ends : null;
  let edges, edgeBands;
  if (ends) {
    const hiV2 = Math.max(0, hiV), given = m.band_top ?? (m.unit === '%' ? Math.min(100, 2 * ends[2] - ends[1]) : 2 * ends[2] - ends[1]);
    const lim = hiw ? Math.max(given, hiV2) : Math.max(given, niceMax(hiV2 * 1.1));
    edges = hiw ? [0, ends[0], ends[1], ends[2], lim] : [0, ends[2], ends[1], ends[0], lim];
    edgeBands = hiw ? ['green', 'yellow', 'orange', 'red'] : ['red', 'orange', 'yellow', 'green'];
  }
  const zones = ends ? edgeBands : undefined;
  const series = [score ? (hiw ? { key: 'v', label: 'Highest in each point', short: 'Highest', band: riskBand, worse: Math.max }
    : { key: 'v', label: 'Lowest in each point', short: 'Lowest', band: perfBand, worse: Math.min })
    : ends ? (hiw ? { key: 'v', label: 'Highest in each point', short: 'Highest', band: v => endBand(v, ends, m.better), worse: Math.max }
      : { key: 'v', label: 'Lowest in each point', short: 'Lowest', band: v => endBand(v, ends, m.better), worse: Math.min })
    : { key: 'v', label: 'Highest in each point', short: 'Highest', color: 'var(--series-1)' }];
  const chart = lineChart(`m-${layer}-${m.key}`, m.points, series, { label: `${m.label} over the window`, max: top, ticks: score ? [0, 25, 50, 75, 100] : [0, top / 2, top],
    fmt, width: 760, height: 160, left: 56, minutes: m.minutes, noclick: true, nodirect: true, nolegend: true, bands: score ? (hiw ? HIGH_BANDS : LOW_BANDS) : zones, edges, edgeBands });
  const show = { p95: fmt(m.percentile_95), worst: m.worst ? fmtPoint(m.worst.t, m.minutes) : '' };
  // A VM's layer metrics, and the KPIs at the top of a cluster's or an ESXi host's Performance tab (D-117), not their Details parts.
  const mark = E2_LAYERS.includes(layer) ? e2mark({ kind: 'metric', layer, metric: m.key, pillar: 'performance' }, m.label, show)
    : askKpi ? e2mark({ kind: 'kpi', metric: m.key, pillar: 'performance' }, m.label, show) : '';
  return `<div class="metric" data-metric="${m.key}"><div class="mname"><h4>${esc(m.label)}</h4>${mark}</div><div class="mfig">
    <dl><dt>Now</dt><dd>${bandFig(m.now, m, figure(m.now, m))}</dd><dt>Worst</dt><dd>${m.worst ? bandFig(m.worst.v, m, figure(m.worst.v, m)) : '–'}</dd><dt>95th percentile</dt><dd>${bandFig(m.percentile_95, m, figure(m.percentile_95, m))}</dd></dl></div>${chart}</div>`;
}
const pointsNote = minutes => `<p class="muted">${esc(WINDOWS.find(w => w[0] === R.window)[1])}, one point every ${fmtDur(minutes)}. Each point shows the worst value in that interval. 95% of points were better than the 95th percentile.</p>`;
// The Performance (%) KPIs come first: they say whether anything is wrong; the counters under them say where (D-100).
function layersView(d) {
  const kpis = d.layers.flatMap(l => l.metrics.filter(m => m.scale).map(m => metricBlock(m, l.key)));
  return pointsNote(d.layers[0].metrics[0].minutes)
    + `<section class="persp kpis" data-section="performance-kpis"><h2>Performance <span class="muted">0 to 100%, higher is better. The Guest OS runs on top of the Virtual Motherboard.</span></h2>${kpis.join('')}</section>`
    + d.layers.map(l => `<section class="persp layer" data-layer="${l.key}"><h2>${esc(l.title)} ${chip(l.status)} <span class="muted">${LAYER_NOTE[l.key]}</span>${e2mark({ kind: 'vm_layer', layer: l.key, pillar: 'performance' }, `the ${l.title} layer`, { name: `${l.title} layer`, layer: l.title })}</h2>${l.metrics.filter(m => !m.scale).map(m => metricBlock(m, l.key)).join('')}</section>`).join('');
}
// "Details" under a cluster KPI: the parts it is made of, one chart each (D-106). Closed by default: a good KPI needs no
// explanation. A fold the person opened stays open when the page redraws (window, time, tab back).
const OPEN_DETAILS = new Set();
function kpiDetails(k) {
  if (!k.details || !k.details.length) return '';
  const id = `${R.object}|${k.key}`;
  return `<details class="kpi-details" data-details="${k.key}"${OPEN_DETAILS.has(id) ? ' open' : ''} data-details-id="${esc(id)}"><summary>Details <span class="muted">What ${esc(k.label)} is made of. Lower is better for every part.</span></summary>
    ${k.details.map(p => metricBlock({ ...p, better: 'lower', scale: null }, 'object')).join('')}</details>`;
}
// A cluster and anything under it, but not a VM: its Performance KPI over the window first, then its children (D-100).
function objectKpis(d) {
  const win = esc(WINDOWS.find(w => w[0] === R.window)[1]).toLowerCase();
  const kpis = d.kpis && d.kpis.length
    ? pointsNote(d.kpis[0].minutes) + d.kpis.map(m => metricBlock(m, 'object', true) + kpiDetails(m)).join('')
    : '<p class="muted">No data for this object in the window.</p>';
  const outside = d.children_total ? `<p data-outside-green>${n0(d.outside_green)} of ${n0(d.children_total)} children outside green: over the ${win}, or in the last hour. They are first in the list below.</p>` : '';
  return `<section class="persp kpis" data-section="performance-kpis"><h2>Performance <span class="muted">0 to 100%</span></h2>${kpis}</section>${outside}`;
}
function perfTab(p, d) {
  const cls = CLASS_NAME[p.class], m = p.point_minutes, sel = p.selected, C = p.consumer, P = p.provider;
  const when = fmtPoint(sel.t, m);
  const filter = `<div class="toolbar"><span class="lbl">Class of service</span><nav class="windows" aria-label="Class of service">${p.classes.map(k => `<a href="${url({ cls: k })}" data-cls="${k}"${k === p.class ? ' aria-current="true"' : ''}>${CLASS_NAME[k]}</a>`).join('')}</nav>
    ${sel.default ? '' : `<a class="link" href="${url({ at: '' })}">Back to the worst time</a>`}</div>
    ${p.stale_locations.length ? `<p class="why">No data from ${esc(p.stale_locations.join(', '))}. Left out, never counted as green.</p>` : ''}`;
  // VM
  const vmRows = C.worst_vms.map(v => `<tr data-vm="${esc(v.vm)}"><td>${objLink(v.vm)}</td><td class="num">${v.vm_performance}</td><td>${chip(v.status)}</td><td>${esc(fmtPoint(v.at, 5))}</td><td>${objLink(v.cluster)}</td><td>${esc(v.location)}</td><td class="num">${n0(v.together)}</td></tr>`).join('');
  let vm = `<section class="persp" data-section="vm"><h2>VM <span class="muted">consumer</span></h2>
    <p>${C.vms ? `${n0(C.different)} different ${esc(cls)} VMs were below green in the window, of ${n0(C.vms)}. Never more than ${n0(C.most_at_once)} at once, at ${esc(fmtPoint(C.most_at, m))}.` : `No ${esc(cls)} VM under this object.`}
    ${C.vms ? ` ${n0(C.near_line)} sit just above the line (75 to 80) over the window.` : ''}</p>
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
    : `Lowest: ${low.worst}% at ${esc(fmtPoint(low.t, m))}, ${esc(low.worst_cluster)}; the ${P.percentile.performance}th percentile then ${low.percentile}%. The worst cluster was out of green for ${fmtDur(outW)}. ${outP ? `The ${P.percentile.performance}th percentile was out of green for ${fmtDur(outP)}: wide at those times.` : `The ${P.percentile.performance}th percentile stayed green: narrow, a few clusters or one.`}`;
  const rNow = P.risk[P.risk.length - 1];
  const riskLine = !P.clusters ? '' : `Highest now: ${rNow.worst}%, ${esc(rNow.worst_cluster)}. The ${P.percentile.risk}th percentile now: ${rNow.percentile}%.`;
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
// ---------------------------------------------------------------- the Capacity tab (monitor.md, Capacity tab; D-094, D-095)
// No forecast here: months ahead belong to the Capacity workspace (L2 design, 4.3.6).
const HIGH_BANDS = [[0, 25, 'green'], [25, 50, 'yellow'], [50, 75, 'orange'], [75, 100, 'red']];
const LOW_BANDS = [[75, 100, 'green'], [50, 75, 'yellow'], [25, 50, 'orange'], [0, 25, 'red']];
// Consumption, Performance and Risk show whole percent: the decimal is not significant. Tiny values show 0.0+%.
const pct = v => {
  if (v == null) return '–';
  const x = Number(v);
  return x > 0 && Math.round(x) === 0 ? tinyPct(1) : `${Math.round(x).toLocaleString('en-US')}%`;
};
const checkPeriod = c => `${c.period_hours} hours to ${fmtTime(c.window_end)}`;
const capGroupURL = (loc, cls) => `/capacity/group/${enc(loc.toUpperCase())}-${enc(cls.charAt(0).toUpperCase() + cls.slice(1))}${PASS ? '?' + PASS : ''}`;
const monthsAhead = href => `<p class="muted" data-months-ahead>To plan ahead and decide when to buy, open the <a class="link" href="${href}">Capacity workspace</a>.</p>`;
function kpiBlock(k, c, m) {
  const hiw = k.better === 'lower', km = { scale: [0, 100], better: k.better };
  const chart = lineChart(`cap-${k.key}`, k.points, [hiw ? { key: 'v', label: 'Highest in each point', short: 'Highest', band: riskBand, worse: Math.max }
    : { key: 'v', label: 'Lowest in each point', short: 'Lowest', band: perfBand, worse: Math.min }],
    { label: `${k.label} over the window, 0 to 100%`, max: 100, width: 760, height: 250, left: 56, minutes: m, noclick: true, nodirect: true, nolegend: true, bands: hiw ? HIGH_BANDS : LOW_BANDS });
  const mark = e2mark({ kind: 'kpi', metric: k.key, pillar: 'capacity' }, k.label, { p95: pct(k.percentile_95), worst: k.worst ? fmtPoint(k.worst.t, m) : '' });
  return `<div class="metric" data-kpi="${k.key}"><div class="mname"><h4>${esc(k.label)}</h4>${mark}</div><div class="mfig">
    <dl><dt>Now</dt><dd>${bandFig(k.now, km, pct(k.now))}</dd><dt>Worst</dt><dd>${k.worst ? bandFig(k.worst.v, km, pct(k.worst.v)) : '–'}</dd>
    <dt>95th percentile</dt><dd>${bandFig(k.percentile_95, km, pct(k.percentile_95))}</dd></dl></div>${chart}</div>`;
}
// Capacity Remaining, Time Remaining and VM Remaining are VCF Operations' own figures; PCM shows them, never computes them.
// Release 1.0 has no connector yet, so the values are placeholders, and the page says so (D-100).
const KIND_WORD = { vm: 'VM', host: 'ESXi host', cluster: 'cluster' };
function remainingSummary(r, kind) {
  if (!r) return '';
  const val = x => `${n0(x.value)}${x.unit === '%' ? '%' : `<span class="u">${esc(x.unit)}</span>`}`;
  return `<section class="persp" data-section="capacity-summary"><h2>Summary <span class="muted">this ${esc(KIND_WORD[kind] || kind)}</span></h2>
    <div class="cards remaining">${r.values.map(x => `<div class="card" data-remaining="${x.key}"><h3>${esc(x.label)}</h3><div class="big2">${val(x)}</div></div>`).join('')}</div>
    ${r.placeholder ? '' : `<p class="muted">From ${esc(r.source)}, ${esc(fmtTime(r.time))}.</p>`}</section>`;
}
// The Periodic Cluster Check as a diagram, with the check's own values (l2.cluster_check_diagram, D-121).
// Three paths to Closed, as vCommunity's capacity model draws them. Each node: the value, its closure level, the distance to it.
// PCM compares the published values with the published levels; it names the path, it never decides (D-094).
function checkDiagram(ck, kpis) {
  const lv = Object.fromEntries(kpis.map(k => [k.key, k.closure_levels]));
  const above = (v, l) => v != null && v > l, below = (v, l) => v != null && v < l;
  const gap = (v, l) => `${Math.abs(l - Math.round(v))} points`; // from the value as shown, so the sum reads right
  const node = (label, v, l, hi, on = true) => {
    const hit = on && (hi ? above(v, l) : below(v, l));
    const dist = v == null ? 'no data' : !on ? 'not checked' : hit ? `${hi ? 'above' : 'below'} by ${gap(v, l)}` : `${gap(v, l)} away`;
    return `<div class="cd-node ${!on ? 'off' : hit ? 'hit' : 'pass'}" data-cd-node="${label.toLowerCase()}"><b>${esc(label)}</b> <span class="cd-v">${pct(v)}</span>
      <span class="cd-l">${hi ? 'closes above' : 'closes below'} ${l}%</span><span class="cd-d">${hit ? '✕' : on && v != null ? '✓' : '–'} ${dist}</span></div>`;
  };
  const cR = lv.consumption.red, pR = lv.performance.red, cO = lv.consumption.orange, pO = lv.performance.orange, rO = lv.risk.orange;
  const cHit = above(ck.consumption, cR), pHit = below(ck.performance, pR);
  const cOr = above(ck.consumption, cO), pOr = below(ck.performance, pO), gate = cOr && pOr, rHit = gate && above(ck.risk, rO);
  const tick = ok => ok ? '✓' : '✕';
  const gateNode = `<div class="cd-node gate ${gate ? 'hit' : 'pass'}" data-cd-node="both"><b>Both orange?</b>
      <span class="cd-l">Consumption ${pct(ck.consumption)} above ${cO}% ${tick(cOr)}</span><span class="cd-l">Performance ${pct(ck.performance)} below ${pO}% ${tick(pOr)}</span>
      <span class="cd-d">${gate ? 'Yes: Risk decides' : 'No: Risk is not checked'}</span></div>`;
  const closed = ck.state === 'closed';
  const line = hit => `<div class="cd-line${hit ? ' hit' : ''}" aria-hidden="true"></div>`;
  return `<div class="cd" data-check-diagram role="group" aria-label="How the check decides: three ways to close">
    <div class="cd-paths">
      <div class="cd-row">${node('Consumption', ck.consumption, cR, true)}${line(cHit)}</div>
      <div class="cd-row">${node('Performance', ck.performance, pR, false)}${line(pHit)}</div>
      <div class="cd-row">${gateNode}<div class="cd-arrow${gate ? ' hit' : ''}" aria-hidden="true"></div>${node('Risk', ck.risk, rO, true, gate)}${line(rHit)}</div>
    </div>
    <div class="cd-out ${closed ? 'closed' : 'open'}" data-cd-out="${ck.state}">${closed ? 'Closed' : 'Open'}</div></div>`;
}
function capCluster(c, d) {
  if (!c.applies) return '<p class="muted">Capacity is tracked on workload clusters. Management and edge clusters run the platform\'s own appliances.</p>';
  const m = c.point_minutes, ck = c.check;
  const period = `the ${checkPeriod(ck)}`;
  const why = ck.state === 'closed' ? `${ck.reason} Based on ${period}.` : `Based on ${period}.`;
  const verdict = ck.state === 'no_check' ? `<span class="chip no_data">No check</span> <span class="muted">A metric has no data for ${esc(period)}.</span>`
    : `<button type="button" class="chip vbtn ${ck.state === 'closed' ? (ck.rule === 2 || ck.performance_red ? 'red' : 'amber') : 'green'}" data-why-toggle aria-expanded="${ck.state === 'closed'}" aria-controls="why-verdict">${ck.state === 'closed' ? 'Closed for new VMs' : 'Open for new VMs'}</button>${ck.state === 'closed' ? ` <span class="muted">since ${esc(fmtDay(ck.since))}</span>` : ''}`;
  const cn = c.contention_now ? ` <a class="chip ${perfBand(c.contention_now.value)}" data-contention-now href="${url({ pillar: 'performance', cls: undefined })}">Contention now</a> Cluster Performance ${pct(c.contention_now.value)} at ${esc(fmtTime(c.contention_now.t))}.` : '';
  const strip = c.strip_as_words
    ? `<p data-strip-words>Latest check, ${esc(checkPeriod(ck))}: ${ck.state === 'closed' ? 'Closed' : ck.state === 'open' ? 'Open' : 'No check'}. The check before, to ${esc(fmtTime(ck.previous.end))}: ${ck.previous.state === 'closed' ? 'Closed' : 'Open'}, Consumption ${pct(ck.previous.consumption)}, Performance ${pct(ck.previous.performance)}, Risk ${pct(ck.previous.risk)}.</p>`
    : `<div class="strip" data-strip role="img" aria-label="One cell per check: closed or open">${c.strip.map(x => `<span class="cell ${x.state}" title="Check to ${esc(fmtTime(x.end))}: ${x.state === 'closed' ? 'Closed' : x.state === 'open' ? 'Open' : 'No check'}">${x.state === 'closed' ? 'Closed' : ''}</span>`).join('')}</div>
      <div class="stripaxis muted"><span>${esc(fmtDay(c.strip[0].end))}</span><span>${esc(fmtDay(c.strip[c.strip.length - 1].end))}</span></div>`;
  const u = c.usable;
  const usable = `<table class="data" data-usable><thead><tr><th></th><th class="num">Total</th><th class="num">HA</th><th class="num">Buffer</th><th class="num">Usable</th></tr></thead><tbody>
    ${[['cpu', 'CPU'], ['memory', 'Memory']].map(([k, l]) => `<tr><td>${l} <span class="muted">${esc(u[k].unit)}</span></td><td class="num">${n0(u[k].total)}</td><td class="num">−${n0(u[k].ha)}</td><td class="num">−${n0(u[k].buffer)} <span class="muted">(${u[k].buffer_percent}%)</span></td><td class="num"><strong>${n0(u[k].usable)}</strong></td></tr>`).join('')}</tbody></table>
    <p class="muted">${u.running_hosts} of ${u.hosts} hosts running. The largest host is held back for HA. The Capacity team sets the buffer. The Capacity workspace plans on a bit less, because it also reserves a maintenance host.</p>`;
  const spreadChart = (key, label) => lineChart(`spread-${key}`, c.spread[key], [
    { key: 'highest', who: 'highest_host', label: 'Highest host', short: 'Highest', color: 'var(--series-1)' },
    { key: 'lowest', who: 'lowest_host', label: 'Lowest host', short: 'Lowest', color: 'var(--series-2)', dash: true }],
    { label: `${label}: highest and lowest host, % of each host's own capacity`, max: 100, width: 760, height: 170, left: 56, minutes: m, noclick: true });
  const hostRows = c.hosts.map(h => `<tr data-host="${esc(h.host)}"${h.marked ? ' class="marked" aria-current="true"' : ''}><td>${objLink(h.host)}${h.marked ? ' <span class="chip blue">This host</span>' : ''}</td>
    <td class="num">${pct(h.cpu_thread_utilization.percentile_95)}</td><td class="num">${pct(h.cpu_thread_utilization.worst.v)}</td>
    <td class="num">${pct(h.memory_consumed.percentile_95)}</td><td class="num">${pct(h.memory_consumed.worst.v)}</td><td>${spark(h.spark)}</td>
    <td class="num">${n0(h.running_vms)}</td><td class="num">${h.cpu_overcommit}</td><td class="num">${h.memory_overcommit}</td><td>${h.state === 'running' ? 'Running' : esc(h.state.replace('_', ' '))}</td></tr>`).join('');
  return remainingSummary(c.remaining, d.object.kind) + `${c.remaining && d.object.kind !== 'cluster' ? `<h2>Its cluster, ${esc(c.cluster)}</h2>` : ''}<section class="persp" data-section="capacity-cluster">
    <div class="verdict" data-verdict="${ck.state}"><p>${verdict}${cn}</p>${ck.state === 'no_check' ? '' : `<div class="why-panel" id="why-verdict" data-why${ck.state === 'closed' ? '' : ' hidden'}><p>${esc(why)} The worst ${ck.worst_percent}% of samples are left out.</p>${checkDiagram(ck, c.kpis)}</div>`}</div>
    ${c.marked_host ? `<p class="muted">This is the cluster's capacity. ${esc(c.marked_host)} is highlighted in the host list below.</p>` : ''}
    <h2>Key Trends</h2>
    <p class="muted">${esc(WINDOWS.find(w => w[0] === R.window)[1])}, one point every ${fmtDur(m)}. Each point shows the worst value in that interval.</p>
    ${c.kpis.map(k => kpiBlock(k, ck, m)).join('')}
    <h3>Past checks</h3>${strip}
    <h2>What makes up Consumption <span class="muted">as % of usable capacity</span></h2>
    ${c.parts.map(p => metricBlock({ ...p, better: 'lower', decimals: p.key.startsWith('memory_b') || p.key.startsWith('memory_z') ? 2 : 1, scale: null, minutes: m }, 'part')).join('')}
    <p class="muted">These hosts have no memory tiering.</p>
    <h2>Usable capacity <span class="muted">hosts that are running</span></h2>${usable}
    <h2>Host balance</h2><p class="muted">A wide gap means some hosts are working harder than others.</p>
    ${spreadChart('cpu_thread_utilization', 'CPU Thread Utilization')}${spreadChart('memory_consumed', 'Memory Consumed')}
    <h2>ESXi hosts, worst first</h2>
    <table class="data" data-hosts><thead><tr><th>Host</th><th class="num">CPU Thread Utilization, 95th percentile</th><th class="num">CPU, Worst</th><th class="num">Memory Consumed, 95th percentile</th><th class="num">Memory, Worst</th><th>Memory Consumed</th><th class="num">Running VMs</th><th class="num">CPU Overcommit</th><th class="num">Memory Overcommit</th><th>State</th></tr></thead><tbody>${hostRows}</tbody></table>
    ${monthsAhead(capGroupURL(d.object.path.find(p => p.kind === 'location')?.id || 'sg', c.class_of_service))}</section>`;
}
function capGroup(g, d) {
  const cls = CLASS_NAME[g.class], m = g.point_minutes, sel = g.selected, C = g.closed, N = g.near_closure;
  const filter = `<div class="toolbar"><span class="lbl">Class of service</span><nav class="windows" aria-label="Class of service">${g.classes.map(k => `<a href="${url({ cls: k })}" data-cls="${k}"${k === g.class ? ' aria-current="true"' : ''}>${CLASS_NAME[k]}</a>`).join('')}</nav>
    ${sel.default ? '' : `<a class="link" href="${url({ at: '' })}">Back to the highest point</a>`}</div>
    ${g.stale_locations.length ? `<p class="why">No data from ${esc(g.stale_locations.join(', '))}. Left out, never counted as open.</p>` : ''}`;
  if (!g.clusters) return filter + `<p data-empty>No ${esc(cls)} cluster under this object.</p>` + monthsAhead(`/capacity/clusters${PASS ? '?' + PASS : ''}`);
  const when = fmtPoint(sel.t, m);
  const words = `${C.now} of ${g.clusters} ${esc(cls)} cluster${g.clusters === 1 ? '' : 's'} closed at the latest check${C.now_clusters.length ? ` (${C.now_clusters.map(x => objLink(x)).join(', ')})` : ''}; ${C.closed_since_previous.length} closed and ${C.opened_since_previous.length} opened since the check before.`;
  const closedBars = C.as_words ? '' : `<div class="cbars" data-closed-bars role="img" aria-label="Closed clusters at each check">${C.per_check.map(x => `<span title="${esc(fmtDay(x.end))}: ${x.closed} closed" class="${x.closed ? '' : 'zero'}" style="height:${Math.max(3, 100 * x.closed / Math.max(1, g.clusters))}%"></span>`).join('')}</div>
    <div class="stripaxis muted"><span>${esc(fmtDay(C.per_check[0].end))}</span><span>${esc(fmtDay(C.per_check[C.per_check.length - 1].end))}</span></div>`;
  const hi = g.spread.points.reduce((a, x) => x.highest != null && (a == null || x.highest > a.highest) ? x : a, null);
  const spread = lineChart('capspread', g.spread.points, [
    { key: 'highest', who: 'highest_cluster', label: 'Highest Cluster Consumption', short: 'Highest', band: riskBand, worse: Math.max },
    { key: 'percentile', label: `${g.spread.percentile}th percentile`, short: `${g.spread.percentile}th pct`, band: riskBand, worse: Math.max, dash: true }],
    { label: 'Cluster Consumption across clusters, 0 to 100%', max: 100, minutes: m, bands: HIGH_BANDS, selected: sel.index });
  const rows = g.clusters_at.map(r => `<tr data-cluster-at="${esc(r.cluster)}"><td>${objLink(r.cluster)}</td><td>${esc(r.location)}</td><td>${esc(CLASS_NAME[r.class_of_service] || r.class_of_service)}</td>
    <td>${r.check.state === 'closed' ? `<span class="chip ${r.check.rule === 2 ? 'red' : 'amber'}">Closed for new VMs</span> <span class="muted">since ${esc(fmtDay(r.check.since))}</span>` : r.check.state === 'open' ? `Open${r.near_closure ? ` <span class="near">Near closure, ${pct(r.check.consumption)}</span>` : ''}` : 'No check'}</td>
    <td class="num">${pct(r.consumption)}</td><td class="num">${pct(r.performance)}</td><td class="num">${pct(r.risk)}</td><td>${spark(r.spark)}</td>
    <td>${r.contention_now ? `<a class="chip red" href="${objURL(r.cluster)}">Contention now</a> ${pct(r.contention_now.value)}` : ''}</td></tr>`).join('');
  return filter + `<section class="persp" data-section="capacity-group">
    <h3>Clusters closed for new VMs</h3><p data-closed-words>${words}</p>${closedBars}
    <h3>Consumption across clusters</h3><p data-spread-line>Highest: ${pct(hi.highest)} at ${esc(fmtPoint(hi.t, m))}, ${objLink(hi.highest_cluster)}; the ${g.spread.percentile}th percentile then ${pct(hi.percentile)}.${g.clusters <= 10 ? ` With 10 clusters or fewer, the ${g.spread.percentile}th percentile is the highest.` : ''}</p>${spread}
    <h3>Near closure</h3><p data-near-closure>${N.clusters.length} open cluster${N.clusters.length === 1 ? '' : 's'} with Consumption above ${N.above}% at the latest check${N.clusters.length ? `: ${N.clusters.map(x => objLink(x)).join(', ')}` : ''}. ${esc(N.direction.charAt(0).toUpperCase() + N.direction.slice(1))} over the last 7 checks (${N.counts_7_checks.join(', ')}).</p>
    <h3 data-at="${esc(sel.t)}">Clusters at ${esc(when)} <span class="muted">${sel.default ? 'the highest point of the window' : 'the time you picked'}; closed first, then near closure</span></h3>
    <table class="data" data-clusters-at><thead><tr><th>Cluster</th><th>Location</th><th>Class</th><th>At the latest check</th><th class="num">Consumption</th><th class="num">Performance</th><th class="num">Risk</th><th>Consumption over the window</th><th>Now</th></tr></thead><tbody>${rows}</tbody></table>
    <p class="muted">Performance and Risk across clusters are on the <a class="link" href="${url({ pillar: 'performance' })}">Performance tab</a>.</p>
    ${monthsAhead(`/capacity/clusters${PASS ? '?' + PASS : ''}`)}</section>`;
}
function capacityTab(c, d) {
  if (!c || c.kind === 'none') return '<p class="muted">No cluster under this object.</p>';
  return c.kind === 'group' ? capGroup(c, d) : capCluster(c, d);
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
    if (r.status === 200) go(url({ caseId: r.body.id, newComplaint: undefined }));
    else { document.getElementById('cfmsg').textContent = r.body.error; document.body.dataset.complaint = String(r.status); }
  });
}

function chainTree(links, effect, open) {
  const kids = links.filter(l => l.effect === effect);
  if (!kids.length) return '';
  return `<ul class="links">${kids.map(l => `<li><div class="clink ${l.state}" data-link="${l.id}">
    <div class="cause"><span>${esc(l.cause)}</span>${e2mark({ kind: 'link', case: R.caseId, link: l.id }, 'this link')}</div>
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
  const head = `<div class="objhead"><div><div class="crumbs">${d.path.slice(0, -1).map(p => esc(p)).join(' › ')}</div><div class="kind">Case · ${TRIGGER[d.trigger]}</div><div class="titlerow"><h1>${esc(d.title)}</h1>${e2mark({ kind: 'case', case: d.id }, 'this case', { name: d.title })}</div>
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
    <h2>Layers</h2><table class="data" data-layers><tbody>${d.layers.map(l => `<tr data-layer-row="${l.layer}"><td>${LAYER[l.layer]}</td><td><span class="chip ${VERDICT[l.verdict][0]}">${VERDICT[l.verdict][1]}</span></td><td>${esc(l.values)}</td><td class="e2cell">${e2mark({ kind: 'layer', case: d.id, layer: l.layer }, `the ${LAYER[l.layer]} layer`)}</td></tr>`).join('')}</tbody></table>
    ${d.hand_over ? `<div class="conclusion" data-handover>${esc(d.hand_over)}</div>` : ''}
    <h2>Timeline</h2><ul class="timeline">${tl.join('')}</ul>
    <h2>Who else</h2>${we && we.count ? `<p>${n0(we.count)} object${we.count === 1 ? '' : 's'} share it: ${esc(we.test)}.</p><p>${we.objects.map(o => objLink(o)).join(', ')}</p><p><a class="link" href="${url({ activity: 'rules', caseId: undefined })}">Add a check rule</a></p>` : '<p class="muted">No other object shows this symptom.</p>'}
    <h2>Close</h2>${open ? `<div class="toolbar"><button type="button" class="act secondary" id="draft">Draft the root cause analysis</button><span class="muted">Agent E2 drafts from the confirmed links. It fills no field; you decide.</span></div>
    <div class="draft" id="answer" aria-live="polite" hidden></div>` : ''}${d.closure ? `<p data-closed><strong>Closed</strong> by ${esc(d.closure.by)}: ${esc(d.closure.root_cause)}. Fix: ${esc(d.closure.corrective_action)}. Detection: ${esc(DETECTION[d.closure.detection])}, ${esc(d.closure.detection_note)}</p>`
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
  const dr = document.getElementById('draft');
  if (dr) dr.addEventListener('click', async () => {
    const box = document.getElementById('answer'); box.hidden = false; box.innerHTML = '<span class="muted">Agent E2 is drafting…</span>';
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
  main.innerHTML = objHead(d.object) + `<p class="runline">Framed in capacity: what it frees, how far it moves the next purchase decision.</p>` + tabbed(st, d.object.kind, `<div class="msg" role="status">${esc(msg)}</div>` + body);
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

// ---------------------------------------------------------------- Agent E2: the mark and the panel (frame.md; D-097)
// The mark and the panel are shared with the NOC desk (/e2/panel.js, D-098). Here: what L2's pages send, name and suggest.
// The panel is docked right and pushes the content; the tree folds to a strip while it is open.
const E2_LAYERS = ['guest_os', 'virtual_motherboard'];
const e2mark = E2Panel.mark, e2TopMark = E2Panel.topMark, e2Health = E2Panel.health, e2Follow = E2Panel.follow;
// The context of the page itself: the case, or the object with its tab and window.
const pageCtx = () => R.caseId ? { kind: 'case', case: R.caseId, show: { about: 'this case' } }
  : { kind: 'page', show: { about: 'this page' } };
const objName = () => (main.querySelector('.objhead h1') || {}).textContent || R.object;
const kindName = () => ((main.querySelector('.objhead [data-kind]') || {}).dataset?.kind || (main.querySelector('.objhead .kind') || {}).textContent || 'object').replace(/^Case.*/, 'case');
const winName = w => (WINDOWS.find(x => x[0] === w) || WINDOWS[1])[1];
function e2Label(c) {
  const where = `${objName()} · ${PNAME[c.pillar] || 'Summary'} · ${winName(c.window)}`;
  if (c.kind === 'metric' || c.kind === 'kpi') return `${c.show.about} · ${where}`;
  if (c.kind === 'vm_layer') return `${c.show.name} · ${where}`;
  if (c.kind === 'finding') return `Finding: ${c.show.name || ''}`;
  if (c.case) return R.caseId ? `Case: ${objName()}${c.kind === 'link' ? ' · a link' : c.kind === 'layer' ? ` · ${c.show.about.replace(/^the /, '')}` : ''}` : 'Case';
  if (R.activity === 'troubleshoot' || R.activity === 'rules' || R.activity === 'calendar') return `${objName()} · ${R.activity.charAt(0).toUpperCase() + R.activity.slice(1)}`;
  return where;
}
function suggestions(c) {
  const k = kindName().toLowerCase().replace(/^esxi /, 'ESXi ').replace(/^vm$/, 'VM');
  if (c.kind === 'metric' || c.kind === 'kpi') return [`Is ${c.show.p95} a problem for this ${k}?`, c.show.worst ? `Why the worst at ${c.show.worst}?` : null, 'What should I check next?'].filter(Boolean);
  if (c.kind === 'finding') return ['Explain this finding.', 'What should I check next?'];
  if (c.kind === 'vm_layer') return [`Is the ${c.show.layer} layer the problem?`, 'Which of its metrics matters most here?', 'What should I check next?'];
  if (c.case) return ['Is the VMware platform the cause?', 'What should I check next?'];
  // A whole-page question: on a VM's Performance tab PCM sends both layers' figures (frame.md, Agent E2 panel).
  if (c.pillar === 'performance' && k === 'VM') return [`Is this VM performing well over the ${winName(c.window).replace(/^Last /, 'last ')}?`, 'Which layer is the problem, if any?', 'What should I check next?'];
  return [`What needs me on this ${k}?`, 'What should I check next?'];
}
// Charts measure their box: re-fit them when the panel opens or closes.
function refit() { requestAnimationFrame(() => main.querySelectorAll('[data-chartbox]').forEach(b => { if (CHARTS[b.dataset.chartbox]) mountChart(b); })); }
E2Panel.init({
  store: 'l2.e2',
  get: p => getJSON(p, '', null),
  post: postJSON,
  root: () => main,
  pageCtx,
  full: c => c.case || c.kind === 'finding' ? c : { view: R.view, object: R.object, window: R.window || '24h', pillar: R.pillar || 'summary', ...c },
  label: e2Label,
  suggestions,
  convKey: c => c.case ? `case:${c.case}` : c.kind === 'finding' ? `finding:${c.finding}` : `${c.object}|${c.pillar}`,
  linkHref: l => objURL(l.id, l.view),
  outline: '.metric, .finding, .clink, tr, .objhead, section.layer',
  onToggle: refit,
  answerExtra: a => a.finding && a.finding.outcome === 'problem' ? `<div class="toolbar"><button type="button" class="act secondary" data-e2act="trouble" data-id="${esc(a.finding.id)}">Troubleshoot this</button></div>` : '',
  onAction: async el => { if (el.dataset.e2act !== 'trouble') return; const r = await postJSON('cases', { trigger: 'finding', finding: el.dataset.id }); if (r.status === 200) go(url({ activity: 'troubleshoot', caseId: r.body.id })); },
  escBlocked: () => { const l = document.getElementById('winlist'); return !!(l && !l.hidden); },
});

// ---------------------------------------------------------------- navigation without a page load
// Every in-app link and every change of the address goes through go(). The page, the top bar and the tree stay; the content is replaced.
let CTL = null, SEQ = 0, OPEN_CASES = 0, FOCUS = null;
const RUN = { monitor, troubleshoot, improve, rules, calendar };
const pathOf = u => u.split('?')[0];
function go(href, replace = false) {
  const ae = document.activeElement;
  FOCUS = ae && ae.closest ? (ae.closest('[role="tab"]') ? 'tab' : ae.closest('#winlist') ? 'win' : null) : null;
  closeWin();
  const now = location.pathname + location.search;
  if (href === now) return;
  const moved = pathOf(href) !== pathOf(now);
  try { history[replace ? 'replaceState' : 'pushState'](null, '', href); } catch (e) { location.href = href; return; }
  route({ top: moved });
}
function preview() {
  // Answer at once: the selected tab and the window follow the click while the data is on its way.
  main.querySelectorAll('[role="tab"]').forEach(a => { const on = a.dataset.pillar === R.pillar; a.setAttribute('aria-selected', on); a.tabIndex = on ? 0 : -1; });
  const cur = WINDOWS.find(([w]) => w === R.window);
  const lbl = main.querySelector('.winbtn .lbl');
  if (cur && lbl) lbl.textContent = cur[1];
  main.querySelectorAll('.winlist a').forEach(a => a.setAttribute('aria-selected', a.dataset.w === R.window));
}
async function route({ top = false, first = false } = {}) {
  QS = new URLSearchParams(location.search); PASS = passOf(QS);
  landing(); R = parseRoute();
  const seq = ++SEQ;
  if (CTL) CTL.abort();
  CTL = new AbortController(); SIG = CTL.signal;
  document.body.dataset.ready = '0';
  if (!first) { main.classList.add('loading'); main.setAttribute('aria-busy', 'true'); preview(); }
  try {
    const counts = getJSON('cases', '', null).then(l => l.filter(c => c.state === 'open').length).catch(() => OPEN_CASES);
    if (R.caseId) { const c = await getJSON(`cases/${enc(R.caseId)}`).catch(e => { if (e.name === 'AbortError') throw e; return null; }); if (c) R.object = c.object; }
    if (seq !== SEQ) return;
    const treeDone = (first ? tree() : syncTree()).catch(() => { document.getElementById('tree').innerHTML = '<p class="muted">Could not load the tree.</p>'; });
    await Promise.all([counts.then(n => { OPEN_CASES = n; return topBar(n); }), (RUN[R.activity] || monitor)()]);
    if (seq !== SEQ) return;
    await treeDone;
    main.classList.remove('loading'); main.removeAttribute('aria-busy');
    e2Follow();
    if (top) window.scrollTo(0, 0);
    // The header is redrawn, so a keyboard user would lose their place: put the focus back where it was.
    if (FOCUS === 'tab') { const t = main.querySelector('[role="tab"][aria-selected="true"]'); if (t) t.focus({ preventScroll: true }); }
    else if (FOCUS === 'win') { const w = document.getElementById('winbtn'); if (w) w.focus({ preventScroll: true }); }
    FOCUS = null;
    document.body.dataset.ready = '1';
  } catch (e) {
    if (e && e.name === 'AbortError' || seq !== SEQ) return; // a newer navigation owns the page
    main.classList.remove('loading'); main.removeAttribute('aria-busy');
    main.innerHTML = '<p>Could not load data. Try again later.</p>'; document.body.dataset.ready = 'error';
  }
}
document.addEventListener('click', e => {
  if (e.defaultPrevented || e.button !== 0 || e.metaKey || e.ctrlKey || e.shiftKey || e.altKey) return;
  const a = e.target.closest('a[href]');
  if (!a || a.target || a.hasAttribute('download')) return;
  let u; try { u = new URL(a.href, location.href); } catch (err) { return; }
  if (u.origin !== location.origin || !/^\/l2(\/|$)/.test(u.pathname)) return;
  e.preventDefault();
  // A tree or search link names an object; its pillar and window are read now, not when it was drawn.
  go(a.dataset.obj ? objURL(a.dataset.obj, a.dataset.view || undefined) : u.pathname + u.search);
});
window.addEventListener('popstate', () => route({ top: false }));

// ---------------------------------------------------------------- the time dropdown and the tab keys
function closeWin() {
  document.querySelectorAll('.winbtn[aria-expanded="true"]').forEach(b => { b.setAttribute('aria-expanded', 'false'); const l = document.getElementById('winlist'); if (l) l.hidden = true; });
}
function openWin(focusSelected) {
  const b = document.getElementById('winbtn'), l = document.getElementById('winlist');
  if (!b || !l) return;
  l.hidden = false; b.setAttribute('aria-expanded', 'true');
  if (focusSelected) (l.querySelector('[aria-selected="true"]') || l.querySelector('a')).focus();
}
document.addEventListener('click', e => {
  const b = e.target.closest('#winbtn');
  if (b) { b.getAttribute('aria-expanded') === 'true' ? closeWin() : openWin(false); return; }
  if (!e.target.closest('#winlist')) closeWin();
});
document.addEventListener('keydown', e => {
  const b = document.getElementById('winbtn'), l = document.getElementById('winlist');
  if (e.key === 'Escape' && l && !l.hidden) { closeWin(); b.focus(); return; }
  if (e.target === b && ['ArrowDown', 'ArrowUp'].includes(e.key)) { e.preventDefault(); openWin(true); return; }
  if (l && !l.hidden && l.contains(e.target)) {
    const items = [...l.querySelectorAll('a')], i = items.indexOf(e.target);
    const to = { ArrowDown: items[(i + 1) % items.length], ArrowUp: items[(i - 1 + items.length) % items.length], Home: items[0], End: items[items.length - 1] }[e.key];
    if (to) { e.preventDefault(); to.focus(); }
    if (e.key === 'Tab') closeWin();
  }
  // Tabs: the arrows move between them, Enter opens one. A tab fetches data, so moving is not choosing.
  const tab = e.target.closest && e.target.closest('[role="tab"]');
  if (tab && ['ArrowLeft', 'ArrowRight', 'Home', 'End'].includes(e.key)) {
    const all = [...tab.parentElement.querySelectorAll('[role="tab"]')], i = all.indexOf(tab);
    const to = { ArrowRight: all[(i + 1) % all.length], ArrowLeft: all[(i - 1 + all.length) % all.length], Home: all[0], End: all[all.length - 1] }[e.key];
    e.preventDefault(); to.focus();
  }
});

// ---------------------------------------------------------------- start
e2Health();
route({ first: true });
