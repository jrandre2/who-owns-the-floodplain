# Who Owns the Floodplain?

**Organizational Form, Portfolio Scale, and Regulatory Flood Exposure in Douglas County, Nebraska**

## Manuscript Status

| Field | Value |
|-------|-------|
| Journal | Environment and Planning B: Urban Analytics and City Science |
| Manuscript ID | EPB-2025-0878 |
| Status | Major Revisions |
| Revision Deadline | March 16, 2026 |

## Abstract

This study examines how property ownership structure relates to regulatory flood exposure in Douglas County, Nebraska. Using a fine-tuned BERT transformer model to classify owner organizational form (Individual, LLC, Corporation, Trust, Government/Nonprofit) from assessor records, we analyze 184,333 single-family residential parcels to understand who bears flood risk.

## Key Findings

- Single-parcel LLCs have 67% higher risk of SFHA exposure than individual owners (RR=1.67, 95% CI: 1.31-2.13)
- Multi-parcel corporations show 62% higher exposure risk
- Evidence of "liability siloing": single-parcel LLCs more exposed than multi-parcel LLCs
- Significant concentration of flood-exposed properties among a small number of corporate and governmental owners

## Directory Structure

```
who-owns-the-floodplain/
├── manuscript/      # Main manuscript documents
├── revision/        # Reviewer responses and revised materials
├── figures/         # Supplementary figures (LISA maps, forest plots)
├── supplementary/   # Appendices and supplementary material
├── data/            # Processed data for replication
├── code/            # Analysis scripts
├── docs/            # Documentation and methodology notes
└── archive/         # Historical drafts
```

## Methodology

- Modified Poisson regression with neighborhood fixed effects
- BERT transformer classifier for ownership structure (97.8% accuracy)
- FEMA Special Flood Hazard Areas (SFHAs) as primary exposure metric
- Lorenz curves and Gini coefficients for concentration analysis

## Citation

Andrews, J. (2025). Who Owns the Floodplain? Organizational Form, Portfolio Scale, and Regulatory Flood Exposure in Douglas County, Nebraska. *Environment and Planning B: Urban Analytics and City Science* (under review).
