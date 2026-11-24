from qiskit import QuantumCircuit, __version__ as qiskit_version
from qiskit_aer import AerSimulator

qc = QuantumCircuit(2, 2)
qc.h(0)
qc.cx(0, 1)
qc.measure([0, 1], [0, 1])

counts = AerSimulator().run(qc, shots=1000).result().get_counts()
print(f"Qiskit {qiskit_version}")
print(qc.draw())
print(counts)

assert set(counts) <= {"00", "11"}, "Unexpected outcomes; entanglement failed"
print("Qiskit environment OK")
