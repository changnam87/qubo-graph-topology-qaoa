"""
Run formal but compact RQ1 regression models.

Input:
    results/rq1_extended/merged_rq1_metrics_with_alignment.csv

Outputs:
    results/rq1_extended/rq1_regression_model_summary.csv
    results/rq1_extended/rq1_regression_coefficients.csv
    results/rq1_extended/rq1_regression_model_notes.md

Purpose:
    Evaluate whether QUBO graph descriptors and topology-alignment descriptors
    explain QAOA circuit/transpilation metrics.

Important:
    These models are explanatory/screening models.
    They are not causal models and do not claim quantum advantage.
"""

from __future__ import annotations

from pathlib import Path
import sys

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf


PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))


RESULTS_DIR = PROJECT_ROOT / "results" / "rq1_extended"

INPUT_PATH = RESULTS_DIR / "merged_rq1_metrics_with_alignment.csv"
MODEL_SUMMARY_PATH = RESULTS_DIR / "rq1_regression_model_summary.csv"
COEF_PATH = RESULTS_DIR / "rq1_regression_coefficients.csv"
NOTES_PATH = RESULTS_DIR / "rq1_regression_model_notes.md"


def zscore(series: pd.Series) -> pd.Series:
    """
    Population z-score.

    If the standard deviation is zero, return zeros.
    """
    mean = series.mean()
    std = series.std(ddof=0)

    if std == 0 or pd.isna(std):
        return pd.Series(np.zeros(len(series)), index=series.index)

    return (series - mean) / std


def fit_ols_model(df: pd.DataFrame, formula: str, model_name: str, outcome: str):
    """
    Fit OLS with HC3 robust standard errors.
    """
    model = smf.ols(formula=formula, data=df).fit(cov_type="HC3")

    summary_row = {
        "model_name": model_name,
        "outcome": outcome,
        "n": int(model.nobs),
        "r_squared": model.rsquared,
        "adj_r_squared": model.rsquared_adj,
        "aic": model.aic,
        "bic": model.bic,
        "formula": formula,
    }

    coef_rows = []

    conf = model.conf_int()
    conf.columns = ["ci_lower", "ci_upper"]

    for term in model.params.index:
        coef_rows.append(
            {
                "model_name": model_name,
                "outcome": outcome,
                "term": term,
                "coef": model.params[term],
                "std_error_hc3": model.bse[term],
                "t_value": model.tvalues[term],
                "p_value": model.pvalues[term],
                "ci_lower": conf.loc[term, "ci_lower"],
                "ci_upper": conf.loc[term, "ci_upper"],
            }
        )

    return summary_row, coef_rows


