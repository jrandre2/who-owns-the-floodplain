# Who Owns the Floodplain?

**Replication Data and Code for "Organizational Form, Portfolio Scale, and Regulatory Flood Exposure in Douglas County, Nebraska"**

Published in *Environment and Planning B: Urban Analytics and City Science*

## Overview

This repository contains the data and analysis code for our study examining how property ownership structure relates to regulatory flood exposure in Douglas County, Nebraska. Using a fine-tuned BERT transformer model to classify owner organizational form from assessor records, we analyze 184,333 single-family residential parcels.

## Key Findings

- Single-parcel LLCs have 67% higher risk of SFHA exposure than individual owners (RR=1.67, 95% CI: 1.31-2.13)
- Multi-parcel corporations show 62% higher exposure risk
- Evidence of "liability siloing": single-parcel LLCs more exposed than multi-parcel LLCs
- Significant concentration of flood-exposed properties among a small number of corporate and governmental owners

## Repository Structure

```
who-owns-the-floodplain/
├── data/       # Processed datasets for replication
├── code/       # Analysis scripts
├── figures/    # Output figures
└── docs/       # Methodology documentation
```

## Methodology

- Modified Poisson regression with neighborhood fixed effects
- BERT transformer classifier for ownership structure (97.8% accuracy)
- FEMA Special Flood Hazard Areas (SFHAs) as primary exposure metric
- Lorenz curves and Gini coefficients for concentration analysis

## Data

Details on data sources and processing steps are provided in `docs/`.

## Citation

Andrews, J. (2025). Who Owns the Floodplain? Organizational Form, Portfolio Scale, and Regulatory Flood Exposure in Douglas County, Nebraska. *Environment and Planning B: Urban Analytics and City Science*.

## License

See LICENSE file for terms of use.
