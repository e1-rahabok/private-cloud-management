-- PCM prototype database (D-080). Plain SQL that ports to the product database (D-006, PCM core 3.9).
-- Holds only what people and policies DO. Synthetic metrics are generated from "now" (D-067) and never stored.
-- GENERATORS: keep types to TEXT, INTEGER and REAL; times are ISO 8601 text with an offset.

-- The action record: evidence of every action, by whom, under which policy (D-050, D-063, D-079).
-- Append-only: an audit record that can be changed is not evidence.
CREATE TABLE IF NOT EXISTS action_record (
  seq          INTEGER PRIMARY KEY AUTOINCREMENT,
  at           TEXT NOT NULL,
  action       TEXT NOT NULL,
  target       TEXT NOT NULL,
  incident     TEXT,
  actor_agent  TEXT,               -- the agent or policy engine that ran it, if any
  actor_human  TEXT NOT NULL,      -- the person, or the policy owner and version, accountable for it
  reason       TEXT,
  before       TEXT,
  after        TEXT,
  expires_at   TEXT
);
CREATE TRIGGER IF NOT EXISTS action_record_no_update BEFORE UPDATE ON action_record
BEGIN SELECT RAISE(ABORT, 'action_record is append-only'); END;
CREATE TRIGGER IF NOT EXISTS action_record_no_delete BEFORE DELETE ON action_record
BEGIN SELECT RAISE(ABORT, 'action_record is append-only'); END;

-- The demand register (Capacity design, 3.6): demand the data cannot show yet.
CREATE TABLE IF NOT EXISTS demand_register (
  id               TEXT PRIMARY KEY,
  kind             TEXT NOT NULL CHECK (kind IN ('project', 'migration', 'dr', 'growth')),
  source           TEXT NOT NULL DEFAULT '',
  cluster_group    TEXT NOT NULL,
  date             TEXT NOT NULL,
  added            TEXT NOT NULL,
  owner            TEXT NOT NULL CHECK (owner <> ''),
  compute_threads  REAL NOT NULL DEFAULT 0 CHECK (compute_threads >= 0),
  memory_gb        REAL NOT NULL DEFAULT 0 CHECK (memory_gb >= 0),
  storage_tb       REAL NOT NULL DEFAULT 0 CHECK (storage_tb >= 0),
  CHECK (compute_threads + memory_gb + storage_tb > 0)
);

-- Decisions of the monthly review (D-043): what, owner and due date, all required.
-- Done marks live in workflow state, for planted and stored decisions alike.
CREATE TABLE IF NOT EXISTS team_decision (
  id     TEXT PRIMARY KEY,
  made   TEXT NOT NULL,
  what   TEXT NOT NULL CHECK (what <> ''),
  owner  TEXT NOT NULL CHECK (owner <> ''),
  due    TEXT NOT NULL CHECK (due <> ''),
  by     TEXT NOT NULL
);

-- Workflow state: acknowledgements, escalations, closures, proposals, published policies and thresholds,
-- calendar entries, limits. One JSON document per name. A prototype shortcut: the product gets one table each.
CREATE TABLE IF NOT EXISTS workflow_state (
  workspace  TEXT NOT NULL,
  name       TEXT NOT NULL,
  value      TEXT NOT NULL,
  PRIMARY KEY (workspace, name)
);
