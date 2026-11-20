// Rehearse the demo: click through every step of demo/README.md in a real browser and check that each screen
// still says what the script says. Writes one screenshot per step to demo/screens/ (a handout).
// Run from the repository root:  node demo/rehearse.mjs
import { spawn } from 'node:child_process';
import { mkdirSync, mkdtempSync, rmSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { createRequire } from 'node:module';
const { chromium } = createRequire(import.meta.url)('playwright');

const ROOT = new URL('../', import.meta.url).pathname;
const PORT = 8771;
const NOW = '2026-10-19T10:05:00+08:00';
const DBDIR = mkdtempSync(tmpdir() + '/pcm-demo-');
const server = spawn('python3', ['-m', 'build.pcm_proto.server', '--port', String(PORT)],
  { cwd: ROOT, stdio: 'inherit', env: { ...process.env, PCM_DB: DBDIR + '/demo.sqlite', PCM_AGENT_E2_MODE: 'mock' } });
for (let i = 0; i < 50; i++) { try { await fetch(`http://127.0.0.1:${PORT}/exec`); break; } catch { await new Promise(r => setTimeout(r, 200)); } }
const BASE = `http://127.0.0.1:${PORT}`, q = `now=${encodeURIComponent(NOW)}`;
const url = (p, extra = '') => `${BASE}${p}?${q}${extra}`;

const results = [];
const step = (id, ok, detail) => { results.push(ok); console.log(`${ok ? 'OK  ' : 'FAIL'} ${id}${detail ? ' - ' + detail : ''}`); };
mkdirSync(ROOT + 'demo/screens', { recursive: true });
const browser = await chromium.launch();
try {
  // The audience's view: Singapore time, a laptop screen.
  const ctx = await browser.newContext({ timezoneId: 'Asia/Singapore', viewport: { width: 1440, height: 900 }, deviceScaleFactor: 2 });
  const page = await ctx.newPage();
  const go = async (p, extra) => { await page.goto(url(p, extra)); await page.waitForSelector('body[data-ready="1"]'); };
  const shot = (name, full = false) => page.screenshot({ path: ROOT + `demo/screens/${name}.png`, fullPage: full });
  const text = () => page.innerText('body');
  await fetch(url('/api/noc/_reset'), { method: 'POST', body: '{}' });

  // 1. CIO page
  await go('/exec');
  let t = await text();
  step('1 CIO: three questions, safe red with 72 VMs, Singapore order date in the plan',
    /Is it up\?/.test(t) && /Is it fast\?/.test(t) && /Is it safe\?/.test(t) && /\b72\b/.test(t) && /18 Nov/.test(t) && /In the plan/.test(t));
  await shot('1-cio');
  await page.click('#health-cards button[data-q="fast"]');
  await page.waitForSelector('body[data-panel="fast-7"]');
  step('1 CIO: fast detail says Gold above Silver above Bronze', (await page.innerText('#health-panel')).includes('Gold scored above Silver'));
  await page.locator('#health').screenshot({ path: ROOT + 'demo/screens/1-cio-fast.png' });

  // 2. NOC wall
  await page.goto(url('/noc/wall', '&screen=fast')); await page.waitForSelector('body[data-ready="1"]');
  t = await text();
  const strip = await page.$$eval('#strip .s', els => els.map(e => `${e.dataset.screen}:${[...e.classList].find(c => ['red', 'amber', 'green', 'no_data'].includes(c))}`));
  step('2 Wall: "What changed?" and "Is it fast?" red; FR-S-02 at 22', strip.includes('changed:red') && strip.includes('fast:red') && /FR-S-02/.test(t) && /\b22\b/.test(t), strip.join(' '));
  await shot('2-wall');

  // 3. NOC incident
  await go('/noc/alert/inc-fr-s-02');
  const limit = page.locator('button[data-action="time_boxed_limit"]');
  const limitWhy = await page.innerText('main');
  step('3 Incident: limit disabled for a production VM; villain fr-bat-017', (await limit.isDisabled()) && /Production VM: escalate instead/.test(limitWhy) && /fr-bat-017/.test(limitWhy));
  await page.click('button[data-action="stop_provisioning"]'); await page.waitForTimeout(300);
  await page.click('button[data-agent="explain"]'); await page.waitForTimeout(500);
  await page.click('button[data-escalate]'); await page.waitForTimeout(400);
  const hist = await (await fetch(url('/api/noc/history'))).json();
  step('3 Incident: stop new VMs and escalate are recorded', ['stop_provisioning', 'escalate'].every(a => hist.some(h => h.action === a)), hist.map(h => h.action).join(', '));
  await shot('3-incident', true);

  // 4. L2 closes the loop
  await go('/l2/monthly');
  const before = await page.innerText('[data-rep="class_mismatch"]');
  await go('/l2/escalations');
  t = await text();
  step('4 L2: escalation arrived with CPU Ready and the villain', /CPU Ready/.test(t) && /fr-bat-017/.test(t));
  await page.click('button[data-rca="inc-fr-s-02"]'); await page.waitForSelector('body[data-agent]');
  const f = 'form[data-close="inc-fr-s-02"]';
  await page.fill(`${f} input[name="root_cause"]`, 'Bronze batch VM placed in a Silver cluster');
  await page.fill(`${f} input[name="corrective_action"]`, 'Move fr-bat-017 to FR-B-02');
  await page.selectOption(`${f} select[name="detection"]`, 'new_check_rule');
  await page.fill(`${f} input[name="detection_note"]`, 'Daily check flags class mismatch on placement');
  await page.click(`${f} button[type="submit"]`);
  const closed = await page.waitForFunction(() => /Closed with a cause, a fix and a detection decision/.test(document.body.innerText), null, { timeout: 5000 }).then(() => true, () => false);
  step('4 L2: closed with a cause, a fix and a detection decision', closed);
  await shot('4-l2-escalation', true);
  await go('/l2/monthly');
  const after = await page.innerText('[data-rep="class_mismatch"]');
  step('4 L2: monthly review shows the loop closed', /Still open/.test(before) && /Loop closed/.test(after), `${before.replace(/\s+/g, ' ')} -> ${after.replace(/\s+/g, ' ')}`);
  await page.locator('[data-rep="class_mismatch"]').screenshot({ path: ROOT + 'demo/screens/4-l2-loop-closed.png' });

  // 5. Policy as code
  await go('/l2');
  step('5 Policy: no "Make automatic" button', !(await text()).includes('Make automatic'));
  await page.click('button[data-propose="move_vms_between_clusters"]');
  await page.selectOption('#pf select[name="tier"]', 'automatic');
  await page.click('#pf button[type="submit"]'); await page.waitForSelector('body[data-policy-replayed]');
  const replay = await page.innerText('#replay');
  step('5 Policy: replay shows 18 of 23 automatic', /23 runs/.test(replay) && /\b18\b/.test(replay), replay.trim());
  await page.fill('#pf input[name="reason"]', 'Guardrails replace approval');
  await page.click('#publish');
  await page.waitForFunction(() => /Published v2/.test(document.body.innerText), null, { timeout: 5000 }).catch(() => {});
  const msg = await page.innerText('main');
  step('5 Policy: published v2; the waiting move ran automatically', /Published v2/.test(msg) && /p-move-sg-s-04/.test(msg));
  await shot('5-policy');

  // 6. Capacity
  await go('/capacity');
  const moved = await page.innerText('[data-moved="FR-Silver"]');
  step('6 Capacity: FR-Silver 130 days earlier because of the OpenShift migration', /130 days earlier/.test(moved) && /dr-ocp-wave-2/.test(moved), moved);
  await shot('6-capacity-week');
  await go('/capacity/clusters');
  const fr = await page.innerText('[data-row="FR-Silver"]');
  step('6 Capacity: FR-Silver full now on FR-S-02 at 22', /Full now: VMs waiting/.test(fr) && /FR-S-02 \(score 22\)/.test(fr), fr.replace(/\s+/g, ' '));
  await shot('6-capacity-clusters', true);
  await go('/capacity/waste');
  const avoid = await page.getAttribute('[data-avoid]', 'data-avoid');
  await go('/exec');
  await page.click('#value-cards button[data-card="cost"]');
  await page.waitForFunction(() => document.querySelector('#value-panel') && !document.querySelector('#value-panel').hidden);
  const cio = await page.innerText('#value-panel');
  step('6 Capacity: cost avoidance $3,588,000, shown as $3.6M on the CIO page', avoid === '3588000' && /Could still avoid in the next purchase round\s*\$3\.6M/.test(cio), `waste page ${avoid}; CIO page shows it rounded`);
  await go('/capacity/waste'); await shot('6-capacity-waste');

  // 7. Docs
  await go('/docs/threshold/th-cluster-perf-red');
  const used = await page.$$eval('[data-used]', els => els.map(e => e.dataset.used));
  step('7 Docs: threshold used on the wall, the incident and Capacity', ['/noc/wall', '/noc/alert/{id}', '/capacity/clusters'].every(u => used.includes(u)), used.join(', '));
  await shot('7-docs-threshold', true);
  await go('/docs/policy/move_vms_between_clusters');
  const v = await page.innerText('[data-version]');
  const h = await page.locator('[data-history]').count();
  step('7 Docs: policy version 2 with the publish in its history', v === '2' && h === 1, `version ${v}, ${h} history row`);
  await shot('7-docs-policy', true);
} finally {
  await browser.close(); server.kill(); rmSync(DBDIR, { recursive: true, force: true });
}
const failed = results.filter(ok => !ok).length;
console.log(`\n${results.length - failed} steps OK, ${failed} failed`);
process.exit(failed ? 1 : 0);
