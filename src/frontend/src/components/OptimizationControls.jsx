import React from 'react';
import './OptimizationControls.css';

/**
 * OptimizationControls
 *
 * Renders priority sliders for the four optimization parameters that map
 * directly to fields in NW_Structure.py:
 *   - securityWeight   → influences base_sec_level / security_level targets
 *   - costWeight       → influences edge cost
 *   - bandwidthWeight  → influences edge bandwidth
 *   - riskThreshold    → maps to node risk_level ceiling
 *
 * All values are 0–100 integers. The parent is responsible for state.
 */
export default function OptimizationControls({ params, onChange }) {
  const { securityWeight, costWeight, bandwidthWeight, riskThreshold } = params;

  const handleChange = (key) => (e) =>
    onChange({ ...params, [key]: Number(e.target.value) });

  const sliders = [
    {
      key: 'securityWeight',
      label: 'Security Priority',
      value: securityWeight,
      color: '#38bdf8',
      hint: 'Higher = favour nodes with stronger security levels',
    },
    {
      key: 'costWeight',
      label: 'Cost Weight',
      value: costWeight,
      color: '#4ade80',
      hint: 'Higher = minimise total edge cost in routing',
    },
    {
      key: 'bandwidthWeight',
      label: 'Bandwidth Weight',
      value: bandwidthWeight,
      color: '#a78bfa',
      hint: 'Higher = favour high-bandwidth connections',
    },
    {
      key: 'riskThreshold',
      label: 'Risk Threshold',
      value: riskThreshold,
      color: '#fb923c',
      hint: 'Maximum tolerated risk level per node (0 = strict)',
    },
  ];

  return (
    <div className="opt-controls">
      <h3 className="opt-controls__title">Optimization Priorities</h3>
      {sliders.map(({ key, label, value, color, hint }) => (
        <div key={key} className="opt-slider">
          <div className="opt-slider__header">
            <label htmlFor={`slider-${key}`} className="opt-slider__label">
              {label}
            </label>
            <span className="opt-slider__value" style={{ color }}>
              {value}
            </span>
          </div>
          <input
            id={`slider-${key}`}
            type="range"
            min={0}
            max={100}
            step={1}
            value={value}
            onChange={handleChange(key)}
            className="opt-slider__input"
            style={{ '--thumb-color': color, '--track-fill': color }}
            aria-label={label}
            aria-valuemin={0}
            aria-valuemax={100}
            aria-valuenow={value}
          />
          <div className="opt-slider__track-labels">
            <span>0</span>
            <span>50</span>
            <span>100</span>
          </div>
          <p className="opt-slider__hint">{hint}</p>
        </div>
      ))}

      {/* Visual summary bar */}
      <div className="opt-summary" aria-label="Priority distribution">
        <div
          className="opt-summary__segment"
          style={{ flex: securityWeight, background: '#38bdf8' }}
          title={`Security: ${securityWeight}`}
        />
        <div
          className="opt-summary__segment"
          style={{ flex: costWeight, background: '#4ade80' }}
          title={`Cost: ${costWeight}`}
        />
        <div
          className="opt-summary__segment"
          style={{ flex: bandwidthWeight, background: '#a78bfa' }}
          title={`Bandwidth: ${bandwidthWeight}`}
        />
        <div
          className="opt-summary__segment"
          style={{ flex: riskThreshold, background: '#fb923c' }}
          title={`Risk: ${riskThreshold}`}
        />
      </div>
      <div className="opt-summary__legend">
        <span style={{ color: '#38bdf8' }}>■ Security</span>
        <span style={{ color: '#4ade80' }}>■ Cost</span>
        <span style={{ color: '#a78bfa' }}>■ Bandwidth</span>
        <span style={{ color: '#fb923c' }}>■ Risk</span>
      </div>
    </div>
  );
}
