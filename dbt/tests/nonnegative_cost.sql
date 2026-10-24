select * from {{ ref('fact_claims') }} where paid_amount < 0 or paid_amount is null
