# Build (generated)

Everything in this folder is **generated from [`../spec/`](../spec)**. Do not edit it by hand: the next regeneration removes hand edits (D-070). Fix the specification, then regenerate.

Prototype technology: D-071. Not the product stack.

## Run

From the repository root:

```bash
pip install pyyaml
```

```bash
python3 -m build.pcm_proto.server --port 8080
```

Open:
- `http://localhost:8080/exec`: Executive
- `http://localhost:8080/noc/wall`: NOC wall, for a TV
- `http://localhost:8080/noc`: NOC desktop
- `http://localhost:8080/l2`: L2 Platform
- `http://localhost:8080/capacity`: Capacity
- `http://localhost:8080/docs`: Docs (PCM's own objects, read-only)

Options, in the page URL or on the API:

| Parameter | Effect |
|---|---|
| `now=2026-10-19T10:05:00+08:00` | Fix the clock (D-067). Omitted: the present time. |
| `enable=E-7` | Switch on an optional story, here Europe's VCF Operations going stale. |
| `screen=fast` | Wall only: show one screen without rotating, for a wall with one display per screen (D-041). |
| `rotate=5` | Wall only, prototype and test: rotate every 5 seconds instead of 60. |

**Database (D-080):** what people and policies do is kept in SQLite at `var/pcm.sqlite`, so it survives a restart. Set `PCM_DB` to use another file. Tests use `PCM_DB=:memory:`. To start clean, stop the server and delete the file. Synthetic metrics are generated from "now", never stored.

## Install on a lab VM

As a service, reachable from the lab network: [`../deploy/README.md`](../deploy/README.md). The server listens on 127.0.0.1 unless `--host` says otherwise.

## Demo

The demo script and its rehearsal: [`../demo/README.md`](../demo/README.md).

## Test

```bash
python3 -m unittest build.tests.test_executive -v
```

```bash
python3 -m unittest build.tests.test_noc -v
```

```bash
node build/tests/page.test.mjs
```

```bash
node build/tests/noc.page.test.mjs
```

```bash
python3 -m unittest build.tests.test_l2 -v
```

```bash
node build/tests/l2.page.test.mjs
```

```bash
python3 -m unittest build.tests.test_capacity -v
```

```bash
node build/tests/capacity.page.test.mjs
```

```bash
python3 -m unittest build.tests.test_store -v
```

```bash
python3 -m unittest build.tests.test_docs -v
```

```bash
node build/tests/docs.page.test.mjs
```

Export PCM's objects for private-cloud-explained (D-082), into its checkout or any folder:

```bash
python3 -m build.pcm_proto.docs --export ../private-cloud-explained
```

The page test needs Node and Playwright with Chromium. It also writes the review screenshots to `screenshots/`.

## Results: Executive

| Level | Tests | Result |
|---|---|---|
| Catalog | CAT-1 to CAT-22 | 22 passed |
| Story | ST-1 to ST-9 | 9 passed |
| Page | PG-1 to PG-13 | 13 passed |
| Extra | Same inputs give the same data; stories hold on another day (D-067) | 2 passed |

Second build: "Is it fast?" became a KPI with no target (D-072); "Is it safe?" became the Security SLA (D-073).

Fourth build: "Is it up?" became the SP5 Availability SLA (D-077): Operational Availability per VM per calendar month against the class target, with approved change windows from the ITSM change calendar excluded and Actual Availability in the drill-down. The whole-month allowance rule also corrected the Security SLA, which had judged VMs against the month so far.

Third build: the three gaps from the first review are fixed in the specification (D-074) and tested by PG-10 to PG-12: times in the viewer's zone with the zone named; meters say which stale locations they leave out; the Manrope font ships in `web/fonts/` (SIL Open Font License), so no request leaves the PCM host.

**One defect found and fixed in the specification:** green and "in the plan" chips used `#0A7A6D` on `#D2ECE5`, which has a contrast of 4.2:1. Amber chips used `#B45309` on `#F5E1B8`, at 3.9:1. Both came from the mockup and are below the 4.5:1 minimum. PG-9 found them. `spec/design-system/tokens.md` now has `accent.ink` and `amber.ink`.

## Results: NOC

**Wall redesign (D-106):** six screens named Availability, Performance, Security, Volatility, Configuration, Capacity, shown as display-only tabs with no colour and no summary word. Banner: ACME Corp Private Cloud with running VMs and running ESXi hosts. Performance has a one-hour chart (average and lowest cluster). Capacity is new. Tests NST-14 to NST-16 and NPG-12 to NPG-14 cover it. **Found by the page test and fixed:** the Capacity tile of a stale location raised an error because it read numbers a stale tile does not carry. **Not changed:** the CIO page, and its labels.

| Level | Tests | Result |
|---|---|---|
| Catalog | NCAT-1 to NCAT-6 | 6 passed |
| Story | NST-1 to NST-13 | 13 passed |
| Page | NPG-1 to NPG-11 | 11 passed |

**Found while reviewing the screenshots, and fixed in the specification first:**
- The SOP step "is the villain non-production?" showed "fail". It is a branch, not a failure. Branch steps now show their answer.
- The action history showed action IDs (`stop_provisioning`). It now shows plain words.
- "Is it up?" turned red when Europe's VCF Operations stopped answering, with nothing on screen saying why. The screen now names the source and the time of its last good data.

**One test expectation corrected in the specification:** NST-1 expected the wall to pin "Is it fast?". Stories N-1 and N-3 are both active, so the wall pins two screens and cycles through both. The test now checks that "Is it fast?" is among the pins.

## Results: L2

Third L2 build: the workspace is rebuilt around three activities, **Monitor, Troubleshoot, Improve** (D-083 to D-090). One shell page; the frame reads the address: activity in the top bar, object in the inventory tree, pillar in the tabs, time in one picker. The nine pages of the first build (Today, Weekly, Monthly, Escalations, Investigate, Configuration, Inventory, Calendar, Thresholds) are gone; section 12 of `design/l2-workspace.md` says where each went.

| Level | Tests | Result |
|---|---|---|
| Catalog | LCAT-1 to LCAT-16 | all passed |
| Story | LST-1 to LST-30, plus tree, stale, realms, generic complaint, agent and money checks | all passed |
| Page | LPG-1 to LPG-23 | 22 browser checks and the specification check passed |
| Demo rehearsal | 21 steps, 8 of them L2 | all OK |

- **The whole estate is in the tree:** 1,200 hosts, 106 clusters, about 27,900 VMs, built from `spec/data/estate.yaml` (`l2_tree`). Every object a story names sits where the story says. Five views: Compute, Storage, Network, Class of service, Management.
- **Monitor** reads every VM: each node shows its children worst first (score over the window and over the last hour), the count just above the green line, and Group by. London, 7 days, grouped by host model: 9 VMs wider than their host's NUMA node, all on Gen-2019 hosts (story M-1).
- **Troubleshoot:** every case has a trigger (complaint, L1 escalation, monitoring finding). The chain grows link by link; Agent E2's flows propose, L2 confirms or rules out. Story T-1 (from Agent E2's `L4-037`): nine links, a snapshot left by the backup as root cause, a NUMA split as contributing cause, and "add 8 vCPUs" and "add a ninth host" ruled out. The timeline reaches back to the weekend change window.
- **Same numbers as the NOC:** a story that plants a cluster's performance (N-1, T-2) now drives the NOC and L2 from one function. TK-S-03 shows amber on the wall and its incident shows as already escalated.
- **Found in review and fixed:** the 24-hour 95th percentile hid FR-S-02's fall of 20 minutes ago; rows now show the window and the last hour, and the status is the worse of the two. Case work (proposals, confirmations) flooded the timeline and the L1 evidence; it is now kept on the case. Security, capacity, configuration and inventory findings opened cases; only availability and performance are troubleshot (SP5), the rest go to Improve.
- **Speed:** the specification files were parsed again on every call, about 0.3 s each. They are now parsed once per change. The estate summary answers in about 1.5 s, other L2 calls in 0.1 to 0.5 s.
- **Still planted:** the chains for planted stories come from the story file, because Agent E2's flow executor is not called yet. A complaint about any other VM runs a generic SP5 order on that VM's counters.

