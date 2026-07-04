# RQ1 Regression Model Notes

These models are compact explanatory models for RQ1.

Input:
results/rq1_extended/merged_rq1_metrics_with_alignment.csv

Modeling choices:
- OLS regression is used on log1p-transformed circuit/transpilation outcomes.
- Continuous predictors are z-scored.
- HC3 robust standard errors are used.
- Family fixed effects are included where appropriate.
- Topology fixed effects are included for post-transpilation outcomes.
- The models are explanatory/screening models, not causal models.
- No quantum advantage, QAOA superiority, or hardware execution claim is made.

Main model logic:
- M1 tests graph descriptors for pre-transpilation depth.
- M2 tests graph descriptors plus topology fixed effects for transpiled depth.
- M3 adds topology-alignment descriptors for transpiled depth.
- M4 tests graph and alignment descriptors for transpiled two-qubit count.
- M5 tests graph and alignment descriptors for SWAP count across all topologies.
- M6 repeats SWAP-count modeling only on sparse topologies, excluding fully_connected because fully_connected has zero SWAP count by construction.

Recommended reporting:
- Report adjusted R-squared for M1-M6.
- Focus on the sign and magnitude of n_edges, topology_alignment_ratio, and weighted_mean_topology_distance.
- Treat p-values as supportive but not definitive because this is a synthetic/reproducible benchmark study with repeated topology observations per QUBO instance.
