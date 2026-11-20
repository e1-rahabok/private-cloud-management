---
page: /noc/wall
question: "Is anything broken right now that I must act on today?"
role: l1
cadence: [live]
vocabulary: catalog/vocabulary/noc.yaml
design: design/noc-workspace.md
decisions: [D-032, D-035, D-036, D-041, D-049, D-068]
---

# NOC wall

A TV on the wall. No mouse, no keyboard (D-032). Designed for a 14-inch view of the space: large numbers, few words (SP5 live screen).

## Rules

- **No buttons, links, inputs or menus** anywhere on the page (D-041).
- Reads `/api/noc/wall` every `noc.refresh_seconds`.
- **Rotation:** five screens in the fixed order, each for `noc.rotation_seconds`.
- **Status strip:** five chips on every screen, one per question, each with its label and colour.
- **Red interrupts the rotation:**
  - When `pin` is set, the wall shows that screen and stays on it.
  - With several entries in `pins`, it cycles through those screens only.
  - It resumes the full rotation when no pin remains. Acknowledgement happens on the desktop, not here.
- **A red chip whose incidents are all acknowledged** stays red and is marked "In hand".
- **Stale data:** the tile is grey with "No data" and the time of the last good data. Never a value.
- **If PCM itself is not healthy** (`pcm_ok` false): a full-width grey banner, "PCM has no data. Use the VCF Operations screens." (PCM core, 3.11).
- **With five or more displays,** each display shows one screen, given by `?screen=<name>`, and does not rotate (D-041).
- **Location scope:** all locations by default. `?region=<id>` limits it (D-068).
- **Prototype and test only:** `?rotate=<seconds>` overrides the rotation time.

## Screens

### 1. What changed?

```yaml
question: "What changed in the last hour that nobody planned?"
role: l1
cadence: [live]
reads: [noc.vm_changes, noc.vm_changes_expected, noc.changed_status]
```

- **One tile per location.**
- **Each tile has five rows:** created, deleted, powered off, moved, resized. Each row shows the count and the expected count.
- **A red row says:** "<n> deleted, about <expected> expected".
- **States:** normal (green, red), stale, loading, error.

### 2. Is it up?

```yaml
question: "Is anything down?"
role: l1
cadence: [live]
reads: [noc.up_items]
```

- One tile per location, listing the five counts.
- Large number: the total. Zero shows a large "0" and "Nothing down".
- When a VCF Operations instance gives no data, one line under the tiles names it and the time of its last good data, for example "No data from Europe's VCF Operations since 01:45 UTC". A red screen must say why it is red (SP5 5-second test).
- **States:** normal (green, red), stale, loading, error.

### 3. Is it fast?

```yaml
question: "Which clusters are not serving their VMs well right now?"
role: l1
cadence: [live]
reads: [noc.cluster_performance]
```

- **A heat map:** one cell per cluster, grouped by location. Each cell shows the cluster name and its score from 0 to 100, coloured by the SP5 band.
- **Below the map:** the clusters that are not green, largest number first. Each shows its score and the trend of the last hour.
- **States:** normal (green, amber, red), stale (per location group), loading, error.

### 4. Is it safe?

```yaml
question: "Is any server left open right now?"
role: l1
cadence: [live]
reads: [safe.findings, safe.risk_certificates, noc.safe_status]
```

- **One tile per location** with the open findings:
  - SSH or ESXi Shell running;
  - lockdown mode off;
  - certificates expired;
  - root logins not yet explained.
- **One line under the tiles:** certificates expiring within 30 days, as a count. It does not set the colour.
- **States:** normal (green, amber, red), stale, loading, error.

### 5. Is it set right?

```yaml
question: "Did anyone change a high-risk setting in the last hour?"
role: l1
cadence: [live]
reads: [noc.risky_changes]
```

- One tile per location with the count, and the latest change in one line.
- Zero shows "No risky changes in the last hour".
- **States:** normal (green, red), stale, loading, error.
