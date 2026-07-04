"""
Transpilation evaluation utilities for RQ1 and RQ2.

This module transpiles a QAOA circuit to a local coupling-map topology
and extracts basic post-transpilation metrics.

No hardware API calls are used.

RQ2 addition:
    optional initial_layout support.

This allows variable ordering / logical mapping strategies to be imposed
rather than letting Qiskit choose the full initial layout automatically.
"""

from __future__ import annotations

from typing import Dict, Any, List
import time

from qiskit import QuantumCircuit, transpile
from qiskit.transpiler import CouplingMap


def _count_2q_gates(circuit: QuantumCircuit) -> int:
    """
    Count all two-qubit operations in a circuit.
    """
    count = 0

    for instruction in circuit.data:
        operation = instruction.operation
        if operation.num_qubits == 2:
            count += 1

    return count


def transpile_and_evaluate(
    circuit: QuantumCircuit,
    coupling_map: CouplingMap,
    topology_name: str,
    optimization_level: int = 1,
    seed_transpiler: int = 123,
    initial_layout: List[int] | None = None,
) -> Dict[str, Any]:
    """
    Transpile one circuit to one topology and return metrics.

    Parameters
    ----------
    circuit:
        Input Qiskit circuit.

    coupling_map:
        Local hardware topology.

    topology_name:
        Name of topology, used only for reporting.

    optimization_level:
        Qiskit transpiler optimization level.

    seed_transpiler:
        Fixed seed for reproducibility.

    initial_layout:
        Optional physical-qubit layout.

        If None:
            Qiskit is allowed to choose the initial layout.

        If list(range(n)):
            circuit qubit i is initially placed on physical qubit i.

        This is important for RQ2 because ordering strategies should be
        reflected in the imposed logical-to-physical placement.

    Notes
    -----
    We include 'swap' in basis_gates so that inserted SWAP operations
    can be counted directly in this pilot.
    """
    basis_gates = ["rz", "sx", "x", "cx", "swap"]

    start_time = time.perf_counter()

    transpiled = transpile(
        circuit,
        coupling_map=coupling_map,
        basis_gates=basis_gates,
        optimization_level=optimization_level,
        seed_transpiler=seed_transpiler,
        initial_layout=initial_layout,
    )

    elapsed = time.perf_counter() - start_time

    ops = dict(transpiled.count_ops())

    metrics = {
        "topology": topology_name,
        "optimization_level": optimization_level,
        "seed_transpiler": seed_transpiler,
        "initial_layout": None if initial_layout is None else list(initial_layout),

        "transpiled_n_qubits": transpiled.num_qubits,
        "transpiled_depth": transpiled.depth(),
        "transpiled_gate_count": sum(ops.values()),
        "transpiled_2q_count": _count_2q_gates(transpiled),
        "swap_count": int(ops.get("swap", 0)),
        "cx_count": int(ops.get("cx", 0)),
        "transpilation_time_sec": elapsed,
        "transpiled_ops": ops,
    }

    return {
        "transpiled_circuit": transpiled,
        "metrics": metrics,
    }
