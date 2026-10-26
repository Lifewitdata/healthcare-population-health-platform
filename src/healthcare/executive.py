"""Shared dashboard charts and reproducible, aggregate-only client brief."""
import argparse
import json
import math
from html import escape
from pathlib import Path

import duckdb


def findings(database):
    with duckdb.connect(str(database), read_only=True) as con:
        members, total = con.execute(
            'select count(*),sum(total_paid) from main_reporting.rpt_high_cost_members'
        ).fetchone()
        top_n = math.ceil(members * 0.05)
        top_paid = con.execute('''select sum(total_paid) from (
            select total_paid from main_reporting.rpt_high_cost_members
            order by total_paid desc,member_id limit ?)''', [top_n]).fetchone()[0]
        year, eligible, gaps = con.execute('''select year,count(*),sum(testing_gap)
            from main_reporting.rpt_care_gaps group by year order by year desc limit 1''').fetchone()
        index, returns = con.execute('''select index_discharges,readmissions_30d
            from main_reporting.rpt_readmissions where year=?''', [year]).fetchone()
        period = con.execute('select min(month),max(month) from main_core.fact_eligibility').fetchone()
    return dict(members=members,total_paid=float(total),top_members=top_n,
                top_paid=float(top_paid),top_share=100*float(top_paid)/float(total),
                year=int(year),gap_eligible=eligible,gaps=int(gaps),
                gap_pct=100*int(gaps)/eligible,index_discharges=index,
                returns=returns,return_pct=100*returns/index,
                period_start=str(period[0])[:10],period_end=str(period[1])[:7])


def chart(title, left, right, pct):
    """A labelled 100% bar; the dashboard and saved SVG use identical bytes."""
    width = 400 * pct / 100
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="440" height="112" viewBox="0 0 440 112" role="img" aria-label="{escape(title)}: {escape(left)}; {escape(right)}">
<rect width="440" height="112" fill="white"/>
<g font-family="Arial, sans-serif" fill="#183047">
<text x="16" y="22" font-size="14" font-weight="bold">{escape(title)}</text>
<rect x="16" y="38" width="400" height="22" rx="3" fill="#dce5ed"/>
<rect x="16" y="38" width="{width:.3f}" height="22" fill="#087e8b"/>
<rect x="16" y="75" width="9" height="9" fill="#087e8b"/>
<text x="31" y="84" font-size="12">{escape(left)}</text>
<rect x="16" y="94" width="9" height="9" fill="#dce5ed"/>
<text x="31" y="103" font-size="12">{escape(right)}</text>
</g></svg>'''


def charts(d):
    return {
        'cost_concentration': chart('Share of medical + pharmacy spending',
            f"Top 5% of members: {d['top_share']:.1f}% of spend",
            f"Other 95%: {100-d['top_share']:.1f}% of spend", d['top_share']),
        'diabetes_testing': chart(f"{d['year']} annual diabetes testing review",
            f"No test recorded: {d['gaps']:,} ({d['gap_pct']:.1f}%)",
            f"Test recorded: {d['gap_eligible']-d['gaps']:,}", d['gap_pct']),
        'hospital_returns': chart(f"{d['year']} eligible hospital discharges",
            f"30-day return proxy: {d['returns']:,} ({d['return_pct']:.1f}%)",
            f"No qualifying return: {d['index_discharges']-d['returns']:,}", d['return_pct']),
    }


def brief(d):
    return f'''# Where is our cost concentrated, and which members could we help?

**Care management briefing | Synthetic demonstration**  
{d['members']:,} members · {d['period_start'][:4]}–{d['period_end'][:4]} · ${d['total_paid']/1e6:.2f} million in medical and pharmacy payments.

| What we found | Dashboard chart |
| :--- | :--- |
| **1. A small group accounts for a large share of spending.** The highest-cost 5% ({d['top_members']:,} members) account for **{d['top_share']:.1f}% of payments**, or ${d['top_paid']/1e6:.2f} million across both years. High past cost alone does not establish current care needs. | ![Share of spending by member group](images/executive/cost_concentration.svg) |
| **2. {d['gaps']:,} members have no annual diabetes blood-sugar test recorded in {d['year']}.** That is **{d['gap_pct']:.1f}% of {d['gap_eligible']:,} members** with a diabetes diagnosis recorded that year and a full year of coverage. | ![Annual diabetes testing review](images/executive/diabetes_testing.svg) |
| **3. {d['returns']:,} hospital discharges were followed by a return within 30 days in {d['year']}.** This is **{d['return_pct']:.1f}% of {d['index_discharges']:,} eligible discharges**; a member may have multiple discharges. It does not show that a return was preventable. | ![Hospital return proxy](images/executive/hospital_returns.svg) |

**Recommended actions**

- Start by reviewing the **{d['gaps']:,} diabetes records**; confirm current coverage and whether testing happened elsewhere before offering help arranging follow-up.
- Review the **{d['top_members']:,} highest-cost members** with care managers, prioritizing confirmed unmet needs. Check overlap with the diabetes group before assigning outreach.
- Review the **{d['returns']:,} hospital-return events** for follow-up opportunities. Track members reached, appointments completed and confirmed care gaps closed; do not assume savings.

**Caveats:** All people and payments are synthetic. Missing records may not mean missing care. These historical groups are not a current outreach list or a prediction. The readmission figure is a **proxy** with follow-up coverage checks, but without exclusions for planned returns, transfers or deaths; overlapping stays can also affect it. It is not a validated quality measure. ER visits are not identified in this dataset.

*Source: [dashboard](../dashboard/app.py), all regions; [calculation notes and refresh instructions](executive_summary_methods.md). Charts and figures use the same dashboard export.*
'''


def export(database, out):
    out = Path(out)
    images = out/'images'/'executive'
    images.mkdir(parents=True, exist_ok=True)
    d = findings(database)
    for name, svg in charts(d).items():
        (images/f'{name}.svg').write_text(svg, encoding='utf-8')
    (out/'executive_summary.md').write_text(brief(d), encoding='utf-8')
    evidence = out/'evidence'
    evidence.mkdir(exist_ok=True)
    (evidence/'executive_summary.json').write_text(json.dumps(d, indent=2)+'\n')
    return d


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--database', default='runtime/healthcare.duckdb')
    parser.add_argument('--out', default='docs')
    args = parser.parse_args()
    print(json.dumps(export(args.database, args.out), indent=2))
