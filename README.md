# QUBO-Graph-Aware and Topology-Aware QAOA Compilation

This repository contains the reproducibility package for the paper:

From Industrial QUBOs to Executable QAOA Circuits: QUBO-Graph-Aware and Topology-Aware Compilation

## Scope

This repository does not claim quantum advantage, QAOA superiority, or hardware execution performance. The experiments analyze QAOA circuit executability and transpilation-level behavior under controlled QUBO families and backend topology classes.

## Research Questions

RQ1: To what extent do QUBO interaction-graph descriptors explain pre- and post-transpilation QAOA circuit complexity?

RQ2: Can QUBO-graph-aware variable ordering and topology-aware logical mapping reduce transpilation overhead relative to natural, random, and standard Qiskit baselines?

RQ3: How do sub-QUBO extraction strategies trade off interaction preservation, feasibility-related preservation where applicable, classical solution-quality preservation, and QAOA circuit executability?

## Repository Structure

src/        Core Python modules.
scripts/    Scripts for statistical validation and figure generation.
docs/       Experiment checkpoints and result notes.
data/       Generated QUBO and sub-QUBO JSON instances.
results/    Processed result tables and statistical summaries.
figures/    Figures used in the manuscript.

## Main Result Folders

results/rq1_extended/
results/rq2_full/
results/rq3_full/

## Reproducing Key Outputs

Figure generation:

python3 scripts/make_rq1_composite_figure.py
python3 scripts/make_rq2_figure.py
python3 scripts/make_rq3_figure.py

Statistical validation:

python3 scripts/analyze_rq1_statistics.py
python3 scripts/analyze_rq2_statistics.py
python3 scripts/analyze_rq3_statistics.py

## Data

The experiments use synthetically generated or derived benchmark QUBO instances from MaxCut-style, assignment-style, and scheduling-derived toy families. No human-subject data, proprietary industrial data, or hardware-execution data are included.

## License

See LICENSE.
