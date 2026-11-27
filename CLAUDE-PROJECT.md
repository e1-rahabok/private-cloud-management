# CLAUDE-PROJECT.md

Rules, tools and paths of private-cloud-manager, the repository of PCM (Private Cloud Manager). Loaded with [CLAUDE.md](CLAUDE.md), which holds the method. This repository is one of several; work across them follows the workspace's [CLAUDE-PROJECT.md](https://github.com/e1-rahabok/private-cloud-workspace/blob/main/CLAUDE-PROJECT.md).

## Files of the method

- Roadmap, open questions and decisions that bind several repositories: the workspace's [ROADMAP.md](https://github.com/e1-rahabok/private-cloud-workspace/blob/main/ROADMAP.md), [OPEN-QUESTIONS.md](https://github.com/e1-rahabok/private-cloud-workspace/blob/main/OPEN-QUESTIONS.md) and [DECISIONS.md](https://github.com/e1-rahabok/private-cloud-workspace/blob/main/DECISIONS.md).
- No hook runs here. Before acting, read the open milestone in the workspace's ROADMAP.md: the first heading that does not end with ": done".
- Requirements of this repository: [`spec/requirements/`](spec/requirements) (WD-036). Each requirement belongs to the workspace milestone that ROADMAP.md names.
- Decisions inside this repository: [decisions.md](decisions.md), IDs D-nnn.
- Specification: one folder per workspace under [pcm/](pcm), each with its `spec/` folder; front page [spec/README.md](spec/README.md) (D-133). Reasons behind it: each workspace's `design-note.md`, the notes in [pcm/core/design-notes/](pcm/core/design-notes), and [decisions.md](decisions.md).

## Code

- AI generates all code in [pcm/](pcm) from the `spec/` folders and design notes beside it (D-010). Change the specification first.
- Never edit generated code by hand: in a workspace folder, every file outside `spec/` and the design note (D-070).

## Checks before each commit

- The unit tests and page tests listed in [pcm/README.md](pcm/README.md), section Test, from the repository root: `python3 -m unittest pcm.<workspace>.tests.test_<name> -v` and `node pcm/<workspace>/tests/<workspace>.page.test.mjs`.

## Deploy

- Installing PCM and Agent E2 on the lab VM: [deploy/README.md](deploy/README.md). Wait for the author before changing the lab.
