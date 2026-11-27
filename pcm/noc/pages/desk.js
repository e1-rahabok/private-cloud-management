// GENERATED from pcm/noc/spec/pages/desktop.md, alerts.md, incident.md, shift.md. Do not edit by hand (D-070).
// Agent E2: desktop.md, Agent E2 mark and panel (D-098). The mark and the panel are shared with L2 (/agent-e2/panel.js).
'use strict';
const page = document.body.dataset.page;
const main = document.getElementById('main');
const href = p => `${p}${PASS ? '?' + PASS : ''}`;
document.getElementById('nav').innerHTML = navBar(page === 'index' ? '/noc' : page === 'alert' ? '/noc/alerts' : `/noc/${page}`);
let SCREEN = 'fast';  // the screen on show, for a question about the page

// ---------------------------------------------------------------- /noc: six screens with drill-down
async function screens(selected = 'fast') {
  SCREEN = selected;
  const [w, inc] = await Promise.all([getJSON('wall'), getJSON('incidents')]);
  document.getElementById('time').textContent = `Updated ${fmtTime(w.updated_at)}`;
  const incFor = (screen, loc) => inc.find(i => (i.location === loc || !i.location) && screenOf(i) === screen);
  const tabs = `<div class="tabs" role="tablist">${w.strip.map(c => `<button role="tab" type="button" data-s="${c.screen}" aria-selected="${c.screen === selected}">${LABEL[c.screen]} ${chip(c.status)}${c.in_hand ? ' <span class="muted">In hand</span>' : ''}</button>`).join('')}</div>`;
  const s = w.screens[selected];
  let body = '';
  const linkTo = (t) => { const i = incFor(selected, t.location); return (t.status === 'red' || t.status === 'amber') && i ? `<p><a class="link" href="${href('/noc/alert/' + i.id)}">Open incident</a></p>` : ''; };
  const tileMark = (loc, name) => E2Panel.mark({ kind: 'tile', screen: selected, location: loc }, name, { name });
  const card = (t, inner) => t.status === 'no_data' ? `<div class="card no_data"><h3>${esc(t.name)} ${chip('no_data')}${tileMark(t.location, t.name)}</h3><p class="muted">Last good data ${fmtTime(t.last_good)}</p></div>`
    : `<div class="card ${t.status}"><h3>${esc(t.name)} ${chip(t.status)}${tileMark(t.location, t.name)}</h3>${inner}${linkTo(t)}</div>`;
  if (selected === 'changed') body = `<div class="grid5">${s.tiles.map(t => card(t, Object.entries(t.rows).map(([k, r]) => `<div class="row"><span>${CHANGE[k]}</span><span>${r.count} <span class="muted">(about ${r.expected})</span></span></div>`).join(''))).join('')}</div>`;
  if (selected === 'up') body = `<div class="grid5">${s.tiles.map(t => card(t, Object.entries(t.items || {}).map(([k, v]) => `<div class="row"><span>${UP[k]}</span><span>${v}</span></div>`).join(''))).join('')}</div>`
    + (s.no_data_sources || []).map(n => { const i = inc.find(x => x.root_object_type === 'vcf_operations_instance'); return `<p>${chip('red')} No data from ${esc(n.region)}'s VCF Operations since ${fmtTime(n.last_good)}. ${i ? `<a class="link" href="${href('/noc/alert/' + i.id)}">Open incident</a>` : ''}</p>`; }).join('');
  if (selected === 'safe') body = `<div class="grid5">${s.tiles.map(t => card(t, Object.entries(t.findings || {}).map(([k, v]) => `<div class="row"><span>${SAFE[k]}</span><span>${v}</span></div>`).join(''))).join('')}</div><p class="muted">Certificates expiring within 30 days: ${s.risk_certificates}. Escalate them to Platform by SOP.</p>`;
  if (selected === 'set_right') body = `<div class="grid5">${s.tiles.map(t => card(t, `<div class="row"><span>Risky changes, last hour</span><span>${t.count}</span></div>`)).join('')}</div>`;
  if (selected === 'capacity') body = `<div class="grid5">${s.tiles.map(t => card(t, ['compute', 'memory', 'storage'].map(r => `<div class="row"><span>${RES[r]} in use</span><span>${Math.round(t.in_use[r])}%</span></div>`).join('')
    + `<div class="row"><span>Time remaining</span><span>${t.days_remaining === null ? 'Beyond 13 months' : `${num(t.days_remaining)} days`}</span></div>`)).join('')}</div>`;
  if (selected === 'fast') {
    const g = {};
    s.tiles.forEach(t => { (g[t.location] = g[t.location] || { loc: t.location, name: t.name, cells: [] }).cells.push(t); });
    body = `<div class="grid5">${Object.values(g).map(x => `<div class="card"><h3>${esc(x.name)}${tileMark(x.loc, x.name)}</h3><div class="cells desk">${x.cells.map(c => c.status === 'no_data'
      ? `<button type="button" class="cellbtn no_data" disabled>No data</button>`
      : `<button type="button" class="cellbtn ${c.status}" data-cluster="${c.cluster}" aria-label="${c.cluster} score ${Math.round(c.score)}">${Math.round(c.score)}<br><small>${esc(c.cluster)}</small></button>`).join('')}</div></div>`).join('')}</div><div id="detail"></div>`;
  }
  main.innerHTML = `<h1>${LABEL[selected]}</h1>${tabs}${body}`;
  main.querySelectorAll('.tabs button').forEach(b => b.addEventListener('click', () => screens(b.dataset.s)));
  main.querySelectorAll('.cellbtn[data-cluster]').forEach(b => b.addEventListener('click', () => cluster(b.dataset.cluster, inc)));
}
const screenOf = i => ({ cluster: 'fast', vm: 'fast', location: 'changed', datastore: 'up', host: 'up', vcf_operations_instance: 'up' }[i.root_object_type] || 'up');

