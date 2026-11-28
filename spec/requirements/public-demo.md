# Requirements: PCM's public demo

PCM's synthetic ACME demo, served to anyone on the internet at an address of its own, so that visitors of isvara.io can try PCM without installing it. It holds no live instance. Written from the author's request of 2026-11-28 ([author input](https://github.com/e1-rahabok/private-cloud-workspace/blob/main/spec/author-input/)). isvara.io only links to it ([R-SITE-011](https://github.com/e1-rahabok/isvara/blob/main/spec/requirements/site.md)). Every requirement here belongs to milestone M8 in the workspace's [ROADMAP.md](https://github.com/e1-rahabok/private-cloud-workspace/blob/main/ROADMAP.md), the milestone of PCM's demos. IDs are explained in the [glossary](https://github.com/e1-rahabok/private-cloud-workspace/blob/main/spec/glossary.md).

### R-PUBLIC-001 The synthetic demo is open to the internet at its own address

Why: a visitor judges PCM by using it, and installing it first loses most of them (GOAL-6).

Source: the author, 2026-11-28 ("the PCM demo as it is, so it has its own look and feel matching the actual demo... It can open on a new URL"); SCOPE-4 (the synthetic demo stays as it is).

Milestone: M8.

- Given the synthetic ACME demo
- When it is deployed for the public
- Then it opens at its own address, not under isvara.io, with PCM's look and feel and none of isvara.io's
- And its pages, data and drop-down entries match the synthetic demo of the PCM server, with no entry for the live demo
- And it needs no sign-in and asks for no address
- And it reads no lab, no VCF Operations and no credential, and its address is kept apart from the lab VM
- And search engines are told not to index it until the author says so

Test scenarios:
- T-PUBLIC-001a (anywhere, page test, to write): open the public demo's address in a fresh browser; every synthetic page of the PCM server opens with the same title; the drop-down holds no live entry and `/live/l2` answers 404; the response says noindex.
- T-PUBLIC-001b (anywhere, automated by a check, to write): the public demo's files hold no lab address, no host name of the lab and no secret (the workspace's `tools/lab_addresses.py` and `tools/secret_values.py` pass over them).

### R-PUBLIC-002 The public demo is rebuilt from the PCM specification

Why: a second copy kept by hand would drift from the demo the author shows (PRINCIPLE-5).

Source: the author, 2026-11-28 ("the PCM demo as it is"); D-010 (AI generates all code from the specification).

Milestone: M8.

- Given a change to the synthetic demo of PCM
- When the pull request merges
- Then the public demo is built from the same pages and data, by one command, with no hand edit

Test scenarios:
- T-PUBLIC-002a (anywhere, automated by a check, to write): the build of the public demo twice from one commit gives the same files; a page of the PCM server missing from the build fails the check.

### R-PUBLIC-003 Visitors can ask Agent E2 in the public demo, within limits

Why: the demo shows PCM at its best when its explanations answer a visitor's own question, as isvara.io's Ask does today. Ask on isvara.io already receives spam, and an open endpoint costs money on every call, so an unlimited one is a bill and an abuse route.

Source: the author, 2026-11-28 ("look at Ask.io today at isvara.io. It is already answering live question. That's why I said it got spam"); R-PROTECT-001 to R-PROTECT-006 in isvara's [protection.md](https://github.com/e1-rahabok/isvara/blob/main/spec/requirements/protection.md) (the limits chosen for Ask, reused here); RISK-10 (one vendor for hosting and the gateway).

Milestone: M8.

- Given a visitor of the public demo asks Agent E2 a question
- When the question is sent
- Then Agent E2 answers about the synthetic ACME data only, through the same API as PCM, and the demo holds no key of the gateway or the lab
- And the platform's flood limit, a bot check and a per-address question limit apply before any model call, set no looser than isvara.io's Ask
- And a daily spending ceiling of its own, apart from isvara.io's, stops the model calls for the rest of the day when reached, and the visitor sees a plain notice and the stored explanations
- And one switch closes the questions at once, leaving the rest of the demo open
- And a question's text is kept no longer than isvara.io keeps Ask's, and no visitor identifier is stored

Test scenarios:
- T-PUBLIC-003a (anywhere, automated by a page test and a fake Agent E2, to write): a question gets an answer; the fake records that it received only synthetic data; the page holds no key.
- T-PUBLIC-003b (anywhere, automated, to write): more questions than the per-address limit from one address get the limit notice and no model call; with the ceiling reached, the next question gets the notice and no model call; with the switch closed, the question box shows the notice.
