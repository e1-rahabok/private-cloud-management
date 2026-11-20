// Page tests LPG-2 to LPG-7 for /l2, in a real browser.
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
// No Agent E2 service on port 8090 during page tests: LPG-9 checks the unavailable state.
const server = spawn('python3', ['-m', 'build.pcm_proto.server', '--port', String(PORT)], { cwd: ROOT, stdio: 'inherit', env: { ...process.env, PCM_AGENT_E2_MODE: 'mock', PCM_DB: ':memory:' } });
// Wait until the server answers, not a fixed time: a slow start made the first request fail.
for (let i = 0; i < 50; i++) { try { await fetch(`http://127.0.0.1:${PORT}/exec`); break; } catch { await new Promise(r => setTimeout(r, 200)); } }
const BASE = `http://127.0.0.1:${PORT}`;
const q = `?now=${encodeURIComponent(NOW)}`;
const reset = () => fetch(`${BASE}/api/noc/_reset${q}`, { method: 'POST', body: '{}' });
const results = [];
const check = (id, ok, detail = '') => { results.push({ ok }); console.log(`${ok ? 'PASS' : 'FAIL'} ${id}${detail ? ' - ' + detail : ''}`); };
const browser = await chromium.launch();
const hosts = new Set();
try {
  const page = await browser.newPage({ viewport: { width: 1440, height: 1000 } });
  page.on('request', r => hosts.add(new URL(r.url()).host));
  page.on('dialog', d => d.accept('Reason given in the test'));
  const go = async p => { await page.goto(BASE + p + q); await page.waitForSelector('body[data-ready="1"]'); };

  await reset();
  // The NOC escalates first: the loop between the two workspaces (LPG-4).
  await go('/noc/alert/inc-fr-s-02'); await page.click('button[data-escalate]'); await page.waitForTimeout(300);

  const texts = [];
  for (const p of ['/l2', '/l2/weekly', '/l2/monthly', '/l2/inventory', '/l2/escalations', '/l2/investigate/sg-app-117', '/l2/investigate/FR-S-02', '/l2/configuration', '/l2/context', '/l2/authoring']) {
    await go(p); texts.push(await page.innerText('body'));
  }
  await go('/l2/escalations'); await page.click('button[data-rca]'); await page.waitForSelector('body[data-agent]'); texts.push(await page.innerText('body'));
  const all = texts.join('\n');
  const bad = avoided.filter(w => new RegExp(`\\b${w}\\b`, 'i').test(all));
  check('LPG-2', bad.length === 0, bad.length ? `avoided: ${bad}` : 'no avoided word on any L2 page');

  // LPG-8 no decision ID in page text
  const ids = (all).match(/\bD-\d{3}\b/g) || [];
  check('LPG-8', ids.length === 0, ids.length ? `found ${[...new Set(ids)]}` : 'no decision ID in page text');

  await go('/l2');
  const verdicts = await page.$$eval('.verdict', els => els.map(e => e.dataset.verdict));
  check('LPG-3', verdicts.join() === 'present_health,risk,efficiency' && !/health score/i.test(await page.innerText('body')), verdicts.join(', '));

  // LPG-10 no "Make automatic"; Publish only after Replay
  await go('/l2');
  const noAuto = !(await page.innerText('body')).includes('Make automatic');
  await page.click('button[data-propose="move_vms_between_clusters"]');
  const pubBefore = await page.isDisabled('#publish');
  await page.selectOption('#pf select[name="tier"]', 'automatic');
  await page.click('#pf button[type="submit"]'); await page.waitForSelector('body[data-policy-replayed]');
  const replayText = await page.innerText('#replay');
  const pubAfter = await page.isDisabled('#publish');
  check('LPG-10', noAuto && pubBefore && !pubAfter && /18/.test(replayText), replayText.trim());

  // LPG-11 weekly: Assign needs an owner and an action
  await go('/l2/weekly');
  await page.fill('form.assign[data-f="w-sg-ds-11"] input[name="owner"]', 'l2-engineer-1');
  await page.click('form.assign[data-f="w-sg-ds-11"] button'); await page.waitForSelector('body[data-assign="400"]');
  const err = await page.innerText('.msg');
  await page.fill('form.assign[data-f="w-sg-ds-11"] input[name="owner"]', 'l2-engineer-1');
  await page.fill('form.assign[data-f="w-sg-ds-11"] input[name="action"]', 'Remove the backup snapshot on sg-app-301');
  await page.click('form.assign[data-f="w-sg-ds-11"] button'); await page.waitForSelector('body[data-assign="200"]');
  const assigned = await page.innerText('[data-weekly="w-sg-ds-11"]');
  check('LPG-11', /owner and an action/.test(err) && assigned.includes('Assigned to l2-engineer-1'), `${err} / ${assigned.split('\n').pop()}`);

  // LPG-12 monthly opens with last month's decisions
  await go('/l2/monthly');
  const firstH2 = await page.innerText('main h2');
  const snap = await page.innerText('[data-decision="d-snapshots"]');
  check('LPG-12', firstH2 === "Last month's decisions" && snap.includes('Overdue'), `${firstH2}; ${snap.replace(/\s+/g, ' ')}`);

  // LPG-13 inventory: ld-db-021 first among unexplained; DRS moves only counted
  await go('/l2/inventory');
  const firstChange = await page.getAttribute('[data-change]', 'data-change');
  const listed = await page.$$eval('[data-change] strong', els => els.map(e => e.parentElement.innerText));
  const moves = listed.filter(t => /: Moved\./.test(t)).length;
  check('LPG-13', firstChange === 'chg-ld-db-021' && moves === 0 && listed.length === 2, `first unexplained: ${firstChange}; ${listed.length} listed; moves listed: ${moves}`);

  await go('/l2/escalations');
  const escText = await page.innerText('[data-escalation="inc-fr-s-02"]');
  check('LPG-4', /CPU Ready 1.2%/.test(escText) && /fr-bat-017/.test(escText), 'escalation from the NOC arrived with counters');

  await go('/l2/investigate/sg-app-117');
  const concl = await page.innerText('.conclusion');
  check('LPG-5', concl.includes('inside the Guest OS'), concl);

  await go('/l2/authoring');
  const before = await page.isDisabled('[data-publish]');
  await page.fill('input[name="value"]', '60'); await page.click('form[data-t] button[type="submit"]');
  await page.waitForSelector('body[data-replayed]');
  const after = await page.isDisabled('[data-publish]');
  check('LPG-6', before && !after, `publish disabled before replay: ${before}; after: ${after}`);

  // LPG-9 Agent E2 service not running: the page says so and shows no answer
  await go('/l2/investigate/sg-app-117');
  await page.click('#ask button[type="submit"]');
  await page.waitForSelector('body[data-ask]', { timeout: 30000 });
  const askText = await page.innerText('#answer');
  check('LPG-9', askText.includes('The Agent E2 service is not available'), askText.split('\n')[0]);

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
  for (const p of ['/l2', '/l2/weekly', '/l2/monthly', '/l2/inventory', '/l2/escalations', '/l2/investigate/sg-app-117', '/l2/configuration', '/l2/context', '/l2/authoring']) { await go(p); fails.push(...(await contrast()).map(f => `${p}: ${f}`)); }
  const foreign = [...hosts].filter(h => h !== `127.0.0.1:${PORT}`);
  check('LPG-7', !fails.length && !foreign.length, fails.slice(0, 4).join(' | ') || 'contrast ok; no foreign request');

  // Screenshots for review: approve-then-promote flow on Today, the escalation, the investigation.
  mkdirSync(ROOT + 'build/screenshots', { recursive: true });
  const shot = await browser.newPage({ viewport: { width: 1440, height: 1000 }, deviceScaleFactor: 2 });
  shot.on('dialog', d => d.accept('Reason given in the test'));
  await shot.goto(BASE + '/l2' + q); await shot.waitForSelector('body[data-ready="1"]');
  await shot.screenshot({ path: ROOT + 'build/screenshots/l2-today.png', fullPage: true });
  await shot.goto(BASE + '/l2/investigate/sg-app-117' + q); await shot.waitForSelector('body[data-ready="1"]');
  await shot.screenshot({ path: ROOT + 'build/screenshots/l2-investigate-guest-os.png', fullPage: true });
  await shot.goto(BASE + '/l2/escalations' + q); await shot.waitForSelector('body[data-ready="1"]');
  await shot.screenshot({ path: ROOT + 'build/screenshots/l2-escalation.png', fullPage: true });
  for (const [p, name] of [['/l2/weekly', 'l2-weekly'], ['/l2/monthly', 'l2-monthly'], ['/l2/inventory', 'l2-inventory']]) {
    await shot.goto(BASE + p + q); await shot.waitForSelector('body[data-ready="1"]');
    await shot.screenshot({ path: ROOT + `build/screenshots/${name}.png`, fullPage: true });
  }
  await shot.goto(BASE + '/l2/authoring' + q); await shot.waitForSelector('body[data-ready="1"]');
  await shot.fill('input[name="value"]', '60'); await shot.click('form[data-t] button[type="submit"]'); await shot.waitForSelector('body[data-replayed]');
  await shot.screenshot({ path: ROOT + 'build/screenshots/l2-threshold-replay.png', fullPage: true });
} finally {
  await browser.close(); await reset().catch(() => {}); server.kill();
}
const failed = results.filter(r => !r.ok);
console.log(`\n${results.length - failed.length} passed, ${failed.length} failed`);
process.exit(failed.length ? 1 : 0);
