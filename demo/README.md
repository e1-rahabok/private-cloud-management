# PCM demo script

One story across every workspace, about 15 minutes. It shows that PCM is one system with one set of numbers, not five dashboards.

**The story:** a Bronze batch VM lands in a Silver cluster in Frankfurt. The NOC sees it in seconds, follows the SOP, and escalates. L2 finds the cause and closes the loop with a new check rule. Capacity sees the same cluster as "full now". Docs shows exactly which number decided it. The CIO page tells the board the same thing in plain words.

**Before every demo, rehearse it.** The rehearsal clicks through every step below in a browser and checks that each screen still says what this script says. It also writes a screenshot per step to `demo/screens/`, which doubles as a handout. It needs Node and Playwright with Chromium, like the page tests.

```bash
node demo/rehearse.mjs
```

## Setup (before the audience arrives)

1. Start PCM on a database of its own, so the demo always starts clean.

```bash
PCM_DEMO_SWITCHER=1 PCM_DB=var/demo.sqlite python3 -m build.pcm_proto.server --port 8080
```

   `PCM_DEMO_SWITCHER=1` adds a thin role switcher at the top of every page: a drop-down in demo order, with one or two lines on what the role does. It only jumps between the six URLs below and keeps the clock. It is demo scaffolding; production is one URL per person. Leave it off for the page tests (the wall must have no interactive element).

2. Reset the demo state: everything people did in the last run is removed.

```bash
curl -s -X POST "http://localhost:8080/api/noc/_reset" -d '{}'
```

3. Open these tabs, in order. Every URL fixes the clock at `2026-10-19T10:05:00+08:00`, Monday morning in Singapore, so every story is on screen.

| Tab | URL |
|---|---|
| 1 | `http://localhost:8080/exec?now=2026-10-19T10:05:00%2B08:00` |
| 2 | `http://localhost:8080/noc/wall?now=2026-10-19T10:05:00%2B08:00&rotate=8` |
| 3 | `http://localhost:8080/noc/alert/inc-fr-s-02?now=2026-10-19T10:05:00%2B08:00` |
| 4 | `http://localhost:8080/l2/escalations?now=2026-10-19T10:05:00%2B08:00` |
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
- The strip: two red screens, "What changed?" and "Is it fast?". They are pinned, so the wall keeps coming back to them.
- On "Is it fast?": FR-S-02 at 22 out of 100, "was 94 an hour ago". The wall shows the change, not only the state.

**Say:** "The five-second test. Anyone walking into the NOC knows what is wrong, and nobody touches the screen."

**Why it matters:** the wall answers the same five questions every time, in the same order. Green is quiet.

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

### 4. L2 closes the loop (3 minutes) — tab 4

**Refresh the tab.** The escalation is there.

**Point at:** it arrived with raw counters: CPU Ready on the victims, the villain fr-bat-017.

**Click:** "Draft the root cause analysis". Agent E2 drafts; L2 decides.

**Fill the Close form:**
- Root cause: `Bronze batch VM placed in a Silver cluster`
- Corrective action: `Move fr-bat-017 to FR-B-02`
- Detection: `New check rule`
- Detection note: `Daily check flags class mismatch on placement`

**Click:** "Close escalation".

**Say:** "An escalation closes only with a detection decision. The next time, a check finds it before anyone complains."

**Then open** `/l2/monthly` (same clock): under Repeated escalations, "Bronze VM placed in a Silver cluster" now says **Loop closed**, with the new check rule. It was "Still open" a minute ago.

**Why it matters:** L2 is measured by fewer repeats, not faster closures. The monthly review shows it on the day it happens.

### 5. Policy as code (2 minutes) — `/l2`

**Point at:** the Action policies section. There is no "Make automatic" button.

**Click:** "Propose a policy change" on "Move VMs between clusters". Choose tier **automatic**, then **Replay**.

**Point at:** the replay: of the last 23 moves, 18 would have run automatically; 3 were stopped by the 10-VM limit, 1 by the class rule, 1 by the close week.

**Type a reason, then click:** "Publish".

**Point at:** "Published v2", and the waiting move in SG-S-04 that ran automatically under it. No one approved it.

**Say:** "Nobody approves an automatic action. If an approval can be automated, it was never needed. Guardrails make it safe; the policy owner and version are accountable."

**Why it matters:** no approval logs nobody reads. The record stays, as evidence.

### 6. Capacity (2 minutes) — tab 5

**Point at:** "FR-Silver: decision 130 days earlier, now 7 Jan 2027, because of dr-ocp-wave-2 (Migration, OpenShift)". The change is the news; the cause is named.

**Click:** "Cluster groups".

**Point at:** FR-Silver says **Full now: VMs waiting on FR-S-02 (score 22)**. The same cluster, the same score as the NOC wall.

**Say:** "A forecast that says thirteen months left is wrong if VMs are waiting today. Contention overrides the forecast."

**Click:** "Waste". Reclaiming idle and oversized VMs in SG-Silver moves it out of the next purchase round: **cost avoidance $3,588,000**. The CIO page shows the same number, rounded: "Could still avoid in the next purchase round: $3.6M" (Value, Cost, See detail).

**Why it matters:** one engine, one date, one cost, read by every workspace.

### 7. Docs (1 minute) — tab 6

**Point at:**
- The threshold "Cluster Performance below 50" and who owns it.
- **Used on:** the NOC wall, the NOC incident page, and Capacity's cluster groups. Computed from the page specifications, not written by hand.

**Then open** `/docs/policy/move_vms_between_clusters`: version 2, owner and tier, and **History** with the publish you did five minutes ago, from the action record.

**Say:** "Every number on every page is one click from its definition, its owner, and who changed it and why."

**Why it matters:** an auditor's question answered without a meeting.

## Close (1 minute)

- **What is real in this demo:** every screen, every rule, every calculation, the database, the action record, Agent E2.
- **What is synthetic:** ACME's data. A bank with five locations, about 1,200 hosts. Stories are planted so every screen has something to show.
- **What is still planted, not computed:** class performance scores, the L2 weekly and monthly measures, repeated escalations and goal history. Next build replaces them with computed values.
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
| The escalation is not on tab 4 | Refresh tab 4. If still missing, the Escalate click in step 3 did not land: click it again on tab 3. |
| The wall does not rotate | Check the URL has `rotate=8`. |
| Agent E2 shows a fixed text | Expected without `AI_GATEWAY_API_KEY`. Say "this is the offline fallback". |
| Numbers differ from this script | The clock is missing: every URL needs `now=2026-10-19T10:05:00%2B08:00`. |
| A previous run's actions are on screen | Run the reset command in Setup, step 2. |
