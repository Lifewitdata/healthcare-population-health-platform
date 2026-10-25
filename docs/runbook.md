# Runbook

## Local setup

Use Python 3.11 or newer in a virtual environment. From the repository root:

```bash
python -m venv .venv
# Windows PowerShell: .venv\Scripts\Activate.ps1
# macOS/Linux: source .venv/bin/activate
python -m pip install -e ".[test]"
python -m pytest -q
healthcare build --members 25000
python agent/investigator.py
python -m streamlit run dashboard/app.py
```

The generation seed is 42. Generated raw data, processed data, DuckDB and reports live under runtime/ and are gitignored. `--root` selects another runtime directory. Set HEALTHCARE_RUNTIME for the dashboard when using a non-default directory.

`healthcare build --reuse-raw` reprocesses the existing extracts and runs incremental claim handling. Do not shrink or replace the population during an incremental run. `healthcare build --members 100` regenerates a small dataset and full-refreshes the models. Do not run two builds against the same runtime directory simultaneously.

## Snowflake

1. Review and explicitly authorise warehouse/bootstrap.sql; execute it in Snowflake.
2. Copy the non-secret variable names from .env.example into your shell. This application does not automatically load .env. Set your account and username; externalbrowser authentication is the default. Do not commit secrets.
3. Run `healthcare build --target snowflake --members 25000` from your local computer. It generates data, authenticates using your selected method, uploads validated CSVs with PUT/COPY, and runs dbt build against Snowflake.
4. Review ANALYTICS_REPORTING and dbt/target/run_results.json. The dashboard currently reads the local warehouse; use the local build for its current data source. A Snowflake dashboard connection is a future extension.
5. When idle the new warehouse suspends after 60 seconds. Compute and storage still incur provider charges according to your account.

SQL bootstrap is supplied but no Snowflake execution is implied by local results. Table refreshes are scoped to the dedicated project database.

### Native username/password login (PowerShell)

For a native Snowflake login, select password authentication before building:

```powershell
$env:SNOWFLAKE_AUTHENTICATOR = "snowflake"
healthcare build --target snowflake --members 25000
```

Type your password at the hidden prompt in the terminal. It is temporarily passed to the loader and dbt through the process environment and removed afterward, including on failure. The application does not write it to files; dbt uses its secret environment-variable convention for log masking. Never paste passwords into chat or commit them. If your account requires MFA, follow its authentication policy; this setting does not bypass MFA. For unattended runs, supply DBT_ENV_SECRET_SNOWFLAKE_PASSWORD through your secret manager.

## Agent

`python agent/investigator.py` writes a deterministic reference report. For a live run, set OPENAI_API_KEY and OPENAI_MODEL and run `python agent/investigator.py --live`. The live agent may use up to six model turns; provider usage can incur charges. It collects evidence with allow-listed read-only tools. It does not repair data or claim any compliance status.

## Orchestration and recovery

`python orchestration/daily_pipeline.py` runs one local Prefect batch using existing raw files. Prefect may launch a local temporary server. Configure an explicit deployment if scheduling is desired. Retries are bounded at two; data publication stops when quarantine exceeds 2% or dbt checks fail. Review runtime/clean/quality.json and source files, fix upstream data, then rerun with --reuse-raw. The sample intentionally contains four rejected claim rows and one exact duplicate.

A failed dbt build can leave built tables behind; consumers should use the last approved extract. Multi-table atomic release, production alert delivery, account authentication and secret rotation are outside this portfolio implementation.
