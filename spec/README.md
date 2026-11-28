# PCM specification

PCM is built from its specification (D-010). AI generates all code from it. Nobody edits generated code by hand (D-070).

The specification sits beside the code generated from it, in one folder per workspace under [`../pcm/`](../pcm) (D-133). This folder holds the specification's front page and the requirements of PCM's work. The reasons behind each item are in the design notes and [`../decisions.md`](../decisions.md). Every item links to them by ID.

## Layout

`<workspace>` is one of `executive`, `noc`, `l2`, `capacity` and `docs_workspace` (the Docs workspace's folder, D-135).

| Path | Holds | Format |
|---|---|---|
| `pcm/<workspace>/design-note.md` | The workspace's design note: the reasons behind its specification | Markdown |
| `pcm/<workspace>/spec/pages/` | One file per page | Markdown with a YAML header |
| `pcm/<workspace>/spec/api.yaml` | The workspace's part of the API contract that synthetic data and real collection both fill | OpenAPI |
| `pcm/<workspace>/spec/catalog.yaml` | The workspace's definitions: metrics, models, check rules | YAML |
| `pcm/<workspace>/spec/vocabulary.yaml` | The words the workspace's pages use and avoid | YAML |
| `pcm/<workspace>/spec/acceptance-tests.yaml` | The workspace's acceptance tests | YAML |
| [`pcm/noc/spec/sops/`](../pcm/noc/spec/sops), [`pcm/l2/spec/action-policies.yaml`](../pcm/l2/spec/action-policies.yaml) | The NOC's SOPs and L2's action policies | YAML |
| [`pcm/core/design-notes/`](../pcm/core/design-notes) | The design notes every workspace follows | Markdown |
| [`pcm/core/spec/objects.yaml`](../pcm/core/spec/objects.yaml) | The object model | YAML |
| [`pcm/core/spec/catalog/`](../pcm/core/spec/catalog) | Settings, thresholds and configuration standards, which every workspace reads | YAML |
| [`pcm/core/spec/demo-data/`](../pcm/core/spec/demo-data) | Synthetic ACME estate and PCM scenario stories | YAML |
| [`pcm/core/spec/database-schema.sql`](../pcm/core/spec/database-schema.sql) | The prototype database schema (D-080) | SQL |
| [`pcm/core/spec/visual-style.md`](../pcm/core/spec/visual-style.md) | Tokens, colour roles, components | Markdown |
| [`pcm/core/spec/acceptance-tests.yaml`](../pcm/core/spec/acceptance-tests.yaml) | The acceptance tests of the database | YAML |
| [`requirements/`](requirements) | PCM's requirements for release 1.0, with test scenarios; milestones in the workspace's [ROADMAP](https://github.com/e1-rahabok/private-cloud-workspace/blob/main/ROADMAP.md) | Markdown |
| [`test-plan.md`](test-plan.md) | How PCM is tested: levels, lab run order, reference script, pass criteria | Markdown |

## Rules for builders

1. **A page never computes a number.** It names a catalog entry by ID, and the API returns that entry's value. If a page needs a number that has no catalog entry, add the entry first (D-070, 3.2).
2. **Every page and visual names its question, role and cadence** in its header (D-052). Without them it is not built.
3. **Every visual handles every state listed for it:** normal, the warning colours, stale, empty, loading, error. Stale is grey with "No data", never the last value (D-041).
4. **Every value from the API carries its metadata:** source, time, definition ID and version, and a stale flag (PCM core, 3.5). Pages show the time; they never hide the stale flag.
5. **Words follow the workspace's vocabulary list** in its `spec/vocabulary.yaml` (D-051).
6. **Settings are not thresholds invented by the builder.** Every threshold or target is a named setting in `pcm/core/spec/catalog/settings.yaml`, with its default and who owns it.
7. **No request leaves the PCM host.** Fonts, scripts and images ship with PCM. An on-premises customer may have no internet access (D-004, D-074).
8. **Times are shown in the viewer's time zone, with the zone named.** Example: "Updated 10:05 GMT+8". A global team reads the same page from several zones (D-074).
9. **Decision IDs (D-nnn) and design section numbers never appear in page text.** They are for the specification and its reviewers, not for operators.

## Build and test

- Generated code sits beside its specification in each workspace folder: the server code (Python), `pages/` and `tests/`. Every generated file is marked as generated. How to run and test it: [`../pcm/README.md`](../pcm/README.md).
- The synthetic data generator reads `pcm/core/spec/demo-data/estate.yaml`, `pcm/core/spec/demo-data/scenario-stories.yaml`, a seed, and "now" (D-067).
- The demo uses the present time. Each test passes its own "now".
- The tests in each workspace's `tests/` run at three levels: catalog, PCM scenario story, page (D-070, section 4).

## Status

| Workspace | Specification | Build |
|---|---|---|
| Executive | Written (D-053, step 1) | First build: all tests pass (`../pcm/README.md`) |
| NOC | Written (D-053, step 2) | First build: all tests pass (`../pcm/README.md`) |
| L2 | Rewritten around Monitor, Troubleshoot and Improve: frame, monitor, troubleshoot, case, improve, rules, calendar (D-083 to D-090) | Third build: all tests pass (`../pcm/README.md`) |
| Capacity | Written (D-053, step 4) | First build: all tests pass (`../pcm/README.md`) |
| Docs | Written (D-082) | First build: all tests pass (`../pcm/README.md`) |

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
| Capacity Remaining, Time Remaining and VM Remaining on a VM, host and cluster | `l2.capacity_remaining` (D-100) | VCF Operations capacity engine |

- **The PCM adapter's cluster KPIs and check**
  - Item: Cluster Consumption, Cluster Performance, Cluster Risk and their parts; the Periodic Cluster Check (three check values and Close for Business, with the adapter's period, time and Worst Percent); vSphere World's Highest Cluster Utilization, Highest 10 Percent Cluster Utilization, Cluster Delta Close and Open Count
  - Used by: `l2.cluster_kpi_series`, `l2.cluster_check`, `l2.consumption_parts`, `l2.consumption_spread`, `l2.closed_count` (D-094)
  - Assumed source: PCM adapter (vCommunity, D-096), through VCF Operations
