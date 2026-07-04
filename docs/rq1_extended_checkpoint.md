# RQ1 Extended Checkpoint

Project: qubo-graph-topology-qaoa

Paper target: IEEE TQE

Working title:
From Industrial QUBOs to Executable QAOA Circuits: QUBO-Graph-Aware and Topology-Aware Compilation

---

## 1. RQ1

RQ1:
To what extent do QUBO interaction-graph descriptors explain pre- and post-transpilation QAOA circuit complexity?

This checkpoint documents the completed extended RQ1 analysis.

---

## 2. Final RQ1 Dataset

The extended RQ1 dataset includes:

- 60 QUBO instances
- 3 QUBO families
- 5 variable sizes
- 4 local coupling-map topologies
- 240 topology-specific transpilation observations

QUBO families:

1. MaxCut-style QUBOs
2. Assignment-style QUBOs
3. Scheduling-derived toy QUBOs

Variable sizes:

8, 12, 16, 24, 32 binary variables

Topologies:

1. fully_connected
2. grid_2d
3. heavy_hex_like
4. line

No hardware API calls were used.

---

## 3. QAOA and Transpilation Setting

QAOA-style circuit depth:

p = 1

Fixed parameters:

gamma = 0.7
beta = 0.3

Each QUBO was converted to a p = 1 QAOA-style circuit using the binary-to-spin relation:

x_i = (1 - Z_i) / 2

Each quadratic QUBO interaction was implemented using a ZZ-type phase interaction decomposed as:

CX - RZ - CX

Therefore, before transpilation:

pre_transpile_2q_count = 2 x number of QUBO quadratic terms

Transpilation used local Qiskit CouplingMap objects only.

---

## 4. Final RQ1 Python Modules

Reusable modules:

src/qubo_generators.py
src/graph_utils.py
src/graph_metrics.py
src/qubo_io.py
src/qaoa_circuits.py
src/topologies.py
src/topology_alignment.py
src/transpile_eval.py

Key additions beyond the pilot:

- generate_scheduling_toy_qubo in src/qubo_generators.py
- topology-alignment descriptors in src/topology_alignment.py

---

## 5. Final RQ1 Experiment Scripts

Extended RQ1 scripts:

experiments/rq1_pilot/run_rq1_extended_graph_metrics.py
experiments/rq1_pilot/run_rq1_extended_pre_transpile_metrics.py
experiments/rq1_pilot/run_rq1_extended_transpile_metrics.py
experiments/rq1_pilot/merge_rq1_extended_metrics.py
experiments/rq1_pilot/add_rq1_topology_alignment_metrics.py
experiments/rq1_pilot/rq1_alignment_correlation_check.py
experiments/rq1_pilot/make_rq1_final_summary_tables.py
experiments/rq1_pilot/run_rq1_regression_models.py
experiments/rq1_pilot/plot_rq1_final_figures.py

Pilot scripts are retained for traceability but the extended results should be treated as the main RQ1 dataset.

---

## 6. Final RQ1 Output Files

Main extended data files:

