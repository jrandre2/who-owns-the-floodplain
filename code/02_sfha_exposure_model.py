#!/usr/bin/env python3
"""
Module: 02_sfha_exposure_model.py
Purpose: Owner-level Poisson GLM for SFHA flood exposure analysis.

This module estimates the relationship between owner organizational form
and SFHA (Special Flood Hazard Area) exposure using a Poisson regression
with offset for total parcels owned.

Key outputs:
- Incidence Rate Ratios (IRR) by owner type
- 95% confidence intervals
- Overdispersion diagnostics

Adapted from the Freeze and Flight project for standalone replication.

Input Files
-----------
- data/parcels_with_classification.csv
- data/sfr_regression_data.csv

Output Files
------------
- data/owner_level_sfha_results.csv
"""
from __future__ import annotations
from pathlib import Path
import pandas as pd
import numpy as np
import statsmodels.api as sm
from statsmodels.genmod.families import Poisson, NegativeBinomial
import argparse
import warnings
warnings.filterwarnings('ignore')

DATA_DIR = Path('data')


def load_and_merge_data(
    classification_path: Path,
    regression_path: Path
) -> pd.DataFrame:
    """
    Load and merge parcel classification with SFHA status.

    Parameters
    ----------
    classification_path : Path
        Path to owner classification CSV.
    regression_path : Path
        Path to regression data CSV with SFHA status.

    Returns
    -------
    pd.DataFrame
        Merged dataset with owner names and SFHA status.
    """
    print("Loading parcel classification data...")
    parcel_df = pd.read_csv(
        classification_path,
        usecols=['Parcel_ID', 'owner_name', 'predicted_owner_type', 'prediction_confidence']
    )

    print("Loading SFR regression data...")
    sfr_df = pd.read_csv(
        regression_path,
        usecols=['parcel_id', 'in_sfha', 'owner_Corporation', 'owner_LLC', 'owner_Other', 'owner_Trust']
    )

    # Normalize parcel IDs
    parcel_df['parcel_id'] = parcel_df['Parcel_ID'].astype(str)
    sfr_df['parcel_id'] = sfr_df['parcel_id'].astype(str)

    merged = pd.merge(
        sfr_df,
        parcel_df[['parcel_id', 'owner_name', 'predicted_owner_type']],
        on='parcel_id',
        how='inner'
    )

    print(f"Merged: {len(merged):,} SFR parcels with owner names")
    return merged


def aggregate_to_owner_level(merged: pd.DataFrame) -> pd.DataFrame:
    """
    Aggregate parcel data to owner level.

    Parameters
    ----------
    merged : pd.DataFrame
        Parcel-level data with owner names and SFHA status.

    Returns
    -------
    pd.DataFrame
        Owner-level aggregates with parcel counts and SFHA exposure.
    """
    merged['entity_type'] = merged['predicted_owner_type'].fillna('Individual')

    owner_agg = merged.groupby(['owner_name', 'entity_type']).agg(
        total_parcels=('parcel_id', 'count'),
        sfha_parcels=('in_sfha', 'sum')
    ).reset_index()

    print(f"Number of unique owners: {len(owner_agg):,}")
    return owner_agg


def fit_poisson_model(owner_agg: pd.DataFrame) -> dict:
    """
    Fit Poisson GLM with offset for SFHA exposure.

    Parameters
    ----------
    owner_agg : pd.DataFrame
        Owner-level data with total_parcels and sfha_parcels.

    Returns
    -------
    dict
        Model results including IRRs and confidence intervals.
    """
    # Create entity type dummies (Individual as reference)
    owner_agg['is_LLC'] = (owner_agg['entity_type'] == 'LLC').astype(int)
    owner_agg['is_Corporation'] = (owner_agg['entity_type'] == 'Corporation').astype(int)
    owner_agg['is_Trust'] = (owner_agg['entity_type'] == 'Trust').astype(int)
    owner_agg['is_Other'] = (owner_agg['entity_type'] == 'Other').astype(int)

    # Create offset (log of total parcels)
    owner_agg['log_total'] = np.log(owner_agg['total_parcels'])

    # Design matrix
    X = owner_agg[['is_LLC', 'is_Corporation', 'is_Trust', 'is_Other']]
    X = sm.add_constant(X)

    y = owner_agg['sfha_parcels']

    # Fit Poisson model with offset
    print("Fitting Poisson model with offset log(total_parcels)...")
    poisson_model = sm.GLM(y, X, family=Poisson(), offset=owner_agg['log_total'])
    results = poisson_model.fit()

    # Extract IRRs and CIs
    params = results.params
    conf = results.conf_int()
    pvalues = results.pvalues

    irr_df = pd.DataFrame({
        'Coefficient': params,
        'IRR': np.exp(params),
        'CI_lower': np.exp(conf[0]),
        'CI_upper': np.exp(conf[1]),
        'p_value': pvalues
    })

    # Check overdispersion
    pearson_chi2 = results.pearson_chi2
    df_resid = results.df_resid
    dispersion = pearson_chi2 / df_resid

    return {
        'model': results,
        'irr_df': irr_df,
        'owner_agg': owner_agg,
        'dispersion': dispersion,
        'pearson_chi2': pearson_chi2,
        'df_resid': df_resid
    }


