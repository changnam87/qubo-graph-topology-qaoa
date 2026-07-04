# RQ1 statistical validation summary

## Spearman correlations

                 scope                                                  relationship                               x                   y   n  spearman_rho       p_value
      all_observations             QUBO interaction edges vs pre-transpilation depth                         n_edges pre_transpile_depth 240      0.937095 9.025488e-111
      all_observations                    QUBO interaction edges vs transpiled depth                         n_edges    transpiled_depth 240      0.931235 2.542296e-106
      all_observations          QUBO interaction edges vs transpiled two-qubit count                         n_edges transpiled_2q_count 240      0.991323 9.554403e-212
      all_observations                        QUBO graph density vs transpiled depth                         density    transpiled_depth 240      0.718770  1.923714e-39
      all_observations                            Average degree vs transpiled depth                      avg_degree    transpiled_depth 240      0.966864 4.009887e-143
      all_observations                            Maximum degree vs transpiled depth                      max_degree    transpiled_depth 240      0.974192 7.477874e-156
      all_observations                           Weighted degree vs transpiled depth            weighted_degree_mean    transpiled_depth 240      0.951254 1.402668e-123
      all_observations                  Topology-alignment ratio vs transpiled depth        topology_alignment_ratio    transpiled_depth 240     -0.741244  4.345723e-43
      all_observations                        Topology-alignment ratio vs SWAP count        topology_alignment_ratio          swap_count 240     -0.951951 2.631481e-124
      all_observations           Weighted mean topology distance vs transpiled depth weighted_mean_topology_distance    transpiled_depth 240      0.733331  9.205626e-42
      all_observations                 Weighted mean topology distance vs SWAP count weighted_mean_topology_distance          swap_count 240      0.960850 1.164959e-134
      all_observations Weighted mean topology distance vs transpiled two-qubit count weighted_mean_topology_distance transpiled_2q_count 240      0.656926  5.030081e-31
     family=assignment                    QUBO interaction edges vs transpiled depth                         n_edges    transpiled_depth  60           NaN           NaN
     family=assignment                        Topology-alignment ratio vs SWAP count        topology_alignment_ratio          swap_count  60           NaN           NaN
     family=assignment           Weighted mean topology distance vs transpiled depth weighted_mean_topology_distance    transpiled_depth  60           NaN           NaN
     family=assignment                 Weighted mean topology distance vs SWAP count weighted_mean_topology_distance          swap_count  60           NaN           NaN
         family=maxcut                    QUBO interaction edges vs transpiled depth                         n_edges    transpiled_depth 120      0.941343  1.658444e-57
         family=maxcut                        Topology-alignment ratio vs SWAP count        topology_alignment_ratio          swap_count 120     -0.937959  4.110007e-56
         family=maxcut           Weighted mean topology distance vs transpiled depth weighted_mean_topology_distance    transpiled_depth 120      0.616034  6.943407e-14
         family=maxcut                 Weighted mean topology distance vs SWAP count weighted_mean_topology_distance          swap_count 120      0.938560  2.356015e-56
 family=scheduling_toy                    QUBO interaction edges vs transpiled depth                         n_edges    transpiled_depth  60      0.935589  6.662643e-28
 family=scheduling_toy                        Topology-alignment ratio vs SWAP count        topology_alignment_ratio          swap_count  60     -0.932095  2.936175e-27
 family=scheduling_toy           Weighted mean topology distance vs transpiled depth weighted_mean_topology_distance    transpiled_depth  60      0.680167  2.268222e-09
 family=scheduling_toy                 Weighted mean topology distance vs SWAP count weighted_mean_topology_distance          swap_count  60      0.952150  1.514898e-31
sparse_topologies_only                        Topology-alignment ratio vs SWAP count        topology_alignment_ratio          swap_count 180     -0.919550  4.062736e-74
sparse_topologies_only           Weighted mean topology distance vs transpiled depth weighted_mean_topology_distance    transpiled_depth 180      0.902915  3.505870e-67
sparse_topologies_only                 Weighted mean topology distance vs SWAP count weighted_mean_topology_distance          swap_count 180      0.941784  3.472906e-86
