// GENERATED from spec/workspaces/noc/wall.md. Do not edit by hand (D-070).
'use strict';
let data = null, idx = 0, timer = null;
const fixed = QS.get('screen');                       // one display per screen: no rotation (D-041)
const rotateOverride = Number(QS.get('rotate')) || 0;  // prototype and test only

function tileHead(t, body) {
  if (t.status === 'no_data') return `<div class="tile no_data"><h3>${esc(t.name)}</h3><span class="nodata">No data</span><div class="line">Last good data ${fmtTime(t.last_good)}</div></div>`;
  return `<div class="tile ${t.status}"><h3>${esc(t.name)}</h3>${body}</div>`;
}

const RENDER = {
  changed: s => `<div class="tiles">${s.tiles.map(t => tileHead(t, `<div class="rows">${Object.entries(t.rows || {}).map(([k, r]) =>
      `<div class="${r.status}"><span>${CHANGE[k]}</span><span>${r.count}${r.status === 'red' ? ` · about ${r.expected} expected` : ''}</span></div>`).join('')}</div>`)).join('')}</div>`,
  up: s => `<div class="tiles">${s.tiles.map(t => tileHead(t, `<div class="big">${t.total ?? ''}</div><div class="line">${t.total ? '' : 'Nothing down'}</div>`)).join('')}</div>`
      + (s.no_data_sources || []).map(n => `<div class="notgreen"><div class="r">${chip('red')}<strong>No data from ${esc(n.region)}'s VCF Operations since ${fmtTime(n.last_good)}</strong></div></div>`).join(''),
  fast: s => {
    const groups = {};
    s.tiles.forEach(t => { (groups[t.location] = groups[t.location] || { name: t.name, cells: [] }).cells.push(t); });
    const notGreen = s.tiles.filter(t => t.status !== 'green' && t.status !== 'no_data').sort((a, b) => a.score - b.score);
    return `<div class="heat">${Object.values(groups).map(g => `<div class="grp"><h3>${esc(g.name)}</h3><div class="cells">${g.cells.map(c =>
        c.status === 'no_data' ? `<div class="cell no_data">No data</div>` : `<div class="cell ${c.status}">${Math.round(c.score)}<span>${esc(c.cluster)}</span></div>`).join('')}</div></div>`).join('')}</div>`
      + `<div class="notgreen">${notGreen.length ? notGreen.map(c => `<div class="r">${chip(c.status)}<strong>${esc(c.cluster)}</strong><span>${Math.round(c.score)} out of 100</span><span class="line">was ${Math.round(c.trend[0].v)} an hour ago</span></div>`).join('') : '<div class="line">Every cluster is serving its VMs well.</div>'}</div>`;
  },
  safe: s => `<div class="tiles">${s.tiles.map(t => tileHead(t, `<div class="rows">${Object.entries(t.findings || {}).map(([k, v]) =>
      `<div class="${v ? 'red' : ''}"><span>${SAFE[k]}</span><span>${v}</span></div>`).join('')}</div>`)).join('')}</div>`
      + `<div class="line">Certificates expiring within 30 days: ${s.risk_certificates}</div>`,
  set_right: s => `<div class="tiles">${s.tiles.map(t => tileHead(t, `<div class="big">${t.count}</div><div class="line">${t.count ? '' : 'No risky changes in the last hour'}</div>`)).join('')}</div>`,
};

function order() {
  if (fixed) return [fixed];
  return data.pins.length ? data.pins : SCREENS;      // red not acknowledged pins the rotation (D-041)
}

function draw() {
  if (!data) return;
  const list = order();
  const name = list[idx % list.length];
  document.getElementById('title').textContent = LABEL[name];
  document.getElementById('time').textContent = `Updated ${fmtTime(data.updated_at)}`;
  document.getElementById('banner').innerHTML = data.pcm_ok ? '' : '<div class="banner">PCM has no data. Use the VCF Operations screens.</div>';
  document.getElementById('strip').innerHTML = data.strip.map(c =>
    `<div class="s ${c.status}${c.screen === name ? ' current' : ''}" data-screen="${c.screen}"><span>${LABEL[c.screen]}</span><small>${c.in_hand ? 'In hand' : STATUS[c.status]}</small></div>`).join('');
  document.getElementById('screen').innerHTML = RENDER[name](data.screens[name]);
  document.body.dataset.screen = name;
}

async function refresh() {
  try {
    const prevPins = data ? data.pins.join() : null;
    data = await getJSON('wall');
    if (prevPins !== null && prevPins !== data.pins.join()) idx = 0;
    document.body.dataset.ready = '1';
  } catch (e) {
    data = data ? { ...data, pcm_ok: false } : null;
    if (!data) document.getElementById('title').textContent = 'PCM has no data. Use the VCF Operations screens.';
  }
  draw();
}

async function main() {
  await refresh();
  const rot = (rotateOverride || (data && data.rotation_seconds) || 60) * 1000;
  const ref = (Number(QS.get('refresh')) || (data && data.refresh_seconds) || 60) * 1000;
  setInterval(() => { idx += 1; draw(); }, rot);
  setInterval(refresh, ref);
}
main();
