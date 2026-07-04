# RQ2 Pilot Diagnostic Note

## RQ2

Can QUBO-graph-aware variable ordering and topology-aware logical mapping reduce transpilation overhead relative to natural, random, and standard Qiskit baselines?

---

## Current RQ2 Pilot Status

RQ2 has been tested in three stages:

1. Variable ordering strategies were implemented:
   - natural
   - random
   - degree_desc
   - weighted_degree_desc

2. QUBO relabeling was implemented and validated:
   - relabeling preserves QUBO objective energy
   - ordering can be reflected in QAOA circuit qubit indices

3. Fixed initial layout was added:
   - initial_layout = list(range(n))
   - this makes relabeled QUBO ordering affect logical-to-physical placement

---

## Key Finding 1: Ordering Must Be Coupled to Layout

Without an explicit initial_layout, Qiskit can absorb ordering differences through its own layout selection. In that case, different relabelings may produce identical transpilation metrics.

After adding fixed initial layout, ordering differences became visible.

Single-instance scheduling_toy, n = 16, line topology:

natural:
depth = 48, 2q = 81, swap = 41

random:
depth = 46, 2q = 101, swap = 61

degree_desc:
depth = 37, 2q = 58, swap = 18

weighted_degree_desc:
depth = 37, 2q = 58, swap = 18

This showed that graph-aware ordering can reduce overhead in selected cases, but random ordering can increase SWAP overhead.

---

## Key Finding 2: Ordering Alone Is Not Robust

A broader RQ2 pilot used:

- 24 QUBO instances
- 3 families: maxcut, assignment, scheduling_toy
- 2 sizes: 16 and 24 variables
- 3 topologies: line, grid_2d, heavy_hex_like
- 4 ordering strategies: natural, random, degree_desc, weighted_degree_desc

Total:
288 observations

Mean delta vs natural:

degree_desc:
mean_delta_depth = +10.444
mean_delta_2q = +20.625
mean_delta_swap = +20.625

weighted_degree_desc:
mean_delta_depth = +8.556
mean_delta_2q = +22.667
mean_delta_swap = +22.667

random:
mean_delta_depth = +16.903
mean_delta_2q = +35.472
mean_delta_swap = +35.472

Interpretation:
simple graph-aware ordering alone is not robust and can worsen transpilation overhead, especially for MaxCut-style QUBOs.

---

## Key Finding 3: Effects Differ by QUBO Family

Family-level pilot summary:

assignment:
degree_desc and weighted_degree_desc were identical to natural on average.

maxcut:
degree_desc and weighted_degree_desc worsened depth, two-qubit count, and SWAP count.

scheduling_toy:
degree_desc and weighted_degree_desc slightly improved average depth, two-qubit count, and SWAP count.

Interpretation:
QUBO family structure affects whether graph-aware ordering is beneficial.

---

## Key Finding 4: Naive Topology-Aware Placement Can Be Harmful

Two topology-aware placement heuristics were tested:

1. topology_aware_centrality:
   high-degree QUBO variables are placed on central physical qubits.

2. bfs_topology_aware:
   QUBO graph BFS ordering is matched to topology graph BFS ordering.

Single-instance scheduling_toy, n = 16, line topology:

standard_qiskit:
depth = 29, 2q = 52, swap = 12

fixed_identity_after_relabeling:
depth = 37, 2q = 58, swap = 18

topology_aware_centrality:
depth = 64, 2q = 102, swap = 62

bfs_topology_aware:
depth = 64, 2q = 93, swap = 53

Interpretation:
naive topology-aware placement can be worse than both fixed identity and standard Qiskit.

---

## Current RQ2 Interpretation

The current pilot does not support a simple claim that degree-based or weighted-degree-based QUBO ordering universally improves transpilation.

Instead, the current evidence supports a more nuanced and stronger claim:

QUBO-graph-aware mapping must be evaluated jointly with hardware topology and strong transpiler baselines. Naive graph-aware ordering or naive topology-aware placement can increase routing overhead.

This is an important RQ2 result because it prevents overclaiming and motivates a readiness-profile view rather than a universal mapping rule.

---

## Recommended RQ2 Path Forward

For the final RQ2 experiment, keep the following baselines:

1. standard_qiskit
   - initial_layout = None
   - Qiskit chooses layout and routing

2. natural_fixed
   - no relabeling
   - initial_layout = list(range(n))

3. random_fixed
   - random relabeling
   - fixed initial layout

4. degree_desc_fixed
   - degree-based relabeling
   - fixed initial layout

5. weighted_degree_desc_fixed
   - weighted-degree relabeling
   - fixed initial layout

6. centrality_layout
   - graph-aware relabeling
   - central physical placement

7. bfs_topology_aware
   - BFS graph ordering
   - BFS topology placement

Expected final RQ2 conclusion may be:

- standard_qiskit is a strong baseline
- naive graph-aware strategies are not uniformly beneficial
- benefits are family- and topology-dependent
- graph-aware strategies can help selected scheduling-derived QUBOs
- random ordering is unstable and often harmful
- topology-aware mapping requires careful algorithm design beyond simple centrality/BFS heuristics

No claim should be made that graph-aware ordering universally reduces overhead.
