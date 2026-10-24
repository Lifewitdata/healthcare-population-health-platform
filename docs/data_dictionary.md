# Data dictionary

All files are synthetic. Dates cover 2024–2025, with claim update dates extending later for run-out.

| Source | Key / grain | Principal fields |
|---|---|---|
| members | member_id | age_at_2024, geo_id; no names or contact details |
| identity_map | system + source_member_id | canonical member_id; EHR, payer, pharmacy, lab namespaces |
| eligibility | member_id + month | first day of a fully covered month; no partial-month prorating |
| encounters | encounter_id | admit_date, discharge_date, encounter_type, diagnosis_code, provider_id, planned |
| claims | claim_line_id + version before processing | encounter_id, service_date, paid_amount, diagnosis_code, procedure_code, updated_at |
| pharmacy | fill_id | fill_date, drug_code, days_supply, paid_amount; drug codes are deliberately synthetic |
| labs | lab_id | result_date, loinc_code, result_value, unit |
| providers | provider_id | org_id, specialty |
| organisations | org_id | org_name, geo_id |
| geography | geo_id | synthetic region |
| FHIR NDJSON | resourceType + id | Patient identifiers; final numeric Observation values and patient references |

Reference code scope is deliberately small: E11.9, I10, J45.909, Z00.00 (ICD-10-CM examples), 99213 (CPT example; no licensed descriptor set included), and LOINC 4548-4 with percent units. This is an allow-list exercise, not comprehensive terminology validation. No NDC/RxNorm validation is claimed.

Quality JSON includes SHA-256 input hashes, source counts, exact duplicates, superseded versions, accepted rows, quarantined rows and aggregate incidents. Quarantine files contain synthetic rejected rows and a reason. Accepted plus every removed category must equal raw count.
