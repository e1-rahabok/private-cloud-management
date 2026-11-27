---
page: /exec
question: "Is our private cloud healthy, does it have room to grow, and is it worth what it costs?"
role: executive
cadence: [weekly, monthly]
vocabulary: pcm/executive/spec/vocabulary.yaml
design: pcm/executive/design-note.md
decisions: [D-015, D-019, D-035, D-043, D-049, D-051, D-052, D-058, D-059, D-060]
---

# Executive page

One page, with drill-down to the next level (D-015). Desktop first, 1280 to 1440 px wide. The first level must be readable in under 30 seconds.

## Page rules

- **Only one drill-down panel is open per section.** Each panel has a Close button.
- **No "Live" indicator.** The header shows "Updated hh:mm" from `summary.updated_at` (Executive design, 4.2).
- **Every number shown comes from the API with its metadata.** If `meta.stale` is true, the number is replaced by a grey "No data" chip with the time of the last good value (D-041).
- **Words:**
  - All visible text follows `pcm/executive/spec/vocabulary.yaml`.
  - The labels in its `labels` section are used as written.
- **Read only.** No input fields on this page.

## Sections

### 1. Header

```yaml
question: "Whose page is this, and how fresh is it?"
role: executive
cadence: [weekly]
```

- ACME mark, name, "Private cloud".
- Section links: Health, Room to grow, Value, Goals.
- Today's date, and "Updated hh:mm" from `summary.updated_at`, in the viewer's time zone with the zone named, for example "Updated 10:05 GMT+8" (spec README, rule 8).
- **States:**
  - normal;
  - stale: when any section's data is stale, the "Updated" text shows the oldest time, plus "Some data is out of date".

### 2. Scale (hero)

```yaml
question: "How big is what we run, and how much is in use?"
role: executive
cadence: [weekly]
reads: [scale.compute_cores, scale.memory_tb, scale.storage_tb, scale.in_use_percent, scale.location_share_percent, capacity.location_decision]
api: /api/exec/summary → scale; /api/exec/locations/{id}
```

- **Headline:** "ACME Corp private cloud". Sub-headline: "The largest computer in the organisation." (mockup framing, Executive design, section 3).
- **Three meters:**

  | Meter | Label | Value |
  |---|---|---|
  | 1 | Computing power | `compute_cores`, with the unit "processor cores" |
  | 2 | Working memory | `memory_tb`, in TB |
  | 3 | Storage | `storage_tb`, in TB or PB |

  - Each meter shows its in-use share from `in_use_percent`.
  - When `in_use_percent.excludes` is not empty, the meter says so under the value, for example "Excludes Frankfurt and London: no data". A headline that changes without a reason looks like a real change (D-074).
  - The mockup's laptop-equivalent line is removed. Its reference value had no source, and the unit is now defined (Executive design, 4.8).
- **Five towers**, one per location:
  - Height follows `compute_cores`.
  - Lit share follows `in_use_percent`.
  - Label: location name and its share of the estate.
- **Selecting a tower** opens the location detail: compute, memory and storage with their in-use shares, the three health statuses for that location, and its decision from `capacity.location_decision`.
- **States:**
  - normal;
  - stale location: the tower is drawn in `stale` grey with "No data" and keeps its last known height, outlined, never lit;
  - loading;
  - error.

### 3. Health

```yaml
question: "Is it up? Is it fast? Is it safe?"
role: executive
cadence: [weekly, monthly]
reads: [up.availability_percent, up.actual_availability_percent, up.sla_allowance_minutes, fast.production_kpi, fast.class_group_kpi, safe.ksi_percent, safe.vms_below_sla, safe.findings, safe.risk_certificates]
api: /api/exec/summary → health; /api/exec/health/{question}
design: pcm/core/design-notes/service-levels.md
```

- **Three cards in the fixed order** up, fast, safe (D-035).
- **Each card has:**
  - the label from the vocabulary;
  - a status chip (visual style tokens);
  - a headline;
  - a sparkline;
  - one sentence from `health.<q>.sentence`.

| Card | Headline | Window | Example sentence |
|---|---|---|---|
| Is it up? | `up.availability_percent`, two decimals rounded down, "this month" | Calendar month to date (D-077) | "2 virtual machines in Tokyo were down for 15 minutes outside an approved change window. Every virtual machine is still within its target this month." |
| Is it fast? | `fast.production_kpi`, as "94 out of 100". No percent sign, no target line: performance has no SLA (D-072). | 7 days | "Virtual machines scored 94 out of 100 on performance. Gold scored above Silver, and Silver above Bronze, as promised." |
| Is it safe? | `safe.ksi_percent`, two decimal places, "this month" | Calendar month to date (D-073) | "72 virtual machines in London fell below the security target this month: remote admin access was left open on their servers for 8 hours. 2 security certificates expire within 30 days." |

