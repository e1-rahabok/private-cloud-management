---
page: /noc/alerts
question: "What urgent issue is waiting, grouped by cause?"
role: l1
cadence: [live]
vocabulary: catalog/vocabulary/noc.yaml
design: design/noc-workspace.md
decisions: [D-040, D-069]
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
- **States:**
  - normal;
  - empty: "No urgent issues";
  - loading;
  - error.
