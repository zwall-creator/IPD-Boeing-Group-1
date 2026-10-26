import React, { useState, useEffect, useRef } from 'react';
import './App.css';
import { useEventSource } from './hooks/useEventSource';
import NetworkCanvas from './components/NetworkCanvas';
import OptimizationControls from './components/OptimizationControls';
import GraphToolsPanel from './components/GraphToolsPanel';
import ConfirmDialog from './components/ConfirmDialog';

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
  const [optParams, setOptParams]   = useState({
    securityWeight:  50,
    costWeight:      50,
    bandwidthWeight: 50,
    riskThreshold:   30,
  });
  const [quantumStatus, setQuantumStatus] = useState(null);

  // Local UI logs (seed entries shown before the SSE connection is ready)
  const [localLogs, setLocalLogs] = useState([
    { text: '[System] Initialised simulation environment.', variant: 'info' },
    { text: '[Backend] Computation API mapped at :8000.', variant: 'info' },
  ]);

  const { events, status, backendOk, clearEvents, runSim, checkQuantumStatus } = useEventSource();

  // When user switches to quantum solver, fetch IBM status from backend
  useEffect(() => {
    if (solverType === 'quantum') {
      setQuantumStatus(null); // show loading state
      checkQuantumStatus().then(s => setQuantumStatus(s));
    } else {
      setQuantumStatus(null);
    }
  }, [solverType, checkQuantumStatus]);

  // Graph editor state, shared by the sidebar tools and the canvas
  const canvasRef = useRef(null);
  const [graphMode, setGraphMode] = useState('select');
  const [selectedCount, setSelectedCount] = useState(0);
  const [confirmRequest, setConfirmRequest] = useState(null); // Pending confirmation popup: null = close, {message, onConfirm} = show

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
      { text: `[Run] Triggering ${solverType} solver… (sec:${optParams.securityWeight} cost:${optParams.costWeight} bw:${optParams.bandwidthWeight} risk:${optParams.riskThreshold})`, variant: 'info' },
    ]);
    const ok = await runSim(solverType, optParams);
    if (!ok) {
      setLocalLogs(prev => [
        ...prev,
        { text: '[Error] Could not reach backend — is Flask running on :8000?', variant: 'error' },
      ]);
    }
  };

  // Clears system logs (originally handleReset)
  const clearLogs = () => {
    clearEvents();
    setLocalLogs([
      { text: '[System] Canvas reset.', variant: 'warn' },
    ]);
  };

  // Reset canvas
  const handleReset = () => {
    // Empty canvas skips popup
    if (canvasRef.current?.isEmpty() ?? true) {
      clearLogs();
      return;
    }
    setConfirmRequest({
      message: 'This will delete everything in the current network and clear the logs',
      onConfirm: () => {
        canvasRef.current?.clear();
        setGraphMode('select');
        clearLogs();
      },
    });
  };

  // confirm from popup
  const handleConfirm = () => {
    setConfirmRequest(null); // close popup, re-render
    confirmRequest.onConfirm(); // call the action that was requested
  };

  // cancel from popup
  const handleCancel = () => {
    setConfirmRequest(null); // close popup
  };

  const handleDeleteSelected = () => {
    canvasRef.current?.deleteSelected();
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

          {/* IBM Quantum status — shown only when quantum solver is selected */}
          {solverType === 'quantum' && (
            <div className="ibm-status">
              {quantumStatus === null ? (
                <span className="ibm-status__row connecting">Checking IBM Quantum…</span>
              ) : quantumStatus.connected ? (
                <>
                  <span className="ibm-status__row online">IBM Quantum: Connected</span>
                  <span className="ibm-status__detail">Backend: {quantumStatus.backend}</span>
                  <span className="ibm-status__detail">{quantumStatus.qubits} qubits available</span>
                </>
              ) : (
                <>
                  <span className="ibm-status__row offline">IBM Quantum: Unavailable</span>
                  <span className="ibm-status__detail">Using local Aer simulator</span>
                  {quantumStatus.error && (
                    <span className="ibm-status__error">{quantumStatus.error}</span>
                  )}
                </>
              )}
            </div>
          )}

          <div className="control-group">
            <label>Graph Tools</label>
            <GraphToolsPanel
              mode={graphMode}
              selectedCount={selectedCount}
              onModeChange={setGraphMode}
              onDeleteSelected={handleDeleteSelected}
              onReset={handleReset}
            />
          </div>

          {/* Live event counter */}
          <div className="control-group">
            <label>SSE Events Received</label>
            <span className="event-counter">{events.length}</span>
          </div>

          {/* Optimization priority sliders */}
          <OptimizationControls params={optParams} onChange={setOptParams} />
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
      {/* Confirmation popup */}
      <ConfirmDialog
        open={confirmRequest !== null}
        message={confirmRequest?.message}
        onConfirm={handleConfirm}
        onCancel={handleCancel}
      />
    </div>
  );
}
