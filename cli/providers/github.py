"""GitHub enforcement provider for development-stage policies."""
from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path
from urllib.error import HTTPError
from urllib.parse import quote
from urllib.request import Request, urlopen

import yaml

@dataclass(frozen=True)
class GitHubConfig:
    name: str
    owner: str
    repository: str
    visibility: str = "private"
    members_file: str = ""
    base_url: str = "https://api.github.com"

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
        allowed = {"owner", "repository", "visibility", "membersFile", "members", "baseURL"}
        if set(config) - allowed:
            raise ValueError("GitHub config has an unknown field")
        required = ["owner", "repository"]
        if any(not isinstance(config.get(key), str) or not config[key] for key in required):
            raise ValueError("owner and repository are required")
        visibility = config.get("visibility", "private")
        if visibility not in {"public", "private"}:
            raise ValueError("visibility must be public or private")
        return GitHubConfig(role or raw["provider"], config["owner"], config["repository"], visibility, config.get("membersFile", ""), config.get("baseURL", "https://api.github.com"))
    except Exception as error:
        raise ValueError(f"target {path}: {error}") from error


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
def apply(config: GitHubConfig, members: list[GitHubMember] | None = None) -> int:
    client = GitHubClient(config, config.token())
    client.ensure_repository()
    for member in members or []:
        client.invite_member(member)
    return 1
