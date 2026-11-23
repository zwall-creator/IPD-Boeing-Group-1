"""
Used Claude Opus 5.5 to help write this code.

reports/pdf_renderer.py
-----------------------
Renders a report dict (from builder.build_report) to a PDF with ReportLab.

Charts are drawn with ReportLab's own graphics module, so there is no
matplotlib dependency. Colors match the Reports page (light theme).
"""

from __future__ import annotations

import io
import math
from datetime import datetime

from reportlab.graphics.charts.barcharts import VerticalBarChart
from reportlab.graphics.charts.lineplots import LinePlot
from reportlab.graphics.shapes import Drawing, Line, Rect, String
from reportlab.graphics.widgets.markers import makeMarker
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (KeepTogether, Paragraph, SimpleDocTemplate, Spacer, Table,
                                TableStyle)

# Same order as the frontend (SOLVER_COLORS in ReportsView.jsx). Color follows the solver.
SERIES = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100"]
INK = colors.HexColor("#0b0b0b")
INK_2 = colors.HexColor("#52514e")
MUTED = colors.HexColor("#898781")
GRID = colors.HexColor("#e1e0d9")
AXIS = colors.HexColor("#c3c2b7")
HEADER_BG = colors.HexColor("#f3f2ee")
WARN_BG = colors.HexColor("#fff4db")
WARN_BORDER = colors.HexColor("#eda100")

STATUS_LABEL = {"optimal": "Optimal", "feasible": "Feasible", "infeasible": "Infeasible",
                "timeout": "Timed out", "skipped": "Skipped"}

PAGE_W, PAGE_H = letter
MARGIN = 0.7 * inch
CONTENT_W = PAGE_W - 2 * MARGIN


# ---------------------------------------------------------------------------
# Formatting helpers (keep in sync with ReportsView.jsx)
# ---------------------------------------------------------------------------

def fmt_ms(ms):
    if ms is None:
        return "-"
    if ms >= 10000:
        return f"{ms / 1000:.0f} s"
    if ms >= 1000:
        return f"{ms / 1000:.2f} s"
    if ms >= 10:
        return f"{ms:.0f} ms"
    return f"{ms:.2f} ms"


def fmt_pct(v, digits=1):
    return "-" if v is None else f"{v:.{digits}f}%"


def fmt_date(iso):
    try:
        return datetime.fromisoformat(iso).strftime("%b %d, %Y %H:%M UTC")
    except (TypeError, ValueError):
        return str(iso)


def _color(i):
    return colors.HexColor(SERIES[i % len(SERIES)])


# ---------------------------------------------------------------------------
# Styles
# ---------------------------------------------------------------------------

def _styles():
    base = getSampleStyleSheet()
    return {
        "title": ParagraphStyle("title", parent=base["Title"], fontName="Helvetica-Bold", fontSize=20,
                                leading=24, textColor=INK, alignment=TA_LEFT, spaceAfter=4),
        "meta": ParagraphStyle("meta", parent=base["Normal"], fontSize=9, leading=12, textColor=INK_2),
        "h2": ParagraphStyle("h2", parent=base["Heading2"], fontName="Helvetica-Bold", fontSize=13,
                             leading=16, textColor=INK, spaceBefore=14, spaceAfter=6),
        "body": ParagraphStyle("body", parent=base["Normal"], fontSize=10, leading=14, textColor=INK),
        "small": ParagraphStyle("small", parent=base["Normal"], fontSize=8, leading=10.5, textColor=INK_2),
        "cell": ParagraphStyle("cell", parent=base["Normal"], fontSize=8, leading=10, textColor=INK),
        "bullet": ParagraphStyle("bullet", parent=base["Normal"], fontSize=10, leading=14, textColor=INK,
                                 leftIndent=12, bulletIndent=2, spaceAfter=3),
        "banner": ParagraphStyle("banner", parent=base["Normal"], fontSize=9, leading=12, textColor=INK),
    }


