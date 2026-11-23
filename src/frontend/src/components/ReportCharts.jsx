/**
 * SVG charts for the Reports page. No chart library: plain SVG + an HTML tooltip.
 * Colors come from CSS variables (--series-1..4) defined in ReportsView.css,
 * so light/dark mode swap in one place. Color always follows the solver.
 */
import React, { useEffect, useRef, useState } from 'react';
import { fmtMs, STATUS_LABEL } from '../api/reports';

export const seriesVar = (i) => `var(--series-${(i % 4) + 1})`;

// Measure the container so the SVG can be drawn at real pixel size (text stays crisp)
function useWidth() {
  const ref = useRef(null);
  const [width, setWidth] = useState(600);
  useEffect(() => {
    if (!ref.current) return undefined;
    const ro = new ResizeObserver(([entry]) => setWidth(Math.max(280, entry.contentRect.width)));
    ro.observe(ref.current);
    return () => ro.disconnect();
  }, []);
  return [ref, width];
}

export function Legend({ solvers }) {
  return (
    <ul className="chart-legend">
      {solvers.map((s, i) => (
        <li key={s.id}>
          <span className="chart-legend__swatch" style={{ background: seriesVar(i) }} aria-hidden="true" />
          {s.name}
        </li>
      ))}
    </ul>
  );
}

/**
 * Runtime per scenario (scenarios ordered by size on x), log-scale y.
 * A solver's line breaks where it timed out or was skipped.
 */