async function cluster(id, inc) {
  const d = await getJSON(`clusters/${id}`);
  const i = inc.find(x => x.root_object === id);
  const rows = (list, f) => list.length ? list.map(f).join('') : '<tr><td colspan="4" class="muted">None. The cluster is serving its VMs well.</td></tr>';
  document.getElementById('detail').innerHTML = `<div class="panel"><h2>${esc(id)} ${chip(d.status)}${E2Panel.mark({ kind: 'cluster', cluster: id }, id, { name: id })}</h2>
    <p>Score now ${Math.round(d.score)} out of 100, ${Math.round(d.trend[0].v)} an hour ago. ${i ? `<a class="link" href="${href('/noc/alert/' + i.id)}">Open incident</a>` : ''}</p>
    <h3>Villains: using the most</h3><table><thead><tr><th>VM</th><th>Class</th><th>Environment</th><th>Note</th></tr></thead><tbody>${rows(d.villains, v => `<tr><td>${esc(v.vm)}</td><td>${v.class}</td><td>${v.environment.replace('_', '-')}</td><td>${esc(v.note)}</td></tr>`)}</tbody></table>
    <h3>Victims: waiting the most</h3><table><thead><tr><th>VM</th><th>Class</th><th>Environment</th><th>Score out of 100</th></tr></thead><tbody>${rows(d.victims, v => `<tr><td>${esc(v.vm)}</td><td>${v.class}</td><td>${v.environment}</td><td>${v.score}</td></tr>`)}</tbody></table></div>`;
}

// ---------------------------------------------------------------- /noc/alerts
async function alerts() {
  const inc = await getJSON('incidents');
  document.getElementById('time').textContent = '';
  main.innerHTML = `<h1>Alerts</h1>` + (inc.length ? `<table><thead><tr><th>Severity</th><th>Incident</th><th>Location</th><th>Alerts</th><th>Opened</th><th>State</th><th><span class="sr">Agent E2</span></th></tr></thead><tbody>${inc.map(i => `<tr data-incident="${esc(i.id)}">
      <td>${chip(i.severity)}</td><td><a class="link" href="${href('/noc/alert/' + i.id)}">${esc(i.title)}: ${esc(i.root_object)}</a></td><td>${esc(i.location_name || 'All')}</td>
      <td>${i.alert_count}</td><td>${ago(i.opened_at)}</td><td>${i.state}${i.acknowledged_by ? ` by ${esc(i.acknowledged_by)}` : ''}</td><td class="e2cell">${E2Panel.mark({ kind: 'incident', incident: i.id }, 'this incident', { name: `${i.title}: ${i.root_object}` })}</td></tr>`).join('')}</tbody></table>`
    : '<p>No urgent issues.</p>');
}

