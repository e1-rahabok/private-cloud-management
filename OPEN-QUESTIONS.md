# Open questions

Questions about private-cloud-manager only, for the author (DESIGN-23 in the workspace's [system design](https://github.com/e1-rahabok/private-cloud-workspace/blob/main/spec/design/system.md)). A question that binds several repositories goes to the workspace's [OPEN-QUESTIONS.md](https://github.com/e1-rahabok/private-cloud-workspace/blob/main/OPEN-QUESTIONS.md). IDs are `Q-PCM-n` (DESIGN-23). Write the reply after `Answer:`.

### Q-PCM-4 What PCM's users call the /docs workspace

A fresh reader of PCM's folder tree (T-WS-007b in the workspace's [requirements](https://github.com/e1-rahabok/private-cloud-workspace/blob/main/spec/requirements/workspace.md), run on 2026-11-28) guessed that [`pcm/definitions`](pcm/definitions) holds the KPI and metric definitions: thresholds and formulas. It holds the Docs workspace (`/docs`): the read-only pages, API and tests that show PCM's objects. The definitions themselves are in [`pcm/core/spec/catalog/`](pcm/core/spec/catalog) and in each workspace's `catalog.yaml`. The name `definitions` came from your answer to Q-PCM-2 ([round 6](https://github.com/e1-rahabok/private-cloud-workspace/blob/main/spec/author-input/interview-round-6.md)) and is written in R-REPO-008 of [clean-up.md](spec/requirements/clean-up.md), so a rename reverses a requirement, and I stop to ask. The name before it, docs, was read as the repository's documentation (D-135 in [decisions.md](decisions.md)).

- What do the people who use `/docs` call it: Docs, or another name? The folder's name can follow what they call it.
- **Working assumption:** they call it Docs. The folder becomes `pcm/docs-workspace`: it keeps the name people see on screen and in the route, and the suffix says it is a workspace of pages, as `executive` and `noc` are, so a reader does not take it for the repository's documentation. R-REPO-008, the design note and every path change in one pull request, and T-WS-007b runs again on PCM.

Answer:

### Q-PCM-3 How you show the live demo

R-LIVE-036 in [live-demo.md](spec/requirements/live-demo.md) tests the live demo end to end, step by step, as you show it. The synthetic demo has its script and rehearsal in [demo/README.md](demo/README.md); the live demo has none, and the brief and your recorded answers (Q-WS-20 to Q-WS-39) name the pages but not the order you walk them in. Search found no demo order in the brief, the interview rounds or the decisions.

- Which steps do you walk, in which order, and what do you point at on each? Correct the working assumption below, or replace it.
- Do you open VCF Operations beside PCM during the demo, and on which objects?
- **Working assumption**, about 10 minutes:
  1. The demo drop-down, then "Live L2". Say: this is the lab's VCF Operations, read now.
  2. The tree: the VCF instance, then a vCenter, a datacenter and a cluster.
  3. The cluster's Performance tab: Cluster Performance's Now, Worst with its time, and the 5th percentile. VCF Operations opened beside it on the same cluster shows the same numbers.
  4. The Details fold: the parts at the worst point.
  5. Ask Agent E2 "Why the worst?". The answer names the part that pulled the KPI down. Rate it.
  6. The Capacity tab: Capacity Remaining, Time Remaining and VM Remaining from VCF Operations, and the Periodic Cluster Check's verdict.
  7. Back up to the VCF instance: the lines across clusters.
  8. One ESXi host and one VM of the cluster: their Performance tabs.

Answer:
