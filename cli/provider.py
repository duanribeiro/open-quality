from __future__ import annotations

import hashlib
import json
import os
from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from urllib.error import HTTPError
from urllib.parse import quote
from urllib.request import Request, urlopen

import yaml

from .model import Bundle, Resource


@dataclass
class TargetConfig:
    provider: str
    name: str
    base_url: str
    token_env: str = ""
    project: str = ""
    type_href: str = ""
    notify: bool = False
    description: str = ""

    def validate(self) -> None:
        if self.provider != "openproject":
            raise ValueError("provider must be openproject")
        if not all([self.name, self.base_url, self.project, self.type_href]):
            raise ValueError(
                "name, baseURL, project and workPackageTypeHref are required"
            )
        if not self.type_href.startswith("/api/v3/types/"):
            raise ValueError("workPackageTypeHref must be an OpenProject API type href")

    def token(self) -> str:
        if not self.token_env:
            raise ValueError("tokenEnv is required for apply")
        if not (token := os.getenv(self.token_env)):
            raise ValueError(f"environment variable {self.token_env} is empty")
        return token


def load_config(path: str | Path) -> TargetConfig:
    try:
        raw = yaml.safe_load(Path(path).read_text())
        unknown = set(raw) - {
            "provider",
            "name",
            "baseURL",
            "tokenEnv",
            "project",
            "workPackageTypeHref",
            "notify",
            "description",
        }
        if unknown:
            raise ValueError(f"unknown field {sorted(unknown)[0]!r}")
        config = TargetConfig(
            raw.get("provider", ""),
            raw.get("name", ""),
            raw.get("baseURL", ""),
            raw.get("tokenEnv", ""),
            raw.get("project", ""),
            raw.get("workPackageTypeHref", ""),
            raw.get("notify", False),
            raw.get("description", ""),
        )
        config.validate()
        return config
    except Exception as error:
        raise ValueError(f"target {path}: {error}") from error


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


def _description(resource: Resource, kind: str) -> str:
    if kind == "Project":
        return f"**Open Quality resource:** `{resource.id}`\n\n{resource.metadata.get('description', '')}"
    lines = [f"**Open Quality resource:** `{resource.id}`"]
    if kind == "Requirement":
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


def plan(bundle: Bundle, state: ProviderState, config: TargetConfig) -> list[Operation]:
    assert bundle.project
    workflow = bundle.workflows[bundle.project.spec["workflow"]]
    items: list[tuple[Resource, str, str, str]] = [
        (bundle.project, "Project", "[Open Quality] " + bundle.project.name, "")
    ]
    items += [
        (
            bundle.requirements[item],
            "Requirement",
            "[Requirement] " + bundle.requirements[item].name,
            bundle.project.id,
        )
        for item in bundle.project.spec.get("requirements", [])
    ]
    items += [
        (
            bundle.stages[item],
            "Stage",
            "[Stage] " + bundle.stages[item].name,
            bundle.project.id,
        )
        for item in workflow.spec["stages"]
    ]
    seen: set[str] = set()
    for stage_id in workflow.spec["stages"]:
        for gate_id in bundle.stages[stage_id].spec.get("gates", []):
            if gate_id not in seen:
                seen.add(gate_id)
                items.append(
                    (
                        bundle.gates[gate_id],
                        "Gate",
                        "[Gate] " + bundle.gates[gate_id].name,
                        stage_id,
                    )
                )
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
    return operations


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
            raise ValueError(
                f"OpenProject returned {error.code} {error.reason}: {json.loads(body).get('message', body)}"
            ) from error

    def create(self, input: Operation, parent_href: str) -> tuple[int, str]:
        return self._write(
            "POST",
            f"/api/v3/projects/{quote(self.config.project, safe='')}/work_packages?notify={str(self.config.notify).lower()}",
            input,
            parent_href,
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
        self, method: str, path: str, operation: Operation, parent: str, lock: int = 0
    ) -> tuple[int, str]:
        links: dict[str, Any] = {"type": {"href": self.config.type_href}}
        if parent:
            links["parent"] = {"href": parent}
        body: dict[str, Any] = {
            "subject": operation.subject,
            "description": {"format": "markdown", "raw": operation.description},
            "_links": links,
        }
        if lock:
            body["lockVersion"] = lock
        result = self._request(method, path, body)
        href = result.get("_links", {}).get("self", {}).get("href", "")
        if not result.get("id") or not href:
            raise ValueError("OpenProject response is missing id or self link")
        return result["id"], href


def apply(
    operations: list[Operation], state: ProviderState, client: OpenProjectClient
) -> ProviderState:
    for operation in operations:
        if operation.action == "no-op":
            continue
        parent = state.resources.get(operation.parent)
        if operation.parent and not parent:
            raise ValueError(
                f"parent resource {operation.parent!r} has not been materialized"
            )
        external_id, href = (
            client.update(
                state.resources[operation.resource_id].href,
                operation,
                parent.href if parent else "",
            )
            if operation.action == "update"
            else client.create(operation, parent.href if parent else "")
        )
        state.resources[operation.resource_id] = ExternalResource(
            operation.resource_id,
            operation.kind,
            external_id,
            href,
            operation.hash,
            datetime.now(UTC).isoformat(),
        )
    return state
