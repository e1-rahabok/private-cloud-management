// GENERATED from pcm/noc/spec/pages/wall.md. Do not edit by hand (D-070).
'use strict';
let data = null, idx = 0;
const fixed = QS.get('screen');                       // one display per screen: no rotation (D-041)
const rotateOverride = Number(QS.get('rotate')) || 0;  // prototype and test only

function tileHead(t, body) {
  if (t.status === 'no_data') return `<div class="tile no_data"><h3>${esc(t.name)}</h3><span class="nodata">No data</span><div class="line">Last good data ${fmtTime(t.last_good)}</div></div>`;
  return `<div class="tile ${t.status}"><h3>${esc(t.name)}</h3>${body}</div>`;
}
const row = (k, v, cls = '', note = '') => `<div class="row ${cls}"><span class="k">${k}</span><span class="v">${v}</span>${note ? `<small>${note}</small>` : ''}</div>`;

// Overall performance, last hour: the average of all clusters and the lowest one (noc.performance_trend).
function trendSVG(tr, w, h) {
  const pts = tr.points;
  if (!pts.length) return `<div class="nodata">No data</div>`;
  const m = { l: 44, r: 150, t: 12, b: 30 }, iw = w - m.l - m.r, ih = h - m.t - m.b;
  const x = i => m.l + iw * i / (pts.length - 1), y = v => m.t + ih * (1 - v / 100);
  const bands = [[75, 100, '#5EEAD4'], [50, 75, '#F2D45B'], [25, 50, '#F2A93B'], [0, 25, '#F26B5B']]
    .map(([lo, hi, c]) => `<rect x="${m.l}" y="${y(hi)}" width="${iw}" height="${y(lo) - y(hi)}" fill="${c}" opacity=".07"/>`).join('');
  const grid = [0, 25, 50, 75, 100].map(v => `<line x1="${m.l}" x2="${m.l + iw}" y1="${y(v)}" y2="${y(v)}" stroke="#2A3F57"/><text x="${m.l - 10}" y="${y(v) + 6}" text-anchor="end" class="ax">${v}</text>`).join('');
  const xl = [0, 3, 6, 9, 12].filter(i => i < pts.length).map(i => `<text x="${x(i)}" y="${h - 6}" text-anchor="middle" class="ax">${fmtHM(pts[i].t)}</text>`).join('');
  const line = (key, c, wd) => `<polyline fill="none" stroke="${c}" stroke-width="${wd}" stroke-linejoin="round" points="${pts.map((p, i) => `${x(i).toFixed(1)},${y(p[key]).toFixed(1)}`).join(' ')}"/>`;
  const last = pts[pts.length - 1];
  const end = (key, c, text, dy = 0) => `<circle cx="${x(pts.length - 1)}" cy="${y(last[key])}" r="6" fill="${c}"/><text x="${x(pts.length - 1) + 14}" y="${y(last[key]) + 7 + dy}" class="end" fill="${c}">${text}</text>`;
  const clash = Math.abs(y(last.average) - y(last.lowest)) < 26;
  return `<svg width="${w}" height="${h}" viewBox="0 0 ${w} ${h}" role="img" aria-label="Performance over the last hour">${bands}${grid}${xl}${line('average', '#5EEAD4', 4)}${line('lowest', '#F2A93B', 4)}`
    + end('average', '#5EEAD4', Math.round(last.average)) + end('lowest', '#F2A93B', `${Math.round(last.lowest)} ${esc(last.lowest_cluster)}`, clash ? 16 : 0) + `</svg>`;
}

