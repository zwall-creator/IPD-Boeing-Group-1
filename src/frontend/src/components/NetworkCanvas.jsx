import {
  useEffect,
  useEffectEvent,
  useImperativeHandle,
  useRef,
  useState,
} from "react";
import cytoscape from "cytoscape";
import { DEVICE_TYPES } from "../deviceIcons";
import { MODES } from "../graph/networkRules";
import { LAYOUT_PRESETS } from "../graph/layoutPresets";
import NodePropertyPanel from "./NodePropertyPanel";
import EdgePropertyPanel from "./EdgePropertyPanel";
import { serializeNetwork } from "../graph/networkSerializer";
import "./NetworkCanvas.css";

// Color Codings
const VT_MAROON = "#861F41";
const VT_ORANGE = "#E5751F";
const HOKIE_STONE = "#75787B";
const TEXT = "#1f2933";

const NODE_FIELDS = { device_ip: null, base_sec_level: null, risk_level: null };
const EDGE_FIELDS = { cost: 0, bandwidth: 0, connection_type: "TCP", source_port: null };

// Zoom used for preset loads
const PRESET_ZOOM = 1.0;

const STYLE = [
  {
    selector: "node",
    style: {
      "background-color": VT_MAROON,
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
      "background-image": d.iconUrl,
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
    style: { "background-color": VT_ORANGE },
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

export default function NetworkCanvas({
  mode = "select",
  onSelectionChange = () => {},
  ref,
}) {
  const containerRef = useRef(null);
  const typeMenuRef = useRef(null);
  const cyRef = useRef(null);
  const nodeCountRef = useRef(0);
  const edgeCountRef = useRef(0);
  const typeCountsRef = useRef({});
  const [edgeSourceId, setEdgeSourceId] = useState(null);
  const [notice, setNotice] = useState(null);
  const [typeMenu, setTypeMenu] = useState(null);
  const [selectedNode, setSelectedNode] = useState(null);
  const [selectedEdge, setSelectedEdge] = useState(null);

  // Next default name for a device
  // Increments type count
  // Count only goes up, never repeats a previously used number
  function nextDefaultLabel(type) {
    const count = (typeCountsRef.current[type] ?? 0) + 1;
    typeCountsRef.current[type] = count;
    return `${type} ${count}`;
  }

  function addNode(type) {
    cyRef.current.add({
      group: "nodes",
      data: {
        id: `n${++nodeCountRef.current}`,
        label: nextDefaultLabel(type),
        device_type: type,
        autoLabel: true,
        ...NODE_FIELDS,
      },
      position: typeMenu.position,
    });
    setTypeMenu(null);
  }

  function loadPreset(presetId) {
    const preset = LAYOUT_PRESETS[presetId]
    if (!preset || !cyRef.current) return

    cyRef.current.elements().remove()
    nodeCountRef.current = 0
    edgeCountRef.current = 0
    typeCountsRef.current = {}
    setEdgeSourceId(null)
    setTypeMenu(null)
    setNotice(`${preset.label} layout loaded`)

    const nodes = preset.nodes.map(([type, label, x, y]) => {
      typeCountsRef.current[type] = (typeCountsRef.current[type] ?? 0) + 1
      return {
        group: 'nodes',
        data: {
          id: `n${++nodeCountRef.current}`,
          label,
          device_type: type,
          autoLabel: false,
          ...NODE_FIELDS,
        },
        position: { x, y },
      }
    })
    const edges = preset.edges.map(([source, target]) => ({
      group: 'edges',
      data: {
        id: `e${++edgeCountRef.current}`,
        source: `n${source + 1}`,
        target: `n${target + 1}`,
        ...EDGE_FIELDS,
      },
    }))
    cyRef.current.add([...nodes, ...edges])
    cyRef.current.layout({ name: 'preset', fit: true, padding: 50 }).run()
    if (cyRef.current.zoom() > PRESET_ZOOM) {
      cyRef.current.zoom(PRESET_ZOOM) // set the zoom level
      cyRef.current.center()          // pan so the network is in the middle
    }
  }

  function deleteSelected() {
    cyRef.current.$(":selected").remove();
  }

  function getTopology() {
    return serializeNetwork(cyRef.current);
  }

  // Check if canvas is empty
  function isEmpty() {
    return cyRef.current.elements().length === 0;
  }

  // Clear the network back to starting state
  function clear() {
    cyRef.current.elements().remove();
    nodeCountRef.current = 0;
    edgeCountRef.current = 0;
    typeCountsRef.current = {};
    setEdgeSourceId(null);
    setNotice(null);
    setTypeMenu(null);
    cyRef.current.reset();
  }

  // Plain copy of a node for the panel, plus its connections
  function snapshotNode(node) {
    const connections = node.neighborhood("node").map((other) => ({
      id: other.id(),
      label: other.data("label"),
      outgoing: node.edgesTo(other).nonempty(), // edge from this node to the other
      incoming: other.edgesTo(node).nonempty(), // edge from the other node to this one
    }));
    return { ...node.data(), connections };
  }

  // Plain copy of an edge for the panel, plus the nodes it connects
  function snapshotEdge(edge) {
    return {
      ...edge.data(),
      sourceLabel: edge.source().data("label"),
      targetLabel: edge.target().data("label"),
    };
  }

  // Panel close button
  function closePanel() {
    cyRef.current.elements().unselect();
  }

  // Panel Save Changes button: writes new values onto cytoscape node
  function saveNode(nodeId, values) {
    const node = cyRef.current.getElementById(nodeId);
    const nameEdited = values.label !== node.data("label");
    const typeChanged = values.device_type !== node.data("device_type");
    // Still a default name if it was before and user hasn't updated it manually
    const autoLabel = node.data("autoLabel") && !nameEdited;

    node.data({
      ...values,
    autoLabel,
    // Default name + new type
    label: autoLabel && typeChanged ? nextDefaultLabel(values.device_type) : values.label,
  });
    // Refresh panel's copy
    setSelectedNode(snapshotNode(node));
  }

  // Edge panel's save changes
  function saveEdge(edgeId, values) {
    const edge = cyRef.current.getElementById(edgeId);
    edge.data(values);
    // Data changes don't fire select/unselect, so refresh the panel's copy here
    setSelectedEdge(snapshotEdge(edge));
  }

  // App's sidebar buttons call deleteSelected(), isEmpty(), or clear()
  // App's layout buttons call loadPreset(presetId)
  useImperativeHandle(ref, () => ({
    deleteSelected,
    getTopology,
    isEmpty,
    clear,
    loadPreset,
  }));

  const resetInteraction = useEffectEvent(() => {
    cyRef.current.elements().unselect();
    setEdgeSourceId(null);
    setNotice(null);
    setTypeMenu(null);
  });

  const reportSelection = useEffectEvent(() => {
    const selected = cyRef.current.$(":selected");
    onSelectionChange(selected.length);
    // Check if only one node is selected
    const isOneNode = selected.length === 1 && selected[0].isNode();
    // Node panel shows only if one node is selected
    setSelectedNode(isOneNode ? snapshotNode(selected[0]) : null);
    // Edge panel shows only if one edge is selected
    const isOneEdge = selected.length === 1 && selected[0].isEdge();
    setSelectedEdge(isOneEdge ? snapshotEdge(selected[0]) : null);
  });

  const handleTap = useEffectEvent((evt) => {
    const { cy, target } = evt;
    setNotice(null);

    if (mode === "add-node") {
      if (typeMenu) setTypeMenu(null);
      else if (target === cy) {
        const { x, y } = evt.renderedPosition;
        const { clientWidth, clientHeight } = containerRef.current;
        setTypeMenu({
          position: { ...evt.position },
          left: Math.max(0, Math.min(x, clientWidth - 140)),
          top: Math.max(0, Math.min(y, clientHeight - 190)),
        });
      }
      return;
    }

    if (mode !== "add-edge") return;

    if (target === cy) {
      setEdgeSourceId(null);
      return;
    }
    if (!target.isNode()) return;
    if (!edgeSourceId) {
      setEdgeSourceId(target.id());
      return;
    }
    if (target.id() !== edgeSourceId) {
      const source = cy.getElementById(edgeSourceId);
      if (source.edgesTo(target).nonempty()) {
        setNotice("Those nodes are already connected in that direction");
      } else {
        cy.add({
          group: "edges",
          data: {
            id: `e${++edgeCountRef.current}`,
            source: edgeSourceId,
            target: target.id(),
            ...EDGE_FIELDS,
          },
        });
      }
    }
    setEdgeSourceId(null);
  });

  // Escape key handling
  const handleKeyDown = useEffectEvent((e) => {
    if (e.key === "Escape") {
      setTypeMenu(null);
      setEdgeSourceId(null);
      setNotice(null);
      cyRef.current.elements().unselect();
    } else if (
      (e.key === "Delete" || e.key === "Backspace") &&
      !e.target.closest("input, textarea, select, [contenteditable], .property-panel")
    ) {
      deleteSelected();
    }
  });

  // Clicking outside the type menu closes it. Clicks on the canvas are left to handleTap.
  const handlePointerDown = useEffectEvent((e) => {
    if (
      typeMenu &&
      !typeMenuRef.current.contains(e.target) &&
      !containerRef.current.contains(e.target)
    ) {
      setTypeMenu(null);
    }
  });

  useEffect(() => {
    const cy = cytoscape({
      container: containerRef.current,
      style: STYLE,
      minZoom: 0.2,
      maxZoom: 4,
    });
    cyRef.current = cy;

    cy.on("tap", (evt) => handleTap(evt));
    cy.on("select unselect remove", () => reportSelection());

    const onKeyDown = (e) => handleKeyDown(e);
    const onPointerDown = (e) => handlePointerDown(e);
    window.addEventListener("keydown", onKeyDown);
    window.addEventListener("pointerdown", onPointerDown);

    return () => {
      window.removeEventListener("keydown", onKeyDown);
      window.removeEventListener("pointerdown", onPointerDown);
      cy.destroy();
    };
  }, []);

  // Selecting only works in Select mode.
  // Reset first: unselect() does nothing once autounselectify(true) is set.
  useEffect(() => {
    resetInteraction();
    cyRef.current.autounselectify(mode !== "select");
    cyRef.current.autoungrabify(mode === "add-edge");
  }, [mode]);

  useEffect(() => {
    const cy = cyRef.current;
    cy.nodes().removeClass("edge-source");
    if (edgeSourceId) cy.getElementById(edgeSourceId).addClass("edge-source");
  }, [edgeSourceId]);

  let hint = MODES.find((m) => m.id === mode).hint;
  if (mode === "add-edge" && edgeSourceId)
    hint = "Click the target node · Esc to cancel";
  if (notice) hint = notice;

  return (
    <div className="network-canvas">
      <div
        ref={containerRef}
        className="network-canvas__graph"
        data-mode={mode}
        role="application"
        aria-label="Network canvas"
        aria-keyshortcuts="Delete Backspace Escape"
        tabIndex="0"
      />
      <span className="network-canvas__hint" role="status">
        {hint}
      </span>
      {selectedNode && (
        <NodePropertyPanel
          key={selectedNode.id}
          node={selectedNode}
          onClose={closePanel}
          onSave={(values) => saveNode(selectedNode.id, values)}
        />
      )}
      {selectedEdge && (
        <EdgePropertyPanel
          key={selectedEdge.id}
          edge={selectedEdge}
          onClose={closePanel}
          onSave={(values) => saveEdge(selectedEdge.id, values)}
        />
      )}
      {typeMenu && (
        <div
          ref={typeMenuRef}
          className="network-canvas__type-menu"
          style={{ left: typeMenu.left, top: typeMenu.top }}
          role="menu"
          aria-label="Device type"
        >
          <div className="network-canvas__type-menu-title">Device type</div>
          {DEVICE_TYPES.map(({ type, Icon }, i) => (
            <button
              key={type}
              type="button"
              role="menuitem"
              autoFocus={i === 0}
              onClick={() => addNode(type)}
            >
              <Icon size={16} aria-hidden="true" />
              {type}
            </button>
          ))}
        </div>
      )}
    </div>
  );
}
