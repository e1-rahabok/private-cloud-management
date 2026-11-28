# PCM test plan

How PCM is tested, and how a test proves that a number on a live page is correct. The live demo's requirements and their test scenarios are in [live-demo.md](requirements/live-demo.md); the synthetic demo's acceptance tests are in each workspace's `spec/acceptance-tests.yaml`. This plan puts them in the order they run and says what decides a pass. The workspace's [test plan](https://github.com/e1-rahabok/private-cloud-workspace/blob/main/spec/test-plan.md) sets the rules for every repository; this one applies them to PCM. IDs are explained in the workspace's [glossary](https://github.com/e1-rahabok/private-cloud-workspace/blob/main/spec/glossary.md).

The model is the VCF vCommunity Adapter's [Live Validation Test Plan](https://github.com/e1-rahabok/PCM-Adapter/blob/main/tools/validate/validate.md), with one difference. The adapter's validation checks that data exists and is fresh, and says so under "Not covered". PCM's lab tests also check that each value PCM shows equals the value VCF Operations holds, because the audience can open the same object in VCF Operations during the demo (R-LIVE-024).

## Test levels

| Level | Command | Proves | Runs |
| :--- | :--- | :--- | :--- |
| Unit tests | `python3 -m unittest pcm.<workspace>.tests.test_<name> -v`, from the repository root ([pcm/README.md](../pcm/README.md), section Test) | Each workspace's code, the live reader and its figures, with the fake Suite API | Anywhere, before each commit; in CI on every pull request ([tests.yml](../.github/workflows/tests.yml)) |
| Page tests | `node pcm/<workspace>/tests/<workspace>.page.test.mjs` | Each page's parts, states and links, in Chromium | Anywhere, before each commit; in CI on every pull request ([tests.yml](../.github/workflows/tests.yml)), one after the other |
| Synthetic rehearsal | `node demo/rehearse.mjs` ([demo/README.md](../demo/README.md)) | The synthetic demo script, step by step, with a screenshot per step | Anywhere, before every demo |
| Lab tests | `pwsh tools/lab/Test-Live.ps1` (R-LIVE-031, to write) | Every lab scenario of [live-demo.md](requirements/live-demo.md), then the live demo end to end | The author's laptop on the VPN, from M8 |

A lab test is written only for what a fake cannot prove: the real Suite API, the real adapter's keys, the lab's certificate and account rights, and the time a page takes. Everything else is tested with the fake Suite API (`pcm/l2/tests/fake_suite_api.py`, to write).

## The oracle

A lab test needs a second, independent source for the value PCM should show. That source is the reference script, `tools/lab/live_reference.py` (to write).

- It reads the raw 5-minute samples of a key from the lab's Suite API for the window that PCM's API reports, with its own HTTP calls.
- It computes Now (the newest sample), Worst (the lowest sample, or the highest where higher is worse, with its time) and the percentile figure (5th where higher is better, 95th where higher is worse), by nearest rank.
- For the part that moved a KPI (R-LIVE-030) it scores each part at the worst point with the VCF vCommunity Adapter's own scoring code, which it imports from the adapter's clone.
- It prints one line per figure: object, key, figure, value, and the time of the sample.

Design choices:

- **The reference script shares no code with PCM's live reader.** Why: a bug in a shared reader would put the same wrong value on both sides, and the comparison would pass. Rejected: calling PCM's reader from the test, because it then tests PCM against itself; reading the values off the VCF Operations screen, because a screen scrape breaks with each VCF Operations release. Serves: R-LIVE-024, R-LIVE-025, R-LIVE-026, R-LIVE-027.
- **The reference script imports the adapter's scoring code and does not copy it.** Why: the adapter computes the KPI that VCF Operations stores, so its code is the definition of "the part that lost the most points". A copy would drift from it. Rejected: a second scoring in PCM's tests, for the same reason. Serves: R-LIVE-030.
- **The reference script is itself tested on a fixed series.** Why: an oracle with a bug passes a wrong PCM. T-LIVE-024c runs it on the 288 samples of T-LIVE-024b and expects the values computed by hand. Serves: R-LIVE-024.
- **Relevance of a suggested question is decided by Agent E2's written rule, computed by the reference.** Why: "relevant" (Q-PCM-3) needs an oracle a test can run; the rule in Agent E2's `user_suggestions.py` defines the page's situation from its KPI series, and its question table lists what fits each situation. The reference computes the situation from its own reads by that written rule, and the test checks the shown questions come from that situation's list. Rejected: a model judging relevance, because it would pass a fluent question about the wrong situation; a fixed list of expected questions, because the lab's situation changes from day to day. Serves: R-LIVE-038.
- **Correctness of an answer has three layers.** Why: no single check catches every wrong answer. Each figure in the answer is compared with the reference (a wrong number fails at once); the grader of R-E2-005 scores the answer against key points written from the reference (a wrong reason fails); and the author rates every answer at the M8 rehearsal (what neither check sees). Rejected: the grader alone, because a grader can accept a wrong figure stated with a right reason; the author alone, because about 80 answers per walk is too many to read on every run. Serves: R-LIVE-039.
- **Values are compared at whole percent, or at a part's own decimals.** Why: PCM shows whole percent, and a part's limits set its decimals (R-LIVE-025). Rejected: an exact comparison of floating-point values, because rounding on two sides would fail a correct page.

## Safety

- Every lab call is read-only: Suite API `GET` calls and the token request, with the read-only account of DESIGN-9 (R-LIVE-007, R-LIVE-009). T-LIVE-009b proves that no call needs more rights.
- Nothing in VCF Operations, vCenter or the lab VM's data is changed (R-LIVE-031). The one write is PCM's own record of each Agent E2 answer and its rating (R-LIVE-035), in PCM's database on the lab VM.
- Credentials are read from the DPAPI files in `$HOME\.secrets\` (DESIGN-9) and are never printed, logged or saved in a screenshot. The lab's addresses and host names are read from `$HOME\.secrets\lab.json` ([tools/lab/Lab-Config.ps1](../tools/lab/Lab-Config.ps1)); no test, report or screenshot file name holds one (R-WS-010). [tools/lab/Test-Lab.ps1](../tools/lab/Test-Lab.ps1) still reads Windows Credential Manager; [live-demo.md](requirements/live-demo.md), section "Changes to PCM's own specification", lists its move to the DPAPI files.
- Lab facts may reach the cloud model through the gateway (SCOPE-5); the VCF Operations password, token and URL never do (R-LIVE-029).

## Lab run order

`Test-Live.ps1` runs the lab scenarios in this order. A step whose condition fails stops the run, and every later scenario is reported as not run. "Not run" is never reported as a pass.

| Step | What it checks | Scenarios | On failure |
| :--- | :--- | :--- | :--- |
| 1. Access | VPN, sign-ins and the lab VM's pages answer; only 443 and SSH are open ([Test-Lab.ps1](../tools/lab/Test-Lab.ps1)) | T-LIVE-037a | Stop |
| 2. The adapter collects | The VCF vCommunity Adapter's [validate.ps1](https://github.com/e1-rahabok/PCM-Adapter/blob/main/tools/validate/validate.ps1) exits 0 | none of its own | Stop: the pack is not collecting, which is the adapter's fault |
| 3. Sign-in and rights | The read-only account, the lab certificate, no refused call; the lab's VCF Operations version is printed | T-LIVE-007c, T-LIVE-008b, T-LIVE-009b, T-LIVE-031a | Stop |
| 4. The key list | Every key PCM reads exists on the lab and is fresh | T-LIVE-023a, T-LIVE-023c | Stop: a missing key fails every figure after it |
| 5. The live entry and the tree | `/live/l2` opens; the tree is VCF Operations' inventory | T-LIVE-001b, T-LIVE-012b | Go on |
| 6. Figures against the oracle | Every KPI, part, line, remaining value and check equals the oracle | T-LIVE-024a, T-LIVE-025a, T-LIVE-026a, T-LIVE-017b, T-LIVE-027b, T-LIVE-021b, T-LIVE-022b, T-LIVE-018b | Go on |
| 7. Absent data | A powered-off VM shows "No data" | T-LIVE-015b | Go on |
| 8. Page time | A cluster's Performance and Capacity tabs show within 5 seconds with an empty cache | T-LIVE-033b | Go on |
| 9. Agent E2 | "Why the worst?" names the oracle's part | T-LIVE-030a | Go on |
| 10. The demo end to end | The live demo script, every Agent E2 mark and question | T-LIVE-036a, T-LIVE-038a, T-LIVE-039a, T-LIVE-040b | Go on; a failed health check makes every question NOT RUN |
| 11. The author's walk | The author walks the same script and rates every answer | T-LIVE-039b, T-LIVE-037b | Manual, recorded in the M8 pull request |

Step 10 walks the script of [demo/README.md](../demo/README.md), section The live demo: the demo cluster's Performance and Capacity tabs, then one host's and one VM's Performance tab, with every Agent E2 mark and every suggested question on each, about 80 answers (81 on the synthetic demo, LPG-31). It checks Agent E2's health first.

After release 1.0: T-LIVE-034a, the tiering parts, once the lab has a tiered cluster (SCOPE-17).

Each scenario prints one line: its ID, PASS, FAIL or NOT RUN, and a short detail. The run saves a screenshot of every live page it checked in one folder, and exits 1 when any scenario failed or did not run.

## Before M8

The live demo is built in M8, the workspace's milestone for it ([ROADMAP.md](https://github.com/e1-rahabok/private-cloud-workspace/blob/main/ROADMAP.md)). Until then a cloud session cannot reach the lab (CONSTRAINT-6): it runs the unit and page tests with the fake Suite API, reports each lab scenario as not run, lists them in its pull request for M8's lab session, and goes on.

## Pass criteria

- A pull request merges when every unit and page test passes and its text lists the lab scenarios it could not run.
- M8 is done when `Test-Live.ps1` exits 0 on the lab with every scenario passed, the synthetic tests still pass unchanged (R-LIVE-032), the screenshots are in the pull request, and the author approves the milestone.

## Not covered

- Scale: the lab has a few clusters; a large estate's page time is not measured.
- VCF Operations versions other than the lab's; the version is recorded at each run (T-LIVE-031a).
- The tiering parts, until the lab has a tiered cluster (R-LIVE-034).
- The synthetic demo against VCF Operations: it never reads it (R-LIVE-002).