**The Capacity tab (D-094, D-095, D-096):** `pcm_proto/l2_capacity.py`. The snapshot table (CPU and memory average and 95th across hosts, "imbalance") is gone.
- **On a cluster:** the verdict of the PCM adapter's Periodic Cluster Check in words, with the rule that matched ("Closed for new VMs since the check of 19 Oct. Consumption 82% is above 80%."), beside "Contention now" from the last hour. Three charts in the rule's order (Cluster Consumption, Performance, Risk) with the closure levels, Now, Worst, 95th percentile and the check value named by its percentile ("95th percentile, 24 hours to 19 Oct, 00:00 UTC"). The check strip, one cell per check. What consumption is made of, usable capacity (total, HA, buffer), the spread between hosts (highest and lowest, no average), the hosts worst first. A host or VM shows its cluster's page with its host marked.
- **Above the cluster:** Gold first, always. Clusters closed per check, the highest Cluster Consumption and its 90th percentile, near closure (open, above 60%), and every cluster at a clicked time. No total, no forecast word; one link to the Capacity workspace.
- **Story M-4:** LD-B-01 shows red at 77 and stays open, then closes at 82; FR-B-04 drifts up (a 7-day finding); FR-B-03 is near closure and steady. FR-S-02 (N-1) is open at the check with contention now at 22.
- **One definition:** each Consumption check value is exactly the 95th percentile of that day's 5-minute points. Performance and Risk are the Performance tab's own series; their check values come from it, so both tabs show one number. Found in review: the first cut drew Performance from that series but took its check value from a separate model (77.5 against 87); fixed.
- **Found in review and fixed:** "Contention now" said 22 while the chart's last point said 31; the last point is now the NOC's value now. A closed cluster's chip had no finding row in the 7-day window; the window now links to the daily finding instead of repeating it. An old daily finding quoted the Capacity workspace's decision date on L2; it now names no date.

