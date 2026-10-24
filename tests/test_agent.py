import importlib.util,json
from pathlib import Path
import pytest
spec=importlib.util.spec_from_file_location('investigator',Path(__file__).parents[1]/'agent/investigator.py')
agent=importlib.util.module_from_spec(spec);spec.loader.exec_module(agent)

def test_agent_tool_rejects_unlisted_source():
    with pytest.raises(ValueError): agent.evidence({'reconciliation':{},'incidents':[]},'arbitrary_sql')

def test_reference_report_requires_review(tmp_path):
    p=tmp_path/'q.json';p.write_text(json.dumps({'incidents':[{'source':'claims','rule':'unknown_member','count':1}]}))
    result=agent.investigate(p)
    assert result['mode'].startswith('deterministic')
    assert result['findings'][0]['requires_review'] is True
