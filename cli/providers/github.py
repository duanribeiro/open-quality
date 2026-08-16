"""GitHub enforcement provider for development-stage policies."""
from __future__ import annotations

import base64
import json
import os
import re
from dataclasses import dataclass
from pathlib import Path
from urllib.error import HTTPError
from urllib.parse import quote
from urllib.request import Request, urlopen

import yaml

from ..model import Bundle, Resource


@dataclass(frozen=True)
class GitHubConfig:
    name: str
    owner: str
    repository: str
    default_branch: str = ""
    visibility: str = "private"
    members_file: str = ""
    base_url: str = "https://api.github.com"
    development_policy: dict | None = None

    def token(self) -> str:
        token = os.getenv("GITHUB_TOKEN")
        if not token:
            raise ValueError("environment variable GITHUB_TOKEN is empty")
        return token


def load_config(path: str | Path | dict, role: str = "") -> GitHubConfig:
    try:
        raw = (path if isinstance(path, dict) else yaml.safe_load(Path(path).read_text())) or {}
        config = raw.get("config") or {}
        if raw.get("provider") != "github":
            raise ValueError("provider must be github")
        if set(raw) - {"provider", "config", "description"}:
            raise ValueError("target has an unknown field")
        allowed = {"owner", "repository", "defaultBranch", "visibility", "membersFile", "members", "baseURL", "developmentPolicy"}
        if set(config) - allowed:
            raise ValueError("GitHub config has an unknown field")
        required = ["owner", "repository"]
        if any(not isinstance(config.get(key), str) or not config[key] for key in required):
            raise ValueError("owner and repository are required")
        visibility = config.get("visibility", "private")
        if visibility not in {"public", "private"}:
            raise ValueError("visibility must be public or private")
        policy = config.get("developmentPolicy")
        if policy is not None and not isinstance(policy, dict):
            raise ValueError("developmentPolicy must be a mapping")
        return GitHubConfig(role or raw["provider"], config["owner"], config["repository"], config.get("defaultBranch", ""), visibility, config.get("membersFile", ""), config.get("baseURL", "https://api.github.com"), policy)
    except Exception as error:
        raise ValueError(f"target {path}: {error}") from error


def _regex(template: str, types: list[str]) -> str:
    tokens = {
        "{issueKey}": r"[A-Z][A-Z0-9]+-[0-9]+",
        "{slug}": r"[a-z0-9]+(-[a-z0-9]+)*",
        "{type}": "(" + "|".join(re.escape(item) for item in types) + ")",
        "{scope}": r"[A-Za-z0-9._/-]+",
        "{description}": r".+",
    }
    parts: list[str] = []
    cursor = 0
    for match in re.finditer(r"\{(?:issueKey|slug|type|scope|description)\}", template):
        parts.append(re.escape(template[cursor:match.start()]).replace(r"\ ", " "))
        parts.append(tokens[match.group()])
        cursor = match.end()
    parts.append(re.escape(template[cursor:]).replace(r"\ ", " "))
    return "^" + "".join(parts) + "$"


@dataclass(frozen=True)
class GitHubMember:
    role: str
    username: str
    permission: str


def load_members(path: str | Path | dict) -> list[GitHubMember]:
    try:
        raw = (path if isinstance(path, dict) else yaml.safe_load(Path(path).read_text())) or {}
        if raw.get("provider") != "github" or set(raw) - {"provider", "members"}:
            raise ValueError("must contain only provider: github and members")
        members = []
        for item in raw.get("members", []):
            if set(item) - {"role", "usernames", "permission"}:
                raise ValueError("member contains an unknown field")
            role, usernames, permission = item.get("role"), item.get("usernames"), item.get("permission")
            if not isinstance(role, str) or not isinstance(usernames, list) or permission not in {"pull", "push", "triage", "maintain", "admin"}:
                raise ValueError("member requires role, usernames and a valid permission")
            members.extend(GitHubMember(role, username, permission) for username in usernames if isinstance(username, str) and username)
        return members
    except Exception as error:
        raise ValueError(f"members {path}: {error}") from error


def policy(config: GitHubConfig) -> dict[str, object] | None:
    if not config.development_policy:
        return None
    commits = config.development_policy.get("commits", {})
    return {
        "branch": _regex(config.development_policy.get("branch", {}).get("pattern", ".+"), []),
        "commits": _regex(commits.get("pattern", ".+"), commits.get("requiredTypes", [])),
        "pullRequest": config.development_policy.get("pullRequest", {}).get("required", []),
    }


