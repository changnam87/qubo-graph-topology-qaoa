# RQ3 statistical validation summary

## Spearman trade-off validation

                scope                                                 relationship                               x                                       y  n  spearman_rho      p_value
         all_families                weighted-edge preservation vs depth reduction mean_weighted_edge_preservation    mean_pct_depth_reduction_vs_original 36     -0.659466 1.217532e-05
         all_families            weighted-edge preservation vs two-qubit reduction mean_weighted_edge_preservation     mean_pct_twoq_reduction_vs_original 36     -0.957705 5.719528e-20
         all_families                 weighted-edge preservation vs SWAP reduction mean_weighted_edge_preservation     mean_pct_swap_reduction_vs_original 24     -0.946887 2.554867e-12
         all_families weighted-edge preservation vs normalized lifted-solution gap mean_weighted_edge_preservation mean_normalized_energy_gap_vs_reference 36     -0.073630 6.695480e-01
         all_families                sub-QUBO size k vs weighted-edge preservation                     k_variables         mean_weighted_edge_preservation 36      0.760513 7.364778e-08
         all_families                           sub-QUBO size k vs depth reduction                     k_variables    mean_pct_depth_reduction_vs_original 36     -0.393833 1.747568e-02
         all_families                       sub-QUBO size k vs two-qubit reduction                     k_variables     mean_pct_twoq_reduction_vs_original 36     -0.747400 1.630786e-07
         all_families                            sub-QUBO size k vs SWAP reduction                     k_variables     mean_pct_swap_reduction_vs_original 24     -0.914737 4.005018e-10
         all_families            sub-QUBO size k vs normalized lifted-solution gap                     k_variables mean_normalized_energy_gap_vs_reference 36     -0.534326 7.885839e-04
    family=assignment            weighted-edge preservation vs two-qubit reduction mean_weighted_edge_preservation     mean_pct_twoq_reduction_vs_original 12     -1.000000 0.000000e+00
    family=assignment                 weighted-edge preservation vs SWAP reduction mean_weighted_edge_preservation     mean_pct_swap_reduction_vs_original  0           NaN          NaN
    family=assignment weighted-edge preservation vs normalized lifted-solution gap mean_weighted_edge_preservation mean_normalized_energy_gap_vs_reference 12     -0.357664 2.536822e-01
    family=assignment                sub-QUBO size k vs weighted-edge preservation                     k_variables         mean_weighted_edge_preservation 12      0.755153 4.516164e-03
    family=assignment                       sub-QUBO size k vs two-qubit reduction                     k_variables     mean_pct_twoq_reduction_vs_original 12     -0.755153 4.516164e-03
    family=assignment                            sub-QUBO size k vs SWAP reduction                     k_variables     mean_pct_swap_reduction_vs_original  0           NaN          NaN
        family=maxcut            weighted-edge preservation vs two-qubit reduction mean_weighted_edge_preservation     mean_pct_twoq_reduction_vs_original 12     -0.965035 3.880985e-07
        family=maxcut                 weighted-edge preservation vs SWAP reduction mean_weighted_edge_preservation     mean_pct_swap_reduction_vs_original 12     -0.965035 3.880985e-07
        family=maxcut weighted-edge preservation vs normalized lifted-solution gap mean_weighted_edge_preservation mean_normalized_energy_gap_vs_reference 12     -0.965035 3.880985e-07
        family=maxcut                sub-QUBO size k vs weighted-edge preservation                     k_variables         mean_weighted_edge_preservation 12      0.946100 3.271760e-06
        family=maxcut                       sub-QUBO size k vs two-qubit reduction                     k_variables     mean_pct_twoq_reduction_vs_original 12     -0.946100 3.271760e-06
        family=maxcut                            sub-QUBO size k vs SWAP reduction                     k_variables     mean_pct_swap_reduction_vs_original 12     -0.946100 3.271760e-06
family=scheduling_toy            weighted-edge preservation vs two-qubit reduction mean_weighted_edge_preservation     mean_pct_twoq_reduction_vs_original 12     -0.936396 7.363376e-06
family=scheduling_toy                 weighted-edge preservation vs SWAP reduction mean_weighted_edge_preservation     mean_pct_swap_reduction_vs_original 12     -0.929329 1.232013e-05
family=scheduling_toy weighted-edge preservation vs normalized lifted-solution gap mean_weighted_edge_preservation mean_normalized_energy_gap_vs_reference 12     -0.505300 9.378559e-02
family=scheduling_toy                sub-QUBO size k vs weighted-edge preservation                     k_variables         mean_weighted_edge_preservation 12      0.832214 7.844348e-04
family=scheduling_toy                       sub-QUBO size k vs two-qubit reduction                     k_variables     mean_pct_twoq_reduction_vs_original 12     -0.951101 2.027733e-06
family=scheduling_toy                            sub-QUBO size k vs SWAP reduction                     k_variables     mean_pct_swap_reduction_vs_original 12     -0.832214 7.844348e-04

