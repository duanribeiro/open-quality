"""Jira Cloud provider using the Jira REST API v3."""

from __future__ import annotations

import base64
import hashlib
import json
import os
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
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
    provider: str
    name: str
    base_url: str
    project_key: str
    template_key: str
    issue_type: str
    members_file: str = ""
    columns: list[str] = field(default_factory=list)

    def credentials(self) -> tuple[str, str]:
        """Return the (email, API token) pair, or raise if either is unset."""
        email, token = os.getenv("JIRA_EMAIL"), os.getenv("JIRA_API_TOKEN")
        if not email or not token:
            raise ValueError("JIRA_EMAIL and JIRA_API_TOKEN are required for apply")
        return email, token


def load_config(path: str | Path | dict, role: str = "") -> JiraConfig:
    """Load and validate a Jira Cloud provider target from a path or inline mapping."""
    raw = (
        path if isinstance(path, dict) else yaml.safe_load(Path(path).read_text())
    ) or {}
    cfg = raw.get("config") or {}
    try:
        if raw.get("provider") != "jira-cloud":
            raise ValueError("provider must be jira-cloud")
        if set(raw) - {"provider", "config", "description"}:
            raise ValueError("provider has an unknown field")
        if set(cfg) - {
            "baseURL",
            "projectKey",
            "projectTemplateKey",
            "issueTypeName",
            "membersFile",
            "members",
            "kanban",
        }:
            raise ValueError("Jira config has an unknown field")
        required = ["baseURL", "projectKey"]
        if any(not cfg.get(key) for key in required):
            raise ValueError("baseURL and projectKey are required")
        kanban = cfg.get("kanban") or {}
        columns = kanban.get("columns", [])
        if not isinstance(columns, list) or not all(
            isinstance(x, str) and x for x in columns
        ):
            raise ValueError("kanban.columns must be a list of strings")
        return JiraConfig(
            "jira-cloud",
            role or raw["provider"],
            cfg["baseURL"],
            cfg["projectKey"],
            cfg.get(
                "projectTemplateKey", "com.pyxis.greenhopper.jira:gh-kanban-template"
            ),
            cfg.get("issueTypeName", "Task"),
            cfg.get("membersFile", ""),
            columns,
        )
    except Exception as error:
        raise ValueError(f"target {path}: {error}") from error


@dataclass(frozen=True)
class JiraMember:
    role: str
    email: str
    jira_role: str


def load_members(path: str | Path | dict) -> list[JiraMember]:
    """Load Jira Cloud members from a path or inline mapping, one per email."""
    raw = (
        path if isinstance(path, dict) else yaml.safe_load(Path(path).read_text())
    ) or {}
    if raw.get("provider") != "jira-cloud":
        raise ValueError("members provider must be jira-cloud")
    result = []
    for item in raw.get("members", []):
        for email in item.get("emails", []):
            result.append(JiraMember(item["role"], email, item["jiraProjectRole"]))
    return result


@dataclass
class JiraState:
    version: int
    provider: str
    target: str
    resources: dict[str, ExternalResource] = field(default_factory=dict)


def load_state(path: str | Path, target: str) -> JiraState:
    """Load provider state from `path`, or start fresh state if it doesn't exist."""
    path = Path(path)
    if not path.exists():
        return JiraState(1, "jira-cloud", target)
    raw = json.loads(path.read_text())
    if raw.get("provider") != "jira-cloud" or raw.get("target") != target:
        raise ValueError("state belongs to another provider or target")
    return JiraState(
        raw.get("version", 1),
        raw["provider"],
        raw["target"],
        {
            key: ExternalResource(**value)
            for key, value in raw.get("resources", {}).items()
        },
    )


def save_state(path: str | Path, state: JiraState) -> None:
    """Atomically write provider state to `path` as JSON."""
    path = Path(path)
    path.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_text(
        json.dumps(
            {
                "version": state.version,
                "provider": state.provider,
                "target": state.target,
                "resources": {
                    key: asdict(value) for key, value in state.resources.items()
                },
            },
            indent=2,
        )
        + "\n"
    )
    temporary.replace(path)


