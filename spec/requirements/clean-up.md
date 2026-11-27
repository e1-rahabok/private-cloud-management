# Requirements: clean-up of private-cloud-manager

The clean-up of private-cloud-manager in milestone M2 of the workspace's [ROADMAP.md](https://github.com/e1-rahabok/private-cloud-workspace/blob/main/ROADMAP.md): the product's name, and folders and files named for what they hold. Question IDs point at the interview ([round 1](https://github.com/e1-rahabok/private-cloud-workspace/blob/main/spec/interview-round-1.md), [round 2](https://github.com/e1-rahabok/private-cloud-workspace/blob/main/spec/interview-round-2.md), [round 3](https://github.com/e1-rahabok/private-cloud-workspace/blob/main/spec/interview-round-3.md), [round 4](https://github.com/e1-rahabok/private-cloud-workspace/blob/main/spec/interview-round-4.md)); other IDs are explained in the [glossary](https://github.com/e1-rahabok/private-cloud-workspace/blob/main/spec/glossary.md).

## Names

### R-REPO-005 The product is called Private Cloud Manager

Milestone: M2.

Source: Q-WS-60 (round 3: "Manager, not Management"); WD-028.

- Given PCM's documents and its decision log
- When a reader meets the product's full name
- Then it is "Private Cloud Manager", in PCM's README, its design documents and D-001
- And "Private Cloud Management" remains only where it names the discipline or the author's books

Test scenarios:
- T-REPO-005a (anywhere, manual review): search PCM's documents for "Private Cloud Management"; expect each remaining use to name the discipline or a book.

### R-REPO-007 PCM's folders and files are named for what they hold

Milestone: M2.

Source: WD-030; PCM D-132.

- Given [private-cloud-manager](https://github.com/e1-rahabok/private-cloud-manager), whose folder [`build/`](https://github.com/e1-rahabok/private-cloud-manager/tree/main/build) holds the application's source code and [`sources/`](https://github.com/e1-rahabok/private-cloud-manager/tree/main/sources) holds the author's papers
- When a reader sees its folder tree
- Then the Python package `pcm_proto` is `pcm`
- And [`sources/`](https://github.com/e1-rahabok/private-cloud-manager/tree/main/sources) is `author-papers/`, and the papers' file names carry no version number
- And "story" becomes "PCM scenario story" in every file of PCM: design notes, decisions, spec, tests and generated code; the IDs stay (N-2, O-1, M-5)
- And `l2_story_m5.py` and `test_story_m5.py` are named for what their PCM scenario story shows; the ID M-5 in the file name tells a reader nothing
- And [`spec/data/`](https://github.com/e1-rahabok/private-cloud-manager/tree/main/spec/data) is `spec/demo-data/`
- And "design" names one thing: [`design/`](https://github.com/e1-rahabok/private-cloud-manager/tree/main/design) and [`spec/design-system/`](https://github.com/e1-rahabok/private-cloud-manager/tree/main/spec/design-system) no longer share the word with two meanings
- And [`tools/moltbot/`](https://github.com/e1-rahabok/private-cloud-manager/tree/main/tools/moltbot) is named for what it does
- And every reference to an old path is updated in the same change: PCM's tests, service files, deploy scripts, documents, and the requirement files of this workspace

Test scenarios:
- T-REPO-007a (anywhere, automated by PCM's own tests): every test passes after the renames, and the demo starts.
- T-REPO-007b (anywhere, automated by a search to write in [checks](https://github.com/e1-rahabok/private-cloud-workspace/tree/main/checks)): no file in any repository, outside the requirement files that name them to forbid them, names [`build/pcm_proto`](https://github.com/e1-rahabok/private-cloud-manager/tree/main/build/pcm_proto), `pcm_proto`, [`sources/`](https://github.com/e1-rahabok/private-cloud-manager/tree/main/sources) of PCM or `story_m5`, outside archives and dated records.
- T-REPO-007c (anywhere, manual): T-WS-007b on PCM finds no wrong guess.

### R-REPO-008 PCM's folders are grouped by workspace

Milestone: M2.

Source: Q-WS-134 (round 4: "Yes, by workspace."); WD-030.

- Given PCM's five workspaces (executive, NOC, L2, capacity, docs) and the parts they share
- When a session works on one workspace
- Then one folder per workspace holds everything that workspace needs: its design note, its API, catalog and test specifications, its server code, its page code and its tests
- And each workspace folder has the workspace's full name, for example `executive` and not `exec`, and the page code for Agent E2 is named `agent-e2` and not `e2`
- And the parts every workspace uses (the server, the store, the object model, the database schema, the shared catalog files, the demo data generator, the fonts) sit in one shared folder named for what it holds
- And [`build/`](https://github.com/e1-rahabok/private-cloud-manager/tree/main/build) no longer exists, and the moves are done in the same change as R-REPO-007, so no file moves twice
- And PCM's decision log records the layout as a PCM decision
- And the layout is set in PCM's specification first and the code is generated into it, as D-010 and D-070 require; PCM's CLAUDE-PROJECT.md and the build README move with it
- And the contract check C3, which imports PCM's Agent E2 client, moves in three steps: the client is importable from its new path and its old one, the check moves to the new path, and the old path goes

Test scenarios:
- T-REPO-008a (anywhere, automated by PCM's own tests): every test passes after the move, and the demo starts.
- T-REPO-008d (anywhere, automated by the workspace's `checks/run_all.py`): C3 passes after each of the three steps.
- T-REPO-008b (anywhere, manual): list every file that only the L2 workspace uses; expect each one inside L2's folder.
- T-REPO-008c (anywhere, manual): T-WS-007b on PCM finds no wrong guess.
