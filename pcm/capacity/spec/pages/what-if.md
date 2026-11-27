---
page: /capacity/what-if
question: "What happens if we add, remove or change something?"
role: capacity
cadence: [weekly, monthly]
vocabulary: pcm/capacity/spec/vocabulary.yaml
design: pcm/capacity/design-note.md
decisions: [D-061]
---

# Capacity: what-if

## Hardware refresh

```yaml
question: "Does replacing old hosts cover next year's growth?"
role: capacity
cadence: [monthly]
reads: [capacity.usable, capacity.forecast]
api: /api/capacity/what-if/refresh
```

- **Inputs:** location, previous-generation hosts to replace, current-standard hosts to buy.
- **Output, before and after:**
  - threads;
  - DRAM;
  - licensed cores;
  - next year's growth.
- **The sentence:** "Covers next year's growth" or "Does not cover next year's growth".
- **Licensed cores are always shown,** because VCF is licensed per core (D-061).

## Host specification

```yaml
question: "How many VMs of a class fit on a host, and how much DRAM should it have?"
role: capacity
cadence: [monthly]
reads: [capacity.planning_six_numbers]
api: /api/capacity/what-if/host
```

- **Inputs:** class; cores, base GHz and DRAM per host.
- **Output:** the six numbers (allocation, reservation and utilization, for CPU and memory), the one that binds, and the DRAM that matches the CPU (SP5 host specification).
- **States:** normal, loading, error.
