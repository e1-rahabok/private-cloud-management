# PCM core

Status: draft for the author's review. Decisions proposed here move to [`decisions.md`](../decisions.md) once accepted.

The core is everything the four workspaces share: data, definitions, engines, identity, and Agent E2. Workspaces have no menu in common (D-011), but they must share the same numbers. That sharing happens here.

## 1. Principle: one number, one definition, one place

- **What:** every KPI, model, threshold and rule is defined once, in the core.
  - NOC, L2, Capacity, Executive and Agent E2 all read the same definition.
  - No workspace computes its own version of a number.
- **Why:**
  - Trust breaks the first time two screens disagree. Example: the CIO sees "cluster group runs out in 140 days" while the Capacity team sees 95. After that, both numbers are doubted, and the meeting is spent reconciling instead of deciding.
  - The specification is what is maintained (D-010). A number defined in four places drifts in four directions on each regeneration.

## 2. Layers

| Layer | Holds | Owner |
|---|---|---|
| Sources | VCF Operations (one or many), VCF Operations for Logs, vCenter, NSX, SDDC Manager (read only), VMware Live Site Recovery, VCF Automation. Connectors: ITSM (read: approved change windows, D-077; write after the fact, D-025), CMDB, email (D-003). Migration sources: OpenShift (D-023). | Outside PCM |
| Collection | Pulls data from each source, per region | PCM |
| Store | PCM's own database (D-006) | PCM |
| Catalog | Definitions of KPIs, models, thresholds, check rules, SOPs, action types | PCM; edited by L2 (D-045) |
| Engines | Check, action, forecast, notification | PCM |
| Registers | Business calendar, demand register, goals, decisions | PCM; edited by roles |
| API | One read and act interface, with role permissions | PCM |
| Workspaces | NOC, L2, Capacity, Executive, Docs | PCM |
| Agent E2 | Uses the API with the permissions of the human who asked (D-050) | PCM |

## 3. Design considerations

### 3.1 The object model is VMware's, not vendor-neutral

- **What:** the objects are VCF objects:
  - VCF instance, workload domain, vCenter, cluster, ESXi host, VM, Guest OS;
  - datastore, vSAN cluster;
  - distributed switch, NSX Edge.

  Competitor platforms appear only as migration sources, in a separate model (D-023).
- **Why:**
  - Early in this project I argued for a vendor-neutral model. D-023 and D-034 make that wrong: PCM manages VMware only.
  - A neutral model would add a translation layer to every metric and every rule, for platforms PCM will never manage. That is cost with no benefit.
  - VMware's own concepts (HA admission control, DRS, the VM versus Guest OS boundary) are what the SP5 rules are written in. Abstracting them away would hide the very mechanisms the rules depend on.
  - Migration sources need only inventory and sizing (CPU, memory, disk, network, and the growth of each). That fits a small separate model.

### 3.2 PCM computes the SP5 models itself

- **What:** PCM computes the SP5 models from raw metrics, in the core, from definitions in the catalog:
  - VM Performance (%)
  - ESXi Performance (%)
  - Cluster Performance (%), Cluster Risk (%), Cluster Consumption (%)
  - Stop Provisioning
  - idle, oversized and unused VM
  - capacity remaining and time remaining

  VCF Operations supplies the raw metrics. It does not supply the verdicts.
- **Why:**
  - **The same definition across many VCF Operations instances.**
    - With super metrics in each VCF Operations, a global estate ends up with different versions in different regions.
    - Federation (D-009) then compares numbers that mean different things.
  - **Capacity needs more history than VCF Operations keeps.** Its forecast reads at most 90 days (Capacity design, 3.5).
  - **Cost: VCF Operations computes a cost per VM. D-060 says there is no VM cost.**
    - PCM does not use the VCF Operations cost engine.
    - It uses its own model: product, service, people, with unit cost per thread (D-061).
  - **The definitions are part of the specification.** They are versioned, tested and regenerated with it (D-010).

### 3.3 Store peaks, not averages, and keep the history

- **What:**

  | Data | Resolution | Kept |
  |---|---|---|
  | Curated metrics per object | 5 minutes, holding the **20-second peak** of each interval | 45 days |
  | Rollups | 1 hour and 1 day, each keeping max, 95th percentile and average | 13 months for 1 hour; 5 years for 1 day |
  | Model results (KPIs, verdicts) | Same as their inputs | Same as the rollups |
  | Events and log findings | As they arrive | 13 months |
  | Action history (3.7) | As they happen | 13 months. The audit log as a compliance record comes in phase 2 (D-063). |

