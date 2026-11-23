// Client for the report generation service (computation/reports/routes.py)
import { BACKEND_URL } from '../hooks/useEventSource';

async function getJson(path, options) {
  try {
    const res = await fetch(`${BACKEND_URL}${path}`, options);
    const body = await res.json().catch(() => ({}));
    if (!res.ok) return { ok: false, error: body.error || `Request failed with status ${res.status}` };
    return { ok: true, data: body };
  } catch {
    return { ok: false, error: 'The computation service could not be reached.' };
  }
}

export const listReports = () => getJson('/reports');

export const getReport = (id) => getJson(`/reports/${encodeURIComponent(id)}`);

export const generateReport = (body = {}) =>
  getJson('/reports/generate', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  });

export const reportPdfUrl = (id, { inline = false } = {}) =>
  `${BACKEND_URL}/reports/${encodeURIComponent(id)}/pdf${inline ? '?inline=1' : ''}`;

// Formatting shared by the page and charts (mirrors pdf_renderer.py)
export function fmtMs(ms) {
  if (ms === null || ms === undefined) return '–';
  if (ms >= 10000) return `${(ms / 1000).toFixed(0)} s`;
  if (ms >= 1000) return `${(ms / 1000).toFixed(2)} s`;
  if (ms >= 10) return `${ms.toFixed(0)} ms`;
  return `${ms.toFixed(2)} ms`;
}

export function fmtPct(v, digits = 1) {
  return v === null || v === undefined ? '–' : `${v.toFixed(digits)}%`;
}

export function fmtDate(iso) {
  const d = new Date(iso);
  return Number.isNaN(d.getTime())
    ? iso
    : d.toLocaleString(undefined, { dateStyle: 'medium', timeStyle: 'short' });
}

export const STATUS_LABEL = {
  optimal: 'Optimal',
  feasible: 'Feasible',
  infeasible: 'Infeasible',
  timeout: 'Timed out',
  skipped: 'Skipped',
};
