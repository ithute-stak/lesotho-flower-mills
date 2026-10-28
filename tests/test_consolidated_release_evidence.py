from scripts.consolidate_release_evidence import REQUIRED,REQUIRED_PATHS,evaluate

SHA="a"*40

def run(name,status="completed",conclusion="success",sha=SHA,event="push"):
 return {"name":name,"status":status,"conclusion":conclusion,"head_sha":sha,"event":event,"head_branch":"main","path":REQUIRED_PATHS[name],"run_number":2,"run_attempt":1,"html_url":"https://github.com/example/actions/runs/1"}

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
 configured=set(REQUIRED)-{"CI"}
 result=evaluate(records,SHA,configured)
 assert result["ci_verdict"]=="BLOCKED"
 assert result["workflow_name_mismatches"]==["CI"]

def test_evidence_api_failure_leaves_gate_blocked(monkeypatch,tmp_path):
 import urllib.error
 import scripts.consolidate_release_evidence as gate
 monkeypatch.chdir(tmp_path)
 monkeypatch.setenv("GITHUB_REPOSITORY","example/project")
 monkeypatch.setenv("GITHUB_SHA",SHA)
 monkeypatch.setenv("GH_TOKEN","synthetic-token")
 def unavailable(*args):
  raise urllib.error.URLError("synthetic network outage")
 monkeypatch.setattr(gate,"fetch_all",unavailable)
 import pytest
 with pytest.raises(SystemExit) as exc:
  gate.main()
 assert exc.value.code==1
 import json
 report=json.loads((tmp_path/"release-evidence/consolidated.json").read_text())
 assert report["ci_verdict"]=="BLOCKED"
 assert "evidence_error" in report
 assert "Evidence retrieval error:" in (tmp_path/"release-evidence/consolidated.md").read_text()
 assert report["production_approved"] is False

def test_explicit_release_sha_overrides_workflow_dispatch_head(monkeypatch,tmp_path):
 import json
 import scripts.consolidate_release_evidence as gate
 target="b"*40
 monkeypatch.chdir(tmp_path)
 monkeypatch.setenv("GITHUB_REPOSITORY","example/project")
 monkeypatch.setenv("GITHUB_SHA",SHA)
 monkeypatch.setenv("TARGET_RELEASE_SHA",target)
 monkeypatch.setenv("GH_TOKEN","synthetic-token")
 monkeypatch.setattr(gate,"fetch_all",lambda repo,sha,token:[run(name,sha=sha) for name in REQUIRED])
 monkeypatch.setattr(gate,"fetch_workflow_names",lambda repo,token:set(REQUIRED))
 monkeypatch.setattr(gate,"is_main_ancestor",lambda repo,sha,token:True)
 gate.main()
 report=json.loads((tmp_path/"release-evidence/consolidated.json").read_text())
 assert report["release_sha"]==target
 assert report["ci_verdict"]=="PASS"
 assert report["production_approved"] is False

def test_malformed_release_sha_rejected(monkeypatch):
 import pytest
 import scripts.consolidate_release_evidence as gate
 monkeypatch.setenv("GITHUB_REPOSITORY","example/project")
 monkeypatch.setenv("GITHUB_SHA",SHA)
 monkeypatch.setenv("TARGET_RELEASE_SHA","../../not-a-commit")
 monkeypatch.setenv("GH_TOKEN","synthetic-token")
 with pytest.raises(ValueError,match="40-character"):
  gate.main()

def test_run_pagination_overflow_blocks_instead_of_silent_partial_pass(monkeypatch):
 import io,json,pytest
 import scripts.consolidate_release_evidence as gate
 class Response:
  def __enter__(self):return self
  def __exit__(self,*args):pass
  def read(self,*args):return self.body.read(*args)
  def __init__(self):
   self.body=io.BytesIO(json.dumps({"workflow_runs":[{"name":"synthetic"}]*100}).encode())
 monkeypatch.setattr(gate.urllib.request,"urlopen",lambda *args,**kwargs:Response())
 with pytest.raises(ValueError,match="pagination exceeded"):
  gate.fetch_all("example/project",SHA,"synthetic-token")

