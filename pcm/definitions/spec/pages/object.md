---
page: /docs/{kind}/{id}
question: "What exactly does this mean, who owns it, and what would a change touch?"
role: all
cadence: [on_demand]
vocabulary: pcm/definitions/spec/vocabulary.yaml
design: pcm/definitions/design-note.md
decisions: [D-050, D-063, D-080, D-082]
---

# Docs: one object

## Definition

```yaml
question: "What exactly does this mean?"
role: all
cadence: [on_demand]
reads: []
api: /api/docs/{kind}/{id}
```

- **Per kind:**
  - measure: description, formula, unit, status rule, notes, and "shown as" where a workspace uses a plain label (2.6);
  - SOP: what starts it, each step with its kind, the actions it allows and who may press them;
  - action policy: tier, guardrails, the record as evidence;
  - threshold: the measure, operator and value;
  - standard: what it applies to, the value, why;
  - setting: the default, unit, and where the default comes from.
- **Version, owner, status** (proposal or confirmed).
- **Where it is changed:** a link to the workspace page that owns the change (2.2). None when nothing in PCM changes it.
- **No decision ID in page text** (builder rule 9).
- **States:** normal, unknown object ("No such object"), loading, error.

## Used on

```yaml
question: "Who sees a different number if this changes?"
role: all
cadence: [on_demand]
reads: []
```

- **Every page section that reads the object,** with its question, role and cadence, computed from the page specifications (2.3). A threshold lists the sections that read its measure.
- **States:** normal, empty ("No page reads this directly."), loading, error.

## History

```yaml
question: "Who changed it, when and why?"
role: all
cadence: [on_demand]
reads: []
```

- **From the action record** (2.4): time, who, what before and after, reason. Newest first.
- **States:** normal, empty ("No change recorded."), loading, error.
