-- Educational annual HbA1c testing proxy, NOT a HEDIS specification.
with covered as (
 select member_id,extract(year from month) as year,count(*) as covered_months
 from {{ ref('fact_eligibility') }} group by 1,2 having count(*)=12
), diabetic as (
 select distinct member_id,extract(year from admit_date) as year from {{ ref('fact_encounters') }} where diagnosis_code='E11.9'
), tested as (
 select member_id,extract(year from result_date) as year,count(*) as tests from {{ ref('fact_labs') }} where loinc_code='4548-4' and unit='%' group by 1,2
)
select c.member_id,c.year,c.covered_months,coalesce(t.tests,0) as hba1c_tests,
 case when coalesce(t.tests,0)=0 then 1 else 0 end as testing_gap
from covered c join diabetic d on c.member_id=d.member_id and c.year=d.year
left join tested t on c.member_id=t.member_id and c.year=t.year
