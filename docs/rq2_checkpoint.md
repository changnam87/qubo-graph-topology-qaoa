# RQ2 Checkpoint

Project: qubo-graph-topology-qaoa

Paper target: IEEE TQE

Working title:
From Industrial QUBOs to Executable QAOA Circuits: QUBO-Graph-Aware and Topology-Aware Compilation

---

## 1. RQ2

RQ2:
Can QUBO-graph-aware variable ordering and topology-aware logical mapping reduce transpilation overhead relative to natural, random, and standard Qiskit baselines?

This checkpoint documents the completed RQ2 mapping-strategy experiment.

---

## 2. Final RQ2 Dataset

The full RQ2 experiment reused the RQ1 extended QUBO dataset:

- 60 QUBO instances
- 3 QUBO families
- 5 variable sizes
- 3 sparse topologies
- 8 mapping strategies
- 1,440 strategy-topology-instance observations

QUBO families:

1. MaxCut-style QUBOs
2. Assignment-style QUBOs
3. Scheduling-derived toy QUBOs

Variable sizes:

8, 12, 16, 24, 32 binary variables

Sparse topologies:

1. line
2. grid_2d
3. heavy_hex_like

The fully connected topology was excluded from RQ2 because mapping and routing effects are not meaningful when every interaction is directly connected.

---

## 3. RQ2 Strategy Set

The final RQ2 strategies were:

1. standard_qiskit
   - no custom relabeling
   - initial_layout = None
   - Qiskit chooses layout and routing

2. natural_fixed
   - natural variable order
   - initial_layout = [0, 1, ..., n-1]

3. random_fixed
   - random relabeling
   - fixed identity layout after relabeling

4. degree_desc_fixed
   - degree-descending QUBO variable relabeling
   - fixed identity layout after relabeling

5. weighted_degree_desc_fixed
   - weighted-degree-descending QUBO variable relabeling
   - fixed identity layout after relabeling

6. degree_desc_centrality_layout
   - degree-descending QUBO variable relabeling
   - central physical qubit placement

7. weighted_degree_desc_centrality_layout
   - weighted-degree-descending QUBO variable relabeling
   - central physical qubit placement

8. bfs_topology_aware
   - QUBO BFS ordering
   - topology BFS physical placement

---

## 4. RQ2 Code Components

New or modified modules:

src/mapping_strategies.py
src/qubo_relabeling.py
src/rq2_mapping_eval.py
src/transpile_eval.py

Key functionality:

- variable ordering strategies
- QUBO relabeling by ordering
- objective-preserving relabeling validation
- optional initial_layout support in transpile_and_evaluate
- topology-aware centrality placement
- BFS topology-aware placement
- unified RQ2 mapping condition preparation

---

## 5. RQ2 Experiment Scripts

Main RQ2 scripts:

experiments/rq1_pilot/rq2_single_instance_ordering_test.py
experiments/rq1_pilot/rq2_single_instance_ordering_fixed_layout_test.py
experiments/rq1_pilot/run_rq2_ordering_pilot_metrics.py
experiments/rq1_pilot/rq2_single_instance_topology_aware_test.py
experiments/rq1_pilot/rq2_single_instance_bfs_topology_aware_test.py
experiments/rq1_pilot/run_rq2_final_scope_dry_run.py
experiments/rq1_pilot/run_rq2_full_mapping_metrics.py
experiments/rq1_pilot/make_rq2_summary_tables.py

---

## 6. RQ2 Output Files

Main full RQ2 output:

results/rq2_full/rq2_mapping_metrics.csv

Summary tables:

results/rq2_full/table_rq2_strategy_summary.csv
results/rq2_full/table_rq2_family_strategy_summary.csv
results/rq2_full/table_rq2_topology_strategy_summary.csv
results/rq2_full/table_rq2_win_rates.csv

Writing files:

docs/rq2_pilot_diagnostic_note.md
docs/rq2_results_paragraph.md
docs/rq2_checkpoint.md

---

## 7. Main Validation Results

Completed validation checks:

PASS: RQ2 variable ordering strategies work.
PASS: QUBO relabeling preserves objective energy.
PASS: RQ2 single-instance ordering comparison generated and validated.
PASS: transpile_and_evaluate supports initial_layout.
PASS: RQ2 fixed-layout single-instance ordering comparison generated and validated.
PASS: topology-aware physical layout functions work.
PASS: RQ2 single-instance topology-aware placement comparison generated and validated.
PASS: BFS topology-aware layout function works.
PASS: RQ2 BFS topology-aware single-instance comparison generated and validated.
PASS: RQ2 pilot diagnostic note saved.
PASS: RQ2 mapping condition helper works.
PASS: RQ2 final-scope dry run generated and validated.
PASS: full RQ2 mapping metrics generated and validated.
PASS: RQ2 summary tables generated and validated.
PASS: RQ2 Results paragraph saved.

---

## 8. Key RQ2 Findings

Main result:

standard_qiskit was the strongest overall baseline.

Relative to natural_fixed, standard_qiskit reduced:

- mean transpiled depth by 7.361
- mean two-qubit count by 12.261
- mean SWAP count by 12.261

Approximate percentage reductions:

- depth: 8.4%
- two-qubit count: 8.6%
- SWAP count: 33.3%

Win rate of standard_qiskit vs natural_fixed:

- two-qubit count: about 71.1%
- SWAP count: about 71.1%

---

## 9. Custom Strategy Findings

Custom strategies did not provide universal improvement.

Relative to natural_fixed:

- degree_desc_fixed increased average depth, two-qubit count, and SWAP count.
- weighted_degree_desc_fixed also increased average overhead.
- random_fixed was unstable and generally harmful.
- centrality-based topology-aware placement increased overhead on average.
- BFS topology-aware placement also increased overhead on average.

Selected scheduling-derived instances showed improvement under degree-based ordering, but the effect was not robust across families and topologies.

---

## 10. Family-Dependent Effects

The RQ2 pilot diagnostics showed:

assignment:
degree-based strategies were often identical or close to natural due to structural symmetry.

maxcut:
degree-based and weighted-degree strategies often worsened routing overhead.

scheduling_toy:
degree-based strategies showed selected improvements, but not enough to support a universal claim.

---

## 11. Topology-Dependent Effects

Sparse and path-like topologies showed stronger sensitivity to poor mapping.

Line topology was especially sensitive to ordering and placement.

Naive centrality placement was harmful on line topology because placing important variables near central physical qubits did not necessarily preserve QUBO interaction locality along the path.

---

## 12. RQ2 Main Conclusion

RQ2 does not support the claim that simple QUBO-graph-aware ordering universally reduces transpilation overhead.

Instead, RQ2 supports a bounded and practically important conclusion:

Mapping strategy performance is baseline-dependent, family-dependent, and topology-dependent.

Standard Qiskit layout/routing is a strong baseline.

Random ordering is unstable.

Naive graph-aware ordering and naive topology-aware placement can increase routing overhead.

Therefore, QUBO-graph-aware compilation should be reported as a strategy-dependent readiness profile rather than as a universal mapping rule.

---

## 13. Bounded Claims

No quantum advantage claim is made.

No QAOA optimization superiority claim is made.

No hardware execution claim is made.

The RQ2 results are compilation-level evidence about transpilation overhead under local coupling-map simulations.

---

## 14. Current Status

RQ2 is complete enough to move to RQ3.

Recommended next step:

Begin RQ3 sub-QUBO extraction experiments.

RQ3 should evaluate how sub-QUBO extraction strategies trade off:

- interaction preservation
- feasibility preservation
- classical solution-quality preservation
- QAOA circuit executability
