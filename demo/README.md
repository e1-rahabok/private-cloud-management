# PCM demo script

One walk through every workspace, about 17 minutes. It shows that PCM is one system with one set of numbers, not five dashboards.

**What happens:** a Bronze batch VM lands in a Silver cluster in Frankfurt. The NOC sees it in seconds, follows the SOP, and escalates. L2 monitors the whole estate top down, troubleshoots the escalation as a case, and closes the loop with a new check rule. L2's Capacity tab shows the same cluster open at the daily check, with contention now. Docs shows exactly which number decided it. The CIO page tells the board the same thing in plain words.

**Before every demo, rehearse it.** The rehearsal clicks through every step below in a browser and checks that each screen still says what this script says. It also writes a screenshot per step to `demo/screens/`, which doubles as a handout. It needs Node and Playwright with Chromium, like the page tests.

```bash
node demo/rehearse.mjs
```

## Setup (before the audience arrives)

1. Start PCM on a database of its own, so the demo always starts clean.

```bash
PCM_DB=var/demo.sqlite python3 -m pcm.core.server --port 8080
```

   The server adds a thin red role switcher at the top of every page, labelled "Demo control · not part of PCM": a drop-down in demo order, with one or two lines on what the role does. It only jumps between the six URLs below and keeps the clock. It is demo scaffolding; production is one URL per person. It is on by default. Set `PCM_DEMO_SWITCHER=0` to turn it off; the page tests do, because the wall itself must have no interactive element (D-041). The switcher sits above the wall, outside it.

2. Reset the demo state: everything people did in the last run is removed.

```bash
curl -s -X POST "http://localhost:8080/api/noc/_reset" -d '{}'
```

3. Open these tabs, in order. Every URL fixes the clock at `2026-10-19T10:05:00+08:00`, Monday morning in Singapore, so every PCM scenario story is on screen.

| Tab | URL |
|---|---|
| 1 | `http://localhost:8080/exec?now=2026-10-19T10:05:00%2B08:00` |
| 2 | `http://localhost:8080/noc/wall?now=2026-10-19T10:05:00%2B08:00&rotate=8` |
| 3 | `http://localhost:8080/noc/alert/inc-fr-s-02?now=2026-10-19T10:05:00%2B08:00` |
| 4 | `http://localhost:8080/l2?now=2026-10-19T10:05:00%2B08:00` |
| 5 | `http://localhost:8080/capacity?now=2026-10-19T10:05:00%2B08:00` |
| 6 | `http://localhost:8080/docs/threshold/th-cluster-perf-red?now=2026-10-19T10:05:00%2B08:00` |

- Agent E2 drafts work without a key; they fall back to a fixed text. For live model drafts, set `AI_GATEWAY_API_KEY` before starting the server. Live drafts take 2 to 6 seconds.
- `rotate=8` makes the wall rotate every 8 seconds instead of 60, so the audience sees the rotation.

## The script

Each step: what to click, what to point at, and the one sentence to say. Say the sentence; the screen proves it.

### 1. The CIO page (2 minutes) — tab 1

**Click:** nothing at first.

**Point at:**
- The three questions: Is it up? Is it fast? Is it safe? Each with a status, not a score.
- "Is it safe?" is red: 72 virtual machines below the security target this month.
- Room to grow: Singapore must order by 18 Nov 2026, and it is "In the plan".

**Click:** "See detail" on "Is it fast?".

**Say:** "Performance is a score, not a contract. Gold scores above Silver, and Silver above Bronze, as we promised the business."

**Why it matters:** the CIO gets three plain answers and one date to act on. Every number has one definition, shared with the teams below.

### 2. The NOC wall (1 minute) — tab 2

**Point at:**
- The tabs: two screens have open incidents, Volatility and Performance. They are pinned, so the wall keeps coming back to them.
- On Performance: FR-S-02 at 22 out of 100, "was 94 an hour ago". The one-hour chart shows the lowest cluster falling while the average barely moves. The wall shows the change, not only the state.

**Say:** "The five-second test. The banner says whose cloud it is and how big. Anyone walking into the NOC knows what is wrong, and nobody touches the screen."

