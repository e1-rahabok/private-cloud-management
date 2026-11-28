# Specification structure

Status: draft for the author's review. Decisions proposed here move to [`decisions.md`](../../../decisions.md) once accepted.

The specification is the maintained artifact; AI writes all the code (D-010). This document sets how the specification is organised, so that an AI can build PCM from it and a test can prove each build right.

## 1. Design notes hold the why, `spec/` holds the what

- **What:**
  - A design note keeps the reasons: considerations, trade-offs, what was rejected. Each workspace has one (`design-note.md` in its folder); the notes that apply to every workspace are in `pcm/core/design-notes/` (this note is one).
  - A `spec/` folder keeps what to build: exact, testable, with no argument in it. Each workspace has one, and `pcm/core/spec/` holds what every workspace shares.
  - Every item in a `spec/` folder links to the decision (`D-nnn`) or design section it comes from.
- **Why:**
  - **The builder and the reviewer need different texts.**
    - An AI builder given the reasons alongside the rules may treat a rejected option as an option.
    - A human reviewer given only the rules cannot tell a deliberate choice from an accident.
  - **The two change at different speeds.** A threshold changes monthly. The reason for using the worst VM instead of the average does not change.
  - **The link keeps them honest.** A spec item with no decision behind it is a guess. A decision that no spec item uses is either not built yet or no longer needed.

## 2. One folder per workspace (D-133)

```text
spec/
  README.md              the specification's front page: where each part is, the rules for builders
  requirements/          the requirements of PCM's work, with their test scenarios
pcm/
  core/                  what every workspace uses
    design-notes/        PCM core, service levels, this note, synthetic ACME data
    spec/
      objects.yaml       the object model (PCM core, 3.1)
      database-schema.sql
      catalog/           settings, thresholds, configuration standards
      demo-data/         the estate and the PCM scenario stories of the synthetic ACME data
      visual-style.md    tokens, colour roles, components, chart rules
      acceptance-tests.yaml
  executive/  noc/  l2/  capacity/  docs_workspace/
    design-note.md
    spec/
      pages/             one file per page
      api.yaml           the workspace's part of the API contract (OpenAPI)
      catalog.yaml       definitions: KPIs, models, check rules, grouping rules, class of service
      vocabulary.yaml    the words the workspace uses and avoids
      acceptance-tests.yaml   PCM scenario story + "now" + expected result
      sops/, action-policies.yaml   catalog files only one workspace reads: the NOC's SOPs, L2's action policies
```

- **`objects.yaml`, catalog files, `demo-data/`**
  - Format: YAML
  - Why this format: They are data. L2 edits the catalog (D-045), and the generator reads the PCM scenario story file. YAML is read by people, by AI and by code without conversion, and git shows each change line by line.
- **`api.yaml`**
  - Format: OpenAPI
  - Why this format: The one contract that synthetic data and real collection both fill (PCM core, 3.13). It is a standard, so client and server code can be generated from it and checked against it.
- **`pages/`, `visual-style.md`, `README.md`**
  - Format: Markdown
  - Why this format: Pages and visuals need prose: layout, states, interactions. Markdown is what AI reads best.
- **`acceptance-tests.yaml`**
  - Format: YAML
  - Why this format: Each test is data: a PCM scenario story, a "now", an expected value. Data is easier to review than test code, and the author can add a test without writing code.

- **Why one folder per workspace:** a session that works on one workspace finds its whole context in one folder: its design note, its specification, its code and its tests (Q-WS-134).

## 3. Rules every spec file follows

### 3.1 Every page names its question, role and cadence (D-052)

- **What:** each page file starts with:

  ```yaml
  question: "When must we order more, and is it in the plan?"
  role: executive
  cadence: [weekly, monthly]
  decisions: [D-015, D-051, D-060]
  ```

  Each visual on the page repeats the same three fields. A page or visual without them is rejected before it is built.
- **Why:**
  - D-052 is only a rule if something checks it.
  - Putting the fields first makes the check mechanical: a test reads the header.

### 3.2 Catalog entries for every number

- **What:**
  - A page says "show `cluster.decision_date` for the earliest cluster group in the location".
  - It never says "run-out date minus lead time".
  - The formula lives once, in `catalog/`.
- **Why:**
  - One number, one definition (PCM core, 1).
  - If a page could hold a formula, the AI would build it into that page. The next page would get its own copy, and the two would drift on the next regeneration.

