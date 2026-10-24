select member_id,month from {{ ref('fact_eligibility') }} group by 1,2 having count(*)>1
