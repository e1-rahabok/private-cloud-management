---
page: /noc/wall
question: "Is anything broken right now that I must act on today?"
role: l1
cadence: [live]
vocabulary: catalog/vocabulary/noc.yaml
design: design/noc-workspace.md
decisions: [D-032, D-035, D-036, D-041, D-049, D-068, D-106]
---

# NOC wall

A TV on the wall. No mouse, no keyboard (D-032). Designed for a 14-inch view of the space: large numbers, few words (SP5 live screen).

## Layout

From top to bottom:

1. **Banner:** "ACME Corp Private Cloud" with "NOC wall" under it. At the right: **Running VMs** and **Running ESXi hosts** as large numbers (`noc.running_counts`), then the time of the last update. If a location has no data, its numbers are left out and a line says "Excludes <locations>: no data". With no data at all the number is "No data", never zero.
2. **Tabs:** six, one per screen, in the fixed order below. Display only (D-041).
3. **The screen** of the active tab.

## Rules

- **No buttons, links, inputs or menus** anywhere on the page (D-041). The tabs are display only.
- Reads `/api/noc/wall` every `noc.refresh_seconds`.
- **Rotation:** six screens in the fixed order, each for `noc.rotation_seconds`.
- **Tabs:**
  - Names only: Availability, Performance, Security, Volatility, Configuration, Capacity. No question, no summary word, no status colour (D-106).
  - The active tab is filled, with a bar under it. The others are plain.
  - A tab shows at most one small label: "In hand" (a red whose incidents are all acknowledged), "No data" (stale), or "<n> open" (open incidents on that screen). Nothing when none.
- **There is no screen title.** The active tab names the screen.
- **Colour only on what is wrong.** A normal tile, row or cell is neutral. An amber or red one is coloured and also carries its number or text (D-106).
- **Red interrupts the rotation:**
  - When `pin` is set, the wall shows that screen and stays on it.
  - With several entries in `pins`, it cycles through those screens only.
  - It resumes the full rotation when no pin remains. Acknowledgement happens on the desktop, not here.
- **Stale data:** the tile is grey with "No data" and the time of the last good data. Never a value.
- **If PCM itself is not healthy** (`pcm_ok` false): a full-width grey banner, "PCM has no data. Use the VCF Operations screens." (PCM core, 3.11).
- **With six or more displays,** each display shows one screen, given by `?screen=<name>`, and does not rotate (D-041). Names: `up`, `fast`, `safe`, `changed`, `set_right`, `capacity`.
- **Location scope:** all locations by default. `?region=<id>` limits it (D-068).
- **Prototype and test only:** `?rotate=<seconds>` overrides the rotation time.
- **Type:** nothing smaller than 14 px; rows 23 px or more.

## Screens

### 1. Availability

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

### 2. Performance

```yaml
question: "Which clusters are not serving their VMs well right now?"
role: l1
cadence: [live]
reads: [noc.cluster_performance, noc.performance_trend]
```

- **A heat map:** one cell per cluster, grouped by location. Each cell shows the score from 0 to 100 and the cluster name, coloured by the SP5 band only when the cluster is not green.
- **Below the map, two panels side by side:**
  - **Overall performance, last hour:** a line chart, 0 to 100, one point every 5 minutes (`noc.performance_trend`). Two lines: the average of all clusters and the lowest cluster. The end of each line is labelled; the lowest is labelled with its cluster. Band zones are drawn faintly behind. The time axis is in the viewer's time zone.
  - **Below normal:** the clusters that are not green, lowest score first. Each shows its score and "was <n> an hour ago", with a dot in its band colour. No summary word.
- **Chart states:** stale (clusters of a location with no data are left out; if none remain the panel shows "No data"), loading, error.
- **States:** normal (green, amber, red), stale (per location group), loading, error.

### 3. Security

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

### 4. Volatility

```yaml
question: "What changed in the last hour that nobody planned?"
role: l1
cadence: [live]
reads: [noc.vm_changes, noc.vm_changes_expected, noc.changed_status]
```

- **One tile per location.**
- **Each tile has five rows:** created, deleted, powered off, moved, resized, each with its count.
- **A red row** shows the count and, on a line under it, "About <expected> expected".
- **States:** normal (green, red), stale, loading, error.

### 5. Configuration

```yaml
question: "Did anyone change a high-risk setting in the last hour?"
role: l1
cadence: [live]
reads: [noc.risky_changes]
```

- One tile per location with the count, and the latest change in one line.
- Zero shows "No risky changes in the last hour".
- **States:** normal (green, red), stale, loading, error.

### 6. Capacity

```yaml
question: "How full is each location, and how long until it is full?"
role: l1
cadence: [live]
reads: [noc.capacity_status, scale.in_use_percent, capacity.time_remaining_days]
```

- **One tile per location** with three rows: compute, memory, storage. Each shows the share of usable capacity in use, as a whole number with a bar.
- **A line at the foot of the tile:** "Time remaining", in days, for the tightest cluster group of the location. "Beyond 13 months" when the capacity engine finds no run-out in its horizon.
- **One line under the tiles** says what the numbers are: in use is the share of usable capacity; time remaining is for the tightest cluster group.
- The tile is red only when `noc.capacity_status` is red. The wall makes no purchase decision; it shows the engine's result.
- **States:** normal (green, red), stale, loading, error.
