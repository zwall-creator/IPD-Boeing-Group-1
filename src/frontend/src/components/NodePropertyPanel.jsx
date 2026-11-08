import { useState } from "react";
import { Pencil, X } from "lucide-react";
import { formatFieldValue, checkNodeName } from "../graph/networkRules";
import { DEVICE_TYPES } from "../deviceIcons";
import "./NodePropertyPanel.css";

/**
 * Properties of selected node
 * node: plain copy of node's data (selectedNode from NetworkCanvas)
 * onClose: called when close button is clicked
 * onSave: called when save button is clicked
 */
export default function NodePropertyPanel({ node, onClose, onSave }) {
  // Edit mode
  const [isEditing, setIsEditing] = useState(false);
  // Draft device type for editing mode
  const [draftType, setDraftType] = useState(node.device_type);
  // Draft name for editing mode
  const [draftLabel, setDraftLabel] = useState(node.label);
  // Error message for name field
  const [nameError, setNameError] = useState(null);

  // Edit: start the form from node's current value
  function startEditing() {
    setDraftType(node.device_type);
    setDraftLabel(node.label);
    setNameError(null);
    setIsEditing(true);
  }

  // Save change: sned the new value to NetworkCanvas, back to view mode
  function handleSubmit(event) {
    event.preventDefault();
    const error = checkNodeName(draftLabel);
    if (error) {
      setNameError(error);
      return
    }
    onSave({ device_type: draftType, label: draftLabel.trim() });
    setIsEditing(false);
  }

  function handleKeyDown(event) {
    if (event.key === "Escape" && isEditing) {
      event.stopPropagation();
      setIsEditing(false);
    }
  }

  return (
    <section className="node-panel" aria-label="Node properties">
      <form 
        className="node-panel__form" 
        onSubmit={handleSubmit} 
        onKeyDown={handleKeyDown}
      >
        <div className="node-panel__header">
          {isEditing ? (
            <input
              className="node-panel__name-input"
              aria-label="Node name"
              autoFocus
              value={draftLabel}
              aria-invalid={nameError !== null}
              aria-describedby={nameError ? "node-name-error" : undefined}
              onChange={(event) => {
                setDraftLabel(event.target.value);
                setNameError(null); // hide error when typing
              }}
            />
          ) : (
            <h3 className="node-panel__title">{node.label}</h3>
          )}
          {/* Pencil only shows in view mode. While editing, Save/Cancel take over */}
          {!isEditing && (
            <button
              type="button"
              className="node-panel__icon-button"
              aria-label="Edit node properties"
              onClick={startEditing}
            >
              <Pencil size={16} aria-hidden="true" />
            </button>
          )}
          <button
            type="button"
            className="node-panel__icon-button"
            aria-label="Close node properties"
            onClick={onClose}
          >
            <X size={16} aria-hidden="true" />
          </button>
        </div>
        {nameError && (
          <p id="node-name-error" className="node-panel__error" role="alert">
            {nameError}
          </p>
        )}
          <dl className="node-panel__fields">
            <dt>Device type:</dt>
            <dd>
              {isEditing ? (
                <select
                  aria-label="Device type"
                  value={draftType}
                  onChange={(event) => setDraftType(event.target.value)}
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
            <dt>Security level:</dt>
            {/* TODO: make editable */}
            <dd>{formatFieldValue(node.base_sec_level)}</dd>
          </dl>
          {isEditing && (
            <div className="node-panel__actions">
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