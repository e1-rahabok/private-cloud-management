// Page tests DPG-2 to DPG-4 for /docs, in a real browser.
// GENERATED from spec/tests/docs.yaml. Do not edit by hand (D-070).
// Run from the repository root:  node build/tests/docs.page.test.mjs
import { spawn } from 'node:child_process';
import { readFileSync, mkdirSync } from 'node:fs';
import { createRequire } from 'node:module';
const { chromium } = createRequire(import.meta.url)('playwright');

const ROOT = new URL('../../', import.meta.url).pathname;
const PORT = 8770;
const NOW = readFileSync(ROOT + 'spec/tests/docs.yaml', 'utf8').match(/^now:\s*"([^"]+)"/m)[1];
const server = spawn('python3', ['-m', 'build.pcm_proto.server', '--port', String(PORT)], { cwd: ROOT, stdio: 'inherit', env: { ...process.env, PCM_DB: ':memory:' } });
for (let i = 0; i < 50; i++) { try { await fetch(`http://127.0.0.1:${PORT}/docs`); break; } catch { await new Promise(r => setTimeout(r, 200)); } }
const BASE = `http://127.0.0.1:${PORT}`, q = `?now=${encodeURIComponent(NOW)}`;
const results = [];
const check = (id, ok, detail = '') => { results.push({ ok }); console.log(`${ok ? 'PASS' : 'FAIL'} ${id}${detail ? ' - ' + detail : ''}`); };
const browser = await chromium.launch();
const hosts = new Set();
try {
  const page = await browser.newPage({ viewport: { width: 1440, height: 1000 } });
  page.on('request', r => hosts.add(new URL(r.url()).host));
  const go = async p => { await page.goto(BASE + p + q); await page.waitForSelector('body[data-ready="1"]'); };

  await go('/docs');
  const all = Number(await page.getAttribute('body', 'data-shown'));
  await page.fill('#q', 'run_out');
  await page.waitForFunction(n => Number(document.body.dataset.shown) < n, all);
  const ids = await page.$$eval('[data-id]', els => els.map(e => e.dataset.id));
  check('DPG-2', ids.length > 0 && ids.length < all && ids.includes('capacity.run_out_date'), `${all} objects; "run_out" shows ${ids.length}: ${ids.slice(0, 4).join(', ')}`);

  await go('/docs/measure/capacity.run_out_date');
  const used = await page.$$eval('[data-used]', els => els.map(e => e.dataset.used));
  check('DPG-3', used.some(u => u.startsWith('/capacity')), used.join(', '));

  const texts = [];
  const pages = ['/docs', '/docs/measure/capacity.run_out_date', '/docs/sop/sop-cluster-contention', '/docs/policy/move_vms_between_clusters',
    '/docs/threshold/th-cluster-perf-red', '/docs/standard/ntp_server', '/docs/setting/capacity.class_planning', '/docs/measure/up.availability_percent'];
  const contrast = () => page.evaluate(() => {
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
  for (const p of pages) { await go(p); texts.push(await page.innerText('body')); fails.push(...(await contrast()).map(f => `${p}: ${f}`)); }
  const dids = texts.join('\n').match(/\bD-\d{3}\b/g) || [];
  const foreign = [...hosts].filter(h => h !== `127.0.0.1:${PORT}`);
  check('DPG-4', !dids.length && !fails.length && !foreign.length,
    dids.length ? `decision IDs ${[...new Set(dids)]}` : fails.slice(0, 4).join(' | ') || (foreign.length ? `requests to ${foreign}` : 'no decision ID; contrast ok; no foreign request'));

  mkdirSync(ROOT + 'build/screenshots', { recursive: true });
  const shot = await browser.newPage({ viewport: { width: 1440, height: 1000 }, deviceScaleFactor: 2 });
  for (const [p, name] of [['/docs', 'docs-index'], ['/docs/threshold/th-cluster-perf-red', 'docs-threshold'], ['/docs/measure/capacity.run_out_date', 'docs-measure']]) {
    await shot.goto(BASE + p + q); await shot.waitForSelector('body[data-ready="1"]');
    await shot.screenshot({ path: ROOT + `build/screenshots/${name}.png`, fullPage: p !== '/docs' });
  }
} finally {
  await browser.close(); server.kill();
}
const failed = results.filter(r => !r.ok);
console.log(`\n${results.length - failed.length} passed, ${failed.length} failed`);
process.exit(failed.length ? 1 : 0);
