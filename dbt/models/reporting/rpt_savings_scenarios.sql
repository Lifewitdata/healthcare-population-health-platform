-- Illustrative arithmetic only; no causal claim or realised savings.
with high_cost as (select sum(total_paid) as baseline_paid,count(*) as members from {{ ref('rpt_high_cost_members') }} where cost_decile=1), assumptions as (
 select 0.02 as reduction_fraction union all select 0.05 union all select 0.10
)
select h.*,a.reduction_fraction,h.baseline_paid*a.reduction_fraction as gross_savings,
 h.members*240 as assumed_program_cost,
 h.baseline_paid*a.reduction_fraction-h.members*240 as net_savings
from high_cost h cross join assumptions a
