"""Prefect batch pipeline. Deploy a schedule explicitly; none is enabled by import."""
from prefect import flow,task
from healthcare.pipeline import build

@task(retries=2,retry_delay_seconds=15)
def run_batch(root,target):
    return build(root=root,target=target,regenerate=False)

@flow(name='healthcare-daily-batch',log_prints=True)
def daily_pipeline(root='runtime',target='local'):
    return run_batch(root,target)

if __name__=='__main__': daily_pipeline()
