#!/usr/bin/env python3
"""
Module: 03_concentration_analysis.py
Purpose: Ownership concentration analysis using Lorenz curves and Gini coefficients.

This module computes distributional measures of property ownership concentration
to understand how flood-exposed properties are distributed across owner types.

Key outputs:
- Lorenz curves by owner type
- Gini coefficients for ownership concentration
- Concentration ratios (CR4, CR10)

Input Files
-----------
- data/owners_labeled.parquet (or parcels_with_classification.csv)

Output Files
------------
- data/concentration_metrics.csv
- figures/fig_lorenz_curves.png
"""
from __future__ import annotations
from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import argparse

DATA_DIR = Path('data')
FIG_DIR = Path('figures')


def compute_gini(values: np.ndarray) -> float:
    """
    Compute Gini coefficient for a distribution.

    Parameters
    ----------
    values : np.ndarray
        Array of non-negative values (e.g., parcel counts per owner).

    Returns
    -------
    float
        Gini coefficient (0 = perfect equality, 1 = perfect inequality).
    """
    values = np.array(values, dtype=float)
    values = values[~np.isnan(values)]

    if len(values) == 0 or np.sum(values) == 0:
        return np.nan

    # Sort values
    sorted_vals = np.sort(values)
    n = len(sorted_vals)

    # Compute Gini using the formula:
    # G = (2 * sum(i * x_i)) / (n * sum(x_i)) - (n + 1) / n
    cumsum = np.cumsum(sorted_vals)
    gini = (2 * np.sum((np.arange(1, n + 1) * sorted_vals))) / (n * cumsum[-1]) - (n + 1) / n

    return gini


def compute_lorenz_curve(values: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """
    Compute Lorenz curve coordinates.

    Parameters
    ----------
    values : np.ndarray
        Array of non-negative values.

    Returns
    -------
    tuple[np.ndarray, np.ndarray]
        (x, y) coordinates for Lorenz curve where:
        - x = cumulative share of population
        - y = cumulative share of total value
    """
    values = np.array(values, dtype=float)
    values = values[~np.isnan(values)]

    if len(values) == 0 or np.sum(values) == 0:
        return np.array([0, 1]), np.array([0, 1])

    # Sort and compute cumulative shares
    sorted_vals = np.sort(values)
    n = len(sorted_vals)

    # Population share (x-axis)
    x = np.arange(0, n + 1) / n

    # Value share (y-axis)
    cumsum = np.concatenate([[0], np.cumsum(sorted_vals)])
    y = cumsum / cumsum[-1]

    return x, y


def compute_concentration_ratios(values: np.ndarray, top_n: list[int] = [4, 10, 20]) -> dict:
    """
    Compute concentration ratios (share held by top N owners).

    Parameters
    ----------
    values : np.ndarray
        Array of values (e.g., parcel counts per owner).
    top_n : list[int]
        List of top N values to compute ratios for.

    Returns
    -------
    dict
        Dictionary with CR{N} keys and concentration ratio values.
    """
    values = np.array(values, dtype=float)
    values = values[~np.isnan(values)]

    if len(values) == 0 or np.sum(values) == 0:
        return {f'CR{n}': np.nan for n in top_n}

    sorted_vals = np.sort(values)[::-1]  # Descending
    total = np.sum(sorted_vals)

    ratios = {}
    for n in top_n:
        if n <= len(sorted_vals):
            ratios[f'CR{n}'] = np.sum(sorted_vals[:n]) / total
        else:
            ratios[f'CR{n}'] = 1.0  # All owners if fewer than N

    return ratios


def analyze_ownership_concentration(
    df: pd.DataFrame,
    owner_col: str = 'owner_key',
    type_col: str = 'owner_form',
    sfha_col: str = 'in_sfha'
) -> pd.DataFrame:
    """
    Analyze ownership concentration by entity type.

    Parameters
    ----------
    df : pd.DataFrame
        Parcel-level data with owner and SFHA information.
    owner_col : str
        Column name for owner identifier.
    type_col : str
        Column name for owner type.
    sfha_col : str
        Column name for SFHA status (binary).

    Returns
    -------
    pd.DataFrame
        Concentration metrics by owner type.
    """
    results = []

    # Overall concentration
    if owner_col in df.columns:
        owner_counts = df.groupby(owner_col).size()

        overall = {
            'owner_type': 'All',
            'n_owners': len(owner_counts),
            'n_parcels': len(df),
            'gini': compute_gini(owner_counts.values),
            **compute_concentration_ratios(owner_counts.values)
        }
        results.append(overall)

    # By owner type
    if type_col in df.columns and owner_col in df.columns:
        for otype in df[type_col].dropna().unique():
            subset = df[df[type_col] == otype]
            owner_counts = subset.groupby(owner_col).size()

            metrics = {
                'owner_type': otype,
                'n_owners': len(owner_counts),
                'n_parcels': len(subset),
                'gini': compute_gini(owner_counts.values),
                **compute_concentration_ratios(owner_counts.values)
            }
            results.append(metrics)

    # SFHA-specific concentration (if available)
    if sfha_col in df.columns and owner_col in df.columns:
        sfha_df = df[df[sfha_col] == 1]
        if len(sfha_df) > 0:
            owner_counts = sfha_df.groupby(owner_col).size()

            sfha_metrics = {
                'owner_type': 'SFHA_only',
                'n_owners': len(owner_counts),
                'n_parcels': len(sfha_df),
                'gini': compute_gini(owner_counts.values),
                **compute_concentration_ratios(owner_counts.values)
            }
            results.append(sfha_metrics)

    return pd.DataFrame(results)


def plot_lorenz_curves(
    df: pd.DataFrame,
    owner_col: str = 'owner_key',
    type_col: str = 'owner_form',
    output_path: Path = FIG_DIR / 'fig_lorenz_curves.png'
):
    """
    Plot Lorenz curves by owner type.

    Parameters
    ----------
    df : pd.DataFrame
        Parcel-level data.
    owner_col : str
        Column name for owner identifier.
    type_col : str
        Column name for owner type.
    output_path : Path
        Output path for figure.
    """
    fig, ax = plt.subplots(figsize=(8, 6))

    # Plot line of equality
    ax.plot([0, 1], [0, 1], 'k--', linewidth=1, label='Perfect equality')

    colors = {
        'Individual': 'steelblue',
        'LLC': 'coral',
        'Corporation': 'forestgreen',
        'Trust': 'purple',
        'Other': 'gray',
        'All': 'black'
    }

    # Overall Lorenz curve
    if owner_col in df.columns:
        owner_counts = df.groupby(owner_col).size().values
        x, y = compute_lorenz_curve(owner_counts)
        gini = compute_gini(owner_counts)
        ax.plot(x, y, color='black', linewidth=2.5,
                label=f'All owners (Gini={gini:.3f})')

    # By owner type
    if type_col in df.columns and owner_col in df.columns:
        for otype in sorted(df[type_col].dropna().unique()):
            subset = df[df[type_col] == otype]
            if len(subset) < 10:
                continue

            owner_counts = subset.groupby(owner_col).size().values
            x, y = compute_lorenz_curve(owner_counts)
            gini = compute_gini(owner_counts)

            color = colors.get(otype, 'gray')
            ax.plot(x, y, color=color, linewidth=1.5,
                    label=f'{otype} (Gini={gini:.3f})')

    ax.set_xlabel('Cumulative Share of Owners', fontsize=11)
    ax.set_ylabel('Cumulative Share of Parcels', fontsize=11)
    ax.set_title('Ownership Concentration: Lorenz Curves by Entity Type', fontsize=12)
    ax.legend(loc='lower right', fontsize=9)
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f'Wrote {output_path}')


