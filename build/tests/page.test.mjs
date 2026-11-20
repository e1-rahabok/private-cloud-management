// Page tests PG-2 to PG-9 for /exec, in a real browser.
// GENERATED from spec/tests/executive.yaml. Do not edit by hand (D-070).
// Run from the repository root:  node build/tests/page.test.mjs
import { spawn } from 'node:child_process';
import { readFileSync, mkdirSync } from 'node:fs';
import { createRequire } from 'node:module';
const require = createRequire(import.meta.url);
const { chromium } = require('playwright');

const ROOT = new URL('../../', import.meta.url).pathname;
const PORT = 8765;
const specTests = readFileSync(ROOT + 'spec/tests/executive.yaml', 'utf8');
const NOW = specTests.match(/^now:\s*"([^"]+)"/m)[1];
const vocab = readFileSync(ROOT + 'spec/catalog/vocabulary/executive.yaml', 'utf8');
const avoided = vocab.split('avoided:')[1].split('labels:')[0].split('\n')
  .map(l => l.trim()).filter(l => l.startsWith('- ')).map(l => l.slice(2).trim());

const server = spawn('python3', ['-m', 'build.pcm_proto.server', '--port', String(PORT)], { cwd: ROOT, stdio: 'inherit' });
await new Promise(r => setTimeout(r, 800));

const results = [];
const check = (id, ok, detail = '') => { results.push({ id, ok, detail }); console.log(`${ok ? 'PASS' : 'FAIL'} ${id}${detail ? ' - ' + detail : ''}`); };
const base = `http://127.0.0.1:${PORT}/exec?now=${encodeURIComponent(NOW)}`;

