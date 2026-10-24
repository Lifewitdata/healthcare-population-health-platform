select 1 as failure where abs(
 (select sum(total_paid) from {{ ref('rpt_cost_pmpm') }}) -
 (select sum(paid_amount) from {{ ref('fact_claims') }}) -
 (select sum(paid_amount) from {{ ref('fact_pharmacy') }})
)>0.01