def _table_style(extra=()):
    return TableStyle([
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("TEXTCOLOR", (0, 0), (-1, -1), INK),
        ("BACKGROUND", (0, 0), (-1, 0), HEADER_BG),
        ("LINEBELOW", (0, 0), (-1, 0), 0.75, AXIS),
        ("LINEBELOW", (0, 1), (-1, -1), 0.25, GRID),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        *extra,
    ])


# ---------------------------------------------------------------------------
# Charts
# ---------------------------------------------------------------------------

def _runtime_scaling_chart(report, width=CONTENT_W, height=230):
    """Runtime vs network size, log y axis. One line per solver, gaps where it could not run."""
    solvers = report["solvers"]
    scen = sorted(report["scenarios"], key=lambda s: s["nodes"])
    by_key = {(r["solver_id"], r["scenario_id"]): r for r in report["results"]}

    series, used = [], []
    for i, sv in enumerate(solvers):
        pts = []
        for sc in scen:
            r = by_key.get((sv["id"], sc["id"]))
            if r and r["runtime_ms_mean"] and r["status"] in ("optimal", "feasible"):
                pts.append((scen.index(sc), math.log10(r["runtime_ms_mean"])))
        if pts:
            series.append(pts)
            used.append(i)

    d = Drawing(width, height)
    if not series:
        d.add(String(width / 2, height / 2, "No runtime data", fontName="Helvetica", textAnchor="middle",
                     fillColor=MUTED))
        return d

    ys = [y for s in series for _, y in s]
    y_min, y_max = math.floor(min(ys)), math.ceil(max(ys))
    if y_min == y_max:
        y_max += 1

    lp = LinePlot()
    lp.x, lp.y = 46, 34
    lp.width, lp.height = width - 46 - 110, height - 34 - 14
    lp.data = series
    lp.joinedLines = 1
    for k, i in enumerate(used):
        lp.lines[k].strokeColor = _color(i)
        lp.lines[k].strokeWidth = 2
        m = makeMarker("FilledCircle")
        m.size = 5
        m.fillColor = _color(i)
        m.strokeColor = colors.white
        m.strokeWidth = 1
        lp.lines[k].symbol = m

    xa = lp.xValueAxis
    # Scenarios are evenly spaced categories ordered by size (several share a node count)
    xa.valueMin, xa.valueMax = -0.4, len(scen) - 0.6
    xa.valueSteps = list(range(len(scen)))
    xa.labelTextFormat = lambda v: f"{scen[int(round(v))]['name']} ({scen[int(round(v))]['nodes']}n)"
    xa.labels.fontName, xa.labels.fontSize, xa.labels.fillColor = "Helvetica", 7.5, INK_2
    xa.strokeColor = AXIS
    xa.visibleTicks = 0

    ya = lp.yValueAxis
    ya.valueMin, ya.valueMax = y_min, y_max
    ya.valueSteps = list(range(y_min, y_max + 1))
    ya.labelTextFormat = lambda v: fmt_ms(10 ** v)
    ya.labels.fontName, ya.labels.fontSize, ya.labels.fillColor = "Helvetica", 7.5, INK_2
    ya.visibleGrid = 1
    ya.gridStrokeColor, ya.gridStrokeWidth = GRID, 0.5
    ya.visibleAxis = 0
    ya.visibleTicks = 0
    d.add(lp)

    # Direct labels at each line's last point (nudged apart so they don't collide)
    label_pos = []
    for k, i in enumerate(used):
        x, y = series[k][-1]
        px = lp.x + (x - xa.valueMin) / (xa.valueMax - xa.valueMin) * lp.width
        py = lp.y + (y - y_min) / (y_max - y_min) * lp.height
        label_pos.append([py, px, solvers[i]["name"]])
    label_pos.sort()
    for j in range(1, len(label_pos)):
        if label_pos[j][0] - label_pos[j - 1][0] < 10:
            label_pos[j][0] = label_pos[j - 1][0] + 10
    for py, px, name in label_pos:
        d.add(String(px + 7, py - 3, name, fontName="Helvetica", fontSize=8, fillColor=INK))

    d.add(String(lp.x + lp.width / 2, 6, "Scenario (ordered by size)", fontName="Helvetica", fontSize=8,
                 fillColor=INK_2,
                 textAnchor="middle"))
    return d