const RENDER = {
  changed: s => `<div class="tiles">${s.tiles.map(t => tileHead(t, `<div class="rows">${Object.entries(t.rows || {}).map(([k, r]) =>
      row(CHANGE[k], r.count, r.status === 'red' ? 'red' : '', r.status === 'red' ? `About ${r.expected} expected` : '')).join('')}</div>`)).join('')}</div>`,
  up: s => `<div class="tiles">${s.tiles.map(t => tileHead(t, `<div class="big">${t.total ?? ''}</div><div class="line">${t.total ? '' : 'Nothing down'}</div>`)).join('')}</div>`
      + (s.no_data_sources || []).map(n => `<div class="notgreen"><div class="r"><span class="dot red"></span><strong>No data from ${esc(n.region)}'s VCF Operations since ${fmtTime(n.last_good)}</strong></div></div>`).join(''),
  fast: s => {
    const groups = {};
    s.tiles.forEach(t => { (groups[t.location] = groups[t.location] || { name: t.name, cells: [] }).cells.push(t); });
    const notGreen = s.tiles.filter(t => t.status !== 'green' && t.status !== 'no_data').sort((a, b) => a.score - b.score);
    return `<div class="heat">${Object.values(groups).map(g => `<div class="grp"><h3>${esc(g.name)}</h3><div class="cells">${g.cells.map(c =>
        c.status === 'no_data' ? `<div class="cell no_data">No data</div>` : `<div class="cell ${c.status}"><b>${Math.round(c.score)}</b><span>${esc(c.cluster)}</span></div>`).join('')}</div></div>`).join('')}</div>`
      + `<div class="perf-low"><div class="panel-w"><h3>Overall performance, last hour<span class="legend"><i style="background:#5EEAD4"></i>Average of all clusters<i style="background:#F2A93B"></i>Lowest cluster</span></h3><div id="chart" class="chart"></div></div>`
      + `<div class="panel-w"><h3>Below normal</h3>${notGreen.length ? notGreen.map(c => `<div class="r ${c.status}"><span class="dot ${c.status}"></span><strong>${esc(c.cluster)}</strong><span class="sc">${Math.round(c.score)} out of 100</span><span class="line">was ${Math.round(c.trend[0].v)} an hour ago</span></div>`).join('') : '<div class="line">Every cluster is serving its VMs well.</div>'}</div></div>`;
  },
  safe: s => `<div class="tiles">${s.tiles.map(t => tileHead(t, `<div class="rows">${Object.entries(t.findings || {}).map(([k, v]) =>
      row(SAFE[k], v, v ? 'red' : '')).join('')}</div>`)).join('')}</div>`
      + `<div class="line">Certificates expiring within 30 days: ${s.risk_certificates}</div>`,
  set_right: s => `<div class="tiles">${s.tiles.map(t => tileHead(t, `<div class="big">${t.count}</div><div class="line">${t.count ? '' : 'No risky changes in the last hour'}</div>`)).join('')}</div>`,
  capacity: s => `<div class="tiles">${s.tiles.map(t => tileHead(t, !t.in_use ? '' : `<div class="rows">${['compute', 'memory', 'storage'].map(r =>
      `<div class="row"><span class="k">${RES[r]}</span><span class="v">${Math.round(t.in_use[r])}%</span><i class="bar"><b style="width:${Math.min(100, t.in_use[r])}%"></b></i></div>`).join('')}</div>`
      + `<div class="remain"><span class="k">Time remaining</span><span class="v">${t.days_remaining === null ? 'Beyond 13 months' : `${num(t.days_remaining)} days`}</span></div>`)).join('')}</div>`
      + `<div class="line">In use is the share of usable capacity. Time remaining is for the tightest cluster group.</div>`,
};

function order() {
  if (fixed) return [fixed];
  return data.pins.length ? data.pins : SCREENS;      // red not acknowledged pins the rotation (D-041)
}

function counts() {
  const sc = data.scale || {};
  const one = (v, label) => `<div class="count"><span class="n">${v === null || v === undefined ? 'No data' : num(v)}</span><span class="l">${label}</span></div>`;
  const left = (sc.locations_without_data || []).length ? `<div class="count-note">Excludes ${sc.locations_without_data.map(esc).join(', ')}: no data</div>` : '';
  return one(sc.vms_running, 'Running VMs') + one(sc.hosts_running, 'Running ESXi hosts') + left;
}

function tab(c, name) {
  const note = c.in_hand ? 'In hand' : c.status === 'no_data' ? 'No data' : c.open_incidents ? `${c.open_incidents} open` : '';
  return `<div class="s${c.screen === name ? ' current' : ''}" data-screen="${c.screen}" role="tab" aria-selected="${c.screen === name}"><span>${LABEL[c.screen]}</span>${note ? `<small>${note}</small>` : ''}</div>`;
}

function draw() {
  if (!data) return;
  const list = order();
  const name = list[idx % list.length];
  document.getElementById('time').textContent = `Updated ${fmtTime(data.updated_at)}`;
  document.getElementById('counts').innerHTML = counts();
  document.getElementById('banner').innerHTML = data.pcm_ok ? '' : '<div class="banner">PCM has no data. Use the VCF Operations screens.</div>';
  document.getElementById('strip').innerHTML = data.strip.map(c => tab(c, name)).join('');
  document.getElementById('screen').innerHTML = RENDER[name](data.screens[name]);
  const chart = document.getElementById('chart');
  if (chart) { const r = chart.getBoundingClientRect(); chart.innerHTML = trendSVG(data.screens.fast.trend, Math.max(400, Math.floor(r.width)), Math.max(140, Math.floor(r.height))); }
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
    if (!data) document.getElementById('banner').innerHTML = '<div class="banner">PCM has no data. Use the VCF Operations screens.</div>';
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
