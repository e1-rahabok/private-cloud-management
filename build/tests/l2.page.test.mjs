// Page tests LPG-2 to LPG-13 for /l2 (Monitor, Troubleshoot, Improve, Rules, Calendar), in a real browser.
// GENERATED from spec/tests/l2.yaml. Do not edit by hand (D-070).
// Run from the repository root:  node build/tests/l2.page.test.mjs
import { spawn } from 'node:child_process';
import { readFileSync, mkdirSync } from 'node:fs';
import { createRequire } from 'node:module';
const { chromium } = createRequire(import.meta.url)('playwright');

const ROOT = new URL('../../', import.meta.url).pathname;
const PORT = 8768;
const NOW = readFileSync(ROOT + 'spec/tests/l2.yaml', 'utf8').match(/^now:\s*"([^"]+)"/m)[1];
const avoided = readFileSync(ROOT + 'spec/catalog/vocabulary/l2.yaml', 'utf8').split('avoided:')[1].split('labels:')[0]
  .split('\n').map(l => l.trim()).filter(l => l.startsWith('- ')).map(l => l.slice(2).trim());
// No Agent E2 service on port 8090 during page tests: LPG-8 checks the unavailable state.
const server = spawn('python3', ['-m', 'build.pcm_proto.server', '--port', String(PORT)], { cwd: ROOT, stdio: 'inherit', env: { ...process.env, PCM_DEMO_SWITCHER: '0', PCM_AGENT_E2_MODE: 'mock', PCM_DB: ':memory:' } });
for (let i = 0; i < 50; i++) { try { await fetch(`http://127.0.0.1:${PORT}/exec`); break; } catch { await new Promise(r => setTimeout(r, 200)); } }
const BASE = `http://127.0.0.1:${PORT}`;
const NQ = `now=${encodeURIComponent(NOW)}`;
const withNow = p => p + (p.includes('?') ? '&' : '?') + NQ;
const reset = () => fetch(`${BASE}/api/noc/_reset?${NQ}`, { method: 'POST', body: '{}' });
const results = [];
const check = (id, ok, detail = '') => { results.push({ ok }); console.log(`${ok ? 'PASS' : 'FAIL'} ${id}${detail ? ' - ' + detail : ''}`); };
const browser = await chromium.launch();
const hosts = new Set();
const PAGES = ['/l2', '/l2/monitor/compute/estate/performance', '/l2/monitor/compute/ld/performance?window=7d&group=host_model', '/l2/monitor/compute/estate/capacity',
  '/l2/monitor/compute/estate/security', '/l2/monitor/compute/estate/configuration', '/l2/monitor/compute/estate/inventory', '/l2/monitor/compute/estate/availability',
  '/l2/monitor/compute/estate/summary?window=1y', '/l2/monitor/compute/sg-app-117/performance', '/l2/monitor/storage/estate/performance',
  '/l2/troubleshoot/compute/estate', '/l2/troubleshoot/new', '/l2/troubleshoot/case/case-sg-app-117', '/l2/troubleshoot/case/case-inc-tk-s-03',
  '/l2/improve/compute/estate/summary', '/l2/improve/compute/estate/configuration', '/l2/improve/compute/estate/capacity', '/l2/rules', '/l2/calendar'];
