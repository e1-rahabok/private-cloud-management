# CLAUDE-PROJECT.md

Rules, tools and paths of private-cloud-manager, the repository of PCM (Private Cloud Manager). Loaded with [CLAUDE.md](CLAUDE.md), which holds the method. This repository is one of several; work across them follows the workspace's [CLAUDE-PROJECT.md](https://github.com/e1-rahabok/private-cloud-workspace/blob/main/CLAUDE-PROJECT.md).

## Files of the method

- Roadmap, open questions and decisions that bind several repositories: the workspace's [ROADMAP.md](https://github.com/e1-rahabok/private-cloud-workspace/blob/main/ROADMAP.md), [OPEN-QUESTIONS.md](https://github.com/e1-rahabok/private-cloud-workspace/blob/main/OPEN-QUESTIONS.md) and [DECISIONS.md](https://github.com/e1-rahabok/private-cloud-workspace/blob/main/DECISIONS.md).
- No hook runs here. Before acting, read the open milestone in the workspace's ROADMAP.md: the first heading that does not end with ": done".
- Decisions inside this repository: [decisions.md](decisions.md), IDs D-nnn.
- Specification: [spec/](spec) ([spec/README.md](spec/README.md)). Reasons behind it: [design/](design).

## Code

- AI generates all code in [build/](build) from [spec/](spec) (D-010). Change the specification first.
- Never edit [build/](build) by hand (D-070).

## Checks before each commit

- The unit tests and page tests listed in [build/README.md](build/README.md), section Tests: `python3 -m unittest build.tests.test_<workspace> -v` and `node build/tests/<workspace>.page.test.mjs`.

## Deploy

- Installing PCM and Agent E2 on the lab VM: [deploy/README.md](deploy/README.md). Wait for the author before changing the lab.
