import json, os, subprocess
from pathlib import Path
import duckdb
from healthcare.generate import generate
from healthcare.transform import transform, KEYS
ROOT=Path(__file__).resolve().parents[2]

def load_local(clean, database):
    con=duckdb.connect(str(database));con.execute('create schema if not exists raw')
    for name in KEYS:
        path=str((Path(clean)/f'{name}.csv').resolve())
        con.execute(f'create or replace table raw.{name} as select * from read_csv_auto(?)',[path])
    con.close()

def build(root='runtime',members=25000,target='local',regenerate=True):
    root=Path(root).resolve();root.mkdir(parents=True,exist_ok=True)
    if regenerate: generate(root/'raw',members)
    report=transform(root/'raw',root/'clean')
    # Known injected defects are quarantined. Unexpected error rate blocks publication.
    rate=sum(v['quarantined'] for v in report['reconciliation'].values())/sum(v['raw'] for v in report['reconciliation'].values())
    if rate>0.02: raise ValueError('Quarantine exceeds 2%; publication blocked')
    if target=='local': load_local(root/'clean',root/'healthcare.duckdb')
    else:
        from healthcare.snowflake import load
        load(root/'clean')
    env={**os.environ,'DBT_DUCKDB_PATH':str(root/'healthcare.duckdb'),'DBT_RAW_SCHEMA':'RAW' if target=='snowflake' else 'raw'}
    subprocess.run(['dbt','build','--project-dir',str(ROOT/'dbt'),'--profiles-dir',str(ROOT/'dbt'),'--target',target]+(['--full-refresh'] if regenerate else []),env=env,check=True)
    if target=='local': export(root)
    return report

def export(root):
    root=Path(root);out=root/'reports';out.mkdir(exist_ok=True)
    con=duckdb.connect(str(root/'healthcare.duckdb'),read_only=True)
    for (name,) in con.execute("select table_name from information_schema.tables where table_schema='main_reporting'").fetchall():
        con.execute(f"copy main_reporting.{name} to '{out/name}.csv' (header, delimiter ',')")
    con.close()
