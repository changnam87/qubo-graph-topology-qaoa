"""
Input/output utilities for saved QUBO JSON files.

The RQ1 pipeline saves each generated QUBO instance as JSON.
This module loads those JSON files back into the internal QUBO dictionary format.

This is needed before QAOA circuit construction, because later scripts should
read saved QUBOs instead of regenerating them from scratch.
"""

from __future__ import annotations

from pathlib import Path
from typing import Dict, Any, Tuple
import json


def load_qubo_json(path: str | Path) -> Dict[str, Any]:
    """
    Load a QUBO JSON file and convert it back to the internal QUBO format.

    In JSON, quadratic keys are saved as strings like:

        "0,3": 12.0

    This function converts them back to tuple keys:

        (0, 3): 12.0
    """
    path = Path(path)

    with path.open("r", encoding="utf-8") as f:
        raw = json.load(f)

    linear = {
        int(i): float(value)
        for i, value in raw["linear"].items()
    }

    quadratic: Dict[Tuple[int, int], float] = {}

    for key, value in raw["quadratic"].items():
        i_str, j_str = key.split(",")
        i = int(i_str)
        j = int(j_str)

        if i == j:
            raise ValueError(f"Invalid self-loop quadratic key: {key}")

        a, b = sorted((i, j))
        quadratic[(a, b)] = float(value)

    qubo = {
        "name": raw["name"],
        "family": raw["family"],
        "n_variables": int(raw["n_variables"]),
        "linear": linear,
        "quadratic": quadratic,
        "constant": float(raw["constant"]),
        "metadata": raw.get("metadata", {}),
    }

    return qubo
