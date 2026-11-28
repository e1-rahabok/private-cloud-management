// Page tests LPG-2 to LPG-32 for /l2 (Monitor, Troubleshoot, Improve, Rules, Calendar), in a real browser.
// GENERATED from pcm/l2/spec/acceptance-tests.yaml. Do not edit by hand (D-070).
// Run from the repository root:  node pcm/l2/tests/l2.page.test.mjs
import { spawn } from 'node:child_process';
import { createServer } from 'node:http';
import { readFileSync, mkdirSync } from 'node:fs';
import { createRequire } from 'node:module';
const { chromium } = createRequire(import.meta.url)('playwright');

const ROOT = new URL('../../../', import.meta.url).pathname;  // the repository root
const HERE = new URL('../', import.meta.url).pathname;  // the workspace folder
const PORT = 8768;
const NOW = readFileSync(HERE + 'spec/acceptance-tests.yaml', 'utf8').match(/^now:\s*"([^"]+)"/m)[1];
const avoided = readFileSync(HERE + 'spec/vocabulary.yaml', 'utf8').split('avoided:')[1].split('labels:')[0]
  .split('\n').map(l => l.trim()).filter(l => l.startsWith('- ')).map(l => l.slice(2).trim());
// PCM points at a stub Agent E2 service (PCM_AGENT_E2_URL). It is not running for LPG-8 (the unavailable state); LPG-20 and LPG-21 start it.
// Each page test owns its ports, so tests can run side by side (specification-structure.md, section 4).
const E2_PORT = 8772;
const server = spawn('python3', ['-m', 'pcm.core.server', '--port', String(PORT)], { cwd: ROOT, stdio: 'inherit', env: { ...process.env, PCM_DEMO_SWITCHER: '0', PCM_AGENT_E2_MODE: 'mock', PCM_DB: ':memory:', PCM_AGENT_E2_URL: `http://127.0.0.1:${E2_PORT}` } });
const E2_SEEN = [], E2_TOPIC = [];  // answer requests; topic requests (D-130)
const E2_ANSWER = 'No. A Guest OS Run Queue of 0.38 per vCPU at the 95th percentile is not a CPU shortage inside fr-svc-5526.\n\nCheck next: VM CPU Ready on the same hour, then the host fr-esx-218.';
const stub = createServer((req, res) => {
  let b = ''; req.on('data', c => { b += c; }); req.on('end', () => {
    const send = d => { res.writeHead(200, { 'Content-Type': 'application/json' }); res.end(JSON.stringify(d)); };
    if (req.url === '/v1/health') return send({ ok: true, model: 'stub-model', files: 286 });
    const body = JSON.parse(b || '{}');
    // The stub's topic decision (D-129): the person's choice; else a question on Memory Zip Swap is a new topic; else it continues.
    const h = body.history || [], ch = body.topic_choice || 'auto';
    const topic = ch !== 'auto' ? { continues: ch === 'continue' && h.length > 0, by: 'user' } : !h.length ? { continues: false, by: 'first' }
      : { continues: !/Zip Swap/i.test(body.question), by: 'model' };
    // An Agent E2 older than topics (D-130): no /v1/topic, and no topic in its answer.
    const old = /old service/i.test(body.question || '');
    if (req.url === '/v1/topic') {
      E2_TOPIC.push(body);
      if (old) { res.writeHead(404, { 'Content-Type': 'application/json' }); return res.end('{"error":"not found"}'); }
      return send(topic);
    }
    E2_SEEN.push(body);
    if (!body.turns && /which counter/i.test(body.question)) return send({ type: 'clarify', content: '', questions: ['Do you mean the Guest OS Run Queue or the VM CPU Ready?'], files_read: [], computed: [], model: 'stub-model', knowledge_commit: 'abc1234' });
    // Agent E2 writes its opening as one bullet per KPI when the facts hold several (D-119).
    const kpis = (body.facts && body.facts.kpis) || [];
    const lead = kpis.length > 1 ? kpis.map(k => `- ${k.label || k.name} stayed within its normal movement.`).join('\n') : 'Peak vCPU run queue length is 1.5 threads waiting, 0.38 per vCPU.';
    const out = { type: 'answer', content: E2_ANSWER, questions: [], files_read: ['guest-os/cpu/metrics/run-queue', 'vsphere/technology/cpu/metrics/vm/ready'], lead, computed: ['0.38 per vCPU × 4 vCPU = 1.5 threads waiting'], topic: old ? undefined : topic, model: 'stub-model', knowledge_commit: 'abc1234' };
    // A slow answer, so the test can flip the topic while it is written (D-130).
    if (/slowly/i.test(body.question || '') && ch === 'continue') return setTimeout(() => send(out), 3000);
    send(out);
  });
});
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
  '/l2/improve/compute/estate/summary', '/l2/improve/compute/estate/configuration', '/l2/improve/compute/estate/capacity', '/l2/rules', '/l2/calendar',
  '/l2/monitor/compute/LD-B-01/capacity?window=7d', '/l2/monitor/compute/wld-fr-gen/capacity?window=7d&class=bronze', '/l2/monitor/compute/FR-S-02/capacity'];
const CAPACITY_PAGES = ['/l2/monitor/compute/LD-B-01/capacity?window=7d', '/l2/monitor/compute/LD-B-01/capacity', '/l2/monitor/compute/wld-fr-gen/capacity?window=7d&class=bronze',
  '/l2/monitor/compute/wld-fr-gen/capacity', '/l2/monitor/compute/estate/capacity?class=all', '/l2/monitor/compute/FR-S-02/capacity', '/l2/monitor/compute/ld-esx-202/capacity?window=30d'];
