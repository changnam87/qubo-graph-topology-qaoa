# Full Experiment Checkpoint

Project: qubo-graph-topology-qaoa

Paper target: IEEE TQE

Working title:
From Industrial QUBOs to Executable QAOA Circuits: QUBO-Graph-Aware and Topology-Aware Compilation

---

## 1. Paper Scope

This project evaluates how industrial-style QUBO structure affects the construction and transpilation of executable QAOA-style circuits.

The paper does not claim:

- quantum advantage
- QAOA optimization superiority
- hardware execution performance

The contribution is a compilation-analysis framework linking:

1. QUBO interaction graph structure
2. QAOA circuit complexity
3. topology-aware transpilation overhead
4. mapping-strategy behavior
5. sub-QUBO extraction trade-offs

The final framing is a readiness-profile framing, not a universal readiness score or universal mapping/extraction rule.

---

## 2. Research Questions

RQ1:
To what extent do QUBO interaction-graph descriptors explain pre- and post-transpilation QAOA circuit complexity?

RQ2:
Can QUBO-graph-aware variable ordering and topology-aware logical mapping reduce transpilation overhead relative to natural, random, and standard Qiskit baselines?

RQ3:
How do sub-QUBO extraction strategies trade off interaction preservation, feasibility preservation, classical solution-quality preservation, and QAOA circuit executability?

---

## 3. RQ1 Status

RQ1 is complete.

Dataset:

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

8, 12, 16, 24, 32

Topologies:

1. fully_connected
2. grid_2d
3. heavy_hex_like
4. line

Main RQ1 files:

results/rq1_extended/merged_rq1_metrics_with_alignment.csv
results/rq1_extended/table_rq1_family_topology_summary.csv
results/rq1_extended/table_rq1_key_correlations.csv
results/rq1_extended/rq1_regression_model_summary.csv
results/rq1_extended/rq1_regression_coefficients.csv
results/rq1_extended/fig_rq1a_edges_vs_transpiled_depth.png
results/rq1_extended/fig_rq1b_topology_distance_vs_swap_count.png
docs/rq1_extended_results_paragraph.md
docs/rq1_extended_checkpoint.md

Main RQ1 conclusion:

QUBO graph descriptors strongly explain pre-transpilation QAOA circuit complexity.

Topology-alignment descriptors add explanatory value for post-transpilation depth and SWAP overhead.

RQ1 supports a compilation-level claim that QUBO graph structure and QUBO-topology alignment are useful explanatory variables for executable QAOA circuit metrics.

---

## 4. RQ1 Key Numerical Results

Adjusted R-squared values:

M1_pre_depth_graph:
0.9789

M2_transpiled_depth_graph_topologyFE:
0.9484

M3_transpiled_depth_graph_alignment:
0.9662

M4_transpiled_2q_graph_alignment:
0.9244

M5_swap_all_topologies:
0.9508

M6_swap_sparse_topologies_only:
0.9642

Key interpretation:

Adding topology-alignment descriptors improved transpiled-depth explanation from adjusted R2 = 0.9484 to adjusted R2 = 0.9662.

For SWAP count, topology-alignment ratio was negatively associated with SWAP count, while weighted mean topology distance was positively associated with SWAP count.

---

## 5. RQ2 Status

RQ2 is complete.

Dataset:

- 60 QUBO instances
- 3 sparse topologies
- 8 mapping strategies
- 1,440 strategy-topology-instance observations

Sparse topologies:

1. line
2. grid_2d
3. heavy_hex_like

RQ2 strategies:

1. standard_qiskit
2. natural_fixed
3. random_fixed
4. degree_desc_fixed
5. weighted_degree_desc_fixed
6. degree_desc_centrality_layout
7. weighted_degree_desc_centrality_layout
8. bfs_topology_aware

Main RQ2 files:

results/rq2_full/rq2_mapping_metrics.csv
results/rq2_full/table_rq2_strategy_summary.csv
results/rq2_full/table_rq2_family_strategy_summary.csv
results/rq2_full/table_rq2_topology_strategy_summary.csv
results/rq2_full/table_rq2_win_rates.csv
docs/rq2_pilot_diagnostic_note.md
docs/rq2_results_paragraph.md
docs/rq2_checkpoint.md

