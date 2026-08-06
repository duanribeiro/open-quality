from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class Resource:
    spec_version: str
    kind: str
    metadata: dict[str, Any]
    spec: dict[str, Any]

    @property
    def id(self) -> str:
        return self.metadata.get("id", "")

    @property
    def name(self) -> str:
        return self.metadata.get("name", "")


@dataclass
class Bundle:
    project: Resource | None = None
    workflows: dict[str, Resource] = field(default_factory=dict)
    requirements: dict[str, Resource] = field(default_factory=dict)
    quality_characteristics: dict[str, Resource] = field(default_factory=dict)
    quality_subcharacteristics: dict[str, Resource] = field(default_factory=dict)
    stages: dict[str, Resource] = field(default_factory=dict)
    gates: dict[str, Resource] = field(default_factory=dict)
    metrics: dict[str, Resource] = field(default_factory=dict)
    quality_measure_elements: dict[str, Resource] = field(default_factory=dict)
    artifacts: dict[str, Resource] = field(default_factory=dict)
    roles: dict[str, Resource] = field(default_factory=dict)
    approval_policies: dict[str, Resource] = field(default_factory=dict)
    files: dict[str, str] = field(default_factory=dict)


@dataclass
class Check:
    id: str
    name: str
    passed: bool
    warning: bool = False
    reason: str = ""


@dataclass
class StageResult:
    id: str
    name: str
    status: str
    gates: list[Check] = field(default_factory=list)
    approval: Check | None = None
    documentation: list[Check] = field(default_factory=list)
    reports: list[Check] = field(default_factory=list)


@dataclass
class Report:
    project: str = ""
    workflow: str = ""
    current_stage: str = ""
    requirements: list[Check] = field(default_factory=list)
    stages: list[StageResult] = field(default_factory=list)
    gates: list[Check] = field(default_factory=list)
    ready: bool = True