def _solver_bar(report, key, title, fmt, width, height=170, scale=1.0):
    solvers = report["solvers"]
    summ = {s["solver_id"]: s for s in report["summary"]}
    vals = [summ[sv["id"]][key] for sv in solvers]
    plot_vals = [(v or 0) * scale for v in vals]

    d = Drawing(width, height)
    d.add(String(0, height - 10, title, fontSize=9, fontName="Helvetica-Bold", fillColor=INK))
    bc = VerticalBarChart()
    bc.x, bc.y = 30, 30
    bc.width, bc.height = width - 40, height - 58
    bc.data = [plot_vals]
    bc.barSpacing = 2
    bc.groupSpacing = 14
    bc.strokeColor = None
    bc.bars.strokeColor = None
    for i in range(len(solvers)):
        bc.bars[(0, i)].fillColor = _color(i)
    top = max(plot_vals) if any(plot_vals) else 1
    bc.valueAxis.valueMin = 0
    bc.valueAxis.valueMax = top * 1.2
    bc.valueAxis.visibleAxis = 0
    bc.valueAxis.visibleTicks = 0
    bc.valueAxis.visibleLabels = 0
    bc.valueAxis.visibleGrid = 1
    bc.valueAxis.gridStrokeColor = GRID
    bc.valueAxis.gridStrokeWidth = 0.5
    bc.categoryAxis.categoryNames = [sv["name"] for sv in solvers]
    bc.categoryAxis.labels.fontName = "Helvetica"
    bc.categoryAxis.labels.fontSize = 7.5
    bc.categoryAxis.labels.fillColor = INK_2
    bc.categoryAxis.strokeColor = AXIS
    bc.categoryAxis.visibleTicks = 0
    d.add(bc)

    # Value labels on top of each bar (text in ink, not the series color)
    n = len(solvers)
    slot = bc.width / n
    for i, v in enumerate(vals):
        cx = bc.x + slot * (i + 0.5)
        cy = bc.y + (plot_vals[i] / bc.valueAxis.valueMax) * bc.height + 4
        d.add(String(cx, cy, fmt(v), fontName="Helvetica", fontSize=8, fillColor=INK, textAnchor="middle"))
    d.add(Line(bc.x, bc.y, bc.x + bc.width, bc.y, strokeColor=AXIS, strokeWidth=0.75))
    return d


def _legend(report):
    cells = []
    for i, sv in enumerate(report["solvers"]):
        swatch = Drawing(10, 10)
        swatch.add(Rect(0, 1, 9, 9, rx=2, ry=2, fillColor=_color(i), strokeColor=None))
        cells += [swatch, Paragraph(f'{sv["name"]} <font color="#898781">({sv["paradigm"]})</font>',
                                    ParagraphStyle("lg", fontSize=8, leading=10, textColor=INK))]
    t = Table([cells], colWidths=[12, CONTENT_W / len(report["solvers"]) - 12] * len(report["solvers"]))
    t.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                           ("LEFTPADDING", (0, 0), (-1, -1), 0)]))
    return t


# ---------------------------------------------------------------------------
# Page decoration
# ---------------------------------------------------------------------------

def _decorate(report):
    def draw(canvas, doc):
        canvas.saveState()
        if report.get("is_sample_data"):
            canvas.setFillColor(colors.Color(0.85, 0.2, 0.2, alpha=0.05))
            canvas.setFont("Helvetica-Bold", 70)
            canvas.translate(PAGE_W / 2, PAGE_H / 2)
            canvas.rotate(35)
            canvas.drawCentredString(0, 0, "SAMPLE DATA")
            canvas.rotate(-35)
            canvas.translate(-PAGE_W / 2, -PAGE_H / 2)
        canvas.setFont("Helvetica", 7.5)
        canvas.setFillColor(MUTED)
        canvas.drawString(MARGIN, 0.45 * inch, f"IPD Solver Comparison Report · {report['title']}")
        canvas.drawRightString(PAGE_W - MARGIN, 0.45 * inch, f"Page {doc.page}")
        canvas.restoreState()
    return draw


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------

