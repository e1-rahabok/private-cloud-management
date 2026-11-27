---
page: /capacity/demand
question: "What demand is coming that the data cannot show?"
role: capacity
cadence: [weekly]
vocabulary: pcm/capacity/spec/vocabulary.yaml
design: pcm/capacity/design-note.md
decisions: [D-023, D-054]
---

# Capacity: demand register

## Register

```yaml
question: "What demand is coming that the data cannot show?"
role: capacity
cadence: [weekly]
reads: [capacity.forecast]
api: /api/capacity/demand
```

- **One row per entry:**
  - kind (project, migration, DR, growth of new VMs);
  - source;
  - cluster group;
  - date;
  - amounts (threads, GB, TB);
  - owner;
  - when it was added.
- **An Add form.** The forecast reads the entry at once.
- **States:** normal, empty ("Nothing registered. The forecast sees only the past."), loading, error.
