# Executive summary: calculation and refresh notes

The client-facing [one-page brief](executive_summary.md) uses three charts from the dashboard's **Executive summary** tab. That tab and the export command call the same `healthcare.executive` functions; the SVG files are identical, not separately recreated illustrations. All regions are included regardless of the Cost overview filter.

## Definitions

- **Cost concentration:** rank all members by full-period medical plus pharmacy paid cost, descending, with member ID breaking ties. Select `ceil(member_count × 0.05)` members. Divide their cost by all members' cost. The default 25,000-member build selects exactly 1,250 members. A different population size may require rounding the 5% count upward.
- **Diabetes testing:** use the latest year in `rpt_care_gaps` (2025 in this snapshot). Count member-year records and sum `testing_gap`. Eligibility requires a same-year diabetes diagnosis and 12 covered months. Missing annual HbA1c testing is a retrospective record-based proxy, not a current clinical determination. The generated population is adult-only.
- **Hospital returns:** select that same year from `rpt_readmissions`. Divide qualifying 30-day return events by eligible index discharges. The unit is discharges, not unique members. Do not interpret the count as a patient outreach list.
- These groups can overlap. Counts must not be added together. No ER-visit flag exists in the source, so no diabetes-plus-ER claim is made.

See [metric definitions](metric_definitions.md) for follow-up coverage and clinical limitations. The saved [aggregate values](evidence/executive_summary.json) contain no member identifiers.

## Refresh

From the repository root after installing the project:

```bash
healthcare build --members 25000
python -m healthcare.executive --database runtime/healthcare.duckdb --out docs
python -m streamlit run dashboard/app.py
```

The command refreshes the Markdown, all three SVG charts and aggregate JSON together. In the dashboard, each chart also has a download button. The summary tab is population-wide and uses the latest available annual care-gap year; it is independent of the regional filter. The checked-in snapshot uses the default seed 42 and 2024–2025 reporting period. No individual outreach list is published.