**The KPI first (D-100):** `object_kpis` in `pcm_proto/l2_monitor.py`, `capacity_remaining` in `pcm_proto/l2_capacity.py`.
- **Performance tab, VM:** Guest OS Performance and VM Performance first, in a section of their own; the layers keep their counters.
- **Performance tab, cluster and below:** the four cards are gone. The object's KPI over the window comes first: Cluster Performance and Cluster Risk on a cluster (the same series as the Capacity tab: FR-B-04 shows 82.2, 80.2, 80.7 on both), ESXi Performance on a host. "Just above the line" is a 7-day chart.
- **Band figures:** Now, Worst and 95th percentile of every 0 to 100% KPI are pills in the band of their value, with its name; text 6.2:1 or better (LPG-23 measures it in the browser).
- **Capacity tab, VM, host, cluster:** a summary first, Capacity Remaining, Time Remaining and, on a host and a cluster, VM Remaining. Placeholder values, stable per object, not labelled on the page. Never on a group (LST-30, LPG-18).
- Screenshots: `screenshots/l2-monitor-vm-performance.png`, `l2-monitor-cluster-performance.png`, `l2-monitor-capacity-host.png`.
- **Pre-existing, not from this change:** run in one `unittest` call together with the L2, Capacity and NOC tests, `test_executive` fails ST-2 and "stories hold on another day"; run alone, as listed under Test, it passes. The same happens on the commit before this change.

**Policy as code (D-079):** the trust ladder is gone. Action policies (tier and guardrails, versioned, owned) decide what runs automatically. The approval record is evidence only. "Propose a policy change" replays against history before Publish. The L-4 move runs automatically under v2, with the policy owner and version as its accountable party and no approval record.

**Capacity engine:** decision dates on every page now come from `pcm_proto/capacity.py` (13-month forecast, usable capacity, purchase plan). They are no longer planted from stories.