- **Why:**
  - **A rollup that keeps only the average destroys the signal.**
    - SP5: a few seconds of spike vanish in 300 seconds of average.
    - Performance reads the 20-second peak. An hourly average of 5-minute averages shows nothing.
  - **13 months of hourly data** puts last year's peak in this year's forecast (Capacity design, 3.5).
  - **5 years of daily data** matches the depreciation period. The monthly review compares against goals (D-043).
  - **A curated set, not everything.** The models need a small set per object (SP5 "it is on my court" lists about 20 per VM).
    - At 100,000 VMs × 20 metrics × 288 intervals a day, that is about 576 million points a day.
    - That is heavy but feasible for a time-series database.
    - Collecting every metric would multiply the load on VCF Operations and on PCM for numbers no model reads.

### 3.4 Detail on demand, not stored

- **What:** detailed data is fetched from the source when L2 opens an investigation. It is not stored. Examples:
  - per-second data;
  - per-instance metrics such as each vCPU or virtual disk;
  - full log searches.
- **Why:**
  - SP5: troubleshooting needs per-second data only for the object in question, and only when it changes the fix.
  - Storing it for every object would cost far more than it returns.
  - The federation prototype already uses this pattern: a live pass-through to the source instance.

### 3.5 Every number carries where it came from and how old it is

- **What:** every value in the API carries:
  - its source (which VCF Operations, which vCenter);
  - its time;
  - its definition version in the catalog.

  A value older than two collection cycles is marked stale. Workspaces show stale data as grey, never as green (D-041).
- **Why:**
  - **The most dangerous screen is green because it is blind.** A collector that stopped, or a VCF Operations instance that did not answer, must show as missing data, not as a healthy estate.
  - **The definition version answers "why did this number change?"** Sometimes the estate changed. Sometimes the definition did. The two must be told apart.

### 3.6 The catalog is data that L2 edits, under version control

- **What:** the catalog holds the definitions of:
  - KPIs and thresholds;
  - check rules;
  - SOPs and the action types they contain;
  - class of service.

  L2 edits it (D-045). Every change is versioned. A threshold change is replayed against the last 30 days before it is published (L2 design, 3.9).
- **Why:**
  - The rules change more often than the code. Making them data lets L2 tune them without regenerating PCM.
  - **Start from the Agent E2 threshold catalog.** It already holds the SP5 values with their sources. One catalog serves both PCM and Agent E2, so an explanation from Agent E2 never contradicts a number PCM shows.

### 3.7 The action engine is the only way to change anything

- **What:** every change PCM makes goes through one engine. A change can come from an L1 SOP button, an L2 approval, an automatic rule, or Agent E2. For each one, the engine:
  1. reads the action type's policy (D-029, D-079): its tier and its guardrails, at its current version;
  2. checks the guardrails; a run that breaks one does not run and becomes a proposal for a person:
     - the blast radius, for example no more than N VMs per cluster per hour;
     - the time: maintenance windows, close weeks;
     - the class of service and environment of the target;
  3. runs the action against vCenter or NSX with a service account that has only the rights for that action type;
  4. sets an expiry if the action is temporary, and undoes it at expiry (D-040: limits on villain VMs);
  5. writes the action history: what, which object, the actor, the accountable party (the human who ordered it, or for an automatic run the policy owner and version, D-050), why, before and after. This is an operational record in 1.0. The audit log as a compliance record is phase 2 (D-063);
  6. optionally, sends a record to ITSM after the fact (D-025).
- **Why:**
  - **One path means one place to audit and one place to stop.** If there are two paths, the second one is where the 03:00 incident comes from.
  - **Service accounts scoped per action type.** A compromised PCM must not mean a compromised estate. PCM holds the keys to every vCenter, so it is the most valuable target in the private cloud.
  - **Expiry is enforced by the engine, not remembered by a person.** Forgotten temporary settings are a classic cause of slowness that appears months later.

### 3.8 Registers hold what is not in any computer

- **What:** four registers, each with an owner:

  | Register | Owner | Read by |
  |---|---|---|
  | Business calendar (L2 design, 3.6) | L2 | Check engine, Agent E2 |
  | Demand register (Capacity design, 3.6) | Capacity | Forecast engine |
  | Goals (D-043) | Monthly review | Executive, monthly review |
  | Decisions and owners (D-043) | Monthly review | Next month's review |

