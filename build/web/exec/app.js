// GENERATED from spec/workspaces/executive/page.md. Do not edit by hand (D-070).
// Pages never compute numbers: they show API values and their metadata (spec README, rule 1).
'use strict';

const qs = new URLSearchParams(location.search);
const passthrough = ['now', 'enable'].filter(k => qs.get(k)).map(k => `${k}=${encodeURIComponent(qs.get(k))}`).join('&');
const url = (p, extra = '') => `/api/exec/${p}${passthrough || extra ? '?' : ''}${[passthrough, extra].filter(Boolean).join('&')}`;
const getJSON = p => fetch(url(p)).then(r => { if (!r.ok) throw new Error(r.status); return r.json(); });

const LABEL = { up: 'Is it up?', fast: 'Is it fast?', safe: 'Is it safe?' };
const CHIP = { green: 'Good', amber: 'Watch', red: 'Act now', in_plan: 'In the plan', no_data: 'No data',
  on_track: 'On track', at_risk: 'At risk', missed: 'Missed' };
const CHIP_CLASS = { on_track: 'green', at_risk: 'amber', missed: 'red' };
const RES = { compute: 'computing power', memory: 'working memory', storage: 'storage' };
const SAFE_LABEL = { certificates_expiring: 'Security certificates expiring soon',
  ssh_or_shell_enabled: 'Servers with remote admin access left open',
  lockdown_off: 'Servers without the required access lock', root_logins: 'Logins with the highest admin rights' };

