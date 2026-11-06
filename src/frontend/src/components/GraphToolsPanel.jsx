import { MODES } from "../graph/networkRules";
import {LAYOUT_PRESETS } from "../graph/layoutPresets";
import "./GraphToolsPanel.css";

/**
 * GraphToolsPanel: sidebar controls for the network canvas
 */
export default function GraphToolsPanel({
  mode,
  selectedCount,
  onModeChange,
  onDeleteSelected,
  onReset,
  onLoadPreset
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
      {/* Starter networks */}
      <div className="graph-tools__presets" role="group" aria-label="Network presets">
        <span className="graph-tools__heading">Network Presets</span>
        {Object.entries(LAYOUT_PRESETS).map(([id, preset]) => (
          <button type="button"
            key={id} 
            className="btn-secondary"
            onClick={() => onLoadPreset(id)} 
          >
            {preset.label}
          </button>
        ))}
      </div>
    </div>
  );
}
