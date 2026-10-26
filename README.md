# Healthcare Population Health & Cost Analytics Platform

A reproducible portfolio pipeline joining synthetic eligibility, EHR encounters, medical claims, pharmacy fills and lab results. Python/Polars transforms source extracts; dbt builds cost and population-health reports; Streamlit makes them reviewable. Snowflake deployment code and a bounded tool-calling investigation agent are included.

**For business readers:** [Read the one-page care management summary](docs/executive_summary.md) — three findings with dashboard charts, recommended actions and clear limitations.

**Status:** local implementation validated on 25,000 synthetic members (24 models, 51 dbt tests); see docs/validation.md for measured results. Snowflake provisioning requires approval. No live LLM run is claimed.

## Run locally

```bash
python -m pip install -e ".[test]"
healthcare build --members 25000
python agent/investigator.py
python -m streamlit run dashboard/app.py
```

Use a Python virtual environment; Windows instructions and Snowflake deployment steps are in [the runbook](docs/runbook.md).

## What is implemented

- Deterministic synthetic population with 25,000 members and 24 months of coverage history.
- Multiple linked source extracts, system-specific IDs, claim revisions, duplicates and invalid records.
- Polars cleaning, exact identity mapping, quarantine and row-count reconciliation.
- Selected FHIR R4 Patient/Observation parsing and cross-source identity/value checks.
- DuckDB local execution plus an authenticated Snowflake PUT/COPY loader and dbt target.
- Dimensional modelling, including provider → organisation → geography normalisation.
- Version-aware incremental claims, cost reconciliation and business-rule tests.
- PMPM, utilisation, retrospective care-gap and readmission proxies, high-cost segmentation and savings scenarios.
- Streamlit report with export, Prefect batch retries and GitHub Actions validation workflow.
- Optional OpenAI tool-calling agent that investigates aggregate quality failures; deterministic offline reference mode is clearly labelled.

## Honest scope

Synthetic multi-source simulation, not integration with live EHR systems. No HL7 v2 interface, streaming, Data Vault, validated risk adjustment, certified HEDIS, demonstrated cost reduction or HIPAA certification. Snowflake SQL is not considered deployed until verified in the account. Live agent execution requires a configured model and API key. The dashboard currently reads the local warehouse, not Snowflake.

## Documentation

- [Architecture](docs/architecture.md)
- [Data dictionary and coding scope](docs/data_dictionary.md)
- [Metric definitions](docs/metric_definitions.md)
- [Privacy boundary](docs/privacy_controls.md)
- [Runbook](docs/runbook.md)
- [Validation evidence](docs/validation.md)

Source references: [FHIR R4 Observation](https://hl7.org/fhir/R4/observation.html), [dbt incremental models](https://docs.getdbt.com/docs/build/incremental-models), [Snowflake COPY INTO](https://docs.snowflake.com/en/sql-reference/sql/copy-into-table). These inform implementation choices, not a conformance certification.
