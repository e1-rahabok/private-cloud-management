// Demo switcher. Thin bar at the top of every page, on by default; PCM_DEMO_SWITCHER=0 turns it off.
// Demo scaffolding, not part of PCM: the real product is one URL per person. The six URLs stay as they are.
'use strict';
(() => {
  const NOW = '2026-10-19T10:05:00+08:00';
  const qs = new URLSearchParams(location.search);
  const now = qs.get('now') || NOW;
  // Sequence follows demo/README.md.
  const ROLES = [
    { name: '1. CIO', path: '/exec', match: p => p === '/exec',
      about: 'Gets three plain answers: is it up, is it fast, is it safe. Today "safe" is red and Singapore must order by 18 Nov 2026.' },
    { name: '2. NOC wall', path: '/noc/wall', extra: '&rotate=8', match: p => p === '/noc/wall',
      about: 'A TV nobody touches. Tells the room what is wrong in five seconds. Today "Is it fast?" is red: FR-S-02 is at 22, was 94 an hour ago.' },
    { name: '3. NOC L1 engineer', path: '/noc/alert/inc-fr-s-02', match: p => p.startsWith('/noc'),
      about: 'Follows the SOP on one page. Can stop new VMs on FR-S-02, cannot limit a production VM, then escalates to Platform with the evidence.' },
    { name: '4. L2 platform engineer', path: '/l2', match: p => p.startsWith('/l2'),
      about: 'Monitors the whole estate top down, troubleshoots cases (complaints, L1 escalations, findings) layer by layer, and closes each only with a detection. Improves what is not broken.' },
    { name: '5. Capacity planner', path: '/capacity', match: p => p.startsWith('/capacity'),
      about: 'Sees when each cluster group runs out and why the date moved. FR-Silver is full now; reclaiming waste avoids $3.6M.' },
    { name: '6. Docs reader (auditor)', path: '/docs/threshold/th-cluster-perf-red', match: p => p.startsWith('/docs'),
      about: 'Follows any number to its definition, owner and history. "Cluster Performance below 50" is used on the wall, the incident and capacity.' },
  ];
  const href = r => `${r.path}?now=${encodeURIComponent(now)}${r.extra || ''}`;
  let cur = ROLES.findIndex(r => r.match(location.pathname.replace(/\/$/, '') || '/exec'));
  if (cur < 0) cur = 0;

  const css = document.createElement('style');
  css.textContent = `
    #demo-switcher{position:fixed;top:0;left:0;right:0;height:44px;z-index:2147483647;box-sizing:border-box;display:flex;align-items:center;gap:14px;padding:0 16px;
      background:#D90429;color:#fff;font:500 13px/1.3 Manrope,system-ui,sans-serif;border-bottom:3px solid #fff}
    #demo-switcher b{font-weight:800;letter-spacing:.04em;text-transform:uppercase;font-size:11px;color:#fff;background:#7A0016;padding:4px 8px;border-radius:4px;white-space:nowrap}
    #demo-switcher select{font:600 13px Manrope,system-ui,sans-serif;color:#0B1B2B;background:#fff;border:0;border-radius:6px;padding:5px 8px;min-width:200px}
    #demo-switcher span{flex:1;min-width:0;overflow:hidden;display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;font-weight:600}
    html{padding-top:44px}
    body.wall{height:calc(100vh - 44px)}
    @media (max-width:700px){#demo-switcher{height:auto;min-height:44px;flex-wrap:wrap;padding:6px 12px}html{padding-top:84px}}`;
  document.head.appendChild(css);

  const bar = document.createElement('div');
  bar.id = 'demo-switcher';
  bar.setAttribute('role', 'region');
  bar.setAttribute('aria-label', 'Demo role switcher');
  const label = document.createElement('b'); label.textContent = 'Demo control · not part of PCM';
  const sel = document.createElement('select'); sel.setAttribute('aria-label', 'Switch role');
  ROLES.forEach((r, i) => { const o = document.createElement('option'); o.value = String(i); o.textContent = r.name; if (i === cur) o.selected = true; sel.appendChild(o); });
  const about = document.createElement('span'); about.textContent = ROLES[cur].about;
  sel.addEventListener('change', () => { location.href = href(ROLES[+sel.value]); });
  bar.append(label, sel, about);
  document.body.prepend(bar);
})();