data/instances_rq1_extended/*.json
results/rq1_extended/graph_metrics.csv
results/rq1_extended/pre_transpile_circuit_metrics.csv
results/rq1_extended/transpile_metrics.csv
results/rq1_extended/merged_rq1_metrics.csv
results/rq1_extended/merged_rq1_metrics_with_alignment.csv

Summary and analysis files:

results/rq1_extended/rq1_alignment_correlation_summary.csv
results/rq1_extended/table_rq1_family_topology_summary.csv
results/rq1_extended/table_rq1_key_correlations.csv
results/rq1_extended/rq1_regression_model_summary.csv
results/rq1_extended/rq1_regression_coefficients.csv
results/rq1_extended/rq1_regression_model_notes.md

Figures:

results/rq1_extended/fig_rq1a_edges_vs_transpiled_depth.png
results/rq1_extended/fig_rq1b_topology_distance_vs_swap_count.png

Writing files:

docs/rq1_extended_results_paragraph.md
docs/rq1_extended_checkpoint.md

---

## 7. Graph Descriptors Used

Topology-independent QUBO graph descriptors include:

- n_variables
- n_edges
- density
- avg_degree
- max_degree
- degree_std
- weighted_degree_mean
- weighted_degree_max
- weighted_degree_std
- quadratic coefficient range
- coefficient_entropy
- coefficient_concentration
- connected_components
- community_count
- modularity

---

## 8. Topology-Alignment Descriptors Used

Topology-aware descriptors include:

- topology_alignment_ratio
- weighted_topology_alignment_ratio
- mean_topology_distance
- weighted_mean_topology_distance
- max_topology_distance
- n_aligned_edges
- n_unaligned_edges

For RQ1, these descriptors use natural mapping:

logical variable i -> physical qubit i

Alternative mappings are reserved for RQ2.

---

## 9. Main Regression Models

Six compact explanatory models were fitted:

M1_pre_depth_graph:
Graph descriptors explaining log pre-transpile depth.

M2_transpiled_depth_graph_topologyFE:
Graph descriptors plus topology fixed effects explaining log transpiled depth.

M3_transpiled_depth_graph_alignment:
Graph descriptors plus topology-alignment descriptors explaining log transpiled depth.

M4_transpiled_2q_graph_alignment:
Graph and alignment descriptors explaining log transpiled two-qubit count.

M5_swap_all_topologies:
Graph and alignment descriptors explaining log SWAP count across all topologies.

M6_swap_sparse_topologies_only:
Graph and alignment descriptors explaining log SWAP count only for sparse topologies, excluding fully_connected.

All models used log1p-transformed outcomes, z-scored continuous predictors, family fixed effects, and HC3 robust standard errors. Post-transpilation models included topology fixed effects.

---

## 10. Regression Model Summary

Adjusted R-squared results:

M1_pre_depth_graph:
Adj. R2 = 0.9789

M2_transpiled_depth_graph_topologyFE:
Adj. R2 = 0.9484

M3_transpiled_depth_graph_alignment:
Adj. R2 = 0.9662

M4_transpiled_2q_graph_alignment:
Adj. R2 = 0.9244

M5_swap_all_topologies:
Adj. R2 = 0.9508

M6_swap_sparse_topologies_only:
Adj. R2 = 0.9642

Key interpretation:

Graph descriptors strongly explain pre-transpilation circuit complexity.

Topology-alignment descriptors add explanatory value for post-transpilation depth.

Topology-alignment descriptors strongly explain SWAP overhead.

---

## 11. Key Coefficient Patterns

For log transpiled depth in M3:

topology_alignment_ratio:
negative association with transpiled depth

weighted_mean_topology_distance:
positive association with transpiled depth

For log SWAP count in M5 and M6:

topology_alignment_ratio:
negative association with SWAP count

weighted_mean_topology_distance:
positive association with SWAP count

Interpretation:

Better QUBO-topology alignment reduces routing overhead.

Longer topology distance increases routing overhead.

---

## 12. Important Interpretation Note

Simple correlations showed that n_edges had strong positive marginal associations with circuit depth.

However, in multivariable regression, n_edges coefficients became negative in some models because graph descriptors are correlated with each other.

Therefore, the correct interpretation is not:

n_edges alone universally determines circuit complexity.

The correct interpretation is:

a compact profile of QUBO graph descriptors and topology-alignment descriptors jointly explains QAOA circuit complexity and topology-aware transpilation overhead.

In the conditional models, max_degree and coefficient-distribution descriptors captured substantial variation once edge count, density, family, topology, and alignment descriptors were included.

---

## 13. RQ1 Main Conclusion

RQ1 is supported at the compilation-analysis level.

Main conclusion:

QUBO interaction-graph descriptors provide a strong first-order explanation of p = 1 QAOA circuit complexity before transpilation.

Topology-alignment descriptors explain additional topology-aware transpilation overhead after coupling-map constraints are imposed.

Bounded claim:

These results provide explanatory compilation evidence that QUBO graph structure and QUBO-topology alignment are useful predictors of executable QAOA circuit metrics.

No quantum advantage claim is made.

No QAOA optimization superiority claim is made.

No hardware execution claim is made.

---

## 14. RQ1 Figures

Figure RQ1-A:
results/rq1_extended/fig_rq1a_edges_vs_transpiled_depth.png

Message:
QUBO interaction graph size is associated with transpiled circuit depth.

Figure RQ1-B:
results/rq1_extended/fig_rq1b_topology_distance_vs_swap_count.png

Message:
QUBO-topology distance is associated with SWAP insertion and routing overhead.

---

## 15. RQ1 Results Paragraph

Final RQ1 extended Results paragraph is saved in:

docs/rq1_extended_results_paragraph.md

This paragraph should be used as the basis for the manuscript Results subsection for RQ1.

---

## 16. Current Status

RQ1 is complete enough to move to RQ2.

Recommended next step:

Begin RQ2 variable ordering and topology-aware logical mapping experiments.

RQ2 should reuse the same extended QUBO dataset and compare:

1. natural ordering
2. random ordering
3. degree-based ordering
4. weighted-degree-based ordering
5. community-aware ordering if feasible
6. topology-aware initial layout / mapping heuristic

The primary RQ2 outcomes should be:

- transpiled_depth
- transpiled_gate_count
- transpiled_2q_count
- swap_count
- depth_overhead
- twoq_overhead
- transpilation_time_sec

RQ2 should compare these strategies against Qiskit baseline transpilation behavior.
