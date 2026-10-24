select * from {{ ref('rpt_readmissions') }} where readmissions_30d > index_discharges or readmission_rate < 0 or readmission_rate > 1
