with costs as (
 select member_id,paid_amount from {{ ref('fact_claims') }} union all select member_id,paid_amount from {{ ref('fact_pharmacy') }}
), totals as (select member_id,sum(paid_amount) as total_paid from costs group by 1), conditions as (
 select member_id,count(distinct case when diagnosis_code in ('E11.9','I10','J45.909') then diagnosis_code end) as condition_count
 from {{ ref('fact_encounters') }} group by 1
)
select m.member_id,coalesce(t.total_paid,0) as total_paid,coalesce(c.condition_count,0) as condition_count,
 case when coalesce(c.condition_count,0)>=2 or m.age_at_2024>=65 then 'Higher' else 'Standard' end as illustrative_risk_tier,
 ntile(10) over(order by coalesce(t.total_paid,0) desc,m.member_id) as cost_decile
from {{ ref('dim_members') }} m left join totals t on m.member_id=t.member_id left join conditions c on m.member_id=c.member_id
