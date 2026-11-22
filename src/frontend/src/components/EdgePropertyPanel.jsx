import { useState } from "react";
import { Pencil, X } from "lucide-react";
import { formatFieldValue, describeConnection } from "../graph/networkRules";
import { CONNECTION_TYPES, checkEdgeForm, toEdgeFormValues } from "../graph/edgeRules";
import "./PropertyPanel.css";

/**
 * EdgePropertyPanel: shows and edits the selected edge's properties (#127)
 * edge: plain copy of the edge's data plus sourceLabel/targetLabel (selectedEdge from NetworkCanvas)
 * onClose: called when the close button is clicked
 * onSave: called with { cost, bandwidth, connection_type } once Save changes passes the checks
 */
export default function EdgePropertyPanel({ edge, onClose, onSave }) {
  const [isEditing, setIsEditing] = useState(false);
  // Form text for each field ("" = Not set)
  const [draft, setDraft] = useState(toEdgeFormValues(edge));
  // Error message per field, e.g. { cost: "Cost must be ..." }; {} = no errors
  const [errors, setErrors] = useState({});

  // One edge always goes from its source to its target
  const { arrow, words } = describeConnection({ outgoing: true, incoming: false });

  // Edit: start the form from the edge's current values
  function startEditing() {
    setDraft(toEdgeFormValues(edge));
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
    const result = checkEdgeForm(draft);
    if (result.values === null) {
      setErrors(result.errors); // stay in edit mode; the edge isn't changed
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

  // Text input for cost or bandwidth, with its error message linked for screen readers
  function numberField(key, label) {
    const errorId = `edge-${key}-error`;
    return (
      <>
        <input
          inputMode="numeric"
          aria-label={label}
          aria-invalid={Boolean(errors[key])}
          aria-describedby={errors[key] ? errorId : undefined}
          autoFocus={key === "cost"}
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
    <section className="property-panel" aria-label="Edge properties">
      <form
        className="property-panel__form"
        onSubmit={handleSubmit}
        onKeyDown={handleKeyDown}
      >
        <div className="property-panel__header">
          <h3 className="property-panel__title">
            {edge.sourceLabel}{" "}
            <span className="property-panel__arrow" aria-hidden="true">{arrow}</span>
            <span className="visually-hidden">{words}</span>{" "}
            {edge.targetLabel}
          </h3>
          {/* Pencil only shows in view mode. While editing, Save/Cancel take over */}
          {!isEditing && (
            <button
              type="button"
              className="property-panel__icon-button"
              aria-label="Edit edge properties"
              onClick={startEditing}
            >
              <Pencil size={16} aria-hidden="true" />
            </button>
          )}
          <button
            type="button"
            className="property-panel__icon-button"
            aria-label="Close edge properties"
            onClick={onClose}
          >
            <X size={16} aria-hidden="true" />
          </button>
        </div>

        <dl className="property-panel__fields">
          <dt>Cost:</dt>
          <dd>{isEditing ? numberField("cost", "Cost") : formatFieldValue(edge.cost)}</dd>
          <dt>Bandwidth:</dt>
          <dd>
            {isEditing ? numberField("bandwidth", "Bandwidth") : formatFieldValue(edge.bandwidth)}
          </dd>
          <dt>Connection type:</dt>
          <dd>
            {isEditing ? (
              <select
                aria-label="Connection type"
                value={draft.connection_type}
                onChange={(event) => updateField("connection_type", event.target.value)}
              >
                <option value="">Not set</option>
                {CONNECTION_TYPES.map((type) => (
                  <option key={type} value={type}>
                    {type}
                  </option>
                ))}
              </select>
            ) : (
              formatFieldValue(edge.connection_type)
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