const capAvoided = readFileSync(HERE + 'spec/vocabulary.yaml', 'utf8').match(/^capacity_tab_avoided:\s*\[(.*)\]/m)[1].split(',').map(w => w.trim());
const capGroupAvoided = readFileSync(HERE + 'spec/vocabulary.yaml', 'utf8').match(/^capacity_group_avoided:\s*\[(.*)\]/m)[1].split(',').map(w => w.trim());
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
  const win = (await page.innerText('.winbtn .lbl')).trim();
  check('LPG-4', landed === '/l2/monitor/compute/estate/summary' && rows.join() === 'availability,performance,capacity,security,configuration,inventory' && win === 'Last 24 hours' && !/health score/i.test(await page.innerText('main')), `${landed}; ${rows.length} pillar rows; ${win}`);

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

  // LPG-8 Agent E2 service not running: a grey mark, and the panel says so
  await page.waitForSelector('body[data-e2="down"]');
  const offLabel = await page.getAttribute('#e2top', 'aria-label'), offGrey = await page.$eval('#e2top', b => b.classList.contains('off'));
  await page.click('.objhead .e2mark'); await page.waitForSelector('#e2 [data-sugg]');
  await page.click('#e2 [data-sugg]'); await page.waitForSelector('#e2 .e2a', { timeout: 30000 });
  const askText = await page.innerText('#e2 .e2a');
  const noAnswer = !(await page.$('#e2 .e2src')) && !(await page.$('#e2 .e2lead'));
  await page.keyboard.press('Escape');
  check('LPG-8', offLabel === 'Agent E2 is not available' && offGrey && askText.includes('The Agent E2 service is not available') && noAnswer, `${offLabel}; ${askText.split('\n')[0]}`);

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

  // LPG-17 a cluster's Capacity tab: the verdict, the three KPIs in the rule's order, the strip, statistics named
  await go('/l2/monitor/compute/LD-B-01/capacity?window=7d');
  const capOrder = await page.evaluate(() => [...document.querySelectorAll('[data-verdict], [data-kpi], [data-strip]')].map(e => e.dataset.verdict ? 'verdict' : e.dataset.kpi || 'strip'));
  const verdictText = await page.innerText('[data-verdict]');
  const kpiLabels = await page.$$eval('[data-kpi] dt', xs => xs.map(x => x.textContent.trim()));
  const checkLabels = await page.$$eval('[data-check-label]', xs => xs.map(x => x.textContent.trim()));
  const cells = await page.$$eval('[data-strip] .cell', xs => xs.map(x => x.className.replace('cell', '').trim()));
  const refs = await page.$$eval('[data-kpi] .legend, [data-kpi] .ref', xs => xs.length);
  const whyText = await page.innerText('[data-why]');
  const diag = await page.evaluate(() => ({ out: document.querySelector('[data-cd-out]')?.dataset.cdOut, hit: [...document.querySelectorAll('[data-cd-node].hit')].map(e => e.dataset.cdNode).join(), off: [...document.querySelectorAll('[data-cd-node].off')].map(e => e.dataset.cdNode).join() }));
  const capText = await page.innerText('main');
  const chipsCap = await page.$$eval('[data-section="capacity-cluster"] .chip', xs => xs.map(x => x.textContent.trim()));
  const capFindings = await page.$$eval('.finding', xs => xs.length) + await page.$$eval('[data-daily-finding] a', xs => xs.length);
  check('LPG-17', capOrder.join() === 'verdict,consumption,performance,risk,strip' && /^Closed for new VMs/.test(verdictText) && /Consumption 82% is above 80%\./.test(whyText)
    && diag.out === 'closed' && diag.hit === 'consumption' && diag.off === 'risk' && /above by 2 points/.test(whyText)
    && checkLabels.length === 0
    && ['Now', 'Worst', '95th percentile', '5th percentile'].every(k => kpiLabels.includes(k)) && cells.length === 7 && cells[6] === 'closed'
    && refs === 0 && !/average/i.test(capText) && chipsCap.includes('Closed for new VMs') && capFindings >= 1 && !/Nothing needs you under this object/.test(capText),
    `${capOrder}; ${verdictText.slice(0, 80)}; diagram ${JSON.stringify(diag)}; cells ${cells.length}; findings ${capFindings}`);

  // LPG-18 no forecast word on any Capacity tab; one link to the Capacity workspace
  const capBad = [];
  for (const p of CAPACITY_PAGES) {
    await go(p);
    const t = await page.innerText('#panel');
    const isGroup = !!(await page.$('[data-section="capacity-group"]')) || !!(await page.$('[data-empty]'));
    for (const w of isGroup ? [...capAvoided, ...capGroupAvoided] : capAvoided) {
      const re = w === 'imbalance' ? /(?<!CPU )\bimbalance\b/i : new RegExp(`\\b${w}\\b`, 'i');
      if (re.test(t)) capBad.push(`${p}: ${w}`);
    }
    const links = await page.$$('[data-months-ahead] a[href^="/capacity"]');
    if (links.length !== 1) capBad.push(`${p}: ${links.length} links to the Capacity workspace`);
  }
  check('LPG-18', capBad.length === 0, capBad.slice(0, 4).join(' | ') || `${CAPACITY_PAGES.length} Capacity tabs, no forecast word`);

  // LPG-19 the group page: Gold first, empty; Bronze one click away; a time and a cluster picked by click
  await go('/l2/monitor/compute/wld-fr-gen/capacity?window=7d');
  const goldSel = await page.innerText('nav[aria-label="Class of service"] a[aria-current="true"]');
  const empty = await page.innerText('[data-empty]').catch(() => '');
  await Promise.all([page.waitForURL(/class=bronze/), page.click('nav[aria-label="Class of service"] a[data-cls="bronze"]')]); await page.waitForSelector('body[data-ready="1"]');
  const capU1 = new URL(page.url());
  const capHit = page.locator('[data-chartbox="capspread"] rect.hit'); await capHit.scrollIntoViewIfNeeded();
  const cb = await capHit.boundingBox();
  await Promise.all([page.waitForURL(/[?&]at=/), capHit.click({ position: { x: cb.width * 0.6, y: 20 } })]); await page.waitForSelector('body[data-ready="1"]');
  const capAt = new URL(page.url()).searchParams.get('at');
  const capHead = await page.getAttribute('h3[data-at]', 'data-at');
  const capHeadText = await page.innerText('h3[data-at]');
  await Promise.all([page.waitForURL(/FR-B-04\/capacity/), page.click('tr[data-cluster-at="FR-B-04"] a')]); await page.waitForSelector('body[data-ready="1"]');
  const capU2 = new URL(page.url());
  check('LPG-19', goldSel === 'Gold' && empty === 'No Gold cluster under this object.' && capU1.pathname.endsWith('/wld-fr-gen/capacity') && capU1.searchParams.get('window') === '7d'
    && !!capAt && capHead === capAt && capHeadText.includes('the time you picked') && capU2.searchParams.get('window') === '7d',
    `${goldSel}; ${empty}; ${capU1.pathname}; at=${capAt}; ${capU2.pathname}${capU2.search}`);

  // LPG-15 a VM's Performance tab: two layers, statistics named, units after numbers
  await go('/l2/monitor/compute/fr-app-1272/performance?group=host_model');
  const tabsText = (await page.$$eval('nav.tabs a', xs => xs.map(x => x.textContent.trim()))).join();
  const layers = await page.$$eval('section.layer', xs => xs.map(x => x.dataset.layer));
  const names = await page.$$eval('.metric h4', xs => xs.map(x => x.textContent));
  const figs = await page.$$eval('.metric dd', xs => xs.map(x => x.textContent.trim()));
  const labels = await page.$$eval('.metric dt', xs => [...new Set(xs.map(x => x.textContent.trim()))]);
  const mainText = await page.innerText('main');
  check('LPG-15', tabsText === 'Summary,Availability,Performance,Capacity,Security,Configuration' && layers.join() === 'guest_os,virtual_motherboard' && names.length === 16
    && [...labels].sort().join() === '5th percentile,95th percentile,Now,Worst' && figs.every(f => /\d\+?(%|\/s| ms| per vCPU| pages\/s| IOs| MB)/.test(f)) && names.every(n => /^[A-Z]/.test(n) && !/percent| ms$|%/.test(n))
    && !(await page.$('#grp')) && !/side by side|Just above the line|Children outside green/i.test(mainText) && !/average/i.test(mainText),
    `${tabsText}; ${layers}; ${names.length} charts; ${figs.slice(0, 3)}`);

  // LPG-23 the KPI first: band figures on the Performance tabs, the remaining summary first on the Capacity tab (D-100)
  const lum = c => { const [r, g, b] = c.match(/\d+/g).slice(0, 3).map(x => { x = x / 255; return x <= 0.03928 ? x / 12.92 : ((x + 0.055) / 1.055) ** 2.4; }); return 0.2126 * r + 0.7152 * g + 0.0722 * b; };
  const ratio = (a, b) => { const [x, y] = [lum(a), lum(b)].sort((p, q) => q - p); return (x + 0.05) / (y + 0.05); };
  const band = v => v >= 75 ? 'green' : v >= 50 ? 'yellow' : v >= 25 ? 'orange' : 'red';
  const pills = async () => page.$$eval('.metric:not(.kpi-details .metric)', ms => ms.map(m => ({ key: m.dataset.metric || m.dataset.kpi, pills: [...m.querySelectorAll('dd')].map(d => { const p = d.querySelector('.bv'); if (!p) return null; const cs = getComputedStyle(p);
    return { band: p.dataset.band, text: p.textContent.trim(), v: parseFloat(p.textContent.replace(/,/g, '')), fg: cs.color, bg: cs.backgroundColor }; }) })));
  const pillsOk = (ms, hiw) => ms.every(m => m.pills.every(p => p === null || (p.band === band(hiw(m.key) ? 100 - p.v : p.v) && !/green|yellow|orange|red/i.test(p.text) && ratio(p.fg, p.bg) >= 4.5)));
  await go('/l2/monitor/compute/fr-bat-6839/performance');
  const vmFirst = await page.$eval('section.persp', s => s.dataset.section);
  const vmKpis = await page.$$eval('[data-section="performance-kpis"] .metric', ms => ms.map(m => m.dataset.metric));
  const vmLayerKpis = await page.$$eval('section.layer .metric', ms => ms.map(m => m.dataset.metric).filter(k => /performance/.test(k)));
  const vmPills = await pills();
  const VM_END = { run_queue_per_vcpu: [2, 4, 8], disk_queue: [20, 40, 80], free_memory_mb: [512, 256, 128], paging_per_s: [1000, 2000, 4000], cpu_ready_percent: [2, 4, 8], co_stop_percent: [1, 2, 4], cpu_overlap_percent: [0.5, 1, 2], memory_wait_percent: [0.5, 1, 2], disk_latency_ms: [10, 20, 40], network_dropped_tx_percent: [0, 0.5, 1], cpu_run_percent: [95, 97, 99], memory_ballooned_percent: [2, 4, 8], memory_zip_swap_percent: [0.25, 0.5, 1] };
  const endOf = (v, e) => ['green', 'yellow', 'orange'].find((_, i) => e[0] > e[1] ? v >= e[i] : v <= e[i]) || 'red';
  const counterPlain = vmPills.filter(m => !/performance/.test(m.key) && !VM_END[m.key]).every(m => m.pills.every(p => p === null))
    && vmPills.filter(m => VM_END[m.key]).length === 13 && vmPills.filter(m => VM_END[m.key]).every(m => m.pills.every(p => p !== null && p.band === endOf(p.v, VM_END[m.key])));
  const vmPillOk = pillsOk(vmPills.filter(m => /performance/.test(m.key)), () => false) && vmPills.filter(m => /performance/.test(m.key)).every(m => m.pills.every(p => p !== null));
  await go('/l2/monitor/compute/FR-B-04/performance');
  const clKpis = await page.$$eval('[data-section="performance-kpis"] .metric:not(.kpi-details .metric) h4', hs => hs.map(h => h.textContent));
  const clText = await page.innerText('main');
  const clPills = await pills();
  const clPillOk = pillsOk(clPills, k => k === 'cluster_risk') && clPills.filter(m => m.key.startsWith('cluster_')).every(m => m.pills.every(p => p !== null));
  const noCards = !/This object|Children outside green\n/.test(clText) && !(await page.$('.cards .card h3'));
  await go('/l2/monitor/compute/fr-esx-244/capacity');
  const capFirst = await page.evaluate(() => [...document.querySelectorAll('[data-section="capacity-summary"], [data-verdict]')].map(e => e.dataset.section ? 'summary' : 'verdict'));
  const rem = await page.$$eval('[data-remaining] h3', hs => hs.map(h => h.textContent));
  const placeholder = await page.innerText('[data-section="capacity-summary"]');
  const PART_KEYS = ['cpu_thread_utilization', 'memory_consumed', 'memory_ballooned', 'memory_zip_swap'];
  const capPillOk = pillsOk((await pills()).filter(m => !PART_KEYS.includes(m.key)), k => k !== 'performance');
  // the parts of Consumption carry the band of their value from the catalog's band ends (D-104), and no band word
  await go('/l2/monitor/compute/FR-B-04/capacity?class=bronze');
  const END = { cpu_thread_utilization: [55, 70, 85], memory_consumed: [70, 80, 90], memory_ballooned: [1, 2, 4], memory_zip_swap: [0.25, 0.5, 1] };
  const partBand = (k, v) => ['green', 'yellow', 'orange'].find((_, i) => v <= END[k][i]) || 'red';
  await page.click('details[data-details="consumption-parts"] > summary');  // the parts sit in a closed fold under the Consumption chart (D-122)
  const partPills = (await page.$$eval('details[data-details="consumption-parts"] .metric', ms => ms.map(m => ({ key: m.dataset.metric, pills: [...m.querySelectorAll('dd')].map(d => { const p = d.querySelector('.bv'); if (!p) return null; const cs = getComputedStyle(p);
    return { band: p.dataset.band, text: p.textContent.trim(), v: parseFloat(p.textContent.replace(/,/g, '')), fg: cs.color, bg: cs.backgroundColor }; }) })))).filter(m => END[m.key]);
  const partsOk = partPills.length === 4 && partPills.every(m => m.pills.every(p => p !== null && p.band === partBand(m.key, p.v) && !/green|yellow|orange|red/i.test(p.text) && ratio(p.fg, p.bg) >= 4.5));
  check('LPG-23', vmFirst === 'performance-kpis' && vmKpis.join() === 'guest_os_performance,vm_performance' && vmLayerKpis.length === 0 && counterPlain && vmPillOk
    && clKpis.join() === 'Cluster Performance,Cluster Risk' && clPillOk && noCards
    && capFirst.join() === 'summary,verdict' && rem.join() === 'Capacity Remaining,Time Remaining,VM Remaining' && !/Placeholder values/.test(placeholder) && capPillOk && partsOk,
    `VM ${vmKpis}; cluster ${clKpis}; capacity ${capFirst} ${rem}; pills ${vmPillOk}/${clPillOk}/${capPillOk}/${partsOk}`);

  // LPG-24 Details under each cluster KPI: closed by default, one chart per part, risk parts banded from the catalog's ends (D-106)
  await go('/l2/monitor/compute/FR-B-04/performance');
  const dets = await page.$$eval('details.kpi-details', ds => ds.map(d => ({ key: d.dataset.details, open: d.open, title: d.querySelector('summary').firstChild.textContent.trim(), parts: d.querySelectorAll('.metric').length })));
  const detsClosed = dets.map(d => d.key).join() === 'cluster_performance,cluster_risk' && dets.every(d => !d.open && d.title === 'Details');
  await page.click('details[data-details="cluster_risk"] summary');
  await page.click('details[data-details="cluster_performance"] summary');
  const detsOpen = await page.$$eval('details.kpi-details', ds => ds.map(d => ({ open: d.open, parts: d.querySelectorAll('.metric').length, charts: d.querySelectorAll('svg.lc').length, w: Math.round(d.querySelector('svg.lc').getBoundingClientRect().width) })));
  const RISK_END = { highest_esxi_cpu_thread_utilization: [60, 80, 90], worst_esxi_memory_ballooned: [1, 2, 4], highest_esxi_cpu_overcommit: [1, 2, 3] };
  const riskPills = await page.$$eval('details[data-details="cluster_risk"] .metric', ms => ms.map(m => ({ key: m.dataset.metric, pills: [...m.querySelectorAll('dd .bv')].map(p => ({ band: p.dataset.band, v: parseFloat(p.textContent) })) })));
  const riskBandOk = riskPills.filter(m => RISK_END[m.key]).length === 3 && riskPills.filter(m => RISK_END[m.key]).every(m => m.pills.every(p => p.band === (['green', 'yellow', 'orange'].find((_, i) => p.v <= RISK_END[m.key][i]) || 'red')));
  const PERF_END = { worst_vcpu_ready: [4, 8, 16], p90_disk_latency: [20, 40, 60], highest_esxi_packets: [0, 0.2, 0.4] };
  const bandedAll = async sel => page.$$eval(sel + ' .metric', ms => ms.every(m => [...m.querySelectorAll('dd .bv')].length === 3 && m.querySelectorAll('.zones rect').length >= 1));
  const perfPills = await page.$$eval('details[data-details="cluster_performance"] .metric', ms => ms.map(m => ({ key: m.dataset.metric, pills: [...m.querySelectorAll('dd .bv')].map(p => ({ band: p.dataset.band, v: parseFloat(p.textContent) })) })));
  const perfBandOk = perfPills.filter(m => PERF_END[m.key]).length === 3 && perfPills.filter(m => PERF_END[m.key]).every(m => m.pills.length === 3 && m.pills.every(p => p.band === endOf(p.v, PERF_END[m.key])));
  const perfAllBanded = await bandedAll('details[data-details="cluster_performance"]') && await bandedAll('details[data-details="cluster_risk"]');
  await go('/l2/monitor/compute/fr-esx-244/performance');
  await page.click('details[data-details="esxi_performance"] summary');
  const hostDets = await page.$$eval('details.kpi-details', ds => ds.map(d => ({ parts: d.querySelectorAll('.metric').length, closedTitle: d.querySelector('summary').firstChild.textContent.trim() })));
  const hostBanded = await bandedAll('details[data-details="esxi_performance"]');
  check('LPG-24', detsClosed && detsOpen.length === 2 && detsOpen.every(d => d.open && d.charts === d.parts && d.w > 300) && detsOpen[0].parts === 9 && detsOpen[1].parts === 10 && riskBandOk && perfBandOk && perfAllBanded && hostDets.length === 1 && hostDets[0].parts === 9 && hostBanded,
    `closed ${detsClosed}; open ${JSON.stringify(detsOpen)}; risk bands ${riskBandOk}; perf bands ${perfBandOk}/${perfAllBanded}; host ${JSON.stringify(hostDets)}/${hostBanded}`);

  // LPG-25 charts keep their own height: a chart box is as tall as its drawing; the wall's chart rules stay in the wall (D-108)
  await go('/l2/monitor/compute/LD-B-01/capacity');
  await page.$$eval('details.kpi-details', ds => ds.forEach(d => { d.open = true; }));  // charts in a closed fold have no width
  const chartBoxes = await page.$$eval('[data-chartbox]', cs => cs.map(c => ({ plot: c.querySelector('.plot').getBoundingClientRect().height, svg: c.querySelector('svg.lc').getBoundingClientRect().height })));
  const stacked = await page.$$eval('[data-chartbox], h2, h3, table.data', els => { const r = els.map(e => e.getBoundingClientRect()).sort((a, b) => a.top - b.top); return r.every((x, i) => i === 0 || x.top >= r[i - 1].bottom - 1 || x.left >= r[i - 1].right - 1); });
  check('LPG-25', chartBoxes.length >= 9 && chartBoxes.every(b => b.plot >= b.svg - 1) && stacked, `${chartBoxes.length} charts; boxes ${chartBoxes.every(b => b.plot >= b.svg - 1)}; no overlap ${stacked}`);

  // LPG-16 moving between pages does not load the page; the window is a drop-down; tabs are tabs; no dot
  await go('/l2/monitor/compute/estate/summary');
  await page.evaluate(() => { window.__same = 'yes'; });
  const moves = [];
  await page.click('[role="tab"][data-pillar="performance"]'); await page.waitForSelector('body[data-ready="1"]');
  moves.push(new URL(page.url()).pathname);
  const dots = await page.$$eval('[role="tab"]', ts => ts.map(t => !t.querySelector('.dot')));
  const selected = await page.$$eval('[role="tab"][aria-selected="true"]', ts => ts.map(t => t.dataset.pillar));
  const panelBy = await page.$eval('[role="tabpanel"]', p => p.getAttribute('aria-labelledby'));
  await page.click('#winbtn');
  const options = await page.$$eval('#winlist a', as => as.map(a => a.textContent.trim()));
  await page.click('#winlist a[data-w="7d"]'); await page.waitForSelector('body[data-ready="1"]');
  const label = (await page.innerText('.winbtn .lbl')).trim();
  moves.push(new URL(page.url()).searchParams.get('window'));
  await page.click('aside.tree a.node[data-obj="emea"]'); await page.waitForSelector('body[data-ready="1"]');
  const node = new URL(page.url()).pathname.split('/')[4];
  await page.goBack(); await page.waitForSelector('body[data-ready="1"]');
  const back = new URL(page.url()).searchParams.get('window');
  const same = await page.evaluate(() => window.__same);
  check('LPG-16', same === 'yes' && moves.join() === '/l2/monitor/compute/estate/performance,7d' && dots.every(Boolean) && selected.join() === 'performance'
    && panelBy === 'tab-performance' && options.join() === 'Last hour,Last 24 hours,Last 7 days,Last 30 days,Last year' && label === 'Last 7 days' && node === 'emea' && back === '7d',
    `same document: ${same}; ${moves}; dots ${dots.filter(Boolean).length}/${dots.length}; ${label}; back to ${back}`);

  // LPG-20 the Agent E2 mark and panel (D-097)
  // A taken port rejects here, so the finally below stops the PCM server.
  await new Promise((r, j) => { stub.once('error', j); stub.listen(E2_PORT, '127.0.0.1', r); });
  await new Promise(r => setTimeout(r, 3200)); // PCM keeps a health answer for 3 seconds
  await go('/l2/monitor/compute/estate/summary');
  const e2utils = await page.$$eval('nav.utils > *', xs => xs.map(x => x.id || x.textContent.trim()));
  const findRows = await page.$$eval('.finding', xs => xs.map(x => !!x.querySelector('.e2mark')));
  const noExplain = !(await page.innerText('main')).includes('Explain this finding');
  await go('/l2/monitor/compute/fr-svc-5526/performance');
  await page.waitForSelector('body[data-e2="up"]');
  const marks = await page.$$eval('.metric', ms => ms.map(m => [m.querySelector('h4').textContent, m.querySelector('.e2mark') && m.querySelector('.e2mark').getAttribute('aria-label')]));
  const marksOk = marks.length === 16 && marks.every(([n, l]) => l === `Ask Agent E2 about ${n}`);
  await page.click('.metric[data-metric="run_queue_per_vcpu"] .e2mark'); await page.waitForSelector('#e2 [data-sugg]');
  await page.waitForTimeout(300);
  const panelBox = await page.$eval('#e2', e => e.getBoundingClientRect().toJSON());
  const chartRight = await page.$eval('.metric[data-metric="run_queue_per_vcpu"] svg.lc', e => e.getBoundingClientRect().right);
  const folded = await page.$eval('#tree', e => getComputedStyle(e).display === 'none') && await page.isVisible('.treefold');
  const outlined = await page.$eval('.metric[data-metric="run_queue_per_vcpu"]', e => e.classList.contains('e2-asked'));
  const ctx = await page.innerText('[data-e2ctx]');
  const nSugg = (await page.$$('#e2 [data-sugg]')).length;
  await page.click('#e2 [data-sugg]'); await page.waitForSelector('#e2 .e2src', { timeout: 30000 });
  // D-099: the sources are a closed control with their number; one click opens the chips.
  const srcLabel = await page.$eval('#e2 .e2src summary', e => e.textContent.trim());
  const srcClosed = await page.$eval('#e2 .e2src details', d => !d.open) && !(await page.isVisible('#e2 .srcchip'));
  await page.click('#e2 .e2src summary');
  const srcOpened = await page.isVisible('#e2 .srcchip');
  const chips = (await page.$$('#e2 .srcchip')).length, boxes = (await page.$$('#e2 .e2computed, #e2 .box')).length;
  // D-119: the opening comes first, as one paragraph in the text's own style, no box; the calculator's lines are not shown.
  const leadOk = await page.$eval('#e2 .e2a', a => { const l = a.querySelector('.e2lead'), p = l && l.firstElementChild; return !!l && a.firstElementChild === l && l.children.length === 1 && p.tagName === 'P' && /^Peak vCPU run queue length is 1\.5/.test(p.textContent)
    && [l, p].every(e => getComputedStyle(e).borderTopStyle === 'none' && getComputedStyle(e).backgroundColor === 'rgba(0, 0, 0, 0)') && !a.textContent.includes('×'); });
  const objLinks = await page.$$eval('#e2 .e2a a[data-obj]', as => as.map(a => a.dataset.obj));
  const foot = await page.innerText('#e2 .e2foot');
  const sentFacts = E2_SEEN[E2_SEEN.length - 1];
  await page.click('[role="tab"][data-pillar="capacity"]'); await page.waitForSelector('body[data-ready="1"]');
  const stillOpen = await page.isVisible('#e2'), ctx2 = await page.innerText('[data-e2ctx]');
  await page.keyboard.press('Escape');
  const closed = !(await page.isVisible('#e2')) && await page.$eval('#tree', e => getComputedStyle(e).display !== 'none');
  const focusBack = await page.evaluate(() => document.activeElement && document.activeElement.id);
  check('LPG-20', e2utils[0] === 'e2top' && e2utils.slice(1).join() === 'Rules,Calendar' && findRows.length > 0 && findRows.every(Boolean) && noExplain && marksOk
    && chartRight <= panelBox.x && folded && outlined && /fr-svc-5526/.test(ctx) && /Performance/.test(ctx) && /Last 24 hours/.test(ctx) && nSugg >= 1 && nSugg <= 3
    && srcLabel === 'Sources (2)' && srcClosed && srcOpened && chips === 2 && boxes === 0 && leadOk && objLinks.includes('fr-esx-218') && foot.includes('recorded in the action history') && sentFacts.role === 'l2' && sentFacts.facts.asked_about_metric.name === 'Peak vCPU run queue length'
    && stillOpen && /Capacity/.test(ctx2) && closed && focusBack === 'e2top',
    `${e2utils}; ${findRows.length} findings marked; ${marks.length} metric marks; chart right ${Math.round(chartRight)} <= panel ${Math.round(panelBox.x)}; ${ctx}; ${nSugg} suggestions; ${chips} sources; links ${objLinks}; then ${ctx2}; focus ${focusBack}`);

  // LPG-22 a question about a layer, and a question about the whole page
  await go('/l2/monitor/compute/fr-svc-5526/performance');
  const layerMarks = await page.$$eval('section.layer > h2 .e2mark', ms => ms.map(m => m.getAttribute('aria-label')));
  await page.click('section.layer[data-layer="guest_os"] > h2 .e2mark'); await page.waitForSelector('#e2 [data-sugg]');
  const layerCtx = await page.innerText('[data-e2ctx]');
  const layerSugg = await page.$$eval('#e2 [data-sugg]', bs => bs.map(b => b.textContent));
  const layerOutlined = await page.$eval('section.layer[data-layer="guest_os"]', e => e.classList.contains('e2-asked'));
  await page.keyboard.press('Escape');
  await page.click('#e2top'); await page.waitForSelector('#e2 [data-sugg]');
  const pageSugg = await page.$$eval('#e2 [data-sugg]', bs => bs.map(b => b.textContent));
  const shownBefore = (await page.$$('#e2 .e2a')).length, sentBefore = E2_SEEN.length;
  await page.click('#e2 [data-sugg]'); await page.waitForFunction(n => document.querySelectorAll('#e2 .e2a').length > n, shownBefore);
  const pageFacts = E2_SEEN[sentBefore] && E2_SEEN[sentBefore].facts;
  // D-119: an opening on two KPIs is a list of two bullets, first in the answer, with no box.
  const pageLead = await page.$$eval('#e2 .e2a', as => { const a = as[as.length - 1], l = a.querySelector('.e2lead'); return { first: !!l && a.firstElementChild === l, items: l ? l.querySelectorAll('ul > li').length : 0, plain: !!l && getComputedStyle(l).borderTopStyle === 'none' && getComputedStyle(l).backgroundColor === 'rgba(0, 0, 0, 0)' }; });
  await page.keyboard.press('Escape');
  // LPG-26 the mark on the KPIs at the top of a cluster's and an ESXi host's Performance tab (D-117)
  const kpiMarks = () => page.$$eval('[data-section="performance-kpis"] > .metric', ms => ms.map(m => { const b = m.querySelector('.mname .e2mark'); return b && b.getAttribute('aria-label'); }));
  await go('/l2/monitor/compute/SG-S-01/performance');
  const clusterMarks = await kpiMarks();
  const partMarks = (await page.$$('.kpi-details .e2mark')).length;
  const look = await page.$eval('[data-section="performance-kpis"] .e2mark', b => { const s = getComputedStyle(b); return [s.backgroundColor, s.color, !b.querySelector('.dot')]; });
  const topBg = await page.$eval('#e2top', b => getComputedStyle(b).backgroundColor);
  const kSent = E2_SEEN.length;
  await page.click('[data-section="performance-kpis"] .metric[data-metric="cluster_performance"] .e2mark'); await page.waitForSelector('#e2 [data-sugg]');
  const kShown = (await page.$$('#e2 .e2a')).length;
  await page.click('#e2 [data-sugg]'); await page.waitForFunction(n => document.querySelectorAll('#e2 .e2a').length > n, kShown);
  const kFacts = E2_SEEN[kSent] && E2_SEEN[kSent].facts;
  await page.keyboard.press('Escape');
  await go('/l2/monitor/compute/sg-esx-110/performance');
  const hostMarks = await kpiMarks();
  check('LPG-26', clusterMarks.join() === 'Ask Agent E2 about Cluster Performance,Ask Agent E2 about Cluster Risk' && hostMarks.join() === 'Ask Agent E2 about ESXi Performance'
    && partMarks === 0 && look[0] === topBg && look[1] === 'rgb(255, 255, 255)' && look[2]
    && !!kFacts && kFacts.asked_about_kpi.label === 'Cluster Performance' && kFacts.asked_about_kpi.parts_at_worst.parts.length === 9,
    `cluster ${clusterMarks}; host ${hostMarks}; ${partMarks} part marks; mark ${look} top ${topBg}; sent ${kFacts ? kFacts.asked_about_kpi.label : 'nothing'}`);

  check('LPG-22', layerMarks.join() === 'Ask Agent E2 about the Guest OS layer,Ask Agent E2 about the Virtual Motherboard layer' && /Guest OS layer/.test(layerCtx)
    && layerSugg[0] === 'Is the Guest OS layer the problem?' && layerOutlined && pageSugg[0] === 'Is this VM performing well over the last 24 hours?'
    && !!pageFacts && pageFacts.layers.length === 2 && pageFacts.layers.every(l => l.metrics.every(m => m.percentile_95 !== undefined && m.values === undefined))
    && pageLead.first && pageLead.items === 2 && pageLead.plain,
    `${layerMarks.length} layer marks; ${layerCtx}; ${layerSugg[0]}; ${pageSugg[0]}; page facts layers ${pageFacts && pageFacts.layers.map(l => l.layer)}; opening ${pageLead.items} bullets`);

  // LPG-21 a clarifying round carries the earlier turns; a narrow screen shows the panel as a sheet
  await go('/l2/monitor/compute/fr-svc-5526/performance');
  await page.click('.metric[data-metric="cpu_ready_percent"] .e2mark'); await page.waitForSelector('#e2q');
  await page.fill('#e2q', 'Which counter do I read?'); await page.press('#e2q', 'Enter'); await page.waitForSelector('#e2 .e2asks', { timeout: 30000 });
  const asks = await page.innerText('#e2 .e2asks');
  const before = E2_SEEN.length, shown = (await page.$$('#e2 .e2a')).length;
  await page.fill('#e2q', 'The VM one'); await page.press('#e2q', 'Enter'); await page.waitForFunction(n => document.querySelectorAll('#e2 .e2a').length > n, shown);
  const turns = E2_SEEN[before] && E2_SEEN[before].turns;
  await page.setViewportSize({ width: 800, height: 900 }); await page.waitForTimeout(200);
  const sheet = await page.$eval('#e2', e => e.getBoundingClientRect().toJSON());
  const closeTop = await page.$eval('#e2 .e2close', e => e.getBoundingClientRect().top);
  await page.keyboard.press('Escape'); await page.setViewportSize({ width: 1440, height: 1000 });
  check('LPG-21', /Agent E2 asks/i.test(asks) && Array.isArray(turns) && turns.length === 3 && turns[0] === 'Which counter do I read?' && turns[2] === 'The VM one'
    && sheet.x === 0 && sheet.width === 800 && closeTop < 60, `${asks.split('\n')[0]}; turns ${turns && turns.length}; sheet ${sheet.x},${sheet.width}; close at ${Math.round(closeTop)}`);

  // LPG-28 a second question carries the first as history (D-128)
  await go('/l2/monitor/compute/fr-svc-5526/performance');
  await page.click('.metric[data-metric="cpu_ready_percent"] .e2mark'); await page.waitForSelector('#e2q');
  const n28 = (await page.$$('#e2 .e2a')).length;
  await page.fill('#e2q', 'Is this a problem?'); await page.press('#e2q', 'Enter'); await page.waitForFunction(n => document.querySelectorAll('#e2 .e2a').length > n, n28);
  const at28 = E2_SEEN.length, tp28 = E2_TOPIC.length;
  await page.fill('#e2q', 'I do not understand. Explain again.'); await page.press('#e2q', 'Enter'); await page.waitForFunction(n => document.querySelectorAll('#e2 .e2a').length > n, n28 + 1);
  const hist = E2_SEEN[at28] && E2_SEEN[at28].history;
  const last = hist && hist[hist.length - 1];
  const cont28 = await page.$$eval('#e2 [data-topic-continues]', els => els.length ? els[els.length - 1].innerText : '');
  check('LPG-28', Array.isArray(hist) && hist.length >= 1 && last.question === 'Is this a problem?' && last.answer.startsWith('Peak vCPU run queue length') && last.answer.includes('Check next')
    && E2_TOPIC[tp28] && E2_TOPIC[tp28].topic_choice === 'auto' && E2_TOPIC[tp28].history.length === hist.length
    && E2_SEEN[at28].topic_choice === 'continue' && /^Continuing: “/.test(cont28),
    `history ${hist && hist.length}; last ${last && last.question}; topic call ${E2_TOPIC[tp28] && E2_TOPIC[tp28].topic_choice}; answer ${E2_SEEN[at28].topic_choice}; ${cont28}`);

  // LPG-29 a new topic: divider, its own history; the flip asks again; New topic and a suggestion send topic_choice new
  const askAt = i => E2_SEEN.slice(i).find(b => typeof b.question === 'string') || {};
  const histOf29 = b => b.history || [];
  const turns29 = async () => (await page.$$('#e2 .e2turn')).length;
  const askWait = async q => { const n = (await page.$$('#e2 .e2a')).length; await page.fill('#e2q', q); await page.press('#e2q', 'Enter'); await page.waitForFunction(m => document.querySelectorAll('#e2 .e2a').length > m && !document.querySelector('#e2 .e2wait'), n); };
  const div0 = (await page.$$('#e2 [data-topic-new]')).length;
  await askWait('What does Memory Zip Swap mean?');
  const div1 = (await page.$$('#e2 [data-topic-new]')).length, flipText = await page.$eval('#e2 [data-e2flip]', b => b.innerText).catch(() => '');
  const at29 = E2_SEEN.length;
  await askWait('Why?');
  const own = histOf29(askAt(at29));
  const nT = await turns29(), at29b = E2_SEEN.length;
  await page.click('#e2 [data-e2flip]'); await page.waitForFunction(() => !document.querySelector('#e2 .e2wait') && document.querySelector('#e2 [data-e2flip]'));
  const flipSent = askAt(at29b), replaced = (await turns29()) === nT;
  await page.click('#e2 [data-e2new]'); const pressed = await page.$eval('#e2 [data-e2new]', b => b.getAttribute('aria-pressed'));
  const at29c = E2_SEEN.length;
  await askWait('Why?');
  const forced = askAt(at29c);
  await page.keyboard.press('Escape');
  await page.click('#e2top'); await page.waitForSelector('#e2 [data-sugg]');
  const at29d = E2_SEEN.length, nS = (await page.$$('#e2 .e2a')).length;
  await page.click('#e2 [data-sugg]'); await page.waitForFunction(n => document.querySelectorAll('#e2 .e2a').length > n, nS);
  const sugg29 = E2_SEEN.slice(at29d).find(b => b.question && !(b.facts && b.facts.card));
  await page.click('#e2 [data-e2del="ask"]'); await page.click('#e2 [data-e2del="yes"]');  // leave the page's conversation empty for LPG-27
  await page.keyboard.press('Escape');
  check('LPG-29', div1 === div0 + 1 && flipText === 'Continue the last topic instead' && own.length === 1 && own[0].question === 'What does Memory Zip Swap mean?'
    && flipSent.topic_choice === 'new' && histOf29(flipSent).length === 0 && replaced && pressed === 'true'
    && forced.topic_choice === 'new' && histOf29(forced).length === 0 && !!sugg29 && sugg29.topic_choice === 'new',
    `dividers ${div0}->${div1}; flip "${flipText}"; own ${own.length}; flip sent ${flipSent.topic_choice}/${histOf29(flipSent).length}; replaced ${replaced}; pressed ${pressed}; forced ${forced && forced.topic_choice}; suggestion ${sugg29 && sugg29.topic_choice}`);

  // LPG-30 the topic decision shows before the answer, and can be flipped while waiting (D-130); no decision continues
  await go('/l2/monitor/compute/fr-svc-5526/performance');
  await page.click('.metric[data-metric="cpu_ready_percent"] .e2mark'); await page.waitForSelector('#e2q');
  const ask30 = async q => { const n = (await page.$$('#e2 .e2a')).length; await page.fill('#e2q', q); await page.press('#e2q', 'Enter'); await page.waitForFunction(m => document.querySelectorAll('#e2 .e2a').length > m && !document.querySelector('#e2 .e2wait'), n); };
  await ask30('Is this a problem?');
  const n30 = (await page.$$('#e2 .e2turn')).length, s30 = E2_SEEN.length, d30 = (await page.$$('#e2 [data-topic-new]')).length;
  await page.fill('#e2q', 'More details, slowly'); await page.press('#e2q', 'Enter');
  await page.waitForSelector('#e2 [data-topic-waiting]', { timeout: 15000 });
  const waitLine = await page.innerText('#e2 [data-topic-waiting]'), stillWaiting = !!(await page.$('#e2 .e2wait'));
  await page.click('#e2 [data-e2flipwait]');
  await page.waitForFunction(() => !document.querySelector('#e2 .e2wait'), null, { timeout: 15000 });
  await page.waitForTimeout(3500);  // the dropped slow answer arrives late: it must not be added
  const sent30 = E2_SEEN.slice(s30), n30b = (await page.$$('#e2 .e2turn')).length, d30b = (await page.$$('#e2 [data-topic-new]')).length;
  const s30c = E2_SEEN.length;
  await ask30('The old service: explain again');
  const old30 = E2_SEEN[s30c] || {}, oldCont = await page.$$eval('#e2 [data-topic-continues]', els => els.length ? els[els.length - 1].innerText : '');
  await page.click('#e2 [data-e2del="ask"]'); await page.click('#e2 [data-e2del="yes"]');
  await page.keyboard.press('Escape');
  check('LPG-30', /^Continuing: “Is this a problem\?”/.test(waitLine) && /Start a new topic instead/.test(waitLine) && stillWaiting
    && sent30.length === 2 && sent30.some(b => b.topic_choice === 'continue' && b.history.length === 1) && sent30.some(b => b.topic_choice === 'new' && (b.history || []).length === 0)
    && n30b === n30 + 1 && d30b === d30 + 1 && old30.topic_choice === 'continue' && (old30.history || []).length === 1 && /^Continuing: “More details, slowly”/.test(oldCont),
    `waiting "${waitLine.replace(/\s+/g, ' ')}"; sent ${sent30.map(b => b.topic_choice + '/' + (b.history || []).length).join(', ')}; turns ${n30}->${n30b}; dividers ${d30}->${d30b}; old service ${old30.topic_choice}/${(old30.history || []).length}, "${oldCont}"`);

  // LPG-27 delete a conversation (D-123): Delete, then Yes; No keeps it
  await go('/l2/monitor/compute/fr-svc-5526/performance');
  await page.click('#e2top'); await page.waitForSelector('#e2 [data-sugg]');
  const t0 = (await page.$$('#e2 .e2turn')).length;
  const noDelEmpty = t0 === 0 ? !(await page.$('#e2 [data-e2del]')) : !!(await page.$('#e2 [data-e2del="ask"]'));
  const nBefore = (await page.$$('#e2 .e2a')).length;
  await page.click('#e2 [data-sugg]'); await page.waitForFunction(n => document.querySelectorAll('#e2 .e2a').length > n, nBefore);
  await page.click('#e2 [data-e2del="ask"]');
  const asked = await page.innerText('#e2 .e2del');
  await page.click('#e2 [data-e2del="no"]');
  const keptAfterNo = (await page.$$('#e2 .e2turn')).length === t0 + 1 && !!(await page.$('#e2 [data-e2del="ask"]'));
  await page.click('#e2 [data-e2del="ask"]'); await page.click('#e2 [data-e2del="yes"]');
  const gone = (await page.$$('#e2 .e2turn')).length === 0 && !!(await page.$('#e2 [data-sugg]')) && !(await page.$('#e2 [data-e2del]'));
  await page.keyboard.press('Escape');
  check('LPG-27', noDelEmpty && /Delete\?/.test(asked) && keptAfterNo && gone, `${noDelEmpty}; ${asked.replace(/\s+/g, ' ')}; kept ${keptAfterNo}; gone ${gone}`);

  // LPG-31 the live demo's walk of Agent E2 (R-LIVE-036, T-LIVE-036c): every mark, every suggested question, on the four release 1.0 pages
  const WALK = ['/l2/monitor/compute/SG-S-01/performance', '/l2/monitor/compute/SG-S-01/capacity', '/l2/monitor/compute/sg-esx-110/performance', '/l2/monitor/compute/sg-api-1617/performance'];
  const walk = [], walkBad = [];
  const clearPanel = async () => { if (await page.$('#e2 [data-e2del="ask"]')) { await page.click('#e2 [data-e2del="ask"]'); await page.click('#e2 [data-e2del="yes"]'); } };
  for (const p of WALK) {
    await go(p); await page.waitForSelector('body[data-e2="up"]');
    const nMarks = (await page.$$('main .e2mark')).length;
    for (let m = -1; m < nMarks; m++) {
      const mark = m < 0 ? '#e2top' : `main .e2mark >> nth=${m}`;
      const card = m < 0 ? '' : (await page.getAttribute(mark, 'aria-label')).replace(/^Ask Agent E2 about (the )?/, '').replace(/ layer$/, '');
      await page.click(mark); await page.waitForSelector('#e2 [data-sugg]', { timeout: 15000 });
      await clearPanel(); await page.waitForSelector('#e2 [data-sugg]', { timeout: 15000 });
      const ctx = await page.innerText('[data-e2ctx]');
      const nS = (await page.$$('#e2 [data-sugg]')).length;
      let asked = 0;
      for (let q = 0; q < nS; q++) {
        await clearPanel(); await page.waitForSelector('#e2 [data-sugg]', { timeout: 15000 });
        const before = E2_SEEN.length, nA = (await page.$$('#e2 .e2a')).length;
        await page.click(`#e2 [data-sugg] >> nth=${q}`);
        await page.waitForFunction(n => document.querySelectorAll('#e2 .e2a').length > n && !document.querySelector('#e2 .e2wait'), nA, { timeout: 30000 });
        const sent = E2_SEEN.slice(before), f = (sent[0] || {}).facts || {};
        const about = Object.keys(f).filter(k => k.startsWith('asked_about_')).map(k => (f[k] || {}).name || (f[k] || {}).label || (f[k] || {}).layer || '');
        const fits = m < 0 ? about.length === 0 : about.some(n => n && (card.includes(n) || n.includes(card)));
        if (sent.length !== 1 || !fits) walkBad.push(`${p} ${card || 'top bar'} q${q + 1}: ${sent.length} sent, about [${about}]`);
        asked++;
      }
      if (nS < 1 || nS > 3 || !/Performance|Capacity/.test(ctx)) walkBad.push(`${p} ${card || 'top bar'}: ${nS} suggestions, context ${ctx}`);
      walk.push(asked);
      await clearPanel();
      await page.keyboard.press('Escape');
    }
  }
  check('LPG-31', walk.length >= 8 && walkBad.length === 0, walkBad.slice(0, 4).join(' | ') || `${walk.length} marks on ${WALK.length} pages, ${walk.reduce((a, b) => a + b, 0)} questions asked, each with its card`);

  // LPG-32 Agent E2 stops during a demo (R-LIVE-040, T-LIVE-040a): the panel says so, the page stays, and it answers again once back
  await go('/l2/monitor/compute/SG-S-01/performance'); await page.waitForSelector('body[data-e2="up"]');
  await page.click('#e2top'); await page.waitForSelector('#e2 [data-sugg]');
  const askOne = async q => {
    const n = (await page.$$('#e2 .e2a')).length;
    await page.fill('#e2q', q); await page.press('#e2q', 'Enter');
    await page.waitForFunction(m => document.querySelectorAll('#e2 .e2a').length > m && !document.querySelector('#e2 .e2wait'), n, { timeout: 30000 });
    return page.$$eval('#e2 .e2a', as => as[as.length - 1].innerText);
  };
  const a1 = await askOne('Is this cluster healthy?');
  const figs32 = await page.innerText('main');
  const stopped = new Promise(r => stub.close(r)); stub.closeAllConnections(); await stopped;
  const a2 = await askOne('And the hosts?');
  const sameFigs = (await page.innerText('main')) === figs32;
  await new Promise(r => stub.listen(E2_PORT, '127.0.0.1', r));
  const a3 = await askOne('Is this cluster healthy now?');
  await clearPanel();
  await page.keyboard.press('Escape');
  check('LPG-32', !/not available/.test(a1) && /not available|cannot be reached/i.test(a2) && sameFigs && !/not available/.test(a3),
    `first "${a1.split('\n')[0]}"; stopped "${a2.split('\n')[0]}"; page unchanged ${sameFigs}; back "${a3.split('\n')[0]}"`);

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
  for (const p of ['/l2', '/l2/monitor/compute/fr-svc-5526/performance', '/l2/monitor/compute/ld/performance?window=7d&group=host_model', '/l2/monitor/compute/LD-B-01/capacity?window=7d', '/l2/monitor/compute/wld-fr-gen/capacity?window=7d&class=bronze', '/l2/troubleshoot/compute/estate', '/l2/troubleshoot/case/case-inc-tk-s-03', '/l2/improve/compute/estate/summary', '/l2/rules', '/l2/calendar']) {
    await go(p); fails.push(...(await contrast()).map(f => `${p}: ${f}`));
  }
  const foreign = [...hosts].filter(h => h !== `127.0.0.1:${PORT}`);
  check('LPG-12', !fails.length && !foreign.length, fails.slice(0, 4).join(' | ') || 'contrast ok; no foreign request');

  // Screenshots for review.
  mkdirSync(HERE + 'screenshots', { recursive: true });
  const shot = await browser.newPage({ viewport: { width: 1440, height: 1000 }, deviceScaleFactor: 2 });
  shot.on('dialog', d => d.accept('Reason given in the test'));
  for (const [p, name, full] of [['/l2', 'l2-monitor-estate', false], ['/l2/monitor/compute/ld/performance?window=7d&group=host_model', 'l2-monitor-group-by', false],
    ['/l2/monitor/compute/estate/performance', 'l2-monitor-performance', true],
    ['/l2/monitor/compute/fr-bat-6839/performance', 'l2-monitor-vm-performance', true], ['/l2/monitor/compute/FR-B-04/performance', 'l2-monitor-cluster-performance', true],
    ['/l2/monitor/compute/fr-esx-244/capacity', 'l2-monitor-capacity-host', true],
    ['/l2/monitor/compute/LD-B-01/capacity?window=7d', 'l2-monitor-capacity-cluster', true], ['/l2/monitor/compute/wld-fr-gen/capacity?window=7d&class=bronze', 'l2-monitor-capacity-group', true],
    ['/l2/troubleshoot/compute/estate', 'l2-troubleshoot-cases', false], ['/l2/troubleshoot/case/case-inc-tk-s-03', 'l2-case-escalation', true],
    ['/l2/troubleshoot/case/case-sg-app-117', 'l2-case-guest-os', true], ['/l2/improve/compute/estate/summary', 'l2-improve', false], ['/l2/rules', 'l2-rules', false]]) {
    await shot.goto(BASE + withNow(p)); await shot.waitForSelector('body[data-ready="1"]', { timeout: 60000 });
    await shot.screenshot({ path: HERE + `screenshots/${name}.png`, fullPage: full });
  }
  await shot.goto(BASE + withNow('/l2/monitor/compute/fr-svc-5526/performance')); await shot.waitForSelector('body[data-ready="1"]');
  await shot.click('.metric[data-metric="run_queue_per_vcpu"] .e2mark'); await shot.waitForSelector('#e2 [data-sugg]');
  await shot.click('#e2 [data-sugg]'); await shot.waitForSelector('#e2 .e2src', { timeout: 30000 }); await shot.waitForTimeout(300);
  await shot.screenshot({ path: HERE + 'screenshots/l2-agent-e2-panel.png' });
  await shot.goto(BASE + withNow('/l2/troubleshoot/compute/estate')); await shot.waitForSelector('body[data-ready="1"]');
  const t1 = await shot.$$eval('tr[data-case]', trs => trs.map(t => [t.dataset.case, t.innerText]).find(([, x]) => /sg-gl-db-01/.test(x)));
  if (t1) {
    await shot.goto(BASE + withNow(`/l2/troubleshoot/case/${t1[0]}`)); await shot.waitForSelector('body[data-ready="1"]');
    await shot.screenshot({ path: HERE + 'screenshots/l2-case-complaint.png', fullPage: true });
  }
} finally {
  await browser.close(); await reset().catch(() => {}); server.kill(); stub.close();
}
const failed = results.filter(r => !r.ok);
console.log(`\n${results.length - failed.length} passed, ${failed.length} failed`);
process.exit(failed.length ? 1 : 0);
