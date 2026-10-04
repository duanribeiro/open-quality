"""GitHub Projects v2 provider for Open Quality work management."""

from __future__ import annotations

import json
import os
from dataclasses import asdict, dataclass, field
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import Request, urlopen


@dataclass(frozen=True)
class Config:
    name: str
    owner: str
    project: str
    owner_type: str = "organization"
    base_url: str = "https://api.github.com"

    def token(self) -> str:
        if not (token := os.getenv("GITHUB_TOKEN")):
            raise ValueError("environment variable GITHUB_TOKEN is empty")
        return token


def load_config(raw: dict, role: str = "") -> Config:
    try:
        if raw.get("provider") != "github" or set(raw) - {"provider", "config", "description"}:
            raise ValueError("target must contain provider: github, config and optional description")
        values = raw.get("config") or {}
        allowed = {"owner", "project", "ownerType", "baseURL"}
        if not isinstance(values, dict) or set(values) - allowed:
            raise ValueError("GitHub Projects config has an unknown field")
        if not all(isinstance(values.get(key), str) and values[key] for key in ("owner", "project")):
            raise ValueError("owner and project are required for GitHub Projects")
        owner_type = values.get("ownerType", "organization")
        if owner_type not in {"organization", "user"}:
            raise ValueError("ownerType must be organization or user")
        return Config(role or "workManagement", values["owner"], values["project"], owner_type, values.get("baseURL", "https://api.github.com"))
    except Exception as error:
        raise ValueError(f"GitHub Projects target: {error}") from error


@dataclass
class State:
    version: int
    provider: str
    target: str
    project_id: str = ""
    # Preserve draft issue references from older state files for compatibility.
    resources: dict[str, dict[str, str]] = field(default_factory=dict)


def load_state(path: str | Path, target: str) -> State:
    path = Path(path)
    if not path.exists():
        return State(1, "github-projects", target)
    raw = json.loads(path.read_text())
    if raw.get("provider") != "github-projects" or raw.get("target") != target:
        raise ValueError("state belongs to a different provider target")
    return State(raw.get("version", 1), raw["provider"], raw["target"], raw.get("project_id", ""), raw.get("resources", {}))


def save_state(path: str | Path, state: State) -> None:
    path = Path(path)
    path.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
    temp = path.with_name(path.name + ".tmp")
    temp.write_text(json.dumps(asdict(state), indent=2) + "\n")
    temp.replace(path)


class Client:
    def __init__(self, config: Config, token: str):
        self.config, self.token = config, token

    def query(self, query: str, variables: dict | None = None) -> dict:
        request = Request(self.config.base_url.rstrip("/") + "/graphql", data=json.dumps({"query": query, "variables": variables or {}}).encode(), headers={"Authorization": f"Bearer {self.token}", "Content-Type": "application/json"})
        try:
            with urlopen(request, timeout=30) as response:
                result = json.load(response)
        except HTTPError as error:
            raise ValueError(f"GitHub returned {error.code}: {error.read().decode()}") from error
        if result.get("errors"):
            raise ValueError("GitHub GraphQL error: " + "; ".join(item.get("message", "unknown error") for item in result["errors"]))
        return result.get("data", {})

    def ensure_project(self) -> str:
        owner_field = "organization" if self.config.owner_type == "organization" else "user"
        data = self.query(f"query($login:String!){{{owner_field}(login:$login){{id projectsV2(first:100){{nodes{{id title}}}}}}}}", {"login": self.config.owner})
        owner = data.get(owner_field)
        if not owner:
            raise ValueError(f"GitHub {self.config.owner_type} {self.config.owner!r} not found")
        found = next((p["id"] for p in owner["projectsV2"]["nodes"] if p["title"] == self.config.project), None)
        if found:
            return found
        data = self.query("mutation($owner:ID!,$title:String!){createProjectV2(input:{ownerId:$owner,title:$title}){projectV2{id}}}", {"owner": owner["id"], "title": self.config.project})
        return data["createProjectV2"]["projectV2"]["id"]


def apply(config: Config, state: State, save) -> None:
    client = Client(config, config.token())
    project_id = state.project_id or client.ensure_project()
    state.project_id = project_id
    save(state)
