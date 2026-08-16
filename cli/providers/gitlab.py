"""GitLab provider for development-stage policies."""
from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path
from urllib.error import HTTPError
from urllib.parse import quote
from urllib.request import Request, urlopen

import yaml

from ..model import Bundle, Resource
from .github import _regex


ACCESS_LEVELS = {"guest": 10, "reporter": 20, "developer": 30, "maintainer": 40}


@dataclass(frozen=True)
class GitLabConfig:
    name: str; base_url: str; project: str; default_branch: str = ""; development_policy: dict | None = None
    def token(self) -> str:
        token = os.getenv("GITLAB_TOKEN")
        if not token: raise ValueError("environment variable GITLAB_TOKEN is empty")
        return token


@dataclass(frozen=True)
class GitLabMember:
    role: str; username: str; access_level: str


def load_config(source: str | Path | dict, role: str = "") -> GitLabConfig:
    try:
        raw = (source if isinstance(source, dict) else yaml.safe_load(Path(source).read_text())) or {}; cfg = raw.get("config") or {}
        if raw.get("provider") != "gitlab": raise ValueError("provider must be gitlab")
        if set(raw) - {"provider", "config", "description"}: raise ValueError("target has an unknown field")
        if set(cfg) - {"baseURL", "project", "defaultBranch", "members", "developmentPolicy"}: raise ValueError("GitLab config has an unknown field")
        if any(not cfg.get(key) for key in ("baseURL", "project")): raise ValueError("baseURL and project are required")
        policy = cfg.get("developmentPolicy")
        if policy is not None and not isinstance(policy, dict): raise ValueError("developmentPolicy must be a mapping")
        return GitLabConfig(role or raw["provider"], cfg["baseURL"], cfg["project"], cfg.get("defaultBranch", ""), policy)
    except Exception as error: raise ValueError(f"target {source}: {error}") from error


def load_members(raw: dict) -> list[GitLabMember]:
    members = []
    for item in raw.get("members", []):
        if set(item) - {"role", "usernames", "accessLevel"}: raise ValueError("GitLab member contains an unknown field")
        role, usernames, access = item.get("role"), item.get("usernames"), item.get("accessLevel")
        if not isinstance(role, str) or not isinstance(usernames, list) or access not in ACCESS_LEVELS: raise ValueError("GitLab member requires role, usernames and accessLevel")
        if not all(isinstance(username, str) and username for username in usernames): raise ValueError("GitLab usernames must be non-empty strings")
        members.extend(GitLabMember(role, username, access) for username in usernames)
    return members


def policy(config: GitLabConfig) -> dict[str, object] | None:
    if not config.development_policy: return None
    commits = config.development_policy.get("commits", {})
    return {"branch": _regex(config.development_policy.get("branch", {}).get("pattern", ".+"), []), "commits": _regex(commits.get("pattern", ".+"), commits.get("requiredTypes", []))}


def pipeline(policy: dict[str, object]) -> str:
    return f'''stages: [open_quality]

open_quality_development_policy:
  stage: open_quality
  rules:
    - if: '$CI_PIPELINE_SOURCE == "merge_request_event"'
  script:
    - |
      set -eu
      [[ "$CI_MERGE_REQUEST_SOURCE_BRANCH_NAME" =~ {policy["branch"]} ]] || {{ echo "branch name violates Open Quality policy"; exit 1; }}
      git log --format=%B "$CI_MERGE_REQUEST_DIFF_BASE_SHA..$CI_COMMIT_SHA" | awk 'NF' | while IFS= read -r commit; do
        [[ "$commit" =~ {policy["commits"]} ]] || {{ echo "commit violates Open Quality policy: $commit"; exit 1; }}
      done
'''


class GitLabClient:
    def __init__(self, config: GitLabConfig, token: str): self.config, self.token = config, token
    def request(self, method: str, path: str, body: dict | None = None) -> dict | list:
        request = Request(self.config.base_url.rstrip("/") + path, method=method, data=json.dumps(body).encode() if body is not None else None, headers={"PRIVATE-TOKEN": self.token, "Content-Type": "application/json"})
        try:
            with urlopen(request, timeout=30) as response:
                payload = response.read(); return json.loads(payload) if payload else {}
        except HTTPError as error: raise ValueError(f"GitLab returned {error.code}: {error.read().decode()}") from error
    @property
    def project_path(self) -> str: return "/projects/" + quote(self.config.project, safe="")
    def project(self) -> dict: return self.request("GET", self.project_path)  # type: ignore[return-value]
    def put_file(self, project_id: int, branch: str, content: str) -> None:
        path = f"/projects/{project_id}/repository/files/{quote('.gitlab-ci.yml', safe='')}"; body = {"branch": branch, "content": content, "commit_message": "chore: enforce Open Quality development policy"}
        try: self.request("GET", path + f"?ref={quote(branch)}"); method = "PUT"
        except ValueError as error:
            if "404" not in str(error): raise
            method = "POST"
        self.request(method, path, body)
    def configure_merge_policy(self, project_id: int) -> None:
        self.request("PUT", f"/projects/{project_id}", {"only_allow_merge_if_pipeline_succeeds": True, "only_allow_merge_if_all_discussions_are_resolved": True})
    def invite_member(self, project_id: int, member: GitLabMember) -> None:
        users = self.request("GET", f"/users?username={quote(member.username)}")
        if not isinstance(users, list) or not users: raise ValueError(f"GitLab user not found: {member.username}")
        self.request("POST", f"/projects/{project_id}/members", {"user_id": users[0]["id"], "access_level": ACCESS_LEVELS[member.access_level]})


def apply(bundle: Bundle, config: GitLabConfig, members: list[GitLabMember]) -> int:
    client = GitLabClient(config, config.token()); project = client.project(); branch = config.default_branch or project["default_branch"]
    policy_value = policy(config)
    if not policy_value: raise ValueError("source control provider has no developmentPolicy")
    client.put_file(project["id"], branch, pipeline(policy_value))
    client.configure_merge_policy(project["id"])
    for member in members: client.invite_member(project["id"], member)
    return 1
