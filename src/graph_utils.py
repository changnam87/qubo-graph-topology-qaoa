"""
Utilities for converting QUBOs into interaction graphs.

In this project, a QUBO interaction graph is defined as:

    node = binary variable
    edge = nonzero quadratic QUBO term
    edge weight = quadratic coefficient q_ij

This graph is the central structural object for RQ1.
"""

from __future__ import annotations

from typing import Dict, Any
import networkx as nx


def qubo_to_interaction_graph(qubo: Dict[str, Any]) -> nx.Graph:
    """
    Convert a QUBO dictionary into a NetworkX interaction graph.

    Parameters
    ----------
    qubo:
        Dictionary representation of a QUBO instance.
        Expected keys:
            - name
            - family
            - n_variables
            - quadratic

    Returns
    -------
    graph:
        NetworkX graph where nodes are QUBO variables and edges are
        nonzero quadratic interactions.
    """
    n_variables = int(qubo["n_variables"])

    graph = nx.Graph()

    # Add one node for each binary variable.
    graph.add_nodes_from(range(n_variables))

    # Add one edge for each nonzero quadratic QUBO term.
    for (i, j), coefficient in qubo["quadratic"].items():
        graph.add_edge(
            int(i),
            int(j),
            weight=float(coefficient),
            abs_weight=abs(float(coefficient)),
        )

    # Store useful metadata inside the graph object.
    graph.graph["name"] = qubo.get("name", "unknown")
    graph.graph["family"] = qubo.get("family", "unknown")
    graph.graph["n_variables"] = n_variables

    return graph
