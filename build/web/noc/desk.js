// GENERATED from spec/workspaces/noc/desktop.md, alerts.md, incident.md, shift.md. Do not edit by hand (D-070).
'use strict';
const page = document.body.dataset.page;
const main = document.getElementById('main');
const href = p => `${p}${PASS ? '?' + PASS : ''}`;
document.getElementById('nav').innerHTML = navBar(page === 'index' ? '/noc' : page === 'alert' ? '/noc/alerts' : `/noc/${page}`);

// ---------------------------------------------------------------- /noc: five screens with drill-down
async function screens(selected = 'fast') {
  const [w, inc] = await Promise.all([getJSON('wall'), getJSON('incidents')]);
  document.getElementById('time').textContent = `Updated ${fmtTime(w.updated_at)}`;
  const incFor = (screen, loc) => inc.find(i => (i.location === loc || !i.location) && screenOf(i) === screen);
  const tabs = `<div class="tabs" role="tablist">${w.strip.map(c => `<button role="tab" type="button" data-s="${c.screen}" aria-selected="${c.screen === selected}">${LABEL[c.screen]} ${chip(c.status)}${c.in_hand ? ' <span class="muted">In hand</span>' : ''}</button>`).join('')}</div>`;
  const s = w.screens[selected];
  let body = '';
  const linkTo = (t) => { const i = incFor(selected, t.location); return (t.status === 'red' || t.status === 'amber') && i ? `<p><a class="link" href="${href('/noc/alert/' + i.id)}">Open incident</a></p>` : ''; };
  const card = (t, inner) => t.status === 'no_data' ? `<div class="card no_data"><h3>${esc(t.name)} ${chip('no_data')}</h3><p class="muted">Last good data ${fmtTime(t.last_good)}</p></div>`
    : `<div class="card ${t.status}"><h3>${esc(t.name)} ${chip(t.status)}</h3>${inner}${linkTo(t)}</div>`;
  if (selected === 'changed') body = `<div class="grid5">${s.tiles.map(t => card(t, Object.entries(t.rows).map(([k, r]) => `<div class="row"><span>${CHANGE[k]}</span><span>${r.count} <span class="muted">(about ${r.expected})</span></span></div>`).join(''))).join('')}</div>`;
  if (selected === 'up') body = `<div class="grid5">${s.tiles.map(t => card(t, Object.entries(t.items || {}).map(([k, v]) => `<div class="row"><span>${UP[k]}</span><span>${v}</span></div>`).join(''))).join('')}</div>`
    + (s.no_data_sources || []).map(n => { const i = inc.find(x => x.root_object_type === 'vcf_operations_instance'); return `<p>${chip('red')} No data from ${esc(n.region)}'s VCF Operations since ${fmtTime(n.last_good)}. ${i ? `<a class="link" href="${href('/noc/alert/' + i.id)}">Open incident</a>` : ''}</p>`; }).join('');
  if (selected === 'safe') body = `<div class="grid5">${s.tiles.map(t => card(t, Object.entries(t.findings || {}).map(([k, v]) => `<div class="row"><span>${SAFE[k]}</span><span>${v}</span></div>`).join(''))).join('')}</div><p class="muted">Certificates expiring within 30 days: ${s.risk_certificates}. Escalate them to Platform by SOP.</p>`;
  if (selected === 'set_right') body = `<div class="grid5">${s.tiles.map(t => card(t, `<div class="row"><span>Risky changes, last hour</span><span>${t.count}</span></div>`)).join('')}</div>`;
  if (selected === 'fast') {
    const g = {};
    s.tiles.forEach(t => { (g[t.location] = g[t.location] || { name: t.name, cells: [] }).cells.push(t); });
    body = `<div class="grid5">${Object.values(g).map(x => `<div class="card"><h3>${esc(x.name)}</h3><div class="cells desk">${x.cells.map(c => c.status === 'no_data'
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
  document.getElementById('detail').innerHTML = `<div class="panel"><h2>${esc(id)} ${chip(d.status)}</h2>
    <p>Score now ${Math.round(d.score)} out of 100, ${Math.round(d.trend[0].v)} an hour ago. ${i ? `<a class="link" href="${href('/noc/alert/' + i.id)}">Open incident</a>` : ''}</p>
    <h3>Villains: using the most</h3><table><thead><tr><th>VM</th><th>Class</th><th>Environment</th><th>Note</th></tr></thead><tbody>${rows(d.villains, v => `<tr><td>${esc(v.vm)}</td><td>${v.class}</td><td>${v.environment.replace('_', '-')}</td><td>${esc(v.note)}</td></tr>`)}</tbody></table>
    <h3>Victims: waiting the most</h3><table><thead><tr><th>VM</th><th>Class</th><th>Environment</th><th>Score out of 100</th></tr></thead><tbody>${rows(d.victims, v => `<tr><td>${esc(v.vm)}</td><td>${v.class}</td><td>${v.environment}</td><td>${v.score}</td></tr>`)}</tbody></table></div>`;
}

// ---------------------------------------------------------------- /noc/alerts
async function alerts() {
  const inc = await getJSON('incidents');
  document.getElementById('time').textContent = '';
  main.innerHTML = `<h1>Alerts</h1>` + (inc.length ? `<table><thead><tr><th>Severity</th><th>Incident</th><th>Location</th><th>Alerts</th><th>Opened</th><th>State</th></tr></thead><tbody>${inc.map(i => `<tr>
      <td>${chip(i.severity)}</td><td><a class="link" href="${href('/noc/alert/' + i.id)}">${esc(i.title)}: ${esc(i.root_object)}</a></td><td>${esc(i.location_name || 'All')}</td>
      <td>${i.alert_count}</td><td>${ago(i.opened_at)}</td><td>${i.state}${i.acknowledged_by ? ` by ${esc(i.acknowledged_by)}` : ''}</td></tr>`).join('')}</tbody></table>`
    : '<p>No urgent issues.</p>');
}

// ---------------------------------------------------------------- /noc/alert/{id}: the SOP is the page
const KIND = { diagnosis: 'Check', action: 'Action', escalate: 'Escalate', verify: 'Verify' };
const DONE = { acknowledge: 'Acknowledged', escalate: 'Escalated', close: 'Closed', stop_provisioning: 'Stopped new VMs', reopen_provisioning: 'Reopened to new VMs', time_boxed_limit: 'Limited until end of shift', restart_vm: 'Restarted' };
async function incident(msg = '') {
  const id = location.pathname.split('/').pop();
  const d = await getJSON(`incidents/${id}`);
  const step = s => {
    let right = '';
    if (s.kind === 'action') right = `<div><button type="button" class="act" data-action="${s.action}" data-target="${esc(s.target)}" ${s.allowed ? '' : 'disabled'}>${s.action === 'time_boxed_limit' ? `Limit ${esc(s.target)} until end of shift` : s.action === 'stop_provisioning' ? 'Stop new VMs here' : s.action}</button>${s.allowed ? '' : `<div class="why">${esc(s.refusal)}</div>`}</div>`;
    if (s.kind === 'escalate') right = `<button type="button" class="act" data-escalate="1" ${s.applies && d.state !== 'escalated' && d.state !== 'closed' ? '' : 'disabled'}>Escalate to ${s.route[0].toUpperCase() + s.route.slice(1)}</button>`;
    const res = s.result ? `<div class="res">${esc(s.result)} ${s.passed === true ? '· pass' : s.passed === false ? '· fail' : ''}</div>` : '';
    return `<li><span class="kind">${KIND[s.kind]}</span><div>${esc(s.text)}${res}</div>${right}</li>`;
  };
  main.innerHTML = `<p><a class="link" href="${href('/noc/alerts')}">All alerts</a></p>
    <h1>${chip(d.severity)} ${esc(d.title)}: ${esc(d.root_object)}</h1>
    <p>${esc(d.location_name || 'All locations')} · opened ${ago(d.opened_at)} · ${d.alert_count} alerts grouped · state: <strong>${d.state}</strong>${d.acknowledged_by ? ` by ${esc(d.acknowledged_by)}` : ''}</p>
    <p><button type="button" class="act" id="ack" ${d.state === 'new' ? '' : 'disabled'}>Acknowledge</button></p>
    <h2>SOP: ${esc(d.sop.title)} <span class="muted">(version ${d.sop.version})</span></h2>
    <ol class="steps">${d.sop.steps.map(step).join('')}</ol>
    <h2>Agent E2</h2><div class="draft">${esc(d.agent_draft)}</div>
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

const RUN = { index: () => screens('fast'), alerts, alert: () => incident(), shift: () => shift() };
RUN[page]().then(() => { document.body.dataset.ready = '1'; }).catch(e => { main.innerHTML = '<p>Could not load data. Try again later.</p>'; document.body.dataset.ready = 'error'; });
