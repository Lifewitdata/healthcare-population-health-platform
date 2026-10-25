import argparse,json
from healthcare.generate import generate
from healthcare.pipeline import build
from healthcare.auth import login_password

def main():
    p=argparse.ArgumentParser();p.add_argument('command',choices=['generate','build']);p.add_argument('--members',type=int,default=25000);p.add_argument('--root',default='runtime');p.add_argument('--target',choices=['local','snowflake'],default='local');p.add_argument('--reuse-raw',action='store_true');a=p.parse_args()
    with login_password(a.command == 'build' and a.target == 'snowflake'):
        result=generate(a.root+'/raw',a.members) if a.command=='generate' else build(a.root,a.members,a.target,not a.reuse_raw)
    print(json.dumps(result,indent=2))