def test_workflow_listing_overflow_blocks(monkeypatch):
 import io,json,pytest
 import scripts.consolidate_release_evidence as gate
 class Response:
  def __enter__(self):return self
  def __exit__(self,*args):pass
  def read(self,*args):return self.body.read(*args)
  def __init__(self):
   self.body=io.BytesIO(json.dumps({"workflows":[{"name":"synthetic","state":"active"}]*100}).encode())
 monkeypatch.setattr(gate.urllib.request,"urlopen",lambda *args,**kwargs:Response())
 with pytest.raises(ValueError,match="listing exceeded"):
  gate.fetch_workflow_names("example/project","synthetic-token")

def test_required_workflow_names_match_workflow_files():
 """Avoid a silently blocked release caused by renamed workflow headers."""
 from pathlib import Path
 import re
 workflow_paths={
  "CI":".github/workflows/ci.yml",
  "Backend Browser E2E":".github/workflows/backend-browser-e2e.yml",
  "Deployment Config":".github/workflows/deployment-config.yml",
  "Docker Network Isolation":".github/workflows/docker-network-isolation.yml",
  "Full Stack Network Isolation":".github/workflows/full-stack-network-isolation.yml",
  "Release Readiness Evidence":".github/workflows/release-readiness.yml",
 }
 assert set(workflow_paths)==REQUIRED
 root=Path(__file__).resolve().parents[1]
 for expected,path in workflow_paths.items():
  text=(root/path).read_text()
  match=re.search(r"^name:\s*(.+?)\s*$",text,re.MULTILINE)
  assert match, f"Missing workflow name in {path}"
  assert match.group(1).strip().strip("\'\"")==expected, f"Incorrect workflow name in {path}"

def test_push_from_non_main_branch_cannot_satisfy_release_gate():
 records=[run(name) for name in REQUIRED]
 records[0]["head_branch"]="feature/not-main"
 result=evaluate(records,SHA)
 assert result["ci_verdict"]=="BLOCKED"
 assert records[0]["name"] in result["missing"]

def test_unrelated_commit_blocks_release_even_with_successful_ci(monkeypatch,tmp_path):
 import json,pytest
 import scripts.consolidate_release_evidence as gate
 monkeypatch.chdir(tmp_path)
 monkeypatch.setenv("GITHUB_REPOSITORY","example/project")
 monkeypatch.setenv("GITHUB_SHA",SHA)
 monkeypatch.delenv("TARGET_RELEASE_SHA",raising=False)
 monkeypatch.setenv("GH_TOKEN","synthetic-token")
 monkeypatch.setattr(gate,"fetch_all",lambda repo,sha,token:[run(name) for name in REQUIRED])
 monkeypatch.setattr(gate,"fetch_workflow_names",lambda repo,token:set(REQUIRED))
 monkeypatch.setattr(gate,"is_main_ancestor",lambda repo,sha,token:False)
 with pytest.raises(SystemExit) as exc:
  gate.main()
 assert exc.value.code==1
 report=json.loads((tmp_path/"release-evidence/consolidated.json").read_text())
 assert report["ci_verdict"]=="BLOCKED"
 assert report["commit_on_main"] is False
 assert report["production_approved"] is False

def test_latest_rerun_attempt_takes_precedence_over_older_success():
 records=[run(name) for name in REQUIRED]
 name=records[0]["name"]
 prior=records[0].copy()
 prior["run_number"]=9
 prior["run_attempt"]=1
 failed=records[0].copy()
 failed["run_number"]=9
 failed["run_attempt"]=2
 failed["conclusion"]="failure"
 records[0]=prior
 result=evaluate(records+[failed],SHA)
 assert result["ci_verdict"]=="BLOCKED"
 assert result["not_successful"][name]=="failure"

def test_successful_latest_rerun_can_clear_prior_failure():
 records=[run(name) for name in REQUIRED]
 previous=records[0].copy()
 previous["conclusion"]="failure"
 previous["run_attempt"]=1
 records[0]["run_attempt"]=2
 assert evaluate([previous]+records,SHA)["ci_verdict"]=="PASS"

def test_duplicate_workflow_name_from_wrong_path_cannot_approve_release():
 records=[run(name) for name in REQUIRED]
 records[0]["path"]=".github/workflows/other-ci.yml"
 result=evaluate(records,SHA)
 assert result["ci_verdict"]=="BLOCKED"
 assert records[0]["name"] in result["missing"]

def test_workflow_path_with_github_ref_suffix_is_accepted():
 records=[run(name) for name in REQUIRED]
 records[0]["path"]=records[0]["path"]+"@refs/heads/main"
 assert evaluate(records,SHA)["ci_verdict"]=="PASS"
