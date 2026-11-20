# L2 workspace (Platform)

Status: draft for the author's review. Decisions proposed here move to [`decisions.md`](../decisions.md) once accepted.

Path: `privatecloud.acme.com/l2` (D-028).

## 1. The role

- SP5 calls this role **Platform**. It takes over when Level 1 cannot solve the problem.
- **What it does** (SP5 People):
  - Focuses on insight, not alerts. Looks at the big picture to stop alerts from happening.
  - Owns risk: configuration risk, and compliance risk after release 1.0 (D-022).
  - Advanced troubleshooting, often with logs.
  - Writes the knowledge base and the SOPs, and automates the SOPs.
  - After each problem it solves, updates the troubleshooting guide so L1 can handle the case next time.
  - Designs and maintains dashboards and alerts. It sets the thresholds L1 works with.
  - May specialize: vSAN, networking.
- **Cadence:**
  - daily check, 10 minutes, twice a day (D-039)
  - weekly check, 1 hour (D-042)
  - monthly review, 1 day
  - escalations at any time
  - mobile push for red alerts (D-031)
- **Scope:** VMware infrastructure (D-034), plus the Guest OS at OS level (D-038). Not applications.

**Why this role is the centre of PCM**
- L1 runs what L2 writes: SOPs, thresholds, actions.
- The Executive reads what L2 keeps healthy.
- If the L2 workspace is weak, every other workspace runs on stale rules.

## 2. What L2 is measured by

Everything in this workspace serves these outcomes. Each outcome is a number PCM can show.

| Outcome | Measure | Why it is the right measure |
|---|---|---|
| Fewer alerts | Alert count and intensity, trend over months | SP5: well-run operations have few alerts. Insight replaces most yellow alerts. |
| Fewer escalations of the same kind | Repeat escalations per problem type | Each solved problem should become an SOP that L1 can run. A repeat means the loop did not close. |
| Problems found before customers notice | Share of issues first found by a check, not by an alert or a complaint | This is the prevention window: the time between "we know" and "the customer knows". |
| Second time is fast | Time to diagnose a known problem | SP5: the first incident is forgivable once. The second is known within minutes. |

- What L2 is **not** measured by: tickets closed. SP5 aims to remove tickets, not to process them faster (why-a-new-framework).

## 3. Design considerations

### 3.1 The landing page is the check result, not the alert list

- **What:** `/l2` opens on the latest daily check: what needs a human, worst first.
- **Why:**
  - An alert is bottom up. One object crossed a threshold. It is the tip of the iceberg; many objects sit just below.
  - An alert list says nothing about the whole environment, and L2's job is the whole environment.
  - Opening on alerts trains L2 into reactive work. Opening on the check trains it into prevention.
  - Alerts are still one click away. They are a guard rail, not the starting point.

### 3.2 Three verdicts, never one health score

- **What:** the check result shows three separate verdicts.
  - **Present health:** is it up, is it fast, is it safe.
  - **Risk:** configuration, capacity trend, and compliance after 1.0.
  - **Efficiency:** waste.
- **Why:**
  - A single score drops on risk and waste too. It reads low while everything runs well, and soon nobody trusts it.
  - The three verdicts lead to different actions with different urgency:
    - present health means fix today;
    - risk means plan a change;
    - efficiency means reclaim when convenient.

  Mixing them hides which kind of work is waiting.

### 3.3 Top down, worst first, provider before consumer

- **What:** every list starts at the cluster, sorted by its worst KPI. From a failing cluster, PCM goes to its hosts, then to its VMs.
  - When a single VM is investigated, PCM first shows whether its cluster and host are serving their VMs well.
- **Why:**
  - At 100,000 VMs, starting from a VM is a needle in a haystack. A parent's verdict tells where to look next.
  - "Clear the infrastructure first." If the cluster fails most of its VMs, troubleshooting one VM wastes hours.
  - Cluster and host health is judged from their VMs (worst VM and 90th percentile), never from cluster averages. An average hides the victim.

### 3.4 One fixed order of checks, the what before the why

- **What:** the investigation view always follows the SP5 order.
  - **Down:** log → saturation → configuration → known bug.
  - **Slow:** contention → consumption → configuration → known bug → log.
  - Configuration and known bugs sit inside each pillar, not after it.
- **Why:**
  - Experts under pressure skip steps. The classic skip is jumping to "CPU is at 100%" when there is no contention: that is a busy VM, not a slow one.
  - A fixed order makes two engineers reach the same conclusion. It also lets PCM pre-run the steps and show which ones pass, so L2 starts at the first failed step.
  - The same order appears in L1's SOPs, in the daily check and in troubleshooting. One mental model across the team.

