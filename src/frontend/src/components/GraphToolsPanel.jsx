import { MODES } from "../graph/networkRules";
import "./GraphToolsPanel.css";

/**
 * GraphToolsPanel: sidebar controls for the network canvas (issue #37).
 * Replaces the toolbar that sat on the canvas. Presentational component:
 * no state; App passes values in as props and gets clicks back via callbacks.
 * AI-assisted: drafted with Claude, reviewed by Hudson.
 */
export default function GraphToolsPanel({
  mode,
  selectedCount,
  onModeChange,
  onDeleteSelected,
  onReset,
}) {
  return (
    <div className="graph-tools" role="group" aria-label="Graph tools">
      {MODES.map((m) => (
        <button
          key={m.id}
          type="button"
          className="btn-secondary"
          aria-pressed={mode === m.id}
          onClick={() => onModeChange(m.id)}
        >
          {m.label}
        </button>
      ))}
      <button
        type="button"
        className="btn-secondary"
        onClick={onDeleteSelected}
        disabled={selectedCount === 0}
      >
        Delete{selectedCount > 0 ? ` (${selectedCount})` : ""}
      </button>
      <button type="button" className="btn-secondary" onClick={onReset}>
        Reset Canvas
      </button>
    </div>
  );
}