**Why it matters:** the wall shows the same six screens every time, in the same order. Green is quiet.

### 3. The NOC incident (3 minutes) — tab 3

**Point at:**
- The SOP is the page. Each step shows its result: the cluster score is below 50; the top VM using the most is fr-bat-017.
- "Limit fr-bat-017 until end of shift" is disabled: "Production VM: escalate instead". L1 may not limit production. The SOP knows it.

**Click:**
1. "Stop new VMs here" — PCM closes FR-S-02 to new VMs and records it.
2. "Explain this incident" — Agent E2 explains in L1's words.
3. "Escalate to Platform" — the incident goes to L2 with its evidence.

**Say:** "L1 did everything L1 is allowed to do, in two minutes, and handed over a complete case."

**Why it matters:** fewer people per shift, because the SOP, the allowed actions and the evidence are on one page.

### 4. L2 monitors the whole estate (2 minutes) — tab 4

**Point at:**
- The top bar: three activities, **Monitor, Troubleshoot, Improve**. Rules and Calendar sit apart. No page per day, week or month: those are the window.
- The tree on the left is the inventory, and the menu. Europe is red.
- Summary: one row per pillar, never one score. The findings say where each goes: "Troubleshoot this" for a problem, "Improve this" for a risk.

**Click:** Europe › London in the tree, then **Performance**, then **7 days**, then **Group by: Host model**.

**Point at:** 9 VMs wider than their host's NUMA node, all on Gen-2019 hosts; none on Gen-2024. 3,000 VMs read at once.

**Say:** "An alert is the tip of the iceberg. Monitoring reads every VM, top down, and finds what objects share."

**Why it matters:** a pattern across the estate is found before it spreads. No alert would show it.

### 5. L2 troubleshoots the escalation as a case (3 minutes) — tab 4

**Click:** **Troubleshoot** in the top bar. The NOC's escalation is a case, beside a Tokyo escalation and a complaint.

**Open** the Frankfurt case. **Point at:** it arrived with raw counters: CPU Ready on the victims, the villain fr-bat-017.

**Click:**
1. "Accept".
2. "Propose the next link", four times. Agent E2 follows its flows; each link names the flow and the evidence.
3. Confirm the wait, the villain and the class mismatch. Rule out "the cluster is short of hosts", with a reason: it ran at 94 an hour ago.
4. "Draft the root cause analysis". Agent E2 drafts; L2 decides.

**Fill the Close form** (the root cause is prefilled from the deepest confirmed link):
- Corrective action: `Move fr-bat-017 to FR-B-02`
- Detection: `New check rule`
- Detection note: `Daily check flags class mismatch on placement`

**Click:** "Close the case".

**Say:** "A case closes only with a detection decision. The next time, a check finds it before anyone complains."

**Then open** Monitor, estate, **1 year**: under Repeated problems, "Bronze VM placed in a Silver cluster" now says **Loop closed**. It was "Still open" a minute ago.

**Optional, 3 minutes — a complaint several layers deep:** Troubleshoot › "Log complaint" for `sg-gl-db-01` (the general ledger is slow). Propose the links one by one: Windows is ruled out, then disk latency, a snapshot chain, the backup job that left it in the weekend change window, and a NUMA split that contributes. "Add 8 vCPUs" and "add a ninth host" are ruled out with evidence. The timeline reaches back 40 days.

**Why it matters:** L2 is measured by fewer repeats, not faster closures. Escalation is one way a case starts; a complaint and a monitoring finding are the others.

### 6. Policy as code (2 minutes) — Rules

**Click:** **Rules** in the top bar. **Point at:** the Action policies section. There is no "Make automatic" button.

**Click:** "Propose a policy change" on "Move VMs between clusters". Choose tier **automatic**, then **Replay**.

**Point at:** the replay: of the last 23 moves, 18 would have run automatically; 3 were stopped by the 10-VM limit, 1 by the class rule, 1 by the close week.

**Type a reason, then click:** "Publish".