### 3.5 The VM and the Guest OS are separate, with evidence for each side

- **What:** investigation pages show VM health and Guest OS health side by side, as two objects. Each has its "on my court" evidence:
  - VM: CPU Ready, Co-stop, Overlap, Other Wait; memory latency, swapped, ballooned; disk latency; vMotion stun time.
  - Guest OS: run queue, context switches, paging.
- **Why:**
  - "A day in the life of a cloud admin" (SP5 source): the application team proves the Guest OS is fine and blames the shared platform. Without evidence on both sides, the argument is about reputation, not data.
  - With both sides shown, the conversation takes minutes:
    - The VM is not waiting → the cause is inside Windows or Linux, and the evidence goes to the OS team.
    - The VM is waiting → it is the platform's problem, and L2 owns it.

### 3.6 Business context is an input, not a memory

- **What:** L2 records the expected events: month-end batch, a planned migration, a retail peak, a DR test, a maintenance window. PCM reads them when it judges what is abnormal.
- **Why:**
  - SP5: an insight is useless to someone who does not know the environment. Anomaly detection by mathematics alone gives false positives, because it has no business context.
  - Today this context lives in one senior engineer's head. That fails SP5's acid test: the lead takes a long holiday and nobody calls them.
  - Written down, the context serves:
    - the daily check, which knows that low IOPS on a sale day is bad;
    - Agent E2, which explains a finding with today's context;
    - the next engineer on shift.

### 3.7 Policy as code decides what runs automatically (D-079)

- **What:**
  - The daily and weekly checks come with proposed fixes.
  - Each action type has a **policy** in the catalog: its tier (automatic, approval, never), its guardrails, its version and its owner.
  - A fix whose action type is automatic, and that passes every guardrail, runs. A fix that breaks a guardrail becomes a proposal for L2, with the guardrail named.
  - PCM keeps a record per action type: approvals, rejections, rollbacks. It is evidence for L2, never a gate.
  - **"Propose a policy change":** L2 edits a tier and guardrails. PCM replays the change against recent history, then L2 publishes it as a new version.
- **Why:**
  - Automatic approval is a contradiction. If an approval can be automated, it is not needed; remove it from the policy.
  - Guardrails make automation safe: blast radius, time windows, class of service, expiry and undo, a scoped service account. A count of past clicks does not.
  - Replay before publish shows what the change would have done, as threshold replay does (3.9).
  - A rejection with a reason is still data. It tells L2 which rule or guardrail is wrong.
  - *This replaces the first version of 3.7, a trust ladder in which an action type "earned" automation by its approval count (D-079).*

### 3.8 Escalations arrive complete, and the loop closes

- **What:**
  - An L1 escalation arrives with its evidence already gathered (D-040).
  - L2 accepts it or rejects it with a reason. Rejection should be rare, because PCM fills the evidence.
  - An escalation closes only with:
    1. a root cause;
    2. a corrective action that prevents a repeat;
    3. a decision on detection: a new check step, a new alert, or a new SOP so L1 can handle it next time.
- **Why:**
  - SP5: an RCA is done when the alert that detects a recurrence is set up, not when the cause is named.
  - L2 then becomes measurably less needed for known problems (section 2). Without this rule, L2 solves the same problem every month.
  - An L1 escalation that L2 rejects for missing evidence points to a gap in the SOP. It is fed back into SOP authoring.

### 3.9 L2 authors what L1 runs: SOPs, thresholds, actions

- **What:**
  - L2 writes and edits SOPs (in `/docs`), check rules, thresholds and the SOP buttons L1 may press.
  - Agent E2 drafts an SOP from a closed RCA. L2 reviews and publishes it. The NOC sees the new SOP at once.
  - Every published change is versioned.
- **Why:**
  - SP5 People: L2 develops and automates the SOPs, and sets the thresholds L1 uses.
  - Documentation and action in one place (D-024). The SOP that L1 reads is the same object that drives L1's buttons, so they cannot drift apart.
  - Any threshold change is tested against the last 30 days first. PCM shows how many alerts the new value would have raised.
    - Reason: alert storms come from thresholds set conservatively and never measured. If a threshold cannot be shown to be rare, it should not ship.

### 3.10 Configuration is reviewed by urgency, against a standard

