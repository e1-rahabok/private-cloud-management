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

The page test needs Node and Playwright with Chromium. It also writes the review screenshots to `screenshots/`.

## Results: Executive

| Level | Tests | Result |
|---|---|---|
| Catalog | CAT-1 to CAT-18 | 18 passed |
| Story | ST-1 to ST-8 | 8 passed |
| Page | PG-1 to PG-12 | 12 passed |
| Extra | Same inputs give the same data; stories hold on another day (D-067) | 2 passed |

Second build: "Is it fast?" became a KPI with no target (D-072); "Is it safe?" became the Security SLA (D-073).

Third build: the three gaps from the first review are fixed in the specification (D-074) and tested by PG-10 to PG-12: times in the viewer's zone with the zone named; meters say which stale locations they leave out; the Manrope font ships in `web/fonts/` (SIL Open Font License), so no request leaves the PCM host.

**One defect found and fixed in the specification:** green and "in the plan" chips used `#0A7A6D` on `#D2ECE5`, which has a contrast of 4.2:1. Amber chips used `#B45309` on `#F5E1B8`, at 3.9:1. Both came from the mockup and are below the 4.5:1 minimum. PG-9 found them. `spec/design-system/tokens.md` now has `accent.ink` and `amber.ink`.

## Results: NOC

| Level | Tests | Result |
|---|---|---|
| Catalog | NCAT-1 to NCAT-6 | 6 passed |
| Story | NST-1 to NST-8 | 8 passed |
| Page | NPG-1 to NPG-8 | 8 passed |

**Found while reviewing the screenshots, and fixed in the specification first:**
- The SOP step "is the villain non-production?" showed "fail". It is a branch, not a failure. Branch steps now show their answer.
- The action history showed action IDs (`stop_provisioning`). It now shows plain words.
- "Is it up?" turned red when Europe's VCF Operations stopped answering, with nothing on screen saying why. The screen now names the source and the time of its last good data.

**One test expectation corrected in the specification:** NST-1 expected the wall to pin "Is it fast?". Stories N-1 and N-3 are both active, so the wall pins two screens and cycles through both. The test now checks that "Is it fast?" is among the pins.

## Known gaps (to fix in the specification, not here)

| Gap | Effect | Proposed fix |
|---|---|---|
| Capacity decision dates are planted from stories | No forecast engine yet | Comes with the Capacity workspace (D-053) |
| Class group KPIs are planted from the background, not computed from VM daily KPIs | No VM KPI engine yet | Comes with the NOC and L2 workspaces (D-053) |
| Agent E2 on the NOC incident page shows a fixed draft | No local LLM in the prototype | Connect Agent E2 (D-017) |
| L1 cannot split an incident yet | D-069 allows splitting | Add to the incident page |
| `?region=` scope on the wall is not built | D-068 | Add to the wall |
| The shift view uses the Asia Pacific shift only | One region shown | Use the viewer's region from sign-in |
| Limits record their expiry, but nothing removes them at expiry | No clock runs in the prototype | The action engine runs expiries (PCM core, 3.7) |
| No sign-in: every action is by `operator-1` | Prototype | Single sign-on (PCM core, 3.10) |
| "Is it up?" and "Is it set right?" have no planted story | Always green | Add stories with L2 |
| L2 and Capacity workspaces | Not built yet | Next in order (D-053) |

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
| `tests/` | Catalog and story tests (Python), page tests (Playwright) |
| `screenshots/` | Screenshots for review, written by the page test |
