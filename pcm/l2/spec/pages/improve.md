---
page: /l2/improve/{view}/{object}/{pillar}
question: "What should be better under this object, though nothing is broken?"
role: l2
cadence: [weekly, monthly]
vocabulary: pcm/l2/spec/vocabulary.yaml
design: pcm/l2/design-note.md
decisions: [D-027, D-029, D-043, D-079, D-083, D-097]
---

# L2 Improve

Risk and efficiency, not broken things (L2 design, 6). Framed in capacity, never in money (D-027).

## Opportunities

```yaml
question: "Which risks and opportunities sit under this object, largest first?"
role: l2
cadence: [weekly]
reads: [l2.opportunities, l2.findings]
api: /api/l2/improve/{view}/{object}/{pillar}
```

- **Summary tab:** one row per pillar with its count of opportunities and risks under the object.
- **Pillar tabs:** one row per opportunity, largest first: object, path, what, why, size (VMs, hosts, GB or threads), and its proposal if any.
  - **Capacity:** reclaim powered-off, idle and oversized VMs (with how far it moves the next purchase decision, read from the Capacity workspace); rebalance between clusters.
  - **Configuration:** see below.
  - **Availability:** restore and HA tests due.
  - **Performance:** placements that will contend (for example a VM wider than the NUMA node of some hosts in its cluster).
- **Agent E2 mark** on every row that comes from a finding, as in Monitor (frame.md, Agent E2 mark).
- **Proposed fix:** where an opportunity has one, Approve and Reject (reason required). An automatic policy run shows "Ran automatically under policy {type} v{n}, owner {owner}" and no approval.
- **States:** normal; empty ("Nothing to improve under this object."); loading; error.

## Configuration, by urgency

```yaml
question: "What is wrong, outdated, complex or wasteful?"
role: l2
cadence: [weekly]
reads: [l2.config_order]
api: /api/l2/configuration
```

- **Four groups in SP5 time order:** Correct it, Update it, Simplify it, Optimize it.
- **Each item:** object, setting, actual, standard with its version, and two choices: "Fix the setting" (creates a proposal) or "Fix the standard" (publishes a new standard version).
- **Only items under the selected object.**
- **States:** normal; empty per group ("Nothing to correct."); loading; error.

## Decision register

```yaml
question: "What did we decide, who owns it, and is it done?"
role: l2
cadence: [monthly]
reads: [l2.team_decision]
api: /api/l2/decisions
```

- **On the Summary tab at the estate root.** Every decision with owner, due date and state (overdue, open, done); overdue first.
- **Mark done** records who and when.
- **Record a decision:** what, owner, due date, all three required (D-043).
- **The monthly review is this register plus Monitor at the estate root with the 1-year window,** on one screen in the room. There is no separate monthly page.
- **States:** normal; empty ("No decision is open."); loading; error.
