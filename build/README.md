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

Options, in the page URL or on the API:

| Parameter | Effect |
|---|---|
| `now=2026-10-19T10:05:00+08:00` | Fix the clock (D-067). Omitted: the present time. |
| `enable=E-7` | Switch on an optional story, here Europe's VCF Operations going stale. |
| `screen=fast` | Wall only: show one screen without rotating, for a wall with one display per screen (D-041). |
| `rotate=5` | Wall only, prototype and test: rotate every 5 seconds instead of 60. |

**Database (D-080):** what people and policies do is kept in SQLite at `var/pcm.sqlite`, so it survives a restart. Set `PCM_DB` to use another file. Tests use `PCM_DB=:memory:`. To start clean, stop the server and delete the file. Synthetic metrics are generated from "now", never stored.

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

| Level | Tests | Result |
|---|---|---|
| Catalog | NCAT-1 to NCAT-6 | 6 passed |
| Story | NST-1 to NST-12 | 12 passed |
| Page | NPG-1 to NPG-10 | 10 passed |

**Found while reviewing the screenshots, and fixed in the specification first:**
- The SOP step "is the villain non-production?" showed "fail". It is a branch, not a failure. Branch steps now show their answer.
- The action history showed action IDs (`stop_provisioning`). It now shows plain words.
- "Is it up?" turned red when Europe's VCF Operations stopped answering, with nothing on screen saying why. The screen now names the source and the time of its last good data.

**One test expectation corrected in the specification:** NST-1 expected the wall to pin "Is it fast?". Stories N-1 and N-3 are both active, so the wall pins two screens and cycles through both. The test now checks that "Is it fast?" is among the pins.

## Results: L2

All nine L2 pages: Today (daily check), Weekly, Monthly, Escalations, Investigate, Configuration, Inventory, Calendar, Thresholds.

| Level | Tests | Result |
|---|---|---|
| Catalog | LCAT-1 to LCAT-6 | 6 passed |
| Story | LST-1 to LST-14, the RCA draft record, ask-why and no-promotion checks | 18 passed |
| Page | LPG-1 to LPG-13 | 13 passed |

- **The escalation loop works across workspaces.** The NOC escalates FR-S-02. L2 sees it with raw counters and drafts the root cause analysis with Agent E2. L2 closes it with a cause, a fix and a detection decision, and the NOC incident closes too.
- **Live RCA draft, 2026-11-20 (Gemma 4 31B through the gateway):** grounded in the evidence. It separates what is proven from the fix, and reports only what L1 did. The wording is stiff.

**Weekly, monthly and inventory (second L2 build):**
- **Weekly** shows only what a day cannot: a snapshot growing 7 nights in a row (full in about 14 days), one vCPU at 97% in a VM averaging 14%, one log disk at 38 ms in a VM averaging 4 ms, three hosts behind on patches. The slipped alert on va-db-033 is explained by its log disk.
- **Monthly** opens with last month's decisions: the snapshot decision is overdue, and it is the cause of this week's drift. Goal projections are the CIO page's numbers. The capacity outlook is the Capacity workspace's own.
- **Inventory** counts the explained changes and lists only the unexplained: a CPU limit set directly in vCenter on a production Gold VM, and the 40 Tokyo deletions. PCM's own actions are explained by the action record.
- **Found in review and fixed:** long chips overlapped the text; trend bars started at zero, so a 12% drift looked flat; alert counts showed decimals.

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
- **Contention:** FR-Silver says "Full now: VMs waiting" on FR-S-02 (score 22, the NOC's own number).
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

- "Ask Agent E2 why" on `/l2/investigate/{object}` calls the Agent E2 service (`harness/answer_service.py` in the Agent E2 repository, merged 2026-11-20). PCM sends the question, the investigation facts on the page, and the role.
- **Run it next to PCM:** `python3 harness/answer_service.py --port 8090` from the Agent E2 repository. It takes about 50 s to start. The URL is the setting `agent_e2.service_url`.
- **Live check, 2026-11-20:**
  - sg-app-117 answered in 32 s: "the issue is inside the Guest OS".
  - The answer cites SP5 files and adds that the run queue of 6.5 per vCPU is in the orange band. It names what to check next.
  - Minor: it cited the cluster performance file for VM-level green bands.
- **Without the service,** the page says "The Agent E2 service is not available" (test LPG-9).

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
| `pcm_proto/l2.py` | L2 daily check, proposals, action policies, escalations, configuration, calendar, threshold replay |
| `pcm_proto/capacity.py` | Capacity engine: usable capacity, forecast, decision dates, purchase plan, reclamation, what-if |
| `web/l2/` | The L2 pages |
| `web/capacity/` | The Capacity pages |
| `pcm_proto/store.py` | The prototype database (SQLite): action record, demand register, workflow state |
| `pcm_proto/agent_e2.py` | Agent E2 client: drafts, vocabulary check, fallback |
| `tests/` | Catalog and story tests (Python), page tests (Playwright) |
| `screenshots/` | Screenshots for review, written by the page test |