export function RuntimeChart({ report }) {
  const [ref, width] = useWidth();
  const [hover, setHover] = useState(null); // scenario index
  const height = 280;
  const m = { top: 14, right: 104, bottom: 40, left: 58 };
  const iw = width - m.left - m.right;
  const ih = height - m.top - m.bottom;

  const scenarios = [...report.scenarios].sort((a, b) => a.nodes - b.nodes);
  const cell = (sv, sc) => report.results.find((r) => r.solver_id === sv && r.scenario_id === sc);
  const ok = (r) => r && r.runtime_ms_mean && (r.status === 'optimal' || r.status === 'feasible');

  const all = report.results.filter(ok).map((r) => Math.log10(r.runtime_ms_mean));
  if (!all.length) return <p className="chart-empty">No runtime data.</p>;
  const yMin = Math.floor(Math.min(...all));
  const yMax = Math.max(yMin + 1, Math.ceil(Math.max(...all)));
  const step = iw / scenarios.length;
  const x = (i) => step * (i + 0.5);
  const y = (ms) => ih - ((Math.log10(ms) - yMin) / (yMax - yMin)) * ih;
  const ticks = Array.from({ length: yMax - yMin + 1 }, (_, k) => yMin + k);

  // Line segments per solver (split at gaps) and the end point for the direct label
  const lines = report.solvers.map((sv, si) => {
    const segs = [];
    let cur = [];
    scenarios.forEach((sc, i) => {
      const r = cell(sv.id, sc.id);
      if (ok(r)) cur.push([x(i), y(r.runtime_ms_mean)]);
      else if (cur.length) { segs.push(cur); cur = []; }
    });
    if (cur.length) segs.push(cur);
    const last = segs.length ? segs[segs.length - 1].at(-1) : null;
    return { sv, si, segs, last };
  });

  // Nudge direct labels apart vertically
  const labels = lines.filter((l) => l.last).map((l) => ({ ...l, ly: l.last[1] }))
    .sort((a, b) => a.ly - b.ly);
  for (let k = 1; k < labels.length; k++) {
    if (labels[k].ly - labels[k - 1].ly < 13) labels[k].ly = labels[k - 1].ly + 13;
  }

  const hovered = hover === null ? null : scenarios[hover];

  return (
    <div className="chart" ref={ref}>
      <svg width={width} height={height} role="img"
        aria-label="Line chart of mean solver runtime for each scenario, log scale">
        <g transform={`translate(${m.left},${m.top})`}>
          {ticks.map((t) => (
            <g key={t}>
              <line className="chart-grid" x1={0} x2={iw} y1={y(10 ** t)} y2={y(10 ** t)} />
              <text className="chart-axis-label" x={-8} y={y(10 ** t)} dy="0.32em" textAnchor="end">
                {fmtMs(10 ** t)}
              </text>
            </g>
          ))}
          <line className="chart-baseline" x1={0} x2={iw} y1={ih} y2={ih} />
          {scenarios.map((sc, i) => (
            <text key={sc.id} className="chart-axis-label" x={x(i)} y={ih + 16} textAnchor="middle">
              {sc.name}
              <tspan x={x(i)} dy="1.2em" className="chart-axis-sub">{sc.nodes} nodes</tspan>
            </text>
          ))}
          {hovered && <line className="chart-crosshair" x1={x(hover)} x2={x(hover)} y1={0} y2={ih} />}
          {lines.map(({ sv, si, segs }) => (
            <g key={sv.id}>
              {segs.map((pts, k) => (
                <polyline key={k} fill="none" stroke={seriesVar(si)} strokeWidth={2}
                  strokeLinejoin="round" points={pts.map((p) => p.join(',')).join(' ')} />
              ))}
              {segs.flat().map(([px, py], k) => (
                <circle key={k} cx={px} cy={py} r={4} fill={seriesVar(si)}
                  stroke="var(--chart-surface)" strokeWidth={2} />
              ))}
            </g>
          ))}
          {labels.map((l) => (
            <text key={l.sv.id} className="chart-direct-label" x={l.last[0] + 9} y={l.ly} dy="0.32em">
              {l.sv.name}
            </text>
          ))}
          {/* Hit targets: one full-height column per scenario */}
          {scenarios.map((sc, i) => (
            <rect key={sc.id} x={x(i) - step / 2} y={0} width={step} height={ih} fill="transparent"
              onMouseEnter={() => setHover(i)} onMouseLeave={() => setHover(null)} />
          ))}
        </g>
      </svg>
      {hovered && (
        <div className="chart-tooltip" role="status"
          style={{ left: Math.min(m.left + x(hover) + 12, width - 210), top: m.top }}>
          <strong>{hovered.name}</strong>
          <span className="chart-tooltip__sub">{hovered.nodes} nodes · {hovered.links} links</span>
          {report.solvers.map((sv, si) => {
            const r = cell(sv.id, hovered.id);
            return (
              <div key={sv.id} className="chart-tooltip__row">
                <span className="chart-legend__swatch" style={{ background: seriesVar(si) }} />
                <span>{sv.name}</span>
                <span className="chart-tooltip__val">
                  {ok(r) ? fmtMs(r.runtime_ms_mean) : (r ? STATUS_LABEL[r.status] : '–')}
                </span>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}

/** One bar per solver for a summary metric. */
export function SolverBarChart({ report, metric, format, label }) {
  const [ref, width] = useWidth();
  const [hover, setHover] = useState(null);
  const height = 210;
  const m = { top: 22, right: 8, bottom: 28, left: 8 };
  const iw = width - m.left - m.right;
  const ih = height - m.top - m.bottom;
  const rows = report.solvers.map((sv, i) => {
    const s = report.summary.find((x) => x.solver_id === sv.id);
    return { sv, i, s, v: s?.[metric] ?? null };
  });
  const max = Math.max(...rows.map((r) => r.v ?? 0)) || 1;
  const slot = iw / rows.length;
  const bw = Math.min(56, slot * 0.55);

  return (
    <div className="chart" ref={ref}>
      <svg width={width} height={height} role="img" aria-label={`Bar chart: ${label}`}>
        <g transform={`translate(${m.left},${m.top})`}>
          {[0.5, 1].map((f) => (
            <line key={f} className="chart-grid" x1={0} x2={iw} y1={ih - (ih * f) / 1.15} y2={ih - (ih * f) / 1.15} />
          ))}
          {rows.map(({ sv, i, v }) => {
            const h = v === null ? 0 : (v / max / 1.15) * ih;
            const cx = slot * (i + 0.5);
            return (
              <g key={sv.id}>
                {h > 0 && (
                  <path fill={seriesVar(i)}
                    d={`M${cx - bw / 2},${ih} V${ih - h + Math.min(4, h)} q0,-${Math.min(4, h)} ${Math.min(4, h)},-${Math.min(4, h)}
                        H${cx + bw / 2 - Math.min(4, h)} q${Math.min(4, h)},0 ${Math.min(4, h)},${Math.min(4, h)} V${ih} Z`} />
                )}
                <text className="chart-value-label" x={cx} y={ih - h - 6} textAnchor="middle">{format(v)}</text>
                <text className="chart-axis-label" x={cx} y={ih + 16} textAnchor="middle">{sv.name}</text>
                <rect x={cx - slot / 2} y={0} width={slot} height={ih} fill="transparent"
                  onMouseEnter={() => setHover(i)} onMouseLeave={() => setHover(null)} />
              </g>
            );
          })}
          <line className="chart-baseline" x1={0} x2={iw} y1={ih} y2={ih} />
        </g>
      </svg>
      {hover !== null && (
        <div className="chart-tooltip" role="status"
          style={{ left: Math.min(m.left + slot * (hover + 0.5) + bw / 2 + 6, width - 200), top: m.top }}>
          <strong>{rows[hover].sv.name}</strong>
          <span className="chart-tooltip__sub">{rows[hover].sv.paradigm}</span>
          <div className="chart-tooltip__row">
            <span>{label}</span>
            <span className="chart-tooltip__val">{format(rows[hover].v)}</span>
          </div>
          {rows[hover].s && (
            <div className="chart-tooltip__row">
              <span>Scenarios solved</span>
              <span className="chart-tooltip__val">
                {rows[hover].s.scenarios_solved} / {rows[hover].s.scenarios_attempted}
              </span>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
