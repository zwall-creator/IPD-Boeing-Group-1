import React, { useState, useEffect, useRef } from 'react';
import './App.css';
import { useEventSource } from './hooks/useEventSource';
import NetworkCanvas from './components/NetworkCanvas';

// Map SSE event types to a log-entry CSS variant for colour coding
function eventToLogVariant(type) {
  if (type === 'connected')              return 'info';
  if (type === 'simulation.started')     return 'info';
  if (type === 'simulation.progress')    return 'default';
  if (type === 'simulation.done')        return 'success';
  if (type === 'error')                  return 'error';
  if (type === 'warn')                   return 'warn';
  return 'default';
}

function formatEvent(event) {
  const { type, data } = event;
  switch (type) {
    case 'connected':
      return '[SSE] Connection established.';
    case 'simulation.started':
      return `[Sim] Started — solver: ${data.solver}`;
    case 'simulation.progress':
      return `[Sim] Step ${data.step}/${data.total}: ${data.message}`;
    case 'simulation.done':
      return `[Sim] Complete — solver: ${data.solver} · status: ${data.status}`;
    default:
      return `[${type}] ${JSON.stringify(data)}`;
  }
}

export default function App() {
  const [activeView, setActiveView] = useState('topology');
  const [solverType, setSolverType] = useState('classical');

  // Local UI logs (seed entries shown before the SSE connection is ready)
  const [localLogs, setLocalLogs] = useState([
    { text: '[System] Initialised simulation environment.', variant: 'info' },
    { text: '[Backend] Computation API mapped at :8000.', variant: 'info' },
  ]);

  const { events, status, backendOk, clearEvents, emitEvent, runSim } = useEventSource();

  // Scroll the log console to the bottom whenever new entries arrive
  const logEndRef = useRef(null);
  useEffect(() => {
    logEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [events, localLogs]);

  // Derive combined log list: local seed entries + live SSE events
  const liveEntries = events.map(ev => ({
    text: formatEvent(ev),
    variant: eventToLogVariant(ev.type),
  }));
  const allLogs = [...localLogs, ...liveEntries];

  const utilityViews = {
    simulation: ['Simulation Runs', 'Configure a solver, run the current scenario, and monitor progress in the execution log below.'],
    reports: ['Reports', 'Completed simulation reports will appear here for review and export.'],
    solutions: ['Solutions', 'Saved solver solutions and recommended network changes will appear here.'],
  };

  // ------------------------------------------------------------------
  // Handlers
  // ------------------------------------------------------------------
  const handleRunSimulation = async () => {
    setLocalLogs(prev => [
      ...prev,
      { text: `[Run] Triggering ${solverType} solver…`, variant: 'info' },
    ]);
    const ok = await runSim(solverType);
    if (!ok) {
      setLocalLogs(prev => [
        ...prev,
        { text: '[Error] Could not reach backend — is Flask running on :8000?', variant: 'error' },
      ]);
    }
  };

  const handleAddNode = () =>
    emitEvent('graph.add_node', { label: `Node-${Date.now()}` });

  const handleAddEdge = () =>
    emitEvent('graph.add_edge', { from: 'A', to: 'B' });

  const handleReset = () => {
    clearEvents();
    setLocalLogs([
      { text: '[System] Canvas reset.', variant: 'warn' },
    ]);
  };

  // ------------------------------------------------------------------
  // Status badge
  // ------------------------------------------------------------------
  const statusLabel =
    status === 'connected'    ? 'Backend: Connected'    :
    status === 'connecting'   ? 'Backend: Connecting…'  :
    status === 'error'        ? 'Backend: Reconnecting…' :
                                'Backend: Disconnected';

  const statusVariant =
    status === 'connected' && backendOk ? 'online' :
    status === 'connecting'             ? 'connecting' :
                                          'offline';

  // ------------------------------------------------------------------
  // Render
  // ------------------------------------------------------------------
  return (
    <div className="app-container">
      {/* Top Application Bar */}
      <header className="app-header">
        <div className="header-brand">
          <h2>IPD Simulation &amp; Computation Engine</h2>
          <span className="badge-env">Local Dev</span>
        </div>
        <div className="header-actions">
          <span className={`status-indicator ${statusVariant}`}>{statusLabel}</span>
          <button
            type="button"
            className="btn-primary"
            onClick={handleRunSimulation}
          >
            Run Simulation
          </button>
        </div>
      </header>

      {/* Main Workspace Body */}
      <div className="workspace-body">
        {/* Left Toolbar / Configuration Panel */}
        <aside className="workspace-sidebar">
          <h3>Workspace</h3>
          <nav className="workspace-nav" aria-label="Workspace views">
            <button className={activeView === 'topology' ? 'active' : ''} onClick={() => setActiveView('topology')} type="button">Network Topology</button>
            <button className={activeView === 'simulation' ? 'active' : ''} onClick={() => setActiveView('simulation')} type="button">Simulation Runs</button>
            <button className={activeView === 'reports' ? 'active' : ''} onClick={() => setActiveView('reports')} type="button">Reports</button>
            <button className={activeView === 'solutions' ? 'active' : ''} onClick={() => setActiveView('solutions')} type="button">Solutions</button>
          </nav>

          <h3>Controls &amp; Solvers</h3>

          <div className="control-group">
            <label htmlFor="solver-select">Solver Mode</label>
            <select
              id="solver-select"
              value={solverType}
              onChange={(e) => setSolverType(e.target.value)}
            >
              <option value="classical">Classical RCPSP (CP-SAT)</option>
              <option value="quantum">Quantum Qiskit (QAOA/VQE)</option>
            </select>
          </div>

          <div className="control-group">
            <label>Graph Tools</label>
            <button type="button" className="btn-secondary" onClick={handleAddNode}>
              + Add Node
            </button>
            <button type="button" className="btn-secondary" onClick={handleAddEdge}>
              + Add Edge
            </button>
            <button type="button" className="btn-secondary" onClick={handleReset}>
              Reset Canvas
            </button>
          </div>

          {/* Live event counter */}
          <div className="control-group">
            <label>SSE Events Received</label>
            <span className="event-counter">{events.length}</span>
          </div>
        </aside>

        {/* Central Display / Visual Canvas Container */}
        <main className="workspace-canvas">
          <div className="canvas-header">
            <span className="canvas-title">{activeView === 'topology' ? 'Network Topology' : utilityViews[activeView][0]}</span>
            <span className="canvas-meta">IPD Workspace</span>
          </div>

          <div className="canvas-viewport">
            {activeView === 'topology' ? <NetworkCanvas /> : (
              <div className="utility-view">
                <p>{utilityViews[activeView][0]}</p>
                <small>{utilityViews[activeView][1]}</small>
                {activeView === 'simulation' && <button type="button" className="btn-primary utility-action" onClick={handleRunSimulation}>Run current scenario</button>}
              </div>
            )}
          </div>
        </main>
      </div>

      {/* Bottom Logs Panel */}
      <footer className="app-footer">
        <div className="footer-title">
          Output &amp; Execution Logs
          <span className={`sse-badge ${statusVariant}`}>{statusLabel}</span>
        </div>
        <div className="log-console">
          {allLogs.map((entry, idx) => (
            <div key={idx} className={`log-entry ${entry.variant}`}>
              {entry.text}
            </div>
          ))}
          <div ref={logEndRef} />
        </div>
      </footer>
    </div>
  );
}
