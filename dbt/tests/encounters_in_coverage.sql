select v.* from {{ ref('fact_encounters') }} v left join {{ ref('fact_eligibility') }} e
on v.member_id=e.member_id and cast(date_trunc('month',v.admit_date) as date)=e.month where e.member_id is null
