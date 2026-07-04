# RQ1 Pilot Checkpoint

Project: qubo-graph-topology-qaoa

Paper target: IEEE TQE

Working title:
From Industrial QUBOs to Executable QAOA Circuits: QUBO-Graph-Aware and Topology-Aware Compilation

---

## 1. RQ1

RQ1:
To what extent do QUBO interaction-graph descriptors explain pre- and post-transpilation QAOA circuit complexity?

This checkpoint documents the first successful RQ1 pilot pipeline.

---

## 2. Completed Pipeline

The current pilot implements the following pipeline:

QUBO generation
-> QUBO JSON saving
-> QUBO interaction graph construction
-> graph descriptor extraction
-> p = 1 QAOA-style circuit construction
-> local topology coupling-map construction
-> topology-aware transpilation
-> RQ1 merged metric dataset
-> sanity summary, correlation screening, and first visualization

---

## 3. QUBO Families Included

The current pilot includes:

1. MaxCut-style QUBOs
2. Assignment-style QUBOs

Scheduling-derived toy QUBOs are not yet included.

---

## 4. Pilot Instance Sizes

The current pilot uses:

n_variables = 8, 12, 16

The pilot contains 27 QUBO instances.

Details:

MaxCut-style:
3 seeds x 3 sizes x 2 edge probabilities = 18 instances

Assignment-style:
3 seeds x 3 sizes = 9 instances

Total:
27 instances

---

## 5. Topologies Included

The current local topology set includes:

1. fully_connected
2. grid_2d
3. heavy_hex_like
4. line

No hardware API calls are used.

All topology experiments use local Qiskit CouplingMap objects.

---

## 6. QAOA Setting

The current pilot uses:

p = 1
gamma = 0.7
beta = 0.3

The QAOA-style circuit is constructed directly from the QUBO objective using:

x_i = (1 - Z_i) / 2

Each quadratic QUBO interaction is implemented as a ZZ-type interaction using:

CX - RZ - CX

Therefore, before transpilation:

pre_transpile_2q_count = 2 x number of QUBO quadratic terms

---

## 7. Python Modules Created

Current reusable modules:

src/qubo_generators.py
src/graph_utils.py
src/graph_metrics.py
src/qubo_io.py
src/qaoa_circuits.py
src/topologies.py
src/transpile_eval.py

Module roles:

qubo_generators.py:
Generates MaxCut-style and assignment-style QUBOs.

graph_utils.py:
Converts QUBOs into NetworkX interaction graphs.

graph_metrics.py:
Extracts graph descriptors from QUBO interaction graphs.

qubo_io.py:
Loads saved QUBO JSON files.

qaoa_circuits.py:
Builds p = 1 QAOA-style circuits and extracts pre-transpile metrics.

topologies.py:
Creates local coupling maps for line, grid_2d, heavy_hex_like, and fully_connected topologies.

transpile_eval.py:
Transpiles circuits to local coupling maps and extracts post-transpile metrics.

---

## 8. Experiment Scripts Created

Current experiment scripts:

experiments/rq1_pilot/run_graph_metrics.py
experiments/rq1_pilot/run_pre_transpile_metrics.py
experiments/rq1_pilot/run_transpile_metrics.py
experiments/rq1_pilot/merge_rq1_metrics.py
experiments/rq1_pilot/summarize_rq1_pilot.py
experiments/rq1_pilot/plot_rq1_first_sanity.py
experiments/rq1_pilot/core_correlation_check.py
experiments/rq1_pilot/make_rq1_interpretation_table.py

---

## 9. Main Output Files

Current result files:

