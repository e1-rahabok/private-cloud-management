---
page: /l2/rules
question: "What do L1 and PCM run, and is each rule shown to be rare before it ships?"
role: l2
cadence: [weekly]
vocabulary: pcm/l2/spec/vocabulary.yaml
design: pcm/l2/design-note.md
decisions: [D-029, D-045, D-050, D-079, D-082]
---

# L2 Rules

A utility, not an activity. L2 authors what L1 and PCM run (L2 design, 7.1). SOPs themselves are documented in `/docs` (D-082); they are edited here.

## Detections from closed cases

```yaml
question: "Which detections did closed cases ask for?"
role: l2
cadence: [weekly]
reads: [l2.case_close]
api: /api/l2/rules/drafts
```

- **One row per closed case whose detection is not "none":** case, detection kind, note, closed by, and its state (draft, published).
- **States:** normal; empty ("No detection waits."); loading; error.

## Thresholds

```yaml
question: "How many alerts would this value have raised?"
role: l2
cadence: [weekly]
reads: [l2.threshold_replay]
api: /api/l2/thresholds
```

- **One row per threshold L2 owns:** metric, operator, value, version.
- **Replay** a new value over the last `l2.replay_days` days: alerts per day at the current value and at the new one. **Publish** is enabled only after a replay. The version increments.
- **States:** normal; loading; error.

## Action policies

```yaml
question: "What runs automatically, and within which guardrails?"
role: l2
cadence: [weekly]
reads: [l2.action_policy, l2.action_record, l2.policy_replay]
api: /api/l2/policies
```

- **One row per action type:** tier; guardrails in plain words; version and owner; the record as evidence (approvals, rejections, rollbacks).
- **The record is evidence, never a gate.** No button turns it into automation (D-079).
- **"Propose a policy change":** tier and guardrails. **Replay** shows how many past runs would have run automatically and how many each guardrail would have stopped. **Publish** needs a replay and a reason; the new version is recorded with its owner.
- **An automatic run shows its accountable party** as "policy {type} v{n}, owner {name}" (D-050).
- **States:** normal; loading; error.
