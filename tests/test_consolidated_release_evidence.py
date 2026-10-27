from scripts.consolidate_release_evidence import REQUIRED,evaluate

SHA="a"*40

def run(name,status="completed",conclusion="success",sha=SHA,event="push"):
 return {"name":name,"status":status,"conclusion":conclusion,"head_sha":sha,"event":event,"run_number":2,"run_attempt":1,"html_url":"https://github.com/example/actions/runs/1"}

def test_all_required_exact_sha_push_runs_can_pass():
 result=evaluate([run(name) for name in REQUIRED],SHA)
 assert result["ci_verdict"]=="PASS"
 assert result["production_approved"] is False

def test_missing_workflow_blocks_release():
 result=evaluate([run(name) for name in list(REQUIRED)[:-1]],SHA)
 assert result["ci_verdict"]=="BLOCKED"
 assert result["missing"]

def test_failure_and_pending_block_release():
 names=list(REQUIRED)
 records=[run(name) for name in names]
 records[0]["conclusion"]="failure"
 assert evaluate(records,SHA)["ci_verdict"]=="BLOCKED"
 records[0]["conclusion"]=None
 records[0]["status"]="in_progress"
 assert evaluate(records,SHA)["ci_verdict"]=="BLOCKED"

def test_other_shas_and_pr_runs_do_not_count():
 records=[run(n,sha="b"*40) for n in REQUIRED]
 assert evaluate(records,SHA)["ci_verdict"]=="BLOCKED"
 records=[run(n,event="pull_request") for n in REQUIRED]
 assert evaluate(records,SHA)["ci_verdict"]=="BLOCKED"

def test_wrongly_named_workflow_blocks_release_even_with_successful_runs():
 records=[run(name) for name in REQUIRED]
 configured=set(REQUIRED)-{"Main CI"}
 result=evaluate(records,SHA,configured)
 assert result["ci_verdict"]=="BLOCKED"
 assert result["workflow_name_mismatches"]==["Main CI"]