**Found in review and fixed in the specification first:** decision IDs ("D-039", "D-073", "D-040") appeared in page text and SOP steps. New builder rule 9: decision IDs never appear in page text. Tests PG-13, NPG-10 and LPG-8 now check every workspace, and the NOC test found two SOP steps that leaked one.

## Results: Capacity

All seven Capacity pages: This week, Cluster groups, One group, Demand, What-if, Purchase plan, Waste.

| Level | Tests | Result |
|---|---|---|
| Catalog | KCAT-1 to KCAT-5 | 5 passed |
| Story | KST-1 to KST-8, register add, cost not price | 10 passed |
| Page | KPG-1 to KPG-6, demand add | 7 passed |

- **SP5 host specification:** Silver fits 25.9 VMs on a 64-core, 768 GB host; memory binds; the matching DRAM is 839 GB. Gold 520 GB, Bronze 660 GB.
- **This week:** FR-Silver's decision moved 130 days earlier because of the OpenShift migration entry.
- **The check overrides the forecast (D-094):** LD-Bronze says "Closed for new VMs: LD-B-01", read from the Periodic Cluster Check, the same verdict as L2's Capacity tab. "Full now: VMs waiting" is gone: placement sends new VMs elsewhere, nothing waits. FR-S-02's contention of the last 20 minutes is L2's and the NOC's, not this page's (no live data, Capacity design 3.16).
- **Peak warning:** TK-Silver's March close week crosses usable memory; the 90-day trend sees no run-out. Amber chip, no purchase.
- **Waste:** TK-Gold in dark grey. Reclaiming SG-Silver moves it out of the round: cost avoidance $3,588,000, the same number as the Executive cost card.
- **Hardware refresh:** London, 90 old hosts to 75 new ones, covers next year's growth; licensed cores rise from 3,600 to 4,800.

**Found in review and fixed:**
- Groups beyond 13 months piled up on the scatter's right edge with overlapping labels. They now sit there unlabelled, with a count ("9 beyond 13 months"). The table lists them all.
- TK-Silver showed "Good" next to a peak warning. It now shows an amber "Peak warning" chip.
- A new register entry pulled VA-Silver's decision date into the past, shown as a plain date. It now says "overdue since".

## Results: Database

| Level | Tests | Result |
|---|---|---|
| Catalog | DB-1 to DB-4 | 4 passed |
| Page | DBP-1 | 1 passed |

- The action record refuses UPDATE and DELETE.
- After a restart: the escalation, the published policy v2, the register entry and every record are still there. The decision date is unchanged.
- The database refuses a register entry with no amount, a negative amount or an unknown kind.
- Only three tables. The planted OpenShift entry stays synthetic.
- Page tests now wait until the server answers. A fixed 0.8-second wait made the Executive page test fail once.
- The Executive page test was still flaky. It opened each panel, waited a fixed 150 ms, then looked for the 7/30-day switch, and sometimes found the previous panel's switch. It now waits for the panel it opened. Three runs in a row pass.

## Results: Docs

| Level | Tests | Result |
|---|---|---|
| Catalog | DCAT-1 to DCAT-4 | 4 passed |
| Story | DST-1 to DST-4, no decision ID in any object | 5 passed |
| Page | DPG-1 to DPG-4 | 4 passed |

- 122 objects: 73 measures, 5 SOPs, 5 action policies, 1 threshold, 4 configuration standards, 34 settings.
- "Used on" is computed from the page specifications. The Cluster Performance threshold shows on the NOC wall and incident page, and also on Capacity's cluster groups page, through the contention override.
- History comes from the action record: after L2 publishes 60, the threshold shows version 2, 50 to 60, and who.
- The export writes 9 files in private-cloud-explained's content model: 5 runbooks, 3 operations plans, 1 inventory register. Every file has its front matter fields and the required headings of its type.