def workflow(policy: dict[str, object]) -> str:
    required = set(policy["pullRequest"])
    linked = "true" if "linkedIssue" in required else "false"
    description = "true" if "descriptionTemplate" in required else "false"
    return f'''name: Open Quality source control policy
on:
  pull_request:
    types: [opened, edited, synchronize, reopened]
permissions:
  contents: read
jobs:
  development-policy:
    name: Open Quality development policy
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0
      - name: Validate branch, commits and pull request
        env:
          BRANCH_PATTERN: '{policy["branch"]}'
          COMMIT_PATTERN: '{policy["commits"]}'
          REQUIRE_LINKED_ISSUE: '{linked}'
          REQUIRE_DESCRIPTION: '{description}'
          PR_BODY: ${{{{ github.event.pull_request.body }}}}
        run: |
          set -euo pipefail
          [[ "${{{{ github.head_ref }}}}" =~ $BRANCH_PATTERN ]] || {{ echo 'branch name violates Open Quality policy'; exit 1; }}
          git log --format=%B "origin/${{{{ github.base_ref }}}}..HEAD" | awk 'NF' | while IFS= read -r commit; do
            [[ "$commit" =~ $COMMIT_PATTERN ]] || {{ echo "commit violates Open Quality policy: $commit"; exit 1; }}
          done
          if [[ "$REQUIRE_LINKED_ISSUE" == true ]]; then grep -Eqi '(close|closes|closed|fix|fixes|fixed|resolve|resolves|resolved) #[0-9]+' <<< "$PR_BODY"; fi
          if [[ "$REQUIRE_DESCRIPTION" == true ]]; then [[ -n "${{PR_BODY//[[:space:]]/}}" ]]; fi
'''


class GitHubClient:
    def __init__(self, config: GitHubConfig, token: str): self.config, self.token = config, token
    def request(self, method: str, path: str, body: dict | None = None) -> dict:
        request = Request(self.config.base_url.rstrip("/") + path, method=method, data=json.dumps(body).encode() if body is not None else None, headers={"Accept": "application/vnd.github+json", "Authorization": f"Bearer {self.token}", "X-GitHub-Api-Version": "2022-11-28", "Content-Type": "application/json"})
        try:
            with urlopen(request, timeout=30) as response:
                return json.load(response) if response.length != 0 else {}
        except HTTPError as error:
            raise ValueError(f"GitHub returned {error.code}: {error.read().decode()}") from error
    @property
    def repository_path(self) -> str: return f"/repos/{quote(self.config.owner)}/{quote(self.config.repository)}"
    def ensure_repository(self) -> dict:
        try:
            return self.request("GET", self.repository_path)
        except ValueError as error:
            if "404" not in str(error):
                raise
        account = self.request("GET", "/user")
        payload = {"name": self.config.repository, "private": self.config.visibility == "private"}
        if account.get("login", "").casefold() == self.config.owner.casefold():
            return self.request("POST", "/user/repos", payload)
        return self.request("POST", f"/orgs/{quote(self.config.owner)}/repos", payload)
    def invite_member(self, member: GitHubMember) -> None:
        self.request("PUT", f"{self.repository_path}/collaborators/{quote(member.username)}", {"permission": member.permission})
    def put_file(self, path: str, content: str, branch: str) -> None:
        encoded_path = "/".join(quote(part) for part in path.split("/")); body = {"message": "chore: enforce Open Quality development policy", "content": base64.b64encode(content.encode()).decode(), "branch": branch}
        try: body["sha"] = self.request("GET", f"{self.repository_path}/contents/{encoded_path}?ref={quote(branch)}")["sha"]
        except ValueError as error:
            if "404" not in str(error): raise
        self.request("PUT", f"{self.repository_path}/contents/{encoded_path}", body)
    def upsert_ruleset(self, name: str, branch: str) -> None:
        body = {"name": name, "target": "branch", "enforcement": "active", "conditions": {"ref_name": {"include": [f"refs/heads/{branch}"], "exclude": []}}, "rules": [{"type": "pull_request", "parameters": {"dismiss_stale_reviews_on_push": False, "require_code_owner_review": False, "require_last_push_approval": False, "required_approving_review_count": 0, "required_review_thread_resolution": False}}, {"type": "required_status_checks", "parameters": {"required_status_checks": [{"context": "Open Quality development policy"}], "strict_required_status_checks_policy": True}}]}
        existing = next((item for item in self.request("GET", f"{self.repository_path}/rulesets") if item["name"] == name), None)
        self.request("PUT" if existing else "POST", f"{self.repository_path}/rulesets/{existing['id']}" if existing else f"{self.repository_path}/rulesets", body)


def apply(bundle: Bundle, config: GitHubConfig, members: list[GitHubMember] | None = None) -> int:
    client = GitHubClient(config, config.token()); repository = client.ensure_repository(); branch = config.default_branch or repository["default_branch"]
    policy_value = policy(config)
    if not policy_value:
        raise ValueError("source control provider has no developmentPolicy")
    client.put_file(".github/workflows/open-quality-source-control.yaml", workflow(policy_value), branch)
    client.upsert_ruleset("Open Quality source control policy", branch)
    for member in members or []:
        client.invite_member(member)
    return 1
