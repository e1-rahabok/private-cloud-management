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

Open `http://localhost:8080/exec`.

Options, in the page URL or on the API:

| Parameter | Effect |
|---|---|
| `now=2026-10-19T10:05:00+08:00` | Fix the clock (D-067). Omitted: the present time. |
| `enable=E-7` | Switch on an optional story, here Europe's VCF Operations going stale. |

## Test

```bash
python3 -m unittest build.tests.test_executive -v
```

```bash
node build/tests/page.test.mjs
```

The page test needs Node and Playwright with Chromium. It also writes the review screenshots to `screenshots/`.

## Results of the first build

| Level | Tests | Result |
|---|---|---|
| Catalog | CAT-1 to CAT-18 | 18 passed |
| Story | ST-1 to ST-8 | 8 passed |
| Page | PG-1 to PG-9 | 9 passed |
| Extra | Same inputs give the same data; stories hold on another day (D-067) | 2 passed |

Second build: "Is it fast?" became a KPI with no target (D-072); "Is it safe?" became the Security SLA (D-073).

**One defect found and fixed in the specification:** green and "in the plan" chips used `#0A7A6D` on `#D2ECE5`, which has a contrast of 4.2:1. Amber chips used `#B45309` on `#F5E1B8`, at 3.9:1. Both came from the mockup and are below the 4.5:1 minimum. PG-9 found them. `spec/design-system/tokens.md` now has `accent.ink` and `amber.ink`.

## Known gaps (to fix in the specification, not here)

| Gap | Effect | Proposed fix |
|---|---|---|
| Capacity decision dates are planted from stories | No forecast engine yet | Comes with the Capacity workspace (D-053) |
| Class group KPIs are planted from the background, not computed from VM daily KPIs | No VM KPI engine yet | Comes with the NOC and L2 workspaces (D-053) |
| Times show in the browser's time zone | A viewer in another zone sees a different "Updated" time from the CIO | Specify the time zone shown: the viewer's, with the zone named |
| Estate "in use" percentages skip stale locations | With Europe stale, the headline changes without saying why | Specify a note on the meter: "excludes Frankfurt and London: no data" |
| The page loads the Manrope font from Google Fonts | An on-premises customer without internet access falls back to the system font (D-004) | Bundle the font with the build |
| Only the Executive page exists | Other workspaces follow in order (D-053) | |

## Layout

| Path | What |
|---|---|
| `pcm_proto/catalog.py` | One function per catalog entry |
| `pcm_proto/generator.py` | Synthetic ACME data from estate, stories, seed and "now" |
| `pcm_proto/api.py` | API responses shaped by `spec/api/openapi.yaml`, each value with its metadata |
| `pcm_proto/server.py` | Mock API and static page server |
| `web/exec/` | The Executive page: HTML, CSS, JavaScript, SVG. No framework. |
| `tests/` | Catalog and story tests (Python), page tests (Playwright) |
| `screenshots/` | Screenshots for review, written by the page test |
