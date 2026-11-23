"""
Used Claude Opus 5.5 to help write this code.

Tests for the report generation service (reports/ package).
Run from src/computation:  python -m pytest tests/test_reports.py
"""

from flask import Flask

from reports import sample_data, service
from reports.builder import build_report
from reports.pdf_renderer import render_pdf
from reports.routes import reports_bp


def _client():
    app = Flask(__name__)
    app.register_blueprint(reports_bp)
    return app.test_client()


def test_sample_data_is_deterministic():
    assert sample_data.generate_records(5) == sample_data.generate_records(5)


def test_every_cell_present_and_gaps_non_negative():
    rep = service.get_report("sample-001")
    assert len(rep["results"]) == len(rep["solvers"]) * len(rep["scenarios"])
    for r in rep["results"]:
        if r["optimality_gap_pct"] is not None:
            assert r["optimality_gap_pct"] >= 0
        assert 0.0 <= r["success_rate"] <= 1.0
    assert rep["is_sample_data"] is True


def test_builder_with_handwritten_records():
    solvers = [{"id": "a", "name": "A", "paradigm": "x", "description": ""},
               {"id": "b", "name": "B", "paradigm": "x", "description": ""}]
    scenarios = [{"id": "s", "name": "S", "nodes": 3, "links": 2, "devices": 1}]
    rec = dict(scenario_id="s", violations=0, extra={}, note=None, devices_placed=1, nodes_protected=3)
    records = [
        {**rec, "solver_id": "a", "trial": 1, "status": "optimal", "runtime_ms": 10.0, "objective": 4.0},
        {**rec, "solver_id": "b", "trial": 1, "status": "feasible", "runtime_ms": 2.0, "objective": 5.0},
        {**rec, "solver_id": "b", "trial": 2, "status": "infeasible", "runtime_ms": 2.0, "objective": None,
         "violations": 1},
    ]
    rep = build_report({"id": "t", "title": "t", "generated_at": "2026-01-01T00:00:00+00:00",
                        "is_sample_data": False, "config": {}}, solvers, scenarios, records)
    b = next(r for r in rep["results"] if r["solver_id"] == "b")
    assert b["optimality_gap_pct"] == 25.0
    assert b["success_rate"] == 0.5
    assert rep["scenarios"][0]["best_known_objective"] == 4.0


def test_pdf_renders():
    pdf = render_pdf(service.get_report("sample-003"))
    assert pdf.startswith(b"%PDF")


def test_routes():
    c = _client()
    listing = c.get("/reports").get_json()
    assert {r["id"] for r in listing} >= {"sample-001", "sample-002", "sample-003"}
    assert c.get("/reports/sample-002").status_code == 200
    assert c.get("/reports/nope").status_code == 404
    pdf = c.get("/reports/sample-001/pdf")
    assert pdf.mimetype == "application/pdf"
    assert "attachment" in pdf.headers["Content-Disposition"]
    created = c.post("/reports/generate", json={"title": "Mine", "seed": 3})
    assert created.status_code == 201
    assert created.get_json()["title"] == "Mine"
