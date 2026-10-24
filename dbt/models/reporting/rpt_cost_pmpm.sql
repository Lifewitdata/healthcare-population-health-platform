with costs as (
 select member_id, cast(date_trunc('month',service_date) as date) as month, paid_amount as medical, 0 as pharmacy
 from {{ ref('fact_claims') }}
 union all
 select member_id, cast(date_trunc('month',fill_date) as date),0,paid_amount from {{ ref('fact_pharmacy') }}
), summed as (
 select member_id,month,sum(medical) as medical,sum(pharmacy) as pharmacy from costs group by 1,2
)
select e.month,g.region,count(*) as member_months,
 sum(coalesce(c.medical,0)) as medical_paid,
 sum(coalesce(c.pharmacy,0)) as pharmacy_paid,
 sum(coalesce(c.medical,0)+coalesce(c.pharmacy,0)) as total_paid,
 sum(coalesce(c.medical,0)+coalesce(c.pharmacy,0))/nullif(count(*),0) as pmpm
from {{ ref('fact_eligibility') }} e
join {{ ref('dim_members') }} m on e.member_id=m.member_id
join {{ ref('dim_geography') }} g on m.geo_id=g.geo_id
left join summed c on e.member_id=c.member_id and e.month=c.month
group by 1,2
