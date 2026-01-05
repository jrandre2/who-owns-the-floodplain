#!/usr/bin/env python3
"""
Module: 01_classify_owners.py
Purpose: Classify property owner organizational form and compute portfolio metrics.

This module enriches parcel data with owner metadata including:
- Owner type (Individual, LLC, Corporation, Trust, Other/Gov)
- Portfolio scale (single vs. multi-parcel owners)
- Owner-parcel locality indicators

Adapted from the Freeze and Flight project for standalone replication.

Input Files
-----------
- data/parcels_with_classification.csv (owner classification results)
- data/sales_parcel_joined.parquet (optional: sales transactions)

Output Files
------------
- data/owners_labeled.parquet
- data/diagnostics/classify_owners_audit.log
"""
from __future__ import annotations
from pathlib import Path
from datetime import datetime
import pandas as pd
import numpy as np
import argparse

# Default paths (can be overridden via CLI)
DATA_DIR = Path('data')
OUTPUT_DIR = Path('data')
DIAGNOSTICS_DIR = Path('data/diagnostics')


def _log_audit(log_lines: list, message: str):
    """Append message to audit log."""
    log_lines.append(f'{datetime.now().isoformat()} - {message}')
    print(f'  AUDIT: {message}')


def classify_owners(
    classification_path: Path,
    output_path: Path,
    audit_log_path: Path
) -> pd.DataFrame:
    """
    Classify owner organizational form and compute portfolio metrics.

    Parameters
    ----------
    classification_path : Path
        Path to classification CSV with owner metadata.
    output_path : Path
        Path for output parquet file.
    audit_log_path : Path
        Path for audit log file.

    Returns
    -------
    pd.DataFrame
        DataFrame with owner classification and portfolio metrics.
    """
    audit_log = []
    _log_audit(audit_log, 'Starting owner classification')

    if not classification_path.exists():
        raise FileNotFoundError(f'Missing classification CSV at {classification_path}')

    # Read classification data
    head = pd.read_csv(classification_path, nrows=0).columns.tolist()
    use_cols = [c for c in [
        'Parcel_ID', 'parcel_id',
        'predicted_owner_type', 'owner_type',
        'Current_Ow', 'owner_name',
        'OwnerZIP5', 'owner_zip',
        'ParcelZIP5', 'situs_zip', 'Zip', 'Ph_Zip5'
    ] if c in head]

    meta = pd.read_csv(classification_path, usecols=use_cols)
    _log_audit(audit_log, f'Classification metadata: {len(meta):,} rows')

    # Normalize parcel ID column
    if 'Parcel_ID' in meta.columns:
        meta['parcel_id'] = meta['Parcel_ID'].astype(str)
    elif 'parcel_id' in meta.columns:
        meta['parcel_id'] = meta['parcel_id'].astype(str)

    # Owner key for portfolio counting
    owner_col = 'Current_Ow' if 'Current_Ow' in meta.columns else 'owner_name'
    if owner_col in meta.columns:
        meta['owner_key'] = meta[owner_col].astype(str).str.strip()
        empty_keys = (meta['owner_key'] == '') | (meta['owner_key'] == 'nan') | (meta['owner_key'] == 'None')
        _log_audit(audit_log, f'Empty/invalid owner_key: {empty_keys.sum():,}')

    # Owner type
    type_col = 'predicted_owner_type' if 'predicted_owner_type' in meta.columns else 'owner_type'
    if type_col in meta.columns:
        meta.rename(columns={type_col: 'owner_form'}, inplace=True)
    else:
        meta['owner_form'] = 'Unknown'

    # Compute portfolio size
    if 'owner_key' in meta.columns:
        valid_mask = ~((meta['owner_key'] == '') | (meta['owner_key'] == 'nan') | (meta['owner_key'] == 'None'))
        valid_meta = meta.loc[valid_mask, 'owner_key']
        counts = valid_meta.groupby(valid_meta).size().rename('owner_parcel_count')
        meta = meta.merge(counts, on='owner_key', how='left')
        meta['owner_scale'] = meta['owner_parcel_count'].apply(
            lambda x: 'multi' if pd.notna(x) and x > 1 else 'single'
        )
        multi_count = (meta['owner_scale'] == 'multi').sum()
        _log_audit(audit_log, f'Multi-property owners: {multi_count:,}')

    # ZIP code processing for locality
    if 'OwnerZIP5' in meta.columns:
        meta['owner_zip'] = meta['OwnerZIP5']
    elif 'owner_zip' not in meta.columns and 'Ph_Zip5' in meta.columns:
        meta['owner_zip'] = meta['Ph_Zip5']

    if 'ParcelZIP5' in meta.columns:
        meta['situs_zip'] = meta['ParcelZIP5']
    elif 'situs_zip' not in meta.columns and 'Zip' in meta.columns:
        meta['situs_zip'] = meta['Zip']

    # Normalize ZIP codes
    for c in ['owner_zip', 'situs_zip']:
        if c in meta.columns:
            original_non_null = meta[c].notna().sum()
            if pd.api.types.is_numeric_dtype(meta[c]):
                meta[c] = meta[c].fillna(-1).astype(int).astype(str).str.zfill(5)
                meta.loc[meta[c] == '-0001', c] = np.nan
            else:
                meta[c] = meta[c].astype(str).str.extract(r'(\d{5})', expand=False)
            extracted = meta[c].notna().sum()
            _log_audit(audit_log, f'{c}: {extracted:,} valid ZIPs')

    # Compute LocalOwner indicator
    if 'owner_zip' in meta.columns and 'situs_zip' in meta.columns:
        both_valid = meta['owner_zip'].notna() & meta['situs_zip'].notna()
        meta['is_local'] = np.where(
            both_valid,
            (meta['owner_zip'] == meta['situs_zip']).astype(float),
            np.nan
        )
        local_count = (meta['is_local'] == 1).sum()
        nonlocal_count = (meta['is_local'] == 0).sum()
        _log_audit(audit_log, f'Local: {local_count:,}, Non-local: {nonlocal_count:,}')

    # Select output columns
    keep_cols = ['parcel_id']
    for c in ['owner_key', 'owner_form', 'owner_scale', 'owner_parcel_count',
              'owner_zip', 'situs_zip', 'is_local']:
        if c in meta.columns:
            keep_cols.append(c)

    out = meta[keep_cols].copy()

    # Write output
    output_path.parent.mkdir(parents=True, exist_ok=True)
    out.to_parquet(output_path, index=False)
    print(f'Wrote {output_path} ({len(out):,} rows)')

    # Write audit log
    audit_log_path.parent.mkdir(parents=True, exist_ok=True)
    with open(audit_log_path, 'w') as f:
        f.write('\n'.join(audit_log))
    print(f'Wrote audit log to {audit_log_path}')

    return out


def main():
    parser = argparse.ArgumentParser(description='Classify property owner organizational form')
    parser.add_argument('--input', type=Path, default=DATA_DIR / 'parcels_with_classification.csv',
                        help='Input classification CSV')
    parser.add_argument('--output', type=Path, default=OUTPUT_DIR / 'owners_labeled.parquet',
                        help='Output parquet file')
    parser.add_argument('--audit-log', type=Path, default=DIAGNOSTICS_DIR / 'classify_owners_audit.log',
                        help='Audit log file')
    args = parser.parse_args()

    classify_owners(args.input, args.output, args.audit_log)


if __name__ == '__main__':
    main()