// ---------------------------------------------------------------- /noc/alert/{id}: the SOP is the page
const KIND = { diagnosis: 'Check', action: 'Action', escalate: 'Escalate', verify: 'Verify' };
const DONE = { agent_draft: 'Agent E2 draft', agent_ask: 'Asked Agent E2', acknowledge: 'Acknowledged', escalate: 'Escalated', close: 'Closed', stop_provisioning: 'Stopped new VMs', reopen_provisioning: 'Reopened to new VMs', time_boxed_limit: 'Limited until end of shift', restart_vm: 'Restarted' };
async function incident(msg = '') {
  const id = location.pathname.split('/').pop();
  const d = await getJSON(`incidents/${id}`);
  const step = (s, n) => {
    let right = '';
    if (s.kind === 'action') right = `<div><button type="button" class="act" data-action="${s.action}" data-target="${esc(s.target)}" ${s.allowed ? '' : 'disabled'}>${s.action === 'time_boxed_limit' ? `Limit ${esc(s.target)} until end of shift` : s.action === 'stop_provisioning' ? 'Stop new VMs here' : s.action}</button>${s.allowed ? '' : `<div class="why">${esc(s.refusal)}</div>`}</div>`;
    if (s.kind === 'escalate') right = `<button type="button" class="act" data-escalate="1" ${s.applies && d.state !== 'escalated' && d.state !== 'closed' ? '' : 'disabled'}>Escalate to ${s.route[0].toUpperCase() + s.route.slice(1)}</button>`;
    const res = s.result ? `<div class="res">${esc(s.result)} ${s.passed === true ? '· pass' : s.passed === false ? '· fail' : ''}</div>` : '';
    return `<li data-step="${n}"><span class="kind">${KIND[s.kind]}</span><div>${esc(s.text)}${res}</div>${right}${E2Panel.mark({ kind: 'step', incident: id, step: n }, 'this step', { name: `${d.title}: ${d.root_object}`, n: n + 1 })}</li>`;
  };
  main.innerHTML = `<p><a class="link" href="${href('/noc/alerts')}">All alerts</a></p>
    <h1>${chip(d.severity)} ${esc(d.title)}: ${esc(d.root_object)} ${E2Panel.mark({ kind: 'incident', incident: id }, 'this incident', { name: `${d.title}: ${d.root_object}` })}</h1>
    <p>${esc(d.location_name || 'All locations')} · opened ${ago(d.opened_at)} · ${d.alert_count} alerts grouped · state: <strong>${d.state}</strong>${d.acknowledged_by ? ` by ${esc(d.acknowledged_by)}` : ''}</p>
    <p><button type="button" class="act" id="ack" ${d.state === 'new' ? '' : 'disabled'}>Acknowledge</button></p>
    <h2>SOP: ${esc(d.sop.title)} <span class="muted">(version ${d.sop.version})</span></h2>
    <ol class="steps">${d.sop.steps.map(step).join('')}</ol>
    <h2>Close</h2><p><label for="cause">Root cause</label> <select id="cause"><option value="">Choose a root cause</option>${d.root_causes.map(c => `<option value="${c}">${c.replaceAll('_', ' ')}</option>`).join('')}</select>
      <button type="button" class="act secondary" id="close" disabled>Close incident</button></p>
    <div class="msg" id="msg" role="status">${esc(msg)}</div>
    <h2>Action history</h2>${d.history.length ? `<table><thead><tr><th>Time</th><th>Action</th><th>Target</th><th>Person</th><th>Agent</th><th>Before</th><th>After</th><th>Expires</th></tr></thead><tbody>${d.history.map(h => `<tr><td>${fmtTime(h.at)}</td><td>${DONE[h.action] || h.action}</td><td>${esc(h.target)}</td><td>${esc(h.actor_human)}</td><td>${esc(h.actor_agent || '-')}</td><td>${esc(h.before)}</td><td>${esc(h.after)}</td><td>${h.expires_at ? fmtTime(h.expires_at) : '-'}</td></tr>`).join('')}</tbody></table>` : '<p class="muted">No actions yet.</p>'}
    <h2>Alerts in this incident</h2><table><thead><tr><th>Object</th><th>Alert</th><th>Severity</th><th>Raised</th></tr></thead><tbody>${d.alerts.map(a => `<tr><td>${esc(a.object)}</td><td>${esc(a.title)}</td><td>${chip(a.severity)}</td><td>${ago(a.raised)}</td></tr>`).join('')}</tbody></table>`;
  const cause = document.getElementById('cause'), close = document.getElementById('close');
  cause.addEventListener('change', () => { close.disabled = !cause.value; });
  close.addEventListener('click', async () => { const r = await postJSON(`incidents/${id}/close`, { root_cause: cause.value }); incident(r.status === 200 ? 'Closed.' : r.body.error); });
  document.getElementById('ack').addEventListener('click', async () => { await postJSON(`incidents/${id}/acknowledge`, {}); incident('Acknowledged. The wall resumes its rotation.'); });
  main.querySelectorAll('[data-action]').forEach(b => b.addEventListener('click', async () => {
    const r = await postJSON(`actions/${b.dataset.action}`, { target: b.dataset.target, incident: id });
    incident(r.status === 200 ? 'Done. Written to the action history.' : r.body.error);
  }));
  main.querySelectorAll('[data-escalate]').forEach(b => b.addEventListener('click', async () => {
    const r = await postJSON(`incidents/${id}/escalate`, {}); incident(r.status === 200 ? `Escalated to ${r.body.to}, with the evidence attached.` : r.body.error);
  }));
}

