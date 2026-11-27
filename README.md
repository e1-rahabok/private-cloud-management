# PCM, Private Cloud Manager

A web application for the operations roles of a private cloud on VMware Cloud Foundation: CIO, NOC, L2 platform engineer, capacity planner and auditor. Each role has its own workspace with its own URL (D-011, D-012). PCM reads VCF Operations and asks [Agent E2](https://github.com/e1-rahabok/agent-e2) to explain what it shows.

## Files

- [`spec/`](spec): what PCM is built from ([spec/README.md](spec/README.md)). AI generates all code from it (D-010).
- [`build/`](build): the code generated from `spec/`. Do not edit it by hand (D-070). How to run and test it: [build/README.md](build/README.md).
- [`design/`](design) and [decisions.md](decisions.md): the reasons behind the specification. Decision IDs are D-nnn.
- [`deploy/`](deploy): installing PCM and Agent E2 on a lab VM ([deploy/README.md](deploy/README.md)).
- [`demo/`](demo): the demo script and its rehearsal ([demo/README.md](demo/README.md)).

## Run

```bash
pip install pyyaml
```

```bash
python3 -m build.pcm_proto.server --port 8080
```

Then open `http://localhost:8080/exec`.

## Related repositories

- [agent-e2](https://github.com/e1-rahabok/agent-e2): the knowledge service behind PCM's Agent E2 panel.
- [PCM-Adapter](https://github.com/e1-rahabok/PCM-Adapter): the VCF vCommunity Adapter, the VCF Operations management pack whose KPIs PCM reads.
- [isvara](https://github.com/e1-rahabok/isvara): isvara.io, the public website.
- [private-cloud-workspace](https://github.com/e1-rahabok/private-cloud-workspace): the contracts between these repositories, the decisions that bind several of them, and the roadmap with its releases and milestones.
