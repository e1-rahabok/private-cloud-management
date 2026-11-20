---
page: /noc/shift
question: "What do I hand over?"
role: l1
cadence: [live]
vocabulary: catalog/vocabulary/noc.yaml
design: design/noc-workspace.md
decisions: [D-031, D-068]
---

# NOC shift handover

## Handover

```yaml
question: "What do I hand over?"
role: l1
cadence: [live]
api: /api/noc/shift
```

- **The current shift and region** come from `noc.shift_times`. Times are shown in the viewer's zone.
- **Lists:**
  - incidents still open;
  - incidents acknowledged this shift, with who acknowledged them;
  - incidents waiting on L2;
  - limits that expire at the end of this shift.
- **A handover note box.** Saving it shows the note to the next shift.
- **States:**
  - normal;
  - empty: "Nothing open";
  - loading;
  - error.
