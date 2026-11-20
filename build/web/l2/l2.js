// GENERATED from spec/workspaces/l2/. Do not edit by hand (D-070).
'use strict';
const QS = new URLSearchParams(location.search);
const PASS = ['now', 'enable'].filter(k => QS.get(k)).map(k => `${k}=${encodeURIComponent(QS.get(k))}`).join('&');
const apiURL = (p, extra = '') => `/api/l2/${p}${PASS || extra ? '?' : ''}${[PASS, extra].filter(Boolean).join('&')}`;
const getJSON = (p, extra) => fetch(apiURL(p, extra)).then(r => { if (!r.ok) throw new Error(r.status); return r.json(); });
const postJSON = (p, body) => fetch(apiURL(p), { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body || {}) })
  .then(async r => ({ status: r.status, body: await r.json() }));
const esc = s => String(s ?? '').replace(/[&<>"]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
const href = p => `${p}${PASS ? '?' + PASS : ''}`;
const fmtTime = iso => new Date(iso).toLocaleString('en-GB', { day: 'numeric', month: 'short', hour: '2-digit', minute: '2-digit', timeZoneName: 'short' });
const STATUS = { green: 'Good', amber: 'Watch', red: 'Act now', pass: 'Pass', fail: 'Fail', info: 'Note' };
const chip = s => `<span class="chip ${s === 'pass' ? 'green' : s === 'fail' ? 'red' : s === 'info' ? 'no_data' : s}">${STATUS[s] || s}</span>`;
const VERDICT = { present_health: 'Present health', risk: 'Risk', efficiency: 'Efficiency' };
const GROUP = { correct_it: 'Correct it', update_it: 'Update it', simplify_it: 'Simplify it', optimize_it: 'Optimize it' };
const STEP = { contention: 'Contention', consumption: 'Consumption', configuration: 'Configuration', known_bug: 'Known bug', log: 'Log' };
const page = document.body.dataset.page;
const main = document.getElementById('main');

function nav() {
  const cur = { index: '/l2', escalations: '/l2/escalations', investigate: '/l2', configuration: '/l2/configuration', context: '/l2/context', authoring: '/l2/authoring' }[page];
  const link = (h, t) => `<a href="${href(h)}"${cur === h ? ' aria-current="page"' : ''}>${t}</a>`;
  document.getElementById('nav').innerHTML = `<header class="top"><span class="name">L2 Platform</span><nav aria-label="L2">${link('/l2', 'Today')}${link('/l2/escalations', 'Escalations')}${link('/l2/configuration', 'Configuration')}${link('/l2/context', 'Calendar')}${link('/l2/authoring', 'Thresholds')}</nav><span class="time" id="time"></span></header>`;
}

// ---------------------------------------------------------------- /l2: daily check result
async function daily(msg = '') {
  const d = await getJSON('daily');
  const count = v => d.findings.filter(f => f.verdict === v).length;
  const finding = f => {
    const p = f.proposal;
    const prop = p ? `<div class="proposal"><strong>Proposed fix:</strong> ${esc(p.reason)} ${p.state === 'waiting'
      ? `<button type="button" class="act" data-approve="${p.id}">Approve</button> <button type="button" class="act secondary" data-reject="${p.id}">Reject</button>`
      : `<strong>${esc(p.state)}</strong> by ${esc(p.decided_by)}${p.rejection_reason ? `: ${esc(p.rejection_reason)}` : ''}`}</div>` : '';
    const inv = f.investigate ? ` <a class="link" href="${href('/l2/investigate/' + f.investigate)}">Investigate</a>` : '';
    return `<div class="finding" data-finding="${f.id}">${chip(f.severity)}<div><div class="chain">${esc(VERDICT[f.verdict])} · ${esc(f.pillar)} · ${f.parent_chain.map(esc).join(' › ')}</div>
      <strong>${esc(f.object)}</strong>: ${esc(f.summary)}${inv}
      ${f.explained_by ? `<div class="explained">Explained by the calendar: ${esc(f.explained_by.note)}</div>` : ''}${prop}</div><div></div></div>`;
  };
  main.innerHTML = `<h1>Today's check</h1>
    <p class="muted">PCM ran the daily check for ${esc(d.run.region)} from ${fmtTime(d.run.started_at)} to ${fmtTime(d.run.finished_at)}. ${esc(d.run.review)}</p>
    <div class="verdicts">${['present_health', 'risk', 'efficiency'].map(v => `<div class="verdict ${d.verdicts[v]}" data-verdict="${v}"><h2>${VERDICT[v]} ${chip(d.verdicts[v])}</h2><div>${count(v)} ${count(v) === 1 ? 'finding' : 'findings'}</div></div>`).join('')}</div>
    <h2>Findings, worst first</h2>${d.findings.length ? d.findings.map(finding).join('') : '<p>Nothing needs you this morning.</p>'}
    <div class="msg" role="status">${esc(msg)}</div>
    <h2>Trust ladder</h2><table><thead><tr><th>Action type</th><th>Tier</th><th>Approvals</th><th>Rollbacks</th><th></th></tr></thead><tbody>
    ${d.action_types.map(t => `<tr><td>${esc(t.action_type.replaceAll('_', ' '))}</td><td>${t.tier}${t.promoted_by ? ` (by ${esc(t.promoted_by)})` : ''}</td><td>${t.approvals}</td><td>${t.rollbacks}</td>
      <td>${t.promotion_offered ? `<button type="button" class="act" data-promote="${t.action_type}">Make automatic</button>` : ''}</td></tr>`).join('')}</tbody></table>
    <h2>Slipped alerts</h2>${d.slipped_alerts.length ? `<ul>${d.slipped_alerts.map(s => `<li>${esc(s.object)}: ${esc(s.title)}, ${fmtTime(s.raised)}. No check finding predicted it. <a class="link" href="${href('/l2/authoring')}">Add a check rule</a></li>`).join('')}</ul>` : '<p>The check predicted every alert.</p>'}`;
  main.querySelectorAll('[data-approve]').forEach(b => b.addEventListener('click', async () => { await postJSON(`proposals/${b.dataset.approve}/approve`); daily('Approved. Counted on the trust ladder.'); }));
  main.querySelectorAll('[data-reject]').forEach(b => b.addEventListener('click', async () => {
    const reason = prompt('Why reject? The reason tells L2 which rule is wrong.');
    const r = await postJSON(`proposals/${b.dataset.reject}/reject`, { reason }); daily(r.status === 200 ? 'Rejected, with the reason recorded.' : r.body.error);
  }));
  main.querySelectorAll('[data-promote]').forEach(b => b.addEventListener('click', async () => {
    const reason = prompt('Why make it automatic? You will be the person accountable for its automatic runs.');
    const r = await postJSON(`action-types/${b.dataset.promote}/promote`, { reason }); daily(r.status === 200 ? `Now automatic. Accountable: ${r.body.promoted_by}.` : r.body.error);
  }));
}

// ---------------------------------------------------------------- /l2/escalations
async function escalations(msg = '') {
  const list = await getJSON('escalations');
  const block = e => {
    const ev = e.evidence;
    const vil = ev.villains.map(v => `<tr><td>${esc(v.vm)}</td><td>${v.class}, ${v.environment}</td><td>CPU usage ${v.cpu_usage_percent}% of ${v.vcpu} vCPU</td><td>CPU Ready ${v.cpu_ready_percent}%</td></tr>`).join('');
    const vic = ev.victims.map(v => `<tr><td>${esc(v.vm)}</td><td>VM Performance ${v.vm_performance}</td><td>CPU Ready ${v.cpu_ready_percent}%</td><td>Co-stop ${v.co_stop_percent}%</td></tr>`).join('');
    const closed = e.closure;
    return `<section class="panel" data-escalation="${e.id}"><h2>${chip(e.severity)} ${esc(e.title)}: ${esc(e.root_object)}</h2><p class="muted">${esc(e.location_name || '')} · escalated to ${esc(e.escalation_route)}</p>
      <h3>SOP steps run by L1</h3><ul>${ev.sop_steps.filter(s => s.result).map(s => `<li>${esc(s.text)} <span class="muted">${esc(s.result)}</span></li>`).join('')}</ul>
      <h3>What L1 already did</h3>${ev.l1_actions.length ? `<ul>${ev.l1_actions.map(a => `<li>${esc(a.action.replaceAll('_', ' '))} on ${esc(a.target)} by ${esc(a.by)}: ${esc(a.after)}</li>`).join('')}</ul>` : '<p class="muted">Nothing.</p>'}
      ${vil ? `<h3>Villains</h3><table><tbody>${vil}</tbody></table>` : ''}${vic ? `<h3>Victims</h3><table><tbody>${vic}</tbody></table>` : ''}
      <p><a class="link" href="${href('/l2/investigate/' + e.root_object)}">Investigate ${esc(e.root_object)}</a></p>
      <h3>Agent E2</h3><p><button type="button" class="act secondary" data-rca="${e.id}">Draft the root cause analysis</button></p><div class="draft" id="rca-${e.id}"><span class="muted">Agent E2 drafts; you decide.</span></div>
      <h3>Close</h3>${closed ? `<p><strong>Closed</strong> by ${esc(closed.by)}: ${esc(closed.root_cause)}. Fix: ${esc(closed.corrective_action)}. Detection: ${esc(closed.detection.replaceAll('_', ' '))}, ${esc(closed.detection_note)}</p>`
        : `<form class="inline" data-close="${e.id}"><label>Root cause<input type="text" name="root_cause"></label><label>Corrective action<input type="text" name="corrective_action"></label>
        <label>Detection<select name="detection"><option value="">Choose</option><option value="new_check_rule">New check rule</option><option value="new_alert">New alert</option><option value="new_sop">New SOP for L1</option><option value="sop_updated">SOP updated</option><option value="none_with_reason">None, with a reason</option></select></label>
        <label>Detection note<input type="text" name="detection_note"></label><button type="submit" class="act">Close escalation</button></form>`}</section>`;
  };
  main.innerHTML = `<h1>Escalations</h1><div class="msg" role="status">${esc(msg)}</div>` + (list.length ? list.map(block).join('') : '<p>Nothing escalated to you.</p>');
  main.querySelectorAll('[data-rca]').forEach(b => b.addEventListener('click', async () => {
    const box = document.getElementById('rca-' + b.dataset.rca); box.innerHTML = '<span class="muted">Agent E2 is drafting…</span>';
    const r = await postJSON(`escalations/${b.dataset.rca}/agent`, { task: 'rca_draft' });
    const note = r.body.source !== 'model' ? '<p class="why">Agent E2 is not available, or used words not allowed here. Showing the fixed template.</p>' : '';
    box.innerHTML = note + `<p>${esc(r.body.text)}</p><p class="muted">Model: ${esc(r.body.model)} · asked by ${esc(r.body.record.actor_human)} · recorded in the action history</p>`;
    document.body.dataset.agent = r.body.source;
  }));
  main.querySelectorAll('form[data-close]').forEach(f => f.addEventListener('submit', async ev => {
    ev.preventDefault();
    const body = Object.fromEntries(new FormData(f));
    const r = await postJSON(`escalations/${f.dataset.close}/close`, body);
    escalations(r.status === 200 ? 'Closed with a cause, a fix and a detection decision.' : r.body.error);
  }));
}

// ---------------------------------------------------------------- /l2/investigate/{object}
async function investigate() {
  const obj = decodeURIComponent(location.pathname.split('/').pop());
  const d = await getJSON(`investigate/${encodeURIComponent(obj)}`).catch(() => null);
  if (!d) { main.innerHTML = `<h1>${esc(obj)}</h1><p>No such object.</p>`; return; }
  const realm = (name, r) => `<div class="card ${r.status}"><h3>${name} ${chip(r.status)}</h3>${Object.entries(r).filter(([k]) => k !== 'status').map(([k, v]) => `<div class="row"><span>${esc(k.replaceAll('_', ' '))}</span><span>${v}</span></div>`).join('')}</div>`;
  main.innerHTML = `<h1>Investigate ${esc(d.object)}</h1>
    ${d.parents.length ? `<h2>Clear the infrastructure first</h2><ul>${d.parents.map(p => `<li>${chip(p.status)} ${esc(p.kind)} ${esc(p.object)}: ${esc(p.note)}</li>`).join('')}</ul>` : ''}
    <h2>Checks in the SP5 order</h2><table><thead><tr><th>Step</th><th>Result</th><th>Values</th></tr></thead><tbody>
    ${d.steps.map(s => `<tr class="${s.step === d.first_failing ? 'step-fail' : ''}"><td>${STEP[s.step]}${s.step === d.first_failing ? ' (first failing)' : ''}</td><td>${chip(s.status)}</td><td>${esc(s.values)}</td></tr>`).join('')}</tbody></table>
    ${d.realms ? `<h2>VM and Guest OS, side by side</h2><div class="cols2">${realm('VM', d.realms.vm)}${realm('Guest OS', d.realms.guest_os)}</div>` : ''}
    <div class="conclusion" data-realm="${d.realm_verdict}">${esc(d.conclusion)}</div>
    <h2>Log events, same object and window</h2><ul>${d.logs.map(l => `<li>${fmtTime(l.at)}: ${esc(l.text)}</li>`).join('')}</ul>
    <h2>Ask Agent E2 why</h2><form class="inline" id="ask"><label>Question<input type="text" name="question" size="70" value="Is the VMware platform the cause? What should I check next?"></label><button type="submit" class="act">Ask</button></form>
    <div class="draft" id="answer" aria-live="polite"><span class="muted">Agent E2 reads the knowledge base and the facts on this page. It takes about 30 seconds.</span></div>`;
  document.getElementById('ask').addEventListener('submit', async ev => {
    ev.preventDefault();
    const box = document.getElementById('answer');
    box.innerHTML = '<span class="muted">Agent E2 is reading the knowledge base…</span>';
    const r = await postJSON(`investigate/${encodeURIComponent(obj)}/ask`, { question: ev.target.elements.question.value });
    if (r.body.source !== 'service') {
      box.innerHTML = '<p class="why">The Agent E2 service is not available.</p>';
    } else {
      box.innerHTML = `<div class="answer-text">${esc(r.body.content).replace(/\n/g, '<br>')}</div>
        <p class="muted">Knowledge files read: ${r.body.files_read.map(esc).join(', ')}</p>
        <p class="muted">Model: ${esc(r.body.model)} · asked by ${esc(r.body.record.actor_human)} · recorded in the action history</p>`;
    }
    document.body.dataset.ask = r.body.source;
  });
}

// ---------------------------------------------------------------- /l2/configuration
async function configuration(msg = '') {
  const d = await getJSON('configuration');
  main.innerHTML = `<h1>Configuration</h1><p class="muted">Filter: Gold first. Ordered by urgency.</p><div class="msg" role="status">${esc(msg)}</div>`
    + Object.entries(d.groups).map(([g, items]) => `<h2>${GROUP[g]}</h2>` + (items.length ? `<table><thead><tr><th>Object</th><th>Setting</th><th>Actual</th><th>Standard</th><th></th></tr></thead><tbody>${items.map(i => `<tr>
      <td>${esc(i.object)}</td><td>${esc(i.setting.replaceAll('_', ' '))}</td><td>${esc(i.actual)}</td><td>${esc(i.standard)} <span class="muted">(v${i.standard_version})</span></td>
      <td>${i.decision ? esc(i.decision.replaceAll('_', ' ')) : `<button type="button" class="act" data-fix="${i.id}" data-choice="fix_the_setting">Fix the setting</button> <button type="button" class="act secondary" data-fix="${i.id}" data-choice="fix_the_standard">Fix the standard</button>`}</td></tr>`).join('')}</tbody></table>`
      : `<p class="muted">Nothing to ${GROUP[g].toLowerCase().replace(' it', '')}.</p>`)).join('');
  main.querySelectorAll('[data-fix]').forEach(b => b.addEventListener('click', async () => {
    const r = await postJSON(`configuration/${b.dataset.fix}/decide`, { choice: b.dataset.choice });
    configuration(r.body.proposal ? 'A proposal now waits for approval on Today.' : r.body.standard_version ? `Standard updated to version ${r.body.standard_version}.` : r.body.error);
  }));
}

// ---------------------------------------------------------------- /l2/context
async function context(msg = '') {
  const list = await getJSON('calendar');
  main.innerHTML = `<h1>Business calendar</h1><p class="muted">The checks and Agent E2 read these entries before they judge.</p>
    ${list.length ? `<table><thead><tr><th>Kind</th><th>Location</th><th>Starts</th><th>Note</th><th>Added by</th></tr></thead><tbody>${list.map(c => `<tr><td>${esc(c.kind.replaceAll('_', ' '))}</td><td>${esc(c.location || 'All')}</td><td>${fmtTime(c.starts_at)}</td><td>${esc(c.note)}</td><td>${esc(c.added_by)}</td></tr>`).join('')}</tbody></table>`
      : '<p>Nothing on the calendar. The checks judge without business context.</p>'}
    <h2>Add an entry</h2><form class="inline" id="add"><label>Kind<select name="kind"><option value="month_end_close">Month-end close</option><option value="quarter_end_close">Quarter-end close</option><option value="payday">Payday</option><option value="migration">Migration</option><option value="dr_test">DR test</option><option value="maintenance_window">Maintenance window</option><option value="other">Other</option></select></label>
    <label>Location<select name="location"><option value="">All</option><option value="sg">Singapore</option><option value="va">Virginia</option><option value="fr">Frankfurt</option><option value="tk">Tokyo</option><option value="ld">London</option></select></label>
    <label>Start<input type="datetime-local" name="starts_at"></label><label>End<input type="datetime-local" name="ends_at"></label><label>Note<input type="text" name="note"></label><button type="submit" class="act">Add</button></form>
    <div class="msg" role="status">${esc(msg)}</div>`;
  document.getElementById('add').addEventListener('submit', async ev => {
    ev.preventDefault();
    const r = await postJSON('calendar', Object.fromEntries(new FormData(ev.target)));
    context(r.status === 200 ? 'Added. The next check reads it.' : r.body.error);
  });
}

// ---------------------------------------------------------------- /l2/authoring
async function authoring(msg = '') {
  const list = await getJSON('thresholds');
  main.innerHTML = `<h1>Thresholds</h1><p class="muted">Replay a new value over the last 30 days before publishing it.</p>`
    + list.map(t => `<section class="panel"><h2>${esc(t.metric)} ${esc(t.operator)} ${t.value} <span class="muted">(version ${t.version})</span></h2>
      <form class="inline" data-t="${t.id}"><label>New value<input type="number" name="value" value="${t.value}" step="1"></label><button type="submit" class="act secondary">Replay</button>
      <button type="button" class="act" data-publish="${t.id}" disabled>Publish</button></form><div id="r-${t.id}"></div></section>`).join('')
    + `<div class="msg" role="status">${esc(msg)}</div>`;
  main.querySelectorAll('form[data-t]').forEach(f => f.addEventListener('submit', async ev => {
    ev.preventDefault();
    const v = f.elements.value.value;
    const r = await getJSON(`thresholds/${f.dataset.t}/replay`, `value=${encodeURIComponent(v)}`);
    const max = Math.max(1, ...r.per_day.flatMap(x => [x.current, x.new]));
    document.getElementById('r-' + f.dataset.t).innerHTML = `<p>Over ${r.days} days: <strong>${r.total_current}</strong> alerts at the current value, <strong>${r.total_new}</strong> at ${r.new_value}.</p>
      <div class="bars" aria-label="Alerts per day, current then new">${r.per_day.map(x => `<span style="height:${100 * x.current / max}%"></span><span class="new" style="height:${100 * x.new / max}%"></span>`).join('')}</div>
      <p class="muted">Teal: current value. Amber: new value. An alert that fires every day teaches the NOC to ignore it.</p>`;
    const pub = f.querySelector('[data-publish]'); pub.disabled = false; pub.dataset.value = v;
    document.body.dataset.replayed = '1';
  }));
  main.querySelectorAll('[data-publish]').forEach(b => b.addEventListener('click', async () => {
    const r = await postJSON(`thresholds/${b.dataset.publish}/publish`, { value: b.dataset.value, reason: 'Replayed before publishing' });
    authoring(r.status === 200 ? `Published as version ${r.body.version}.` : r.body.error);
  }));
}

nav();
const RUN = { index: daily, escalations, investigate, configuration, context, authoring };
RUN[page]().then(() => { document.body.dataset.ready = '1'; }).catch(() => { main.innerHTML = '<p>Could not load data. Try again later.</p>'; document.body.dataset.ready = 'error'; });
