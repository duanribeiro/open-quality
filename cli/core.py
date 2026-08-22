from __future__ import annotations

import json
import re
from functools import lru_cache
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

import yaml
from jsonschema import Draft202012Validator
from referencing import Registry
from referencing import Resource as SchemaResource

from .model import Bundle, Check, Report, Resource, StageResult

KINDS = {
    "Project": "project",
    "Workflow": "workflows",
    "QualityRequirement": "requirements",
    "Stage": "stages",
    "QualityMeasure": "metrics",
    "QualityMeasureElement": "quality_measure_elements",
    "Artifact": "artifacts",
    "Role": "roles",
    "ApprovalPolicy": "approval_policies",
}
QUALITY_CHARACTERISTICS = {
    "functional-suitability", "performance-efficiency", "compatibility",
    "interaction-capability", "reliability", "security", "maintainability",
    "flexibility", "safety", "beneficialness", "freedom-from-risk", "acceptability",
}
QUALITY_SUBCHARACTERISTICS = {
    "functional-completeness", "functional-correctness", "functional-appropriateness",
    "time-behaviour", "resource-utilization", "capacity", "co-existence",
    "interoperability", "appropriateness-recognizability", "learnability", "operability",
    "user-error-protection", "user-engagement", "inclusivity", "user-assistance",
    "self-descriptiveness", "faultlessness", "availability", "fault-tolerance",
    "recoverability", "confidentiality", "integrity", "non-repudiation", "accountability",
    "authenticity", "resistance", "modularity", "reusability", "analysability",
    "modifiability", "testability", "adaptability", "scalability", "installability",
    "replaceability", "operational-constraint", "risk-identification", "fail-safe",
    "hazard-warning", "safe-integration", "usability", "accessibility", "suitability",
    "freedom-from-economic-risk", "freedom-from-environmental-and-societal-risk",
    "freedom-from-health-risk", "freedom-from-human-life-risk", "experience",
    "trustworthiness", "compliance",
}
TARGET_OPERATORS = {
    "equals", "notEquals", "greaterThan", "greaterThanOrEqual",
    "lessThan", "lessThanOrEqual", "exists", "approved",
}
ALLOWED: dict[str, set[str]] = {
    "Project": {
        "description",
        "workflow",
        "quality",
        "metrics",
        "documentation",
        "roles",
        "approvalPolicies",
    },
    "QualityRequirement": {
        "statement",
        "priority",
        "qualityMeasures",
        "documentation",
    },
    "Workflow": {"stages"},
    "Stage": {
        "environment",
        "reviewScope",
        "description",
        "dependsOn",
        "owner",
        "owners",
        "documentation",
        "approvalPolicy",
    },
    "QualityMeasure": {
        "measurementFunction",
        "unit",
        "description",
        "sourceHint",
    },
    "QualityMeasureElement": {
        "unit",
        "measurementMethod",
        "measurements",
        "description",
    },
    "Artifact": {
        "category",
        "externalLink",
        "required",
        "retention",
        "contentType",
    },
    "Role": {"description", "responsibilities"},
    "ApprovalPolicy": {"strategy", "approvers", "minimum"},
}
SCHEMA_FILES = {
    "Project": "project.schema.json",
    "Workflow": "workflow.schema.json",
    "QualityRequirement": "requirement.schema.json",
    "Stage": "stage.schema.json",
    "QualityMeasure": "metric.schema.json",
    "QualityMeasureElement": "quality-measure-element.schema.json",
    "Artifact": "artifact.schema.json",
    "Role": "role.schema.json",
    "ApprovalPolicy": "approval-policy.schema.json",
}


@lru_cache
def _contract_validator(kind: str) -> Draft202012Validator:
    schema_directory = Path(__file__).parents[1] / "schema" / "v0.1"
    registry = Registry()
    for path in schema_directory.glob("*.json"):
        schema = json.loads(path.read_text())
        registry = registry.with_resource(schema["$id"], SchemaResource.from_contents(schema))
    root = json.loads((schema_directory / SCHEMA_FILES[kind]).read_text())
    return Draft202012Validator(root, registry=registry)