Main RQ2 conclusion:

RQ2 does not support a universal claim that simple QUBO-graph-aware ordering or naive topology-aware placement reduces transpilation overhead.

Instead, mapping strategy performance is baseline-dependent, family-dependent, and topology-dependent.

Standard Qiskit layout/routing is a strong baseline.

Naive graph-aware or topology-aware heuristics can increase routing overhead.

---

## 6. RQ2 Key Numerical Results

Relative to natural_fixed, standard_qiskit reduced:

- mean transpiled depth by 7.361
- mean two-qubit count by 12.261
- mean SWAP count by 12.261

Approximate percentage reductions:

- depth: 8.4%
- two-qubit count: 8.6%
- SWAP count: 33.3%

Win rates of standard_qiskit vs natural_fixed:

- two-qubit count: about 71.1%
- SWAP count: about 71.1%

Custom strategies were not uniformly beneficial.

Random fixed ordering was unstable and harmful on average.

Centrality-based and BFS-based naive topology-aware strategies increased overhead on average.

---

## 7. RQ3 Status

RQ3 full analysis is complete.

Dataset:

- all extended QUBO instances with 24 and 32 variables
- 24 original QUBOs
- 4 extraction strategies
- 3 subproblem sizes
- 288 extracted sub-QUBOs
- 864 sub-QUBO topology-specific transpilation observations

Original QUBO families:

1. MaxCut-style QUBOs
2. Assignment-style QUBOs
3. Scheduling-derived toy QUBOs

Original sizes:

24 and 32 variables

Original QUBO count:

- MaxCut: 12
- Assignment: 6
- Scheduling_toy: 6
- Total: 24

Subproblem sizes:

- k = 8
- k = 12
- k = 16

Extraction strategies:

1. top_weight_edges
2. high_degree_nodes
3. weighted_degree_nodes
4. random_nodes

Sparse topologies for executability evaluation:

1. line
2. grid_2d
3. heavy_hex_like

Main RQ3 files:

