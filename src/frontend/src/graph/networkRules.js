/**
 * networkRules.js: shared network-editor constants and rules
 * only MODES lives here, shared by GraphToolsPanel (button labels)
 * and NetworkCanvas (hint text). The add/delete/edge rules move in later.
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