const browser = await chromium.launch();
try {
  const page = await browser.newPage({ viewport: { width: 1360, height: 900 } });

  async function load(extra = '') {
    await page.goto(base + extra);
    await page.waitForSelector('body[data-ready="1"]');
  }

  // Open every drill-down in turn and collect all visible text, in every state.
  async function allText() {
    const texts = [await page.innerText('body')];
    const n = await page.locator('button.more, button.tower').count();
    for (let i = 0; i < n; i++) {
      await page.locator('button.more, button.tower').nth(i).click(); await page.waitForTimeout(150);
      texts.push(await page.innerText('body'));
      for (const days of ['30', '7']) {
        const sw = page.locator(`.switch button[data-days="${days}"]`);
        if (await sw.count()) { await sw.first().click(); await page.waitForTimeout(150); texts.push(await page.innerText('body')); }
      }
    }
    return texts.join('\n');
  }

  // ---- normal state
  await load();
  const normal = await allText();
  // ---- stale state (story E-7)
  await load('&enable=E-7');
  const stale = await allText();

  // PG-2 vocabulary
  const bad = [];
  for (const w of avoided) {
    const re = new RegExp(`\\b${w.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')}\\b`, 'i');
    if (re.test(normal) || re.test(stale)) bad.push(w);
  }
  check('PG-2', bad.length === 0, bad.length ? `avoided words found: ${bad.join(', ')}` : 'no avoided word in any state');

  // PG-3 no "Live" in the header
  await load();
  const header = await page.innerText('header');
  check('PG-3', !/\bLive\b/.test(header), header.replace(/\s+/g, ' ').slice(0, 80));

  // PG-4 stale locations grey, "No data", no number
  await load('&enable=E-7');
  const pg4 = await page.evaluate(() => ['fr', 'ld', 'sg'].map(id => {
    const t = document.querySelector(`.tower[data-loc="${id}"]`);
    return { id, stale: t.classList.contains('stale'), nodata: t.innerText.includes('No data') };
  }));
  const fr = pg4.find(x => x.id === 'fr'), ld = pg4.find(x => x.id === 'ld'), sg = pg4.find(x => x.id === 'sg');
  await page.click('.tower[data-loc="fr"]'); await page.waitForTimeout(200);
  const frPanel = await page.innerText('#location-panel');
  const noUseNumber = !/\d+(\.\d+)?% in use/.test(frPanel);
  const headerWarn = (await page.innerText('header')).includes('Some data is out of date');
  check('PG-4', fr.stale && fr.nodata && ld.stale && ld.nodata && !sg.stale && noUseNumber && headerWarn,
    `fr ${JSON.stringify(fr)} ld ${JSON.stringify(ld)} sg stale=${sg.stale} in-use hidden=${noUseNumber} header warning=${headerWarn}`);

  // PG-5 site recovery label and footnote
  await load();
  const label = await page.innerText('#value-cards article:nth-child(2) h3');
  await page.click('#value-cards button[data-card="site_recovery"]'); await page.waitForTimeout(200);
  const srPanel = await page.innerText('#value-panel');
  check('PG-5', label.startsWith('Site recovery') && srPanel.includes('Backups are not included.'), label.split('\n')[0]);

  // PG-6 no "saving"
  check('PG-6', !/saving/i.test(normal) && !/saving/i.test(stale));

  // PG-7 in-plan chip
  const chip = await page.$eval('#grow-body .chip', el => ({ cls: el.className, text: el.innerText }));
  check('PG-7', chip.cls.includes('in_plan') && chip.text === 'In the plan', JSON.stringify(chip));

  // PG-8 one panel per section, with Close
  await load();
  await page.click('#health-cards button[data-q="up"]'); await page.waitForTimeout(200);
  await page.click('#health-cards button[data-q="fast"]'); await page.waitForTimeout(200);
  const pg8 = await page.evaluate(() => ({
    expanded: [...document.querySelectorAll('#health-cards button.more')].filter(b => b.getAttribute('aria-expanded') === 'true').length,
    panels: document.querySelectorAll('#health .panel:not([hidden])').length,
    close: !!document.querySelector('#health-panel button.close'),
    title: document.querySelector('#health-panel h3')?.innerText,
  }));
  await page.click('#health-panel button.close'); await page.waitForTimeout(100);
  const closed = await page.$eval('#health-panel', el => el.hidden);
  check('PG-8', pg8.expanded === 1 && pg8.panels === 1 && pg8.close && pg8.title === 'Is it fast?' && closed, JSON.stringify({ ...pg8, closed }));

  // PG-9 contrast >= 4.5:1 for all text, every status chip has text
  await load();
  const pg9 = await page.evaluate(() => {
    const parse = c => (c.match(/[\d.]+/g) || []).map(Number);
    const lum = ([r, g, b]) => [r, g, b].map(v => { v /= 255; return v <= 0.03928 ? v / 12.92 : ((v + 0.055) / 1.055) ** 2.4; })
      .reduce((a, v, i) => a + v * [0.2126, 0.7152, 0.0722][i], 0);
    const bgOf = el => { for (let e = el; e; e = e.parentElement) { const c = parse(getComputedStyle(e).backgroundColor); if (c.length === 3 || (c.length === 4 && c[3] > 0.5)) return c.slice(0, 3); } return [255, 255, 255]; };
    const fails = [];
    for (const el of document.querySelectorAll('body *')) {
      const own = [...el.childNodes].some(n => n.nodeType === 3 && n.textContent.trim());
      if (!own || el.offsetParent === null) continue;
      const fg = parse(getComputedStyle(el).color).slice(0, 3), bg = bgOf(el);
      const [a, b] = [lum(fg), lum(bg)].sort((x, y) => y - x);
      const ratio = (a + 0.05) / (b + 0.05);
      if (ratio < 4.5) fails.push(`${el.className || el.tagName}: ${ratio.toFixed(2)} "${el.textContent.trim().slice(0, 30)}"`);
    }
    const emptyChips = [...document.querySelectorAll('.chip')].filter(c => !c.innerText.trim()).length;
    return { fails, emptyChips };
  });
  check('PG-9', pg9.fails.length === 0 && pg9.emptyChips === 0, pg9.fails.slice(0, 5).join(' | ') || 'all text at least 4.5:1');

  // Screenshots for the author's review (deviceScaleFactor 2).
  mkdirSync(ROOT + 'build/screenshots', { recursive: true });
  const shot = await browser.newPage({ viewport: { width: 1360, height: 900 }, deviceScaleFactor: 2 });
  await shot.goto(base); await shot.waitForSelector('body[data-ready="1"]');
  await shot.screenshot({ path: ROOT + 'build/screenshots/exec-full.png', fullPage: true });
  await shot.click('#value-cards button[data-card="site_recovery"]'); await shot.waitForTimeout(200);
  await shot.locator('#value').screenshot({ path: ROOT + 'build/screenshots/exec-site-recovery.png' });
  await shot.goto(base); await shot.waitForSelector('body[data-ready="1"]');
  await shot.click('#health-cards button[data-q="safe"]'); await shot.waitForTimeout(250);
  await shot.locator('#health').screenshot({ path: ROOT + 'build/screenshots/exec-health-safe.png' });
  await shot.click('#health-cards button[data-q="fast"]'); await shot.waitForTimeout(250);
  await shot.locator('#health').screenshot({ path: ROOT + 'build/screenshots/exec-health-fast.png' });
  await shot.goto(base + '&enable=E-7'); await shot.waitForSelector('body[data-ready="1"]');
  await shot.locator('#scale').screenshot({ path: ROOT + 'build/screenshots/exec-stale-europe.png' });
} finally {
  await browser.close();
  server.kill();
}
const failed = results.filter(r => !r.ok);
console.log(`\n${results.length - failed.length} passed, ${failed.length} failed`);
process.exit(failed.length ? 1 : 0);
