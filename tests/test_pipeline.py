import json
import polars as pl
import pytest
from healthcare.generate import generate
from healthcare.transform import transform

def test_injected_errors_and_conservation(tmp_path):
    generate(tmp_path/'raw',100)
    q=transform(tmp_path/'raw',tmp_path/'clean')
    c=q['reconciliation']['claims']
    assert c['quarantined']==4 and c['exact_duplicates']==1
    assert c['raw']==c['accepted']+c['superseded_versions']+c['exact_duplicates']+c['quarantined']
    assert q['fhir']['patients']==100 and q['fhir']['matched']
    assert {i['rule'] for i in q['incidents']}=={'unknown_member','invalid_diagnosis','invalid_amount','invalid_service_date'}

def test_latest_version_wins_and_rerun_is_stable(tmp_path):
    generate(tmp_path/'raw',100)
    raw=pl.read_csv(tmp_path/'raw/claims.csv');r=raw.row(0,named=True);r.update(version=999,paid_amount=1.23)
    pl.concat([raw,pl.DataFrame([r],schema=raw.schema)]).write_csv(tmp_path/'raw/claims.csv')
    transform(tmp_path/'raw',tmp_path/'clean');first=(tmp_path/'clean/claims.csv').read_bytes()
    clean=pl.read_csv(tmp_path/'clean/claims.csv')
    assert clean.filter(pl.col('claim_line_id')==r['claim_line_id'])['paid_amount'].item()==1.23
    transform(tmp_path/'raw',tmp_path/'clean');assert first==(tmp_path/'clean/claims.csv').read_bytes()

def test_ambiguous_identity_blocks(tmp_path):
    generate(tmp_path/'raw',100)
    p=tmp_path/'raw/identity_map.csv';df=pl.read_csv(p);pl.concat([df,df.head(1)]).write_csv(p)
    with pytest.raises(ValueError,match='Ambiguous'):transform(tmp_path/'raw',tmp_path/'clean')
