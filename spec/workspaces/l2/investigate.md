---
page: /l2/investigate/{object}
question: "Why is it slow, in the SP5 order?"
role: l2
cadence: [live]
vocabulary: catalog/vocabulary/l2.yaml
design: design/l2-workspace.md
decisions: [D-038]
---

# L2 investigation

## Checks in order

```yaml
question: "Why is it slow, in the SP5 order?"
role: l2
cadence: [live]
reads: [l2.investigation_order, l2.realms]
api: /api/l2/investigate/{object}
```

- **Parent first:** whether the cluster and the host serve their VMs well, so L2 clears the infrastructure first (L2 design, 3.3).
- **The steps, in the fixed slow order:** contention, consumption, configuration, known bug, log.
  - Each step has its values and a pass or fail.
  - The first failing step is highlighted.
- **VM and Guest OS side by side,** each with its own values and verdict (L2 design, 3.5).
  - When the VM is fine and the Guest OS is not, the page says: "The cause is inside the Guest OS. Hand this evidence to the Windows or Linux team."
- **Log events of the same object and window,** beside the metrics (L2 design, 3.13).
- **"Ask Agent E2 why"** (D-078): PCM sends the question, the investigation facts on this page and the role to the Agent E2 service. The answer shows with the knowledge files it read, so L2 can open the source. If the service is not running, the page says "The Agent E2 service is not available" and shows no answer.
- **States:** normal, unknown object ("No such object"), stale, loading, error.
