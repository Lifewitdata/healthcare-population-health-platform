with visits as (
 select member_id,cast(date_trunc('month',admit_date) as date) as month,
 sum(case when encounter_type='inpatient' then 1 else 0 end) as admissions,count(*) as encounters
 from {{ ref('fact_encounters') }} group by 1,2
)
select e.month,count(*) as member_months,sum(coalesce(v.admissions,0)) as admissions,
 sum(coalesce(v.encounters,0)) as encounters,
 1000.0*sum(coalesce(v.admissions,0))/count(*) as admissions_per_1000_member_months,
 12000.0*sum(coalesce(v.admissions,0))/count(*) as annualised_admissions_per_1000
from {{ ref('fact_eligibility') }} e left join visits v on e.member_id=v.member_id and e.month=v.month group by 1
