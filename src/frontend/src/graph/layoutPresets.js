/**
 * Starter network templates for the canvas
 * Shared by NetworkCanvas and GraphToolsPanel
 * Each node is [deviceType, label, x, y]
 * Each edge is [sourceNodeIndex, targetNodeIndex]
 */
export const LAYOUT_PRESETS = {
  lan: {
    label: 'Office LAN',
    nodes: [
      ['Router', 'Gateway', 220, 190],
      ['Switch', 'Core Switch', 430, 190],
      ['PC', 'Workstation 1', 650, 110],
      ['PC', 'Workstation 2', 650, 270],
      ['Server', 'File Server', 430, 360],
    ],
    edges: [[0, 1], [1, 2], [1, 3], [1, 4]],
  },
  dmz: {
    label: 'DMZ',
    nodes: [
      ['Router', 'Internet Router', 150, 210],
      ['Switch', 'DMZ Switch', 360, 210],
      ['Server', 'Web Server', 600, 120],
      ['Server', 'Mail Server', 600, 300],
    ],
    edges: [[0, 1], [1, 2], [1, 3]],
  },
  wan: {
    label: 'Branch WAN',
    nodes: [
      ['Router', 'HQ Router', 180, 220],
      ['Router', 'Branch Router', 520, 120],
      ['Router', 'Remote Router', 520, 320],
      ['Switch', 'HQ Switch', 820, 220],
      ['Server', 'Application Server', 1030, 220],
    ],
    edges: [[0, 1], [0, 2], [0, 3], [3, 4]],
  },
};