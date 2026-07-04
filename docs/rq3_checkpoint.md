# RQ3 Checkpoint

Project: qubo-graph-topology-qaoa

Paper target: IEEE TQE

Working title:
From Industrial QUBOs to Executable QAOA Circuits: QUBO-Graph-Aware and Topology-Aware Compilation

---

## 1. RQ3

RQ3:
How do sub-QUBO extraction strategies trade off interaction preservation, feasibility preservation, classical solution-quality preservation, and QAOA circuit executability?

This checkpoint documents the completed full RQ3 analysis.

---

## 2. RQ3 Full Scope

The full RQ3 analysis evaluates sub-QUBO extraction from all extended QUBO instances with 24 and 32 variables.

Original QUBO families:

1. MaxCut-style QUBOs
2. Assignment-style QUBOs
3. Scheduling-derived toy QUBOs

Original sizes:

- 24 variables
- 32 variables

Original QUBO count:

- MaxCut: 12 instances
- Assignment: 6 instances
- Scheduling_toy: 6 instances
- Total: 24 original QUBOs

Subproblem sizes:

- k = 8
- k = 12
- k = 16

Extraction strategies:

1. top_weight_edges
2. high_degree_nodes
3. weighted_degree_nodes
4. random_nodes

Full RQ3 sub-QUBO count:

24 original QUBOs × 3 k values × 4 strategies = 288 sub-QUBOs

Sparse topologies used for executability evaluation:

1. line
2. grid_2d
3. heavy_hex_like

Full RQ3 executability observations:

288 sub-QUBOs × 3 sparse topologies = 864 transpilation observations

---

## 3. RQ3 Pipeline

The completed full RQ3 pipeline is:

original QUBO
-> interaction graph
-> sub-QUBO variable selection
-> induced sub-QUBO extraction
-> interaction preservation metrics
-> p = 1 QAOA circuit construction
-> topology-aware transpilation
-> original-vs-sub-QUBO executability comparison
-> exact sub-QUBO solution
-> lifted solution evaluation in original QUBO space
-> final preservation-executability-quality trade-off table

---

## 4. RQ3 Code Components

New RQ3 modules:

src/subqubo_extraction.py
src/qubo_solvers.py

Key functions in src/subqubo_extraction.py:

- available_subqubo_strategies
- select_subqubo_variables
- extract_subqubo
- compute_interaction_preservation_metrics

Key functions in src/qubo_solvers.py:

- qubo_energy
- brute_force_solve_qubo
- greedy_local_search_qubo
- lift_subqubo_solution_to_original
- solution_hamming_weight

---

## 5. RQ3 Full Experiment Scripts

Main full RQ3 scripts:

experiments/rq1_pilot/run_rq3_full_subqubo_extraction.py
experiments/rq1_pilot/run_rq3_full_subqubo_executability.py
experiments/rq1_pilot/compare_rq3_full_subqubo_vs_original_executability.py
experiments/rq1_pilot/run_rq3_full_solution_quality.py
experiments/rq1_pilot/make_rq3_full_final_tradeoff_table.py

Earlier pilot scripts are retained for traceability, but the full RQ3 results should be used for the manuscript.

---

## 6. RQ3 Full Output Files

Sub-QUBO JSON files:

