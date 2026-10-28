"""Consolidate GitHub workflow evidence without treating CI as deployment approval."""
import json
import os
import re
import sys
import urllib.error
import urllib.request
from datetime import datetime,timezone
from pathlib import Path

REQUIRED={
 "Backend Browser E2E",
 "CI",
 "Deployment Config",
 "Docker Network Isolation",
 "Full Stack Network Isolation",
 "Release Readiness Evidence",
}
# Workflow names must be checked against the repository's actual configured set.
# A missing or renamed required check blocks the automated verdict.

def evaluate(runs, sha, configured_names=None):
 by_name={}
 for run in runs:
  if run.get("head_sha")!=sha or run.get("event")!="push" or run.get("head_branch")!="main":
   continue
  if run.get("name") not in REQUIRED:
   continue
  name=run["name"]
  if name not in by_name or (run.get("run_number",0),run.get("run_attempt",0))>(by_name[name].get("run_number",0),by_name[name].get("run_attempt",0)):
   by_name[name]=run
 missing=sorted(REQUIRED-by_name.keys())
 unmatched=sorted(REQUIRED-set(configured_names)) if configured_names is not None else []
 failures={n:(r.get("conclusion") or r.get("status") or "unknown") for n,r in by_name.items() if r.get("status")!="completed" or r.get("conclusion")!="success"}
 return {"release_sha":sha,"required_workflows":sorted(REQUIRED),
 "checks":{n:{"status":r.get("status"),"conclusion":r.get("conclusion"),"url":r.get("html_url")} for n,r in sorted(by_name.items())},
 "missing":missing,"workflow_name_mismatches":unmatched,"not_successful":failures,
 "ci_verdict":"PASS" if not missing and not failures and not unmatched else "BLOCKED",
 "production_approved":False,"generated_at_utc":datetime.now(timezone.utc).isoformat()}

def fetch_all(repo,sha,token):
 runs=[]
 for page in range(1,11):
  url=f"https://api.github.com/repos/{repo}/actions/runs?head_sha={sha}&per_page=100&page={page}"
  req=urllib.request.Request(url,headers={"Authorization":f"Bearer {token}","Accept":"application/vnd.github+json","X-GitHub-Api-Version":"2022-11-28"})
  with urllib.request.urlopen(req,timeout=20) as response:
   batch=json.load(response).get("workflow_runs",[])
  runs.extend(batch)
  if len(batch)<100:break
 else:
  raise ValueError("GitHub workflow run pagination exceeded verified limit")
 return runs

def fetch_workflow_names(repo,token):
 names=set()
 for page in range(1,11):
  url=f"https://api.github.com/repos/{repo}/actions/workflows?per_page=100&page={page}"
  req=urllib.request.Request(url,headers={"Authorization":f"Bearer {token}","Accept":"application/vnd.github+json","X-GitHub-Api-Version":"2022-11-28"})
  with urllib.request.urlopen(req,timeout=20) as response:
   batch=json.load(response).get("workflows",[])
  names.update(w.get("name") for w in batch if w.get("state")=="active" and w.get("name"))
  if len(batch)<100:break
 else:
  raise ValueError("GitHub workflow listing exceeded verified limit")
 return names

def is_main_ancestor(repo,sha,token):
 """Allow current main HEAD or an earlier commit on main, but not unrelated refs."""
 url=f"https://api.github.com/repos/{repo}/compare/{sha}...main"
 req=urllib.request.Request(url,headers={"Authorization":f"Bearer {token}","Accept":"application/vnd.github+json","X-GitHub-Api-Version":"2022-11-28"})
 with urllib.request.urlopen(req,timeout=20) as response:
  result=json.load(response)
 return result.get("status") in ("ahead","identical")

def main():
 repo=os.environ["GITHUB_REPOSITORY"]
 sha=os.environ.get("TARGET_RELEASE_SHA") or os.environ["GITHUB_SHA"]
 if not re.fullmatch(r"[0-9a-fA-F]{40}",sha):
  raise ValueError("Release SHA must be an exact 40-character Git commit hash")
 sha=sha.lower()
 token=os.environ["GH_TOKEN"]
 try:
  runs=fetch_all(repo,sha,token)
  configured=fetch_workflow_names(repo,token)
  report=evaluate(runs,sha,configured)
  report['commit_on_main']=is_main_ancestor(repo,sha,token)
  if not report['commit_on_main']:
   report['ci_verdict']='BLOCKED'
 except (urllib.error.URLError,TimeoutError,ValueError,OSError) as exc:
  report=evaluate([],sha,[])
  report["commit_on_main"]=False
  report["evidence_error"]=f"{type(exc).__name__}: evidence retrieval failed"
  report["ci_verdict"]="BLOCKED"
 out=Path("release-evidence")
 out.mkdir(exist_ok=True)
 (out/"consolidated.json").write_text(json.dumps(report,indent=2)+"\n")
 lines=["# LFM CI release gate","",f"Commit: `{sha}`",f"CI result: **{report['ci_verdict']}**","Production approval: **NOT GRANTED**","",
 "| Workflow | Status | Conclusion | Evidence |","|---|---|---|---|"]
 for name in sorted(REQUIRED):
  item=report["checks"].get(name,{})
  lines.append(f"| {name} | {item.get('status','missing')} | {item.get('conclusion','unverified')} | {item.get('url') or '—'} |")
 lines+=["",f"Selected commit on main history: {report.get(\'commit_on_main\',False)}",f"Configured workflow name mismatches: {', '.join(report['workflow_name_mismatches']) or 'none'}","This report checks only matching push runs for the exact commit; it does not verify database backups, actual deployment, or business approval."]
 (out/"consolidated.md").write_text("\n".join(lines)+"\n")
 print(json.dumps(report,indent=2))
 if report["ci_verdict"]!="PASS":sys.exit(1)

if __name__=="__main__":main()
