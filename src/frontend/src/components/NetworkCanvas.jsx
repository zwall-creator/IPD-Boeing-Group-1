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
import "./NetworkCanvas.css";

// Color Codings
const VT_MAROON = "#861F41";
const VT_ORANGE = "#E5751F";
const HOKIE_STONE = "#75787B";
const TEXT = "#1f2933";

// Backend fields from src/simulation/NW_Structure.py, all null for now.
// TODO: IP format (string vs list of ints)
// TODO: default values for base_sec_level, risk_level, cost and bandwidth
// TODO: allowed values for connection_type
// TODO: NW_Structure.py doesn't list device types (they come from deviceIcons.jsx)
// TODO: security devices (NW_Sec_Device) not supported yet
// TODO: build derived fields (security_level, connections, destination IP) for the backend
const NODE_FIELDS = { device_ip: null, base_sec_level: null, risk_level: null };
const EDGE_FIELDS = { cost: null, bandwidth: null, connection_type: null };

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

  function addNode(type) {
    const count = (typeCountsRef.current[type] ?? 0) + 1;
    typeCountsRef.current[type] = count;
    cyRef.current.add({
      group: "nodes",
      data: {
        id: `n${++nodeCountRef.current}`,
        label: `${type} ${count}`,
        device_type: type,
        ...NODE_FIELDS,
      },
      position: typeMenu.position,
    });
    setTypeMenu(null);
  }

  // Delete selected elements
  function deleteSelected() {
    cyRef.current.$(":selected").remove();
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

  // App's sidebar buttons call deleteSelected(), isEmpty(), or clear()
  useImperativeHandle(ref, () => ({ deleteSelected, isEmpty, clear }));

  const resetInteraction = useEffectEvent(() => {
    cyRef.current.elements().unselect();
    setEdgeSourceId(null);
    setNotice(null);
    setTypeMenu(null);
  });

  const reportSelection = useEffectEvent(() => {
    onSelectionChange(cyRef.current.$(":selected").length);
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
      />
      <span className="network-canvas__hint" role="status">
        {hint}
      </span>
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
