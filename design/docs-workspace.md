# Docs workspace (`/docs`)

The reference for what PCM owns and acts on (D-082). Documentation for colleagues (architecture, decisions, user guides, team structure, learning) is private-cloud-explained, a separate product.

## 1. The readers

| Reader | Comes to `/docs` to | Usually from |
|---|---|---|
| L1 (NOC) | Read an SOP before or after running it; learn what a wall number means | A link on the NOC page |
| L2 (Platform) | Check a definition before changing a threshold or policy; see what a change would touch | The L2 authoring pages |
| Capacity | Check how usable capacity, run-out and the six host numbers are computed | A link on a Capacity page |
| CIO office | Answer "what does this number mean, exactly?" for an auditor or a board paper | A link on the Executive page |
| Auditor | See who owns a rule, its version, and when and why it changed | A link sent by L2 |

- `/docs` is one workspace for every role, because a definition is the same for all of them. Each role keeps its own workspace for work (D-011); `/docs` is where they meet on meaning.

## 2. Design considerations

### 2.1 The object is the documentation

- **What:** each page is generated from the object PCM runs: the catalog entry, the SOP, the policy, the threshold, the setting. No page is written by hand.
- **Why:** an SOP that L1 reads and an SOP that drives L1's buttons must be one thing (L2 design, 3.9). A hand-written copy is correct on the day it is written and wrong after the next change.

### 2.2 Read-only

- **What:** `/docs` changes nothing. Each object links to the workspace page where it is changed.
- **Why:** every change already has one path with a replay and a record. L2 replays a threshold before publishing it; L2 replays a policy against history. A second edit path would skip both.

### 2.3 "Used on": what a change would touch

- **What:** each object lists the pages and sections that read it, with their role and cadence. The list is computed from the page specifications (`reads:`), not maintained by hand.
- **Why:** the question before any change is "who sees a different number tomorrow?". A threshold that looks like an L2 matter may move a number on the CIO page.

### 2.4 History from the action record

- **What:** each object shows its versions and changes: who, when, why, what before and after. Read from the action record, which is append-only (D-080).
- **Why:** an auditor asks who changed a rule and why. The record already holds the answer with both identity fields (D-050). `/docs` shows it; it does not keep a second history.

### 2.5 Status: proposal or confirmed

- **What:** a setting whose source says "proposal" shows a "Proposal" chip until its owner confirms it.
- **Why:** PCM must not present an invented threshold as an agreed one (spec README, rule 6). The chip makes open items visible to everyone, not only to whoever reads the YAML.

### 2.6 Technical terms, with the plain label where one exists

- **What:** `/docs` uses the technical terms of the catalog (CPU Ready, threads, Operational Availability). Where a workspace shows a plain label, the definition says so, for example `scale.compute_cores` is shown as "computing power" on the CIO page.
- **Why:** the reader of `/docs` wants the exact meaning. The "shown as" line is the bridge between the plain words on the CIO page and the precise definition.
- **Not done:** a label is not guessed from vocabulary files. A wrong bridge is worse than none.

### 2.7 Export to private-cloud-explained

- **What:** a command writes Markdown with private-cloud-explained's front matter: SOPs as runbooks, action policies and thresholds and settings as operations plans, the inventory summary as a register.
- **Why:**
  - These are the overlaps where private-cloud-explained would otherwise hold a hand-written copy that goes stale.
  - PCM's SOPs start from an alert. In private-cloud-explained's content model, that is a runbook (a runbook starts from a symptom; an SOP from a schedule or request).
  - The export goes through private-cloud-explained's pull-request review. PCM does not write to it directly: that keeps the separation of D-082, and a person approves every page there.
- **Needed on the private-cloud-explained side:** source type `pcm` and origin `generated`. Neither exists in its content model today.
- **Not exported:** the definitions of every number. private-cloud-explained has no document type for a metric definition. They stay in `/docs` until it has one.

### 2.8 Found while designing: thresholds and standards lived in code

- The threshold for Cluster Performance red and the configuration standards were written inside the prototype code, not in the specification.
- That breaks the specification-driven build (D-070): a value the spec does not hold cannot be documented, tested or reviewed.
- Both move to the catalog: `catalog/thresholds.yaml` and `catalog/standards.yaml`.

## 3. Pages

| Path | Job | Main question |
|---|---|---|
| `/docs` | Index of every object, searchable, grouped by kind | What does PCM own, and where is it defined? |
| `/docs/{kind}/{id}` | One object: definition, version, owner, used on, history | What exactly does this mean, who owns it, and what would a change touch? |

- Kinds: measure, SOP, policy, threshold, standard, setting.
