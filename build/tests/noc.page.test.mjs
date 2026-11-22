// Page tests NPG-2 to NPG-11 for /noc, in a real browser.
// GENERATED from spec/tests/noc.yaml. Do not edit by hand (D-070).
// Run from the repository root:  node build/tests/noc.page.test.mjs
import { spawn } from 'node:child_process';
import { createServer } from 'node:http';
import { readFileSync, mkdirSync } from 'node:fs';
import { createRequire } from 'node:module';
const { chromium } = createRequire(import.meta.url)('playwright');

const ROOT = new URL('../../', import.meta.url).pathname;
const PORT = 8766;
const NOW = readFileSync(ROOT + 'spec/tests/noc.yaml', 'utf8').match(/^now:\s*"([^"]+)"/m)[1];
const vocab = readFileSync(ROOT + 'spec/catalog/vocabulary/noc.yaml', 'utf8');
const avoided = vocab.split('avoided:')[1].split('labels:')[0].split('\n').map(l => l.trim())
  .filter(l => l.startsWith('- ')).map(l => l.slice(2).trim());

// Agent E2 drafts in mock mode, and a stub Agent E2 service: page tests must not depend on the network (D-076, D-098).
const E2_PORT = 8767;
const E2_SEEN = [];
const stub = createServer((req, res) => {
  let b = ''; req.on('data', c => { b += c; }); req.on('end', () => {
    const send = d => { res.writeHead(200, { 'Content-Type': 'application/json' }); res.end(JSON.stringify(d)); };
    if (req.url === '/v1/health') return send({ ok: true, model: 'stub-model', files: 286 });
    const body = JSON.parse(b || '{}'); E2_SEEN.push(body);
    // A question about the villain gets an L2 word, twice: the panel must not show it.
    const content = /villain/i.test(body.question.split('\n')[0]) ? 'The villain fr-bat-017 drives CPU Ready up.' : 'FR-S-02 scores 22 out of 100: its VMs wait. The SOP says to find the villain and escalate a production one.';
    send({ type: 'answer', content, questions: [], files_read: ['sp5-framework/performance/cluster-performance'], computed: [], model: 'stub-model', knowledge_commit: 'abc1234' });
  });
});
await new Promise(r => stub.listen(E2_PORT, '127.0.0.1', r));
const server = spawn('python3', ['-m', 'build.pcm_proto.server', '--port', String(PORT)], { cwd: ROOT, stdio: 'inherit', env: { ...process.env, PCM_DEMO_SWITCHER: '0', PCM_AGENT_E2_MODE: 'mock', PCM_DB: ':memory:', PCM_AGENT_E2_URL: `http://127.0.0.1:${E2_PORT}` } });
// Wait until the server answers, not a fixed time: a slow start made the first request fail.
for (let i = 0; i < 50; i++) { try { await fetch(`http://127.0.0.1:${PORT}/exec`); break; } catch { await new Promise(r => setTimeout(r, 200)); } }
const BASE = `http://127.0.0.1:${PORT}`;
const q = (extra = '') => `?now=${encodeURIComponent(NOW)}${extra}`;
const reset = () => fetch(`${BASE}/api/noc/_reset`, { method: 'POST', body: '{}' });

