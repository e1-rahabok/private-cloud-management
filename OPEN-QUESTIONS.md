# Open questions

Questions about private-cloud-manager only, for the author (WD-019 in the workspace's [DECISIONS.md](https://github.com/e1-rahabok/private-cloud-workspace/blob/main/DECISIONS.md)). A question that binds several repositories goes to the workspace's [OPEN-QUESTIONS.md](https://github.com/e1-rahabok/private-cloud-workspace/blob/main/OPEN-QUESTIONS.md). IDs are `Q-PCM-n` (WD-038). Write the reply after `Answer:`.

### Q-PCM-1 The style baseline of 249 problems

The workspace's style check (R-WS-006, [tools/style.py](https://github.com/e1-rahabok/private-cloud-workspace/blob/main/tools/style.py)) found 249 problems in 17 files on its first run: 133 in [decisions.md](decisions.md), whose table cells hold whole decisions, and most of the rest in the design notes (long headings, sentence headings such as "What it needs", wide tables). They are listed, file by file with their counts, in [style-baseline.yaml](style-baseline.yaml), which may only shrink: the pull request that fixes a file lowers its count.

- (a) Keep the baseline. A file is fixed when it is next edited, and its count drops.
- (b) Fix them all in M2: decisions.md becomes one block per decision, as the workspace's DECISIONS.md is, and the design notes get noun-phrase headings and bullets in place of wide tables.

- **Recommendation:** (a) for the design notes, which change with each workspace, and (b) for decisions.md, in one pull request, because its table is read most and its cells run to over 100 words.

Answer:

### Q-PCM-2 Two folder names that a newcomer misread

A fresh session guessed each folder from its name alone (T-WS-007b in the workspace's [workspace.md](https://github.com/e1-rahabok/private-cloud-workspace/blob/main/spec/requirements/workspace.md)). Two guesses were off:

- `pcm/docs` read as "documentation of PCM". It is the Docs workspace: read-only pages of PCM's own objects (SOPs, thresholds, policies), named by D-082 with its route `/docs`. Proposed: `pcm/definitions`, with the route kept or renamed with it.
- `spec/` read as "the specification". It holds the front page and the requirement files; each workspace's specification is in `pcm/<workspace>/spec/`. The workspace's tools read `spec/requirements/`, so the folder stays; its front page says where the rest is.

- **Recommendation:** rename `pcm/docs` to `pcm/definitions` and keep the route `/docs`, since users know it; keep `spec/`. A rename revises D-082 and D-133.

Answer:
