# PCM, Private Cloud Manager

A web application for the operations roles of a private cloud on VMware Cloud Foundation: CIO, NOC, L2 platform engineer, capacity planner and auditor. Each role has its own workspace with its own URL (D-011, D-012). PCM reads VCF Operations and asks [Agent E2](https://github.com/e1-rahabok/agent-e2) to explain what it shows.

## Files

- [`pcm/`](pcm): the application, one folder per workspace ([`executive/`](pcm/executive), [`noc/`](pcm/noc), [`l2/`](pcm/l2), [`capacity/`](pcm/capacity), [`docs/`](pcm/docs)) and [`core/`](pcm/core) for the parts every workspace uses (D-133). Each folder holds a design note, the specification in `spec/`, and the code, pages and tests generated from them. AI generates all code from the specification (D-010); do not edit generated code by hand (D-070). How to run and test it: [pcm/README.md](pcm/README.md).
- [`spec/`](spec): the specification's front page ([spec/README.md](spec/README.md)) and the requirements of PCM's work ([spec/requirements/](spec/requirements)).
- [decisions.md](decisions.md): the reasons behind the specification, with the design notes. Decision IDs are D-nnn.
- [`author-papers/`](author-papers): the author's papers that PCM is designed from ([author-papers/README.md](author-papers/README.md)).
- [`deploy/`](deploy): installing PCM and Agent E2 on a lab VM ([deploy/README.md](deploy/README.md)).
- [`demo/`](demo): the demo script and its rehearsal ([demo/README.md](demo/README.md)).
- [`tools/`](tools): scripts for the lab, run from the author's laptop.

## Run

```bash
pip install pyyaml
```

```bash
python3 -m pcm.core.server --port 8080
```

Then open `http://localhost:8080/exec`.

## Related repositories

- [agent-e2](https://github.com/e1-rahabok/agent-e2): the knowledge service behind PCM's Agent E2 panel.
- [PCM-Adapter](https://github.com/e1-rahabok/PCM-Adapter): the VCF vCommunity Adapter, the VCF Operations management pack whose KPIs PCM reads.
- [isvara](https://github.com/e1-rahabok/isvara): isvara.io, the public website.
- [private-cloud-workspace](https://github.com/e1-rahabok/private-cloud-workspace): the contracts between these repositories, the decisions that bind several of them, and the roadmap with its releases and milestones.