def _operation(
    state: JiraState,
    resource_id: str,
    kind: str,
    subject: str,
    parent: str = "",
    data: dict[str, str] | None = None,
) -> Operation:
    """Build one Operation, diffing its digest against the resource in `state`."""
    data = data or {}
    digest = hashlib.sha256(
        json.dumps([kind, subject, parent, data], sort_keys=True).encode()
    ).hexdigest()
    action = (
        "no-op"
        if resource_id in state.resources
        and state.resources[resource_id].hash == digest
        else "update" if resource_id in state.resources else "create"
    )
    return Operation(action, resource_id, kind, subject, "", parent, digest, data)


def plan(
    bundle: Bundle, state: JiraState, config: JiraConfig, members: list[JiraMember]
) -> list[Operation]:
    """Compute the create/update/no-op operations for a bundle's Jira Cloud project."""
    assert bundle.project
    workflow = bundle.workflows[bundle.project.spec["workflow"]]
    operations = [
        _operation(
            state,
            bundle.project.id,
            "QualityContract",
            bundle.project.name,
            data={"key": config.project_key},
        )
    ]
    if workflow.spec["stages"]:
        operations.append(
            _operation(
                state,
                "kanban:" + bundle.project.id,
                "KanbanBoard",
                bundle.project.name,
                bundle.project.id,
                {"key": config.project_key, "columns": json.dumps(config.columns)},
            )
        )
        operations += [
            _operation(
                state,
                "member:" + member.email,
                "ProjectMember",
                member.email,
                bundle.project.id,
                {"email": member.email, "role": member.jira_role},
            )
            for member in members
        ]
    for resource_id in quality_requirements(bundle.project):
        operations.append(
            _operation(
                state,
                resource_id,
                "QualityRequirement",
                bundle.requirements[resource_id].name,
                bundle.project.id,
            )
        )
    for resource_id in workflow.spec["stages"]:
        operations.append(
            _operation(
                state,
                resource_id,
                "Stage",
                bundle.stages[resource_id].name,
                bundle.project.id,
            )
        )
    return operations


class JiraClient:
    def __init__(self, config: JiraConfig, email: str, token: str):
        """Store the target config and precompute the HTTP Basic auth header."""
        self.config = config
        self.auth = "Basic " + base64.b64encode(f"{email}:{token}".encode()).decode()

    def request(self, method: str, path: str, body: dict | None = None) -> dict:
        """Send one authenticated Jira Cloud REST API request and return its JSON body."""
        request = Request(
            self.config.base_url.rstrip("/") + path,
            method=method,
            data=json.dumps(body).encode() if body else None,
            headers={
                "Authorization": self.auth,
                "Accept": "application/json",
                "Content-Type": "application/json",
            },
        )
        try:
            with urlopen(request, timeout=30) as response:
                return (
                    json.load(response)
                    if response.readable() and response.length != 0
                    else {}
                )
        except HTTPError as error:
            raise ValueError(
                f"Jira returned {error.code} {error.reason}: {error.read().decode()}"
            ) from error

    def project(self, key: str) -> dict | None:
        """Fetch the Jira project by key, or None if it doesn't exist."""
        try:
            return self.request("GET", "/rest/api/3/project/" + quote(key))
        except ValueError as error:
            if "404" in str(error):
                return None
            raise

    def invite(self, email: str) -> str:
        """Invite `email` as a Jira user and return their account ID."""
        try:
            return self.request(
                "POST",
                "/rest/api/3/user",
                {"emailAddress": email, "products": ["jira-software"]},
            )["accountId"]
        except ValueError as error:
            if "already" not in str(error).lower():
                raise
            users = self.request(
                "GET",
                "/rest/api/3/user/assignable/search?project="
                + quote(self.config.project_key)
                + "&query="
                + quote(email),
            )
            return next(
                user["accountId"]
                for user in users
                if user.get("emailAddress", "").lower() == email.lower()
            )

    def ensure_kanban_board(self, name: str) -> tuple[int, str]:
        """Return the named Kanban board, creating its filter and board if needed."""
        boards = self.request(
            "GET",
            "/rest/agile/1.0/board?projectKeyOrId="
            + quote(self.config.project_key)
            + "&name="
            + quote(name),
        )
        for board in boards.get("values", []):
            if board.get("name") == name:
                return int(board["id"]), board.get(
                    "self", f"/rest/agile/1.0/board/{board['id']}"
                ).replace(self.config.base_url, "")
        filter_result = self.request(
            "POST",
            "/rest/api/3/filter",
            {
                "name": f"Open Quality: {name}",
                "jql": f"project = {self.config.project_key} ORDER BY Rank ASC",
            },
        )
        board = self.request(
            "POST",
            "/rest/agile/1.0/board",
            {
                "name": name,
                "type": "kanban",
                "filterId": int(filter_result["id"]),
                "location": {
                    "type": "project",
                    "projectKeyOrId": self.config.project_key,
                },
            },
        )
        return int(board["id"]), board.get(
            "self", f"/rest/agile/1.0/board/{board['id']}"
        ).replace(self.config.base_url, "")


