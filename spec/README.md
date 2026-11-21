# PCM specification

This folder is what PCM is built from (D-010). AI generates all code from it. Nobody edits generated code by hand (D-070).

The reasons behind each item are in [`../design/`](../design) and [`../decisions.md`](../decisions.md). Every item here links to them by ID.

## Layout

| Folder | Holds | Format |
|---|---|---|
| `objects/` | The object model | YAML |
| `catalog/` | Every definition: metrics, models, thresholds, settings, vocabulary | YAML |
| `api/` | The API contract that synthetic data and real collection both fill | OpenAPI |
| `design-system/` | Tokens, colour roles, components | Markdown |
| `workspaces/` | One file per page | Markdown with a YAML header |
| `data/` | Synthetic ACME estate and stories | YAML |
| `database/` | The prototype database schema (D-080) | SQL |
| `tests/` | Acceptance tests | YAML |

## Rules for builders

1. **A page never computes a number.** It names a catalog entry by ID, and the API returns that entry's value. If a page needs a number that has no catalog entry, add the entry first (D-070, 3.2).
2. **Every page and visual names its question, role and cadence** in its header (D-052). Without them it is not built.
3. **Every visual handles every state listed for it:** normal, the warning colours, stale, empty, loading, error. Stale is grey with "No data", never the last value (D-041).
4. **Every value from the API carries its metadata:** source, time, definition ID and version, and a stale flag (PCM core, 3.5). Pages show the time; they never hide the stale flag.
5. **Words follow the workspace's vocabulary list** in `catalog/vocabulary/` (D-051).
6. **Settings are not thresholds invented by the builder.** Every threshold or target is a named setting in `catalog/settings.yaml`, with its default and who owns it.
7. **No request leaves the PCM host.** Fonts, scripts and images ship with the build. An on-premises customer may have no internet access (D-004, D-074).
8. **Times are shown in the viewer's time zone, with the zone named.** Example: "Updated 10:05 GMT+8". A global team reads the same page from several zones (D-074).
9. **Decision IDs (D-nnn) and design section numbers never appear in page text.** They are for the specification and its reviewers, not for operators.

## Build and test

- Generated code goes in `../build/`, which is marked as generated.
- The synthetic data generator reads `data/estate.yaml`, `data/stories.yaml`, a seed, and "now" (D-067).
- The demo uses the present time. Each test passes its own "now".
- Tests in `tests/` run at three levels: catalog, story, page (D-070, section 4).

## Status

| Workspace | Specification | Build |
|---|---|---|
| Executive | Written (D-053, step 1) | First build: all tests pass (`../build/README.md`) |
| NOC | Written (D-053, step 2) | First build: all tests pass (`../build/README.md`) |
| L2 | Rewritten around Monitor, Troubleshoot and Improve: frame, monitor, troubleshoot, case, improve, rules, calendar (D-083 to D-090) | Third build: all tests pass (`../build/README.md`) |
| Capacity | Written (D-053, step 4) | First build: all tests pass (`../build/README.md`) |
| Docs | Written (D-082) | First build: all tests pass (`../build/README.md`) |

## Assumptions to verify on the live system (D-062)

Each item below is assumed to be available. The prototype does not depend on it, because it runs on synthetic data. Check each one when the live VCF 9.1 system is available.

| Item | Used by | Assumed source |
|---|---|---|
| Site recovery plans, test runs, protected VMs | `recovery.*` | VMware Live Site Recovery API |
| Request submitted and delivered times | `speed.delivery_time` | VCF Automation API |
| Certificate expiry per component | `safe.certificates_expiring` | SDDC Manager or vCenter API |
| SSH, ESXi Shell and lockdown state per host | `safe.*` | vCenter API, through VCF Operations properties |
| Root logins | `safe.root_logins` | VCF Operations for Logs |
| 20-second peak metrics | `fast.*`, capacity forecast | VCF Operations |
| Cluster Consumption, Cluster Performance, Cluster Risk and their parts; the Periodic Cluster Check (three check values and Close for Business, with the adapter's period, time and Worst Percent); vSphere World's Highest Cluster Utilization, Highest 10 Percent Cluster Utilization, Cluster Delta Close and Open Count | `l2.cluster_kpi_series`, `l2.cluster_check`, `l2.consumption_parts`, `l2.consumption_spread`, `l2.closed_count` (D-094) | PCM adapter (vCommunity, D-096), through VCF Operations |
