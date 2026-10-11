"""GitHub Projects provider for Open Quality work management."""

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
        if raw.get("provider") != "github" or set(raw) - {
            "provider",
            "config",
            "description",
        }:
            raise ValueError(
                "target must contain provider: github, config and optional description"
            )
        values = raw.get("config") or {}
        allowed = {"owner", "project", "ownerType", "baseURL"}
        if not isinstance(values, dict) or set(values) - allowed:
            raise ValueError("GitHub Projects config has an unknown field")
        if not all(
            isinstance(values.get(key), str) and values[key]
            for key in ("owner", "project")
        ):
            raise ValueError("owner and project are required for GitHub Projects")
        owner_type = values.get("ownerType", "organization")
        if owner_type not in {"organization", "user"}:
            raise ValueError("ownerType must be organization or user")
        return Config(
            role or "workManagement",
            values["owner"],
            values["project"],
            owner_type,
            values.get("baseURL", "https://api.github.com"),
        )
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
    project_number: int = 0


def load_state(path: str | Path, target: str) -> State:
    path = Path(path)
    if not path.exists():
        return State(1, "github-projects", target)
    raw = json.loads(path.read_text())
    if raw.get("provider") != "github-projects" or raw.get("target") != target:
        raise ValueError("state belongs to a different provider target")
    return State(
        raw.get("version", 1),
        raw["provider"],
        raw["target"],
        raw.get("project_id", ""),
        raw.get("resources", {}),
        raw.get("project_number", 0),
    )


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
        request = Request(
            self.config.base_url.rstrip("/") + "/graphql",
            data=json.dumps({"query": query, "variables": variables or {}}).encode(),
            headers={
                "Authorization": f"Bearer {self.token}",
                "Content-Type": "application/json",
            },
        )
        try:
            with urlopen(request, timeout=30) as response:
                result = json.load(response)
        except HTTPError as error:
            raise ValueError(
                f"GitHub returned {error.code}: {error.read().decode()}"
            ) from error
        if result.get("errors"):
            raise ValueError(
                "GitHub GraphQL error: "
                + "; ".join(
                    item.get("message", "unknown error") for item in result["errors"]
                )
            )
        return result.get("data", {})

    def rest(self, method: str, path: str, body: dict | None = None):
        request = Request(
            self.config.base_url.rstrip("/") + path,
            method=method,
            data=json.dumps(body).encode() if body is not None else None,
            headers={
                "Authorization": f"Bearer {self.token}",
                "Accept": "application/vnd.github+json",
                "X-GitHub-Api-Version": "2022-11-28",
                "Content-Type": "application/json",
            },
        )
        try:
            with urlopen(request, timeout=30) as response:
                return json.load(response)
        except HTTPError as error:
            raise ValueError(
                f"GitHub returned {error.code}: {error.read().decode()}"
            ) from error

    def owner(self) -> dict:
        owner_field = (
            "organization" if self.config.owner_type == "organization" else "user"
        )
        data = self.query(
            f"query($login:String!){{{owner_field}(login:$login){{id databaseId projectsV2(first:100){{nodes{{id title number}}}}}}}}",
            {"login": self.config.owner},
        )
        owner = data.get(owner_field)
        if not owner:
            raise ValueError(
                f"GitHub {self.config.owner_type} {self.config.owner!r} not found"
            )
        return owner

    def ensure_project(self) -> tuple[str, int, dict]:
        owner = self.owner()
        found = next(
            (
                p
                for p in owner["projectsV2"]["nodes"]
                if p["title"] == self.config.project
            ),
            None,
        )
        if found:
            return found["id"], found["number"], owner
        data = self.query(
            "mutation($owner:ID!,$title:String!){createProjectV2(input:{ownerId:$owner,title:$title}){projectV2{id number}}}",
            {"owner": owner["id"], "title": self.config.project},
        )
        project = data["createProjectV2"]["projectV2"]
        return project["id"], project["number"], owner

    def ensure_workflow_field(self, project_id: str, stage_ids: list[str]) -> dict:
        project = self.query(
            "query($id:ID!){node(id:$id){... on ProjectV2{fields(first:100){nodes{__typename ... on ProjectV2FieldCommon{id name} ... on ProjectV2SingleSelectField{id name databaseId options{id name color description}}}}}}}",
            {"id": project_id},
        )["node"]
        field_data = next(
            (
                item
                for item in project["fields"]["nodes"]
                if item.get("name") == "Open Quality Stage"
            ),
            None,
        )
        if field_data and field_data.get("__typename") != "ProjectV2SingleSelectField":
            raise ValueError(
                "GitHub project field 'Open Quality Stage' exists but is not a single-select field"
            )
        existing = {
            item["name"]: item for item in (field_data or {}).get("options", [])
        }
        options = []
        for stage_id in stage_ids:
            option = {
                "name": stage_id,
                "color": "GRAY",
                "description": "Open Quality workflow stage",
            }
            if stage_id in existing:
                option["id"] = existing[stage_id]["id"]
            options.append(option)
        if field_data:
            result = self.query(
                "mutation($id:ID!,$options:[ProjectV2SingleSelectFieldOptionInput!]!){updateProjectV2Field(input:{fieldId:$id,singleSelectOptions:$options}){projectV2Field{... on ProjectV2SingleSelectField{id databaseId name options{id name}}}}}",
                {"id": field_data["id"], "options": options},
            )
            return result["updateProjectV2Field"]["projectV2Field"]
        result = self.query(
            'mutation($project:ID!,$options:[ProjectV2SingleSelectFieldOptionInput!]!){createProjectV2Field(input:{projectId:$project,name:"Open Quality Stage",dataType:SINGLE_SELECT,singleSelectOptions:$options}){projectV2Field{... on ProjectV2SingleSelectField{id databaseId name options{id name}}}}}',
            {"project": project_id, "options": options},
        )
        return result["createProjectV2Field"]["projectV2Field"]

    def ensure_board_view(
        self, project_id: str, project_number: int, owner: dict, field_id: int
    ) -> None:
        if self.config.owner_type == "organization":
            path = f"/orgs/{self.config.owner}/projectsV2/{project_number}/views"
        else:
            path = f"/users/{self.config.owner}/projectsV2/{project_number}/views"
        views = self.query(
            "query($id:ID!){node(id:$id){... on ProjectV2{views(first:100){nodes{name layout}}}}}",
            {"id": project_id},
        )["node"]["views"]["nodes"]
        if any(
            view.get("name") == "Open Quality workflow"
            and view.get("layout") == "BOARD_LAYOUT"
            for view in views
        ):
            return
        try:
            self.rest(
                "POST",
                path,
                {
                    "name": "Open Quality workflow",
                    "layout": "board",
                    "vertical_group_by": [field_id],
                },
            )
        except ValueError as error:
            raise ValueError(
                f"Could not create GitHub Projects board view at {path}. "
                "The project and stage field may already exist; rerun oq apply after "
                "checking the owner, project number and token access. "
                f"{error}"
            ) from error


def apply(config: Config, state: State, stage_ids: list[str], save) -> None:
    client = Client(config, config.token())
    if state.project_id and state.project_number:
        project_id, project_number, owner = (
            state.project_id,
            state.project_number,
            client.owner(),
        )
    else:
        project_id, project_number, owner = client.ensure_project()
    state.project_id = project_id
    state.project_number = project_number
    save(state)
    if stage_ids:
        field_data = client.ensure_workflow_field(project_id, stage_ids)
        client.ensure_board_view(
            project_id, project_number, owner, field_data["databaseId"]
        )
        save(state)
