"""
QAOA circuit construction utilities.

This module builds a simple p=1 QAOA-style circuit from a QUBO.

QUBO objective:

    minimize sum_i h_i x_i + sum_{i<j} q_ij x_i x_j + constant

with binary variables x_i in {0, 1}.

For circuit construction, we use:

    x_i = (1 - Z_i) / 2

The QUBO is therefore converted into Z and ZZ phase terms.
Global constants are ignored because they do not affect the circuit.
"""

from __future__ import annotations

from typing import Dict, Any
from qiskit import QuantumCircuit


def _count_2q_gates(circuit: QuantumCircuit) -> int:
    """
    Count two-qubit gates in a QuantumCircuit.
    """
    count = 0

    for instruction in circuit.data:
        operation = instruction.operation
        if operation.num_qubits == 2:
            count += 1

    return count


def build_qaoa_p1_circuit(
    qubo: Dict[str, Any],
    gamma: float = 0.7,
    beta: float = 0.3,
    include_barriers: bool = True,
) -> QuantumCircuit:
    """
    Build a p=1 QAOA-style circuit from a QUBO.

    Circuit structure:

        1. Initial Hadamards
        2. Cost phase layer
        3. Mixer layer

    Notes
    -----
    For each linear term h_i x_i:

        h_i x_i = h_i (1 - Z_i) / 2

    Ignoring the constant part, this contributes:

        -h_i/2 * Z_i

    For each quadratic term q_ij x_i x_j:

        q_ij x_i x_j
        = q_ij/4 * (1 - Z_i - Z_j + Z_i Z_j)

    Ignoring the constant part, this contributes:

        -q_ij/4 * Z_i
        -q_ij/4 * Z_j
        +q_ij/4 * Z_i Z_j

    We implement:
        Z rotations using RZ
        ZZ rotations using CX-RZ-CX decomposition
    """
    n = int(qubo["n_variables"])
    linear = qubo["linear"]
    quadratic = qubo["quadratic"]

    circuit = QuantumCircuit(n, name=f"qaoa_p1_{qubo['name']}")

    # 1. Initial equal superposition
    for i in range(n):
        circuit.h(i)

    if include_barriers:
        circuit.barrier()

    # 2-A. Accumulate effective Z coefficients
    z_coefficients = {i: 0.0 for i in range(n)}

    for i, h_i in linear.items():
        z_coefficients[int(i)] += -float(h_i) / 2.0

    for (i, j), q_ij in quadratic.items():
        q_ij = float(q_ij)
        z_coefficients[int(i)] += -q_ij / 4.0
        z_coefficients[int(j)] += -q_ij / 4.0

    # 2-B. Apply single-qubit Z phase terms
    for i in range(n):
        coeff = z_coefficients[i]

        if abs(coeff) > 1e-12:
            # exp(-i gamma coeff Z) corresponds to RZ(2 gamma coeff)
            circuit.rz(2.0 * gamma * coeff, i)

    # 2-C. Apply two-qubit ZZ phase terms
    for (i, j), q_ij in quadratic.items():
        zz_coeff = float(q_ij) / 4.0

        if abs(zz_coeff) > 1e-12:
            # exp(-i gamma zz_coeff Z_i Z_j)
            # implemented as CX - RZ(2 gamma zz_coeff) - CX
            circuit.cx(int(i), int(j))
            circuit.rz(2.0 * gamma * zz_coeff, int(j))
            circuit.cx(int(i), int(j))

    if include_barriers:
        circuit.barrier()

    # 3. Mixer layer: exp(-i beta X)
    # RX(theta) = exp(-i theta X / 2), so theta = 2 beta
    for i in range(n):
        circuit.rx(2.0 * beta, i)

    return circuit


def circuit_basic_metrics(circuit: QuantumCircuit) -> Dict[str, Any]:
    """
    Return basic pre-transpile circuit metrics.
    """
    return {
        "n_qubits": circuit.num_qubits,
        "depth": circuit.depth(),
        "gate_count": sum(circuit.count_ops().values()),
        "two_qubit_gate_count": _count_2q_gates(circuit),
        "ops": dict(circuit.count_ops()),
    }