- **What:** the configuration page orders findings by the SP5 time dimension:
  1. **Correct it:** wrong, insecure, against the standard.
  2. **Update it:** old versions, oldest first, out of support first.
  3. **Simplify it:** variance and complexity.
  4. **Optimize it:** cost and capacity.

  Every finding offers two choices: fix the setting, or fix the standard.
- **Why:**
  - Thousands of settings exist. Grouping them by product feature hides urgency. Grouping by Day 2 impact shows it.
  - Drift means nothing without a documented standard. When reality differs, one of the two is wrong. Sometimes the standard is out of date. Offering "fix the standard" stops L2 from forcing a bad standard onto a good estate.
  - Default filter is the Gold class of service, so critical workloads come first in a large estate.

### 3.11 One workspace, with specialty lenses

- **What:** one L2 workspace. Storage and network specialists use lenses inside it (the default is platform), not separate workspaces.
- **Why:**
  - With vSAN and NSX, storage and network are software in the same stack. One incident often crosses all three.
  - Separate workspaces bring back the "ping-pong between teams" that SP5 calls the manual stage of maturity. Each team proves "it is not on my court" with a different screen.
  - One workspace means one evidence set, one timeline, one RCA.
  - The lens changes the default view, not the data. SP5's storage test: agree within 1 minute whether a problem is storage.
  - This follows D-011 (one workspace per role): storage and network specialists share the Platform role.

### 3.12 Time windows follow the job

| Job | Default window | Why |
|---|---|---|
| Troubleshooting | Last 8–24 hours, any point in the past | Older data rarely matters for a live problem. By the time someone looks, the problem may be gone, so going back to any point in time is a must. |
| Daily check | Next 12 hours, from 1 week of data | Prevent today's alerts. |
| Weekly check | 1 week, per-instance metrics | Patterns a day cannot show (D-042). |
| Monthly review | 1 year | Baselines, quarterly patterns, large problems. |

- Performance reads the **20-second peak** of each 5-minute interval, not the 5-minute average. A spike of a few seconds disappears in 300 seconds of average.

### 3.13 Logs beside metrics

- **What:** every investigation shows the log events of the same object and time window next to its metrics.
- **Why:**
  - Availability lives mostly in logs, not metrics.
  - The root cause is often a log message on another object that never became an alarm.
  - SP5 check before turning a log message into an alert: count how often it appears on healthy objects over a week. PCM runs this count when L2 proposes a log-based alert. A message seen 1,000 times in 5 days on healthy hosts is noise.

### 3.14 The monthly review is a team meeting (D-043)

- **What:** `/l2/monthly` is presented on one screen in the room as a live dashboard.
  - PCM prepares it in advance:
    - one-year baselines;
    - repeated escalations;
    - alerts that slipped through;
    - configuration risk progress;
    - the capacity outlook;
    - progress against the year's goals.
  - The meeting records decisions with owners and due dates.
  - Next month's pack opens with their status.
- **Why:**
  - It is the one day the whole team meets, so its time goes to judgement, not slide-making.
  - Goals held in PCM are measured from the same data every month. Goals in a slide deck are forgotten by March.
  - Decisions without owners come back unchanged next month.

### 3.15 A suspected breach goes to the security team (D-044)

- **What:** when a finding points to a breach, L2 secures the evidence and hands it over. PCM does not investigate the breach.
  - Evidence: the logs, the events, and the configuration at that point in time.
- **Why:**
  - SP5: a breach is a forensic investigation, not troubleshooting.
  - Evidence handling has its own rules. An L2 engineer who "just checks" can destroy the trail.

### 3.16 Agent E2: explains and drafts, never decides

- **Agent E2 may:**
  - explain a finding in the context of the knowledge base and today's business context;
  - suggest the next check step;
  - draft the RCA and the SOP;
  - answer "why" questions with sources.
- **Agent E2 may not:**
  - set a severity;
  - approve an action;
  - change an action policy;
  - close an escalation.
- **Accountability (D-050):** each Agent E2 task records two fields: Agent E2's ID and the human who ordered the task.
  - Agent E2 can never act beyond what that person may do.
  - For actions that run automatically, the second field is the policy owner and the policy version (D-050, D-079).
- **Why:**
  - A confident wrong answer from an LLM at L2 level spreads: it becomes an SOP that L1 runs at 03:00.
  - Grounding in the knowledge base plus a human approval keeps the knowledge correct.

### 3.17 Considerations from the weekly, monthly and inventory build

