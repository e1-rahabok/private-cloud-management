# Specification structure

Status: draft for the author's review. Decisions proposed here move to [`decisions.md`](../decisions.md) once accepted.

The specification is the maintained artifact; AI writes all the code (D-010). This document sets how the specification is organised, so that an AI can build PCM from it and a test can prove each build right.

## 1. Two folders: `design/` holds the why, `spec/` holds the what

- **What:**
  - `design/` (this folder) keeps the reasons: considerations, trade-offs, what was rejected.
  - `spec/` keeps what to build: exact, testable, with no argument in it.
  - Every item in `spec/` links to the decision (`D-nnn`) or design section it comes from.
- **Why:**
  - **The builder and the reviewer need different texts.**
    - An AI builder given the reasons alongside the rules may treat a rejected option as an option.
    - A human reviewer given only the rules cannot tell a deliberate choice from an accident.
  - **The two change at different speeds.** A threshold changes monthly. The reason for using the worst VM instead of the average does not change.
  - **The link keeps them honest.** A spec item with no decision behind it is a guess. A decision that no spec item uses is either not built yet or no longer needed.

## 2. Layout of `spec/`

```text
spec/
  README.md            how to build, run and test PCM from this specification
  objects/             the object model (PCM core, 3.1)
  catalog/             definitions: KPIs, models, thresholds, check rules,
                       action types and tiers, SOPs, grouping rules,
                       class of service, vocabulary lists
  api/                 the API contract (OpenAPI)
  design-system/       tokens, colour roles, components, chart rules
  workspaces/
    executive/         one file per page
    noc/
    l2/
    capacity/
    docs/
  data/                story file and generator rules for synthetic ACME data
  tests/               acceptance tests: story + "now" + expected result
```

| Folder | Format | Why this format |
|---|---|---|
| `objects/`, `catalog/`, `data/` | YAML | They are data. L2 edits the catalog (D-045), and the generator reads the story file. YAML is read by people, by AI and by code without conversion, and git shows each change line by line. |
| `api/` | OpenAPI | The one contract that synthetic data and real collection both fill (PCM core, 3.13). It is a standard, so client and server code can be generated from it and checked against it. |
| `workspaces/`, `design-system/`, `README.md` | Markdown | Pages and visuals need prose: layout, states, interactions. Markdown is what AI reads best. |
| `tests/` | YAML | Each test is data: a story, a "now", an expected value. Data is easier to review than test code, and the author can add a test without writing code. |

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

### 3.2 A page never defines a number; it names a catalog entry

- **What:**
  - A page says "show `cluster.decision_date` for the earliest cluster group in the location".
  - It never says "run-out date minus lead time".
  - The formula lives once, in `catalog/`.
- **Why:**
  - One number, one definition (PCM core, 1).
  - If a page could hold a formula, the AI would build it into that page. The next page would get its own copy, and the two would drift on the next regeneration.

### 3.3 Every state is specified, not only the normal one

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
  - L2 and Capacity use full technical terms in SP5 units.

  A test scans the page text against the list.
- **Why:**
  - Vocabulary is part of the per-role design (D-011).
  - Without a test, terms leak across workspaces with each regeneration.

### 3.5 The wall has its own rules, and they are tested

- **What:** `/noc/wall` must have:
  - no buttons, inputs or links;
  - a refresh every minute;
  - the fixed status strip;
  - grey for stale data.

  Tests check each one.
- **Why:** a wall rule broken once becomes a habit. An interactive element on a TV fails in the room, not in review.

## 4. Tests: three levels

| Level | Checks | Example | Why this level exists |
|---|---|---|---|
| Catalog | The maths of each definition, against worked examples | Host spec for Silver on 64 cores, 2.5 GHz, Hyper-Threading on: 28.5 VMs and 839 GB (SP5 host spec example) | The numbers must be right before any page shows them. The SP5 worked examples are free, trusted test cases. |
| Story | End to end: generator, API, page, with a fixed "now" (D-067) | C-1: SG-Silver's decision date is 4 weeks after "now", and it is at the top of the cluster list | Proves that the four workspaces agree on the same objects (synthetic data design, 1). |
| Page | The spec rules in section 3 | No avoided word on `/exec`; no interactive element on `/noc/wall`; every visual names a question | The rules that make each workspace what it is. |

- **What tests cannot check:** whether a page passes the 5-second test, or whether a story convinces the approval audience. That is the author's review.

## 5. The build loop

1. The specification changes. This is the only place anyone edits.
2. AI regenerates the affected code.
3. All tests run.
4. A failure is fixed in the specification or in the generation, **never by hand-editing code**.
5. The author reviews what tests cannot check.

- **Why no hand edits:**
  - A hand edit lives only in the code. The next regeneration removes it, and nobody knows it existed.
  - If a fix is worth keeping, it belongs in the specification.
- **Generated code is marked as generated.** It sits in its own folder, so nobody mistakes it for the source.

## 6. Versioning

- The specification has one version, tagged in git, for each build that passes all tests.
- Catalog entries carry their own version (PCM core, 3.5), so a number on screen can be traced to the definition that produced it.
- **Why:**
  - "The number changed" has two possible causes: the estate or the definition.
  - Without versions on definitions, nobody can tell which one it was.

## 7. What is written first

- Only what the Executive prototype needs (D-053):
  - `spec/README.md`
  - the objects and catalog entries the Executive page reads
  - the part of the API contract it calls
  - `spec/workspaces/executive/`
  - the design system tokens from the mockup
  - stories E-1 to E-5 and the stories they depend on (C-1, C-6, N-4)
  - their tests
- **Why:**
  - Writing the full specification before building anything would guess at problems the first build would reveal for free.
  - Each workspace adds its part when its turn comes (D-053).