const $ = id => document.getElementById(id);
const esc = s => String(s).replace(/[&<>"]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
const chip = st => `<span class="chip ${CHIP_CLASS[st] || st}">${CHIP[st]}</span>`;
const fmtInt = n => Math.round(n).toLocaleString('en-US');
const money = n => n >= 1e6 ? `$${(n / 1e6).toFixed(1)}M` : `$${fmtInt(n)}`;
const fmtDate = iso => new Date(iso + 'T00:00:00').toLocaleDateString('en-GB', { day: 'numeric', month: 'long', year: 'numeric' });
const fmtTime = iso => new Date(iso).toLocaleTimeString('en-GB', { hour: '2-digit', minute: '2-digit' });
// A stale value is never shown as a number (D-041).
const show = (v, f = x => x) => (v.meta && v.meta.stale) || v.value === null ? '<span class="chip no_data">No data</span>' : f(v.value);

function storage(tb) { return tb >= 1000 ? `${(tb / 1000).toFixed(1)} PB` : `${fmtInt(tb)} TB`; }

// ---------------------------------------------------------------- panels: one open per section (PG-8)
function openPanel(panelId, btn, html) {
  const panel = $(panelId);
  const wasOpen = btn.getAttribute('aria-expanded') === 'true';
  document.querySelectorAll(`[data-panel="${panelId}"]`).forEach(b => b.setAttribute('aria-expanded', 'false'));
  if (wasOpen) { panel.hidden = true; panel.innerHTML = ''; return; }
  btn.setAttribute('aria-expanded', 'true');
  panel.innerHTML = html;
  panel.hidden = false;
  panel.querySelector('button.close').addEventListener('click', () => {
    panel.hidden = true; panel.innerHTML = '';
    btn.setAttribute('aria-expanded', 'false'); btn.focus();
  });
}
const panelHead = title => `<div class="panel-head"><h3>${esc(title)}</h3><button class="close" type="button">Close</button></div>`;

// ---------------------------------------------------------------- charts (custom SVG)
function lineSVG(points, cls, target, h = 48) {
  const vals = points.map(p => p.v).filter(v => v !== null);
  if (!vals.length) return '';
  let lo = Math.min(...vals, target ?? Infinity), hi = Math.max(...vals, target ?? -Infinity);
  if (hi - lo < 1e-6) { hi += 1; lo -= 1; }
  const pad = (hi - lo) * 0.15; lo -= pad; hi += pad;
  const W = 300, x = i => (i / (points.length - 1)) * W, y = v => h - ((v - lo) / (hi - lo)) * h;
  const d = points.map((p, i) => `${i ? 'L' : 'M'}${x(i).toFixed(1)},${y(p.v).toFixed(1)}`).join('');
  const t = target != null ? `<line x1="0" x2="${W}" y1="${y(target)}" y2="${y(target)}" stroke="#B45309" stroke-dasharray="5 4" stroke-width="1.5"/>` : '';
  return `<svg class="${cls}" viewBox="0 0 ${W} ${h}" preserveAspectRatio="none" aria-hidden="true">${t}<path d="${d}" fill="none" stroke="#0E9F8E" stroke-width="2"/></svg>`;
}

function towerSVG(loc, maxCores) {
  const slabs = Math.max(2, Math.round(loc.compute_cores.value / 1500));
  const lit = loc.stale ? 0 : Math.round(slabs * (loc.in_use_percent.value || 0) / 100);
  const H = 300, sh = 11, w = 70, cx = 50;
  let g = '';
  for (let i = 0; i < slabs; i++) {
    const yb = H - 20 - i * (sh + 3);
    const on = i < lit;
    const front = loc.stale ? '#2A3B4E' : (on ? '#2CC4AE' : '#2A3F57');
    const top = loc.stale ? '#3A4C60' : (on ? '#8EF5E3' : '#3E5C79');
    const stroke = loc.stale ? ' stroke="#B8C2CC" stroke-width="1"' : '';
    g += `<polygon points="${cx - w / 2},${yb} ${cx},${yb + 8} ${cx},${yb + 8 - sh} ${cx - w / 2},${yb - sh}" fill="${front}"${stroke}/>`;
    g += `<polygon points="${cx},${yb + 8} ${cx + w / 2},${yb} ${cx + w / 2},${yb - sh} ${cx},${yb + 8 - sh}" fill="${front}" opacity=".8"${stroke}/>`;
    if (i === slabs - 1) g += `<polygon points="${cx - w / 2},${yb - sh} ${cx},${yb - sh - 8} ${cx + w / 2},${yb - sh} ${cx},${yb + 8 - sh}" fill="${top}"${stroke}/>`;
  }
  return `<svg viewBox="0 0 100 ${H}" aria-hidden="true">${g}</svg>`;
}

// ---------------------------------------------------------------- sections
function renderHeader(s) {
  const t = `${new Date(s.updated_at).toLocaleDateString('en-GB', { weekday: 'long', day: 'numeric', month: 'long', year: 'numeric' })} · Updated ${fmtTime(s.updated_at)}`;
  $('updated').innerHTML = s.stale_locations.length
    ? `${esc(t)} · <span class="warn">Some data is out of date</span> (oldest ${fmtTime(s.oldest_data_at)})`
    : esc(t);
}

function renderScale(s) {
  const sc = s.scale;
  $('eyebrow').textContent = `Our private cloud · ${sc.locations.length} locations`;
  const m = (label, v, unit, use) => `<div class="meter"><div class="meter-head"><span>${label}</span><span class="use">${show(use, x => `${x}% in use`)}</span></div>
    <div class="meter-value">${v} <span class="meter-unit">${unit}</span></div><div class="bar"><span style="width:${use.value || 0}%"></span></div></div>`;
  $('meters').innerHTML = m('Computing power', fmtInt(sc.compute_cores.value), 'processor cores', sc.in_use_percent.compute)
    + m('Working memory', fmtInt(sc.memory_tb.value), 'TB', sc.in_use_percent.memory)
    + m('Storage', storage(sc.storage_tb.value).split(' ')[0], storage(sc.storage_tb.value).split(' ')[1], sc.in_use_percent.storage);
  const max = Math.max(...sc.locations.map(l => l.compute_cores.value));
  $('towers').innerHTML = sc.locations.map(l => `<button type="button" class="tower${l.stale ? ' stale' : ''}" data-loc="${l.id}" data-panel="location-panel" aria-pressed="false" aria-expanded="false">
      ${towerSVG(l, max)}<div class="t-name">${esc(l.name)}</div>
      <div class="t-share">${l.share_percent.value}% of total</div>${l.stale ? '<span class="t-nodata">No data</span>' : ''}</button>`).join('');
  document.querySelectorAll('.tower').forEach(b => b.addEventListener('click', () => selectTower(b)));
}

async function selectTower(btn) {
  const pressed = btn.getAttribute('aria-pressed') === 'true';
  document.querySelectorAll('.tower').forEach(t => { t.setAttribute('aria-pressed', 'false'); t.classList.remove('dim'); });
  if (!pressed) {
    btn.setAttribute('aria-pressed', 'true');
    document.querySelectorAll('.tower').forEach(t => { if (t !== btn) t.classList.add('dim'); });
  }
  const d = await getJSON(`locations/${btn.dataset.loc}`);
  const L = d.location, dec = L.decision;
  const rows = Object.entries(d.in_use_by_resource).map(([r, v]) => `<tr><td>${RES[r][0].toUpperCase() + RES[r].slice(1)}</td><td>${show(v, x => `${x}% in use`)}</td></tr>`).join('');
  const html = panelHead(L.name) + `<table><tbody>
      <tr><td>Computing power</td><td>${fmtInt(L.compute_cores.value)} processor cores</td></tr>
      <tr><td>Working memory</td><td>${fmtInt(d.memory_tb.value)} TB</td></tr>
      <tr><td>Storage</td><td>${storage(d.storage_tb.value)}</td></tr>${rows}
      <tr><td>Health</td><td>${['up', 'fast', 'safe'].map(q => `${LABEL[q]} ${chip(d.health[q])}`).join(' &nbsp; ')}</td></tr>
      <tr><td>Order by</td><td>${dec.date.value ? `${fmtDate(dec.date.value)} (${RES[dec.resource]})` : ''} ${chip(dec.date.status)}</td></tr>
    </tbody></table>`;
  openPanel('location-panel', btn, html);
  if (btn.getAttribute('aria-expanded') !== 'true') document.querySelectorAll('.tower').forEach(t => { t.setAttribute('aria-pressed', 'false'); t.classList.remove('dim'); });
}

function renderHealth(s) {
  $('health-cards').innerHTML = ['up', 'fast', 'safe'].map(q => {
    const c = s.health[q], h = c.headline;
    const head = q === 'safe' ? show(h, x => `${x} <small>open findings</small>`) : show(h, x => `${x.toFixed(2)}%`);
    return `<article class="card"><h3>${LABEL[q]} ${chip(h.status)}</h3><div class="headline">${head}</div>
      ${h.meta.stale ? '' : lineSVG(c.sparkline_7d.points, 'spark')}
      <p class="sentence">${esc(c.sentence)}</p>
      <button type="button" class="more" data-q="${q}" data-panel="health-panel" aria-expanded="false">See detail</button></article>`;
  }).join('');
  document.querySelectorAll('#health-cards button.more').forEach(b => b.addEventListener('click', () => healthPanel(b, 7, false)));
}

async function healthPanel(btn, days, refresh) {
  const q = btn.dataset.q;
  const detail = await fetch(url(`health/${q}`, `window_days=${days}`)).then(r => r.json());
  const names = { sg: 'Singapore', va: 'Virginia', fr: 'Frankfurt', tk: 'Tokyo', ld: 'London' };
  let body = '';
  if (q === 'safe') {
    const s = window.__summary.health.safe.safe_counts;
    body += `<table><tbody>${Object.entries(s).map(([k, v]) => `<tr><td>${SAFE_LABEL[k]}</td><td>${show(v)}</td></tr>`).join('')}</tbody></table>`;
  } else {
    body += `<div class="switch" role="group" aria-label="Window"><button type="button" data-days="7" aria-pressed="${days === 7}">7 days</button><button type="button" data-days="30" aria-pressed="${days === 30}">30 days</button></div>`;
    body += lineSVG(detail.series.points, 'chart', detail.target ? detail.target.value : null, 220);
    body += `<p class="muted">Dashed line: target ${detail.target.value}%.</p>`;
  }
  body += `<table><thead><tr><th>Location</th><th>${q === 'safe' ? 'Open findings' : 'Value'}</th></tr></thead><tbody>${detail.by_location.map(r => `<tr><td>${names[r.location]}</td><td>${show(r.value, x => q === 'safe' ? x : `${x}%`)}</td></tr>`).join('')}</tbody></table>`;
  if (detail.events.length) body += `<ul class="events">${detail.events.map(e => `<li>${esc(e.text)}</li>`).join('')}</ul>`;
  else body += `<p class="muted">No notable events in this period.</p>`;
  if (refresh) btn.setAttribute('aria-expanded', 'false');
  openPanel('health-panel', btn, panelHead(LABEL[q]) + body);
  document.querySelectorAll('#health-panel .switch button').forEach(sb => sb.addEventListener('click', () => healthPanel(btn, Number(sb.dataset.days), true)));
}

function renderGrow(s) {
  const r = s.room_to_grow, e = r.estate_decision, names = Object.fromEntries(s.scale.locations.map(l => [l.id, l.name]));
  const when = e.date.value ? `Order more ${RES[e.resource]} for ${names[e.location]} by ${fmtDate(e.date.value)}.` : 'No data';
  $('grow-body').innerHTML = `<div class="grow-head"><div><div class="muted">Earliest order date</div><div class="headline">${esc(when)}</div>
      <p class="sentence muted">${e.date.days_from_now !== null ? `${e.date.days_from_now} days from now. ` : ''}Next purchase round closes on ${fmtDate(r.next_round_closes_on.value)}.</p></div>
      <div>${chip(e.date.status)}</div>
      <button type="button" class="more" data-panel="grow-panel" aria-expanded="false">See by location</button></div>`;
  $('grow-body').querySelector('button.more').addEventListener('click', async ev => {
    const btn = ev.currentTarget, d = await getJSON('capacity');
    const rows = d.locations.map(x => `<tr><td>${names[x.location]}</td><td>${RES[x.resource]}</td><td>${x.date.value ? fmtDate(x.date.value) : ''}</td><td>${x.date.days_from_now ?? ''}</td><td>${chip(x.date.status)}</td></tr>`).join('');
    openPanel('grow-panel', btn, panelHead('Order dates by location') + `<table><thead><tr><th>Location</th><th>Runs short of</th><th>Order by</th><th>Days from now</th><th>Status</th></tr></thead><tbody>${rows}</tbody></table>`);
  });
}

function renderValue(s) {
  const v = s.value;
  const diff = v.public_cloud_difference_percent.value;
  const cmp = diff >= 0 ? `${diff}% less than public cloud` : `${-diff}% more than public cloud`;
  $('value-cards').innerHTML = `
    <article class="card"><h3>Cost</h3><div class="headline">${show(v.cost_annual, money)} <small>per year</small></div>
      <p class="sentence">Over ${5} years: ${show(v.tco, money)}, ${esc(cmp)} for the same estate.</p>
      <p class="sentence">Cost avoided this year: <strong>${show(v.cost_avoided_ytd, money)}</strong></p>
      <button type="button" class="more" data-card="cost" data-panel="value-panel" aria-expanded="false">See detail</button></article>
    <article class="card"><h3>Site recovery ${chip(v.site_recovery_status)}</h3>
      <p class="sentence">${esc(v.site_recovery_summary)}</p>
      <button type="button" class="more" data-card="site_recovery" data-panel="value-panel" aria-expanded="false">See detail</button></article>
    <article class="card"><h3>Speed</h3><div class="headline">${show(v.delivery_hours, x => `${x} hours`)}</div>
      <p class="sentence">To deliver a new business environment. A year ago it took ${show(v.delivery_hours_year_ago, x => `${Math.round(x / 24)} days`)}.</p>
      <button type="button" class="more" data-card="speed" data-panel="value-panel" aria-expanded="false">See detail</button></article>`;
  document.querySelectorAll('#value-cards button.more').forEach(b => b.addEventListener('click', () => valuePanel(b)));
}

async function valuePanel(btn) {
  const card = btn.dataset.card, d = await getJSON(`value/${card}`);
  const names = { sg: 'Singapore', va: 'Virginia', fr: 'Frankfurt', tk: 'Tokyo', ld: 'London' };
  let html;
  if (card === 'cost') {
    const c = d.cost;
    html = panelHead('Cost') + `<table><tbody>
      <tr><td>Product: hardware and software</td><td>${money(c.product.value)} per year</td></tr>
      <tr><td>Service: data centre and managed services</td><td>${money(c.service.value)} per year</td></tr>
      <tr><td>People: the teams who design, build and run it</td><td>${money(c.people.value)} per year</td></tr>
      <tr><td>Total over 5 years</td><td>${money(c.tco.value)}</td></tr>
      <tr><td>Public cloud for the same estate, 5 years</td><td>${money(c.public_cloud_estimate.value)} (estimate dated ${fmtDate(c.public_cloud_estimate.meta.as_of.slice(0, 10))})</td></tr>
      <tr><td>Cost avoided this year</td><td>${money(c.cost_avoided_ytd.value)}</td></tr>
      <tr><td>Could still avoid in the next purchase round</td><td>${money(c.cost_avoidable_next_round.value)}</td></tr>
      </tbody></table><p class="foot-note">Cost avoided means purchases put off by freeing unused capacity, valued at today's price.</p>`;
  } else if (card === 'site_recovery') {
    html = panelHead('Site recovery') + `<table><thead><tr><th>Location</th><th>Last test</th><th>Recovery time</th><th>Virtual machines tested</th><th>Status</th></tr></thead><tbody>
      ${d.site_recovery.map(r => `<tr><td>${names[r.location]}</td><td>${fmtDate(r.last_test_at.value)}</td><td>${r.recovery_minutes.value} min (target ${r.target_minutes.value})</td><td>${r.share_tested_percent.value}%</td><td>${chip(r.status)}</td></tr>`).join('')}
      </tbody></table><p class="foot-note">Shows site recovery tests only. Backups are not included.</p>`;
  } else {
    html = panelHead('Speed') + lineSVG(d.speed.series_12m.points, 'chart', null, 220) + `<p class="muted">Hours to deliver a new business environment, last 12 months.</p>`;
  }
  openPanel('value-panel', btn, html);
}

function renderGoals(s) {
  $('goals-body').innerHTML = s.goals.length ? s.goals.slice(0, 6).map(g => `<div class="goal-row"><div><strong>${esc(g.title)}</strong></div>
      <div class="muted">${show(g.current)} projected · target ${g.direction === 'at_most' ? 'at most' : 'at least'} ${g.target}</div><div>${chip(g.status)}</div></div>`).join('')
    : '<p class="muted">No goals set for this year. They are set in the monthly review.</p>';
}

async function main() {
  try {
    const s = await getJSON('summary');
    window.__summary = s;
    renderHeader(s); renderScale(s); renderHealth(s); renderGrow(s); renderValue(s); renderGoals(s);
    document.body.dataset.ready = '1';
  } catch (e) {
    $('updated').innerHTML = '<span class="error">Could not load data. Try again later.</span>';
    document.body.dataset.ready = 'error';
  }
}
main();
