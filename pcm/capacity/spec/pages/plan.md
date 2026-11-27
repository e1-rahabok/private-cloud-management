---
page: /capacity/plan
question: "What do we buy in the next round, and what does it cost?"
role: capacity
cadence: [monthly]
vocabulary: pcm/capacity/spec/vocabulary.yaml
design: pcm/capacity/design-note.md
decisions: [D-055, D-060, D-061]
---

# Capacity: purchase plan

## Next round

```yaml
question: "What do we buy in the next round, and what does it cost?"
role: capacity
cadence: [monthly]
reads: [capacity.purchase_plan]
api: /api/capacity/plan
```

- **The round's closing date.**
- **One row per group in the round:**
  - resource;
  - hosts;
  - delivery;
  - covered until;
  - cost lines (server, VCF licence per core over the depreciation period, support);
  - total;
  - "On time" or "Too late: the order arrives after the group runs out".
- **The round total.**
- **For IT Finance, as a document** (D-055).
- **The money is cost, never price** (D-027).
- **States:** normal, empty ("No group needs this round."), loading, error.