def apply(
    operations: list[Operation],
    state: JiraState,
    client: JiraClient,
    config: JiraConfig,
    checkpoint: Callable[[JiraState], None] | None = None,
) -> JiraState:
    """Materialize each non-no-op operation in Jira Cloud, checkpointing state as it goes."""
    for operation in operations:
        if operation.action == "no-op":
            continue
        try:
            if operation.kind == "QualityContract":
                current = client.project(config.project_key)
                result = current or client.request(
                    "POST",
                    "/rest/api/3/project",
                    {
                        "key": config.project_key,
                        "name": operation.subject,
                        "projectTypeKey": "software",
                        "projectTemplateKey": config.template_key,
                        "leadAccountId": client.request("GET", "/rest/api/3/myself")[
                            "accountId"
                        ],
                    },
                )
                external_id = int(result["id"])
                href = "/rest/api/3/project/" + config.project_key
            elif operation.kind == "KanbanBoard":
                external_id, href = client.ensure_kanban_board(operation.subject)
            elif operation.kind == "ProjectMember":
                account_id = client.invite(operation.data["email"])
                roles = client.request(
                    "GET", f"/rest/api/3/project/{config.project_key}/role"
                )
                url = roles.get(operation.data["role"])
                if not url:
                    expected = operation.data["role"].casefold().rstrip("s")
                    url = next(
                        (
                            href
                            for name, href in roles.items()
                            if name.casefold().rstrip("s") == expected
                        ),
                        None,
                    )
                if not url:
                    raise ValueError(
                        f"Jira project role not found: {operation.data['role']}; available: {', '.join(roles)}"
                    )
                client.request(
                    "POST", url.replace(config.base_url, ""), {"user": [account_id]}
                )
                external_id = 0
                href = url
            else:
                issue = client.request(
                    "POST",
                    "/rest/api/3/issue",
                    {
                        "fields": {
                            "project": {"key": config.project_key},
                            "summary": operation.subject,
                            "issuetype": {"name": config.issue_type},
                        }
                    },
                )
                external_id = int(issue["id"])
                href = "/rest/api/3/issue/" + issue["id"]
            state.resources[operation.resource_id] = ExternalResource(
                operation.resource_id,
                operation.kind,
                external_id,
                href,
                operation.hash,
                datetime.now(timezone.utc).isoformat(),
            )
            if checkpoint:
                checkpoint(state)
        except ValueError as error:
            raise ValueError(
                f"{operation.action} {operation.kind} {operation.subject!r}: {error}"
            ) from error
    return state
