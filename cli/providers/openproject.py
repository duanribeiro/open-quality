from __future__ import annotations

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
from ..core import quality_requirements


REGISTERED_PROVIDERS = {"openproject"}


@dataclass
class TargetConfig:
    provider: str
    name: str
    base_url: str
    project: str = ""
    type_href: str = ""
    notify: bool = False
    description: str = ""
    members_file: str = ""
    kanban_columns: list[str] = field(default_factory=list)

    def validate(self) -> None:
        if self.provider not in REGISTERED_PROVIDERS:
            raise ValueError(
                f"unsupported provider {self.provider!r}; registered providers: "
                + ", ".join(sorted(REGISTERED_PROVIDERS))
            )
        if not all([self.name, self.base_url, self.type_href]):
            raise ValueError(
                "name, baseURL and workPackageTypeHref are required"
            )
        if not self.type_href.startswith("/api/v3/types/"):
            raise ValueError("workPackageTypeHref must be an OpenProject API type href")

    def token(self) -> str:
        if not (token := os.getenv("OPENPROJECT_TOKEN")):
            raise ValueError("environment variable OPENPROJECT_TOKEN is empty")
        return token


def load_config(path: str | Path | dict[str, Any], role: str = "") -> TargetConfig:
    try:
        raw = path if isinstance(path, dict) else yaml.safe_load(Path(path).read_text())
        unknown = set(raw) - {"provider", "config", "description"}
        if unknown:
            raise ValueError(f"unknown field {sorted(unknown)[0]!r}")
        provider_config = raw.get("config") or {}
        if not isinstance(provider_config, dict):
            raise ValueError("config must be a mapping")
        if raw.get("provider") == "openproject":
            unknown = set(provider_config) - {
                "baseURL", "workPackageTypeHref", "notify", "membersFile", "members", "kanban"
            }
            if unknown:
                raise ValueError(
                    f"OpenProject config contains unknown field {sorted(unknown)[0]!r}"
                )
        kanban = provider_config.get("kanban") or {}
        if not isinstance(kanban, dict) or set(kanban) - {"columns"}:
            raise ValueError("OpenProject kanban must contain only columns")
        columns = kanban.get("columns", [])
        if not isinstance(columns, list) or not all(isinstance(column, str) and column for column in columns):
            raise ValueError("OpenProject kanban.columns must be a list of non-empty strings")
        config = TargetConfig(
            raw.get("provider", ""),
            role or raw.get("provider", ""),
            provider_config.get("baseURL", ""),
            "",
            provider_config.get("workPackageTypeHref", ""),
            provider_config.get("notify", False),
            raw.get("description", ""),
            provider_config.get("membersFile", ""),
            columns,
        )
        config.validate()
        return config
    except Exception as error:
        raise ValueError(f"target {path}: {error}") from error


@dataclass(frozen=True)
class ProjectMember:
    role: str
    email: str
    openproject_role: str


def load_members(path: str | Path | dict) -> list[ProjectMember]:
    try:
        raw = (path if isinstance(path, dict) else yaml.safe_load(Path(path).read_text())) or {}
        if raw.get("provider") != "openproject" or set(raw) - {"provider", "members"}:
            raise ValueError("must contain only provider: openproject and members")
        members: list[ProjectMember] = []
        for entry in raw.get("members", []):
            if set(entry) - {"role", "emails", "openProjectRole"}:
                raise ValueError("member contains an unknown field")
            role, emails, op_role = (
                entry.get("role"),
                entry.get("emails"),
                entry.get("openProjectRole"),
            )
            if not isinstance(role, str) or not isinstance(op_role, str) or not isinstance(emails, list):
                raise ValueError("member requires role, emails and openProjectRole")
            members.extend(ProjectMember(role, email, op_role) for email in emails if isinstance(email, str))
        return members
    except Exception as error:
        raise ValueError(f"members {path}: {error}") from error


@dataclass
class ExternalResource:
    resourceId: str
    kind: str
    externalId: int
    href: str
    hash: str
    appliedAt: str


@dataclass
class ProviderState:
    version: int
    provider: str
    target: str
    resources: dict[str, ExternalResource] = field(default_factory=dict)


def new_state(target: str) -> ProviderState:
    return ProviderState(1, "openproject", target)


