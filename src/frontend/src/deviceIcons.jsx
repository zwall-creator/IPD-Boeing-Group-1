import { renderToStaticMarkup } from 'react-dom/server'
import {
  Laptop,
  Monitor,
  Network,
  Router,
  Server,
  Smartphone,
} from 'lucide-react'

// Single source of truth for device types, used by the canvas and its type menu.
// Each `type` becomes a node's device_type (see src/simulation/NW_Structure.py).
const ICON_COLOR = '#ffffff'

// Cytoscape draws on a <canvas> and can't render React components,
// so each icon is also rendered to an SVG data URL for use as a node image.
const toDataUrl = (Icon) =>
  'data:image/svg+xml;charset=utf-8,' +
  encodeURIComponent(renderToStaticMarkup(<Icon color={ICON_COLOR} />))

// shape is a Cytoscape node shape; width/height are in px.
// Router uses round-diamond: plain "diamond" only registers clicks near its edges in Cytoscape.
export const DEVICE_TYPES = [
  { type: 'PC', Icon: Monitor, shape: 'ellipse', width: 42, height: 42 },
  {
    type: 'Laptop',
    Icon: Laptop,
    shape: 'round-rectangle',
    width: 42,
    height: 42,
  },
  {
    type: 'Cell Phone',
    Icon: Smartphone,
    shape: 'round-rectangle',
    width: 30,
    height: 46,
  },
  {
    type: 'Router',
    Icon: Router,
    shape: 'round-diamond',
    width: 52,
    height: 52,
  },
  { type: 'Switch', Icon: Network, shape: 'hexagon', width: 50, height: 44 },
  { type: 'Server', Icon: Server, shape: 'rectangle', width: 40, height: 40 },
].map((device) => ({ ...device, iconUrl: toDataUrl(device.Icon) }))
