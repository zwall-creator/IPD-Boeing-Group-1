/**
 * Reports page: solver performance comparison.
 * Data comes from the computation service (/reports). Until real benchmark
 * runs are stored, the backend serves sample data and flags it with
 * is_sample_data, which shows the banner below.
 */
import React, { useCallback, useEffect, useState } from 'react';
import { Download, FileText, Plus, RefreshCw } from 'lucide-react';
import {
  fmtDate, fmtMs, fmtPct, generateReport, getReport, listReports, reportPdfUrl, STATUS_LABEL,
} from '../api/reports';
import { Legend, RuntimeChart, SolverBarChart, seriesVar } from './ReportCharts';
import './ReportsView.css';

export default function ReportsView() {
  const [list, setList] = useState([]);
  const [selectedId, setSelectedId] = useState(null);
  const [report, setReport] = useState(null);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(true);
  const [busy, setBusy] = useState(false);

  const loadList = useCallback(async (selectId) => {
    setLoading(true);
    setError(null);
    const res = await listReports();
    if (!res.ok) {
      setError(res.error);
      setLoading(false);
      return;
    }
    setList(res.data);
    setSelectedId((cur) => selectId ?? cur ?? res.data[0]?.id ?? null);
    setLoading(false);
  }, []);

  useEffect(() => { loadList(); }, [loadList]);

  useEffect(() => {
    if (!selectedId) return;
    let cancelled = false;
    getReport(selectedId).then((res) => {
      if (cancelled) return;
      if (res.ok) setReport(res.data);
      else setError(res.error);
    });
    return () => { cancelled = true; };
  }, [selectedId]);

  const handleGenerate = async () => {
    setBusy(true);
    const res = await generateReport();
    setBusy(false);
    if (res.ok) await loadList(res.data.id);
    else setError(res.error);
  };

  if (error && !report) {
    return (
      <div className="reports-view reports-view--center">
        <div className="api-feedback api-feedback--error" role="alert">
          <strong>Could not load reports</strong>
          <span>{error}</span>
        </div>
        <button type="button" className="btn-secondary reports-btn" onClick={() => loadList()}>
          <RefreshCw size={14} aria-hidden="true" /> Retry
        </button>
      </div>
    );
  }
  if (loading && !report) {
    return <div className="reports-view reports-view--center"><p className="reports-muted">Loading reports…</p></div>;
  }
  if (!report) {
    return <div className="reports-view reports-view--center"><p className="reports-muted">No reports yet.</p></div>;
  }

  const solverIdx = Object.fromEntries(report.solvers.map((s, i) => [s.id, i]));
  const solver = Object.fromEntries(report.solvers.map((s) => [s.id, s]));
  const scenario = Object.fromEntries(report.scenarios.map((s) => [s.id, s]));
  const p = report.config?.opt_params ?? {};

  return (
    <div className="reports-view">
      {/* Toolbar */}
      <div className="reports-toolbar">
        <label className="reports-select">
          <FileText size={15} aria-hidden="true" />
          <span className="visually-hidden">Report</span>
          <select value={selectedId ?? ''} onChange={(e) => setSelectedId(e.target.value)}>
            {list.map((r) => (
              <option key={r.id} value={r.id}>{r.title} · {fmtDate(r.generated_at)}</option>
            ))}
          </select>
        </label>
        <div className="reports-toolbar__actions">
          <button type="button" className="btn-secondary reports-btn" onClick={handleGenerate} disabled={busy}>
            <Plus size={14} aria-hidden="true" /> {busy ? 'Generating…' : 'Generate sample report'}
          </button>
          <a className="btn-secondary reports-btn" href={reportPdfUrl(report.id, { inline: true })}
            target="_blank" rel="noreferrer">
            Open PDF
          </a>
          <a className="btn-primary reports-btn" href={reportPdfUrl(report.id)} download>
            <Download size={14} aria-hidden="true" /> Download PDF
          </a>
        </div>
      </div>

      {/* Header */}
      <header className="reports-header">
        <h1>{report.title}</h1>
        <p className="reports-muted">
          {report.id} · Generated {fmtDate(report.generated_at)} · {report.solvers.length} solvers ·{' '}
          {report.scenarios.length} scenarios · {report.config?.trials} trials per run ·{' '}
          {report.config?.time_limit_s} s time limit
        </p>
        <p className="reports-muted">
          Weights: security {p.securityWeight}, cost {p.costWeight}, bandwidth {p.bandwidthWeight},
          risk threshold {p.riskThreshold}
        </p>
      </header>

      {report.is_sample_data && (
        <div className="reports-banner" role="note">
          <strong>Sample data.</strong> These results are generated placeholders that show the report
          layout. They are not measurements from the solvers.
        </div>
      )}

      {/* Per-solver tiles */}
      <section className="reports-tiles" aria-label="Solver summary">
        {report.summary.map((s) => {
          const sv = solver[s.solver_id];
          const largest = scenario[s.largest_solved_scenario];
          return (
            <div key={s.solver_id} className="reports-tile">
              <div className="reports-tile__head">
                <span className="chart-legend__swatch" style={{ background: seriesVar(solverIdx[s.solver_id]) }} aria-hidden="true" />
                <div>
                  <strong>{sv.name}</strong>
                  <span className="reports-muted">{sv.paradigm}</span>
                </div>
              </div>
              <dl>
                <div><dt>Scenarios solved</dt><dd>{s.scenarios_solved} / {s.scenarios_attempted}</dd></div>
                <div><dt>Valid runs</dt><dd>{fmtPct(100 * s.success_rate, 0)}</dd></div>
                <div><dt>Mean optimality gap</dt><dd>{fmtPct(s.optimality_gap_pct_mean, 2)}</dd></div>
                <div><dt>Largest solved</dt><dd>{largest ? `${largest.name} (${largest.nodes}n)` : '–'}</dd></div>
              </dl>
            </div>
          );
        })}
      </section>

      {/* Charts */}
      <section className="reports-card">
        <h2>Runtime vs network size</h2>
        <p className="reports-muted">
          Mean runtime per scenario, log scale. A line stops where the solver timed out or could not run.
        </p>
        <Legend solvers={report.solvers} />
        <RuntimeChart report={report} />
      </section>

      <div className="reports-grid">
        <section className="reports-card">
          <h2>Mean optimality gap</h2>
          <p className="reports-muted">Distance above the best objective found on each scenario. Lower is better.</p>
          <SolverBarChart report={report} metric="optimality_gap_pct_mean" label="Mean optimality gap"
            format={(v) => fmtPct(v, 1)} />
        </section>
        <section className="reports-card">
          <h2>Valid runs</h2>
          <p className="reports-muted">Trials that returned a placement satisfying every constraint. Higher is better.</p>
          <SolverBarChart report={report} metric="success_rate" label="Valid runs"
            format={(v) => (v === null ? '–' : fmtPct(100 * v, 0))} />
        </section>
      </div>

      {/* Detailed table (also the accessible view of the chart data) */}
      <section className="reports-card">
        <h2>Detailed results</h2>
        <div className="reports-table-wrap">
          <table className="reports-table">
            <thead>
              <tr>
                <th scope="col">Scenario</th>
                <th scope="col">Solver</th>
                <th scope="col">Status</th>
                <th scope="col" className="num">Runtime (mean ± sd)</th>
                <th scope="col" className="num">Objective</th>
                <th scope="col" className="num">Gap</th>
                <th scope="col" className="num">Valid</th>
                <th scope="col">Notes</th>
              </tr>
            </thead>
            <tbody>
              {report.scenarios.map((sc) => report.results
                .filter((r) => r.scenario_id === sc.id)
                .map((r, j, arr) => (
                  <tr key={`${sc.id}-${r.solver_id}`} className={j === arr.length - 1 ? 'group-end' : ''}>
                    {j === 0 && (
                      <th scope="row" rowSpan={arr.length}>
                        {sc.name}
                        <span className="reports-muted">{sc.nodes} nodes · {sc.links} links</span>
                      </th>
                    )}
                    <td>
                      <span className="chart-legend__swatch" style={{ background: seriesVar(solverIdx[r.solver_id]) }} aria-hidden="true" />
                      {solver[r.solver_id].name}
                    </td>
                    <td><span className={`status-pill status-pill--${r.status}`}>{STATUS_LABEL[r.status] ?? r.status}</span></td>
                    <td className="num">
                      {r.runtime_ms_mean === null ? '–' : `${fmtMs(r.runtime_ms_mean)} ± ${fmtMs(r.runtime_ms_std)}`}
                    </td>
                    <td className="num">{r.objective_mean === null ? '–' : r.objective_mean.toFixed(2)}</td>
                    <td className="num">{fmtPct(r.optimality_gap_pct, 1)}</td>
                    <td className="num">{Math.round(r.success_rate * r.trials)}/{r.trials}</td>
                    <td className="reports-note">
                      {r.extra?.qubits && r.status !== 'skipped' && `${r.extra.qubits} qubits, depth ${r.extra.circuit_depth}${r.note ? '; ' : ''}`}
                      {r.note}
                    </td>
                  </tr>
                )))}
            </tbody>
          </table>
        </div>
        <p className="reports-muted reports-defs">
          Objective is the total security gap across nodes (risk minus security level); lower is better.
          Gap is measured against the best objective any solver found for that scenario.
        </p>
      </section>
    </div>
  );
}
