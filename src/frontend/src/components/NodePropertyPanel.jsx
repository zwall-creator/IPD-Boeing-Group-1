import { useState } from "react";
import { X } from "lucide-react";
import { formatFieldValue } from "../graph/networkRules";
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

  // Edit: start the form from node's current value
  function startEditing() {
    setDraftType(node.device_type);
    setIsEditing(true);
  }

  // Save change: sned the new value to NetworkCanvas, back to view mode
  function handleSubmit(event) {
    event.preventDefault();
    onSave({ device_type: draftType });
    setIsEditing(false);
  }

  return (
    <section className="node-panel" aria-label="Node properties">
      <div className="node-panel__header">
          <h3 className="node-panel__title">{node.label}</h3>
          <button
            type="button"
            className="node-panel__close"
            aria-label="Close node properties"
            onClick={onClose}
        >
            <X size={14} aria-hidden="true" />
          </button>
      </div>
        {isEditing ? (
          <form className="node-panel__form" onSubmit={handleSubmit}>
            <label htmlFor="node-device-type">Device type</label>
            <select 
            id="node-device-type"
            value={draftType}
            onChange={(event) => setDraftType(event.target.value)}
            >
            {DEVICE_TYPES.map(({ type }) => (
              <option key={type} value={type}>
                {type}
              </option>
              ))}
            </select>
            <dl className="node-panel__fields">
              <dt>Security level</dt>
              <dd>{formatFieldValue(node.base_sec_level)}</dd>
            </dl>
            <div className="node-panel__actions">
              <button type="submit">Save changes</button>
              <button type="button" onClick={() => setIsEditing(false)}>
                Cancel
              </button>
            </div>
        </form>
      ) : (
        <>
          <dl className="node-panel__fields">
            <dt>Device type</dt>
            <dd>{node.device_type}</dd>
            <dt>Security level</dt>
            {/* TODO: add security level to node data */}
            <dd>{formatFieldValue(node.base_sec_level)}</dd>
          </dl>
          <div className="node-panel__actions">
            <button type="button" onClick={startEditing}>
              Edit
            </button>
          </div>
        </>
      )}
    </section>
  );
}