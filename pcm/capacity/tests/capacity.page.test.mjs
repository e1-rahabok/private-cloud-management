// Page tests KPG-2 to KPG-6 for /capacity, in a real browser.
// GENERATED from pcm/capacity/spec/acceptance-tests.yaml. Do not edit by hand (D-070).
// Run from the repository root:  node pcm/capacity/tests/capacity.page.test.mjs
import { spawn } from 'node:child_process';
import { readFileSync, mkdirSync, mkdtempSync, rmSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { createRequire } from 'node:module';
const { chromium } = createRequire(import.meta.url)('playwright');

const ROOT = new URL('../../../', import.meta.url).pathname;  // the repository root
const HERE = new URL('../', import.meta.url).pathname;  // the workspace folder
const PORT = 8769;
const NOW = readFileSync(HERE + 'spec/acceptance-tests.yaml', 'utf8').match(/^now:\s*"([^"]+)"/m)[1];
const avoided = readFileSync(HERE + 'spec/vocabulary.yaml', 'utf8').match(/^avoided:\s*\[(.*)\]/m)[1].split(',').map(s => s.trim());
// A database file of its own, so the test can restart the server and check what survived (DBP-1).
const DBDIR = mkdtempSync(tmpdir() + '/pcm-');
const start = async () => {
  const s = spawn('python3', ['-m', 'pcm.core.server', '--port', String(PORT)], { cwd: ROOT, stdio: 'inherit', env: { ...process.env, PCM_DEMO_SWITCHER: '0', PCM_DB: DBDIR + '/pcm.sqlite' } });
  for (let i = 0; i < 50; i++) { try { await fetch(`http://127.0.0.1:${PORT}/capacity`); return s; } catch { await new Promise(r => setTimeout(r, 200)); } }
  return s;
};
let server = await start();
const BASE = `http://127.0.0.1:${PORT}`;
const q = `?now=${encodeURIComponent(NOW)}`;
const reset = () => fetch(`${BASE}/api/noc/_reset${q}`, { method: 'POST', body: '{}' });
const PAGES = ['/capacity', '/capacity/clusters', '/capacity/group/FR-Silver', '/capacity/group/TK-Silver', '/capacity/demand', '/capacity/what-if', '/capacity/plan', '/capacity/waste'];
const results = [];
const check = (id, ok, detail = '') => { results.push({ ok }); console.log(`${ok ? 'PASS' : 'FAIL'} ${id}${detail ? ' - ' + detail : ''}`); };
const browser = await chromium.launch();
const hosts = new Set();
try {
  await reset();
  const page = await browser.newPage({ viewport: { width: 1440, height: 1000 } });
  page.on('request', r => hosts.add(new URL(r.url()).host));
  const go = async p => { await page.goto(BASE + p + q); await page.waitForSelector('body[data-ready="1"]'); };

  const texts = [];
  for (const p of PAGES) { await go(p); texts.push(await page.innerText('body')); }
  const all = texts.join('\n');
  const bad = avoided.filter(w => new RegExp(`\\b${w}\\b`, 'i').test(all));
  check('KPG-2', bad.length === 0, bad.length ? `avoided: ${bad}` : 'no avoided word on any Capacity page');

  await go('/capacity/clusters');
  const tk = await page.getAttribute('[data-group="TK-Gold"]', 'data-fill');
  const tkChip = await page.innerText('[data-row="TK-Gold"] .chip');
  check('KPG-3', tk === 'var(--waste)' && tkChip === 'Waste', `TK-Gold dot ${tk}, chip "${tkChip}"`);

  const ldb = await page.innerText('[data-row="LD-Bronze"]');
  const allRows = await page.innerText('table');
  check('KPG-4', ldb.includes('Closed for new VMs') && ldb.includes('LD-B-01') && !/Full now|VMs waiting/.test(allRows), ldb.replace(/\s+/g, ' ').trim());

  await go('/capacity');
  const moved = await page.innerText('[data-moved="FR-Silver"]');
  check('KPG-5', moved.includes('earlier') && moved.includes('dr-ocp-wave-2'), moved);

  const ids = all.match(/\bD-\d{3}\b/g) || [];
  const contrast = async () => page.evaluate(() => {
    const parse = c => (c.match(/[\d.]+/g) || []).map(Number);
    const lum = ([r, g, b]) => [r, g, b].map(v => { v /= 255; return v <= 0.03928 ? v / 12.92 : ((v + 0.055) / 1.055) ** 2.4; }).reduce((a, v, i) => a + v * [0.2126, 0.7152, 0.0722][i], 0);
    const bgOf = el => { for (let e = el; e; e = e.parentElement) { const c = parse(getComputedStyle(e).backgroundColor); if (c.length === 3 || (c.length === 4 && c[3] > 0.5)) return c.slice(0, 3); } return [255, 255, 255]; };
    const fails = [];
    for (const el of document.querySelectorAll('body *')) {
      if (el.closest('svg')) continue;
      if (![...el.childNodes].some(n => n.nodeType === 3 && n.textContent.trim()) || el.offsetParent === null) continue;
      const [a, b] = [lum(parse(getComputedStyle(el).color).slice(0, 3)), lum(bgOf(el))].sort((x, y) => y - x);
      const r = (a + 0.05) / (b + 0.05); if (r < 4.5) fails.push(`${el.className || el.tagName} ${r.toFixed(2)}`);
    }
    return fails;
  });
  const fails = [];
  for (const p of PAGES) { await go(p); fails.push(...(await contrast()).map(f => `${p}: ${f}`)); }

  // The Add form: a new entry moves the forecast at once.
  await go('/capacity/demand');
  await page.fill('#add input[name="date"]', '2026-12-15');
  await page.selectOption('#add select[name="group"]', 'VA-Silver');
  await page.fill('#add input[name="memory_gb"]', '20000');
  await page.fill('#add input[name="owner"]', 'apps-team');
  await page.click('#add button[type="submit"]'); await page.waitForSelector('body[data-added]');
  const added = await page.innerText('#msg');
  const rows = await page.locator('[data-entry]').count();
  check('demand-add', rows === 2 && added.includes('VA-Silver'), added);

  // DBP-1 the entry survives a restart of the PCM server
  server.kill(); await new Promise(r => server.on('exit', r));
  server = await start();
  await go('/capacity/demand');
  const kept = await page.locator('[data-entry="dr-001"]').count();
  check('DBP-1', kept === 1, kept ? 'dr-001 still in the register after restart' : 'entry lost on restart');

  const foreign = [...hosts].filter(h => h !== `127.0.0.1:${PORT}`);
  check('KPG-6', !ids.length && !fails.length && !foreign.length,
    ids.length ? `decision IDs ${[...new Set(ids)]}` : fails.slice(0, 4).join(' | ') || (foreign.length ? `requests to ${foreign}` : 'no decision ID; contrast ok; no foreign request'));

  await reset();
  mkdirSync(HERE + 'screenshots', { recursive: true });
  const shot = await browser.newPage({ viewport: { width: 1440, height: 1000 }, deviceScaleFactor: 2 });
  for (const [p, name] of [['/capacity', 'capacity-week'], ['/capacity/clusters', 'capacity-clusters'], ['/capacity/group/TK-Silver', 'capacity-group-peak'],
    ['/capacity/group/FR-Silver', 'capacity-group-migration'], ['/capacity/what-if', 'capacity-what-if'], ['/capacity/plan', 'capacity-plan'], ['/capacity/waste', 'capacity-waste']]) {
    await shot.goto(BASE + p + q); await shot.waitForSelector('body[data-ready="1"]');
    await shot.screenshot({ path: HERE + `screenshots/${name}.png`, fullPage: true });
  }
} finally {
  await browser.close(); await reset().catch(() => {}); server.kill(); rmSync(DBDIR, { recursive: true, force: true });
}
const failed = results.filter(r => !r.ok);
console.log(`\n${results.length - failed.length} passed, ${failed.length} failed`);
process.exit(failed.length ? 1 : 0);
