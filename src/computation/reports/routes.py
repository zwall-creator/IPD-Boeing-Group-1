"""
Used Claude Opus 5.5 to help write this code.

reports/routes.py
-----------------
Flask blueprint for the report generation service. Registered in app.py.

    GET  /reports               list of reports (id, title, date, counts)
    GET  /reports/<id>          full report JSON (drives the Reports page)
    GET  /reports/<id>/pdf      the same report as a downloadable PDF
    POST /reports/generate      create a new report; optional JSON body:
                                {"title": str, "seed": int, "trials": int, "opt_params": {...}}
"""

from __future__ import annotations

import re

from flask import Blueprint, Response, jsonify, request

from . import service
from .pdf_renderer import render_pdf

reports_bp = Blueprint("reports", __name__, url_prefix="/reports")


@reports_bp.get("")
def list_reports():
    return jsonify(service.list_reports())


@reports_bp.get("/<report_id>")
def get_report(report_id):
    report = service.get_report(report_id)
    if report is None:
        return jsonify(ok=False, error=f"report '{report_id}' not found"), 404
    return jsonify(report)


@reports_bp.get("/<report_id>/pdf")
def get_report_pdf(report_id):
    report = service.get_report(report_id)
    if report is None:
        return jsonify(ok=False, error=f"report '{report_id}' not found"), 404
    pdf = render_pdf(report)
    slug = re.sub(r"[^a-z0-9]+", "-", report["title"].lower()).strip("-")[:60]
    filename = f"solver-comparison-{report['id']}-{slug}.pdf"
    # ?inline=1 opens it in the browser tab instead of downloading
    disposition = "inline" if request.args.get("inline") else "attachment"
    return Response(pdf, mimetype="application/pdf",
                    headers={"Content-Disposition": f'{disposition}; filename="{filename}"'})


@reports_bp.post("/generate")
def generate_report():
    body = request.get_json(silent=True) or {}
    try:
        report = service.generate_report(
            title=body.get("title"),
            opt_params=body.get("opt_params"),
            seed=body.get("seed"),
            trials=body.get("trials", 5),
        )
    except (TypeError, ValueError) as exc:
        return jsonify(ok=False, error=str(exc)), 400
    return jsonify(report), 201
