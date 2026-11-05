"""
quantum_backend.py
------------------
Handles all IBM Qiskit Runtime interactions.

Responsibilities:
  - Attempt to connect to IBM Quantum using credentials from environment variables.
  - Submit circuits via the SamplerV2 primitive on the least-busy real backend.
  - Fall back cleanly to the local AerSimulator when:
      * IBM_QUANTUM_TOKEN is absent or empty
      * Credentials are invalid (authentication error)
      * The IBM service is unreachable (network error)
      * The caller explicitly requests the simulator
  - Expose a status dict so the Flask app can surface connection state to the UI.

Environment variables (set in .env):
  IBM_QUANTUM_TOKEN    — API token from https://quantum.cloud.ibm.com/
  IBM_QUANTUM_CHANNEL  — "ibm_quantum" (default) or "ibm_cloud"
"""

import os
import logging
from dataclasses import dataclass, field
from typing import Optional

from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator

log = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Connection state — populated once on first use (lazy init)
# ---------------------------------------------------------------------------

@dataclass
class _IBMState:
    connected: bool = False
    backend_name: str = "aer_simulator"   # name of the active backend
    error: Optional[str] = None           # last connection error message
    channel: str = "ibm_quantum"
    least_busy_qubits: Optional[int] = None


_state = _IBMState()
_ibm_service = None   # QiskitRuntimeService instance, or None if unavailable


def _try_connect() -> None:
    """
    Attempt to authenticate with IBM Quantum and cache the service object.
    Sets _state fields regardless of outcome so callers can always read status.
    Safe to call multiple times — re-uses a cached connection.
    """
    global _ibm_service, _state

    if _ibm_service is not None:
        return  # already connected

    token = os.environ.get("IBM_QUANTUM_TOKEN", "").strip()
    channel = os.environ.get("IBM_QUANTUM_CHANNEL", "ibm_quantum").strip()
    _state.channel = channel

    if not token:
        _state.connected = False
        _state.error = "IBM_QUANTUM_TOKEN not set — using local Aer simulator"
        _state.backend_name = "aer_simulator"
        log.info(_state.error)
        return

    try:
        from qiskit_ibm_runtime import QiskitRuntimeService

        service = QiskitRuntimeService(channel=channel, token=token)
        # least_busy picks the operational backend with the fewest queued jobs
        backend = service.least_busy(operational=True, simulator=False)
        _ibm_service = service
        _state.connected = True
        _state.error = None
        _state.backend_name = backend.name
        _state.least_busy_qubits = backend.num_qubits
        log.info("IBM Quantum connected — backend: %s (%d qubits)",
                 backend.name, backend.num_qubits)
    except ImportError:
        _state.connected = False
        _state.error = "qiskit-ibm-runtime not installed — using local Aer simulator"
        log.warning(_state.error)
    except Exception as exc:
        _state.connected = False
        _state.error = f"IBM connection failed: {exc}"
        _state.backend_name = "aer_simulator (fallback)"
        log.warning(_state.error)


def get_status() -> dict:
    """
    Return the current IBM connection status as a plain dict.
    Triggers a connection attempt on the first call.
    """
    _try_connect()
    return {
        "connected": _state.connected,
        "backend":   _state.backend_name,
        "channel":   _state.channel,
        "error":     _state.error,
        "qubits":    _state.least_busy_qubits,
    }


# ---------------------------------------------------------------------------
# Circuit execution
# ---------------------------------------------------------------------------

def run_circuit(
    circuit: QuantumCircuit,
    shots: int = 1024,
    force_simulator: bool = False,
) -> dict:
    """
    Execute a Qiskit circuit and return the measurement counts.

    Parameters
    ----------
    circuit : QuantumCircuit
        The circuit to run. Must have measurements attached.
    shots : int
        Number of shots (repetitions).
    force_simulator : bool
        If True, skip IBM and always use the local AerSimulator.

    Returns
    -------
    dict with keys:
        counts      — dict[str, int] measurement outcomes
        backend     — str name of backend used
        shots       — int shots requested
        used_ibm    — bool whether real IBM hardware was used
        error       — str | None if something went wrong
    """
    _try_connect()

    # --- IBM path ---
    if _state.connected and not force_simulator and _ibm_service is not None:
        try:
            from qiskit_ibm_runtime import SamplerV2 as Sampler
            from qiskit.transpiler.preset_passmanagers import generate_preset_pass_manager

            backend = _ibm_service.least_busy(operational=True, simulator=False)
            pm = generate_preset_pass_manager(backend=backend, optimization_level=1)
            isa_circuit = pm.run(circuit)

            sampler = Sampler(backend)
            job = sampler.run([isa_circuit], shots=shots)
            result = job.result()

            # SamplerV2 returns BitArray; convert to plain counts dict
            pub_result = result[0]
            counts = pub_result.data.meas.get_counts()

            return {
                "counts":   counts,
                "backend":  backend.name,
                "shots":    shots,
                "used_ibm": True,
                "error":    None,
            }
        except Exception as exc:
            log.warning("IBM execution failed, falling back to Aer: %s", exc)
            _state.error = f"IBM run failed: {exc} — fell back to simulator"

    # --- Aer fallback ---
    try:
        simulator = AerSimulator()
        job = simulator.run(circuit, shots=shots)
        counts = job.result().get_counts()
        return {
            "counts":   counts,
            "backend":  "aer_simulator",
            "shots":    shots,
            "used_ibm": False,
            "error":    _state.error,   # surface any IBM error that caused the fallback
        }
    except Exception as exc:
        return {
            "counts":   {},
            "backend":  "none",
            "shots":    shots,
            "used_ibm": False,
            "error":    f"Aer fallback also failed: {exc}",
        }


def build_sample_circuit(n_qubits: int = 2) -> QuantumCircuit:
    """
    Build a simple Bell-state circuit for smoke-testing the backend.
    In a real integration this would be replaced by the QAOA/VQE circuit
    generated from the network topology.
    """
    qc = QuantumCircuit(n_qubits, n_qubits)
    qc.h(0)
    for i in range(1, n_qubits):
        qc.cx(0, i)
    qc.measure(range(n_qubits), range(n_qubits))
    return qc
