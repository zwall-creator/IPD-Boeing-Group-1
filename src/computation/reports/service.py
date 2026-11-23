"""
Used Claude Opus 5.5 to help write this code.

reports/service.py
------------------
Entry point the Flask routes call. Knows which reports exist and where
their data comes from.

Right now every report is built from sample_data.py. When real runs are
stored in Postgres, add a function that loads records for a report from the
database and call build_report() with them here; the routes, PDF renderer and
frontend stay the same.
"""

from __future__ import annotations

import itertools
from datetime import datetime, timezone

from . import sample_data
from .builder import build_report

_cache: dict[str, dict] = {}
_generated: list[dict] = []          # reports created with POST /reports/generate
_counter = itertools.count(1)


def _catalogue() -> list[dict]:
    return sample_data.SAMPLE_REPORTS + _generated


def _build(entry: dict) -> dict:
    records = sample_data.generate_records(
        seed=entry["seed"],
        scenario_ids=entry.get("scenario_ids"),
        trials=entry.get("trials", 5),
        time_limit_s=entry.get("time_limit_s", sample_data.DEFAULT_TIME_LIMIT_S),
    )
    meta = {
        "id": entry["id"],
        "title": entry["title"],
        "generated_at": entry["generated_at"],
        "is_sample_data": True,
        "config": {
            "trials": entry.get("trials", 5),
            "time_limit_s": entry.get("time_limit_s", sample_data.DEFAULT_TIME_LIMIT_S),
            "aer_max_qubits": sample_data.AER_MAX_QUBITS,
            "opt_params": entry["opt_params"],
        },
    }
    # copy so the builder can annotate without touching the module-level catalogue
    scenarios = [dict(s) for s in sample_data.SCENARIOS]
    return build_report(meta, sample_data.SOLVERS, scenarios, records)


def list_reports() -> list[dict]:
    """Lightweight listing for the Reports page sidebar, newest first."""
    out = []
    for entry in _catalogue():
        rep = get_report(entry["id"])
        out.append({
            "id": rep["id"],
            "title": rep["title"],
            "generated_at": rep["generated_at"],
            "is_sample_data": rep["is_sample_data"],
            "solver_count": len(rep["solvers"]),
            "scenario_count": len(rep["scenarios"]),
        })
    out.sort(key=lambda r: r["generated_at"], reverse=True)
    return out


def get_report(report_id: str) -> dict | None:
    if report_id in _cache:
        return _cache[report_id]
    entry = next((e for e in _catalogue() if e["id"] == report_id), None)
    if entry is None:
        return None
    _cache[report_id] = _build(entry)
    return _cache[report_id]


def generate_report(title: str | None = None, opt_params: dict | None = None,
                    seed: int | None = None, trials: int = 5) -> dict:
    """Create a new (sample) report. Kept in memory until the service restarts."""
    n = next(_counter)
    now = datetime.now(timezone.utc)
    entry = {
        "id": f"generated-{n:03d}",
        "title": title or f"Generated benchmark #{n}",
        "seed": seed if seed is not None else int(now.timestamp()),
        "scenario_ids": None,
        "trials": max(1, min(int(trials), 50)),
        "opt_params": opt_params or {"securityWeight": 50, "costWeight": 50,
                                     "bandwidthWeight": 50, "riskThreshold": 30},
        "generated_at": now.isoformat(),
    }
    _generated.append(entry)
    return get_report(entry["id"])
