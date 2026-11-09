/**
 * Shared edge-editor constants and rules
 * Rules based on NW_Node.add_connection
 */
import { isNotSet } from "./networkRules.js";

// Valid connection types
export const CONNECTION_TYPES = ["TCP", "UDP"];

function parseWholeNumber(text, label) {
  const trimmed = text.trim();
  if (trimmed === "") return { value: null };
  if (!/^\d+$/.test(trimmed)) {
    return { error: `${label} must be a whole number, 0 or more` };
  }
  return { value: Number(trimmed) };
}

// Checks the edge form: {cost, bandwidth, connection_type}
// Returns { values, errors }:
//      values: ready to save or null if fields are wrong
//      errors: error message for invalid fields
export function checkEdgeForm(form) {
  const errors = {};
  const cost = parseWholeNumber(form.cost, "Cost");
  const bandwidth = parseWholeNumber(form.bandwidth, "Bandwidth");
  if (cost.error) { errors.cost = cost.error; }
  if (bandwidth.error) { errors.bandwidth = bandwidth.error; }
  const type = form.connection_type === "" ? null : form.connection_type;
  if (type !== null && !CONNECTION_TYPES.includes(type)) {
    errors.connection_type = "Connection type must be TCP or UDP";
  }

  // Bad field blocks the save
  if (Object.keys(errors).length > 0) { return { values: null, errors }; }
  return {
    values: { cost: cost.value, bandwidth: bandwidth.value, connection_type: type },
    errors,
  };
}

// Turn edge's saved values into text for form inputs
export function toEdgeFormValues(edge) {
  return {
    cost: isNotSet(edge.cost) ? "" : String(edge.cost),
    bandwidth: isNotSet(edge.bandwidth) ? "" : String(edge.bandwidth),
    connection_type: edge.connection_type ?? "",
  };
}
