const DEFAULT_IP_PREFIX = [10, 0, 0];

function toIpString(value, index) {
  if (Array.isArray(value) && value.length === 4) return value.join('.');
  if (typeof value === 'string' && value.trim()) return value.trim();
  return [...DEFAULT_IP_PREFIX, index + 1].join('.');
}

function numberOrDefault(value, fallback = 0) {
  if (value === null || value === undefined || value === '') return fallback;
  const parsed = Number(value);
  return Number.isFinite(parsed) && parsed >= 0 ? parsed : fallback;
}

/** Convert Cytoscape elements into the API's stable graph JSON format. */
export function serializeNetwork(cy) {
  const nodes = cy.nodes().map((node, index) => {
    const data = node.data();
    return {
      id: data.id,
      label: data.label || data.id,
      device_type: data.device_type || 'PC',
      device_ip: toIpString(data.device_ip, index),
      base_sec_level: numberOrDefault(data.base_sec_level),
      risk_level: numberOrDefault(data.risk_level),
      position: { x: Math.round(node.position('x')), y: Math.round(node.position('y')) },
    };
  });

  const edges = cy.edges().map((edge, index) => {
    const data = edge.data();
    return {
      id: data.id,
      source: data.source,
      target: data.target,
      cost: numberOrDefault(data.cost),
      bandwidth: numberOrDefault(data.bandwidth),
      connection_type: data.connection_type || 'TCP',
      source_port: numberOrDefault(data.source_port, 10000 + index),
      index: index + 1,
    };
  });

  return { nodes, edges };
}

export function serializeNode(node) {
  if (!node) return null;
  const data = node.data();
  return {
    id: data.id,
    label: data.label || data.id,
    device_type: data.device_type || 'PC',
    device_ip: data.device_ip || '',
    base_sec_level: data.base_sec_level ?? 0,
    risk_level: data.risk_level ?? 0,
  };
}