data/instances/*.json
results/rq1_pilot/graph_metrics.csv
results/rq1_pilot/pre_transpile_circuit_metrics.csv
results/rq1_pilot/transpile_metrics.csv
results/rq1_pilot/merged_rq1_metrics.csv
results/rq1_pilot/rq1_summary_by_family_topology.csv
results/rq1_pilot/rq1_correlation_screening.csv
results/rq1_pilot/rq1_core_correlation_summary.csv
results/rq1_pilot/rq1_interpretation_table.csv
results/rq1_pilot/fig_n_edges_vs_transpiled_depth.png
docs/rq1_pilot_results_paragraph.md
docs/rq1_pilot_checkpoint.md

---

## 10. Main Validation Results

All completed validation checks passed:

PASS: QUBO generators work.
PASS: QUBO-to-graph conversion works.
PASS: graph descriptor extraction works.
PASS: graph_metrics.csv generated and validated.
PASS: QUBO JSON files saved and linked in graph_metrics.csv.
PASS: QUBO JSON loader works.
PASS: p=1 QAOA circuit construction works.
PASS: pre-transpile circuit metrics generated and validated.
PASS: local topology coupling maps work.
PASS: single-circuit topology-aware transpilation works.
PASS: full transpilation metrics generated and validated.
PASS: merged RQ1 metrics generated and validated.
PASS: RQ1 sanity summaries generated and validated.
PASS: first RQ1 sanity plot generated.
PASS: RQ1 core correlation summary generated and validated.
PASS: RQ1 interpretation table generated and validated.

---

## 11. Key Pilot Numerical Findings

From rq1_interpretation_table.csv:

Topology: fully_connected
mean_transpiled_depth = 35.111
mean_transpiled_2q_count = 47.778
mean_swap_count = 0.000
mean_depth_overhead = 1.458
mean_twoq_overhead = 1.000

Topology: grid_2d
mean_transpiled_depth = 50.704
mean_transpiled_2q_count = 60.222
mean_swap_count = 12.444
mean_depth_overhead = 1.785
mean_twoq_overhead = 1.151

Topology: heavy_hex_like
mean_transpiled_depth = 51.259
mean_transpiled_2q_count = 62.519
mean_swap_count = 14.741
mean_depth_overhead = 1.768
mean_twoq_overhead = 1.180

Topology: line
mean_transpiled_depth = 50.519
mean_transpiled_2q_count = 77.185
mean_swap_count = 29.407
mean_depth_overhead = 1.785
mean_twoq_overhead = 1.374

---

## 12. Core Correlation Findings

n_edges to pre_transpile_depth:
Spearman rho = 0.939 across the pilot set.

n_edges to transpiled_depth:

fully_connected: rho = 0.939
grid_2d: rho = 0.944
heavy_hex_like: rho = 0.941
line: rho = 0.932

n_edges to swap_count:

fully_connected: undefined because swap_count is always zero
grid_2d: rho = 0.957
heavy_hex_like: rho = 0.951
line: rho = 0.931

---

## 13. Current Interpretation

The pilot supports the feasibility of RQ1.

Main interpretation:

QUBO interaction-edge count is strongly associated with both pre-transpilation and post-transpilation QAOA circuit depth.

Topology does not remove this relationship, but changes the overhead profile.

Sparse topologies introduce routing overhead, especially in SWAP count and two-qubit gate overhead.

Bounded claim:

These pilot findings suggest that QUBO graph descriptors can serve as useful first-order explanatory variables for QAOA circuit complexity and topology-aware transpilation overhead.

No quantum advantage claim is made.
No QAOA superiority claim is made.
No hardware execution claim is made.

---

## 14. Saved Results Paragraph

The bounded Results paragraph draft is saved in:

docs/rq1_pilot_results_paragraph.md

---

## 15. Recommended Next Steps

Recommended next steps before moving to RQ2:

1. Add scheduling-derived toy QUBO family.
2. Expand instance sizes modestly, for example n = 8, 12, 16, 24, 32.
3. Add p = 2 as an optional sensitivity condition.
4. Add topology-alignment descriptors:
   - topology alignment ratio
   - weighted topology distance
5. Add more formal RQ1 regression models after expanding the dataset.

Recommended next step if moving toward RQ2:

Implement variable ordering and logical mapping strategies:
- natural
- random
- degree-based
- weighted-degree-based
- community/block-aware
- topology-aware placement heuristic

---

## 16. Current Status

RQ1 pilot minimum viable experiment is complete.

The next decision is whether to:

A. strengthen RQ1 with scheduling-derived toy QUBOs and larger sizes

or

B. begin RQ2 variable ordering and topology-aware mapping experiments
