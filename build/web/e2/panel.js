// GENERATED from spec/workspaces/l2/frame.md (Agent E2 mark, Agent E2 panel) and spec/workspaces/noc/desktop.md. Do not edit by hand (D-070).
// One mark and one panel for every workspace (D-097, D-098). A workspace gives the hooks: what its pages send, how they are named,
// what to suggest. PCM rebuilds the facts on the server from the context; the browser sends only what was clicked.
'use strict';
const E2Panel = (() => {
  const esc = s => String(s ?? '').replace(/[&<>"]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
  const S = { up: null, model: null, open: false, ctx: null, opener: null, busy: false, timer: null, pending: null, waiting: null };
  let H = null;
  const $ = id => document.getElementById(id);
  const convs = () => { try { return JSON.parse(sessionStorage.getItem(H.store) || '{}'); } catch (e) { return {}; } };
  const saveConv = (k, list) => { try { const all = convs(); all[k] = list.slice(-12); sessionStorage.setItem(H.store, JSON.stringify(all)); } catch (e) { /* per-viewer convenience only */ } };

  const mark = (ctx, name, show = {}) => `<button type="button" class="e2mark" data-e2="${esc(JSON.stringify({ ...ctx, show: { about: name, ...show } }))}" aria-label="Ask Agent E2 about ${esc(name)}" title="Ask Agent E2 about ${esc(name)}">E2</button>`;
  function topMark() {
    const label = S.up === false ? 'Agent E2 is not available' : S.up ? 'Agent E2 is available. Ask about this page.' : 'Agent E2';
    return `<button type="button" class="e2mark e2-top${S.up === false ? ' off' : ''}" id="e2top" aria-label="${label}" title="${label}" aria-expanded="${S.open}" aria-controls="e2">E2<span class="dot ${S.up ? 'green' : 'no_data'}" aria-hidden="true"></span></button>`;
  }
  async function health() {
    const h = await H.get('agent/health').catch(() => ({ available: false }));
    S.up = !!h.available; S.model = h.model || null;
    const t = $('e2top');
    if (t) t.outerHTML = topMark();
    document.body.dataset.e2 = S.up ? 'up' : 'down';
    return S.up;
  }
  // A suggestion is a question, or a draft task the workspace runs on its own path (NOC drafts, D-076).
  const sText = x => typeof x === 'string' ? x : x.q;
  function linkify(text, links) {
    let h = esc(text).replace(/`([^`]+)`/g, '<code>$1</code>');
    for (const l of links || []) h = h.replace(new RegExp(`(^|[^\\w-])(${l.name.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')})(?![\\w-])`, 'g'), `$1<a class="link" data-obj="${esc(l.id)}" data-view="${esc(l.view)}" href="${H.linkHref(l)}">$2</a>`);
    return h.split(/\n{2,}/).map(p => `<p>${p.replace(/\n/g, '<br>')}</p>`).join('');
  }
  function answer(a) {
    if (a.error) return `<div class="e2a err"><p class="why">${esc(a.error)}</p></div>`;
    const foot = `<div class="e2foot">Model: ${esc(a.model || '–')}${a.knowledge_commit ? ` · knowledge ${esc(a.knowledge_commit.slice(0, 7))}` : ''} · asked by ${esc(a.record ? a.record.actor_human : '–')} · recorded in the action history</div>`;
    if (a.draft) {
      const note = a.source === 'fallback_unavailable' ? '<p class="why">Agent E2 is not available. Showing the fixed template.</p>'
        : a.source === 'fallback_vocabulary' ? '<p class="why">Agent E2 used words not allowed on this screen. Showing the fixed template.</p>' : '';
      return `<div class="e2a" data-draft>${note}<p>${esc(a.text)}</p>${foot}</div>`;
    }
    if (a.source === 'vocabulary') return `<div class="e2a" data-vocabulary><p class="why">Agent E2's answer used words that are not used on this screen. Escalate if you need the detail.</p>${foot}</div>`;
    if (a.source !== 'service') return '<div class="e2a"><p class="why">The Agent E2 service is not available.</p></div>';
    const comp = a.computed && a.computed.length ? `<div class="e2computed"><div class="lbl">Computed, not written by the model</div>${a.computed.map(x => `<span class="box">${esc(x)}</span>`).join('')}</div>` : '';
    const asks = a.type === 'clarify' && a.questions && a.questions.length ? `<div class="e2asks"><div class="lbl">Agent E2 asks</div><ul>${a.questions.map(q => `<li>${esc(q)}</li>`).join('')}</ul><p class="muted">Your next question is the reply.</p></div>` : '';
    const src = a.files_read && a.files_read.length ? `<div class="e2src"><div class="lbl">Sources</div>${a.files_read.map(f => `<span class="srcchip" title="Knowledge file">${esc(f)}</span>`).join('')}</div>` : '';
    return `<div class="e2a">${a.content ? linkify(a.content, a.links) : ''}${asks}${comp}${src}${H.answerExtra ? H.answerExtra(a) : ''}${foot}</div>`;
  }
  function render() {
    const box = $('e2'), c = S.ctx;
    if (!box || !c) return;
    const k = H.convKey(c), list = convs()[k] || [];
    const thread = list.map(m => `<div class="e2q"><div class="lbl">${esc(m.label)}</div>${esc(m.q)}</div>${answer(m.a)}`).join('');
    const sugg = !S.busy && !S.pending && (!list.length || list[list.length - 1].label !== H.label(c))
      ? `<div class="e2sugg" role="group" aria-label="Suggested questions">${H.suggestions(c).map((x, i) => `<button type="button" class="sugg" data-sugg="${i}">${esc(sText(x))}</button>`).join('')}</div>` : '';
    const kept = !S.busy && box.querySelector('#e2q') ? box.querySelector('#e2q').value : '';
    box.innerHTML = `<div class="e2head"><span class="e2mark big" aria-hidden="true">E2</span><div class="e2who"><h2 id="e2title">Agent E2</h2><div class="ctx" data-e2ctx>${esc(H.label(c))}</div></div>
        <button type="button" class="e2close" aria-label="Close Agent E2" title="Close (Esc)">×</button></div>
      ${S.up === false ? '<p class="why e2down">The Agent E2 service is not available.</p>' : ''}
      <div class="e2body" aria-live="polite">${thread || `<p class="muted">${esc(H.intro ? H.intro(c) : `Ask about ${c.show.about}. Agent E2 reads the knowledge base and the facts PCM sends; it explains, you decide.`)}</p>`}
        ${S.busy && S.waiting && S.waiting.key === k ? `<div class="e2q"><div class="lbl">${esc(S.waiting.label)}</div>${esc(S.waiting.q)}</div><div class="e2wait" role="status">${esc(S.waiting.note)} <span data-secs>0</span> s</div>` : ''}${sugg}</div>
      <form class="e2form" id="e2form"><label class="sr" for="e2q">Question for Agent E2</label><textarea id="e2q" rows="2" placeholder="${S.pending ? 'Your reply to Agent E2…' : 'Ask Agent E2…'}">${esc(kept)}</textarea>
        <button type="submit" class="act"${S.busy ? ' disabled' : ''}>Ask</button></form>`;
    const body = box.querySelector('.e2body'); body.scrollTop = body.scrollHeight;
  }
  function outline(el) {
    const root = H.root();
    root.querySelectorAll('.e2-asked').forEach(x => x.classList.remove('e2-asked'));
    const card = el && el.closest && el.closest(H.outline);
    if (card && root.contains(card)) card.classList.add('e2-asked');
  }
  function open(ctx, opener) {
    S.ctx = H.full(ctx); S.opener = opener || $('e2top');
    if (S.pending && S.pending.key !== H.convKey(S.ctx)) S.pending = null;
    outline(opener);
    const box = $('e2');
    S.open = true; box.hidden = false; document.body.classList.add('e2-open');
    const t = $('e2top'); if (t) t.setAttribute('aria-expanded', 'true');
    render(); if (H.onToggle) H.onToggle();
    $('e2q').focus({ preventScroll: true });
    // Re-checked on every open; only the note changes, so a question being typed is never lost.
    health().then(up => { const b = $('e2'), note = b.querySelector('.e2down');
      if (up && note) note.remove();
      if (!up && !note) b.querySelector('.e2head').insertAdjacentHTML('afterend', '<p class="why e2down">The Agent E2 service is not available.</p>'); });
  }
  function close() {
    const box = $('e2');
    S.open = false; box.hidden = true; document.body.classList.remove('e2-open');
    H.root().querySelectorAll('.e2-asked').forEach(x => x.classList.remove('e2-asked'));
    const t = $('e2top'); if (t) t.setAttribute('aria-expanded', 'false');
    if (H.onToggle) H.onToggle();
    const back = S.opener && document.contains(S.opener) ? S.opener : $('e2top');
    if (back) back.focus({ preventScroll: true });
  }
  // After a move the panel stays; its context becomes the new page's.
  function follow() {
    if (!S.open) return;
    S.ctx = H.full(H.pageCtx()); S.opener = $('e2top');
    render(); if (H.onToggle) H.onToggle();
  }
  async function ask(q, task) {
    q = (q || '').trim();
    if (!q || S.busy || !S.ctx) return;
    const c = S.ctx, k = H.convKey(c), label = H.label(c);
    const { show, ...context } = c;
    const body = { question: q, context };
    if (!task && S.pending && S.pending.key === k) body.turns = [S.pending.first, S.pending.questions.join('\n'), q];
    const list = convs()[k] || [];
    S.busy = true; S.started = Date.now();
    S.waiting = { q, label, key: k, note: task ? 'Agent E2 is drafting.' : 'Agent E2 is reading the knowledge base and the facts PCM sent.' };
    render(); $('e2q').focus({ preventScroll: true }); $('e2q').value = '';
    clearInterval(S.timer);
    S.timer = setInterval(() => { const s = document.querySelector('#e2 [data-secs]'); if (s) s.textContent = Math.round((Date.now() - S.started) / 1000); }, 1000);
    let r;
    try { r = task ? await H.draft(c, task) : await H.post('agent/ask', body); } catch (e) { r = { status: 0, body: { error: 'Could not reach PCM. Try again.' } }; }
    clearInterval(S.timer); S.busy = false; S.waiting = null;
    if (r.status !== 200) {
      saveConv(k, list); render();
      const ta = $('e2q'); if (ta && !task) ta.value = q;
      const b = document.querySelector('#e2 .e2body'); if (b) b.insertAdjacentHTML('beforeend', answer({ error: r.body.error || 'Agent E2 could not answer.' }));
      document.body.dataset.e2ask = 'error';
      return;
    }
    const a = task ? { ...r.body, draft: task } : r.body;
    S.pending = !task && a.type === 'clarify' && a.questions && a.questions.length && a.source === 'service' ? { key: k, first: body.turns ? body.turns[0] : q, questions: a.questions } : null;
    saveConv(k, [...list, { q, label, a }]);
    const keep = document.activeElement === document.body || (document.activeElement && document.activeElement.closest('#e2'));
    if (S.open && H.convKey(S.ctx) === k) render();
    if (keep && S.open) $('e2q').focus({ preventScroll: true });
    document.body.dataset.e2ask = a.source;
  }
  function init(hooks) {
    H = hooks;
    document.addEventListener('click', async e => {
      const m = e.target.closest('.e2mark[data-e2], #e2top');
      if (m) { e.preventDefault(); return open(m.id === 'e2top' ? H.pageCtx() : JSON.parse(m.dataset.e2), m); }
      if (e.target.closest('#e2 .e2close')) return close();
      const s = e.target.closest('#e2 [data-sugg]');
      if (s) { const x = H.suggestions(S.ctx)[Number(s.dataset.sugg)]; return typeof x === 'string' ? ask(x) : ask(x.q, x.draft); }
      const a = e.target.closest('#e2 [data-e2act]');
      if (a && H.onAction) H.onAction(a);
    });
    document.addEventListener('submit', e => { if (e.target.id === 'e2form') { e.preventDefault(); ask($('e2q').value); } });
    document.addEventListener('keydown', e => {
      if (e.target.id === 'e2q' && e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); ask(e.target.value); return; }
      if (e.key === 'Escape' && S.open && !(H.escBlocked && H.escBlocked())) { e.preventDefault(); close(); }
    });
  }
  return { init, mark, topMark, health, open, close, follow, state: S };
})();