data/subqubos_rq3_full/*.json

Main full RQ3 result files:

results/rq3_full/subqubo_extraction_metrics.csv
results/rq3_full/subqubo_executability_metrics.csv
results/rq3_full/subqubo_vs_original_executability.csv
results/rq3_full/subqubo_solution_quality_metrics.csv
results/rq3_full/rq3_final_tradeoff_table.csv

Writing files:

docs/rq3_results_paragraph.md
docs/rq3_checkpoint.md

Pilot result files retained for traceability:

results/rq3_pilot/subqubo_extraction_metrics.csv
results/rq3_pilot/subqubo_executability_metrics.csv
results/rq3_pilot/rq3_tradeoff_summary.csv
results/rq3_pilot/subqubo_vs_original_executability.csv
results/rq3_pilot/subqubo_solution_quality_metrics.csv
results/rq3_pilot/rq3_final_tradeoff_table.csv

---

## 7. Validation Results

Completed validation checks:

PASS: RQ3 sub-QUBO extraction utilities work.
PASS: RQ3 full sub-QUBO extraction generated and validated.
PASS: RQ3 full sub-QUBO executability metrics generated and validated.
PASS: RQ3 full sub-QUBO vs original executability comparison generated and validated.
PASS: RQ3 QUBO solver utilities work.
PASS: sub-QUBO solution lifting works.
PASS: RQ3 full sub-QUBO solution-quality metrics generated and validated.
PASS: RQ3 full final trade-off table generated and validated.
PASS: RQ3 full final trade-off summary printed.
PASS: RQ3 full Results paragraph saved.

---

## 8. Interaction Preservation Findings

Overall mean weighted-edge preservation:

weighted_degree_nodes:
0.3670

high_degree_nodes:
0.3603

top_weight_edges:
0.3320

random_nodes:
0.2144

Interpretation:

weighted-degree-node extraction preserved the most weighted QUBO interaction structure.

high-degree-node extraction was similar.

top-weight-edge extraction preserved a lower but still substantial amount of weighted interaction structure.

random-node extraction preserved substantially less weighted interaction structure.

---

## 9. Executability Findings

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

Interpretation:

more aggressive or less structure-preserving extraction can produce larger executability gains, but it may discard more of the original QUBO interaction structure.

---

## 10. k-Dependent Trade-Off

For k = 8:

weighted-edge preservation was approximately 0.1280 to 0.2126.
two-qubit reductions were approximately 83.26% to 89.89%.
SWAP reductions were approximately 95.22% to 98.08%.

For k = 12:

weighted-edge preservation increased to approximately 0.1649 to 0.3618.
two-qubit reductions were approximately 69.77% to 86.53%.
SWAP reductions were approximately 85.08% to 92.73%.

For k = 16:

weighted-edge preservation increased further to approximately 0.3503 to 0.5267.
two-qubit reductions decreased to approximately 53.11% to 68.52%.
SWAP reductions decreased to approximately 67.75% to 79.57%.

Interpretation:

larger sub-QUBOs preserve more original interaction structure but give smaller executability gains.

smaller sub-QUBOs improve executability more strongly but sacrifice preservation.

---

## 11. Solution-Quality Preservation Findings

Sub-QUBO exact solutions were lifted to the original QUBO variable space using fill_value = 0 for unselected variables.

Original QUBO reference solutions were obtained using greedy local search.

The lifted solution was evaluated on the original QUBO objective.

Overall mean normalized lifted-solution gaps:

random_nodes:
0.3371

weighted_degree_nodes:
0.3822

high_degree_nodes:
0.3886

top_weight_edges:
0.3943

Important interpretation:

This does not imply that random-node extraction is generally preferable.

random_nodes preserved the least interaction structure and is strongly affected by the fill-zero lifting rule.

The safe conclusion is that solution-quality preservation does not monotonically follow interaction preservation.

Family-dependent patterns were observed.

MaxCut-style instances:
weighted_degree_nodes produced the smallest mean normalized quality gap.

Assignment-style and scheduling-derived toy instances:
strategy rankings differed, indicating sensitivity to QUBO family structure and lifting rule.

---

## 12. RQ3 Main Conclusion

RQ3 supports the premise that sub-QUBO extraction is a multi-objective readiness trade-off.

The trade-off has three main dimensions:

1. interaction preservation
2. QAOA circuit executability
3. lifted solution-quality preservation

Main conclusion:

Smaller sub-QUBOs improve circuit executability but sacrifice interaction preservation.

Larger sub-QUBOs preserve more interaction structure but reduce compilation savings.

Solution-quality preservation depends on QUBO family, extraction strategy, and lifting rule.

Therefore, sub-QUBO extraction should be reported as a readiness profile rather than a single best universal reduction rule.

---

## 13. Bounded Claims

No quantum advantage claim is made.

No QAOA optimization superiority claim is made.

No hardware execution claim is made.

Classical solvers are used only as reference tools for evaluating solution-quality preservation.

Sub-QUBO solution quality is evaluated through a simple fill-zero lifting rule, which should be reported as a limitation.

---

## 14. Current Status

RQ3 full analysis is complete enough for manuscript drafting.

Recommended next step:

Update the full experiment checkpoint to reflect RQ3 full rather than RQ3 pilot.

Then proceed to manuscript-ready Results section drafting.