- **Drill-down: Is it up?**
  - Per class: the target (Gold 99.975%, Silver 99.95%, Bronze 99.9%) and the virtual machines below it this month.
  - Operational and Actual availability side by side, each with its downtime in VM-minutes. Across thousands of VMs both percentages round to the same figure; the minutes show the difference. Plus the sentence "Downtime inside an approved change window does not count against the target."
  - Downtime events in plain words, each marked "counted" or "inside an approved change window" with its change number.
  - Values by location.
- **Drill-down: Is it fast?**
  - The three class scores: Gold, Silver, Bronze.
  - Whether the order is kept.
  - Values by location.
  - A 7-day or 30-day chart, with no target line.
  - The sentence "Performance is a score, not a contract: there is no performance target."
- **Drill-down: Is it safe?**
  - Virtual machines below the security target this month, against the contract value of 99.95%.
  - Open findings by check.
  - Risk: certificates expiring soon.
  - Values by location.
  - The sentence "The security target is 99.95% of each month for every virtual machine. Our own target is 100%."
- **No 1-hour view** (Executive design, 4.3).
- **States:**
  - normal (green, amber, red);
  - stale: the chip shows "No data", and the sparkline is hidden;
  - empty: "Is it safe?" with no unsecured minute and no open finding shows "No open findings this month.";
  - loading;
  - error.

### 4. Room to grow

```yaml
question: "When must we order more, and is it in the plan?"
role: executive
cadence: [weekly, monthly]
reads: [capacity.estate_decision, capacity.location_decision]
api: /api/exec/summary → room_to_grow; /api/exec/capacity
```

- **Headline:**
  - "Order by" followed by the date from `capacity.estate_decision.date`, with its location and resource in plain words. Example: "Order more working memory for Singapore by 18 December."
  - Next to it, the status chip. `in_plan` reads "In the plan".
- **Sub-line:** "Next purchase round closes on" `next_round_closes_on`.
- **Drill-down:** one row per location, earliest decision date first. Each row has:
  - the location;
  - the resource;
  - the date and its days from now;
  - the status chip.
- **The cluster group ID is never shown.** It is in the API for traceability only (avoided word "cluster").
- **States:**
  - normal (green, amber, red, in_plan);
  - stale;
  - empty: no decision date within 13 months shows "No order needed in the next 13 months";
  - loading;
  - error.

### 5. Value

```yaml
question: "What does it cost, what does it return, and how does it compare with the alternative?"
role: executive
cadence: [monthly]
reads: [value.cost_annual, value.tco, value.public_cloud_comparison, value.cost_avoided_ytd, value.cost_avoidable_next_round, recovery.site_recovery, speed.delivery_time]
api: /api/exec/summary → value; /api/exec/value/{card}
```

- **Three cards.**

#### Cost card

- **Headline:** `cost_annual` per year.
- **Line 2:** "Public cloud for the same estate:" from `public_cloud_comparison`, shown as "X% less than public cloud" or "X% more than public cloud".
- **Line 3:** "Cost avoided this year:" `cost_avoided_ytd`.
- **Drill-down:**
  - Product, service and people (D-060). No line items.
  - TCO over the depreciation period.
  - The public-cloud estimate and its date.
  - "Could still avoid in the next round:" `cost_avoidable_next_round`.
- **Rule:** the word "saving" is never used for reclamation. The label is "cost avoided" (D-060).

#### Site recovery card

- **Label:** "Site recovery", never "Recovery" alone (D-059).
- **Headline:** the worst location's status, with one sentence. Example: "Frankfurt's recovery was last tested 4 months ago, but 220 virtual machines added since were not in the test."
- **Drill-down:** one row per protected location, with:
  - the last test date;
  - the recovery time against the target;
  - the share of protected virtual machines tested;
  - the status.
- **Footnote, always visible in the drill-down:** "Shows site recovery tests only. Backups are not included."

#### Speed card

- **Headline:** `delivery_hours` against `delivery_hours_year_ago`.
- **Drill-down:** a 12-month trend.

#### States, for each card

- normal;
- stale;
- empty: for site recovery, "No protected locations";
- loading;
- error.

### 6. Goals

```yaml
question: "Are we on track for this year's goals?"
role: executive
cadence: [monthly]
reads: [goals.status]
api: /api/exec/summary → goals
```

- **One row per goal:**
  - the title in plain words;
  - the current value against the target;
  - the status chip: on track (`green`), at risk (`amber`), missed (`red`).
- At most six goals are shown. More than six means the goals are not goals.
- **States:**
  - normal;
  - stale;
  - empty: "No goals set for this year. They are set in the monthly review.";
  - loading;
  - error.

### 7. Footer

```yaml
question: "Where does this data come from?"
role: executive
cadence: [monthly]
```

- "Data from ACME's VCF Operations, VMware Live Site Recovery, VCF Automation and FinOps."
- In the prototype only: "Sample data for demonstration."