- **Why:**
  - D-031 gives the reason three shifts of people remain: not all operational context is in a computer.
  - The registers are where people put that context, so that the engines and Agent E2 can use it.
  - Without them, the context lives in one senior engineer's head, which fails the SP5 holiday test.

### 3.9 Federation: one PCM, reading through VCF Operations (D-064)

- **What:**
  - One PCM per enterprise.
  - PCM has no collectors of its own. It reads from each region's VCF Operations, which already runs a collector (cloud proxy) in each region.
  - PCM talks directly to vCenter and NSX only for actions (D-025) and for the few reads VCF Operations does not hold.
  - Each VCF Operations instance has its own circuit breaker:
    - after repeated failures, PCM stops calling the instance for a while;
    - the instance is marked degraded;
    - its data shows as stale.
- **Why:**
  - **No duplicate collection.** VCF Operations already collects close to the source in each region. A second collector would double the API load on every vCenter and add a component to install, patch and secure in every region.
  - **One PCM.** The CIO sees one estate (Executive design, 4.9), and the NOC sees one wall.
  - **Reuse from the federation prototype.**
    - Reused: the API client for VCF Operations (two authentication methods, delta pulls by watermark, the circuit breaker).
    - Not reused: its storage and polling loop, which a large estate would outgrow.

### 3.10 Identity and access

- **What:**
  - Sign-in through the customer's identity provider (single sign-on).
  - Roles map to workspaces: NOC, L2, Capacity, Executive.
  - Access to the source systems is held only by PCM's service accounts. Users of PCM do not log in to vCenter through PCM (D-040).
  - Agent E2 has its own ID and always acts for a named human (D-050).
- **Why:**
  - **Least privilege by design.** The role sets what a person may see and do. The service account sets what PCM may do. The two are checked separately.
  - **The action history can always name a person.** This holds even when the actor was Agent E2.

### 3.11 PCM watches itself

- **What:**
  - PCM checks its own health: its connections to each VCF Operations, its store, its engines.
  - The NOC wall shows PCM's own state.
  - If PCM itself is down, the wall says so plainly, and the NOC SOP falls back to the native VCF Operations screens.
- **Why:**
  - Once the NOC runs on PCM, PCM is critical infrastructure.
  - An outage of the monitoring layer must never look like a quiet night.

### 3.12 Agent E2 uses the same API as everyone

- **What:**
  - Agent E2 reads and acts only through the PCM API.
  - It uses the permissions of the human it acts for (D-050).
  - Its knowledge comes from the knowledge base and the catalog. Its live facts come from the API.
- **Why:**
  - **No hidden access.** If Agent E2 had its own way into vCenter, the action engine's guarantees (3.7) would not hold.
  - **One source of truth.** Agent E2 quotes the same numbers the workspace shows.

### 3.13 The specification is the source; the prototype reads synthetic data through the same API

- **What:**
  - The specification holds the catalog, the API contract, the page specs and the acceptance tests (D-010).
  - The prototype serves synthetic ACME data (D-018) through the same API contract that real collection will fill later.
- **Why:**
  - **The prototype then proves the real design, not a mockup.** Switching to the lab VCF 9.1 (D-018) replaces only the collection layer.
  - **The acceptance tests run against fixed synthetic data.** Expected numbers are known in advance, so each regeneration can be checked automatically.

## 4. Biggest risk: what the VCF APIs really expose

- Several designs depend on data whose API support has not been verified:
  - the 20-second peak metrics;
  - log queries in VCF Operations for Logs;
  - site recovery test results;
  - VCF Automation request timestamps;
  - the settings PCM must change through vCenter and NSX.
- **Decided (D-062):** the check waits for the live VCF 9.1 system the author will provide.
  - Until then, the prototype runs on synthetic data behind the same API contract (3.13), so nothing built now depends on the answer.
  - Each assumption above is listed in the specification as "to verify on the live system".
- **Why it is still listed:** a design that depends on an API that does not exist fails at the worst time, after approval and during the build. Listing the assumptions keeps them visible until the live check.

## 5. Technology choice is deferred

- The database, the language and the UI framework are not chosen here.
- The prototype runs on synthetic data and needs none of them at scale.
- The choice is made once the API check (section 4) shows the real data volumes and access patterns.
- Rule for the choice: boring, proven, easy for AI to generate and for customers to run on premises (D-004). For example, a well-known open-source relational database with a time-series extension, before anything exotic.

## 6. Settled questions

- Data residency: beyond 1.0. Release 1.0 runs one central PCM (D-066). The later option keeps detailed data in its region and sends only model results to the central PCM.