**Found by building `/docs`, and fixed in the specification first:**
- `capacity.run_out_date` was defined twice, in the Executive and the Capacity catalogs. One definition now, in the Capacity catalog. Test DCAT-4 holds it.
- The monthly review page read `l2.configuration_review`, which does not exist. It now reads `l2.config_order`. Test DCAT-2 checks every read on every page.
- The Cluster Performance alert threshold and the configuration standards were written in the prototype code. They are now `catalog/thresholds.yaml` and `catalog/standards.yaml`. Test DCAT-3 holds it.

**Needed on the private-cloud-explained side:** source type `pcm` and origin `generated` in its content model.

## Agent E2 (D-076)

- Agent E2 drafts on the NOC incident page through one OpenAI-compatible client (`pcm_proto/agent_e2.py`, standard library only).
- **Demo:** Vercel AI Gateway, model `google/gemma-4-31b-it`, one of Agent E2's local candidates. The key comes from `AI_GATEWAY_API_KEY`. **Customer site:** set `agent_e2.endpoint` to the local model server.
- **Tests run with `PCM_AGENT_E2_MODE=mock`,** so they do not depend on the network.
- **Live check, 2026-11-20:** an explanation takes about 1.4 s, an escalation note about 6 s.
- **Found in the first live call, and fixed:**
  - The model reported an SOP action as done when it was only available.
  - The facts now keep `available_action` apart from `actions_already_done`, and the rules say so.
  - Test NST-12 holds the separation.

## Agent E2 service (D-078)

- **Where L2 meets it (D-097):** the E2 mark in the top bar (dark with a green dot when the service answers, grey when not; it asks about the whole page) and on each layer heading and each metric of a VM's Performance tab, each KPI of a cluster's Capacity tab, each finding row, the case header, each chain link and each layer row. A click opens the Agent E2 panel on the right: it pushes the content, and the tree folds to a strip.
- **One endpoint:** `POST /api/l2/agent/ask` with the question and what was clicked. PCM rebuilds the facts on the server (`build/pcm_proto/l2_agent.py`) and calls the Agent E2 service (`harness/answer_service.py` in the Agent E2 repository). `GET /api/l2/agent/health` asks the service's `/v1/health`.
- **Run it next to PCM:** `python3 harness/answer_service.py --port 8090` from the Agent E2 repository. It takes about 50 s to start. The URL is the setting `agent_e2.service_url`; `PCM_AGENT_E2_URL` replaces it.
- **On the lab VM:** `deploy/agent-e2.service` runs it next to PCM (`deploy/README.md`, section Agent E2).
- **Checked against the real service, 2026-11-22** (Agent E2 `d875445`): with its offline mock model, a Run Queue question on fr-svc-5526 came back in 4 s and read `guest-os/cpu/metrics/run-queue`, `.../ready` and `.../co-stop`. Without a key, the service starts and answers its health check, but each question fails at the model; the panel now says "Agent E2 is running, but its model cannot be reached." instead of "not available". Not checked: a live model.
- **The NOC desk has the same mark and panel (D-098):** top bar, each tile, the cluster drill-down, each alert row, the incident title and each SOP step. `POST /api/noc/agent/ask` sends L1's facts with the role l1 (`build/pcm_proto/noc_agent.py`); an answer that keeps a word from the NOC vocabulary's avoided list is asked for once more, then not shown. "Explain this incident" and "Draft the escalation note" are the panel's first suggestions on an incident. One shared module: `web/e2/panel.js` and `web/e2/panel.css`. Screenshot: `screenshots/noc-agent-e2-panel.png`.
- **Page tests** run a stub service: no model and no network. A live check of the panel against the real service has not run yet.
- **Live check, 2026-11-20:**
  - sg-app-117 answered in 32 s: "the issue is inside the Guest OS".
  - The answer cites SP5 files and adds that the run queue of 6.5 per vCPU is in the orange band. It names what to check next.
  - Minor: it cited the cluster performance file for VM-level green bands.
- **Without the service,** the mark is grey and the panel says "The Agent E2 service is not available" (test LPG-8).
- Screenshot of the panel: `screenshots/l2-agent-e2-panel.png`.