### 3.3 The states of every visual

- **What:** each visual lists its states:
  - normal (green)
  - each warning colour
  - **stale** (grey, "No data", D-041)
  - empty (nothing to show)
  - loading
  - error
- **Why:**
  - An AI builder implements what it is told and invents the rest.
  - The invented stale state is usually "show the last value". That is exactly the green-because-blind screen D-041 forbids.
  - Most demo failures happen in the states nobody specified.

### 3.4 Words are checked per workspace

- **What:** each workspace has a vocabulary list in `catalog/vocabulary/`:
  - Executive uses D-051.
  - L1 uses plain questions with scores from 0 to 100%.
  - L2 and Capacity use full technical terms in SP5 units (SP5, the author's framework of five pillars: availability, performance, security, capacity and value).

  A test scans the page text against the list.
- **Why:**
  - Vocabulary is part of the per-role design (D-011).
  - Without a test, terms leak across workspaces with each regeneration.

### 3.5 The wall's own rules and their tests

- **What:** `/noc/wall` must have:
  - no buttons, inputs or links;
  - a refresh every minute;
  - the fixed status strip;
  - grey for stale data.

  Tests check each one.
- **Why:** a wall rule broken once becomes a habit. An interactive element on a TV fails in the room, not in review.

## 4. Tests: three levels

- **Catalog**
  - Checks: The maths of each definition, against worked examples
  - Example: Host spec for Silver on 64 cores, 2.5 GHz, Hyper-Threading on: 28.5 VMs and 839 GB (SP5 host spec example)
  - Why this level exists: The numbers must be right before any page shows them. The SP5 worked examples are free, trusted test cases.
- **PCM scenario story**
  - Checks: End to end: generator, API, page, with a fixed "now" (D-067)
  - Example: C-1: SG-Silver's decision date is 4 weeks after "now", and it is at the top of the cluster list
  - Why this level exists: Proves that the four workspaces agree on the same objects (synthetic data design, 1).
- **Page**
  - Checks: The spec rules in section 3
  - Example: No avoided word on `/exec`; no interactive element on `/noc/wall`; every visual names a question
  - Why this level exists: The rules that make each workspace what it is.

- **Page tests side by side:** each page test owns its ports. No port is used by two tests, the servers and stubs they start included, so tests can run at the same time. A stub that cannot start ends its test, and the test stops the PCM server it started.
  - Why: the capacity page test's server and the L2 page test's stub Agent E2 both used port 8769. Run side by side, a test that found its port taken either stopped and left its PCM server running, or read the other test's server and waited out a 60-second timeout on each page.
- **What tests cannot check:** whether a page passes the 5-second test, or whether a PCM scenario story convinces the approval audience. That is the author's review.

## 5. The build loop

1. The specification changes. This is the only place anyone edits.
2. AI regenerates the affected code.
3. All tests run.
4. A failure is fixed in the specification or in the generation, **never by hand-editing code**.
5. The author reviews what tests cannot check.

- **Why no hand edits:**
  - A hand edit lives only in the code. The next regeneration removes it, and nobody knows it existed.
  - If a fix is worth keeping, it belongs in the specification.
- **Generated code is marked as generated.** In a workspace folder, `spec/` and the design note are the source. Every other file, the server code, `pages/` and `tests/`, opens with a GENERATED line that names the specification it comes from, so nobody mistakes it for the source.

## 6. Versioning

- The specification has one version, tagged in git, for each build that passes all tests.
- Catalog entries carry their own version (PCM core, 3.5), so a number on screen can be traced to the definition that produced it.
- **Why:**
  - "The number changed" has two possible causes: the estate or the definition.
  - Without versions on definitions, nobody can tell which one it was.

## 7. The first specification files

- Only what the Executive prototype needs (D-053):
  - `spec/README.md`
  - the objects and catalog entries the Executive page reads
  - the part of the API contract it calls
  - `pcm/executive/spec/pages/`
  - the visual style tokens from the mockup
  - PCM scenario stories E-1 to E-5 and the PCM scenario stories they depend on (C-1, C-6, N-4)
  - their tests
- **Why:**
  - Writing the full specification before building anything would guess at problems the first build would reveal for free.
  - Each workspace adds its part when its turn comes (D-053).
