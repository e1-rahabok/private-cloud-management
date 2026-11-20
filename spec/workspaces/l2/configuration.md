---
page: /l2/configuration
question: "What is wrong, outdated, complex or wasteful?"
role: l2
cadence: [daily, weekly]
vocabulary: catalog/vocabulary/l2.yaml
design: design/l2-workspace.md
decisions: [D-029]
---

# L2 configuration

## Findings by urgency

```yaml
question: "What is wrong, outdated, complex or wasteful?"
role: l2
cadence: [daily, weekly]
reads: [l2.config_order]
api: /api/l2/configuration
```

- **Four groups, in SP5 order:** Correct it, Update it, Simplify it, Optimize it.
- **Each finding:**
  - the object;
  - the setting;
  - actual against standard;
  - two buttons, "Fix the setting" and "Fix the standard" (L2 design, 3.10).
- **"Fix the setting"** creates a proposal that waits for approval. **"Fix the standard"** records a new standard version.
- **The default filter is Gold.**
- **States:** normal, empty per group ("Nothing to correct."), loading, error.