try {
  const page = await browser.newPage({ viewport: { width: 1440, height: 1000 } });
  page.on('request', r => hosts.add(new URL(r.url()).host));
  page.on('dialog', d => d.accept('Reason given in the test'));
  const errors = [];
  page.on('pageerror', e => errors.push(e.message));
  const go = async p => { await page.goto(BASE + withNow(p)); await page.waitForSelector('body[data-ready="1"]', { timeout: 60000 }); };
  await reset();

  // LPG-2, LPG-13: words and decision IDs, on every page
  const texts = [];
  for (const p of PAGES) { await go(p); texts.push(await page.innerText('body')); }
  const all = texts.join('\n');
  const bad = avoided.filter(w => new RegExp(`\\b${w}\\b`, 'i').test(all));
  check('LPG-2', bad.length === 0, bad.length ? `avoided: ${bad}` : 'no avoided word on any L2 page');
  const ids = all.match(/\bD-\d{3}\b/g) || [];
  check('LPG-13', ids.length === 0 && errors.length === 0, ids.length ? `found ${[...new Set(ids)]}` : errors.length ? errors.join('; ') : 'no decision ID; no page error');

  // LPG-3 the top bar
  await go('/l2');
  const acts = await page.$$eval('nav.acts a', as => as.map(a => a.textContent.replace(/\d+$/, '').trim()));
  const utils = await page.$$eval('nav.utils a', as => as.map(a => a.textContent.trim()));
  const topText = await page.innerText('#top');
  check('LPG-3', acts.join() === 'Monitor,Troubleshoot,Improve' && utils.join() === 'Rules,Calendar' && !/Weekly|Monthly|Escalations|Inventory|Configuration/.test(topText), `${acts} | ${utils}`);

  // LPG-4 /l2 opens Monitor on the estate, Summary, 24 hours, one row per pillar
  const landed = new URL(page.url()).pathname;
  const rows = await page.$$eval('tr[data-pillar]', r => r.map(x => x.dataset.pillar));
  const win = await page.innerText('.windows a[aria-current="true"]');
  check('LPG-4', landed === '/l2/monitor/compute/estate/summary' && rows.join() === 'availability,performance,capacity,security,configuration,inventory' && win === '24 hours' && !/health score/i.test(await page.innerText('main')), `${landed}; ${rows.length} pillar rows; ${win}`);

  // LPG-5 the tree keeps activity and window; switching activity keeps the object
  await go('/l2/monitor/compute/estate/performance?window=7d');
  await page.click('aside.tree li[data-node="emea"] > .item > button.caret'); await page.waitForSelector('li[data-node="fr"]');
  await page.click('li[data-node="fr"] > .item > a.node'); await page.waitForSelector('body[data-ready="1"]');
  const u1 = new URL(page.url());
  await page.click('nav.acts a:has-text("Troubleshoot")'); await page.waitForSelector('body[data-ready="1"]');
  const u2 = new URL(page.url());
  check('LPG-5', u1.pathname === '/l2/monitor/compute/fr/performance' && u1.searchParams.get('window') === '7d' && u2.pathname === '/l2/troubleshoot/compute/fr', `${u1.pathname}?window=${u1.searchParams.get('window')} then ${u2.pathname}`);

  // LPG-6 a complaint opens a case; the chain grows in the T-1 order; Rule out asks for a reason
  await go('/l2/troubleshoot/new?vm=sg-gl-db-01');
  await page.fill('input[name="requester"]', 'General ledger application owner');
  await Promise.all([page.waitForURL(/\/case\//), page.click('#cf button[type="submit"]')]); await page.waitForSelector('body[data-ready="1"]');
  for (let i = 1; i <= 3; i++) { await page.click('#propose'); await page.waitForFunction(n => document.querySelectorAll('[data-link]').length >= n, i); }
  const order = await page.$$eval('[data-link]', xs => xs.map(x => x.dataset.link));
  await page.click('[data-ruleout="t1-guest"]'); await page.waitForSelector('[data-link="t1-guest"].ruled_out');
  const ruled = await page.innerText('[data-link="t1-guest"]');
  check('LPG-6', order.join() === 't1-guest,t1-disk,t1-cpu' && ruled.includes('Reason given in the test'), `${order}; ruled out with a reason: ${ruled.includes('Reason given')}`);

  // LPG-7 the L-2 case hands over to the Guest OS team
  await go('/l2/troubleshoot/case/case-sg-app-117');
  const ho = await page.innerText('[data-handover]');
  check('LPG-7', ho === 'The cause is inside the Guest OS. Hand this evidence to the Windows or Linux team.', ho);

  // LPG-8 Agent E2 service not running
  await page.click('#ask button[type="submit"]'); await page.waitForSelector('body[data-ask]', { timeout: 30000 });
  const askText = await page.innerText('#answer');
  check('LPG-8', askText.includes('The Agent E2 service is not available'), askText.split('\n')[0]);

  // LPG-9 Rules: no "Make automatic"; Publish only after Replay, for policies and thresholds
  await go('/l2/rules');
  const noAuto = !(await page.innerText('body')).includes('Make automatic');
  const thBefore = await page.isDisabled('[data-publish]');
  await page.fill('form[data-t] input[name="value"]', '60'); await page.click('form[data-t] button[type="submit"]'); await page.waitForSelector('body[data-replayed]');
  const thAfter = await page.isDisabled('[data-publish]');
  await page.click('button[data-propose="move_vms_between_clusters"]');
  const pubBefore = await page.isDisabled('#publish');
  await page.selectOption('#pf select[name="tier"]', 'automatic');
  await page.click('#pf button[type="submit"]'); await page.waitForSelector('body[data-policy-replayed]');
  const replayText = await page.innerText('#replay');
  check('LPG-9', noAuto && thBefore && !thAfter && pubBefore && !(await page.isDisabled('#publish')) && /18/.test(replayText), replayText.trim());

  // LPG-10 group by host model in London, 7 days
  await go('/l2/monitor/compute/ld/performance?window=7d&group=host_model');
  const g = await page.innerText('[data-group="Gen-2019, 2 x 20 cores"]');
  const g24 = await page.innerText('[data-group="Gen-2024, 2 x 32 cores"]');
  const wider = row => row.split('\t').map(s => s.trim())[5];
  check('LPG-10', wider(g) === '9' && wider(g24) === '0', `wider than their host's NUMA node: Gen-2019 ${wider(g)}, Gen-2024 ${wider(g24)}`);

  // LPG-11 Improve at the estate shows the decision register
  await go('/l2/improve/compute/estate/summary');
  const snap = await page.innerText('[data-decision="d-snapshots"]');
  check('LPG-11', snap.includes('Overdue'), snap.replace(/\s+/g, ' '));

  // LPG-14 Performance above the cluster: VM, then Cluster; Gold by default; a click on a time selects it
  await go('/l2/monitor/compute/estate/performance');
  const sections = await page.$$eval('section.persp', xs => xs.map(x => x.dataset.section));
  const gold = await page.innerText('nav[aria-label="Class of service"] a[aria-current="true"]');
  const hit = page.locator('[data-chartbox="perf"] rect.hit'); await hit.scrollIntoViewIfNeeded();
  const hb = await hit.boundingBox();
  await Promise.all([page.waitForURL(/[?&]at=/), hit.click({ position: { x: hb.width * 0.5, y: 20 } })]); await page.waitForSelector('body[data-ready="1"]');
  const atParam = new URL(page.url()).searchParams.get('at');
  const head = await page.getAttribute('h3[data-at]', 'data-at');
  check('LPG-14', sections.join() === 'vm,cluster' && gold === 'Gold' && !!atParam && head === atParam && (await page.innerText('h3[data-at]')).includes('the time you picked'), `${sections}; ${gold}; at=${atParam}`);

  // LPG-12 contrast and no foreign request
  const contrast = async () => page.evaluate(() => {
    const parse = c => (c.match(/[\d.]+/g) || []).map(Number);
    const lum = ([r, g, b]) => [r, g, b].map(v => { v /= 255; return v <= 0.03928 ? v / 12.92 : ((v + 0.055) / 1.055) ** 2.4; }).reduce((a, v, i) => a + v * [0.2126, 0.7152, 0.0722][i], 0);
    const bgOf = el => { for (let e = el; e; e = e.parentElement) { const c = parse(getComputedStyle(e).backgroundColor); if (c.length === 3 || (c.length === 4 && c[3] > 0.5)) return c.slice(0, 3); } return [255, 255, 255]; };
    const fails = [];
    for (const el of document.querySelectorAll('body *')) {
      if (![...el.childNodes].some(n => n.nodeType === 3 && n.textContent.trim()) || el.offsetParent === null) continue;
      const [a, b] = [lum(parse(getComputedStyle(el).color).slice(0, 3)), lum(bgOf(el))].sort((x, y) => y - x);
      const r = (a + 0.05) / (b + 0.05); if (r < 4.5) fails.push(`${el.className || el.tagName} ${r.toFixed(2)}`);
    }
    return fails;
  });
  const fails = [];
  for (const p of ['/l2', '/l2/monitor/compute/ld/performance?window=7d&group=host_model', '/l2/troubleshoot/compute/estate', '/l2/troubleshoot/case/case-inc-tk-s-03', '/l2/improve/compute/estate/summary', '/l2/rules', '/l2/calendar']) {
    await go(p); fails.push(...(await contrast()).map(f => `${p}: ${f}`));
  }
  const foreign = [...hosts].filter(h => h !== `127.0.0.1:${PORT}`);
  check('LPG-12', !fails.length && !foreign.length, fails.slice(0, 4).join(' | ') || 'contrast ok; no foreign request');

  // Screenshots for review.
  mkdirSync(ROOT + 'build/screenshots', { recursive: true });
  const shot = await browser.newPage({ viewport: { width: 1440, height: 1000 }, deviceScaleFactor: 2 });
  shot.on('dialog', d => d.accept('Reason given in the test'));
  for (const [p, name, full] of [['/l2', 'l2-monitor-estate', false], ['/l2/monitor/compute/ld/performance?window=7d&group=host_model', 'l2-monitor-group-by', false],
    ['/l2/monitor/compute/estate/performance', 'l2-monitor-performance', true],
    ['/l2/troubleshoot/compute/estate', 'l2-troubleshoot-cases', false], ['/l2/troubleshoot/case/case-inc-tk-s-03', 'l2-case-escalation', true],
    ['/l2/troubleshoot/case/case-sg-app-117', 'l2-case-guest-os', true], ['/l2/improve/compute/estate/summary', 'l2-improve', false], ['/l2/rules', 'l2-rules', false]]) {
    await shot.goto(BASE + withNow(p)); await shot.waitForSelector('body[data-ready="1"]', { timeout: 60000 });
    await shot.screenshot({ path: ROOT + `build/screenshots/${name}.png`, fullPage: full });
  }
  await shot.goto(BASE + withNow('/l2/troubleshoot/compute/estate')); await shot.waitForSelector('body[data-ready="1"]');
  const t1 = await shot.$$eval('tr[data-case]', trs => trs.map(t => [t.dataset.case, t.innerText]).find(([, x]) => /sg-gl-db-01/.test(x)));
  if (t1) {
    await shot.goto(BASE + withNow(`/l2/troubleshoot/case/${t1[0]}`)); await shot.waitForSelector('body[data-ready="1"]');
    await shot.screenshot({ path: ROOT + 'build/screenshots/l2-case-complaint.png', fullPage: true });
  }
} finally {
  await browser.close(); await reset().catch(() => {}); server.kill();
}
const failed = results.filter(r => !r.ok);
console.log(`\n${results.length - failed.length} passed, ${failed.length} failed`);
process.exit(failed.length ? 1 : 0);
