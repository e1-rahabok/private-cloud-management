---
page: /noc/alert/{id}
question: "What does the SOP say, and what may I do?"
role: l1
cadence: [live]
vocabulary: catalog/vocabulary/noc.yaml
design: design/noc-workspace.md
decisions: [D-029, D-040, D-050, D-063, D-069, D-098]
---

# NOC incident: the SOP is the page

## Incident and SOP

```yaml
question: "What does the SOP say, and what may I do?"
role: l1
cadence: [live]
reads: [noc.grouping_rule, noc.cluster_performance, noc.villains, noc.victims, noc.escalation_route]
api: /api/noc/incidents/{id}
```

- **Header:**
  - severity;
  - root object;
  - location;
  - state;
  - the alerts in the group;
  - an Acknowledge button.
- **SOP steps, in order (NOC design, 3.5):**
  - **Diagnosis:** shows the live check and a pass or fail mark. A step marked `branch` shows its answer instead (for example "production"), because it chooses the next step and is not a failure.
  - **Action:** a button.
    - It is enabled only when the step's `when` holds and the action is allowed for L1 on that target (D-040).
    - When disabled, it says why, for example "Production VM: escalate instead".
  - **Escalate:** a button. It shows the L2 group it goes to.
  - **Verify:** shows the live check after an action.
- **Close:**
  - A Close button with a required root cause list. Without a cause it cannot be pressed (D-040).
  - L1 can split an incident but cannot merge incidents (D-069). Splitting is out of the prototype.
- **Action history** for this incident, with both identity fields (D-050, D-063). Actions are named in plain words ("Stopped new VMs", "Acknowledged"), never by their ID.
- **Limits** show when they expire: at the end of the shift.
- **Agent E2 mark** on the title, "Ask Agent E2 about this incident", and on each SOP step, "Ask Agent E2 about this step" (desktop.md, Agent E2 mark and panel; D-098).
- **Agent E2 panel (D-076, D-098):** on an incident, its first two suggestions are "Explain this incident" and "Draft the escalation note"; on a step, "Why does the SOP ask this?" and "What does this result mean?". There is no Agent E2 section on the page.
  - Agent E2 gets the incident facts from the API: alerts, SOP steps and their results, villains and victims, the escalation route; for a step, which step was asked about.
  - It answers in plain words, marked "Draft by Agent E2, to review".
  - The draft is recorded in the action history with Agent E2's ID and the person who asked (D-050).
  - Its words are checked against the NOC vocabulary. If it uses an avoided word, it is asked once to rewrite. If it fails again, the page shows the fixed template.
  - If the model cannot be reached, the page shows the fixed template, labelled "Agent E2 is not available".
- **States:**
  - normal;
  - acknowledged;
  - escalated;
  - closed;
  - stale (diagnosis checks show "No data");
  - loading;
  - error.
