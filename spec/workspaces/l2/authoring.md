---
page: /l2/authoring
question: "What should L1 and PCM do next time?"
role: l2
cadence: [weekly]
vocabulary: catalog/vocabulary/l2.yaml
design: design/l2-workspace.md
decisions: [D-045, D-070]
---

# L2 authoring: thresholds

## Threshold replay

```yaml
question: "How many alerts would this threshold have raised?"
role: l2
cadence: [weekly]
reads: [l2.threshold_replay]
api: /api/l2/thresholds/{id}/replay
```

- **One row per threshold:** current value and version.
- **Enter a new value, then "Replay":** the page shows the alerts the current value raised and the alerts the new value would have raised over the last 30 days, per day.
- **"Publish"** is enabled only after a replay. It increments the version and records the change (D-063).
- **SOP editing** comes in the next L2 build.
- **States:** normal, loading, error.