def load_state(path: str | Path, target: str) -> ProviderState:
    path = Path(path)
    if not path.exists():
        return new_state(target)
    raw = json.loads(path.read_text())
    if raw.get("provider") != "openproject" or raw.get("target") != target:
        raise ValueError(
            f"state belongs to provider {raw.get('provider')!r} target {raw.get('target')!r}"
        )
    return ProviderState(
        raw.get("version", 1),
        raw["provider"],
        raw["target"],
        {
            key: ExternalResource(**value)
            for key, value in raw.get("resources", {}).items()
        },
    )


def save_state(path: str | Path, state: ProviderState) -> None:
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


@dataclass
class Operation:
    action: str
    resource_id: str
    kind: str
    subject: str
    description: str
    parent: str
    hash: str
    data: dict[str, str] = field(default_factory=dict)


def _description(resource: Resource, kind: str) -> str:
    if kind == "QualityContract":
        return f"**Open Quality resource:** `{resource.id}`\n\n{resource.metadata.get('description', '')}"
    lines = [f"**Open Quality resource:** `{resource.id}`"]
    if kind == "QualityRequirement":
        lines += [
            resource.spec.get("statement", ""),
            "",
            f"- Priority: {resource.spec.get('priority', '')}",
        ]
    elif kind == "Stage":
        if resource.spec.get("description"):
            lines += ["", resource.spec["description"]]
        if resource.spec.get("dependsOn"):
            lines += [
                "",
                "- Depends on: `" + "`, `".join(resource.spec["dependsOn"]) + "`",
            ]
    else:
        lines += [
            "",
            "All rules must pass:",
            *[
                f"- `{rule.get('metric')} {rule.get('operator')} {rule.get('value')}`"
                for rule in resource.spec.get("rules", [])
            ],
            f"- Failure action: `{resource.spec.get('failure', {}).get('action', '')}`",
        ]
    return "\n".join(lines)


def plan(
    bundle: Bundle, state: ProviderState, config: TargetConfig, members: list[ProjectMember] | None = None
) -> list[Operation]:
    assert bundle.project
    workflow = bundle.workflows[bundle.project.spec["workflow"]]
    items: list[tuple[Resource, str, str, str]] = [
        (bundle.project, "QualityContract", bundle.project.name, "")
    ]
    items += [
        (
            bundle.requirements[item],
            "QualityRequirement",
            bundle.requirements[item].name,
            bundle.project.id,
        )
        for item in quality_requirements(bundle.project)
    ]
    items += [
        (
            bundle.stages[item],
            "Stage",
            bundle.stages[item].name,
            bundle.project.id,
        )
        for item in workflow.spec["stages"]
    ]
    operations = []
    for resource, kind, subject, parent in items:
        description = _description(resource, kind)
        digest = hashlib.sha256(
            "\0".join([kind, subject, description, parent]).encode()
        ).hexdigest()
        action = (
            "no-op"
            if resource.id in state.resources
            and state.resources[resource.id].hash == digest
            else "update" if resource.id in state.resources else "create"
        )
        operations.append(
            Operation(action, resource.id, kind, subject, description, parent, digest)
        )
    members = members or []
    stages = {stage_id: bundle.stages[stage_id] for stage_id in workflow.spec["stages"]}
    bootstrap: list[Operation] = []
    if stages:
        _append_operation(
            bootstrap, state, f"kanban:{bundle.project.id}", "KanbanBoard",
            bundle.project.name, "Kanban board for the development workflow", bundle.project.id,
            {"projectIdentifier": bundle.project.id, "columns": json.dumps(config.kanban_columns)},
        )
        for member in members:
            _append_operation(
                bootstrap, state, f"member:{member.email}", "ProjectMember", member.email,
                f"{member.role} → {member.openproject_role}", bundle.project.id,
                {"email": member.email, "role": member.openproject_role},
            )
    # Project infrastructure must exist before the workflow work packages.
    operations[1:1] = bootstrap
    for stage in stages.values():
        if stage.spec.get("reviewScope") != "code":
            continue
        policy_id = stage.spec.get("approvalPolicy")
        if not policy_id:
            raise ValueError(f"code review stage {stage.id!r} requires approvalPolicy")
        policy = bundle.approval_policies[policy_id]
        reviewer_roles = set(policy.spec["approvers"])
        for member in members:
            if member.role in reviewer_roles:
                _append_operation(
                    operations, state, f"code-reviewer:{stage.id}:{member.email}", "CodeReviewer",
                    member.email, f"Code reviewer for {stage.name}", stage.id,
                    {"email": member.email},
                )
    return operations


