from pathlib import Path
import json,os
import duckdb
import streamlit as st
import plotly.express as px
st.set_page_config(page_title='Healthcare Population Health',page_icon='🏥',layout='wide')
st.title('Population health & cost analytics')
st.caption('SYNTHETIC DATA • Educational portfolio • 2024–2025 • No clinical or compliance claims')
root=Path(os.getenv('HEALTHCARE_RUNTIME','runtime'))
if not (root/'healthcare.duckdb').exists():
    st.info('Run healthcare build --members 25000 first.');st.stop()
@st.cache_data(ttl=60)
def query(sql):
    with duckdb.connect(str(root/'healthcare.duckdb'),read_only=True) as con: return con.execute(sql).df()
try:
    cost=query('select * from main_reporting.rpt_cost_pmpm')
except duckdb.Error:
    st.info('The warehouse is being built or is not ready. Finish the pipeline, then reload this page.');st.stop()
regions=st.sidebar.multiselect('Regions',sorted(cost.region.unique()),default=sorted(cost.region.unique()))
cost=cost[cost.region.isin(regions)]
st.sidebar.caption('Region selection applies to Cost overview only. Other tabs show the whole population.')
tabs=st.tabs(['Cost overview','Utilisation','Care gaps','Savings scenarios','Pipeline quality'])
with tabs[0]:
    total=cost.total_paid.sum();months=cost.member_months.sum()
    a,b,c=st.columns(3);a.metric('Total paid',f'${total:,.0f}');b.metric('Eligible member-months',f'{months:,.0f}');c.metric('PMPM',f'${total/months:,.2f}' if months else '—')
    trend=cost.groupby('month',as_index=False)[['total_paid','member_months']].sum();trend['pmpm']=trend.total_paid/trend.member_months
    st.plotly_chart(px.line(trend,x='month',y='pmpm',markers=True,title='Paid cost per eligible member-month'),width='stretch')
    st.dataframe(cost,width='stretch',hide_index=True);st.download_button('Download cost report',cost.to_csv(index=False),'cost_report.csv')
with tabs[1]:
    u=query('select * from main_reporting.rpt_utilisation order by month')
    st.plotly_chart(px.bar(u,x='month',y='annualised_admissions_per_1000',title='Annualised admissions per 1,000 members'),width='stretch')
    st.caption('Monthly admissions ÷ eligible member-months × 12,000. This is an annualised rate, not a forecast.')
    st.dataframe(query('select * from main_reporting.rpt_readmissions'),hide_index=True)
with tabs[2]:
    gap=query('select year,count(*) eligible_members,sum(testing_gap) testing_gaps from main_reporting.rpt_care_gaps group by year order by year')
    st.subheader('Annual HbA1c testing proxy');st.caption('Diabetes-coded adults with 12 covered months in the year; not certified HEDIS.')
    st.dataframe(gap,hide_index=True)
    risk=query('select illustrative_risk_tier,count(*) members,sum(total_paid) total_paid from main_reporting.rpt_high_cost_members group by 1')
    st.plotly_chart(px.bar(risk,x='illustrative_risk_tier',y='members'),width='stretch')
with tabs[3]:
    st.warning('Illustrative scenarios only. No realised savings or causal treatment effects.')
    st.dataframe(query('select * from main_reporting.rpt_savings_scenarios'),hide_index=True)
    st.caption('Top cost decile; assumed programme cost $240 per targeted member over the full reporting period.')
with tabs[4]:
    q=json.loads((root/'clean/quality.json').read_text())
    st.json(q['reconciliation']);st.dataframe(q['incidents'],hide_index=True);st.json(q['fhir'])
    if (root/'agent_report.json').exists():st.json(json.loads((root/'agent_report.json').read_text()))
