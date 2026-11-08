/**
 * Shared network-editor constants and rules
 * MODES: shared by GraphToolsPanel (button labels) and NetworkCanvas (hint text)
 * isNotSet / formatFieldValue: shared by NodePropertyPanel and EdgePropertyPanel
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
