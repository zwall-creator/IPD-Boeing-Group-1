import { useState } from "react";
import { Pencil, X } from "lucide-react";
import {
  formatFieldValue,
  describeConnection,
  checkNodeForm,
  toNodeFormValues,
} from "../graph/networkRules";
import { DEVICE_TYPES } from "../deviceIcons";
import "./PropertyPanel.css";

/**
 * NodePropertyPanel: shows and edits the selected node's properties
 * node: plain copy of the node's data plus its connections (selectedNode from NetworkCanvas)
 * onClose: called when the close button is clicked
 * onSave: called with { label, device_type, device_ip, base_sec_level, risk_level }
 *         once Save changes passes the checks
 */
export default function NodePropertyPanel({ node, onClose, onSave }) {
  const [isEditing, setIsEditing] = useState(false);
  // Form text for each field ("" = Not set)
  const [draft, setDraft] = useState(toNodeFormValues(node));
  // Error message per field, e.g. { device_ip: "IP address must ..." }; {} = no errors
  const [errors, setErrors] = useState({});

  // Edit: start the form from the node's current values
  function startEditing() {
    setDraft(toNodeFormValues(node));
    setErrors({});
    setIsEditing(true);
  }

  // Change one field of the draft and hide that field's error
  function updateField(key, value) {
    setDraft({ ...draft, [key]: value });
    setErrors({ ...errors, [key]: undefined });
  }

  // Save changes: check every field; any bad field blocks the whole save
  function handleSubmit(event) {
    event.preventDefault();
    const result = checkNodeForm(draft);
    if (result.values === null) {
      setErrors(result.errors); // stay in edit mode; the node isn't changed
      return;
    }
    onSave(result.values);
    setIsEditing(false);
  }

  // Escape while editing: cancel the edit but keep the panel open.
  // stopPropagation keeps NetworkCanvas's window listener from closing the panel.
  function handleKeyDown(event) {
    if (event.key === "Escape" && isEditing) {
      event.stopPropagation();
      setIsEditing(false);
    }
  }

  // Text input inside the fields grid, with its error message linked for screen readers
  function textField(key, label, placeholder) {
    const errorId = `node-${key}-error`;
    return (
      <>
        <input
          inputMode="decimal"
          aria-label={label}
          placeholder={placeholder}
          aria-invalid={Boolean(errors[key])}
          aria-describedby={errors[key] ? errorId : undefined}
          value={draft[key]}
          onChange={(event) => updateField(key, event.target.value)}
        />
        {errors[key] && (
          <p id={errorId} className="property-panel__error" role="alert">
            {errors[key]}
          </p>
        )}
      </>
    );
  }

  return (
    <section className="property-panel" aria-label="Node properties">
      <form
        className="property-panel__form"
        onSubmit={handleSubmit}
        onKeyDown={handleKeyDown}
      >
        <div className="property-panel__header">
          {isEditing ? (
            <input
              className="property-panel__name-input"
              aria-label="Node name"
              autoFocus
              aria-invalid={Boolean(errors.label)}
              aria-describedby={errors.label ? "node-label-error" : undefined}
              value={draft.label}
              onChange={(event) => updateField("label", event.target.value)}
            />
          ) : (
            <h3 className="property-panel__title">{node.label}</h3>
          )}
          {/* Pencil only shows in view mode. While editing, Save/Cancel take over */}
          {!isEditing && (
            <button
              type="button"
              className="property-panel__icon-button"
              aria-label="Edit node properties"
              onClick={startEditing}
            >
              <Pencil size={16} aria-hidden="true" />
            </button>
          )}
          <button
            type="button"
            className="property-panel__icon-button"
            aria-label="Close node properties"
            onClick={onClose}
          >
            <X size={16} aria-hidden="true" />
          </button>
        </div>
        {errors.label && (
          <p id="node-label-error" className="property-panel__error" role="alert">
            {errors.label}
          </p>
        )}

        <dl className="property-panel__fields">
          <dt>Device type:</dt>
          <dd>
            {isEditing ? (
              <select
                aria-label="Device type"
                value={draft.device_type}
                onChange={(event) => updateField("device_type", event.target.value)}
              >
                {DEVICE_TYPES.map(({ type }) => (
                  <option key={type} value={type}>
                    {type}
                  </option>
                ))}
              </select>
            ) : (
              node.device_type
            )}
          </dd>
          <dt>IP address:</dt>
          <dd>
            {isEditing
              ? textField("device_ip", "IP address", "e.g. 10.0.0.1")
              : formatFieldValue(node.device_ip)}
          </dd>
          <dt>Security level:</dt>
          <dd>
            {isEditing
              ? textField("base_sec_level", "Security level", "e.g. 2.5")
              : formatFieldValue(node.base_sec_level)}
          </dd>
          <dt>Risk level:</dt>
          <dd>
            {isEditing
              ? textField("risk_level", "Risk level", "e.g. 2.5")
              : formatFieldValue(node.risk_level)}
          </dd>
          <dt>Connections:</dt>
          <dd>
            {node.connections.length === 0 ? (
              "None"
            ) : (
              <ul className="property-panel__connections">
                {node.connections.map((connection) => {
                  const { arrow, words } = describeConnection(connection);
                  return (
                    <li key={connection.id}>
                      <span className="property-panel__arrow" aria-hidden="true">{arrow}</span>
                      <span className="visually-hidden">{words}</span> {connection.label}
                    </li>
                  );
                })}
              </ul>
            )}
          </dd>
        </dl>

        {isEditing && (
          <div className="property-panel__actions">
            <button type="submit">Save changes</button>
            <button type="button" onClick={() => setIsEditing(false)}>
              Cancel
            </button>
          </div>
        )}
      </form>
    </section>
  );
}