def _validate_schema(payload: dict[str, Any], kind: str) -> None:
    errors = sorted(
        _contract_validator(kind).iter_errors(payload),
        key=lambda error: list(error.absolute_path),
    )
    if not errors:
        return
    error = errors[0]
    location = ".".join(str(part) for part in error.absolute_path) or "resource"
    if error.validator == "additionalProperties":
        raise ValueError(f"{location} contains unknown field")
    raise ValueError(f"{location}: {error.message}")


def _strict_mapping(value: Any, allowed: set[str], context: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ValueError(f"{context} must be a mapping")
    unknown = set(value) - allowed
    if unknown:
        raise ValueError(f"{context} contains unknown field {sorted(unknown)[0]!r}")
    return value


def parse(data: str | bytes) -> Resource:
    payload = yaml.safe_load(data)
    if not isinstance(payload, dict):
        raise ValueError("resource must be a mapping")
    allowed_top_level = {"specVersion", "kind", "metadata", "spec"}
    if payload.get("kind") == "Project":
        allowed_top_level.add("providers")
    top = _strict_mapping(
        payload, allowed_top_level, "resource"
    )
    version, kind = top.get("specVersion"), top.get("kind")
    if version != "0.1":
        raise ValueError(f"unsupported specVersion {version!r}")
    if kind not in KINDS:
        raise ValueError(f"unsupported kind {kind!r}")
    _validate_schema(payload, kind)
    metadata = _strict_mapping(
        top.get("metadata"), {"id", "name", "description", "labels"}, "metadata"
    )
    spec = _strict_mapping(top.get("spec"), ALLOWED[kind], "spec")
    providers = top.get("providers") or {}
    if kind == "Project":
        providers = _strict_mapping(providers, set(providers), "providers")
        for provider_role, provider in providers.items():
            if not isinstance(provider_role, str) or not provider_role:
                raise ValueError("provider role must be a non-empty string")
            _strict_mapping(
                provider,
                {"provider", "description", "config"},
                f"provider {provider_role!r}",
            )
            if not provider.get("provider"):
                raise ValueError(f"provider {provider_role!r} requires provider")
    return Resource(version, kind, metadata, spec, providers)


def parse_state(data: str | bytes) -> dict[str, Any]:
    value = _strict_mapping(
        yaml.safe_load(data) or {},
        {"metrics", "stages", "approvals", "documentation"},
        "state",
    )
    return {
        "metrics": value.get("metrics") or {},
        "stages": value.get("stages") or {},
        "approvals": value.get("approvals") or {},
        "documentation": value.get("documentation") or {},
    }


def load_contract(root: str | Path) -> Bundle:
    bundle = Bundle()
    for path in sorted(Path(root).rglob("*")):
        if not path.is_file() or path.suffix not in {".yaml", ".yml"}:
            continue
        try:
            resource = parse(path.read_text())
        except Exception as error:
            raise ValueError(f"{path}: {error}") from error
        if not resource.id:
            raise ValueError(f"{path}: metadata.id is required")
        if resource.id in bundle.files:
            raise ValueError(
                f"{path}: duplicate id {resource.id!r} (already declared in {bundle.files[resource.id]})"
            )
        if resource.kind == "Project":
            if bundle.project:
                raise ValueError(f"{path}: contract contains more than one Project")
            bundle.project = resource
        else:
            getattr(bundle, KINDS[resource.kind])[resource.id] = resource
        bundle.files[resource.id] = str(path)
    return bundle


def load_state(path: str | Path) -> dict[str, Any]:
    try:
        return parse_state(Path(path).read_text())
    except Exception as error:
        raise ValueError(f"{path}: {error}") from error


def quality_requirements(project: Resource) -> list[str]:
    """Return requirement IDs in the project's quality hierarchy order."""
    requirements: list[str] = []
    for characteristic in project.spec.get("quality", []):
        if not isinstance(characteristic, dict):
            continue
        requirements.extend(characteristic.get("requirements", []))
        for subcharacteristic in characteristic.get("subcharacteristics", []):
            if isinstance(subcharacteristic, dict):
                requirements.extend(subcharacteristic.get("requirements", []))
    return requirements


def validate(bundle: Bundle) -> list[str]:
    errors: list[str] = []
    add = errors.append
    if not bundle.project:
        return ["exactly one Project is required"]
    project = bundle.project
    if not project.name:
        add("Project metadata.name is required")
    for resource_id in bundle.files:
        if not re.fullmatch(r"[a-z][a-z0-9]*(?:-[a-z0-9]+)*", resource_id):
            add(f"id {resource_id!r} must be lowercase kebab-case")

    def refs(ids: list[str], kind: str, source: dict[str, Resource]) -> None:
        for item in ids or []:
            if item not in source:
                add(f"reference {item!r} does not resolve to {kind}")

    def artifact_refs(ids: list[str], category: str) -> None:
        for item in ids or []:
            artifact = bundle.artifacts.get(item)
            if not artifact:
                add(f"reference {item!r} does not resolve to Artifact")
            elif artifact.spec.get("category") != category:
                add(f"reference {item!r} must be {category}, not Artifact")

    spec = project.spec
    workflow_id = spec.get("workflow", "")
    if not workflow_id:
        add("Project.spec.workflow is required")
    elif workflow_id not in bundle.workflows:
        add(f"Project workflow {workflow_id!r} does not resolve to Workflow")
    quality = spec.get("quality")
    if not isinstance(quality, list) or not quality:
        add("Project.spec.quality must be a non-empty list")
        quality = []
    declared_requirements: set[str] = set()
    def declare_requirements(requirements: Any, context: str) -> None:
        if not isinstance(requirements, list) or not requirements:
            add(f"{context} requires requirements")
            return
        for requirement_id in requirements:
            requirement = bundle.requirements.get(requirement_id)
            if not requirement:
                add(f"Project quality requirement {requirement_id!r} does not resolve to QualityRequirement")
                continue
            if requirement_id in declared_requirements:
                add(f"Project quality requirement {requirement_id!r} is declared more than once")
            declared_requirements.add(requirement_id)

    for characteristic in quality:
        if not isinstance(characteristic, dict) or set(characteristic) - {"characteristic", "subcharacteristics", "requirements"}:
            add("Project quality entry contains an unknown field")
            continue
        characteristic_id = characteristic.get("characteristic")
        if characteristic_id not in QUALITY_CHARACTERISTICS:
            add(f"Project quality characteristic {characteristic_id!r} is not supported")
        subcharacteristics = characteristic.get("subcharacteristics")
        requirements = characteristic.get("requirements")
        if subcharacteristics is not None and requirements is not None:
            add(f"Project quality characteristic {characteristic_id!r} may declare subcharacteristics or requirements, not both")
            continue
        if requirements is not None:
            declare_requirements(requirements, f"Project quality characteristic {characteristic_id!r}")
            continue
        if not isinstance(subcharacteristics, list) or not subcharacteristics:
            add(f"Project quality characteristic {characteristic_id!r} requires subcharacteristics or requirements")
            continue
        for subcharacteristic in subcharacteristics:
            if not isinstance(subcharacteristic, dict) or set(subcharacteristic) - {"subcharacteristic", "requirements"}:
                add("Project quality subcharacteristic entry must contain only subcharacteristic and requirements")
                continue
            subcharacteristic_id = subcharacteristic.get("subcharacteristic")
            if subcharacteristic_id not in QUALITY_SUBCHARACTERISTICS:
                add(f"Project quality subcharacteristic {subcharacteristic_id!r} is not supported")
            declare_requirements(
                subcharacteristic.get("requirements"),
                f"Project quality subcharacteristic {subcharacteristic_id!r}",
            )
    for requirement_id in bundle.requirements:
        if requirement_id not in declared_requirements:
            add(f"QualityRequirement {requirement_id!r} is not declared in Project.spec.quality")
    for key, kind, source in [
        ("metrics", "QualityMeasure", bundle.metrics),
        ("roles", "Role", bundle.roles),
        ("approvalPolicies", "ApprovalPolicy", bundle.approval_policies),
    ]:
        refs(spec.get(key, []), kind, source)
    artifact_refs(spec.get("documentation", []), "documentation")
    for resource_id, workflow in bundle.workflows.items():
        if not workflow.spec.get("stages"):
            add(f"Workflow {resource_id!r} has no stages")
        refs(workflow.spec.get("stages", []), "Stage", bundle.stages)
    for resource_id, stage in bundle.stages.items():
        s = stage.spec
        if s.get("reviewScope") == "code" and not s.get("approvalPolicy"):
            add(f"Stage {resource_id!r} with reviewScope code requires approvalPolicy")
        refs(s.get("dependsOn", []), "Stage", bundle.stages)
        artifact_refs(s.get("documentation", []), "documentation")
        if s.get("owner"):
            refs([s["owner"]], "Role", bundle.roles)
        refs(s.get("owners", []), "Role", bundle.roles)
        if s.get("approvalPolicy"):
            refs([s["approvalPolicy"]], "ApprovalPolicy", bundle.approval_policies)
    for resource_id, requirement in bundle.requirements.items():
        s = requirement.spec
        if not s.get("statement"):
            add(f"Requirement {resource_id!r} statement is required")
        if not requirement.name:
            add(f"Requirement {resource_id!r} metadata.name is required")
        if s.get("priority") not in {"low", "medium", "high", "critical"}:
            add(
                f"Requirement {resource_id!r} has invalid priority {s.get('priority', '')!r}"
            )
        quality_measures = s.get("qualityMeasures")
        if not isinstance(quality_measures, list) or not quality_measures:
            add(f"Requirement {resource_id!r} requires qualityMeasures")
        else:
            for quality_measure in quality_measures:
                if not isinstance(quality_measure, dict) or set(quality_measure) - {"qualityMeasure", "target"}:
                    add(f"Requirement {resource_id!r} quality measure entry has unknown field")
                    continue
                measure_id = quality_measure.get("qualityMeasure")
                refs([measure_id], "QualityMeasure", bundle.metrics)
                target = quality_measure.get("target")
                if not isinstance(target, dict) or not {"operator", "value"} <= set(target):
                    add(f"Requirement {resource_id!r} quality measure {measure_id!r} requires target.operator and target.value")
                elif target["operator"] not in TARGET_OPERATORS:
                    add(
                        f"Requirement {resource_id!r} quality measure {measure_id!r} "
                        f"uses invalid target operator {target['operator']!r}"
                    )
        artifact_refs(s.get("documentation", []), "documentation")
    for resource_id, policy in bundle.approval_policies.items():
        s = policy.spec
        if not s.get("approvers"):
            add(f"ApprovalPolicy {resource_id!r} requires approvers")
        refs(s.get("approvers", []), "Role", bundle.roles)
        if s.get("strategy") not in {"all", "any", "minimum"}:
            add(
                f"ApprovalPolicy {resource_id!r} has invalid strategy {s.get('strategy', '')!r}"
            )
        if s.get("strategy") == "minimum" and not (
            1 <= s.get("minimum", 0) <= len(s.get("approvers", []))
        ):
            add(f"ApprovalPolicy {resource_id!r} has unsatisfiable minimum")
        if s.get("strategy") != "minimum" and "minimum" in s:
            add(f"ApprovalPolicy {resource_id!r} minimum is only valid for minimum strategy")
    for resource_id, artifact in bundle.artifacts.items():
        if artifact.spec.get("category") != "documentation":
            add(
                f"Artifact {resource_id!r} has invalid category {artifact.spec.get('category', '')!r}"
            )
        external_link = artifact.spec.get("externalLink", "")
        if not isinstance(external_link, str):
            add(f"Artifact {resource_id!r} externalLink must be an absolute URL")
        else:
            parsed_link = urlparse(external_link)
            if not (parsed_link.scheme and parsed_link.netloc):
                add(
                    f"Artifact {resource_id!r} externalLink must be an absolute URL"
                )
    if cycle := _find_cycle(bundle.stages):
        add(f"stage dependency cycle: {cycle}")
    return errors


def _find_cycle(stages: dict[str, Resource]) -> list[str]:
    state: dict[str, int] = {}
    stack: list[str] = []

    def visit(resource_id: str) -> list[str]:
        if state.get(resource_id) == 1:
            return [*stack, resource_id]
        if state.get(resource_id) == 2:
            return []
        state[resource_id] = 1
        stack.append(resource_id)
        for dependency in stages.get(resource_id, Resource("", "", {}, {})).spec.get(
            "dependsOn", []
        ):
            if cycle := visit(dependency):
                return cycle
        stack.pop()
        state[resource_id] = 2
        return []

    for resource_id in stages:
        if cycle := visit(resource_id):
            return cycle
    return []


def _compare(
    values: dict[str, Any], metric: str, operator: str, expected: Any
) -> tuple[bool, str]:
    actual = values.get(metric)
    exists = metric in values
    if operator == "exists":
        return (True, "") if exists else (False, f"metric {metric} is missing")
    if not exists:
        return False, f"metric {metric} is missing"
    if operator == "approved":
        ok = actual is True or str(actual).lower() == "approved"
        return (ok, "" if ok else f"metric {metric} is not approved")
    try:
        actual_number, expected_number = float(actual), float(expected)
        predicates = {
            "equals": actual_number == expected_number,
            "notEquals": actual_number != expected_number,
            "greaterThan": actual_number > expected_number,
            "greaterThanOrEqual": actual_number >= expected_number,
            "lessThan": actual_number < expected_number,
            "lessThanOrEqual": actual_number <= expected_number,
        }
        ok = predicates.get(operator, False)
    except (TypeError, ValueError):
        equal = actual == expected or str(actual) == str(expected)
        ok = (
            equal
            if operator == "equals"
            else not equal if operator == "notEquals" else False
        )
    return (
        (True, "")
        if ok
        else (False, f"{metric}={actual} does not satisfy {operator} {expected}")
    )


def evaluate(bundle: Bundle, state: dict[str, Any]) -> Report:
    assert bundle.project
    report = Report(project=bundle.project.name)
    workflow = bundle.workflows.get(bundle.project.spec.get("workflow"))
    if not workflow:
        report.ready = False
        return report
    report.workflow = workflow.name
    active_stages: list[str] = []
    pending_stages: list[str] = []
    for resource_id in quality_requirements(bundle.project):
        requirement = bundle.requirements[resource_id]
        check = Check(resource_id, requirement.name, True)
        for quality_measure in requirement.spec.get("qualityMeasures", []):
            target = quality_measure.get("target", {})
            passed, reason = _compare(
                state["metrics"],
                quality_measure.get("qualityMeasure"),
                target.get("operator"),
                target.get("value"),
            )
            if not passed:
                check.passed = False
                check.reason = reason
        for field, label in (("documentation", "documentation"),):
            for evidence_id in requirement.spec.get(field, []):
                if state[field].get(evidence_id):
                    continue
                check.passed = False
                check.reason = "; ".join(
                    filter(None, [check.reason, f"missing {label} {evidence_id}"])
                )
        report.requirements.append(check)
        report.ready &= check.passed
    for stage_id in workflow.spec.get("stages", []):
        stage = bundle.stages[stage_id]
        status = state["stages"].get(stage_id, "pending") or "pending"
        result = StageResult(stage_id, stage.name, status)
        if status in {"running", "blocked"}:
            active_stages.append(stage.name)
        elif status == "pending":
            pending_stages.append(stage.name)
        for field, checks, label in (
            ("documentation", result.documentation, "documentation"),
        ):
            for evidence_id in stage.spec.get(field, []):
                ok = bool(state[field].get(evidence_id))
                checks.append(
                    Check(
                        evidence_id,
                        bundle.artifacts[evidence_id].name,
                        ok,
                        reason="" if ok else f"missing {label}",
                    )
                )
                report.ready &= ok
        policy_id = stage.spec.get("approvalPolicy")
        if policy_id:
            policy = bundle.approval_policies[policy_id]
            approved = set(state["approvals"].get(policy_id, []))
            approvers = policy.spec.get("approvers", [])
            count = len(approved & set(approvers))
            strategy = policy.spec.get("strategy")
            ok = (
                count == len(approvers)
                if strategy == "all"
                else (
                    count >= 1
                    if strategy == "any"
                    else count >= policy.spec.get("minimum", 0)
                )
            )
            missing = ", ".join(sorted(set(approvers) - approved))
            result.approval = Check(
                policy_id,
                policy.name,
                ok,
                reason="" if ok else f"missing approval from {missing}",
            )
            report.ready &= ok
        if status != "completed":
            report.ready = False
        report.stages.append(result)
    report.current_stage = ", ".join(active_stages) or next(
        iter(pending_stages), "Complete"
    )
    return report
