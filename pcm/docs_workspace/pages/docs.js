// GENERATED from pcm/docs_workspace/spec/pages/. Do not edit by hand (D-070).
'use strict';
const QS = new URLSearchParams(location.search);
const PASS = ['now', 'enable'].filter(k => QS.get(k)).map(k => `${k}=${encodeURIComponent(QS.get(k))}`).join('&');
const getJSON = p => fetch(`/api/docs/${p}${PASS ? '?' + PASS : ''}`).then(r => { if (!r.ok) throw new Error(r.status); return r.json(); });
const esc = s => String(s ?? '').replace(/[&<>"]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
const href = p => `${p}${PASS ? '?' + PASS : ''}`;
const fmtTime = iso => new Date(iso).toLocaleString('en-GB', { day: 'numeric', month: 'short', year: 'numeric', hour: '2-digit', minute: '2-digit', timeZoneName: 'short' });
const KIND = { measure: 'Measures', sop: 'SOPs', policy: 'Action policies', threshold: 'Thresholds', standard: 'Configuration standards', setting: 'Settings' };
const ONE = { measure: 'Measure', sop: 'SOP', policy: 'Action policy', threshold: 'Threshold', standard: 'Configuration standard', setting: 'Setting' };
const STATUS = s => `<span class="chip ${s}">${s === 'proposal' ? 'Proposal' : 'Confirmed'}</span>`;
const page = document.body.dataset.page, main = document.getElementById('main');

document.getElementById('nav').innerHTML = `<header class="top"><span class="name">PCM Docs</span><nav aria-label="Docs"><a href="${href('/docs')}"${page === 'index' ? ' aria-current="page"' : ''}>Index</a></nav><span class="time">Read-only. Generated from what PCM runs.</span></header>`;

async function index() {
  const d = await getJSON('');
  const render = q => {
    const t = q.trim().toLowerCase();
    let shown = 0;
    const html = Object.entries(d.groups).map(([k, rows]) => {
      const m = rows.filter(r => !t || r.id.toLowerCase().includes(t) || (r.title || '').toLowerCase().includes(t));
      shown += m.length;
      if (!m.length) return '';
      return `<section class="block" data-kind="${k}"><h2>${KIND[k]} <span class="muted">(${m.length})</span></h2><table><thead><tr><th>ID</th><th>What</th><th>Version</th><th>Owner</th><th>Status</th></tr></thead><tbody>${m.map(r => `<tr data-id="${esc(r.id)}">
        <td><a class="link id" href="${href(`/docs/${k}/${encodeURIComponent(r.id)}`)}">${esc(r.id)}</a></td><td>${esc(r.title)}</td><td>${r.version ?? ''}</td><td>${esc(r.owner ?? '')}</td><td>${STATUS(r.status)}</td></tr>`).join('')}</tbody></table></section>`;
    }).join('');
    document.getElementById('list').innerHTML = shown ? html : '<p class="muted">Nothing matches.</p>';
    document.body.dataset.shown = String(shown);
  };
  const total = Object.values(d.counts).reduce((a, b) => a + b, 0);
  main.innerHTML = `<h1>What PCM owns</h1><p class="lead">${total} objects. Each page is generated from the object PCM runs, so it cannot drift from it. Change an object in the workspace that owns it.</p>
    <label class="muted" for="q">Search by ID or text</label><br><input id="q" class="search" type="search" autocomplete="off">
    <div id="list"></div>
    <section class="block"><h2>Export to private-cloud-explained</h2><p>SOPs (as runbooks), action policies, thresholds and standards, settings, and the inventory summary are exported as Markdown with its front matter, through its pull-request review:</p><pre><code>python3 -m pcm.docs_workspace.docs_workspace --export &lt;private-cloud-explained checkout&gt;</code></pre></section>`;
  render('');
  document.getElementById('q').addEventListener('input', e => render(e.target.value));
}

const val = v => typeof v === 'object' && v !== null ? `<pre>${esc(JSON.stringify(v, null, 2))}</pre>` : esc(v);
async function object() {
  const [, , kind, id] = location.pathname.split('/');
  let d;
  try { d = await getJSON(`${kind}/${encodeURIComponent(decodeURIComponent(id))}`); } catch (e) { main.innerHTML = '<h1>No such object</h1>'; return; }
  const def = Object.entries(d.body).map(([k, v]) => `<dt>${esc(k.replaceAll('_', ' '))}</dt><dd>${k === 'measure' ? `<a class="link id" href="${href('/docs/measure/' + encodeURIComponent(v))}">${esc(v)}</a>` : val(v)}</dd>`).join('');
  const used = d.used_on.length ? `<table><thead><tr><th>Page</th><th>Section</th><th>Question</th><th>Role</th><th>Cadence</th></tr></thead><tbody>${d.used_on.map(u => `<tr data-used="${esc(u.page)}"><td class="id">${esc(u.page)}</td><td>${esc(u.section)}</td><td>${esc(u.question ?? '')}</td><td>${esc(u.role ?? '')}</td><td>${esc((u.cadence || []).join(', '))}</td></tr>`).join('')}</tbody></table>`
    : '<p class="muted">No page reads this directly.</p>';
  const hist = d.history.length ? `<table><thead><tr><th>When</th><th>Who</th><th>Before</th><th>After</th><th>Why</th></tr></thead><tbody>${d.history.map(h => `<tr data-history><td>${fmtTime(h.at)}</td><td>${esc(h.actor_human)}${h.actor_agent ? ' (' + esc(h.actor_agent) + ')' : ''}</td><td>${esc(h.before)}</td><td>${esc(h.after)}</td><td>${esc(h.reason)}</td></tr>`).join('')}</tbody></table>`
    : '<p class="muted">No change recorded.</p>';
  main.innerHTML = `<p class="muted">${ONE[d.kind]}</p><h1 class="id">${esc(d.id)}</h1><p class="lead">${esc(d.title)}</p>
    <div class="meta"><span>Version: <strong data-version>${d.version ?? 'n/a'}</strong></span><span>${d.kind === 'measure' ? 'Defined in' : 'Owner'}: <strong>${esc(d.owner ?? 'n/a')}</strong></span>${STATUS(d.status)}
      ${d.shown_as ? `<span>Shown as "<strong>${esc(d.shown_as)}</strong>"</span>` : ''}
      <span>${d.changed_at ? `Changed on <a class="link" href="${href(d.changed_at)}">${esc(d.changed_at)}</a>` : 'Changed in the specification, not in PCM'}</span></div>
    <section class="block"><h2>Definition</h2><dl class="def">${def}</dl></section>
    <section class="block"><h2>Used on</h2><p class="muted">Who sees a different number if this changes?</p>${used}</section>
    <section class="block"><h2>History</h2><p class="muted">From the action record.</p>${hist}</section>`;
}

({ index, object })[page]().then(() => { document.body.dataset.ready = '1'; })
  .catch(e => { main.innerHTML = `<p class="muted">Could not load: ${esc(e.message)}</p>`; document.body.dataset.ready = '1'; });