## Known gaps (to fix in the specification, not here)

| Gap | Effect | Proposed fix |
|---|---|---|
| Class group KPIs are planted from the background, not computed from VM daily KPIs | No VM KPI engine yet | Comes with the NOC and L2 workspaces (D-053) |
| NOC and L2 drafts still use the direct model client (facts only) | Fast, but not grounded in the knowledge base | Move them to the Agent E2 service once its latency suits a draft |
| L1 cannot split an incident yet | D-069 allows splitting | Add to the incident page |
| `?region=` scope on the wall is not built | D-068 | Add to the wall |
| The shift view uses the Asia Pacific shift only | One region shown | Use the viewer's region from sign-in |
| Limits record their expiry, but nothing removes them at expiry | No clock runs in the prototype | The action engine runs expiries (PCM core, 3.7) |
| No sign-in: every action is by `operator-1` | Prototype | Single sign-on (PCM core, 3.10) |
| "Is it up?" and "Is it set right?" have no planted story | Always green | Add stories with L2 |
| Weekly and monthly measures, repeated escalations and goal history are planted | No alert or escalation history engine yet | Compute them from the action record and alert history |
| Reject asks for its reason in a browser dialog | Prototype | A proper form on the page |
| The ITSM change calendar connector is simulated by story U-1 | No ITSM in the prototype | Build the read connector; verify on the live system (D-062) |
| L2 cannot yet reclassify a downtime as customer-caused | Specified (D-077) | Add to the L2 pages |
| Workflow state is one JSON document per name | Fine for the prototype | One table each in the product database |
| Capacity: host costs, trend weeks, purchase cover and waste limits are proposals | Numbers not yet confirmed | Author to confirm the settings marked proposal |
| L2 Capacity Remaining, Time Remaining and VM Remaining are placeholders (D-100) | No VCF Operations connector in 1.0 | Read them from VCF Operations; verify the metric keys on the live system (D-062) |

## Layout

| Path | What |
|---|---|
| `pcm_proto/catalog.py` | One function per catalog entry |
| `pcm_proto/generator.py` | Synthetic ACME data from estate, stories, seed and "now" |
| `pcm_proto/api.py` | API responses shaped by `spec/api/openapi.yaml`, each value with its metadata |
| `pcm_proto/server.py` | Mock API and static page server |
| `web/exec/` | The Executive page: HTML, CSS, JavaScript, SVG. No framework. |
| `web/fonts/` | Manrope, bundled, with its licence |
| `pcm_proto/noc.py` | NOC data, grouping, SOPs and the action engine (in memory) |
| `web/noc/` | The NOC wall and desktop pages |
| `pcm_proto/l2.py` | L2 check runs (daily, weekly), proposals, action policies, configuration, calendar, threshold replay, decisions, detailed inventory |
| `pcm_proto/l2_estate.py` | The L2 inventory tree: every host, VM and datastore in five views, and the scores Monitor reads |
| `pcm_proto/l2_monitor.py` | L2 Monitor: findings, pillar views, iceberg, group by, the tree and search |
| `pcm_proto/l2_cases.py` | L2 Troubleshoot: cases, chains, layers, timeline, who else, close |
| `pcm_proto/l2_improve.py` | L2 Improve: opportunities and risks under an object |
| `pcm_proto/capacity.py` | Capacity engine: usable capacity, forecast, decision dates, purchase plan, reclamation, what-if |
| `web/l2/` | The L2 shell page and its script: one frame for every L2 address |
| `web/capacity/` | The Capacity pages |
| `pcm_proto/docs.py` | Docs: objects, used on, history, export for private-cloud-explained |
| `web/docs/` | The Docs pages |
| `pcm_proto/store.py` | The prototype database (SQLite): action record, demand register, workflow state |
| `pcm_proto/agent_e2.py` | Agent E2 client: drafts, vocabulary check, fallback |
| `tests/` | Catalog and story tests (Python), page tests (Playwright) |
| `screenshots/` | Screenshots for review, written by the page test |
