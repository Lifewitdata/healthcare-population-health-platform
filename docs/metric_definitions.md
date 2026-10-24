# Metric contracts

| Metric | Grain and calculation | Boundary |
|---|---|---|
| PMPM | Month × member region; latest medical net paid + pharmacy paid / eligible member-months | Includes only costs in covered months; reconciliation fails if any generated cost falls outside coverage. No premiums or incurred-but-not-reported estimate. |
| Utilisation | Month; encounter admissions / eligible member-months × 1,000 | Admission events, not claim lines. Annualised version multiplies by 12. |
| 30-day readmission proxy | Discharge year; next inpatient admission 1–30 days after discharge / eligible index discharges | Index discharge must have 30-day data maturity and covered follow-up month. No planned-admission, transfer, death, or clinical exclusions; overlapping encounters can suppress a next-event match. Not a validated quality measure. |
| Annual HbA1c testing gap | Member-year; diabetes code in that year and 12 eligible months, without a 4548-4 lab in that year | Adults only in generated population. Same-year retrospective cohort; not prospective outreach eligibility or HEDIS. |
| High cost | Whole-period paid cost; deterministic ranked deciles | Retrospective segmentation; no prediction, causal attribution or risk adjustment. |
| Illustrative risk tier | Age at 2024 ≥65 or at least two distinct selected condition codes | Teaching rule, not validated clinical or actuarial risk. |
| Savings scenarios | Top cost decile spend × 2%, 5%, 10%, minus $240 per targeted member | $240 covers the entire two-year illustration. Assumed reductions; not achieved savings or evidence of programme effectiveness. |

Claim rows are versioned net amounts, not additive adjustments. Latest version replaces earlier versions; exact duplicates are removed first. Negative net amounts are quarantined under this project's source contract. Real claim systems may require signed reversals and different handling.

The eligible population fluctuates across months. Never average regional PMPM values without member-month weights. Dashboard totals recompute sum(cost)/sum(member-months).
