---
page: /l2/troubleshoot/case/{case}
question: "Why is it slow or down, layer by layer, and what caused it over the weeks before?"
role: l2
cadence: [live]
vocabulary: catalog/vocabulary/l2.yaml
design: design/l2-workspace.md
decisions: [D-038, D-044, D-076, D-078, D-084, D-085, D-089, D-097]
---

# L2 case

One case: its trigger, its chain of causes, the layers, one timeline, and the close (L2 design, 5). The window is the case's own and fixed.

## Case header

```yaml
question: "What started this case, about what, and over which window?"
role: l2
cadence: [live]
reads: [l2.case, l2.complaint, noc.escalation_evidence]
api: /api/l2/cases/{case}
```

- **Title, symptom, object with its path, trigger, opened by and when, window, state.**
- **What started it:**
  - complaint: who, through whom, since, fine until, and what they already checked;
  - escalation: the SOP steps L1 ran with their results, villains and victims with raw counters, what L1 already did, and Accept / Reject (reason required);
  - finding: the finding's summary and evidence, with a link back to it in Monitor.
- **Agent E2 mark** at the right of the title: "Ask Agent E2 about this case" (frame.md, Agent E2 mark; D-097).
- **States:** normal; unknown case ("No such case"); loading; error.

## Chain of causes

```yaml
question: "What caused what, and which ideas are ruled out?"
role: l2
cadence: [live]
reads: [l2.chain, l2.realms]
```

- **The symptom at the top.** Under it, each link: the cause, the object, the layer, the SP5 step and the Agent E2 flow that proposed it, its evidence, its kind (main or contributing) and its state.
  - Links are indented under the effect they explain, so A ← B ← C ← D reads top to bottom.
  - Several causes can sit under one effect: a main cause and a contributing cause.
  - **Agent E2 mark** on each link: "Ask Agent E2 about this link". PCM sends the case and the link.
- **States of a link:**
  - **proposed:** "Confirm" and "Rule out" buttons. Rule out asks for a reason, recorded with the link.
  - **confirmed:** the person who confirmed it.
  - **ruled out:** grey, kept visible, with the reason. Red herrings live here.
- **"Propose the next link"** (Agent E2, following its flows, D-089): adds the next proposed link with evidence. When the flows have nothing more to propose, the button says so: "Agent E2 has nothing more to propose from its flows."
- **VM and Guest OS side by side** (l2.realms) when the case object is a VM: each with its values and verdict. When the VM is fine and the Guest OS is not, the case says: "The cause is inside the Guest OS. Hand this evidence to the Windows or Linux team."
- **States:** normal; empty ("Nothing proposed yet. Ask Agent E2 to propose the first link."); loading; error.

## Layers

```yaml
question: "Which layer is on whose court?"
role: l2
cadence: [live]
reads: [l2.layers]
```

- **One row per layer:** Guest OS, VM, host, cluster, storage, network. Each: clear, waiting, or not read, with the values that decide it.
- **Agent E2 mark** on each row: "Ask Agent E2 about the {layer} layer". PCM sends the case and the layer.
- **Hand-over** (l2.layers hand_over): when the evidence points outside scope, the case names the team and says what was checked.
- **States:** normal; loading; error.

## Timeline

```yaml
question: "What happened to these objects over the weeks before?"
role: l2
cadence: [live]
reads: [l2.timeline, l2.change_explanation]
```

- **One time axis, newest last,** for every object in the chain: metric anomalies, events, log messages, changes with their explanation, calendar entries, alerts.
  - Each entry: time, object, kind, text. Changes show what explains them; an explained change can still be wrong (story T-2).
  - The case window is marked on the axis; entries before it show how far back they are.
- **States:** normal; empty ("Nothing recorded for these objects in the window."); loading; error.

## Who else

```yaml
question: "Who else shows the same symptom?"
role: l2
cadence: [live]
reads: [l2.who_else]
```

- **For the case's symptom:** other objects that share a cluster, datastore, host model, ESXi build or change, and show the same symptom, with a count and the first ten by name.
- **A pattern found here** can become a monitoring finding: "Add a check rule" opens Rules.
- **States:** normal; empty ("No other object shows this symptom."); loading; error.

## Ask Agent E2

```yaml
question: "Why, with sources?"
role: l2
cadence: [live]
reads: [l2.chain]
api: /api/l2/agent/ask
```

- **In the Agent E2 panel** (frame.md), not a section of the page. The marks on the header, the links and the layers open it with the case as context (D-097).
- PCM sends the question, the case facts (header, trigger evidence, chain with each link's state, layers, hand-over, timeline) and the role to the Agent E2 service (D-078). The answer shows with the knowledge files it read, behind the "Sources (n)" control (frame.md, D-099).
- If the service is not running, the panel says "The Agent E2 service is not available" and shows no answer.

## Close

```yaml
question: "Is the cause known, the repeat prevented, and the next one detected?"
role: l2
cadence: [live]
reads: [l2.case_close, l2.log_validation]
api: /api/l2/cases/{case}/close
```

- **Four fields, all required** (l2.case_close): root cause, corrective action, detection (new check rule, new alert, new SOP, SOP updated, none with a reason), detection note.
- **"Draft the root cause analysis"** (D-076), above the fields: Agent E2 drafts from the confirmed links. The draft shows above the fields, marked "Draft by Agent E2, to review"; it fills no field. Checked against the L2 vocabulary and recorded.
  - Root cause is prefilled from the confirmed main links; at least one main link must be confirmed.
  - Missing any field: refused, with the missing field named.
- **A log-based detection is validated first** (l2.log_validation): the count on healthy objects over 5 working days is shown; above the limit, PCM says it is noise.
- **After close:** the detection opens in Rules as a draft; for an escalation, the NOC incident closes with the same root cause.
- **A suspected breach** is not a case: "Hand to the security team" secures the logs, events and configuration of the window (D-044).
- **States:** normal; closed (the closure, by whom); error.
