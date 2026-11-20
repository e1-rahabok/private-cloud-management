# Executive workspace

Status: draft for the author's review. Decisions proposed here move to [`decisions.md`](../decisions.md) once accepted.

Path: `privatecloud.acme.com/exec` (D-028). Starting point: the [Executive Dashboard mockup](https://e1-rahabok.github.io/VMW-Executive-Dashboard/design/export/) (D-015). This document lists what stays, what changes, and why.

## 1. The role

- **The CIO.** Under D-048, this is the old middle layer: they know the technology, have little time, and present upward to the CEO, CFO and board.
- **SP5 People, IT Management:**
  - big picture, trends and the future;
  - not hour-by-hour;
  - a weekly overview and a monthly presentation, supported by a live dashboard;
  - no troubleshooting.
- **One page, with drill-down to the next level** (D-015).
- **Plain language with basic IT words** (D-051).

**Why this workspace matters**
- It is the page that gets PCM approved (D-053).
- It is also the page that keeps the private cloud funded.
- If the CIO cannot defend the platform upward in five minutes, the money goes elsewhere.

## 2. The questions the page answers (D-052)

Every section must name its question. Anything that does not answer one of these is cut.

| Section | Question | Cadence |
|---|---|---|
| Scale | How big is what we run, and how much is in use? | Weekly |
| Health | Is it up? Is it fast? Is it safe? (D-035) | Weekly |
| Room to grow | When must we order more, and is it in the plan? | Weekly, monthly |
| Value | What does it cost, what does it return, and how does it compare with the alternative? | Monthly |
| Goals | Are we on track for this year's goals? (D-043) | Monthly |

## 3. What stays from the mockup, and why

- **"The largest computer in the organisation."** The framing works. It turns a cost centre into an asset the board can picture.
- **Summary first, then one level down.** SP5 dashboard design: an executive is "not frequent, high level". A page that takes effort will not be used.
- **Days remaining instead of percentages.** A date leads to a decision. A percentage does not.
- **The decision date.** Run-out date minus delivery time. The most useful single number on the page.
- **Custom SVG, no stock icons, Manrope, the colour roles.** The visual language is good and already accessible.
- **Desktop first. Read-only for the summary.**

## 4. What changes, and why

### 4.1 "Is it secure?" becomes "Is it safe?", measured as the SP5 Security SLA (D-073)

- Superseded in part by `design/service-levels.md`: the hygiene checks below are the release 1.0 benchmark of the Security SLA, measured as unsecured time per VM per month. "Is it fast?" became a KPI with no target (D-072).


- **Mockup:** firewall and intrusion events, for example "Attackers tried and failed".
- **Change:** "Is it safe?" (D-035) shows VMware platform hygiene (D-049):
  - certificates near expiry;
  - root logins;
  - ESXi Shell or SSH left on;
  - lockdown mode off.

  These appear in plain words: "2 security certificates expire within 30 days".
- **Why:**
  - Security operations is out of scope until after 1.0 (D-008, D-044).
  - Showing attack data we do not own invites the question "who is watching this?", and the answer would be nobody.

### 4.2 "Live" is removed from the header

- **Mockup:** a green "Live" pill.
- **Change:** "Updated hh:mm" only.
- **Why:**
  - The CIO's view is weekly and monthly.
  - "Live" invites the CIO to treat this page as a monitoring screen, and to call the NOC about a 2-minute dip already handled.
  - private-cloud-explained names this risk: an executive view mistaken for live monitoring.

### 4.3 The time model follows the cadence

- **Mockup:** 7 days, then 1 hour.
- **Change:**
  - Health: 7 days, then 30 days in the drill-down.
  - Room to grow: 13 months of history plus the forecast.
  - Value: this year against last year.
  - No 1-hour view.
- **Why:**
  - A 1-hour view belongs to the NOC.
  - The CIO decides on weeks and quarters. Showing the last hour pulls them into operations, which SP5 says they should not do.

### 4.4 Room to grow comes from the Capacity workspace

- **Mockup:** one "days remaining" headline, the minimum across resources, with locations as the only breakdown.
- **Change:**
  - The headline is the **earliest decision date** of any cluster group in a location, taken from the Capacity workspace (Capacity design, 3.7).
  - The drill-down shows each location's earliest date and whether it is **already in the next procurement round** (Capacity design, 3.8).
- **Why:**
  - Capacity is per cluster (Capacity design, 3.1). A location-wide total can show plenty while one cluster group runs out.
  - One source for the date. If the CIO and the Capacity team see different dates, the CIO stops trusting both.
  - "Is it in the plan?" is the CIO's real question. A short date already covered by the next round is not a problem. A short date outside it is.

### 4.5 Value shows totals, not line items

- **Mockup:** cost against a public-cloud estimate, with a breakdown into people, hardware, facilities and software. Risk, as recovery time. Speed, as delivery time.
- **Change:**
  - **Cost:** the total, ROI and TCO (D-019).
    - The only breakdown is product, service and people (D-060). It replaces the mockup's four categories.
    - There are no line items.
    - The public-cloud comparison comes from FinOps (D-058). It covers the whole estate over the depreciation period, not one VM for one day.
    - Line items live in the Capacity workspace (D-019, Capacity design 3.8).
  - **Site recovery (D-059):** from VMware Live Site Recovery (formerly Site Recovery Manager) test results:
    - the last test date;
    - the recovery time achieved, against the target;
    - the share of protected VMs actually tested.

    The card is labelled "site recovery" and does not claim backups. The risk matrix is removed: PCM holds no risk register.
  - **Speed:** delivery time from VCF Automation request timestamps.
- **Why:**
  - The CIO defends totals upward. Line items lead to "why did memory cost X?", which is the Capacity team's conversation.
  - Each card must come from data PCM actually holds (VMware only, D-034).
  - A risk matrix typed in by hand is a slide, not a dashboard. It would be stale by the second meeting.

### 4.6 Waste is part of value

- **Change:** the cost card shows **cost avoided**, from the Capacity workspace (Capacity design, 3.11; D-060):
  - purchases deferred by reclamation, valued at today's price;
  - what is still reclaimable.
- **Why:**
  - SP5: show the CFO the cost of waste. The CFO holds the budget and makes each business line act.
  - This page is how the CFO sees it.
  - It also makes the CIO's case honest: "we cost less than public cloud, and here is what we are still wasting".

### 4.7 A goals section is added

- **Change:** a short row with the year's goals (D-043) and their status this month: on track, at risk or missed.
- **Why:**
  - The monthly review measures goals.
  - The CIO is the one asked about them upward.
  - Goals the CIO cannot see are not the CIO's goals.

### 4.8 The word list follows D-051

- **Change:** basic IT words are allowed, among them server, storage, network, virtual machine, backup, recovery, outage and capacity.
  - "Computing power" and "working memory" stay as labels.
  - The drill-down may show units:
    - "computing power (processor cores)";
    - "working memory (GB of memory)".
- **Why:**
  - The CIO knows the technology (D-048) and presents upward. Basic words help both.
  - A build test fails if an avoided term appears (D-051).
  - The mockup's "units" for computing power were never defined. Physical cores are what the CIO's audience can picture and what the VCF licence counts.

### 4.9 Locations come from federation

- **Change:** each location is one or more VCF Operations instances, federated by PCM (D-009).
- **Why:** a global enterprise runs one VCF Operations per region or site. The CIO sees one estate.

## 5. Not on the page

| Item | Why not |
|---|---|
| Alerts and incidents | Hours-old operations detail. The CIO sees the trend through the health cards. |
| Single servers, virtual machines or clusters | Not a CIO decision. |
| Cost line items, price | Capacity workspace (D-019); FinOps after 1.0 (D-027). |
| Attack and breach data | Security after 1.0 (D-044). |
| Mobile layout | Desktop first. A weekly email summary is a better mobile answer, after 1.0. |

## 6. Settled questions

- Public-cloud comparison: owned by FinOps, maintained as an input to PCM in 1.0 (D-058).
- Recovery card: site recovery test results only, labelled so that backup is not implied (D-059).