**Point at:** "Published v2", and the waiting move in SG-S-04 that ran automatically under it. No one approved it. Improve shows it as "Ran automatically".

**Say:** "Nobody approves an automatic action. If an approval can be automated, it was never needed. Guardrails make it safe; the policy owner and version are accountable."

**Why it matters:** no approval logs nobody reads. The record stays, as evidence.

### 7. Capacity (2 minutes) — tab 5

**Point at:** "FR-Silver: decision 130 days earlier, now 7 Jan 2027, because of dr-ocp-wave-2 (Migration, OpenShift)". The change is the news; the cause is named.

**Click:** "Cluster groups".

**Point at:** LD-Bronze says **Closed for new VMs: LD-B-01**. The same verdict as L2's Capacity tab, read from the daily check.

**Say:** "A forecast that says months left is wrong if the cluster cannot take a new VM today. The check overrides the forecast. Placement already sends new VMs elsewhere."

**Click:** "Waste". Reclaiming idle and oversized VMs in SG-Silver moves it out of the next purchase round: **cost avoidance $3,588,000**. The CIO page shows the same number, rounded: "Could still avoid in the next purchase round: $3.6M" (Value, Cost, See detail).

**Why it matters:** one engine, one date, one cost, read by every workspace.

### 8. Docs (1 minute) — tab 6

**Point at:**
- The threshold "Cluster Performance below 50" and who owns it.
- **Used on:** the NOC wall, the NOC incident page, and L2's Capacity tab ("Contention now"). Not the Capacity workspace: it reads the daily check, never the last hour. Computed from the page specifications, not written by hand.

**Then open** `/docs/policy/move_vms_between_clusters`: version 2, owner and tier, and **History** with the publish you did five minutes ago, from the action record.

**Say:** "Every number on every page is one click from its definition, its owner, and who changed it and why."

**Why it matters:** an auditor's question answered without a meeting.

## Close (1 minute)

- **What is real in this demo:** every screen, every rule, every calculation, the database, the action record, Agent E2.
- **What is synthetic:** ACME's data. A bank with five locations, about 1,200 hosts. PCM scenario stories are planted so every screen has something to show.
- **What is still planted, not computed:** class performance scores, the L2 twelve-month measures, repeated problems and goal history, and the chains Agent E2 proposes for the planted PCM scenario stories (its flow executor is not called yet). Next build replaces them with computed values.
- **Next:** connect to a live VCF Operations and check every API assumption.

## Questions the audience asks

| Question | Answer |
|---|---|
| Does it replace VCF Operations? | It replaces its user interface for operations roles. VCF Operations stays as the data source and its collectors. |
| Where does the data go? | Nowhere. PCM runs on premises; no request leaves the PCM host. Agent E2 runs on a local model at a customer site. |
| Can it act on my estate? | Only through action policies: a tier, guardrails, a service account per action type, and an undo. Every action is recorded. |
| Why not one health score? | One score hides which question failed. The CIO needs to know whether it is up, fast or safe, and each has its own owner. |
| What does the date on the CIO page mean? | The last day to order hardware so it arrives before the tightest cluster group runs out, after the purchase lead time. |

## If something goes wrong

| Symptom | Fix |
|---|---|
| The Frankfurt case is not in Troubleshoot | Refresh. If still missing, the Escalate click in step 3 did not land: click it again on tab 3. |
| The wall does not rotate | Check the URL has `rotate=8`. |
| Agent E2 shows a fixed text | Expected without `AI_GATEWAY_API_KEY`. Say "this is the offline fallback". |
| The E2 mark is grey; the panel says "The Agent E2 service is not available." | The Agent E2 service is not running next to PCM. Start it: `deploy/README.md`, section Agent E2. |
| The panel says "Agent E2 is running, but its model cannot be reached." | The service is up; its key or its route to the gateway is not. Check `AI_GATEWAY_API_KEY`, then restart `agent-e2`. |
| Numbers differ from this script | The clock is missing: every URL needs `now=2026-10-19T10:05:00%2B08:00`. |
| A previous run's actions are on screen | Run the reset command in Setup, step 2. |
