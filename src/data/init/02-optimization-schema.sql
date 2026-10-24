-- =============================================================================
-- IPD Boeing Group 1 — Optimization Schema
-- Auto-executed by the PostgreSQL container on first start.
-- =============================================================================

-- ---------------------------------------------------------------------------
-- simulation_runs
-- One row per Run Simulation click. Stores solver config and opt params.
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS simulation_runs (
    id              SERIAL PRIMARY KEY,
    solver          TEXT        NOT NULL CHECK (solver IN ('classical', 'quantum')),
    security_weight INTEGER     NOT NULL DEFAULT 50 CHECK (security_weight BETWEEN 0 AND 100),
    cost_weight     INTEGER     NOT NULL DEFAULT 50 CHECK (cost_weight     BETWEEN 0 AND 100),
    bandwidth_weight INTEGER    NOT NULL DEFAULT 50 CHECK (bandwidth_weight BETWEEN 0 AND 100),
    risk_threshold  INTEGER     NOT NULL DEFAULT 30 CHECK (risk_threshold  BETWEEN 0 AND 100),
    status          TEXT        NOT NULL DEFAULT 'pending'
                                CHECK (status IN ('pending', 'running', 'success', 'fallback', 'error')),
    started_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    completed_at    TIMESTAMPTZ,
    error_message   TEXT
);

-- ---------------------------------------------------------------------------
-- simulation_results
-- Detailed outcome of a run: backend used, shot counts, execution time.
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS simulation_results (
    id              SERIAL PRIMARY KEY,
    run_id          INTEGER     NOT NULL REFERENCES simulation_runs(id) ON DELETE CASCADE,
    backend         TEXT        NOT NULL,   -- e.g. "aer_simulator" or "ibm_brisbane"
    used_ibm        BOOLEAN     NOT NULL DEFAULT FALSE,
    shots           INTEGER,
    counts          JSONB,                  -- raw measurement counts {"00": 536, "11": 488}
    execution_ms    INTEGER,                -- wall-clock time for the circuit run
    recorded_at     TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- ---------------------------------------------------------------------------
-- network_snapshots
-- JSON snapshot of the Cytoscape graph at the time of the run.
-- Lets users reconstruct exactly what topology produced a given result.
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS network_snapshots (
    id              SERIAL PRIMARY KEY,
    run_id          INTEGER     NOT NULL REFERENCES simulation_runs(id) ON DELETE CASCADE,
    nodes           JSONB       NOT NULL DEFAULT '[]',
    edges           JSONB       NOT NULL DEFAULT '[]',
    node_count      INTEGER     GENERATED ALWAYS AS (jsonb_array_length(nodes)) STORED,
    edge_count      INTEGER     GENERATED ALWAYS AS (jsonb_array_length(edges)) STORED,
    captured_at     TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- ---------------------------------------------------------------------------
-- simulation_logs
-- Per-step progress messages broadcast via SSE, also persisted here.
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS simulation_logs (
    id              SERIAL PRIMARY KEY,
    run_id          INTEGER     NOT NULL REFERENCES simulation_runs(id) ON DELETE CASCADE,
    step            INTEGER,
    total_steps     INTEGER,
    message         TEXT        NOT NULL,
    logged_at       TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- ---------------------------------------------------------------------------
-- Indexes for common query patterns
-- ---------------------------------------------------------------------------
CREATE INDEX IF NOT EXISTS idx_runs_started_at      ON simulation_runs(started_at DESC);
CREATE INDEX IF NOT EXISTS idx_results_run_id       ON simulation_results(run_id);
CREATE INDEX IF NOT EXISTS idx_snapshots_run_id     ON network_snapshots(run_id);
CREATE INDEX IF NOT EXISTS idx_logs_run_id_step     ON simulation_logs(run_id, step);

-- ---------------------------------------------------------------------------
-- Confirmation
-- ---------------------------------------------------------------------------
DO $$
BEGIN
    RAISE NOTICE 'IPD optimization schema created successfully.';
END;
$$;
