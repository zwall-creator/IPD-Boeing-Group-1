"""
db.py
-----
Thin database helper for the computation service.

Uses a module-level connection pool (lazy init) so Flask workers share
connections rather than opening a new one per request.

Environment variable:
    DATABASE_URL — postgresql://user:pass@host:port/dbname
                   Set automatically by docker-compose; falls back to None
                   so the app starts cleanly without a database.
"""

import os
import logging
from contextlib import contextmanager
from typing import Optional

log = logging.getLogger(__name__)

_pool = None  # psycopg2 SimpleConnectionPool, or None if DB unavailable


def _get_pool():
    """Lazily initialise the connection pool on first use."""
    global _pool
    if _pool is not None:
        return _pool

    url = os.environ.get("DATABASE_URL", "").strip()
    if not url:
        log.warning("DATABASE_URL not set — database persistence disabled")
        return None

    try:
        from psycopg2 import pool as pg_pool
        _pool = pg_pool.SimpleConnectionPool(1, 10, dsn=url)
        log.info("Database connection pool initialised")
        return _pool
    except Exception as exc:
        log.warning("Could not connect to database: %s — persistence disabled", exc)
        return None


@contextmanager
def get_conn():
    """
    Context manager that yields a psycopg2 connection from the pool.
    Commits on clean exit, rolls back on exception, always returns the
    connection to the pool.

    Usage:
        with get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute(...)
    """
    pool = _get_pool()
    if pool is None:
        yield None
        return

    conn = None
    try:
        conn = pool.getconn()
        yield conn
        conn.commit()
    except Exception:
        if conn:
            conn.rollback()
        raise
    finally:
        if conn:
            pool.putconn(conn)


# ---------------------------------------------------------------------------
# Simulation run helpers
# ---------------------------------------------------------------------------

def insert_run(solver: str, opt_params: dict) -> Optional[int]:
    """
    Insert a new simulation_runs row and return its id.
    Returns None if the database is unavailable.
    """
    sql = """
        INSERT INTO simulation_runs
            (solver, security_weight, cost_weight, bandwidth_weight, risk_threshold, status)
        VALUES (%s, %s, %s, %s, %s, 'running')
        RETURNING id
    """
    try:
        with get_conn() as conn:
            if conn is None:
                return None
            with conn.cursor() as cur:
                cur.execute(sql, (
                    solver,
                    opt_params.get("securityWeight", 50),
                    opt_params.get("costWeight", 50),
                    opt_params.get("bandwidthWeight", 50),
                    opt_params.get("riskThreshold", 30),
                ))
                return cur.fetchone()[0]
    except Exception as exc:
        log.warning("insert_run failed: %s", exc)
        return None


def update_run_status(run_id: int, status: str, error: str = None) -> None:
    """Mark a simulation_runs row as completed."""
    if run_id is None:
        return
    sql = """
        UPDATE simulation_runs
        SET status = %s, completed_at = NOW(), error_message = %s
        WHERE id = %s
    """
    try:
        with get_conn() as conn:
            if conn is None:
                return
            with conn.cursor() as cur:
                cur.execute(sql, (status, error, run_id))
    except Exception as exc:
        log.warning("update_run_status failed: %s", exc)


def insert_result(run_id: int, result: dict) -> None:
    """Persist circuit execution result into simulation_results."""
    if run_id is None:
        return
    import json
    sql = """
        INSERT INTO simulation_results
            (run_id, backend, used_ibm, shots, counts, execution_ms)
        VALUES (%s, %s, %s, %s, %s, %s)
    """
    try:
        with get_conn() as conn:
            if conn is None:
                return
            with conn.cursor() as cur:
                cur.execute(sql, (
                    run_id,
                    result.get("backend", "unknown"),
                    result.get("used_ibm", False),
                    result.get("shots"),
                    json.dumps(result.get("counts", {})),
                    result.get("execution_ms"),
                ))
    except Exception as exc:
        log.warning("insert_result failed: %s", exc)


def insert_log(run_id: int, step: int, total: int, message: str) -> None:
    """Persist a single SSE progress message into simulation_logs."""
    if run_id is None:
        return
    sql = """
        INSERT INTO simulation_logs (run_id, step, total_steps, message)
        VALUES (%s, %s, %s, %s)
    """
    try:
        with get_conn() as conn:
            if conn is None:
                return
            with conn.cursor() as cur:
                cur.execute(sql, (run_id, step, total, message))
    except Exception as exc:
        log.warning("insert_log failed: %s", exc)


def get_runs(limit: int = 20) -> list:
    """Return the most recent simulation runs with their results."""
    sql = """
        SELECT
            r.id, r.solver, r.security_weight, r.cost_weight,
            r.bandwidth_weight, r.risk_threshold, r.status,
            r.started_at, r.completed_at, r.error_message,
            res.backend, res.used_ibm, res.shots, res.counts
        FROM simulation_runs r
        LEFT JOIN simulation_results res ON res.run_id = r.id
        ORDER BY r.started_at DESC
        LIMIT %s
    """
    try:
        with get_conn() as conn:
            if conn is None:
                return []
            with conn.cursor() as cur:
                cur.execute(sql, (limit,))
                cols = [d[0] for d in cur.description]
                return [dict(zip(cols, row)) for row in cur.fetchall()]
    except Exception as exc:
        log.warning("get_runs failed: %s", exc)
        return []
