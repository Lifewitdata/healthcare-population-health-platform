"""Deterministic, linked synthetic extracts; no real people or clinical records."""
import calendar, csv, json, random
from datetime import date, timedelta
from pathlib import Path

CODES = ['E11.9','I10','J45.909','Z00.00']

def write_csv(path, rows):
    with path.open('w', newline='') as f:
        w=csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)

def generate(root, members=25000, seed=42, inject=True):
    if members < 10: raise ValueError('Use at least 10 members')
    root=Path(root); root.mkdir(parents=True,exist_ok=True); rng=random.Random(seed)
    tables={k:[] for k in ['members','identity_map','eligibility','encounters','claims','pharmacy','labs','providers','organisations','geography']}
    tables['geography']=[dict(geo_id=f'G{i}',region=r) for i,r in enumerate(['North','South','East','West'],1)]
    tables['organisations']=[dict(org_id=f'O{i}',org_name=f'Synthetic Network {i}',geo_id=f'G{1+(i-1)%4}') for i in range(1,9)]
    tables['providers']=[dict(provider_id=f'P{i}',org_id=f'O{1+(i-1)%8}',specialty=['Primary Care','Internal Medicine','Pulmonology'][i%3]) for i in range(1,41)]
    fhir=[]
    for i in range(1,members+1):
        mid=f'M{i:06}'; eid=f'EHR{i:06}'; age=rng.randint(18,85)
        tables['members'].append(dict(member_id=mid,age_at_2024=age,geo_id=f'G{rng.randint(1,4)}'))
        for system,prefix in [('ehr','EHR'),('claims','PAY'),('pharmacy','RX'),('lab','LAB')]:
            tables['identity_map'].append(dict(system=system,source_member_id=f'{prefix}{i:06}',member_id=mid))
        start=rng.randint(0,5); end=rng.randint(18,23); months=list(range(start,end+1))
        for m in months:
            tables['eligibility'].append(dict(eligibility_id=f'{mid}-{m}',member_id=mid,month=date(2024+m//12,m%12+1,1).isoformat()))
        diabetes=rng.random()<0.22; hypertension=rng.random()<0.30
        dx='E11.9' if diabetes else ('I10' if hypertension else rng.choice(['J45.909','Z00.00']))
        n=rng.randint(2,9); visitmonths=sorted(rng.choices(months,k=n))
        for j,m in enumerate(visitmonths):
            day=date(2024+m//12,m%12+1,rng.randint(1,20)); inpatient=rng.random()<0.12
            discharge=day+timedelta(days=rng.randint(1,5) if inpatient else 0)
            enc=f'V{i:06}-{j}'; typ='inpatient' if inpatient else 'outpatient'
            tables['encounters'].append(dict(encounter_id=enc,source_member_id=eid,admit_date=str(day),discharge_date=str(discharge),encounter_type=typ,diagnosis_code=dx,provider_id=f'P{rng.randint(1,40)}',planned=False))
            amount=rng.randint(2000,18000) if inpatient else rng.randint(60,450)
            for line in range(1,3):
                cid=f'C{i:06}-{j}-{line}'
                claim=dict(claim_line_id=cid,version=1,source_member_id=f'PAY{i:06}',encounter_id=enc,service_date=str(day),paid_amount=round(amount*(0.8 if line==1 else 0.2),2),diagnosis_code=dx,procedure_code='99213',updated_at=str(discharge+timedelta(days=rng.randint(10,60))))
                tables['claims'].append(claim)
                if rng.random()<0.03:
                    tables['claims'].append({**claim,'version':2,'paid_amount':round(claim['paid_amount']*0.9,2),'updated_at':str(discharge+timedelta(days=90))})
        if diabetes:
            for yr in [2024,2025]:
                valid=[m for m in months if 2024+m//12==yr]
                if valid and rng.random()<0.75:
                    m=rng.choice(valid); d=date(yr,m%12+1,15)
                    lab=dict(lab_id=f'L{i:06}-{yr}',source_member_id=f'LAB{i:06}',result_date=str(d),loinc_code='4548-4',result_value=round(rng.uniform(5.5,11.5),1),unit='%')
                    tables['labs'].append(lab)
                    fhir.append({'resourceType':'Observation','id':lab['lab_id'],'status':'final','code':{'coding':[{'system':'http://loinc.org','code':'4548-4'}]},'subject':{'reference':f'Patient/{eid}'},'effectiveDateTime':str(d),'valueQuantity':{'value':lab['result_value'],'unit':'%','system':'http://unitsofmeasure.org','code':'%'}})
        for j,m in enumerate(months[::3]):
            tables['pharmacy'].append(dict(fill_id=f'F{i:06}-{j}',source_member_id=f'RX{i:06}',fill_date=str(date(2024+m//12,m%12+1,12)),drug_code='SYNTH-DM-01' if diabetes else 'SYNTH-OTHER-01',days_supply=30,paid_amount=rng.randint(8,120)))
        fhir.append({'resourceType':'Patient','id':eid,'active':True,'identifier':[{'system':'urn:synthetic:member','value':mid}]})
    if not tables['labs']:
        tables['labs'].append(dict(lab_id='L-DEMO',source_member_id='LAB000001',result_date='2025-06-15',loinc_code='4548-4',result_value=7.0,unit='%'))
    if inject:
        tables['claims'].append(dict(tables['claims'][0]))
        for suffix,changes in [('unknown',{'source_member_id':'PAY-UNKNOWN'}),('code',{'diagnosis_code':'INVALID'}),('amount',{'paid_amount':-100}),('date',{'service_date':'not-a-date'})]:
            tables['claims'].append({**tables['claims'][0],'claim_line_id':f'BAD-{suffix}',**changes})
    for name, rows in tables.items(): write_csv(root/f'{name}.csv',rows)
    with (root/'fhir.ndjson').open('w') as f:
        for resource in fhir: f.write(json.dumps(resource)+'\n')
    manifest={'seed':seed,'members':members,'period':'2024-01-01 to 2025-12-31','synthetic':True,'raw_rows':{k:len(v) for k,v in tables.items()},'injected_invalid_claims':4 if inject else 0}
    (root/'generation.json').write_text(json.dumps(manifest,indent=2)); return manifest