## Pareto frequency by extraction strategy

  extraction_strategy  n_rows  n_pareto                profile  within_strategy_pareto_rate  share_of_all_pareto_points
    high_degree_nodes       9         3 pareto_circuit_profile                     0.333333                    0.214286
         random_nodes       9         3 pareto_circuit_profile                     0.333333                    0.214286
     top_weight_edges       9         4 pareto_circuit_profile                     0.444444                    0.285714
weighted_degree_nodes       9         4 pareto_circuit_profile                     0.444444                    0.285714
    high_degree_nodes       9         3    pareto_full_profile                     0.333333                    0.157895
         random_nodes       9         5    pareto_full_profile                     0.555556                    0.263158
     top_weight_edges       9         5    pareto_full_profile                     0.555556                    0.263158
weighted_degree_nodes       9         6    pareto_full_profile                     0.666667                    0.315789

## Pareto frequency by extraction strategy and k

  extraction_strategy  k_variables  n_rows  n_pareto                profile  within_strategy_k_pareto_rate  share_of_all_pareto_points
    high_degree_nodes            8       3         1 pareto_circuit_profile                       0.333333                    0.071429
    high_degree_nodes           12       3         1 pareto_circuit_profile                       0.333333                    0.071429
    high_degree_nodes           16       3         1 pareto_circuit_profile                       0.333333                    0.071429
         random_nodes            8       3         2 pareto_circuit_profile                       0.666667                    0.142857
         random_nodes           12       3         1 pareto_circuit_profile                       0.333333                    0.071429
         random_nodes           16       3         0 pareto_circuit_profile                       0.000000                    0.000000
     top_weight_edges            8       3         2 pareto_circuit_profile                       0.666667                    0.142857
     top_weight_edges           12       3         1 pareto_circuit_profile                       0.333333                    0.071429
     top_weight_edges           16       3         1 pareto_circuit_profile                       0.333333                    0.071429
weighted_degree_nodes            8       3         1 pareto_circuit_profile                       0.333333                    0.071429
weighted_degree_nodes           12       3         1 pareto_circuit_profile                       0.333333                    0.071429
weighted_degree_nodes           16       3         2 pareto_circuit_profile                       0.666667                    0.142857
    high_degree_nodes            8       3         1    pareto_full_profile                       0.333333                    0.052632
    high_degree_nodes           12       3         1    pareto_full_profile                       0.333333                    0.052632
    high_degree_nodes           16       3         1    pareto_full_profile                       0.333333                    0.052632
         random_nodes            8       3         2    pareto_full_profile                       0.666667                    0.105263
         random_nodes           12       3         1    pareto_full_profile                       0.333333                    0.052632
         random_nodes           16       3         2    pareto_full_profile                       0.666667                    0.105263
     top_weight_edges            8       3         2    pareto_full_profile                       0.666667                    0.105263
     top_weight_edges           12       3         1    pareto_full_profile                       0.333333                    0.052632
     top_weight_edges           16       3         2    pareto_full_profile                       0.666667                    0.105263
weighted_degree_nodes            8       3         2    pareto_full_profile                       0.666667                    0.105263
weighted_degree_nodes           12       3         2    pareto_full_profile                       0.666667                    0.105263
weighted_degree_nodes           16       3         2    pareto_full_profile                       0.666667                    0.105263

## Strategy-by-k descriptive summary

  extraction_strategy  k_variables  n_cells  mean_weighted_edge_preservation  mean_depth_reduction  mean_twoq_reduction  mean_swap_reduction  mean_normalized_quality_gap
    high_degree_nodes            8        3                         0.206583             49.876877            83.259323            95.219757                     0.513798
    high_degree_nodes           12        3                         0.355122             39.055613            69.773565            85.078291                     0.375658
    high_degree_nodes           16        3                         0.519314             28.949310            53.108730            67.744965                     0.276301
         random_nodes            8        3                         0.127964             53.313347            89.889214            98.079937                     0.508479
         random_nodes           12        3                         0.164866             46.705899            86.527000            92.726302                     0.307505
         random_nodes           16        3                         0.350336             34.823360            68.522427            77.972651                     0.195318
     top_weight_edges            8        3                         0.193381             53.950860            85.370478            97.486756                     0.537353
     top_weight_edges           12        3                         0.327952             47.080408            74.229828            90.979797                     0.381565
     top_weight_edges           16        3                         0.474629             37.856184            60.730299            79.566821                     0.264128
weighted_degree_nodes            8        3                         0.212563             50.258913            83.343102            95.251411                     0.508749
weighted_degree_nodes           12        3                         0.361799             39.400786            70.054151            85.318235                     0.368826
weighted_degree_nodes           16        3                         0.526656             29.306046            53.609274            68.385521                     0.269133
