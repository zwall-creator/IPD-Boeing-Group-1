/**
 * Shared cytoscape style for network graphs
 * STYLE: used by NetworkCanvas and the simulation frame in App
 */
import { DEVICE_TYPES, getDeviceIconUrl } from "../deviceIcons";

// Color Codings
const VT_MAROON = "#861F41";
const VT_ORANGE = "#E5751F";
const HOKIE_STONE = "#75787B";
const TEXT = "#1f2933";

export const STYLE = [
  {
    selector: "node",
    style: {
      "background-color": VT_MAROON,
      width: 42,
      height: 42,
      "background-image": (node) =>
        node.data("custom_image") || getDeviceIconUrl(node.data("device_type")),
      "background-width": "58%",
      "background-height": "58%",
      label: "data(label)",
      color: TEXT,
      "font-size": 11,
      "text-valign": "bottom",
      "text-margin-y": 6,
    },
  },
  ...DEVICE_TYPES.map((d) => ({
    selector: `node[device_type = "${d.type}"]`,
    style: {
      shape: d.shape,
      width: d.width,
      height: d.height,
      ...(d.shape === "round-diamond" && {
        "background-width": "44%",
        "background-height": "44%",
      }),
    },
  })),
  {
    selector: "edge",
    style: {
      width: 2,
      "line-color": HOKIE_STONE,
      "target-arrow-color": HOKIE_STONE,
      "target-arrow-shape": "triangle",
      "curve-style": "bezier",
    },
  },
  {
    selector: "node:selected, node.edge-source",
    style: {
      "background-color": VT_ORANGE,
      "outline-width": 3,
      "outline-color": VT_ORANGE,
      "outline-offset": 2,
    },
  },
  {
    selector: "edge:selected",
    style: {
      width: 3,
      "line-color": VT_ORANGE,
      "target-arrow-color": VT_ORANGE,
    },
  },
];