def format_results_table(
    irr_df: pd.DataFrame,
    owner_agg: pd.DataFrame
) -> pd.DataFrame:
    """
    Format results for publication table.

    Parameters
    ----------
    irr_df : pd.DataFrame
        IRR results from model.
    owner_agg : pd.DataFrame
        Owner-level aggregates.

    Returns
    -------
    pd.DataFrame
        Formatted results table.
    """
    summary = owner_agg.groupby('entity_type').agg(
        n_owners=('owner_name', 'count'),
        total_parcels=('total_parcels', 'sum'),
        mean_parcels=('total_parcels', 'mean'),
        total_sfha=('sfha_parcels', 'sum'),
        mean_sfha=('sfha_parcels', 'mean'),
        pct_any_sfha=('sfha_parcels', lambda x: (x > 0).mean() * 100)
    ).round(3)

    entity_order = ['Individual', 'LLC', 'Corporation', 'Trust', 'Other']
    var_map = {
        'Individual': 'const',
        'LLC': 'is_LLC',
        'Corporation': 'is_Corporation',
        'Trust': 'is_Trust',
        'Other': 'is_Other'
    }

    results_list = []
    for entity in entity_order:
        if entity not in summary.index:
            continue

        row = {
            'entity_type': entity,
            'n_owners': int(summary.loc[entity, 'n_owners']),
            'mean_sfha_parcels': summary.loc[entity, 'mean_sfha']
        }

        if entity == 'Individual':
            row['IRR'] = 1.0
            row['CI_lower'] = np.nan
            row['CI_upper'] = np.nan
            row['p_value'] = np.nan
        else:
            var = var_map[entity]
            if var in irr_df.index:
                row['IRR'] = irr_df.loc[var, 'IRR']
                row['CI_lower'] = irr_df.loc[var, 'CI_lower']
                row['CI_upper'] = irr_df.loc[var, 'CI_upper']
                row['p_value'] = irr_df.loc[var, 'p_value']

        results_list.append(row)

    return pd.DataFrame(results_list)


def main():
    parser = argparse.ArgumentParser(description='Owner-level SFHA exposure model')
    parser.add_argument('--classification', type=Path,
                        default=DATA_DIR / 'parcels_with_classification.csv',
                        help='Path to owner classification CSV')
    parser.add_argument('--regression', type=Path,
                        default=DATA_DIR / 'sfr_regression_data.csv',
                        help='Path to SFR regression data CSV')
    parser.add_argument('--output', type=Path,
                        default=DATA_DIR / 'owner_level_sfha_results.csv',
                        help='Output CSV path')
    args = parser.parse_args()

    # Load and merge data
    merged = load_and_merge_data(args.classification, args.regression)

    # Aggregate to owner level
    owner_agg = aggregate_to_owner_level(merged)

    # Summary statistics
    print("\n=== Owner-Level Summary Statistics ===")
    summary = owner_agg.groupby('entity_type').agg(
        n_owners=('owner_name', 'count'),
        total_parcels=('total_parcels', 'sum'),
        mean_parcels=('total_parcels', 'mean'),
        total_sfha=('sfha_parcels', 'sum'),
        mean_sfha=('sfha_parcels', 'mean'),
        pct_any_sfha=('sfha_parcels', lambda x: (x > 0).mean() * 100)
    ).round(3)
    print(summary.to_string())

    # Fit model
    print("\n=== Running Owner-Level Poisson Model ===")
    model_results = fit_poisson_model(owner_agg)

    print("\n=== Poisson Model Results ===")
    print(model_results['model'].summary())

    print("\n=== Incidence Rate Ratios (IRR) ===")
    print(model_results['irr_df'].round(4).to_string())

    # Overdispersion check
    print("\n=== Overdispersion Check ===")
    print(f"Pearson chi-squared: {model_results['pearson_chi2']:.2f}")
    print(f"Residual DF: {model_results['df_resid']}")
    print(f"Dispersion parameter: {model_results['dispersion']:.3f}")

    if model_results['dispersion'] > 1.5:
        print("\nSubstantial overdispersion detected. Consider Negative Binomial model.")

    # Format and save results
    results_df = format_results_table(model_results['irr_df'], owner_agg)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    results_df.to_csv(args.output, index=False)
    print(f"\nResults saved to: {args.output}")

    # Print formatted table
    print("\n=== TABLE OUTPUT ===")
    print("Owner-level SFHA intensity model (Poisson with offset)")
    print("Reference category: Individual")
    print("-" * 80)
    print(f"\n| Entity type | N owners | Mean SFHA parcels | IRR [95% CI] | p-value |")
    print(f"|-------------|----------|-------------------|--------------|---------|")

    for _, row in results_df.iterrows():
        if row['entity_type'] == 'Individual':
            print(f"| {row['entity_type']} | {row['n_owners']:,} | {row['mean_sfha_parcels']:.3f} | 1.000 (ref) | - |")
        else:
            pval_str = '<0.001' if row['p_value'] < 0.001 else f"{row['p_value']:.3f}"
            print(f"| {row['entity_type']} | {row['n_owners']:,} | {row['mean_sfha_parcels']:.3f} | "
                  f"{row['IRR']:.3f} [{row['CI_lower']:.3f}-{row['CI_upper']:.3f}] | {pval_str} |")


if __name__ == '__main__':
    main()
