import { useEffect, useRef } from "react";
import cytoscape from "cytoscape";
import { STYLE } from "../graph/canvasStyle";
import { topologyToElements } from "../graph/networkSerializer";
import "./SimulationFrame.css";

// Editor style and frame-only rules
const FRAME_STYLE = [
  ...STYLE,
  {
    selector: "node",
    style: {
      label: (node) => `${node.data("label")}\n${node.data("device_ip")}`,
      "text-wrap": "wrap",
    },
  },
  { selector: "core", style: { "active-bg-opacity": 0 } },
  { selector: ":active", style: { "overlay-opacity": 0 } },
];

function fitToFrame(cy) {
  cy.layout({ name: "preset", fit: true, padding: 5 }).run();
  if (cy.zoom() > 1) {
    cy.zoom(1);
    cy.center();
  }
}

// Read-only view of one simulation run's network
export default function SimulationFrame({ run }) {
  const containerRef = useRef(null);
  const cyRef = useRef(null);

  // Create the graph once when the frame appears, destroy it when the frame goes away
  useEffect(() => {
    const cy = cytoscape({
      container: containerRef.current,
      style: FRAME_STYLE,
      minZoom: 0.2,
      maxZoom: 4,
      autoungrabify: true,        // nodes can't be dragged
      autounselectify: true,      // nothing can be selected
      boxSelectionEnabled: false, // no box selection
    });
    cy.on("resize", () => fitToFrame(cy));
    cyRef.current = cy;
    return () => cy.destroy();
  }, []);

  const snapshot = run?.snapshot;

  // Draw the run's network whenever a new snapshot arrives
  useEffect(() => {
    const cy = cyRef.current;
    cy.elements().remove();
    cy.add(topologyToElements(snapshot));
    fitToFrame(cy);
  }, [snapshot]);

  // Start time
  const startTime = run ? new Date(run.startedAt).toLocaleTimeString() : "";

  return (
    <section className="simulation-frame" aria-label="Last simulation run">
      {run && (
        <div
          className={`simulation-frame__status simulation-frame__status--${run.status}`}
          role="status"
        >
          <span className="simulation-frame__solver">{run.solver ?? "Network check"}</span>
          {` · ${startTime} · ${run.status}`}
          {run.status === "failed" && ` — ${run.message}`}
        </div>
      )}
      <div className="simulation-frame__canvas">
        <div ref={containerRef} className="simulation-frame__graph" />
        {!run && (
          <div className="simulation-frame__empty">
            No run yet. Click Check network or Run to see the network here.
          </div>
        )}
      </div>
    </section>
  );
}
