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

// IP address from the form. "" is allowed: the serializer assigns 10.0.0.n when sending.
// Mirrors _ip in src/computation/network_adapter.py: four numbers 0-255, no leading zeros
function checkIp(text) {
  const trimmed = text.trim();
  if (trimmed === "") return { value: null };
  const parts = trimmed.split(".");
  const valid =
    parts.length === 4 &&
    parts.every((part) => /^(0|[1-9]\d{0,2})$/.test(part) && Number(part) <= 255);
  if (!valid) return { error: "IP address must look like 10.0.0.1 (four numbers 0-255)" };
  return { value: trimmed };
}

// Security or risk level from the form. "" -> null (Not set), "2" or "2.5" -> a number.
// Mirrors _number in network_adapter.py: any number 0 or more, decimals allowed
function parseLevel(text, label) {
  const trimmed = text.trim();
  if (trimmed === "") return { value: null };
  if (!/^\d+(\.\d+)?$/.test(trimmed)) {
    return { error: `${label} must be a number, 0 or more` };
  }
  return { value: Number(trimmed) };
}

// Checks the node form. form: { label, device_type, device_ip, base_sec_level, risk_level } as text.
// Returns { values, errors } like checkEdgeForm: values is null if any field is wrong
export function checkNodeForm(form) {
  const errors = {};
  const labelError = checkNodeName(form.label);
  const ip = checkIp(form.device_ip);
  const security = parseLevel(form.base_sec_level, "Security level");
  const risk = parseLevel(form.risk_level, "Risk level");
  if (labelError) errors.label = labelError;
  if (ip.error) errors.device_ip = ip.error;
  if (security.error) errors.base_sec_level = security.error;
  if (risk.error) errors.risk_level = risk.error;

  if (Object.keys(errors).length > 0) return { values: null, errors };
  return {
    values: {
      label: form.label.trim(),
      device_type: form.device_type,
      device_ip: ip.value,
      base_sec_level: security.value,
      risk_level: risk.value,
    },
    errors,
  };
}

// Turns a node's saved values into text for the form inputs (null -> "")
export function toNodeFormValues(node) {
  return {
    label: node.label,
    device_type: node.device_type,
    device_ip: node.device_ip ?? "",
    base_sec_level: isNotSet(node.base_sec_level) ? "" : String(node.base_sec_level),
    risk_level: isNotSet(node.risk_level) ? "" : String(node.risk_level),
  };
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
