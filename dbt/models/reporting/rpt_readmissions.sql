-- All-cause 30-day proxy. No validated clinical exclusions or risk adjustment.
with ordered as (
 select *,lead(admit_date) over(partition by member_id order by admit_date,encounter_id) as next_admit
 from {{ ref('fact_encounters') }} where encounter_type='inpatient'
), eligible as (
 select o.* from ordered o
 where discharge_date <= cast('2025-12-01' as date)
 and exists(select 1 from {{ ref('fact_eligibility') }} e where e.member_id=o.member_id and e.month=cast(date_trunc('month',{{ dbt.dateadd('day',30,'o.discharge_date') }}) as date))
)
select extract(year from discharge_date) as year,count(*) as index_discharges,
 sum(case when {{ dbt.datediff('discharge_date','next_admit','day') }} between 1 and 30 then 1 else 0 end) as readmissions_30d,
 1.0*sum(case when {{ dbt.datediff('discharge_date','next_admit','day') }} between 1 and 30 then 1 else 0 end)/nullif(count(*),0) as readmission_rate
from eligible group by 1
