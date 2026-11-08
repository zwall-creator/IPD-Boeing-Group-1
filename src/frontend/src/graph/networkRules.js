/**
 * Shared network-editor constants and rules
 * MODES: shared by GraphToolsPanel (button labels) and NetworkCanvas (hint text)
 * isNotSet / formatFieldValue: shared by NodePropertyPanel and EdgePropertyPanel
 * checkNodeName: shared with NodePropertyPanel
 * describeConnection: used by NodePropertyPanel
 */
export const MODES = [
  {
    id: "select",
    label: "Select",
    hint: "Click to select · Drag to move · Shift+Click to multi-select",
  },
  {
    id: "add-node",
    label: "Add node",
    hint: "Click empty space, then pick a device type",
  },
  { id: "add-edge", label: "Add edge", hint: "Click the source node" },
];

// True if field has no value (null or undefined)
export function isNotSet(value) {
  return value === null || value === undefined;
}

// Text for property panels: "Not set" if not set, else value as text
export function formatFieldValue(value) {
  return isNotSet(value) ? "Not set" : String(value);
}

// Error message for node name being empty
// Null = valid name
export function checkNodeName(name) {
  if (name.trim() === "") {
    return "Name can't be empty";
  }
  return null;
}

// Display connection and direction
export function describeConnection({ outgoing, incoming }) {
  if (outgoing && incoming) {
    return { arrow: "↔", words: "both ways with" };
  }
  if (outgoing) {
    return { arrow: "→", words: "to" };
  }
  return { arrow: "←", words: "from" };
}