def main() -> None:
    df = pd.read_csv(INPUT_PATH)

    # ------------------------------------------------------------------
    # Outcome transforms
    # ------------------------------------------------------------------
    df["log_pre_depth"] = np.log1p(df["pre_transpile_depth"])
    df["log_transpiled_depth"] = np.log1p(df["transpiled_depth"])
    df["log_swap_count"] = np.log1p(df["swap_count"])
    df["log_transpiled_2q_count"] = np.log1p(df["transpiled_2q_count"])

    # ------------------------------------------------------------------
    # Standardized predictors
    # ------------------------------------------------------------------
    raw_predictors = [
        "n_edges",
        "density",
        "max_degree",
        "weighted_degree_mean",
        "coefficient_entropy",
        "modularity",
        "topology_alignment_ratio",
        "weighted_topology_alignment_ratio",
        "mean_topology_distance",
        "weighted_mean_topology_distance",
    ]

    for col in raw_predictors:
        df[f"z_{col}"] = zscore(df[col])

    # ------------------------------------------------------------------
    # Compact model specifications
    # ------------------------------------------------------------------
    model_specs = []

    # Pre-transpile model:
    # topology alignment should not matter before transpilation.
    model_specs.append(
        {
            "model_name": "M1_pre_depth_graph",
            "outcome": "log_pre_depth",
            "formula": (
                "log_pre_depth ~ z_n_edges + z_density + z_max_degree "
                "+ z_weighted_degree_mean + z_coefficient_entropy "
                "+ C(family)"
            ),
        }
    )

    # Post-transpile depth: graph-only model.
    model_specs.append(
        {
            "model_name": "M2_transpiled_depth_graph_topologyFE",
            "outcome": "log_transpiled_depth",
            "formula": (
                "log_transpiled_depth ~ z_n_edges + z_density + z_max_degree "
                "+ z_weighted_degree_mean + z_coefficient_entropy "
                "+ C(family) + C(topology)"
            ),
        }
    )

    # Post-transpile depth: graph + topology-alignment model.
    model_specs.append(
        {
            "model_name": "M3_transpiled_depth_graph_alignment",
            "outcome": "log_transpiled_depth",
            "formula": (
                "log_transpiled_depth ~ z_n_edges + z_density + z_max_degree "
                "+ z_weighted_degree_mean + z_coefficient_entropy "
                "+ z_topology_alignment_ratio "
                "+ z_weighted_mean_topology_distance "
                "+ C(family) + C(topology)"
            ),
        }
    )

    # Two-qubit count after transpilation.
    model_specs.append(
        {
            "model_name": "M4_transpiled_2q_graph_alignment",
            "outcome": "log_transpiled_2q_count",
            "formula": (
                "log_transpiled_2q_count ~ z_n_edges + z_density + z_max_degree "
                "+ z_weighted_degree_mean + z_coefficient_entropy "
                "+ z_topology_alignment_ratio "
                "+ z_weighted_mean_topology_distance "
                "+ C(family) + C(topology)"
            ),
        }
    )

    # SWAP count across all topologies.
    # fully_connected has all zero swaps, so topology fixed effects are important.
    model_specs.append(
        {
            "model_name": "M5_swap_all_topologies",
            "outcome": "log_swap_count",
            "formula": (
                "log_swap_count ~ z_n_edges + z_density + z_max_degree "
                "+ z_weighted_degree_mean + z_coefficient_entropy "
                "+ z_topology_alignment_ratio "
                "+ z_weighted_mean_topology_distance "
                "+ C(family) + C(topology)"
            ),
        }
    )

    # SWAP count only for sparse topologies.
    sparse_df = df[df["topology"] != "fully_connected"].copy()

    sparse_model_specs = [
        {
            "model_name": "M6_swap_sparse_topologies_only",
            "outcome": "log_swap_count",
            "formula": (
                "log_swap_count ~ z_n_edges + z_density + z_max_degree "
                "+ z_weighted_degree_mean + z_coefficient_entropy "
                "+ z_topology_alignment_ratio "
                "+ z_weighted_mean_topology_distance "
                "+ C(family) + C(topology)"
            ),
        }
    ]

    summary_rows = []
    coefficient_rows = []

    for spec in model_specs:
        summary, coefs = fit_ols_model(
            df=df,
            formula=spec["formula"],
            model_name=spec["model_name"],
            outcome=spec["outcome"],
        )
        summary_rows.append(summary)
        coefficient_rows.extend(coefs)

    for spec in sparse_model_specs:
        summary, coefs = fit_ols_model(
            df=sparse_df,
            formula=spec["formula"],
            model_name=spec["model_name"],
            outcome=spec["outcome"],
        )
        summary_rows.append(summary)
        coefficient_rows.extend(coefs)

    summary_df = pd.DataFrame(summary_rows)
    coef_df = pd.DataFrame(coefficient_rows)

    summary_df.to_csv(MODEL_SUMMARY_PATH, index=False)
    coef_df.to_csv(COEF_PATH, index=False)

    notes = """# RQ1 Regression Model Notes

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
"""

    NOTES_PATH.write_text(notes, encoding="utf-8")

    print("=" * 80)
    print("RQ1 regression models saved")
    print("=" * 80)
    print(f"model summary: {MODEL_SUMMARY_PATH}")
    print(f"coefficients: {COEF_PATH}")
    print(f"notes: {NOTES_PATH}")
    print()

    print("Model summary:")
    print(
        summary_df[
            [
                "model_name",
                "outcome",
                "n",
                "r_squared",
                "adj_r_squared",
                "aic",
                "bic",
            ]
        ].round(4).to_string(index=False)
    )
    print()

    print("Key coefficients:")
    key_terms = [
        "z_n_edges",
        "z_density",
        "z_max_degree",
        "z_weighted_degree_mean",
        "z_topology_alignment_ratio",
        "z_weighted_mean_topology_distance",
    ]

    key = coef_df[coef_df["term"].isin(key_terms)].copy()
    print(
        key[
            [
                "model_name",
                "outcome",
                "term",
                "coef",
                "std_error_hc3",
                "p_value",
                "ci_lower",
                "ci_upper",
            ]
        ].round(4).to_string(index=False)
    )


if __name__ == "__main__":
    main()
