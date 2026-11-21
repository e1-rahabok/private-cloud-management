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

  // 4. L2 Monitor: top down over the whole estate
  await go('/l2');
  t = await text();
  const pillars = await page.$$eval('tr[data-pillar]', r => r.map(x => x.dataset.pillar));
  step('4 L2 Monitor: estate, 24 hours, one row per pillar, Europe red in the tree', pillars.length === 6 && /Findings, worst first/.test(t)
    && (await page.getAttribute('li[data-node="emea"] .dot', 'class')).includes('red'), pillars.join(', '));
  await shot('4-l2-monitor');
  await go('/l2/monitor/compute/ld/performance', '&window=7d&group=host_model');
  const gen19 = (await page.innerText('[data-group="Gen-2019, 2 x 20 cores"]')).split('\t').map(s => s.trim())[5];
  const gen24 = (await page.innerText('[data-group="Gen-2024, 2 x 32 cores"]')).split('\t').map(s => s.trim())[5];
  step('4 L2 Monitor: London, 7 days, group by host model: 9 VMs wider than a Gen-2019 NUMA node, 0 on Gen-2024', gen19 === '9' && gen24 === '0', `${gen19} / ${gen24}`);
  await shot('4-l2-group-by');

  // 5. L2 Troubleshoot: the escalation is a case; the loop closes with a detection
  await go('/l2/monitor/compute/estate/summary', '&window=1y');
  const before = await page.innerText('[data-rep="class_mismatch"]');
  await go('/l2/troubleshoot/compute/estate');
  step('5 L2 Troubleshoot: the NOC escalation is a case, beside the Tokyo escalation and a complaint',
    await page.isVisible('tr[data-case="case-inc-fr-s-02"]') && await page.isVisible('tr[data-case="case-inc-tk-s-03"]') && await page.isVisible('tr[data-case="case-sg-app-117"]'));
  await go('/l2/troubleshoot/case/case-inc-fr-s-02');
  t = await text();
  step('5 L2 Troubleshoot: escalation arrived with CPU Ready and the villain', /CPU Ready/.test(t) && /fr-bat-017/.test(t));
  await page.click('[data-accept]'); await page.waitForSelector('[data-accept]', { state: 'detached' });
  page.on('dialog', d => d.accept('One VM explains the change: the cluster ran at 94 an hour ago'));
  for (let i = 1; i <= 4; i++) { await page.click('#propose'); await page.waitForFunction(n => document.querySelectorAll('[data-link]').length >= n, i); }
  for (const id of ['l1-wait', 'l1-villain', 'l1-class']) { await page.click(`[data-confirm="${id}"]`); await page.waitForSelector(`[data-link="${id}"].confirmed`); }
  await page.click('[data-ruleout="l1-hosts"]'); await page.waitForSelector('[data-link="l1-hosts"].ruled_out');
  step('5 L2 Troubleshoot: the prefilled root cause is the deepest confirmed link', (await page.inputValue('#close input[name="root_cause"]')) === 'fr-bat-017 is a Bronze VM placed in a Silver cluster');
  await page.click('#draft'); await page.waitForSelector('body[data-agent]');
  await page.fill('#close input[name="corrective_action"]', 'Move fr-bat-017 to FR-B-02');
  await page.selectOption('#close select[name="detection"]', 'new_check_rule');
  await page.fill('#close input[name="detection_note"]', 'Daily check flags class mismatch on placement');
  await page.click('#close button[type="submit"]');
  const closed = await page.waitForSelector('[data-closed]', { timeout: 5000 }).then(() => true, () => false);
  step('5 L2 Troubleshoot: closed with a cause, a fix and a detection decision', closed);
  await shot('5-l2-case', true);
  await go('/l2/monitor/compute/estate/summary', '&window=1y');
  const after = await page.innerText('[data-rep="class_mismatch"]');
  step('5 L2: the 1-year view shows the loop closed', /Still open/.test(before) && /Loop closed/.test(after), `${before.replace(/\s+/g, ' ')} -> ${after.replace(/\s+/g, ' ')}`);
  await page.locator('[data-rep="class_mismatch"]').screenshot({ path: ROOT + 'demo/screens/5-l2-loop-closed.png' });

  // 5b. A complaint, several layers deep (optional in the room)
  await go('/l2/troubleshoot/new', '&vm=sg-gl-db-01');
  await page.fill('input[name="requester"]', 'General ledger application owner');
  await page.fill('input[name="via"]', 'Head of finance systems');
  await Promise.all([page.waitForURL(/\/case\//), page.click('#cf button[type="submit"]')]); await page.waitForSelector('body[data-ready="1"]');
  for (let i = 1; i <= 9; i++) { await page.click('#propose'); await page.waitForFunction(n => document.querySelectorAll('[data-link]').length >= n, i); }
  const tl = await page.innerText('.timeline');
  step('5b L2 complaint: nine links proposed; the timeline reaches back to the weekend change window', (await page.$$('[data-link]')).length === 9 && /CHG0042117/.test(tl));
  await shot('5b-l2-complaint', true);

  // 6. Policy as code, in Rules
  await go('/l2/rules');
  step('6 Policy: no "Make automatic" button', !(await text()).includes('Make automatic'));
  await page.click('button[data-propose="move_vms_between_clusters"]');
  await page.selectOption('#pf select[name="tier"]', 'automatic');
  await page.click('#pf button[type="submit"]'); await page.waitForSelector('body[data-policy-replayed]');
  const replay = await page.innerText('#replay');
  step('6 Policy: replay shows 18 of 23 automatic', /23 runs/.test(replay) && /\b18\b/.test(replay), replay.trim());
  await page.fill('#pf input[name="reason"]', 'Guardrails replace approval');
  await page.click('#publish');
  await page.waitForFunction(() => /Published v2/.test(document.body.innerText), null, { timeout: 5000 }).catch(() => {});
  const msg = await page.innerText('main');
  step('6 Policy: published v2; the waiting move ran automatically', /Published v2/.test(msg) && /p-move-sg-s-04/.test(msg));
  await shot('6-policy');

  // 7. Capacity
  await go('/capacity');
  const moved = await page.innerText('[data-moved="FR-Silver"]');
  step('7 Capacity: FR-Silver 130 days earlier because of the OpenShift migration', /130 days earlier/.test(moved) && /dr-ocp-wave-2/.test(moved), moved);
  await shot('7-capacity-week');
  await go('/capacity/clusters');
  const ldb = await page.innerText('[data-row="LD-Bronze"]');
  step('7 Capacity: LD-Bronze closed for new VMs on LD-B-01', /Closed for new VMs/.test(ldb) && /LD-B-01/.test(ldb), ldb.replace(/\s+/g, ' '));
  await shot('7-capacity-clusters', true);
  await go('/capacity/waste');
  const avoid = await page.getAttribute('[data-avoid]', 'data-avoid');
  await go('/exec');
  await page.click('#value-cards button[data-card="cost"]');
  await page.waitForFunction(() => document.querySelector('#value-panel') && !document.querySelector('#value-panel').hidden);
  const cio = await page.innerText('#value-panel');
  step('7 Capacity: cost avoidance $3,588,000, shown as $3.6M on the CIO page', avoid === '3588000' && /Could still avoid in the next purchase round\s*\$3\.6M/.test(cio), `waste page ${avoid}; CIO page shows it rounded`);
  await go('/capacity/waste'); await shot('7-capacity-waste');

  // 8. Docs
  await go('/docs/threshold/th-cluster-perf-red');
  const used = await page.$$eval('[data-used]', els => els.map(e => e.dataset.used));
  step('8 Docs: threshold used on the wall, the incident and Capacity', ['/noc/wall', '/noc/alert/{id}', '/capacity/clusters'].every(u => used.includes(u)), used.join(', '));
  await shot('8-docs-threshold', true);
  await go('/docs/policy/move_vms_between_clusters');
  const v = await page.innerText('[data-version]');
  const h = await page.locator('[data-history]').count();
  step('8 Docs: policy version 2 with the publish in its history', v === '2' && h === 1, `version ${v}, ${h} history row`);
  await shot('8-docs-policy', true);
} finally {
  await browser.close(); server.kill(); rmSync(DBDIR, { recursive: true, force: true });
}
const failed = results.filter(ok => !ok).length;
console.log(`\n${results.length - failed} steps OK, ${failed} failed`);
process.exit(failed ? 1 : 0);