- **The weekly check shows only what a day cannot.**
  - Decision: no daily finding is repeated. The weekly page has three kinds of finding: slow drift, a peak hidden in an average, configuration drift.
  - Why: L2 also does architecture and engineering (D-046). An hour spent re-reading the daily findings is an hour lost. Repeating them also teaches people to skim.
  - **Slow drift:** a metric that moves the same way on at least 5 of 6 night-to-night steps, by at least 10% in total. One night of +1.4% is noise; seven in a row is a straight line to full. Example: a snapshot left by a backup job grows with every write until the datastore fills.
  - **Hidden in the average:** one vCPU or one virtual disk at its red line while the VM total is green. A VM-level alert never fires, because the average dilutes one instance by the number of instances. Examples:
    - one vCPU at 97% in an 8-vCPU VM averaging 14%: a single-threaded process, where more vCPUs will not help;
    - one log disk at 38 ms while the VM averages 4 ms.
  - The second example is also the alert that slipped through. The weekly check explains it and names the check rule that would have caught it. That closes the loop the daily check left open.
- **A weekly finding needs an owner and an action.**
  - Decision: "Assign" refuses either one alone. Unassigned findings sort first.
  - Why: D-042 says each finding goes to L2 with an owner and an action. A finding with only an owner gets read, not done.
- **The monthly pack opens with last month's decisions.**
  - Decision: the first section is the decision register with its states: overdue, open, done. Recording a decision needs what, an owner and a due date. Decisions are a table in the PCM database.
  - Why: a meeting that starts with new topics never checks the old ones. In the synthetic story, the overdue decision on backup snapshots is the cause of this week's slow drift. The room sees both on one screen.
- **Goals and the capacity outlook are read, not recomputed.**
  - Decision: the goal projection is the CIO page's number. The capacity outlook is the Capacity workspace's own: groups in the round, peak warnings, waste.
  - Why: two numbers for one goal end the meeting in an argument about which is right. L2 does not plan capacity (D-014).
- **A repeated escalation's loop closes only with a detection.**
  - Decision: a problem type shows "Loop closed" only when an RCA added a check rule or an SOP.
  - Why: the L2 measure is fewer repeats, not faster closures (L2 design, 2). Closing FR-S-02 with a new class-of-service check rule closes the class-mismatch loop on the monthly page at once.
- **Detailed inventory: explained changes are counted, unexplained ones are listed.**
  - Decision: each change is matched in a fixed order: the PCM action record, an approved change window, a VCF Automation request, DRS. Unmatched changes are listed one by one, production and Gold first. "This was expected" needs a reason.
  - Why: an estate of 1,200 hosts makes tens of thousands of changes a week, most of them DRS moves. A list of all of them is unreadable. The question L2 asks is "is it expected?", so the page answers it and shows only the exceptions.
  - The PCM action record comes first: PCM's own changes, including automatic policy runs, are never flagged as unexplained, and they show both identity fields (D-050).
  - Example: a CPU limit set directly in vCenter on a production Gold VM, outside any window. No request, no PCM action. This is the change that causes "slow" complaints weeks later.

## 4. Pages

| Path | Job | Main question |
|---|---|---|
| `/l2` | Daily check result | What needs me today? |
| `/l2/escalations` | Escalations from L1 | What did L1 hand over, and is it complete? |
| `/l2/investigate/{object}` | Troubleshooting | Why is it down or slow? |
| `/l2/weekly` | Weekly check result | What does a week show that a day did not? |
| `/l2/monthly` | Monthly review and team meeting (D-043) | How are we doing against this year's goals, and what do we decide for next month? |
| `/l2/configuration` | Configuration risk | What is wrong, outdated, complex or wasteful? |
| `/l2/inventory` | Detailed inventory and changes (D-020) | What changed, and is that expected? |
| `/l2/context` | Business calendar (3.6) | What is expected this week? |
| `/l2/authoring` | SOPs, check rules, thresholds, L1 actions, alerts | What should L1 and PCM do next time? |

- Nine pages, compared with five for NOC. L2's work is broader and deeper: the NOC answers one question in the present; L2 owns past, present and future.
- No capacity planning pages: that is the Capacity workspace (D-014).
- SP5 People: capacity "does not get involved in the day-to-day capacity". The reverse also holds: day-to-day capacity (a cluster that cannot serve its current demand) is a performance matter for L2, not a planning matter.

## 5. Open questions for the author

1. **Who owns PCM's own configuration** (class-of-service definitions, action tiers)?
   - Proposal: L2 proposes changes. The Operations Manager approves them after 1.0. Until then, L2 owns them.
