---
page: /noc/alerts
question: "What urgent issue is waiting, grouped by cause?"
role: l1
cadence: [live]
vocabulary: pcm/noc/spec/vocabulary.yaml
design: pcm/noc/design-note.md
decisions: [D-040, D-069, D-098]
---

# NOC alerts

## Incident list

```yaml
question: "What urgent issue is waiting, grouped by cause?"
role: l1
cadence: [live]
reads: [noc.grouping_rule]
api: /api/noc/incidents
```

- **One row per incident:**
  - severity chip (red or orange);
  - root object and location;
  - title;
  - number of alerts grouped;
  - age;
  - state;
  - who acknowledged it.
- **Order:** red first, then orange. Oldest first within each.
- **Yellow never appears.** It is not an alert (NOC design, 3.4).
- **Agent E2 mark** on each row: "Ask Agent E2 about this incident" (desktop.md, Agent E2 mark and panel). The top bar mark asks about the list: "Which incident should I take first?".
- **States:**
  - normal;
  - empty: "No urgent issues";
  - loading;
  - error.
