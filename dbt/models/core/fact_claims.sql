{{ config(materialized='incremental', unique_key='claim_line_id', incremental_strategy='delete+insert') }}
-- Compare version per key, not a global date watermark: late older claims still load.
select s.* from {{ ref('stg_claims') }} s
{% if is_incremental() %}
left join {{ this }} t on s.claim_line_id=t.claim_line_id
where t.claim_line_id is null or s.version > t.version
{% endif %}
