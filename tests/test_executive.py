import duckdb
import pytest
from healthcare.executive import findings


def test_member_denominator_and_discharge_denominator(tmp_path):
    database = tmp_path/'example.duckdb'
    with duckdb.connect(str(database)) as con:
        con.execute('create schema main_reporting; create schema main_core')
        # Twenty members, including zero spenders: top 5% is one member.
        con.execute('''create table main_reporting.rpt_high_cost_members as
            select i as member_id, case when i=1 then 80 when i=2 then 20 else 0 end as total_paid
            from range(1,21) t(i)''')
        con.execute('''create table main_reporting.rpt_care_gaps as
            select * from (values (2024,1),(2025,1),(2025,0),(2025,0),(2025,0)) t(year,testing_gap)''')
        con.execute('''create table main_reporting.rpt_readmissions as
            select * from (values (2024,50,4),(2025,100,3)) t(year,index_discharges,readmissions_30d)''')
        con.execute("create table main_core.fact_eligibility as select date '2024-01-01' as month union all select date '2025-12-01'")
    d = findings(database)
    assert (d['members'], d['top_members'], d['top_share']) == (20, 1, 80)
    assert (d['year'], d['gap_eligible'], d['gaps'], d['gap_pct']) == (2025, 4, 1, 25)
    assert d['return_pct'] == pytest.approx(3)
    assert d['index_discharges'] == 100


def test_chart_proportion_and_accessible_labels():
    from healthcare.executive import chart
    import xml.etree.ElementTree as ET
    svg = chart('Cost & care', 'Group <5: 20%', 'Remaining: 80%', 20)
    root = ET.fromstring(svg)
    rects = root.findall('.//{http://www.w3.org/2000/svg}rect')
    assert any(r.attrib.get('width') == '80.000' for r in rects)
    assert root.attrib['aria-label'] == 'Cost & care: Group <5: 20%; Remaining: 80%'
