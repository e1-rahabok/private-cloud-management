---
page: /l2/escalations
question: "What did L1 hand over, and is it complete?"
role: l2
cadence: [live]
vocabulary: catalog/vocabulary/l2.yaml
design: design/l2-workspace.md
decisions: [D-040, D-050, D-076]
---

# L2 escalations

## Escalations

```yaml
question: "What did L1 hand over, and is it complete?"
role: l2
cadence: [live]
reads: [noc.escalation_evidence, l2.escalation_close]
api: /api/l2/escalations
```

- **One block per escalated incident.** It shows the evidence PCM attached:
  - the SOP steps and their results;
  - the villains and the victims, with their raw "on my court" values (L2 sees counters; L1 did not);
  - what L1 already did.
- **Agent E2: "Draft the root cause analysis."** The draft is checked against the L2 vocabulary and recorded (D-076).
- **Close needs four fields.** Without all four, it is refused (L2 design, 3.8):
  - root cause;
  - corrective action;
  - detection, one of: new check rule, new alert, new SOP, SOP updated, none with a reason;
  - detection note.
- **States:** normal, empty ("Nothing escalated to you."), loading, error.
