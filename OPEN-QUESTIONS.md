# Open questions

Questions about private-cloud-manager only, for the author (DESIGN-23 in the workspace's [system design](https://github.com/e1-rahabok/private-cloud-workspace/blob/main/spec/design/system.md)). A question that binds several repositories goes to the workspace's [OPEN-QUESTIONS.md](https://github.com/e1-rahabok/private-cloud-workspace/blob/main/OPEN-QUESTIONS.md). IDs are `Q-PCM-n` (DESIGN-23). Write the reply after `Answer:`.

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
