"""Polars validation, deterministic identity matching, version selection and quarantine."""
import hashlib, json
from pathlib import Path
import polars as pl

KEYS={'members':'member_id','identity_map':None,'eligibility':'eligibility_id','encounters':'encounter_id','claims':'claim_line_id','pharmacy':'fill_id','labs':'lab_id','providers':'provider_id','organisations':'org_id','geography':'geo_id'}
DATES={'eligibility':['month'],'encounters':['admit_date','discharge_date'],'claims':['service_date','updated_at'],'pharmacy':['fill_date'],'labs':['result_date']}
SYSTEMS={'encounters':'ehr','claims':'claims','pharmacy':'pharmacy','labs':'lab'}

def parse_fhir(path):
    """Parse only Patient and numeric Observation resources from this R4 subset."""
    patients=[]; observations=[]
    for line in Path(path).read_text().splitlines():
        r=json.loads(line)
        if r['resourceType']=='Patient': patients.append({'ehr_id':r['id'],'member_id':r['identifier'][0]['value']})
        elif r['resourceType']=='Observation':
            if r.get('status')!='final': continue
            observations.append({'lab_id':r['id'],'ehr_id':r['subject']['reference'].removeprefix('Patient/'),'loinc_code':r['code']['coding'][0]['code'],'result_value':r['valueQuantity']['value']})
        else: raise ValueError(f"Unsupported FHIR resource {r['resourceType']}")
    return patients,observations

def transform(raw, output):
    raw,output=Path(raw),Path(output);output.mkdir(parents=True,exist_ok=True)
    tables={n:pl.read_csv(raw/f'{n}.csv',infer_schema_length=10000) for n in KEYS}
    ids=tables['identity_map']
    if ids.select(pl.struct(['system','source_member_id']).is_duplicated().any()).item(): raise ValueError('Ambiguous identity mapping')
    incidents=[];stats={}; clean={}
    for name,df in tables.items():
        raw_count=df.height
        strings=[c for c,t in df.schema.items() if t==pl.String]
        df=df.with_columns([pl.col(c).str.strip_chars() for c in strings]).unique(maintain_order=True)
        duplicate_count=raw_count-df.height
        if name in SYSTEMS:
            lookup=ids.filter(pl.col('system')==SYSTEMS[name]).select('source_member_id','member_id')
            df=df.join(lookup,on='source_member_id',how='left',validate='m:1')
        rules=[]
        if name in SYSTEMS: rules.append(('unknown_member',pl.col('member_id').is_null()))
        if KEYS[name]: rules.append(('missing_key',pl.col(KEYS[name]).is_null()))
        for c in DATES.get(name,[]):
            df=df.with_columns(pl.col(c).cast(pl.String).str.to_date(strict=False).alias(c))
            rules.append((f'invalid_{c}',pl.col(c).is_null()))
        if name in ['claims','encounters']:
            df=df.with_columns(pl.col('diagnosis_code').str.to_uppercase())
            rules.append(('invalid_diagnosis',~pl.col('diagnosis_code').is_in(['E11.9','I10','J45.909','Z00.00'])))
        if name=='claims':
            rules += [('invalid_amount',pl.col('paid_amount').is_null() | (pl.col('paid_amount')<0)),('invalid_procedure',pl.col('procedure_code').cast(pl.String)!='99213')]
        if name=='labs': rules += [('invalid_lab_code',pl.col('loinc_code')!='4548-4'),('invalid_lab_unit',pl.col('unit')!='%')]
        if name=='encounters': rules += [('invalid_chronology',pl.col('discharge_date')<pl.col('admit_date'))]
        reason=pl.lit('')
        for label,condition in reversed(rules): reason=pl.when(condition.fill_null(True)).then(pl.lit(label)).otherwise(reason)
        df=df.with_columns(reason.alias('_reason'))
        bad=df.filter(pl.col('_reason')!='')
        if bad.height:
            bad.write_csv(output/f'quarantine_{name}.csv')
            for row in bad.group_by('_reason').len().to_dicts(): incidents.append({'source':name,'rule':row['_reason'],'count':row['len']})
        df=df.filter(pl.col('_reason')=='').drop('_reason')
        versions=0
        if name=='claims':
            if df.select(pl.struct(['claim_line_id','version']).is_duplicated().any()).item(): raise ValueError('Conflicting claim version')
            before=df.height
            df=df.sort(['claim_line_id','version','updated_at']).unique(subset=['claim_line_id'],keep='last',maintain_order=True)
            versions=before-df.height
        if KEYS[name] and df[KEYS[name]].n_unique()!=df.height: raise ValueError(f'Duplicate key: {name}')
        df=df.sort(KEYS[name] or ['system','source_member_id']);df.write_csv(output/f'{name}.csv');clean[name]=df
        stats[name]={'raw':raw_count,'exact_duplicates':duplicate_count,'quarantined':bad.height,'superseded_versions':versions,'accepted':df.height}
        assert raw_count==duplicate_count+bad.height+versions+df.height
    patients,observations=parse_fhir(raw/'fhir.ndjson')
    expected=dict(zip(ids.filter(pl.col('system')=='ehr')['source_member_id'],ids.filter(pl.col('system')=='ehr')['member_id']))
    assert all(expected[p['ehr_id']]==p['member_id'] for p in patients)
    lab_values=dict(zip(clean['labs']['lab_id'],clean['labs']['result_value']))
    assert all(o['lab_id'] in lab_values and abs(lab_values[o['lab_id']]-o['result_value'])<0.001 for o in observations)
    report={'synthetic':True,'reconciliation':stats,'incidents':incidents,'fhir':{'patients':len(patients),'observations':len(observations),'matched':True},'sha256':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in raw.glob('*.csv')}}
    (output/'quality.json').write_text(json.dumps(report,indent=2))
    return report
