# Requirements: PCM live demo

PCM's live demo is the L2 workspace reading the author's lab VCF Operations (its address in `$HOME\.secrets\lab.json` and `/etc/pcm/pcm.env`, DESIGN-9) through its Suite API. It is a separate demo with its own entry in the demo drop-down. The synthetic ACME demo stays as it is. The scope is performance and capacity management only. These requirements come from [SCOPE-5, the live demo decision](https://github.com/e1-rahabok/private-cloud-workspace/blob/main/spec/brief.md), and from the author's answers to Q-WS-20 to Q-WS-39 in the [interview, round 1](https://github.com/e1-rahabok/private-cloud-workspace/blob/main/spec/author-input/interview-round-1.md). Other short names are explained in the [glossary](https://github.com/e1-rahabok/private-cloud-workspace/blob/main/spec/glossary.md).

Milestone ([ROADMAP.md](https://github.com/e1-rahabok/private-cloud-workspace/blob/main/ROADMAP.md)): every requirement here belongs to M8, the PCM live demo. Its first slice is one lab cluster's Cluster Performance on the L2 Performance tab: R-LIVE-001, R-LIVE-024 and R-LIVE-030.

Files involved:

- PCM's L2 specification: [pcm/l2/spec/catalog.yaml](https://github.com/e1-rahabok/private-cloud-manager/blob/main/pcm/l2/spec/catalog.yaml), [pcm/l2/spec/pages/monitor.md](https://github.com/e1-rahabok/private-cloud-manager/blob/main/pcm/l2/spec/pages/monitor.md), [pcm/l2/spec/pages/frame.md](https://github.com/e1-rahabok/private-cloud-manager/blob/main/pcm/l2/spec/pages/frame.md), [pcm/l2/spec/api.yaml](https://github.com/e1-rahabok/private-cloud-manager/blob/main/pcm/l2/spec/api.yaml).
- What VCF vCommunity Adapter publishes, and how it makes absent data and its check settings readable: [adapter.md](https://github.com/e1-rahabok/PCM-Adapter/blob/main/spec/requirements/adapter.md), drafted in parallel. This file does not repeat it.
- The contracts: [C2, KPI metric keys](https://github.com/e1-rahabok/private-cloud-workspace/blob/main/spec/glossary.md#c2) (the keys the VCF vCommunity Adapter publishes and PCM reads) and [C3, the Agent E2 API](https://github.com/e1-rahabok/private-cloud-workspace/blob/main/spec/glossary.md#c3) (the calls PCM makes to Agent E2), in [contracts](https://github.com/e1-rahabok/private-cloud-workspace/blob/main/spec/design/system.md#contracts).

The order the lab scenarios run in, the reference script that gives each expected value, and what decides a pass are in [PCM's test plan](../test-plan.md). Tests named below do not exist yet unless stated; "to write" marks them. Lab scenarios run from the author's laptop over the VPN. They use the read-only VCF Operations credential in `$HOME\.secrets\` ([DESIGN-9, lab credentials](https://github.com/e1-rahabok/private-cloud-workspace/blob/main/spec/design/system.md)). They start by running VCF vCommunity Adapter's [validate.ps1](https://github.com/e1-rahabok/PCM-Adapter/blob/main/tools/validate/validate.ps1), so a failure caused by a pack that is not collecting is reported as such. A lab scenario that cannot reach the lab is reported as not run, never as passed.

## The demo and its scope

### R-LIVE-001 A separate entry for the live demo

Why: the author keeps the synthetic and the live demos apart, so neither can be switched into the other by mistake (SCOPE-4).

Source: the author's answers to Q-WS-20 and Q-WS-32 in the interview, round 1 ("The synthetic and the live are 2 separate demoes. Not flippable"); SCOPE-4, the decision to keep ACME and add a separate live demo; Q-WS-65 (the page `/live/l2` and the API `/api/live/l2/` on the same PCM server).

Milestone: M8, first slice.

- Given PCM runs with the demo control on
- When a person opens the demo drop-down on any page
- Then it lists one new entry for the live L2 demo, with its own URL, `/live/l2`, served with its API under `/api/live/l2/` by the same PCM server
- And every synthetic entry keeps its place, its URL and its behaviour
- And no page of either demo has a control that switches its data to the other

Test scenarios:
- T-LIVE-001a (anywhere, automated by pcm/l2/tests/live.page.test.mjs::test_demo_entry, to write). Data: PCM started against the fake Suite API (pcm/l2/tests/fake_suite_api.py, to write). Steps: open `/exec`, open the drop-down, choose the live entry. Expected: the entry is listed once; choosing it opens `/live/l2`; the synthetic entries are unchanged in order and URL.
- T-LIVE-001b (lab, automated by pcm/l2/tests/live.lab.test.mjs::test_demo_entry, to write). Data: PCM on the lab VM with the live connection configured. Steps: as in 001a. Expected: the live L2 page opens and its tree shows objects from the lab VCF Operations; a screenshot is saved for review.

### R-LIVE-002 Live and synthetic data never meet

Why: a synthetic value shown as live, or a live value as synthetic, would mislead the audience of a demo.

Source: answer to Q-WS-32; SCOPE-5.

- Given the live demo and the synthetic demo run in the same PCM
- When any page or API call of either demo answers
- Then every value from the live demo carries the source of the lab VCF Operations instance in its metadata
- And no live response contains a synthetic object, value, PCM scenario story or calendar entry
- And no synthetic response contains a live object or value

Test scenarios:
- T-LIVE-002a (anywhere, automated by pcm/l2/tests/test_live.py::test_no_mixing, to write). Data: the fake Suite API with three objects whose names do not occur in ACME. Steps: call every live API path, then every synthetic API path. Expected: live responses carry only the fake's objects, each value with the live source; synthetic responses carry no fake object name.

### R-LIVE-003 The live demo is the L2 workspace only

Why: release 1.0 shows the live lab in the L2 workspace only (SCOPE-5), and other workspaces would show synthetic data under a live address.

Source: answer to Q-WS-22 ("The live mode is only L2. The rest of the role is synthetic only"); SCOPE-5.

- Given the live demo
- When a person or a test asks for an Executive, NOC, Capacity or Docs page or API path under the live prefix
- Then PCM answers 404
- And the live demo's pages link to no page of another workspace

Test scenarios:
- T-LIVE-003a (anywhere, automated by pcm/l2/tests/test_live.py::test_l2_only, to write). Steps: request `/live/exec`, `/live/noc`, `/live/capacity`, `/live/docs` and their API paths. Expected: 404 for each; the live L2 page has no link to another workspace.

### R-LIVE-004 Performance and capacity only

Why: the author set release 1.0 on performance and capacity management (Q-WS-33), and the other tabs would have nothing live to show.

Source: answer to Q-WS-33 ("All these are out of scope in 1.0. Focus on performance and capacity management"); SCOPE-5; Q-WS-63 (the Performance and Capacity tabs of a cluster, an ESXi host and a VM, the same tabs on the objects above the cluster, and the tree).

- Given the live L2 page
- When it opens on any object
- Then it shows the Monitor activity with the Performance and Capacity tabs only, on a cluster, an ESXi host, a VM and each object above the cluster in the tree
- And it shows no Troubleshoot, Improve, Rules or Calendar entry, no other pillar tab, no PCM scenario story, no case and no action button
- And an object opens on its Performance tab; the live demo has no Summary tab (Q-PCM-3, step 2: "I'd ignore this in Release 1.0")
- And the live API refuses every write path with 404

Test scenarios:
- T-LIVE-004a (anywhere, automated by pcm/l2/tests/live.page.test.mjs::test_tabs_only, to write). Data: the fake Suite API. Steps: open a cluster, a host, a VM and the VCF instance. Expected: each opens on its Performance tab; only Performance and Capacity tabs, on each, and no Summary tab; no Troubleshoot, Improve, Rules or Calendar entry; no action button.
- T-LIVE-004b (anywhere, automated by pcm/l2/tests/test_live.py::test_no_writes, to write). Steps: POST to each L2 write path under the live prefix (cases, proposals, decisions, policies, thresholds, calendar). Expected: 404 for each, and nothing written to PCM's database.

### R-LIVE-005 No clock and no planted PCM scenario stories in the live demo

Why: the clock and the planted stories belong to the synthetic demo; on live data they would invent events the lab never had.

Source: answer to Q-WS-32; answer to Q-WS-33.

- Given the live API
- When a request carries `now` or `enable`
- Then PCM answers 400 and names the parameter
- And the live page has no control that sets the clock or turns on a PCM scenario story

Test scenarios:
- T-LIVE-005a (anywhere, automated by pcm/l2/tests/test_live.py::test_now_enable_refused, to write). Steps: call a live API path with `now=2026-10-19T10:05:00+08:00`, then with `enable=E-7`. Expected: 400 each time, with the parameter named in the body.

### R-LIVE-006 No class of service, region, environment or time zone

Why: the lab has no class of service, region or environment data (CONSTRAINT-5), and showing them would invent facts.

Source: answer to Q-WS-24 ("All these are only applicable in synthetic"); SCOPE-5.

- Given the live L2 page above the cluster, on the Performance or Capacity tab
- When it opens
- Then it has no class of service filter, and no text about Gold, Silver or Bronze
- And the lines across clusters (worst and percentile) cover every cluster under the selected object
- And no live object shows a region, location, class, environment or local time zone
- And times are shown in the viewer's time zone with the zone named, as in the synthetic demo ([PCM D-074, three rules from the first build's review](https://github.com/e1-rahabok/private-cloud-manager/blob/main/decisions.md#d-074-rules-from-the-first-builds-review))

Test scenarios:
- T-LIVE-006a (anywhere, automated by pcm/l2/tests/live.page.test.mjs::test_no_class, to write). Data: the fake Suite API with two clusters under one VCF instance. Steps: open the VCF instance's Performance and Capacity tabs. Expected: no class filter; the words Gold, Silver and Bronze are absent; the worst line is the lower of the two clusters at each point.

## Connection to VCF Operations

### R-LIVE-007 Sign-in with a read-only account from the lab VM's secret file

Why: the live demo only reads, so it signs in with an account that cannot change the lab, from a file outside the repository (DESIGN-9).

Source: answer to Q-WS-34 ("agree"); DESIGN-9.

- Given `/etc/pcm/pcm.env` on the lab VM holds the Suite API URL, user and password in `PCM_VCFOPS_URL`, `PCM_VCFOPS_USER` and `PCM_VCFOPS_PASSWORD`
- When the live demo needs data
- Then PCM acquires a Suite API token with them, keeps it until it expires, and acquires a new one once after a 401
- And the password and the token appear in no log, page, API response, error message or Agent E2 fact
- And PCM itself keeps no sign-in of its own in release 1.0, behind the lab firewall

Test scenarios:
- T-LIVE-007a (anywhere, automated by pcm/l2/tests/test_live.py::test_token_reuse_and_renewal, to write). Data: the fake Suite API counting token requests, set to answer 401 once. Steps: load three pages; then trigger the 401. Expected: one token request for the three pages; exactly one new token request after the 401; the page then loads.
- T-LIVE-007b (anywhere, automated by pcm/l2/tests/test_live.py::test_no_secret_leak, to write). Data: a password and a token with a unique marker string. Steps: load every live page, force a login failure, and capture the server log, the responses and the facts sent to a stub Agent E2. Expected: the marker appears nowhere.
- T-LIVE-007c (lab, automated by tools/lab/Test-Live.ps1, to write). Data: the read-only credential. Steps: open the live page on the lab VM. Expected: data loads; the VCF Operations account used is the read-only one.

### R-LIVE-008 The lab certificate is checked

Why: an unchecked certificate lets anything on the network pretend to be the lab's VCF Operations.

Source: answer to Q-WS-34 (the lab CA pinned, no skip-verify).

- Given the CA file of the lab VCF Operations certificate is named in `/etc/pcm/pcm.env` in `PCM_VCFOPS_CA_FILE`
- When PCM connects to the Suite API
- Then it verifies the certificate against that file
- And a certificate that does not verify is a failed read (R-LIVE-011), with the reason "certificate not trusted"

Test scenarios:
- T-LIVE-008a (anywhere, automated by pcm/l2/tests/test_live.py::test_tls_pinned, to write). Data: the fake Suite API over TLS with a certificate from a test CA. Steps: start PCM with the test CA, then with another CA. Expected: data loads with the right CA; with the wrong CA the page shows the failed-read state with "certificate not trusted".
- T-LIVE-008b (lab, automated by tools/lab/Test-Live.ps1, to write). Steps: read one cluster with the lab CA file. Expected: the read succeeds with verification on.

### R-LIVE-009 PCM never writes to VCF Operations

Why: the work stays read-only against VCF Operations, and a demo must never change the lab it shows.

Source: answer to Q-WS-23 ("It can't store in the VCF Operations database"); SCOPE-5.

- Given the live demo
- When PCM calls the Suite API for any page or Agent E2 question
- Then every call is on a list of read calls: token acquire and release, GET calls, and the query calls that use POST only to read (for example the stats query)
- And no call creates, changes or deletes anything in VCF Operations

Test scenarios:
- T-LIVE-009a (anywhere, automated by pcm/l2/tests/test_live.py::test_read_calls_only, to write). Data: the fake Suite API logging method and path. Steps: load every live page and ask one Agent E2 question on each. Expected: every logged call is on the read list.
- T-LIVE-009b (lab, automated by tools/lab/Test-Live.ps1, to write). Steps: run the full lab test with the read-only account. Expected: no call is refused for lack of rights; the run passes.

### R-LIVE-010 Read through, with a 60-second cache and no store

Why: a store would be a second copy of VCF Operations' data that drifts from it; a short cache keeps pages fast without one (DESIGN-15).

Source: answer to Q-WS-30 ("Agree"); SCOPE-5.

- Given the live demo
- When the same data is asked for twice within 60 seconds
- Then PCM calls the Suite API once
- And after 60 seconds it calls again
- And PCM writes no metric value to its database, to disk or to any other store; the answer records of R-LIVE-035, which hold Agent E2's text, are the one exception

Test scenarios:
- T-LIVE-010a (anywhere, automated by pcm/l2/tests/test_live.py::test_cache_60s, to write). Data: the fake Suite API counting stats calls, and a fake clock in the cache. Steps: load a cluster's Performance tab at 0 s, 30 s and 61 s. Expected: two stats calls.
- T-LIVE-010b (anywhere, automated by pcm/l2/tests/test_live.py::test_no_metric_store, to write). Steps: load every live page, then read PCM's SQLite file and its data folder. Expected: no metric value from the fake is stored anywhere, outside the text of an answer record (R-LIVE-035).

### R-LIVE-011 A failed read shows "No data" for the whole page

Why: a page that shows some values after a failed read looks complete and is not (DESIGN-17).

Source: answer to Q-WS-27 ("If the data is stale, say no data"); [PCM D-041, wall behaviour: stale data turns grey, never green](https://github.com/e1-rahabok/private-cloud-manager/blob/main/decisions.md#d-041-noc-wall-behaviour); Q-WS-69 (a Suite API read stops after 10 seconds).

- Given the Suite API does not answer within 10 seconds, answers an HTTP error, refuses the login, or fails the certificate check
- When a live page loads
- Then every KPI, part and check value on it shows "No data", in grey
- And the page says that VCF Operations did not answer, with the reason and the time of the last good read
- And no last value, zero or green colour is shown

Test scenarios:
- T-LIVE-011a (anywhere, automated by pcm/l2/tests/live.page.test.mjs::test_failed_read, to write). Data: the fake Suite API set in turn to time out, answer 500, and refuse the login. Steps: load a cluster's Performance tab in each case. Expected: "No data" in grey for every figure; the reason and the last good read time are shown; no green and no 0.

## Inventory

### R-LIVE-012 The tree is VCF Operations' inventory, from the VCF instance down

Why: the audience knows VCF Operations' inventory, and PCM's tree must look like it.

Source: answer to Q-WS-25 ("Use the inventory from VCF Operations. It starts with VCF Instance"); SCOPE-5; Q-WS-66 (VCF Operations' VCF chain, without datacenters and folders); Q-WS-67 (compute only).

- Given the lab VCF Operations
- When the live L2 page opens
- Then its tree starts at the VCF instance objects and follows VCF Operations' own parent and child relationships down the VCF chain: VCF instance, workload domain, vCenter, cluster, ESXi host, VM
- And it shows no datacenter, no folder, no Guest OS node and no Storage, Network or Management view
- And each node shows the object's name as VCF Operations shows it, and its type
- And a node whose KPI has no data shows grey "No data"

Test scenarios:
- T-LIVE-012a (anywhere, automated by pcm/l2/tests/test_live.py::test_tree_from_relationships, to write). Data: the fake Suite API with one VCF instance, two clusters, three hosts and five VMs, linked as parent and child. Steps: open the tree and expand every node. Expected: the same hierarchy, names and types as the fake; a datacenter and a folder that the fake also holds are not shown; nothing else.
- T-LIVE-012b (lab, automated by tools/lab/live_reference.py and pcm/l2/tests/live.lab.test.mjs::test_tree, to write). Steps: the reference script lists the lab's VCF instance and its descendants through the Suite API; the page test expands the tree. Expected: the tree has the same objects under the same parents; a screenshot is saved.

### R-LIVE-013 An object's ID is its VCF Operations resource ID

Why: names repeat across vCenters, and only the resource ID names one object.

Source: answer to Q-WS-26 ("Yes"); SCOPE-5.

- Given any live object
- When it appears in a URL, an API response or an Agent E2 fact
- Then its ID is its VCF Operations resource ID, and its name is a separate field
- And a renamed object keeps its URL

Test scenarios:
- T-LIVE-013a (anywhere, automated by pcm/l2/tests/test_live.py::test_resource_id, to write). Data: the fake Suite API with two clusters of the same name under different vCenters. Steps: open each; then rename one in the fake. Expected: two distinct URLs by resource ID; after the rename the same URL opens the object with its new name.

## The values shown

### R-LIVE-014 PCM shows what the VCF vCommunity Adapter publishes

Why: PCM shows what the adapter publishes (SCOPE-5), so the audience can check any point in VCF Operations itself.

Source: answer to Q-WS-23 ("PCM can compute for UI purpose"); answer to Q-WS-27 ("PCM simply regurgitate the adapter"); SCOPE-5.

- Given a KPI, a part or a check value that the VCF vCommunity Adapter publishes on a live object
- When a live page shows it
- Then each point on the chart is the sample value VCF Operations returns for that key and time
- And PCM computes only what the page displays from those samples: Now, Worst, the percentile figure, the worst and percentile lines across objects, and the band colour
- And PCM never recomputes a KPI from its parts, nor a check result from its inputs

Test scenarios:
- T-LIVE-014a (anywhere, automated by pcm/l2/tests/test_live.py::test_values_passed_through, to write). Data: the fake Suite API with a Cluster Performance series that cannot be rebuilt from its parts. Steps: open the cluster's Performance tab. Expected: the chart's points equal the fake's KPI samples exactly.

### R-LIVE-015 A stale value shows "No data" at once

Why: a stale value looks like a current one, and the audience acts on it (DESIGN-17).

Source: answer to Q-WS-27 ("No need to wait 15 minutes"); SCOPE-5; Q-WS-64 (10 minutes for a value).

- Given VCF vCommunity Adapter collects every 5 minutes, and marks its own inputs stale after 10 minutes ([STALE_AFTER_MINUTES in ops_stats.py](https://github.com/e1-rahabok/PCM-Adapter/blob/main/Management%20Pack/app/utils/ops_stats.py#L32))
- When the newest sample of a key on an object is older than 10 minutes (one collection cycle plus a margin of one cycle) at the time PCM reads it
- Then Now shows "No data" in grey, with the time of the newest sample
- And the chart keeps the older points and draws nothing after the newest
- And the value is never shown as 0 or coloured green
- And with the 60-second cache (R-LIVE-010), a value is shown as stale at most 11 minutes after its newest sample

Test scenarios:
- T-LIVE-015a (anywhere, automated by pcm/l2/tests/test_live.py::test_stale_after_10_minutes, to write). Data: the fake Suite API with Cluster Performance samples ending 9 minutes ago on one cluster and 11 minutes ago on another. Steps: open both Performance tabs. Expected: the first shows its Now value; the second shows "No data" with the time of its newest sample.
- T-LIVE-015b (lab, automated by tools/lab/Test-Live.ps1, to write). Data: a powered-off lab VM, which the VCF vCommunity Adapter stops publishing for. Steps: open the VM's Performance tab. Expected: VM Performance's Now shows "No data" with the time of the last sample. If the lab has no powered-off VM, the scenario reports "not run" and asks the author for one; it never changes the lab itself.

### R-LIVE-016 Gaps stay visible

Why: a line drawn across a gap shows data that was never collected.

Source: answer to Q-WS-27; answer to Q-WS-30.

- Given a key whose samples in the window have a gap longer than one collection cycle
- When its chart is drawn
- Then the line breaks at the gap; nothing is drawn or filled in across it
- And the percentile figure is computed over the samples that exist, and the page states how many

Test scenarios:
- T-LIVE-016a (anywhere, automated by pcm/l2/tests/live.page.test.mjs::test_gap, to write). Data: the fake Suite API with a 24-hour series missing 40 minutes in the middle. Steps: open the chart. Expected: two separate line segments; the percentile uses 280 samples and says so.

### R-LIVE-017 A window longer than the history

Why: a window longer than the history must not pretend to cover it, and the maximum per slot keeps short peaks visible.

Source: answer to Q-WS-30 ("Agree": longer windows ask for the maximum per slot, draw nothing before the first point, say "Data from {date}").

- Given a window of 7 days, 30 days or 1 year
- When PCM reads a key for it
- Then it asks VCF Operations for the maximum of each slot (1 hour, 4 hours and 1 day, as in [l2.statistics](https://github.com/e1-rahabok/private-cloud-manager/blob/main/pcm/l2/spec/catalog.yaml#L241))
- And when the key's history starts inside the window, nothing is drawn before the first point, and the chart says "Data from {date}"

Test scenarios:
- T-LIVE-017a (anywhere, automated by pcm/l2/tests/test_live.py::test_long_window, to write). Data: the fake Suite API with 3 days of samples. Steps: open the 30-day window. Expected: the stats request asks for the maximum per 4-hour slot; the chart starts at the first point and says "Data from" that date.
- T-LIVE-017b (lab, automated by tools/lab/live_reference.py and pcm/l2/tests/live.lab.test.mjs::test_long_window, to write). Steps: open one lab cluster's 7-day window; the reference script reads the same key with the maximum per hour. Expected: the points match at whole percent.

### R-LIVE-018 Parts carry the catalog's names, found by key

Why: the author's knowledge names each part in Agent E2's catalog, and the key finds the row (Q-WS-1).

Source: answer to Q-WS-1 ("For key, adapter is correct. For name, Agent E2 is correct"); [SCOPE-7, VCF vCommunity Adapter changes and key and name ownership](https://github.com/e1-rahabok/private-cloud-workspace/blob/main/spec/brief.md).

- Given a part VCF vCommunity Adapter publishes under its key
- When a live page shows it
- Then its name is the name in Agent E2's catalog row that holds that key ([C1, KPI definitions](https://github.com/e1-rahabok/private-cloud-workspace/blob/main/spec/glossary.md#c1))
- And a key with no catalog row is shown under its key, and the key list check (R-LIVE-023) fails on it

Test scenarios:
- T-LIVE-018a (anywhere, automated by pcm/l2/tests/test_live.py::test_part_names_from_catalog, to write). Data: the fake Suite API publishing two catalog keys and one key the catalog lacks. Steps: open the Details fold. Expected: the two parts under their catalog names; the third under its key.
- T-LIVE-018b (lab, automated by pcm/l2/tests/live.lab.test.mjs::test_part_names, to write). Steps: open one lab cluster's Details folds. Expected: every part has its catalog name; a screenshot is saved.

### R-LIVE-019 Band colours follow the statistic of each key

Why: each limit holds for one statistic, so a 20-second peak judged by a 5-minute limit gets the wrong colour.

Source: answer to Q-WS-19 ("If a metric does not have the word peak, it's likely a 5-minute average"); SCOPE-7; Q-WS-81 (the catalog's interval is the rule).

- Given a part whose catalog row gives its interval as 20 seconds
- When its figures and chart are coloured
- Then the catalog's 20-second limits are used
- And a part whose row gives 5 minutes uses the catalog's 5-minute limits, whatever its name says
- And a part with no limits for its statistic stays uncoloured

Test scenarios:
- T-LIVE-019a (anywhere, automated by pcm/l2/tests/test_live.py::test_band_by_statistic, to write). Data: one 20-second part, one 5-minute part whose name says "peak", and one part with no limits for its interval, from a copy of the catalog. Steps: open the Details fold. Expected: the first two coloured by the matching limits; the third plain.

### R-LIVE-020 Parts an object does not have

Why: a part shown empty on an object that cannot have it reads as missing data.

Source: answer to Q-WS-28 ("we should fix them in the PCM Adapter"); SCOPE-7; Q-WS-68 (a part the object does not have is left out until the VCF vCommunity Adapter makes absent data explicit, after release 1.0 by [DESIGN-17](https://github.com/e1-rahabok/private-cloud-workspace/blob/main/spec/design/system.md)).

- Given a part key that VCF Operations does not hold for an object at all (for example a memory tiering key on a cluster without a tiered host)
- When the object's Details fold opens
- Then that part is left out, and the fold's heading counts the parts it shows
- And a part key the object holds, with no recent sample, shows "No data" (R-LIVE-015)

Test scenarios:
- T-LIVE-020a (anywhere, automated by pcm/l2/tests/test_live.py::test_absent_part, to write). Data: the fake Suite API with a cluster that holds 10 of the 12 Cluster Risk part keys, one of them with samples ending 30 minutes ago. Steps: open the Cluster Risk Details fold. Expected: 10 parts shown; the old one shows "No data".
- The same check on a cluster with tiered hosts is [R-LIVE-034](#r-live-034-tiered-clusters-show-their-tiering-parts), after release 1.0.

### R-LIVE-021 The Periodic Cluster Check as the adapter publishes it

Why: the check's verdict is the adapter's, and PCM recomputing it could give a different answer.

Source: answer to Q-WS-31 ("PCM gets from the PCM Adapter"); Q-WS-64 (30 minutes for a check result); [PCM D-094, the Capacity tab reads the check and never recomputes it](https://github.com/e1-rahabok/private-cloud-manager/blob/main/decisions.md#d-094-the-l2-capacity-tab-and-vcommunitys-capacity-model).

- Given a lab cluster with Periodic Cluster Check values for its latest window
- When its Capacity tab opens
- Then the verdict and the three check values are the published values of that window, with its window end
- And the rule shown is named by comparing published values with published closure levels; PCM decides nothing
- And when no value is published for a window that ended more than 30 minutes ago (the VCF vCommunity Adapter may publish a few cycles late), the page says "No check for the {period} to {end time}", never "Open"

Test scenarios:
- T-LIVE-021a (anywhere, automated by pcm/l2/tests/test_live.py::test_check_published, to write). Data: the fake Suite API with a check window ending 2 hours ago (Close for Business 1) and none for a window ending 40 minutes ago. Steps: open the Capacity tab. Expected: "No check" for the latest window; the strip shows the earlier window closed with its published values.
- T-LIVE-021b (lab, automated by tools/lab/live_reference.py and pcm/l2/tests/live.lab.test.mjs::test_check, to write). Steps: read the four check keys of one lab cluster through the Suite API; open its Capacity tab. Expected: the same verdict and values, with the same window end.

### R-LIVE-022 The check labels use the adapter's own settings

Why: the label must say what the check measured, and the adapter's settings are the only record of it.

Source: answer to Q-WS-31; [PCM D-095, which statistic, on which axis](https://github.com/e1-rahabok/private-cloud-manager/blob/main/decisions.md#d-095-statistics-over-time-and-across-objects).

- Given the Adapter Instance's Cluster Check Period, Cluster Check Time (UTC) and Cluster Check Worst Percent, made readable by the VCF vCommunity Adapter ([adapter.md](https://github.com/e1-rahabok/PCM-Adapter/blob/main/spec/requirements/adapter.md))
- When the Capacity tab labels a check value
- Then the label uses those settings, for example "5th percentile, 24 hours to 08:00 GMT+8"
- And when the settings cannot be read, the label omits the percentile rank and the period, and says "check settings not available"

Test scenarios:
- T-LIVE-022a (anywhere, automated by pcm/l2/tests/test_live.py::test_check_labels, to write). Data: the fake with period 12 hours, time 06:00 UTC and Worst Percent 10; then the fake with no settings. Steps: open the Capacity tab, viewer zone GMT+8. Expected: "10th percentile, 12 hours to 14:00 GMT+8" for Cluster Performance; then "check settings not available".
- T-LIVE-022b (lab, automated by tools/lab/Test-Live.ps1, to write). Steps: read the lab Adapter Instance's settings through the mechanism of the adapter's adapter.md; open one cluster's Capacity tab. Expected: the labels match the settings.

### R-LIVE-023 The key list comes from the adapter, confirmed on the lab

Why: PCM's pages read only keys that exist on the lab, and a key list from the code alone may name keys VCF Operations never shows.

Source: answer to Q-WS-29 ("You will need to get from a live environment"); [DESIGN-17](https://github.com/e1-rahabok/private-cloud-workspace/blob/main/spec/design/system.md) (PCM's key list comes from the adapter's module tables, and the lab read checks it); C2.

- Given the keys the VCF vCommunity Adapter declares in its module tables ([R-ADP-007](https://github.com/e1-rahabok/PCM-Adapter/blob/main/spec/requirements/adapter.md)), and the VCF Operations capacity keys PCM reads
- When the key tool runs
- Then it writes one file in PCM's specification, `pcm/l2/spec/vcf-operations-keys.yaml`, with each key, its object type, its unit and its catalog name, plus the adapter version and the date
- And on the lab, the same tool confirms that the cluster, host and VM objects hold each key ([R-ADP-019](https://github.com/e1-rahabok/PCM-Adapter/blob/main/spec/requirements/adapter.md))
- And every key PCM's live demo reads is in that file
- And the C2 check compares the file with the keys PCM reads and with what the VCF vCommunity Adapter says it publishes ([adapter.md](https://github.com/e1-rahabok/PCM-Adapter/blob/main/spec/requirements/adapter.md))

Test scenarios:
- T-LIVE-023a (lab, automated by tools/lab/live_keys.py, to write). Steps: run the tool from the adapter's module tables, then against the lab. Expected: the file lists at least the KPI score keys and their parts for cluster, host and VM; each is found on a lab object; it names the adapter version shown by validate.ps1.
- T-LIVE-023b (anywhere, automated by contract-checks/kpi_keys.py, to write). Data: the key file and PCM's catalog. Steps: run the check; then plant a key PCM reads that the file lacks. Expected: passes on the real files; fails and names the planted key.
- T-LIVE-023c (lab, automated by contract-checks/kpi_keys.py --lab, to write). Expected: each listed key has a sample newer than 10 minutes on at least one lab object, or is marked conditional by PCM-Adapter.

### R-LIVE-024 Cluster Performance matches VCF Operations

Why: the audience can open the same cluster in VCF Operations, and a number that differs there breaks the demo.

Source: answer to Q-WS-35 ("okay"); [PCM D-131, percentiles labelled by rank](https://github.com/e1-rahabok/private-cloud-manager/blob/main/decisions.md#d-131-percentile-labels-by-statistical-rank).

Milestone: M8, first slice.

- Given one lab cluster and the 24-hour window
- When its live Performance tab opens
- Then the API returns the window's start and end, aligned to 5 minutes
- And for that window, Now is the newest 5-minute sample of `vCommunity|Cluster Performance|Cluster Performance Score`, Worst is the lowest sample with its time, and the 5th percentile is taken by nearest rank over the samples
- And each equals the reference computed from the Suite API for the same window, at whole percent

Test scenarios:
- T-LIVE-024a (lab, automated by tools/lab/live_reference.py and pcm/l2/tests/live.lab.test.mjs::test_cluster_performance_matches, to write). Steps: open the tab; read its window from the API; the reference script reads the raw samples for that window and computes Now, Worst and the 5th percentile. Expected: all three equal at whole percent; Worst's time equal; a screenshot is saved.
- T-LIVE-024b (anywhere, automated by pcm/l2/tests/test_live.py::test_figures_nearest_rank, to write). Data: a fake series of 288 known samples. Expected: Now, Worst, its time and the 5th percentile equal the values computed by hand in the test.
- T-LIVE-024c (anywhere, automated by tools/lab/test_live_reference.py, to write). Data: the 288 samples of T-LIVE-024b, served by the fake Suite API. Steps: run the reference script on them. Expected: it prints the same hand-computed Now, Worst, its time and 5th percentile; the oracle of the lab tests is itself proved ([test-plan.md](../test-plan.md), section The oracle).

### R-LIVE-025 The other KPIs match VCF Operations

Why: the audience can open the same object in VCF Operations, and a number that differs there breaks the demo.

Source: answer to Q-WS-35; [PCM D-124, the four pages of release 1.0](https://github.com/e1-rahabok/private-cloud-manager/blob/main/decisions.md#d-124-suggested-questions-of-a-whole-page). Q-WS-63 (round 2) decided the page list.

Milestone: M8.

- Given the live Performance and Capacity tabs of a lab cluster, a lab ESXi host and a lab VM
- When they open on the 24-hour window
- Then Cluster Risk, Cluster Consumption, ESXi Performance, VM Performance and Guest OS Performance, and each of their parts, match the reference of R-LIVE-024
- And the percentile figure is the 5th where higher is better and the 95th where higher is worse

Test scenarios:
- T-LIVE-025a (lab, automated by tools/lab/live_reference.py and pcm/l2/tests/live.lab.test.mjs::test_all_kpis_match, to write). Steps: as T-LIVE-024a, for every KPI and part on the three objects. Expected: all equal at whole percent, or at the part's own decimals where its limits have decimals.

### R-LIVE-026 Lines across clusters agree with vSphere World

Why: vSphere World summarises the clusters, so its lines must be built from the scores the clusters show.

Source: answer to Q-WS-23; [PCM D-091, the Performance tab above the cluster](https://github.com/e1-rahabok/private-cloud-manager/blob/main/decisions.md#d-091-the-performance-tab-above-the-cluster).

Milestone: M8.

- Given every lab cluster is under the selected node
- When its Performance and Capacity tabs above the cluster open
- Then the worst and percentile lines are computed from each cluster's published score at each point
- And they equal VCF vCommunity Adapter's vSphere World metrics (Worst Cluster Performance, Worst 10 Percent Cluster Performance, Worst Cluster Risk, Worst 10 Percent Cluster Risk, Highest Cluster Utilization, Highest 10 Percent Cluster Utilization) at whole percent

Test scenarios:
- T-LIVE-026a (lab, automated by tools/lab/live_reference.py and pcm/l2/tests/live.lab.test.mjs::test_world_lines, to write). Steps: open the lab's VCF instance node; read the vSphere World keys for the same window. Expected: equal at whole percent at every point. If the lab has one cluster only, the scenario says so and still compares.

### R-LIVE-027 Capacity Remaining, Time Remaining and VM Remaining are read

Why: capacity remaining is VCF Operations' own model, and a second calculation in PCM would disagree with it.

Source: answer to Q-WS-20 ("yes": live mode reads what the synthetic demo shows as placeholders); [PCM D-100, the KPI first on the Performance and Capacity tabs](https://github.com/e1-rahabok/private-cloud-manager/blob/main/decisions.md#d-100-kpi-over-time-on-performance-and-capacity-tabs).

Milestone: M8.

- Given a lab VM, ESXi host or cluster
- When its live Capacity tab opens
- Then Capacity Remaining and Time Remaining (and VM Remaining on a host and a cluster) are VCF Operations' own values, from the keys in the key list (R-LIVE-023), with their time and the line "From VCF Operations, {time}"
- And a value VCF Operations does not hold shows "No data"; no placeholder is shown

Test scenarios:
- T-LIVE-027a (anywhere, automated by pcm/l2/tests/test_live.py::test_remaining, to write). Data: the fake with the three values on a cluster and none on a VM. Expected: the cluster shows the fake's values and the line; the VM shows "No data".
- T-LIVE-027b (lab, automated by tools/lab/live_reference.py and pcm/l2/tests/live.lab.test.mjs::test_remaining, to write). Expected: the page shows the same values as the Suite API.

## Agent E2 in the live demo

### R-LIVE-028 Agent E2 gets the live facts in the usual shapes

Why: Agent E2 answers on the facts it was built and graded on, so live facts must have the same shapes.

Source: answer to Q-WS-36 ("agree"); C3.

- Given a question asked in the Agent E2 panel of the live demo
- When PCM builds the facts
- Then they have the same fields and shapes as in the synthetic demo (the screen, the KPI series, the parts at the KPI's worst point, the parts once an hour, the page's KPI series for the suggested questions), filled only with live values from the same reads as the page
- And a fact with no data is sent with its value missing and marked "no data"; it is never dropped silently and never filled with a synthetic value
- And the list of facts each answer feature needs is the one in C3's specification

Test scenarios:
- T-LIVE-028a (anywhere, automated by pcm/l2/tests/test_live.py::test_agent_facts, to write). Data: the fake Suite API, with one part key stale; a stub Agent E2 that records the request. Steps: ask "Why the worst?" on Cluster Performance. Expected: the recorded facts have every field of the synthetic request; values equal the page's; the stale part is present and marked "no data".
- T-LIVE-028b (anywhere, automated by contract-checks/agent_e2_api.py, to extend). Data: a live-shaped request with one fact marked "no data". Expected: the real Agent E2 service in mock mode accepts it, and its answer says the fact is missing.

### R-LIVE-029 What the live facts never carry

Why: lab facts may go to the cloud model (SCOPE-5), and customer data must never.

Source: answer to Q-WS-39 ("yes no issue at all. It's just a lab"); answer to Q-WS-33.

- Given a question asked in the live demo
- When PCM sends the facts to Agent E2
- Then they carry lab object names and values, which may reach the cloud model
- And they never carry the VCF Operations password, token or URL
- And they carry no PCM scenario story, case, calendar or action record

Test scenarios:
- T-LIVE-029a (anywhere, automated by pcm/l2/tests/test_live.py::test_facts_clean, to write). Data: the marker password and token of T-LIVE-007b, and a calendar entry in PCM's database. Steps: ask one question on each live page. Expected: no marker, no Suite API URL and no calendar entry in any recorded request.

### R-LIVE-030 Agent E2 names the part that moved the KPI

Why: release 1.0 succeeds when Agent E2 explains a real lab KPI correctly (GOAL-4), and the part that moved the KPI is the first thing to explain.

Source: answer to Q-WS-35 (the worst part is the one that lost the most points at the worst point, under the adapter's scoring); Q-WS-70 (a quiet lab is accepted: Agent E2 then says no part pulled the KPI down); [GOAL-4, release 1.0 success](https://github.com/e1-rahabok/private-cloud-workspace/blob/main/spec/brief.md).

Milestone: M8, first slice.

- Given one lab cluster and the 24-hour window
- When the person asks Agent E2 "Why the worst?" on its Cluster Performance
- Then Agent E2's answer names, as the main cause, the part the reference identifies: the part that lost the most points at the KPI's worst point, scored by the VCF vCommunity Adapter's own scoring code, which the reference script imports and does not copy
- And when no part lost points, the answer says no part pulled the KPI down

Test scenarios:
- T-LIVE-030a (lab, automated by tools/lab/live_reference.py and pcm/l2/tests/live.lab.test.mjs::test_agent_worst_part, to write). Data: Agent E2 on the lab VM with the gateway key. Steps: the reference script scores every part at the worst point; the page test asks the question and reads the answer. Expected: the answer names the reference's part as the main cause; when the wording differs, the automatic grader of [SCOPE-6, Agent E2 in release 1.0](https://github.com/e1-rahabok/private-cloud-workspace/blob/main/spec/brief.md) judges it with one key point: the reference's part, named as the main cause.

## Tests and the synthetic demo

### R-LIVE-031 Lab tests run automatically from the laptop

Why: the lab is reached only from the author's laptop (CONSTRAINT-6), so lab tests must run there in one step, without manual work.

Source: answer to Q-WS-37 ("You forgot you have live access"); Q-WS-71 (the lab's VCF Operations version is read at sign-in and recorded in the workspace's [system design](https://github.com/e1-rahabok/private-cloud-workspace/blob/main/spec/design/system.md#lab), section Lab); [SCOPE-17, the lab build and lab tests from the laptop](https://github.com/e1-rahabok/private-cloud-workspace/blob/main/spec/brief.md); DESIGN-9.

- Given the author's laptop on the VPN, the read-only credential file in `$HOME\.secrets\`, and the live demo deployed on the lab VM
- When one command runs, `pwsh tools/lab/Test-Live.ps1` in PCM
- Then it runs VCF vCommunity Adapter's validate.ps1 first and stops with its result if the pack is not collecting
- And it runs every lab scenario of this file, writes a screenshot of each live page checked, and prints pass, fail or not run per scenario
- And it changes nothing in VCF Operations, vCenter or the lab VM's data
- And it prints the lab VCF Operations version read at sign-in (Q-WS-71)

Test scenarios:
- T-LIVE-031a (lab, automated by tools/lab/Test-Live.ps1, to write). Steps: run it. Expected: a result line per lab scenario; screenshots in one folder; the VCF Operations version printed and then written in the lab table of the workspace's [system design](https://github.com/e1-rahabok/private-cloud-workspace/blob/main/spec/design/system.md#lab); exit code 1 if any scenario failed.
- T-LIVE-031b (anywhere, automated by pcm/l2/tests/test_live.py::test_runner_reports_not_run, to write). Data: an unreachable address in place of the lab. Expected: every lab scenario reports "not run", and the command exits with failure.

### R-LIVE-032 The synthetic demo is unchanged

Why: the synthetic demo is the main demo (ASSUMPTION-1), and the live demo must not break it.

Source: answer to Q-WS-20 ("The synthetic remains as they are"); SCOPE-4.

- Given the live demo is added
- When the existing synthetic tests run (executive, noc, l2, capacity, store, definitions, and the page tests in [pcm/README.md](https://github.com/e1-rahabok/private-cloud-manager/blob/main/pcm/README.md))
- Then all pass, with no test or expected value changed

Test scenarios:
- T-LIVE-032a (anywhere, automated by the existing tests in every workspace's `tests/` folder). Steps: run every test listed in pcm/README.md on the branch that adds the live demo. Expected: all pass; `git diff` shows no change to any workspace's `spec/acceptance-tests.yaml` or `tests/` folder other than new live files.

### R-LIVE-033 A live page opens within 5 seconds

Why: a demo page that keeps the audience waiting loses them.

Source: Q-WS-69 (a page in under 5 seconds; a Suite API read stops after 10 seconds).

- Given the live demo on the lab VM and a Suite API that answers
- When a person opens a live tab, with PCM's 60-second cache empty
- Then the tab shows its figures within 5 seconds

Test scenarios:
- T-LIVE-033a (anywhere, automated by pcm/l2/tests/live.page.test.mjs::test_page_time, to write). Data: the fake Suite API answering each read after 300 milliseconds. Steps: open a cluster's Performance tab with an empty cache. Expected: the figures show within 5 seconds.
- T-LIVE-033b (lab, automated by tools/lab/Test-Live.ps1, to write). Steps: open one lab cluster's Performance and Capacity tabs with an empty cache. Expected: each shows its figures within 5 seconds.

### R-LIVE-034 Tiered clusters show their tiering parts

Why: the tiering parts can be shown only once the lab has tiered hosts (SCOPE-17).

Source: Q-WS-68; [SCOPE-17](https://github.com/e1-rahabok/private-cloud-workspace/blob/main/spec/brief.md) (the lab build for memory tiering comes after release 1.0).

Milestone: after release 1.0.

- Given the nested tiered cluster of [R-LAB-002](https://github.com/e1-rahabok/private-cloud-workspace/blob/main/spec/requirements/lab-build.md)
- When its Cluster Risk Details fold opens
- Then the tiering parts are shown with data

Test scenarios:
- T-LIVE-034a (lab, automated by pcm/l2/tests/live.lab.test.mjs::test_tiered_parts, to write). Data: the nested tiered cluster. Steps: open its Cluster Risk Details fold. Expected: the tiering parts are shown with data.

### R-LIVE-035 PCM keeps each Agent E2 answer with its trace and rating

Why: a wrong answer can be traced and fixed only while its question, answer, trace and rating are kept (DESIGN-13).

Source: Q-WS-61 (PCM and isvara.io store question, answer, trace ID and rating; Agent E2 keeps traces 30 days). PCM keeps a record for the 30 days its trace lives in Agent E2 ([R-E2-023](https://github.com/e1-rahabok/agent-e2/blob/main/project/requirements/answer-service.md#r-e2-023-every-answer-can-be-traced-for-30-days)), so every kept answer can be traced. It makes the one exception to SCOPE-5's "stores no metrics", which R-LIVE-010 states and SCOPE-5's status records.

Milestone: M8.

- Given an Agent E2 answer in the live demo
- When it is shown, and when the person rates it
- Then PCM's database keeps the question, the answer, Agent E2's `trace_id` and the rating, for 30 days

Test scenarios:
- T-LIVE-035a (anywhere, automated by pcm/l2/tests/test_live.py::test_answer_record, to write). Data: a stub Agent E2 answering with a trace ID. Steps: ask one question and rate it. Expected: one record with the four fields; with the clock moved 31 days on, it is gone.

### R-LIVE-036 The live demo runs end to end as the author shows it

Why: each lab scenario proves one page, but the audience sees one walk through the live demo; a step that leads nowhere, or a number that changes between two steps, breaks the demo even when every page passes on its own.

Source: answer to Q-PCM-3 (the author's live demo script, 16 steps: "Same structure and UI as the synthetic demo, except the data is live"; recorded in the workspace's [round 6](https://github.com/e1-rahabok/private-cloud-workspace/blob/main/spec/author-input/interview-round-6.md)); answer to Q-WS-37 ("You forgot you have live access"); [GOAL-4, release 1.0 success](https://github.com/e1-rahabok/private-cloud-workspace/blob/main/spec/brief.md); SCOPE-5. The steps are the live demo script in [demo/README.md](../../demo/README.md), section The live demo.

Milestone: M8.

- Given the live demo on the lab VM, the 24-hour window, and the demo cluster: the cluster named `demo_cluster` in `$HOME\.secrets\lab.json`, else the first cluster in the tree
- When the live rehearsal walks the script in a browser, from the demo drop-down, through the tree to the demo cluster
- Then the cluster opens on its Performance tab (R-LIVE-004)
- And on each page of the walk it opens Agent E2 from the top bar mark, then from every Agent E2 mark on the page, and asks every suggested question of each (R-LIVE-038, R-LIVE-039)
- And the pages of the walk, in order: the cluster's Performance tab; its Capacity tab; the first host in its list of hosts, worst first, on its Performance tab; the first VM of that host, worst first, on its Performance tab
- And each number on a page equals the reference script's value for the same object and window, and the same object shows the same value on every step that shows it
- And a screenshot of each page and of each answer is saved, as `demo/rehearse.mjs` does for the synthetic demo

Test scenarios:
- T-LIVE-036a (lab, automated by demo/rehearse.mjs --live, run as step 10 of tools/lab/Test-Live.ps1, to write). Data: the lab VCF Operations, the reference script, Agent E2 on the lab VM with the gateway key. Steps: walk the script. Expected: every step passes; one line per step and per question, with the answer's time and tokens; a screenshot per page and per answer in the run's folder.
- T-LIVE-036b (anywhere, automated by demo/rehearse.mjs --live against the fake Suite API and the stub Agent E2, to write). Data: the fake Suite API with one cluster, two hosts and three VMs. Steps: as 036a. Expected: the walk reaches each of the four pages by its links; every mark on them opens the panel and every suggested question reaches the stub with the context of the mark clicked.
- T-LIVE-036c (anywhere, automated by pcm/l2/tests/l2.page.test.mjs, LPG-31). Data: the synthetic demo and the stub Agent E2. Steps: on SG-S-01's Performance and Capacity tabs, sg-esx-110's Performance tab and sg-api-1617's Performance tab, open the panel from the top bar mark and from every Agent E2 mark, and click every suggested question. Expected: each mark opens the panel with one to three suggestions and its own context line; each click reaches the stub once, with the context of the mark clicked; each shows an answer. The synthetic UI is the live UI (R-LIVE-032), so this proves the walk's clicks before the lab.

### R-LIVE-037 The lab VM is reached only through TLS, from the VPN, and stays patched

Why: PCM has no sign-in in release 1.0, so the VPN is its only gate (ASSUMPTION-9); a plain-HTTP port would carry the live data unencrypted on the lab network, and an unpatched VM is the easiest way past the VPN (OWASP ASVS V9 and V14).

Source: ASSUMPTION-9 and DESIGN-24 (the security baseline, in the workspace's [system design](https://github.com/e1-rahabok/private-cloud-workspace/blob/main/spec/design/system.md)); DESIGN-25 (unattended upgrades on the lab VM); [deploy/README.md](../../deploy/README.md), section HTTPS with nginx, Close port 8080.

Milestone: M8.

- Given the lab VM that runs PCM and the Agent E2 service
- When a lab browser or another host on the network connects to it
- Then only port 443 (nginx, TLS) and SSH answer from the network
- And PCM listens on `127.0.0.1:8080` only (`PCM_HOST=127.0.0.1` in `/etc/pcm/pcm.env`), and the Agent E2 service on `127.0.0.1:8090` only
- And the VM's firewall accepts 443 and SSH only from the lab and VPN networks
- And `unattended-upgrades` installs security updates every day
- And no port of the VM answers from outside the VPN

Test scenarios:
- T-LIVE-037a (lab, automated by tools/lab/Test-Lab.ps1, to write). Steps: from the laptop on the VPN, connect to 443, 8080 and 8090 on the lab VM; on the VM, run `ss -ltn` and `systemctl is-enabled unattended-upgrades`. Expected: 443 answers with TLS; 8080 and 8090 refuse; `ss` lists 8080 and 8090 on `127.0.0.1` only; unattended upgrades are enabled.
- T-LIVE-037b (lab, manual once, recorded in the M8 pull request). Steps: with the VPN off, connect to 443 and SSH on the lab VM's address. Expected: neither answers.

### R-LIVE-038 The suggested questions fit the page and the card

Why: the author clicks every suggested question in front of the audience (Q-PCM-3, steps 6 and 9: "The default OOTB questions must be relevant"); a question about a situation the screen does not show, or about another object, tells the audience the assistant is not reading the page.

Source: answer to Q-PCM-3; D-124 and D-127 (the page's and the card's suggestions), in [pcm/l2/spec/pages/frame.md](../../pcm/l2/spec/pages/frame.md), section Suggested questions; Agent E2's rule in [harness/user_suggestions.py](https://github.com/e1-rahabok/agent-e2/blob/main/harness/user_suggestions.py) and its questions in [harness/user_suggestions.yaml](https://github.com/e1-rahabok/agent-e2/blob/main/harness/user_suggestions.yaml).

Milestone: M8.

- Given a page of the walk of R-LIVE-036 and its live KPI series
- When the panel opens from the top bar mark
- Then the suggestions come from Agent E2 (`source` service), not from the general fallback
- And the situation Agent E2 returns (level and movement) equals the one the reference script computes from the same series by the rule written in `user_suggestions.py`
- And each question is one that `user_suggestions.yaml` lists for that situation and that kind of object, with `{time}` the worst point's time as the page writes it
- And when the panel opens from a card's mark, the first question is Agent E2's showcase question for that card, or none; every figure it names equals the card's; the others are the card's own questions of frame.md
- And no question names another object or a KPI that is not on the page

Test scenarios:
- T-LIVE-038a (lab, automated by demo/rehearse.mjs --live with tools/lab/live_reference.py, to write). Steps: on each page of the walk, read the suggestions and the situation from `/api/l2/agent/suggest`; the reference computes the situation from its own reads. Expected: equal situations; every question from the situation's list; every figure in a showcase question equals the card's.
- T-LIVE-038b (anywhere, automated by pcm/l2/tests/test_live.py::test_suggest_live, to write). Data: the fake Suite API with a series falling all morning, and the real Agent E2 rule in mock mode. Expected: situation declining; the questions are the declining questions of the cluster.

### R-LIVE-039 Every suggested question gets a correct answer

Why: the author checks each answer in front of the audience (Q-PCM-3, step 7: "verifying their answer is correct"), and a confident wrong answer is the main risk (RISK-1).

Source: answer to Q-PCM-3; [GOAL-4 and RISK-1](https://github.com/e1-rahabok/private-cloud-workspace/blob/main/spec/brief.md); the grader of [R-E2-005](https://github.com/e1-rahabok/agent-e2/blob/main/project/requirements/answer-service.md#r-e2-005-an-automated-grader-scores-every-answer); R-LIVE-030 for the part that moved the KPI.

Milestone: M8.

- Given each suggested question asked in the walk of R-LIVE-036
- When its answer is shown
- Then the answer is an answer: not a clarifying question, not an error, and it arrives within Agent E2's job limit (R-E2-008)
- And each figure it states for the page's object (a KPI's Now, Worst, its time, the percentile figure, a part's value) equals the reference script's value at whole percent, or at the part's own decimals
- And it names the page's object, and no object of the synthetic demo
- And a question that asks why the KPI moved names the reference's part as the main cause, as R-LIVE-030 states
- And the grader scores it 2 or 3, given the question, the facts PCM sent, and key points written from the reference: the object, the level and movement, and the part where the question asks for a cause
- And a fact marked "no data" (R-LIVE-028) is said to be missing, and no value is given for it

Test scenarios:
- T-LIVE-039a (lab, automated by demo/rehearse.mjs --live with tools/lab/live_reference.py and Agent E2's grader, to write). Steps: for every answer of the walk, compare its figures with the reference, then grade it. Expected: every figure equal; every score 2 or 3; one line per answer with its score and the grader's reason. A score below 2 is a type of question that fails: it goes to agent-e2's [screen_answer_check.yaml](https://github.com/e1-rahabok/agent-e2/blob/main/benchmark/runner/screen_answer_check.yaml) with 20 wordings, by agent-e2's rule.
- T-LIVE-039b (lab, manual, at the M8 rehearsal). Steps: the author walks the script and rates every answer (R-LIVE-035). Expected: every rating is up; each rating down is reported with its question and answer, and treated as in 039a.

### R-LIVE-040 A failure of Agent E2 or the gateway during the demo

Why: the walk asks about 80 questions through the cloud gateway (81 on the synthetic demo, LPG-31) (SCOPE-5); one failed call must not end the demo or be mistaken for a pass.

Source: answer to Q-PCM-3 ("The answer is coming live from Vercel the AI gateway, just like in synthetic demo. No difference at all"); R-E2-020 (the waiting, not-responding and unavailable states); CONSTRAINT-1 (the gateway budget).

Milestone: M8.

- Given the live demo and Agent E2 on the lab VM
- When it runs
- Then Agent E2 uses the same service, model and gateway key as the synthetic demo, and `/api/l2/agent/health` reports the same model in both
- And when Agent E2 or the gateway cannot be reached, the panel says so (R-E2-020), the page and its numbers stay, and the next question can be asked
- And the rehearsal checks the health endpoint before the walk, reports every question after a failed call as NOT RUN, and never as a pass
- And the rehearsal prints the walk's model calls, tokens and cost, which the first lab run measures against the gateway budget

Test scenarios:
- T-LIVE-040a (anywhere, automated by pcm/l2/tests/l2.page.test.mjs, LPG-32). Data: the synthetic demo; the stub Agent E2 stopped after the first answer. Steps: ask a second question. Expected: the panel shows the unavailable state; the page's charts and figures are unchanged; after the stub restarts, the next question gets an answer.
- T-LIVE-040b (lab, automated by demo/rehearse.mjs --live, to write). Steps: run the walk with the gateway key removed from the Agent E2 service. Expected: the rehearsal stops at the health check and reports every question as NOT RUN.

## Changes to PCM's own specification

Each line is a change to make in private-cloud-manager in a later pull request. Nothing here is edited yet.

| File | Change |
|---|---|
| [decisions.md, D-076](https://github.com/e1-rahabok/private-cloud-manager/blob/main/decisions.md#d-076-model-client-and-gateway-for-agent-e2) and its [rationale](https://github.com/e1-rahabok/private-cloud-manager/blob/main/decisions.md#d-076-agent-e2-in-the-demo-through-vercel-ai-gateway) | Say that the live demo sends lab facts to the cloud model through the gateway (Q-WS-39), and that facts never carry the VCF Operations credential, token or URL. |
| [decisions.md](https://github.com/e1-rahabok/private-cloud-manager/blob/main/decisions.md) | Add a PCM decision for the live demo that points to SCOPE-5 and this file. |
| [decisions.md, D-062](https://github.com/e1-rahabok/private-cloud-manager/blob/main/decisions.md#d-062-checks-of-the-vcf-apis) | The VCF APIs are now checked against the lab VCF Operations; record its version. |
| [decisions.md, D-087](https://github.com/e1-rahabok/private-cloud-manager/blob/main/decisions.md#d-087-the-five-views-of-the-inventory-tree) | Add that the live demo's tree is VCF Operations' inventory from the VCF instance down (Q-WS-25). |
| [decisions.md, D-100 rationale](https://github.com/e1-rahabok/private-cloud-manager/blob/main/decisions.md#d-100-the-kpi-first-performance-and-capacity-tabs) and [D-106](https://github.com/e1-rahabok/private-cloud-manager/blob/main/decisions.md#d-106-the-details-fold-on-the-clusters-performance-tab) | "Release 1.0: placeholder values" becomes "synthetic demo: placeholder or PCM scenario story values; live demo: read from VCF Operations". |
| [pcm/core/design-notes/pcm-core.md, 3.2](https://github.com/e1-rahabok/private-cloud-manager/blob/main/pcm/core/design-notes/pcm-core.md#L46) | PCM reads every KPI, part and check value from the VCF vCommunity Adapter and computes only for display (Q-WS-23). |
| [pcm/core/design-notes/pcm-core.md, 3.3](https://github.com/e1-rahabok/private-cloud-manager/blob/main/pcm/core/design-notes/pcm-core.md#L67) | Release 1.0 stores no metrics; the live demo reads through with a 60-second cache (Q-WS-30). |
| [pcm/core/design-notes/pcm-core.md, 3.5](https://github.com/e1-rahabok/private-cloud-manager/blob/main/pcm/core/design-notes/pcm-core.md#L108) | Replace "two collection cycles" with the rule of R-LIVE-015 once confirmed. |
| [pcm/core/design-notes/pcm-core.md, 3.13](https://github.com/e1-rahabok/private-cloud-manager/blob/main/pcm/core/design-notes/pcm-core.md#L207) | The live demo is a separate demo, L2 only (Q-WS-20, Q-WS-22). |
| [pcm/l2/design-note.md, 3.2](https://github.com/e1-rahabok/private-cloud-manager/blob/main/pcm/l2/design-note.md#L97) | Fix the Compute path to match D-087, and add the live tree. |
| [pcm/l2/spec/catalog.yaml](https://github.com/e1-rahabok/private-cloud-manager/blob/main/pcm/l2/spec/catalog.yaml#L111) (L111, L264, L285) | Placeholders become synthetic-only; "PCM keeps its own history" becomes synthetic-only; add a `key` per part from the key list. |
| [pcm/core/spec/catalog/settings.yaml](https://github.com/e1-rahabok/private-cloud-manager/blob/main/pcm/core/spec/catalog/settings.yaml) | Add the live settings: the Suite API URL, user, password and CA file variable names, cache 60 s, stale after 10 minutes, check late after 30 minutes, read timeout 10 s. |
| `pcm/l2/spec/vcf-operations-keys.yaml` (new) | The key list from the adapter's module tables, confirmed on the lab (R-LIVE-023). |
| [pcm/l2/spec/pages/monitor.md](https://github.com/e1-rahabok/private-cloud-manager/blob/main/pcm/l2/spec/pages/monitor.md#L48) | The Details placeholder rule becomes synthetic-only; fix the stale band text and part counts at L45 and L46 (see D-108 and D-113). |
| [pcm/l2/spec/pages/frame.md](https://github.com/e1-rahabok/private-cloud-manager/blob/main/pcm/l2/spec/pages/frame.md) | Add the live frame: Monitor with Performance and Capacity tabs only, no class filter, the failed-read state. |
| [pcm/l2/spec/api.yaml](https://github.com/e1-rahabok/private-cloud-manager/blob/main/pcm/l2/spec/api.yaml#L6) | Add the live API prefix, the window start and end in responses, and the 400 for `now` and `enable`. |
| [pcm/executive/spec/api.yaml](https://github.com/e1-rahabok/private-cloud-manager/blob/main/pcm/executive/spec/api.yaml#L85) (L85, L101) | `now` is synthetic-only; the stale flag follows R-LIVE-015; the live source ID in `Meta.source`. |
| [pcm/core/spec/objects.yaml](https://github.com/e1-rahabok/private-cloud-manager/blob/main/pcm/core/spec/objects.yaml#L45) (L45, L47, L87) | A live object's ID is its resource ID; class of service and environment are synthetic-only. |
| [spec/README.md](https://github.com/e1-rahabok/private-cloud-manager/blob/main/spec/README.md#L49) | Add the live demo to the status table; move each verified assumption out of "to verify". |
| [pcm/README.md](https://github.com/e1-rahabok/private-cloud-manager/blob/main/pcm/README.md#L279) | Remove the gap "No VCF Operations connector in 1.0"; add the live tests. |
| [deploy/README.md](https://github.com/e1-rahabok/private-cloud-manager/blob/main/deploy/README.md#L3) and [deploy/pcm.env.example](https://github.com/e1-rahabok/private-cloud-manager/blob/main/deploy/pcm.env.example) | The live demo connects read-only to VCF Operations; add its variables to `pcm.env`. |
| [demo/README.md](https://github.com/e1-rahabok/private-cloud-manager/blob/main/demo/README.md#L21) | The drop-down has the live entry. The live demo script of R-LIVE-036 is in its section The live demo. |
| [tools/lab/Test-Lab.ps1](https://github.com/e1-rahabok/private-cloud-manager/blob/main/tools/lab/Test-Lab.ps1#L2) | Read the DPAPI files of DESIGN-9 in place of Windows Credential Manager (Q-WS-40). |

## Agent E2's progress on screen

### R-E2-020 PCM reads an Agent E2 job every 10 seconds

Why: the author accepts a 10-second wait between progress reads (ASSUMPTION-2), and reading more often only adds load.

Source: SCOPE-6 ("the user always sees that Agent E2 is still working"); answer to Q-WS-I3 ("how to inform user Agent E2 is not hung or dead?"); [ASSUMPTION-2](https://github.com/e1-rahabok/private-cloud-workspace/blob/main/spec/brief.md) (the author, 2026-11-27: "VMware Admin does not mind 10 seconds waiting as he knows this is not a general chat").

- Given PCM's live demo waiting on an Agent E2 job (R-E2-007)
- When the job is queued or running
- Then PCM reads `GET /v1/jobs/<id>` once every 10 seconds, and not more often
- And between reads, the time so far counts up every second in the browser, with no call to Agent E2
- And the screen shows the current stage as words a person reads, never the stage's code name
- And when `updated_at` is more than 60 seconds old, the screen says that Agent E2 is not responding and offers to try again
- And when the job fails, the screen shows the reason of R-E2-008; when Agent E2 cannot be reached, it says that Agent E2 is unavailable

Test scenarios:
- T-E2-020a (anywhere, automated in private-cloud-manager by `pcm/core/tests/agent_e2_job.test.mjs`, to write): a fake job endpoint that counts requests and runs a job for 60 seconds; expect at most 7 reads, the stage in words, and the answer at the end.
- T-E2-020b (anywhere, the same test): the fake stops changing `updated_at`; expect "not responding" on screen within 70 seconds.
- isvara.io's side is [R-ASK-002](https://github.com/e1-rahabok/isvara/blob/main/spec/requirements/ask.md#r-ask-002-the-visitor-sees-agent-e2-working), in M5.

## Questions for round two

The questions on this file, with their decisions, are in the [interview, round 2](https://github.com/e1-rahabok/private-cloud-workspace/blob/main/spec/author-input/interview-round-2.md): Q-WS-63 to Q-WS-71 (and Q-WS-57). None is open.