const results = [];
const check = (id, ok, detail = '') => { results.push({ id, ok }); console.log(`${ok ? 'PASS' : 'FAIL'} ${id}${detail ? ' - ' + detail : ''}`); };
const browser = await chromium.launch();
const hosts = new Set();
try {
  const page = await browser.newPage({ viewport: { width: 1440, height: 1000 } });
  page.on('request', r => hosts.add(new URL(r.url()).host));
  const go = async (path, extra = '') => { await page.goto(BASE + path + q(extra)); await page.waitForSelector('body[data-ready="1"]'); };

  // Collect text from every NOC page and state.
  await reset();
  const texts = [];
  for (const extra of ['', '&enable=E-7']) {
    await go('/noc', extra);
    for (const s of ['changed', 'up', 'fast', 'safe', 'set_right']) {
      await page.click(`.tabs button[data-s="${s}"]`); await page.waitForTimeout(150); texts.push(await page.innerText('body'));
    }
    await page.click(`.tabs button[data-s="fast"]`); await page.waitForTimeout(150);
    const cell = page.locator('.cellbtn.red').first();
    if (await cell.count()) { await cell.click(); await page.waitForTimeout(200); texts.push(await page.innerText('body')); }
    await go('/noc/alerts', extra); texts.push(await page.innerText('body'));
    for (const id of ['inc-fr-s-02', 'inc-tk', 'inc-ld-ds-07']) { await go('/noc/alert/' + id, extra); texts.push(await page.innerText('body')); }
    await go('/noc/shift', extra); texts.push(await page.innerText('body'));
    for (const s of ['changed', 'up', 'fast', 'safe', 'set_right']) { await go('/noc/wall', `${extra}&screen=${s}`); texts.push(await page.innerText('body')); }
  }
  const all = texts.join('\n');
  const bad = avoided.filter(w => new RegExp(`\\b${w.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')}\\b`, 'i').test(all));
  check('NPG-2', bad.length === 0, bad.length ? `avoided words: ${bad.join(', ')}` : 'no avoided word on any NOC page, in any state');

  // NPG-10 no decision ID in page text
  const ids = (all).match(/\bD-\d{3}\b/g) || [];
  check('NPG-10', ids.length === 0, ids.length ? `found ${[...new Set(ids)]}` : 'no decision ID in page text');

  // NPG-3 no interactive element on the wall
  await go('/noc/wall');
  const interactive = await page.$$eval('button, a, input, select, textarea', els => els.length);
  check('NPG-3', interactive === 0, `${interactive} interactive elements`);

  // NPG-4 red not acknowledged pins the rotation
  await reset();
  await go('/noc/wall', '&rotate=1');
  const seen = new Set();
  for (let i = 0; i < 8; i++) { seen.add(await page.getAttribute('body', 'data-screen')); await page.waitForTimeout(500); }
  check('NPG-4', [...seen].every(s => ['changed', 'fast'].includes(s)) && seen.has('fast'), `screens shown: ${[...seen].join(', ')}`);

  // NPG-5 acknowledge on the desktop, the wall rotates again and shows In hand
  await go('/noc/alert/inc-fr-s-02'); await page.click('#ack'); await page.waitForTimeout(300);
  await go('/noc/alert/inc-tk'); await page.click('#ack'); await page.waitForTimeout(300);
  await go('/noc/wall', '&rotate=1');
  const seen2 = new Set();
  for (let i = 0; i < 12; i++) { seen2.add(await page.getAttribute('body', 'data-screen')); await page.waitForTimeout(500); }
  const fastChip = await page.innerText('.strip .s[data-screen="fast"]');
  check('NPG-5', seen2.size === 5 && /In hand/.test(fastChip), `screens shown: ${[...seen2].join(', ')}; fast chip: ${fastChip.replace(/\s+/g, ' ')}`);

  // NPG-6 stale tiles are grey with No data and no number
  await reset();
  await go('/noc/wall', '&enable=E-7&screen=up');
  const stale = await page.$$eval('.tile.no_data', els => els.map(e => ({ t: e.innerText, num: /\b\d+\b/.test(e.querySelector('h3').nextElementSibling.innerText) })));
  check('NPG-6', stale.length === 2 && stale.every(s => s.t.includes('No data') && !s.num), JSON.stringify(stale.map(s => s.t.split('\n')[0])));

  // NPG-7 limit disabled for the production villain
  await go('/noc/alert/inc-fr-s-02');
  const limitBtn = page.locator('button[data-action="time_boxed_limit"]');
  const disabled = await limitBtn.isDisabled();
  const why = await page.locator('.why').first().innerText();
  check('NPG-7', disabled && why.includes('Production VM: escalate instead'), why);

  // NPG-9 Agent E2 draft on the incident page, from the panel
  await go('/noc/alert/inc-fr-s-02');
  const noSection = !(await page.$('button[data-agent]')) && !(await page.$$eval('main h2', hs => hs.some(h => h.textContent.trim() === 'Agent E2')));
  await page.click('main h1 .e2mark'); await page.waitForSelector('#e2 [data-sugg]');
  const firstSugg = await page.innerText('#e2 [data-sugg="0"]');
  await page.click('#e2 [data-sugg="0"]'); await page.waitForSelector('#e2 [data-draft]', { timeout: 30000 });
  const draftText = await page.innerText('#e2 [data-draft]');
  await page.keyboard.press('Escape');
  check('NPG-9', noSection && firstSugg === 'Explain this incident' && /^Draft by Agent E2, to review/m.test(draftText) && /asked by operator-1/.test(draftText), `${firstSugg}; ${draftText.split('\n')[0].slice(0, 70)}`);

  // NPG-11 the Agent E2 mark and panel on the desk; L1's words only
  const tops = [];
  for (const p of ['/noc', '/noc/alerts', '/noc/alert/inc-fr-s-02', '/noc/shift']) { await go(p); tops.push((await page.$$('header.top #e2top')).length); }
  await page.goto(BASE + '/noc/wall' + q('&screen=fast')); await page.waitForSelector('body[data-ready="1"]');
  const wallMarks = (await page.$$('.e2mark')).length;
  await go('/noc/alerts');
  const rowMarks = await page.$$eval('tr[data-incident]', trs => trs.map(t => !!t.querySelector('.e2mark')));
  await go('/noc/alert/inc-fr-s-02');
  const stepMarks = await page.$$eval('li[data-step]', ls => ls.map(l => !!l.querySelector('.e2mark')));
  await go('/noc');
  await page.waitForSelector('body[data-e2="up"]');
  const tileMarks = await page.$$eval('.grid5 .card', cs => cs.map(c => !!c.querySelector('h3 .e2mark')));
  await page.click('.cellbtn[data-cluster="FR-S-02"]'); await page.waitForSelector('#detail .panel h2 .e2mark');
  await page.click('#detail .panel h2 .e2mark'); await page.waitForSelector('#e2 [data-sugg]'); await page.waitForTimeout(300);
  const mainRight = await page.$eval('main', m => m.getBoundingClientRect().right), panelX = await page.$eval('#e2', e => e.getBoundingClientRect().x);
  const panelTexts = [await page.innerText('#e2')];
  await page.click('#e2 [data-sugg="0"]'); await page.waitForSelector('#e2 .e2src', { timeout: 30000 });
  panelTexts.push(await page.innerText('#e2'));
  const sent = E2_SEEN[E2_SEEN.length - 1];
  await page.fill('#e2q', 'Who is the villain?'); await page.press('#e2q', 'Enter'); await page.waitForSelector('#e2 [data-vocabulary]', { timeout: 30000 });
  const vocabText = await page.innerText('#e2 [data-vocabulary]');
  panelTexts.push(await page.innerText('#e2'));
  await page.keyboard.press('Escape');
  const panelBad = avoided.filter(w => new RegExp(`\\b${w.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')}\\b`, 'i').test(panelTexts.join('\n')));
  check('NPG-11', tops.every(n => n === 1) && wallMarks === 0 && rowMarks.length > 0 && rowMarks.every(Boolean) && stepMarks.length > 0 && stepMarks.every(Boolean)
    && tileMarks.length === 5 && tileMarks.every(Boolean) && mainRight <= panelX && sent.role === 'l1' && sent.facts.cluster.cluster === 'FR-S-02'
    && vocabText.includes("Agent E2's answer used words that are not used on this screen") && !/CPU Ready/.test(vocabText) && panelBad.length === 0,
    `top marks ${tops}; wall ${wallMarks}; rows ${rowMarks.length}; steps ${stepMarks.length}; tiles ${tileMarks.length}; main right ${Math.round(mainRight)} <= panel ${Math.round(panelX)}; role ${sent.role}; avoided in panel: ${panelBad.join(', ') || 'none'}`);

  // NPG-8 no request leaves the PCM host; contrast on desk and wall
  const contrast = async () => page.evaluate(() => {
    const parse = c => (c.match(/[\d.]+/g) || []).map(Number);
    const lum = ([r, g, b]) => [r, g, b].map(v => { v /= 255; return v <= 0.03928 ? v / 12.92 : ((v + 0.055) / 1.055) ** 2.4; }).reduce((a, v, i) => a + v * [0.2126, 0.7152, 0.0722][i], 0);
    const bgOf = el => { for (let e = el; e; e = e.parentElement) { const c = parse(getComputedStyle(e).backgroundColor); if (c.length === 3 || (c.length === 4 && c[3] > 0.5)) return c.slice(0, 3); } return [255, 255, 255]; };
    const fails = [];
    for (const el of document.querySelectorAll('body *')) {
      if (![...el.childNodes].some(n => n.nodeType === 3 && n.textContent.trim()) || el.offsetParent === null) continue;
      const [a, b] = [lum(parse(getComputedStyle(el).color).slice(0, 3)), lum(bgOf(el))].sort((x, y) => y - x);
      const r = (a + 0.05) / (b + 0.05);
      if (r < 4.5) fails.push(`${el.className || el.tagName} ${r.toFixed(2)} "${el.textContent.trim().slice(0, 24)}"`);
    }
    return fails;
  });
  await reset();
  const fails = [];
  for (const [p, x] of [['/noc', ''], ['/noc/alerts', ''], ['/noc/alert/inc-fr-s-02', ''], ['/noc/shift', ''], ['/noc/wall', '&screen=fast'], ['/noc/wall', '&screen=changed'], ['/noc/wall', '&screen=safe'], ['/noc/wall', '&enable=E-7&screen=up']]) {
    await go(p, x); fails.push(...(await contrast()).map(f => `${p}: ${f}`));
  }
  const foreign = [...hosts].filter(h => h !== `127.0.0.1:${PORT}`);
  check('NPG-8', fails.length === 0 && foreign.length === 0, (fails.slice(0, 4).join(' | ') || 'all text at least 4.5:1') + (foreign.length ? `; foreign hosts ${foreign}` : '; no foreign request'));

  // Screenshots for review.
  mkdirSync(ROOT + 'build/screenshots', { recursive: true });
  await reset();
  const tv = await browser.newPage({ viewport: { width: 1920, height: 1080 }, deviceScaleFactor: 1 });
  for (const s of ['fast', 'changed', 'safe']) {
    await tv.goto(BASE + '/noc/wall' + q(`&screen=${s}`)); await tv.waitForSelector('body[data-ready="1"]');
    await tv.screenshot({ path: ROOT + `build/screenshots/noc-wall-${s}.png` });
  }
  await tv.goto(BASE + '/noc/wall' + q('&enable=E-7&screen=up')); await tv.waitForSelector('body[data-ready="1"]');
  await tv.screenshot({ path: ROOT + 'build/screenshots/noc-wall-up-stale-europe.png' });
  const desk = await browser.newPage({ viewport: { width: 1440, height: 1000 }, deviceScaleFactor: 2 });
  await desk.goto(BASE + '/noc/alert/inc-fr-s-02' + q()); await desk.waitForSelector('body[data-ready="1"]');
  await desk.click('button[data-action="stop_provisioning"]'); await desk.waitForTimeout(400);
  await desk.screenshot({ path: ROOT + 'build/screenshots/noc-incident-sop.png', fullPage: true });
  await desk.goto(BASE + '/noc' + q()); await desk.waitForSelector('body[data-ready="1"]');
  await desk.click('.cellbtn.red'); await desk.waitForTimeout(300);
  await desk.screenshot({ path: ROOT + 'build/screenshots/noc-desk-fast.png', fullPage: true });
  await desk.goto(BASE + '/noc/alert/inc-fr-s-02' + q()); await desk.waitForSelector('body[data-ready="1"]');
  await desk.click('main h1 .e2mark'); await desk.waitForSelector('#e2 [data-sugg]');
  await desk.click('#e2 [data-sugg="0"]'); await desk.waitForSelector('#e2 [data-draft]', { timeout: 30000 }); await desk.waitForTimeout(300);
  await desk.screenshot({ path: ROOT + 'build/screenshots/noc-agent-e2-panel.png' });
} finally {
  await browser.close();
  await reset().catch(() => {});
  server.kill(); stub.close();
}
const failed = results.filter(r => !r.ok);
console.log(`\n${results.length - failed.length} passed, ${failed.length} failed`);
process.exit(failed.length ? 1 : 0);
