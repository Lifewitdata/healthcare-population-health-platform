"""Local authenticated bulk loader; credentials never enter committed code."""
import os,re
from pathlib import Path
import snowflake.connector
from healthcare.transform import KEYS
from healthcare.auth import password_options

def identifier(value):
    if not re.fullmatch(r'[A-Za-z_][A-Za-z0-9_]*',value): raise ValueError('Invalid SQL identifier')
    return value.upper()

def load(clean):
    db=identifier(os.getenv('SNOWFLAKE_DATABASE','HEALTHCARE_POPULATION'))
    with snowflake.connector.connect(account=os.environ['SNOWFLAKE_ACCOUNT'],user=os.environ['SNOWFLAKE_USER'],authenticator=os.getenv('SNOWFLAKE_AUTHENTICATOR','externalbrowser'),role=os.getenv('SNOWFLAKE_ROLE','SYSADMIN'),warehouse=os.getenv('SNOWFLAKE_WAREHOUSE','HEALTHCARE_WH'),database=db,schema='RAW',**password_options()) as con:
        cur=con.cursor()
        cur.execute("CREATE FILE FORMAT IF NOT EXISTS HEALTHCARE_CSV TYPE=CSV PARSE_HEADER=TRUE FIELD_OPTIONALLY_ENCLOSED_BY='\"' EMPTY_FIELD_AS_NULL=TRUE")
        cur.execute('CREATE STAGE IF NOT EXISTS HEALTHCARE_LOAD FILE_FORMAT=HEALTHCARE_CSV')
        for name in KEYS:
            path=(Path(clean)/f'{name}.csv').resolve().as_posix()
            cur.execute(f"PUT 'file://{path}' @HEALTHCARE_LOAD/{name}/ OVERWRITE=TRUE AUTO_COMPRESS=TRUE")
            cur.execute(f"CREATE OR REPLACE TABLE {name}_NEXT USING TEMPLATE (SELECT ARRAY_AGG(OBJECT_CONSTRUCT(*)) FROM TABLE(INFER_SCHEMA(LOCATION=>'@HEALTHCARE_LOAD/{name}/',FILE_FORMAT=>'HEALTHCARE_CSV',IGNORE_CASE=>TRUE)))")
            cur.execute(f"COPY INTO {name}_NEXT FROM @HEALTHCARE_LOAD/{name}/ FILE_FORMAT=(FORMAT_NAME=HEALTHCARE_CSV) MATCH_BY_COLUMN_NAME=CASE_INSENSITIVE ON_ERROR=ABORT_STATEMENT")
        # All copies must succeed before publishing tables. Batch mode is not CDC.
        for name in KEYS: cur.execute(f'CREATE OR REPLACE TABLE {name} CLONE {name}_NEXT')
