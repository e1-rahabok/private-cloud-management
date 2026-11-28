---
page: /docs
question: "What does PCM own, and where is it defined?"
role: all
cadence: [on_demand]
vocabulary: pcm/docs_workspace/spec/vocabulary.yaml
design: pcm/docs_workspace/design-note.md
decisions: [D-024, D-070, D-082]
---

# Docs: index

Every object PCM owns and acts on, generated from the specification and the PCM database (Docs design, 2.1). Read-only (2.2).

## Objects

```yaml
question: "Where is this defined?"
role: all
cadence: [on_demand]
reads: []
api: /api/docs
```

- **Grouped by kind:** measures, SOPs, action policies, thresholds, configuration standards, settings. Each group with its count.
- **One row per object:** ID, title or one-line description, version, owner, and a "Proposal" chip where the owner has not confirmed it (2.5).
- **A search box** filters by ID or text, as the reader types.
- **The export line:** what PCM exports to private-cloud-explained, and how (2.7).
- **States:** normal, empty search ("Nothing matches."), loading, error.
