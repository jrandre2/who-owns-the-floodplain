# Identification Diagnostics

*Proposed addition to Section 3 (Methods) or new Section 3.9*

---

## 3.9 Identification Diagnostics

We conduct several formal tests to validate the boundary RD-in-panel design.

### 3.9.1 McCrary Density Test

To test for manipulation or sorting at the SFHA boundary, we implement the McCrary (2008) density discontinuity test. This procedure examines whether the density of parcel centroids changes discontinuously at the boundary, which would indicate that properties systematically sort across the regulatory line.

Figure X presents the density of parcels as a function of signed distance to the SFHA boundary. We find a statistically significant discontinuity (z = 7.78, p < 0.001), with higher parcel density on the inside (negative distance) than the outside. This pattern likely reflects the historical relationship between flood hazard mapping and urban development: SFHA zones follow natural floodplain topography, and development has been denser in low-lying riverine corridors. Importantly, this density discontinuity reflects *pre-existing* development patterns, not strategic sorting in response to the 2019 flood. The SFHA boundary has been stable over the study period, and parcel creation/destruction is rare at the margin.

*[Insert Figure: fig_mccrary_sfha.png]*

### 3.9.2 Parallel Trends Validation

Our difference-in-differences design requires that inside and outside parcels would have followed parallel outcome trajectories absent the flood. Figure X displays event-study coefficients (β_τ) for the inside × time interactions, with 95% confidence intervals. The pre-event coefficients (τ < 0) should be statistically indistinguishable from zero if the parallel trends assumption holds.

We conduct a formal joint F-test of the null hypothesis that all pre-event coefficients equal zero. For the SFHA boundary at ±300m, we reject this null (F = 3.33, p < 0.001), indicating some pre-existing differential trends. The average pre-period inside-outside gap is approximately 0.00039 per parcel-month, compared to the post-period DiD of -0.00089. This suggests that while there is a pre-existing trend, the post-flood divergence exceeds what would be predicted by extrapolating pre-trends alone.

At the realized inundation boundary, the parallel trends assumption is more strongly supported (F = 1.50, p = 0.15), though sample sizes are smaller.

*[Insert Figure: fig_event_study_sfha_300m.png]*

### 3.9.3 Bandwidth Sensitivity

We estimate the main DiD specification across multiple caliper widths (100m to 500m) to assess sensitivity to bandwidth choice. Figure X shows that the point estimate is stable across bandwidths from 150m to 400m, ranging from -0.00066 to -0.00089. Statistical significance is achieved at calipers of 200m and above. This stability suggests that our results are not artifacts of a particular bandwidth choice.

*[Insert Figure: fig_bandwidth_sfha.png]*

### 3.9.4 SUTVA and Spillover Robustness

A potential threat to identification arises from the ring model results (Section 4.3), which document increased sales activity in the 0-250m ring just outside the SFHA post-flood (rate ratio ≈ 1.44). If demand reroutes from inside to outside the boundary, our "control" parcels are themselves treated by spillover demand, violating the stable unit treatment value assumption (SUTVA) and likely attenuating our estimates.

To assess the magnitude of this concern, we estimate a "donut" specification that excludes parcels within 100m outside the SFHA boundary. This specification yields a DiD estimate of -0.00097, approximately 9% larger in magnitude than the baseline estimate of -0.00089. This pattern is consistent with spillover attenuation: excluding the zone where demand reroutes produces larger (more negative) estimates of the inside effect.

We interpret our baseline estimates as likely lower bounds on the true effect of the flood on inside transaction rates. The ring models should be understood not merely as evidence of spatial substitution, but as documentation of a specific SUTVA violation that attenuates our primary estimates.

*[Insert Table: Donut RD results]*

---

## Discussion of Identification Threats

*(Proposed addition to Section 5.5 Limitations)*

### SUTVA Violation

Our ring models document demand substitution to "near-but-dry" parcels just outside the SFHA (rate ratios ≈ 1.44 in 0-250m, 1.31 in 250-300m). This pattern, while substantively interesting as evidence of spatial sorting, implies that our control group is partially treated by redirected demand. Standard SUTVA requires that treatment of one unit does not affect outcomes for other units; our setting violates this condition.

The direction of bias is clear: if demand flows from inside (treatment) to outside (control), the control group experiences *increased* sales activity, shrinking the inside-outside gap and attenuating our DiD estimate toward zero. Our donut specifications confirm this: excluding the spillover zone produces larger estimated effects (-0.00097 vs. -0.00089, a 9% increase).

We therefore interpret our baseline estimates as lower bounds on the true freeze effect inside the SFHA. The market response to flood risk salience may be larger than what can be identified from boundary contrasts alone.

### Exclusion Restriction

The SFHA boundary packages multiple treatments that may independently affect market outcomes:

1. **Flood risk**: Physical exposure to riverine flooding
2. **Insurance mandate**: Mandatory flood insurance for federally-backed mortgages
3. **Disclosure requirements**: Seller disclosure of SFHA status in many states
4. **Lender overlays**: Elevated underwriting scrutiny beyond regulatory minima

Our design estimates the joint effect of crossing the SFHA boundary, not the isolated effect of flood risk salience. This is appropriate for policy purposes—the boundary is the relevant margin for many administrative decisions—but readers should interpret effects as "boundary effects" rather than "risk capitalization" in the pure sense. Separating these channels would require variation in insurance requirements or disclosure rules that is not present in our single-county setting.

### Pre-Trends at the SFHA Boundary

The formal pre-trends test rejects the null of zero pre-event coefficients for the SFHA boundary (p < 0.001), raising questions about the parallel trends assumption. We note three considerations:

First, the pre-period differential (≈0.00039) is less than half the magnitude of the estimated post-period DiD (≈0.00089), suggesting that the flood induced a change beyond what would be predicted by pre-existing trends.

Second, the inundation boundary—which tracks the realized flood footprint rather than the regulatory map—passes the pre-trends test (p = 0.15). Results at this boundary are directionally similar but less precisely estimated given smaller sample sizes.

Third, pre-existing differentials may reflect other time-varying factors that correlate with but are distinct from the flood event. We cannot rule out that unobserved confounders explain part of the estimated effect.

---

## References for New Methods

McCrary, J. (2008). Manipulation of the running variable in the regression discontinuity design: A density test. *Journal of Econometrics*, 142(2), 698-714.
