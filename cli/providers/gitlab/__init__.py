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

ACCESS_LEVELS = {"guest": 10, "reporter": 20, "developer": 30, "maintainer": 40}


@dataclass(frozen=True)
class GitLabConfig:
    name: str
    base_url: str
    project: str

    def token(self) -> str:
        """Return the GITLAB_TOKEN environment variable, or raise if unset."""
        token = os.getenv("GITLAB_TOKEN")
        if not token:
            raise ValueError("environment variable GITLAB_TOKEN is empty")
        return token


@dataclass(frozen=True)
class GitLabMember:
    role: str
    username: str
    access_level: str


def load_config(source: str | Path | dict, role: str = "") -> GitLabConfig:
    """Load and validate a GitLab provider target from a path or inline mapping."""
    try:
        raw = (
            source
            if isinstance(source, dict)
            else yaml.safe_load(Path(source).read_text())
        ) or {}
        cfg = raw.get("config") or {}
        if raw.get("provider") != "gitlab":
            raise ValueError("provider must be gitlab")
        if set(raw) - {"provider", "config", "description"}:
            raise ValueError("target has an unknown field")
        if set(cfg) - {"baseURL", "project", "members"}:
            raise ValueError("GitLab config has an unknown field")
        if any(not cfg.get(key) for key in ("baseURL", "project")):
            raise ValueError("baseURL and project are required")
        return GitLabConfig(role or raw["provider"], cfg["baseURL"], cfg["project"])
    except Exception as error:
        raise ValueError(f"target {source}: {error}") from error


def load_members(raw: dict) -> list[GitLabMember]:
    """Parse the inline `members` list of a GitLab target config."""
    members = []
    for item in raw.get("members", []):
        if set(item) - {"role", "usernames", "accessLevel"}:
            raise ValueError("GitLab member contains an unknown field")
        role, usernames, access = (
            item.get("role"),
            item.get("usernames"),
            item.get("accessLevel"),
        )
        if (
            not isinstance(role, str)
            or not isinstance(usernames, list)
            or access not in ACCESS_LEVELS
        ):
            raise ValueError("GitLab member requires role, usernames and accessLevel")
        if not all(isinstance(username, str) and username for username in usernames):
            raise ValueError("GitLab usernames must be non-empty strings")
        members.extend(GitLabMember(role, username, access) for username in usernames)
    return members


class GitLabClient:
    def __init__(self, config: GitLabConfig, token: str):
        """Store the target config and API token used by every request."""
        self.config, self.token = config, token

    def request(self, method: str, path: str, body: dict | None = None) -> dict | list:
        """Send one authenticated GitLab REST API request and return its JSON body."""
        request = Request(
            self.config.base_url.rstrip("/") + path,
            method=method,
            data=json.dumps(body).encode() if body is not None else None,
            headers={"PRIVATE-TOKEN": self.token, "Content-Type": "application/json"},
        )
        try:
            with urlopen(request, timeout=30) as response:
                payload = response.read()
                return json.loads(payload) if payload else {}
        except HTTPError as error:
            raise ValueError(
                f"GitLab returned {error.code}: {error.read().decode()}"
            ) from error

    @property
    def project_path(self) -> str:
        """Return the API path for the configured project."""
        return "/projects/" + quote(self.config.project, safe="")

    def project(self) -> dict:
        """Fetch the configured GitLab project."""
        return self.request("GET", self.project_path)  # type: ignore[return-value]

    def invite_member(self, project_id: int, member: GitLabMember) -> None:
        """Add `member` to the project at the given access level."""
        users = self.request("GET", f"/users?username={quote(member.username)}")
        if not isinstance(users, list) or not users:
            raise ValueError(f"GitLab user not found: {member.username}")
        self.request(
            "POST",
            f"/projects/{project_id}/members",
            {
                "user_id": users[0]["id"],
                "access_level": ACCESS_LEVELS[member.access_level],
            },
        )


def apply(config: GitLabConfig, members: list[GitLabMember]) -> int:
    """Ensure the project exists and invite every member; return projects touched."""
    client = GitLabClient(config, config.token())
    project = client.project()
    for member in members:
        client.invite_member(project["id"], member)
    return 1
