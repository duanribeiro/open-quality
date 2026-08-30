"""Jira Cloud provider using the Jira REST API v3."""
from __future__ import annotations

import base64
import hashlib
import json
import os
from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Callable
from urllib.error import HTTPError
from urllib.parse import quote
from urllib.request import Request, urlopen

import yaml

from ..model import Bundle, Resource
from .openproject import ExternalResource, Operation
from ..core import quality_requirements


@dataclass
class JiraConfig:
    provider: str; name: str; base_url: str; project_key: str; template_key: str; issue_type: str; members_file: str = ""; columns: list[str] = field(default_factory=list)
    def credentials(self) -> tuple[str, str]:
        email, token = os.getenv("JIRA_EMAIL"), os.getenv("JIRA_API_TOKEN")
        if not email or not token: raise ValueError("JIRA_EMAIL and JIRA_API_TOKEN are required for apply")
        return email, token

def load_config(path: str | Path | dict, role: str = "") -> JiraConfig:
    raw = (path if isinstance(path, dict) else yaml.safe_load(Path(path).read_text())) or {}; cfg = raw.get("config") or {}
    try:
        if raw.get("provider") != "jira-cloud": raise ValueError("provider must be jira-cloud")
        if set(raw) - {"provider", "config", "description"}: raise ValueError("provider has an unknown field")
        if set(cfg) - {"baseURL", "projectKey", "projectTemplateKey", "issueTypeName", "membersFile", "members", "kanban"}: raise ValueError("Jira config has an unknown field")
        required = ["baseURL", "projectKey"]
        if any(not cfg.get(key) for key in required): raise ValueError("baseURL and projectKey are required")
        kanban = cfg.get("kanban") or {}; columns = kanban.get("columns", [])
        if not isinstance(columns, list) or not all(isinstance(x, str) and x for x in columns): raise ValueError("kanban.columns must be a list of strings")
        return JiraConfig("jira-cloud", role or raw["provider"], cfg["baseURL"], cfg["projectKey"], cfg.get("projectTemplateKey", "com.pyxis.greenhopper.jira:gh-kanban-template"), cfg.get("issueTypeName", "Task"), cfg.get("membersFile", ""), columns)
    except Exception as error: raise ValueError(f"target {path}: {error}") from error

@dataclass(frozen=True)
class JiraMember: role: str; email: str; jira_role: str
def load_members(path: str | Path | dict) -> list[JiraMember]:
    raw = (path if isinstance(path, dict) else yaml.safe_load(Path(path).read_text())) or {}
    if raw.get("provider") != "jira-cloud": raise ValueError("members provider must be jira-cloud")
    result=[]
    for item in raw.get("members", []):
        for email in item.get("emails", []): result.append(JiraMember(item["role"], email, item["jiraProjectRole"]))
    return result

@dataclass
class JiraState:
    version: int; provider: str; target: str; resources: dict[str, ExternalResource] = field(default_factory=dict)
def load_state(path: str | Path, target: str) -> JiraState:
    p=Path(path)
    if not p.exists(): return JiraState(1,"jira-cloud",target)
    raw=json.loads(p.read_text())
    if raw.get("provider") != "jira-cloud" or raw.get("target") != target: raise ValueError("state belongs to another provider or target")
    return JiraState(raw.get("version",1),raw["provider"],raw["target"],{k:ExternalResource(**v) for k,v in raw.get("resources",{}).items()})
def save_state(path: str | Path, state: JiraState) -> None:
    p=Path(path); p.parent.mkdir(mode=0o700, parents=True,exist_ok=True); temporary=p.with_name(p.name+".tmp"); temporary.write_text(json.dumps({"version":state.version,"provider":state.provider,"target":state.target,"resources":{k:asdict(v) for k,v in state.resources.items()}},indent=2)+"\n"); temporary.replace(p)

def _op(state:JiraState,rid:str,kind:str,subject:str,parent:str="",data:dict[str,str]|None=None)->Operation:
    data=data or {}; digest=hashlib.sha256(json.dumps([kind,subject,parent,data],sort_keys=True).encode()).hexdigest(); action="no-op" if rid in state.resources and state.resources[rid].hash==digest else "update" if rid in state.resources else "create"; return Operation(action,rid,kind,subject,"",parent,digest,data)
