# Who Owns the Floodplain?

**Replication code and figures for "Organizational Form, Portfolio Scale, and Regulatory Flood Exposure in Douglas County, Nebraska"**

Published in *Environment and Planning B: Urban Analytics and City Science* (Andrews, 2025).

## What This Project Studies

This study examines how property ownership structure relates to regulatory flood exposure in Douglas County, Nebraska. Using a fine-tuned BERT transformer model to classify owner organizational form from county assessor records, we analyze 184,333 single-family residential parcels and their relationship to FEMA Special Flood Hazard Areas (SFHAs).

**Key findings:**
- Single-parcel LLCs have 67% higher risk of SFHA exposure than individual owners (RR = 1.67, 95% CI: 1.31–2.13)
- Multi-parcel corporations show 62% higher exposure risk
- Evidence of "liability siloing": single-parcel LLCs are more exposed than multi-parcel LLCs
- Flood-exposed properties are significantly concentrated among a small number of corporate and governmental owners

## No Manuscript File in This Repository

The published article is available via the journal. This repository contains replication code, methodology documentation, and publication figures only.

## Repository Map

```
who-owns-the-floodplain/
├── code/                          # Analysis scripts (run in order)
│   ├── 01_classify_owners.py      # Classify owner organizational form; produces owners_labeled.parquet
│   ├── 02_sfha_exposure_model.py  # Poisson GLM for SFHA exposure; produces owner_level_sfha_results.csv
│   └── 03_concentration_analysis.py  # Lorenz curves and Gini coefficients
├── data/                          # Input data (not tracked; see Data section below)
│   └── .gitkeep
├── figures/                       # Publication-ready figures (PNG and PDF)
│   ├── fig_A1_forest_rr.png       # Forest plot: incidence rate ratios by owner type
│   ├── fig_A5_lorenz_small_multiples.png  # Lorenz curves by owner category
│   ├── fig_A6_small_multiple_maps.png     # Spatial distribution maps
│   ├── fig_B9_classifier_panels.png/.pdf  # BERT classifier performance panels
│   └── entity_LISA_is_*.png       # Local Indicators of Spatial Association by entity type
├── docs/                          # Methodology documentation
│   └── IDENTIFICATION_DIAGNOSTICS.md  # Formal identification tests (McCrary, parallel trends, bandwidth sensitivity)
└── requirements.txt               # Python dependencies
```
## Reproducibility

### Requirements

Python 3.9+ with dependencies from `requirements.txt`:

```bash
pip install -r requirements.txt
```

Core packages: `pandas`, `numpy`, `statsmodels`, `scipy`, `matplotlib`.
Optional spatial analysis: `geopandas`, `libpysal`, `esda` (commented out in requirements.txt).

### Data

Input data files are not tracked in this repository due to size and sensitivity. Place the following files in `data/` before running:

| File | Description |
|------|-------------|
| `data/parcels_with_classification.csv` | Owner classification results from BERT model |
| `data/sfr_regression_data.csv` | Single-family residential parcels with SFHA status |

### Running the Analysis

Execute scripts in order:

```bash
python code/01_classify_owners.py        # Classify owners, compute portfolio metrics
python code/02_sfha_exposure_model.py    # Fit Poisson GLM for SFHA exposure
python code/03_concentration_analysis.py # Compute Lorenz curves and Gini coefficients
```

Each script accepts `--help` for CLI options to override default input/output paths.

### Methods Summary

- **Owner classification**: Fine-tuned BERT transformer on county assessor name strings (97.8% accuracy)
- **Exposure model**: Modified Poisson regression with log(total parcels) offset; individual owners as reference category
- **Concentration analysis**: Lorenz curves and Gini coefficients by owner type; CR4/CR10 concentration ratios
- **Spatial analysis**: Local Indicators of Spatial Association (LISA) by entity type; neighborhood fixed effects

### Identification and Robustness

See `docs/IDENTIFICATION_DIAGNOSTICS.md` for formal identification tests including:
- McCrary (2008) density test at the SFHA boundary
- Parallel trends validation and joint F-tests
- Bandwidth sensitivity analysis (100m–500m calipers)
- SUTVA/spillover robustness via donut specifications

## Citation

Andrews, J. (2025). Who Owns the Floodplain? Organizational Form, Portfolio Scale, and Regulatory Flood Exposure in Douglas County, Nebraska. *Environment and Planning B: Urban Analytics and City Science*.

## License

Code in this repository is released under the MIT License. See LICENSE file if present, or contact the author for reuse terms.
