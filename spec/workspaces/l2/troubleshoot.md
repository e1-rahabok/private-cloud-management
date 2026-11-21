---
page: /l2/troubleshoot/{view}/{object}
question: "Which problems are open under this object, and who started them?"
role: l2
cadence: [live]
vocabulary: catalog/vocabulary/l2.yaml
design: design/l2-workspace.md
decisions: [D-040, D-084, D-085]
---

# L2 Troubleshoot: cases

Every troubleshooting effort is a case. Escalation is one of three triggers, not the activity (D-084).

## Cases

```yaml
question: "Which cases are open under this object, and who started each?"
role: l2
cadence: [live]
reads: [l2.case, noc.escalation_evidence]
api: /api/l2/cases
```

- **One row per case under the selected object** (the estate shows every case): open first, then closed, newest first.
- **Each row:**
  - the trigger: Complaint, Escalation from L1, or Monitoring finding;
  - the object and its path;
  - the symptom (slow or down) and the title;
  - age;
  - the chain so far: how many links are confirmed, proposed and ruled out;
  - state.
- **An escalation from L1 appears as a case** as soon as the NOC escalates it, with its evidence attached (D-040). L2 accepts it, or rejects it with a reason; a rejection is a gap in the SOP and is recorded.
- **"Log complaint"** button, top right.
- **States:** normal; empty ("No open case under this object."); loading; error.

## Log complaint

```yaml
question: "Who complained about which VM, since when, and what have they checked?"
role: l2
cadence: [live]
reads: [l2.complaint]
api: /api/l2/cases
```

- **Path:** `/l2/troubleshoot/new`, prefilled with the selected VM if a VM or Guest OS is selected.
- **Fields** (l2.complaint):
  - VM, required: searched by name, in any view. A complaint about an application is logged against its VMs.
  - Who complained, required. Through whom (for example their manager), optional.
  - Symptom, required: slow or down.
  - Since, required. Fine until, optional.
  - What they already checked, optional, one line each.
- **Save** opens the case page. The case window runs from "fine until" (or one hour before "since") to now.
- **No application or transaction field** (D-085).
- **States:** normal; error with the missing field named.
