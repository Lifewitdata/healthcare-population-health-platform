# Architecture and deployment status

Separate synthetic EHR, payer claims, pharmacy, lab and eligibility extracts enter a Python/Polars batch pipeline. Exact system-scoped identity mappings link records; there is no probabilistic person matching. Invalid rows are quarantined and reconciliation counts must balance. FHIR NDJSON carries Patient and Observation resources; the parser checks identity and lab-value agreement with extracts. FHIR is a supported subset, not a full validation engine or HL7 v2 interface.

Validated CSV snapshots are loaded into RAW using DuckDB locally or Snowflake PUT/COPY via an authenticated local connector. dbt builds staging, core and reporting layers. Claims use version-aware incremental delete/insert; other models rebuild. New claim IDs load even if their update date is older than the warehouse maximum. Same-version corrections and hard deletes require a source contract change/full refresh. A fresh generated dataset always triggers a full refresh.

The physical model combines dimensions and facts with normalised geography and provider organisation dimensions: encounters → providers → organisations → geography. Member geography is a separate join path. There is no Data Vault, CDC, streaming service, or production scheduler enabled.

Prefect wraps the batch with retries. The local flow requires an existing raw extract directory. A deployment schedule must be configured explicitly; importing the file does not schedule or run jobs.

The optional OpenAI agent selects read-only tools to investigate aggregate validation incidents and propose reviewed actions. It has no arbitrary SQL, file-write, or repair tool. Offline reports are explicitly deterministic reference outputs, not agent runs. No LLM endpoint has been executed unless separate live evidence says so.

Snowflake setup is supplied in warehouse/bootstrap.sql. Provisioning and the Snowflake pipeline require a separate authorised execution. Local dbt tests do not prove Snowflake execution. The Snowflake loader publishes tables sequentially after all copies finish; batch-wide atomic publication is a documented production gap.
