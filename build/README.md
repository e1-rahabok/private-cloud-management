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

Options, in the page URL or on the API:

| Parameter | Effect |
|---|---|
| `now=2026-10-19T10:05:00+08:00` | Fix the clock (D-067). Omitted: the present time. |
| `enable=E-7` | Switch on an optional story, here Europe's VCF Operations going stale. |
| `screen=fast` | Wall only: show one screen without rotating, for a wall with one display per screen (D-041). |
| `rotate=5` | Wall only, prototype and test: rotate every 5 seconds instead of 60. |

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

The page test needs Node and Playwright with Chromium. It also writes the review screenshots to `screenshots/`.

## Results: Executive

| Level | Tests | Result |
|---|---|---|
| Catalog | CAT-1 to CAT-18 | 18 passed |
| Story | ST-1 to ST-8 | 8 passed |
| Page | PG-1 to PG-13 | 13 passed |
| Extra | Same inputs give the same data; stories hold on another day (D-067) | 2 passed |

Second build: "Is it fast?" became a KPI with no target (D-072); "Is it safe?" became the Security SLA (D-073).

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

Six of the nine L2 pages in this build: Today (daily check), Escalations, Investigate, Configuration, Calendar, Thresholds. Weekly, monthly and detailed inventory follow in the next L2 build.

| Level | Tests | Result |
|---|---|---|
| Catalog | LCAT-1 to LCAT-3 | 3 passed |
| Story | LST-1 to LST-8, plus the RCA draft record | 9 passed |
| Page | LPG-1 to LPG-8 | 8 passed |

- **The escalation loop works across workspaces.** The NOC escalates FR-S-02. L2 sees it with raw counters and drafts the root cause analysis with Agent E2. L2 closes it with a cause, a fix and a detection decision, and the NOC incident closes too.
- **Live RCA draft, 2026-11-20 (Gemma 4 31B through the gateway):** grounded in the evidence. It separates what is proven from the fix, and reports only what L1 did. The wording is stiff.

**Found in review and fixed in the specification first:** decision IDs ("D-039", "D-073", "D-040") appeared in page text and SOP steps. New builder rule 9: decision IDs never appear in page text. Tests PG-13, NPG-10 and LPG-8 now check every workspace, and the NOC test found two SOP steps that leaked one.

## Agent E2 (D-076)

- Agent E2 drafts on the NOC incident page through one OpenAI-compatible client (`pcm_proto/agent_e2.py`, standard library only).
- **Demo:** Vercel AI Gateway, model `google/gemma-4-31b-it`, one of Agent E2's local candidates. The key comes from `AI_GATEWAY_API_KEY`. **Customer site:** set `agent_e2.endpoint` to the local model server.
- **Tests run with `PCM_AGENT_E2_MODE=mock`,** so they do not depend on the network.
- **Live check, 2026-11-20:** an explanation takes about 1.4 s, an escalation note about 6 s.
- **Found in the first live call, and fixed:**
  - The model reported an SOP action as done when it was only available.
  - The facts now keep `available_action` apart from `actions_already_done`, and the rules say so.
  - Test NST-12 holds the separation.

## Known gaps (to fix in the specification, not here)

| Gap | Effect | Proposed fix |
|---|---|---|
| Capacity decision dates are planted from stories | No forecast engine yet | Comes with the Capacity workspace (D-053) |
| Class group KPIs are planted from the background, not computed from VM daily KPIs | No VM KPI engine yet | Comes with the NOC and L2 workspaces (D-053) |
| Agent E2 gets incident facts only, not the knowledge base | It explains what PCM shows, not why SP5 says so | Connect the Agent E2 harness (reading plan over the knowledge base) behind the same client |
| L1 cannot split an incident yet | D-069 allows splitting | Add to the incident page |
| `?region=` scope on the wall is not built | D-068 | Add to the wall |
| The shift view uses the Asia Pacific shift only | One region shown | Use the viewer's region from sign-in |
| Limits record their expiry, but nothing removes them at expiry | No clock runs in the prototype | The action engine runs expiries (PCM core, 3.7) |
| No sign-in: every action is by `operator-1` | Prototype | Single sign-on (PCM core, 3.10) |
| "Is it up?" and "Is it set right?" have no planted story | Always green | Add stories with L2 |
| L2 weekly, monthly and detailed inventory pages | Not built yet | Next L2 build |
| Reject and promote ask for their reason in a browser dialog | Prototype | A proper form on the page |
| Capacity workspace | Not built yet | Next in order (D-053) |

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
| `pcm_proto/l2.py` | L2 daily check, proposals, trust ladder, escalations, configuration, calendar, threshold replay |
| `web/l2/` | The L2 pages |
| `pcm_proto/agent_e2.py` | Agent E2 client: drafts, vocabulary check, fallback |
| `tests/` | Catalog and story tests (Python), page tests (Playwright) |
| `screenshots/` | Screenshots for review, written by the page test |
