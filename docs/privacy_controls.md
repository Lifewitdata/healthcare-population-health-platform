# Privacy boundary

No real patient data is collected or included. This project does not demonstrate HIPAA certification, a BAA, a legal assessment, or operating a HIPAA-compliant service.

The optional SQL examples show an aggregate-only reader role and a member-ID masking policy. They are not applied automatically. Masking requires an eligible Snowflake edition. A production review must cover least privilege, row access, retention, encryption, audit review, authentication, vendor agreements and incident response.

The investigation agent is passed only source-level counts and predefined rule names. Its tools cannot query patient rows or write to a warehouse. API keys belong in private shell variables or a secret manager. Do not commit a .env file, account credentials, raw production records or agent traces containing sensitive data.

The Streamlit dashboard reads local synthetic reports. It is not deployed publicly, has no production authentication, and must not be used to expose real clinical data. The repository is public and includes only code, synthetic samples and synthetic aggregate evidence.