def render_pdf(report: dict) -> bytes:
    st = _styles()
    solvers = {s["id"]: s for s in report["solvers"]}
    scen = {s["id"]: s for s in report["scenarios"]}
    cfg = report.get("config", {})
    p = cfg.get("opt_params", {})

    story = [
        Paragraph("Solver Performance Comparison", st["title"]),
        Paragraph(report["title"], ParagraphStyle("sub", parent=st["body"], fontSize=12, leading=15,
                                                  textColor=INK_2, spaceAfter=6)),
        Paragraph(
            f"Report ID {report['id']} · Generated {fmt_date(report['generated_at'])} · "
            f"{len(report['solvers'])} solvers · {len(report['scenarios'])} scenarios · "
            f"{cfg.get('trials', '?')} trials per run · {cfg.get('time_limit_s', '?')} s time limit",
            st["meta"]),
        Paragraph(
            f"Optimization weights: security {p.get('securityWeight', '-')}, cost {p.get('costWeight', '-')}, "
            f"bandwidth {p.get('bandwidthWeight', '-')}, risk threshold {p.get('riskThreshold', '-')}",
            st["meta"]),
        Spacer(1, 10),
    ]

    if report.get("is_sample_data"):
        banner = Table([[Paragraph(
            "<b>Sample data.</b> These results are generated placeholders that show the report layout. "
            "They are not measurements from the solvers.", st["banner"])]], colWidths=[CONTENT_W])
        banner.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), WARN_BG),
                                    ("LINEBEFORE", (0, 0), (0, -1), 3, WARN_BORDER),
                                    ("LEFTPADDING", (0, 0), (-1, -1), 8),
                                    ("TOPPADDING", (0, 0), (-1, -1), 6),
                                    ("BOTTOMPADDING", (0, 0), (-1, -1), 6)]))
        story += [banner, Spacer(1, 6)]

    # Solver summary table
    rows = [["Solver", "Paradigm", "Solved", "Valid runs", "Mean gap", "Matched best", "Largest solved"]]
    for s in report["summary"]:
        largest = scen.get(s["largest_solved_scenario"])
        rows.append([
            solvers[s["solver_id"]]["name"], solvers[s["solver_id"]]["paradigm"],
            f"{s['scenarios_solved']} / {s['scenarios_attempted']}",
            fmt_pct(100 * s["success_rate"], 0),
            fmt_pct(s["optimality_gap_pct_mean"], 2),
            f"{s['matched_best_count']} / {s['scenarios_solved']}",
            f"{largest['name']} ({largest['nodes']} nodes)" if largest else "-",
        ])
    widths = [0.14, 0.2, 0.09, 0.11, 0.1, 0.13, 0.23]
    t = Table(rows, colWidths=[w * CONTENT_W for w in widths], repeatRows=1)
    t.setStyle(_table_style([("ALIGN", (2, 1), (5, -1), "RIGHT"), ("ALIGN", (2, 0), (5, 0), "RIGHT")]))
    story += [Paragraph("Solver summary", st["h2"]), t]

    # Charts
    story.append(KeepTogether([
        Paragraph("Runtime vs network size", st["h2"]),
        Paragraph("Mean runtime per scenario, log scale. A line stops where the solver timed out or "
                  "could not run.", st["small"]),
        Spacer(1, 4),
        _runtime_scaling_chart(report),
        Spacer(1, 4),
        _legend(report),
    ]))

    half = CONTENT_W / 2 - 8
    bars = Table([[
        _solver_bar(report, "optimality_gap_pct_mean", "Mean optimality gap (lower is better)",
                    lambda v: fmt_pct(v, 1), half),
        _solver_bar(report, "success_rate", "Valid runs (higher is better)",
                    lambda v: fmt_pct(100 * v, 0) if v is not None else "-", half),
    ]], colWidths=[half + 8, half + 8])
    bars.setStyle(TableStyle([("LEFTPADDING", (0, 0), (-1, -1), 0), ("VALIGN", (0, 0), (-1, -1), "TOP")]))
    story.append(KeepTogether([
        Paragraph("Solution quality and reliability", st["h2"]),
        Paragraph("Optimality gap is the mean objective's distance above the best objective any solver "
                  "found on that scenario, averaged over the scenarios the solver completed. "
                  "Valid runs counts trials that returned a placement satisfying every constraint "
                  "(skipped scenarios excluded).", st["small"]),
        Spacer(1, 6),
        bars,
    ]))

    # Detailed results
    story.append(Paragraph("Detailed results", st["h2"]))
    rows = [["Scenario", "Size", "Solver", "Status", "Runtime (mean ± sd)", "Objective", "Gap",
             "Valid", "Notes"]]
    shade = []
    row_i = 1
    for k, sc in enumerate(report["scenarios"]):
        sc_rows = [r for r in report["results"] if r["scenario_id"] == sc["id"]]
        for j, r in enumerate(sc_rows):
            rt = "-" if r["runtime_ms_mean"] is None else (
                f"{fmt_ms(r['runtime_ms_mean'])} ± {fmt_ms(r['runtime_ms_std'])}")
            notes = r.get("note") or ""
            extra = r.get("extra", {})
            if "qubits" in extra and r["status"] != "skipped":
                notes = (f"{extra['qubits']} qubits, depth {extra.get('circuit_depth', '-')}"
                         + (f"; {notes}" if notes else ""))
            rows.append([
                sc["name"] if j == 0 else "",
                f"{sc['nodes']}n / {sc['links']}l" if j == 0 else "",
                solvers[r["solver_id"]]["name"],
                STATUS_LABEL.get(r["status"], r["status"]),
                rt,
                "-" if r["objective_mean"] is None else f"{r['objective_mean']:.2f}",
                fmt_pct(r["optimality_gap_pct"], 1),
                f"{round(r['success_rate'] * r['trials'])}/{r['trials']}",
                Paragraph(notes, st["cell"]),
            ])
        if k % 2 == 1:
            shade.append(("BACKGROUND", (0, row_i), (-1, row_i + len(sc_rows) - 1), colors.HexColor("#fafaf8")))
        row_i += len(sc_rows)
    widths = [0.11, 0.09, 0.11, 0.09, 0.15, 0.08, 0.07, 0.06, 0.24]
    t = Table(rows, colWidths=[w * CONTENT_W for w in widths], repeatRows=1)
    t.setStyle(_table_style([*shade, ("ALIGN", (4, 1), (7, -1), "RIGHT"),
                             ("ALIGN", (4, 0), (7, 0), "RIGHT")]))
    story.append(t)

    # Definitions
    story.append(KeepTogether([
        Paragraph("Metric definitions", st["h2"]),
        Paragraph("<b>Objective</b>: total security gap across nodes (sum of risk minus security level). "
                  "Lower is better.", st["small"]),
        Paragraph("<b>Optimal</b>: the solver proved optimality, or matched the best known objective. "
                  "<b>Feasible</b>: a valid placement without an optimality proof. "
                  "<b>Infeasible</b>: the returned placement broke a constraint. "
                  "<b>Timed out</b>: no solution within the time limit. "
                  "<b>Skipped</b>: the problem exceeded a backend limit (for example simulator qubits).",
                  st["small"]),
        Paragraph("<b>Size</b>: n = nodes, l = links. Decision variables = links × security devices, "
                  "which is also the qubit count for QAOA.", st["small"]),
    ]))

    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=letter, leftMargin=MARGIN, rightMargin=MARGIN,
                            topMargin=MARGIN, bottomMargin=0.8 * inch,
                            title=f"Solver comparison: {report['title']}", author="IPD Boeing Group 1")
    deco = _decorate(report)
    doc.build(story, onFirstPage=deco, onLaterPages=deco)
    return buf.getvalue()