def _append_operation(
    operations: list[Operation], state: ProviderState, resource_id: str, kind: str,
    subject: str, description: str, parent: str, data: dict[str, str] | None = None,
) -> None:
    digest = hashlib.sha256("\0".join([kind, subject, description, parent, json.dumps(data or {}, sort_keys=True)]).encode()).hexdigest()
    action = "no-op" if resource_id in state.resources and state.resources[resource_id].hash == digest else "update" if resource_id in state.resources else "create"
    operations.append(Operation(action, resource_id, kind, subject, description, parent, digest, data or {}))


class OpenProjectClient:
    def __init__(self, config: TargetConfig, token: str):
        self.config, self.token = config, token

    def _request(
        self, method: str, path: str, payload: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        url = (
            path
            if path.startswith("http")
            else self.config.base_url.rstrip("/") + "/" + path.lstrip("/")
        )
        request = Request(
            url,
            method=method,
            data=json.dumps(payload).encode() if payload else None,
            headers={
                "Authorization": "Bearer " + self.token,
                "Accept": "application/hal+json",
                "Content-Type": "application/json",
            },
        )
        try:
            with urlopen(request, timeout=30) as response:
                return json.load(response)
        except HTTPError as error:
            body = error.read().decode()
            try:
                response = json.loads(body)
                message = response.get("message", body)
                details = response.get("_embedded", {}).get("details")
                if details:
                    message += ": " + json.dumps(details, ensure_ascii=False)
                elif response.get("_embedded"):
                    message += ": " + json.dumps(
                        response["_embedded"], ensure_ascii=False
                    )
            except json.JSONDecodeError:
                message = body or "no response body"
            raise ValueError(
                f"OpenProject returned {error.code} {error.reason}: {message}"
            ) from error

    def find_project(self, identifier: str) -> tuple[int, str] | None:
        try:
            result = self._request("GET", f"/api/v3/projects/{quote(identifier, safe='')}")
        except ValueError as error:
            if " 404 " in str(error):
                return None
            raise
        href = result.get("_links", {}).get("self", {}).get("href", "")
        if not result.get("id") or not href:
            raise ValueError("OpenProject project response is missing id or self link")
        return result["id"], href

    def _collection(self, path: str) -> list[dict[str, Any]]:
        return self._request("GET", path).get("_embedded", {}).get("elements", [])

    def _user_href(self, email: str) -> str:
        # OpenProject 17 exposes email in User resources but does not support it
        # as an API v3 filter. Match the returned user records exactly instead.
        users = [
            user
            for user in self._collection("/api/v3/users?pageSize=1000")
            if user.get("email", "").casefold() == email.casefold()
        ]
        if not users:
            # An invited account needs only an email address. OpenProject sends
            # the activation invitation and returns the newly created user.
            created = self._request(
                "POST", "/api/v3/users", {"email": email, "status": "invited"}
            )
            href = created.get("_links", {}).get("self", {}).get("href")
            if not href:
                raise ValueError(
                    f"OpenProject invitation response is missing self link for {email!r}"
                )
            return href
        if len(users) != 1:
            raise ValueError(f"multiple OpenProject users found for email {email!r}")
        href = users[0].get("_links", {}).get("self", {}).get("href")
        if not href:
            raise ValueError(f"OpenProject user response is missing self link for {email!r}")
        return href

    def _role_href(self, name: str) -> str:
        for role in self._collection("/api/v3/roles?pageSize=1000"):
            if role.get("name") == name:
                return role["_links"]["self"]["href"]
        raise ValueError(f"OpenProject role not found: {name!r}")

    def _kanban_columns(self, columns: list[str]) -> list[dict[str, Any]]:
        statuses = {status.get("name"): status for status in self._collection("/api/v3/statuses")}
        missing = [column for column in columns if column not in statuses]
        if missing:
            raise ValueError("OpenProject Kanban status not found: " + ", ".join(repr(column) for column in missing))
        return [statuses[column] for column in columns]

    def _set_kanban_columns(
        self, board: dict[str, Any], columns: list[str]
    ) -> dict[str, Any]:
        if not columns:
            return board
        statuses = self._kanban_columns(columns)
        configured = []
        for index, status in enumerate(statuses, start=1):
            configured.append(
                {
                    "_type": "GridWidget",
                    "identifier": "work_package_query",
                    "startRow": 1,
                    "endRow": 2,
                    "startColumn": index,
                    "endColumn": index + 1,
                    "options": {
                        "filters": [
                            {
                                "status_id": {
                                    "operator": "=",
                                    "values": [str(status["id"])],
                                }
                            }
                        ]
                    },
                }
            )
        payload = {
            "name": board.get("name", ""),
            "options": {"type": "action", "attribute": "status"},
            "rowCount": 2,
            "columnCount": len(configured) + 1,
            "widgets": configured,
            "_links": {"scope": board.get("_links", {}).get("scope", {})},
        }
        href = board["_links"]["self"]["href"]
        # Grid updates retain widgets that are not explicitly removed. Clear the
        # existing lists first so the requested columns cannot overlap them.
        clear_payload = {
            "name": board.get("name", ""),
            "options": {"type": "action", "attribute": "status"},
            "rowCount": 1,
            "columnCount": 1,
            "widgets": [],
            "_links": {"scope": board.get("_links", {}).get("scope", {})},
        }
        self._request("PATCH", href, clear_payload)
        return self._request("PATCH", href, payload)

    def create_kanban_board(
        self, project_identifier: str, name: str, columns: list[str]
    ) -> tuple[int, str]:
        payload = {
            "name": name,
            "_links": {"scope": {"href": f"/projects/{project_identifier}/boards"}},
            "options": {"type": "action", "attribute": "status"},
        }
        if columns:
            statuses = self._kanban_columns(columns)
            payload["rowCount"] = 2
            payload["columnCount"] = len(statuses) + 1
            payload["widgets"] = [
                {
                    "_type": "GridWidget",
                    "identifier": "work_package_query",
                    "startRow": 1,
                    "endRow": 2,
                    "startColumn": index,
                    "endColumn": index + 1,
                    "options": {"filters": [{"status_id": {"operator": "=", "values": [str(status["id"])]}}]},
                }
                for index, status in enumerate(statuses, start=1)
            ]
        form = self._request("POST", "/api/v3/grids/form", payload)
        write_payload = form.get("_embedded", {}).get("payload", payload)
        result = self._request("POST", "/api/v3/grids", write_payload)
        href = result.get("_links", {}).get("self", {}).get("href", "")
        if not result.get("id") or not href:
            raise ValueError("OpenProject Kanban board response is missing id or self link")
        result = self._request("GET", href)
        result = self._set_kanban_columns(result, columns)
        href = result.get("_links", {}).get("self", {}).get("href", "")
        if not result.get("id") or not href:
            raise ValueError("OpenProject Kanban board response is missing id or self link")
        return result["id"], href

    def update_kanban_board(self, href: str, columns: list[str]) -> tuple[int, str]:
        result = self._set_kanban_columns(self._request("GET", href), columns)
        return result["id"], result["_links"]["self"]["href"]

    def update_project(self, href: str, name: str) -> tuple[int, str]:
        current = self._request("GET", href)
        result = self._request(
            "PATCH", href, {"name": name, "lockVersion": current.get("lockVersion", 0)}
        )
        return result["id"], result["_links"]["self"]["href"]

    def add_member(self, project_href: str, email: str, role: str) -> tuple[int, str]:
        result = self._request("POST", "/api/v3/memberships", {
            "_links": {
                "project": {"href": project_href},
                "principal": {"href": self._user_href(email)},
                "roles": [{"href": self._role_href(role)}],
            },
            "_meta": {"sendNotifications": False},
        })
        return result["id"], result["_links"]["self"]["href"]

    def add_code_reviewer(self, work_package_href: str, email: str) -> tuple[int, str]:
        user_href = self._user_href(email)
        self._request("POST", work_package_href + "/watchers", {"user": {"href": user_href}})
        return int(user_href.rsplit("/", 1)[-1]), user_href

    def create(self, input: Operation, parent_href: str, project_href: str = "") -> tuple[int, str]:
        if input.kind == "QualityContract":
            result = self._request(
                "POST",
                "/api/v3/projects",
                {"identifier": input.resource_id, "name": input.subject},
            )
            return result["id"], result["_links"]["self"]["href"]
        project_id = project_href.rsplit("/", 1)[-1]
        return self._write(
            "POST",
            f"/api/v3/projects/{quote(project_id, safe='')}/work_packages?notify={str(self.config.notify).lower()}",
            input,
            parent_href,
            project_href=project_href,
        )

    def update(self, href: str, input: Operation, parent_href: str) -> tuple[int, str]:
        current = self._request("GET", href)
        return self._write(
            "PATCH",
            href + f"?notify={str(self.config.notify).lower()}",
            input,
            parent_href,
            current.get("lockVersion", 0),
        )

    def _write(
        self,
        method: str,
        path: str,
        operation: Operation,
        parent: str,
        lock: int | None = None,
        project_href: str = "",
    ) -> tuple[int, str]:
        links: dict[str, Any] = {"type": {"href": self.config.type_href}}
        if project_href:
            links["project"] = {"href": project_href}
        if parent:
            links["parent"] = {"href": parent}
        body: dict[str, Any] = {
            "subject": operation.subject,
            "description": {"format": "markdown", "raw": operation.description},
            "_links": links,
        }
        if lock is not None:
            body["lockVersion"] = lock
        result = self._request(method, path, body)
        href = result.get("_links", {}).get("self", {}).get("href", "")
        if not result.get("id") or not href:
            raise ValueError("OpenProject response is missing id or self link")
        return result["id"], href


def apply(
    operations: list[Operation], state: ProviderState, client: OpenProjectClient,
    checkpoint: Callable[[ProviderState], None] | None = None,
) -> ProviderState:
    for operation in operations:
        if operation.action == "no-op":
            continue
        parent = state.resources.get(operation.parent)
        if operation.parent and not parent:
            raise ValueError(
                f"parent resource {operation.parent!r} has not been materialized"
            )
        project = state.resources.get(
            next((item.resource_id for item in operations if item.kind == "QualityContract"), "")
        )
        try:
            if operation.kind == "KanbanBoard":
                if not parent:
                    raise ValueError("Kanban board requires an OpenProject project")
                columns = json.loads(operation.data["columns"])
                external_id, href = (
                    client.update_kanban_board(
                        state.resources[operation.resource_id].href, columns
                    )
                    if operation.action == "update"
                    else client.create_kanban_board(
                        operation.data["projectIdentifier"], operation.subject, columns
                    )
                )
            elif operation.kind == "ProjectMember":
                if not parent:
                    raise ValueError("project member requires an OpenProject project")
                external_id, href = client.add_member(
                    parent.href, operation.data["email"], operation.data["role"]
                )
            elif operation.kind == "CodeReviewer":
                if not parent:
                    raise ValueError("code reviewer requires a code-review work package")
                external_id, href = client.add_code_reviewer(parent.href, operation.data["email"])
            elif operation.kind == "QualityContract" and operation.action == "update":
                external_id, href = client.update_project(
                    state.resources[operation.resource_id].href, operation.subject
                )
            else:
                external_id, href = (
                    client.update(
                        state.resources[operation.resource_id].href,
                        operation,
                        parent.href if parent and parent.kind != "QualityContract" else "",
                    )
                    if operation.action == "update"
                    else client.create(
                        operation,
                        parent.href if parent and parent.kind != "QualityContract" else "",
                        project.href if project else "",
                    )
                )
        except ValueError as error:
            raise ValueError(
                f"{operation.action} {operation.kind} {operation.subject!r}: {error}"
            ) from error
        state.resources[operation.resource_id] = ExternalResource(
            operation.resource_id,
            operation.kind,
            external_id,
            href,
            operation.hash,
            datetime.now(UTC).isoformat(),
        )
        if checkpoint:
            checkpoint(state)
    return state


class OpenProjectProvider:
    """OpenProject implementation of the provider adapter contract."""

    name = "openproject"

    def __init__(self, config: TargetConfig, token: str):
        self.config = config
        self.client = OpenProjectClient(config, token)

    def plan(
        self, bundle: Bundle, state: ProviderState, members: list[ProjectMember]
    ) -> list[Operation]:
        return plan(bundle, state, self.config, members)

    def apply(
        self, operations: list[Operation], state: ProviderState,
        checkpoint: Callable[[ProviderState], None] | None = None,
    ) -> ProviderState:
        return apply(operations, state, self.client, checkpoint)
