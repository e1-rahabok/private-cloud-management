---
page: /noc
question: "What does the wall show, and where exactly?"
role: l1
cadence: [live]
vocabulary: catalog/vocabulary/noc.yaml
design: design/noc-workspace.md
decisions: [D-032, D-041, D-052]
---

# NOC desktop: the five screens with drill-down

## The five screens

```yaml
question: "What does the wall show, and where exactly?"
role: l1
cadence: [live]
reads: [noc.screen_status]
api: /api/noc/wall
```

- **The same data and colours as the wall** (NOC design, 3.3), shown as five tabs. There is no rotation.
- **A tile in "Is it fast?" opens the cluster:**
  - top villains and victims, with their scores from 0 to 100;
  - their environment: production or non-production;
  - their class.
- **A red or amber tile links to its incident** on `/noc/alert/{id}`.
- **A navigation bar links** to Alerts and Shift. It does not link to other workspaces (D-011).
- **States:**
  - normal;
  - stale;
  - empty: "Nothing to show";
  - loading;
  - error.