def plan(bundle:Bundle,state:JiraState,config:JiraConfig,members:list[JiraMember])->list[Operation]:
    assert bundle.project; workflow=bundle.workflows[bundle.project.spec["workflow"]]; ops=[_op(state,bundle.project.id,"QualityContract",bundle.project.name,data={"key":config.project_key})]
    if workflow.spec["stages"]:
        ops.append(_op(state,"kanban:"+bundle.project.id,"KanbanBoard",bundle.project.name,bundle.project.id,{"key":config.project_key,"columns":json.dumps(config.columns)}))
        ops += [_op(state,"member:"+m.email,"ProjectMember",m.email,bundle.project.id,{"email":m.email,"role":m.jira_role}) for m in members]
    for rid in quality_requirements(bundle.project): ops.append(_op(state,rid,"QualityRequirement",bundle.requirements[rid].name,bundle.project.id))
    for rid in workflow.spec["stages"]: ops.append(_op(state,rid,"Stage",bundle.stages[rid].name,bundle.project.id))
    return ops

class JiraClient:
 def __init__(self,c:JiraConfig,email:str,token:str): self.c=c; self.auth="Basic "+base64.b64encode(f"{email}:{token}".encode()).decode()
 def req(self,method:str,path:str,body:dict|None=None)->dict:
  q=Request(self.c.base_url.rstrip("/")+path,method=method,data=json.dumps(body).encode() if body else None,headers={"Authorization":self.auth,"Accept":"application/json","Content-Type":"application/json"})
  try:
   with urlopen(q,timeout=30) as r: return json.load(r) if r.readable() and r.length != 0 else {}
  except HTTPError as e: raise ValueError(f"Jira returned {e.code} {e.reason}: {e.read().decode()}") from e
 def project(self,key:str)->dict|None:
  try:return self.req("GET","/rest/api/3/project/"+quote(key))
  except ValueError as e:
   if "404" in str(e): return None
   raise
 def invite(self,email:str)->str:
  try: return self.req("POST","/rest/api/3/user",{"emailAddress":email,"products":["jira-software"]})["accountId"]
  except ValueError as e:
   if "already" not in str(e).lower(): raise
   users=self.req("GET","/rest/api/3/user/assignable/search?project="+quote(self.c.project_key)+"&query="+quote(email)); return next(u["accountId"] for u in users if u.get("emailAddress","").lower()==email.lower())
 def ensure_kanban_board(self,name:str)->tuple[int,str]:
  boards=self.req("GET","/rest/agile/1.0/board?projectKeyOrId="+quote(self.c.project_key)+"&name="+quote(name))
  for board in boards.get("values",[]):
   if board.get("name")==name:
    return int(board["id"]),board.get("self",f"/rest/agile/1.0/board/{board['id']}").replace(self.c.base_url,"")
  filter_result=self.req("POST","/rest/api/3/filter",{"name":f"Open Quality: {name}","jql":f"project = {self.c.project_key} ORDER BY Rank ASC"})
  board=self.req("POST","/rest/agile/1.0/board",{"name":name,"type":"kanban","filterId":int(filter_result["id"]),"location":{"type":"project","projectKeyOrId":self.c.project_key}})
  return int(board["id"]),board.get("self",f"/rest/agile/1.0/board/{board['id']}").replace(self.c.base_url,"")

def apply(ops:list[Operation],state:JiraState,client:JiraClient,config:JiraConfig,checkpoint:Callable[[JiraState],None]|None=None)->JiraState:
 for op in ops:
  if op.action=="no-op": continue
  try:
   if op.kind=="QualityContract":
    current=client.project(config.project_key); result=current or client.req("POST","/rest/api/3/project",{"key":config.project_key,"name":op.subject,"projectTypeKey":"software","projectTemplateKey":config.template_key,"leadAccountId":client.req("GET","/rest/api/3/myself")["accountId"]}); eid=int(result["id"]); href="/rest/api/3/project/"+config.project_key
   elif op.kind=="KanbanBoard": eid,href=client.ensure_kanban_board(op.subject)
   elif op.kind=="ProjectMember":
    aid=client.invite(op.data["email"]); roles=client.req("GET",f"/rest/api/3/project/{config.project_key}/role"); url=roles.get(op.data["role"])
    if not url:
     expected=op.data["role"].casefold().rstrip("s")
     url=next((href for name,href in roles.items() if name.casefold().rstrip("s")==expected),None)
    if not url: raise ValueError(f"Jira project role not found: {op.data['role']}; available: {', '.join(roles)}")
    client.req("POST",url.replace(config.base_url,""),{"user":[aid]}); eid=0; href=url
   else:
    issue=client.req("POST","/rest/api/3/issue",{"fields":{"project":{"key":config.project_key},"summary":op.subject,"issuetype":{"name":config.issue_type}}}); eid=int(issue["id"]); href="/rest/api/3/issue/"+issue["id"]
   state.resources[op.resource_id]=ExternalResource(op.resource_id,op.kind,eid,href,op.hash,datetime.now(UTC).isoformat())
   if checkpoint: checkpoint(state)
  except ValueError as e: raise ValueError(f"{op.action} {op.kind} {op.subject!r}: {e}") from e
 return state
