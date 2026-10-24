# Validation evidence

Validated on 25 October 2026 (India time).

- Full synthetic build: 25,000 members, 474,901 eligible member-months, 137,394 encounters, 274,788 accepted claim lines, 166,595 pharmacy fills and 8,494 lab results.
- Claims: 283,034 input rows = 274,788 accepted + 8,241 superseded versions + 1 exact duplicate + 4 quarantined errors.
- 24 dbt models and 51 data tests completed successfully on the full dataset; the unchanged incremental rerun also passed.
- Python tests cover injected defects, row conservation, FHIR matching, claim version selection, repeatable outputs, ambiguous identities and agent boundaries.
- Streamlit AppTest: all tabs executed without exceptions; region selection and an empty selection passed.
- Synthetic report total paid: $206,631,578 (rounded), PMPM $435.10. Figures are portfolio outputs, not real programme results.
- Offline agent reference report generated. Live LLM execution is pending a configured provider.
- Snowflake sign-in verified; setup worksheet prepared. Provisioning and warehouse execution remain pending explicit approval.

Evidence files are in [evidence](evidence/); the tested package versions are in [requirements-tested.txt](../requirements-tested.txt). CI is configured; local results do not imply that GitHub Actions has run.