// ---------------------------------------------------------------- /noc/shift
async function shift(msg = '') {
  const s = await getJSON('shift');
  const list = (title, rows) => `<h2>${title}</h2>` + (rows.length ? `<ul>${rows.map(r => `<li><a class="link" href="${href('/noc/alert/' + r.id)}">${esc(r.title)}: ${esc(r.root_object)}</a> ${chip(r.severity)}${r.acknowledged_by ? ` · ${esc(r.acknowledged_by)}` : ''}</li>`).join('')}</ul>` : '<p class="muted">Nothing.</p>');
  main.innerHTML = `<h1>Shift handover</h1><p>This shift ends at ${fmtTime(s.shift_ends)}.</p>`
    + list('Still open', s.open) + list('Acknowledged this shift', s.acknowledged) + list('Waiting on L2', s.waiting_on_l2)
    + `<h2>Limits that end with this shift</h2>${s.limits_expiring.length ? `<ul>${s.limits_expiring.map(l => `<li>${esc(l.target)}, set by ${esc(l.set_by)}, ends ${fmtTime(l.expires_at)}</li>`).join('')}</ul>` : '<p class="muted">None.</p>'}`
    + `<h2>Handover note</h2><label for="note" class="muted">For the next shift</label><textarea id="note"></textarea><p><button type="button" class="act" id="save">Save note</button></p><div class="msg" role="status">${esc(msg)}</div>`
    + (s.notes.length ? `<h2>Earlier notes</h2><ul>${s.notes.map(n => `<li>${fmtTime(n.at)} · ${esc(n.by)}: ${esc(n.note)}</li>`).join('')}</ul>` : '');
  document.getElementById('save').addEventListener('click', async () => { await postJSON('shift', { note: document.getElementById('note').value }); shift('Saved.'); });
}

// ---------------------------------------------------------------- Agent E2 (desktop.md, Agent E2 mark and panel; D-098)
// L1's facts and L1's words: the server checks every answer against the NOC vocabulary. No action button in the panel.
const incidentId = () => location.pathname.split('/').pop();
const pageCtx = () => page === 'alert' ? { kind: 'incident', incident: incidentId(), show: { about: 'this incident', name: (main.querySelector('h1') || {}).textContent || '' } }
  : { kind: 'page', page: page === 'index' ? 'screens' : page, ...(page === 'index' ? { screen: SCREEN } : {}), show: { about: 'this page' } };
function e2Label(c) {
  if (c.kind === 'tile') return `${c.show.name} · ${LABEL[c.screen]}`;
  if (c.kind === 'cluster') return `${c.cluster} · Is it fast?`;
  if (c.kind === 'incident') return `Incident: ${c.show.name.trim()}`;
  if (c.kind === 'step') return `Incident: ${c.show.name} · SOP step ${c.show.n}`;
  return c.page === 'screens' ? `Screens · ${LABEL[c.screen]}` : c.page === 'shift' ? 'Shift handover' : 'Alerts';
}
function e2Suggestions(c) {
  if (c.kind === 'tile') return ['What does this tile tell me?', 'What does the SOP say I should do?'];
  if (c.kind === 'cluster') return ['Why is this cluster not serving its VMs well?', 'Who is the villain, and is it production?', 'What does the SOP say I should do?'];
  if (c.kind === 'incident') return [{ q: 'Explain this incident', draft: 'explain' }, { q: 'Draft the escalation note', draft: 'escalation_note' }, 'What does the SOP say I should do next?'];
  if (c.kind === 'step') return ['Why does the SOP ask this?', 'What does this result mean?'];
  return c.page === 'screens' ? ['What needs me first?', 'Explain this screen in plain words.'] : c.page === 'shift' ? ['What should the next shift know?'] : ['Which incident should I take first?'];
}
E2Panel.init({
  store: 'noc.e2',
  get: p => getJSON(p),
  post: postJSON,
  root: () => main,
  pageCtx,
  full: c => c,
  label: e2Label,
  suggestions: e2Suggestions,
  convKey: c => c.incident ? `incident:${c.incident}` : c.kind === 'cluster' ? `cluster:${c.cluster}` : c.kind === 'tile' ? `tile:${c.screen}:${c.location}` : `page:${c.page}:${c.screen || ''}`,
  linkHref: () => '#',
  outline: '.card, .panel, tr, li[data-step], h1',
  intro: c => `Ask about ${c.show.about}. Agent E2 answers in plain words, from the SOP and the scores PCM sends. It explains; you follow the SOP.`,
  draft: (c, task) => postJSON(`incidents/${c.incident}/agent`, { task }),
});
document.querySelector('.top .time').insertAdjacentHTML('beforebegin', E2Panel.topMark());
E2Panel.health();

const RUN = { index: () => screens('fast'), alerts, alert: () => incident(), shift: () => shift() };
RUN[page]().then(() => { document.body.dataset.ready = '1'; }).catch(e => { main.innerHTML = '<p>Could not load data. Try again later.</p>'; document.body.dataset.ready = 'error'; });
