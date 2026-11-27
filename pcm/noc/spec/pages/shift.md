---
page: /noc/shift
question: "What do I hand over?"
role: l1
cadence: [live]
vocabulary: pcm/noc/spec/vocabulary.yaml
design: pcm/noc/design-note.md
decisions: [D-031, D-068, D-098]
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
- **Agent E2:** the top bar mark only (desktop.md, Agent E2 mark and panel). Suggestion: "What should the next shift know?". It drafts in the panel; the operator writes the note.
- **States:**
  - normal;
  - empty: "Nothing open";
  - loading;
  - error.