data/subqubos_rq3_full/*.json
results/rq3_full/subqubo_extraction_metrics.csv
results/rq3_full/subqubo_executability_metrics.csv
results/rq3_full/subqubo_vs_original_executability.csv
results/rq3_full/subqubo_solution_quality_metrics.csv
results/rq3_full/rq3_final_tradeoff_table.csv
docs/rq3_results_paragraph.md
docs/rq3_checkpoint.md

Pilot RQ3 files are retained for traceability, but the full RQ3 files should be used for manuscript writing.

Main RQ3 conclusion:

Sub-QUBO extraction creates a multi-objective trade-off among interaction preservation, QAOA circuit executability, and lifted solution-quality preservation.

Smaller sub-QUBOs improve circuit executability but sacrifice interaction preservation.

Larger sub-QUBOs preserve more interaction structure but reduce executability gains.

Solution-quality preservation is family-dependent and does not follow interaction preservation monotonically.

---

## 8. RQ3 Key Numerical Results

Overall mean weighted-edge preservation:

weighted_degree_nodes:
0.3670

high_degree_nodes:
0.3603

top_weight_edges:
0.3320

random_nodes:
0.2144

Overall mean reductions relative to original QUBO circuits:

top_weight_edges:
depth reduction about 46.30%
two-qubit reduction about 73.44%
SWAP reduction about 89.34%

random_nodes:
depth reduction about 44.95%
two-qubit reduction about 81.65%
SWAP reduction about 89.59%

weighted_degree_nodes:
depth reduction about 39.66%
two-qubit reduction about 69.00%
SWAP reduction about 82.99%

high_degree_nodes:
depth reduction about 39.29%
two-qubit reduction about 68.71%
SWAP reduction about 82.68%

k-dependent pattern:

For k = 8:
weighted-edge preservation was approximately 0.1280 to 0.2126, while two-qubit reductions were approximately 83.26% to 89.89% and SWAP reductions were approximately 95.22% to 98.08%.

For k = 12:
weighted-edge preservation increased to approximately 0.1649 to 0.3618, while two-qubit reductions were approximately 69.77% to 86.53% and SWAP reductions were approximately 85.08% to 92.73%.

For k = 16:
weighted-edge preservation increased further to approximately 0.3503 to 0.5267, while two-qubit reductions decreased to approximately 53.11% to 68.52% and SWAP reductions decreased to approximately 67.75% to 79.57%.

Solution-quality finding:

Solution-quality preservation did not monotonically follow weighted interaction preservation. Random-node extraction showed the lowest overall mean normalized lifted-solution gap, but it also preserved the least interaction structure and is strongly affected by the fill-zero lifting rule. The safe conclusion is that interaction preservation, executability, and lifted solution quality are distinct dimensions.

---

## 9. Main Code Modules

Core modules:

src/qubo_generators.py
src/graph_utils.py
src/graph_metrics.py
src/qubo_io.py
src/qaoa_circuits.py
src/topologies.py
src/topology_alignment.py
src/transpile_eval.py

RQ2 modules:

src/mapping_strategies.py
src/qubo_relabeling.py
src/rq2_mapping_eval.py

RQ3 modules:

src/subqubo_extraction.py
src/qubo_solvers.py

---

## 10. Main Experiment Scripts

RQ1 main scripts:

experiments/rq1_pilot/run_rq1_extended_graph_metrics.py
experiments/rq1_pilot/run_rq1_extended_pre_transpile_metrics.py
experiments/rq1_pilot/run_rq1_extended_transpile_metrics.py
experiments/rq1_pilot/merge_rq1_extended_metrics.py
experiments/rq1_pilot/add_rq1_topology_alignment_metrics.py
experiments/rq1_pilot/make_rq1_final_summary_tables.py
experiments/rq1_pilot/run_rq1_regression_models.py
experiments/rq1_pilot/plot_rq1_final_figures.py

RQ2 main scripts:

experiments/rq1_pilot/run_rq2_full_mapping_metrics.py
experiments/rq1_pilot/make_rq2_summary_tables.py

RQ3 full scripts:

experiments/rq1_pilot/run_rq3_full_subqubo_extraction.py
experiments/rq1_pilot/run_rq3_full_subqubo_executability.py
experiments/rq1_pilot/compare_rq3_full_subqubo_vs_original_executability.py
experiments/rq1_pilot/run_rq3_full_solution_quality.py
experiments/rq1_pilot/make_rq3_full_final_tradeoff_table.py

---

## 11. Main Experimental Claims

Safe claim 1:

QUBO interaction-graph descriptors provide a strong first-order explanation of QAOA circuit complexity.

Safe claim 2:

QUBO-topology alignment descriptors explain additional topology-aware transpilation overhead, especially SWAP insertion.

Safe claim 3:

Standard Qiskit layout/routing is a strong baseline, and naive graph-aware mapping heuristics are not universally beneficial.

Safe claim 4:

Sub-QUBO extraction improves QAOA circuit executability but trades off interaction preservation and lifted solution quality.

Safe claim 5:

The results support a readiness-profile framing rather than a universal readiness score or universal mapping/extraction rule.

---

## 12. Claims to Avoid

Do not claim:

- quantum advantage
- QAOA superiority
- hardware performance
- universal mapping improvement
- universal best extraction strategy
- solution-quality guarantees from sub-QUBO extraction
- industrial-scale deployment readiness

---

## 13. Recommended Manuscript Integration

Results section should be organized by RQ:

1. RQ1: QUBO graph descriptors and QAOA circuit complexity
2. RQ2: graph-aware and topology-aware mapping strategies
3. RQ3: sub-QUBO extraction trade-offs

Discussion should emphasize:

- QUBO graph structure matters
- topology alignment matters
- strong transpiler baselines are necessary
- naive graph-aware heuristics can fail
- subproblem extraction is a multi-objective trade-off
- readiness should be reported as a profile, not a universal score

---

## 14. Current Status

RQ1, RQ2, and RQ3 full experiments are complete enough for manuscript drafting.

Next recommended step:

Create manuscript-ready Results section draft using:

docs/rq1_extended_results_paragraph.md
docs/rq2_results_paragraph.md
docs/rq3_results_paragraph.md

Then revise Experimental Design and Discussion around the final evidence.