def main():
    parser = argparse.ArgumentParser(description='Ownership concentration analysis')
    parser.add_argument('--input', type=Path,
                        default=DATA_DIR / 'owners_labeled.parquet',
                        help='Input parquet or CSV with owner data')
    parser.add_argument('--output', type=Path,
                        default=DATA_DIR / 'concentration_metrics.csv',
                        help='Output CSV for concentration metrics')
    parser.add_argument('--figure', type=Path,
                        default=FIG_DIR / 'fig_lorenz_curves.png',
                        help='Output path for Lorenz curve figure')
    args = parser.parse_args()

    # Load data
    if args.input.suffix == '.parquet':
        df = pd.read_parquet(args.input)
    else:
        df = pd.read_csv(args.input)

    print(f"Loaded {len(df):,} records")

    # Detect column names
    owner_col = 'owner_key' if 'owner_key' in df.columns else 'owner_name'
    type_col = 'owner_form' if 'owner_form' in df.columns else 'owner_form_snapshot'
    sfha_col = 'in_sfha' if 'in_sfha' in df.columns else None

    print(f"Using columns: owner={owner_col}, type={type_col}, sfha={sfha_col}")

    # Compute concentration metrics
    print("\n=== Ownership Concentration Analysis ===")
    metrics = analyze_ownership_concentration(df, owner_col, type_col, sfha_col)
    print(metrics.to_string(index=False))

    # Save metrics
    args.output.parent.mkdir(parents=True, exist_ok=True)
    metrics.to_csv(args.output, index=False)
    print(f"\nWrote {args.output}")

    # Plot Lorenz curves
    plot_lorenz_curves(df, owner_col, type_col, args.figure)


if __name__ == '__main__':
    main()
