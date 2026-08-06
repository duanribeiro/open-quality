from __future__ import annotations

import re
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

import yaml

from .model import Bundle, Check, Report, Resource, StageResult

KINDS = {
    "Project": "project",
    "Workflow": "workflows",
    "Requirement": "requirements",
    "QualityCharacteristic": "quality_characteristics",
    "QualitySubcharacteristic": "quality_subcharacteristics",
    "Stage": "stages",
    "Gate": "gates",
    "Metric": "metrics",
    "QualityMeasureElement": "quality_measure_elements",
    "Artifact": "artifacts",
    "Role": "roles",
    "ApprovalPolicy": "approval_policies",
}
STAGE_TYPES = {
    "refinement",
    "development",
    "review",
    "continuous-integration",
    "deploy",
}
STAGE_ACTIVITIES = {
    "continuous-integration": {
        "linter",
        "build",
        "unit-tests",
        "integration-tests",
        "static-analysis",
        "vulnerability-scan",
        "secrets-scan",
        "artifact-generation",
    },
}
ALLOWED: dict[str, set[str]] = {
    "Project": {
        "description",
        "workflow",
        "requirements",
        "gates",
        "metrics",
        "documentation",
        "reports",
        "roles",
        "approvalPolicies",
    },
    "Requirement": {
        "statement",
        "priority",
        "qualityCharacteristic",
        "qualitySubcharacteristic",
        "owner",
        "target",
        "documentation",
        "reports",
    },
    "QualityCharacteristic": {"model"},
    "QualitySubcharacteristic": {"characteristic"},
    "Workflow": {"stages"},
    "Stage": {
        "type",
        "environment",
        "reviewScope",
        "activities",
        "description",
        "dependsOn",
        "owner",
        "owners",
        "gates",
        "documentation",
        "reports",
        "approvalPolicy",
    },
    "Gate": {"rules", "failure"},
    "Metric": {
        "qualityCharacteristic",
        "qualitySubcharacteristic",
        "measurementFunction",
        "type",
        "unit",
        "description",
        "sourceHint",
    },
    "QualityMeasureElement": {"type", "unit", "measurementMethod", "description"},
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


def _strict_mapping(value: Any, allowed: set[str], context: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ValueError(f"{context} must be a mapping")
    unknown = set(value) - allowed
    if unknown:
        raise ValueError(f"{context} contains unknown field {sorted(unknown)[0]!r}")
    return value


def parse(data: str | bytes) -> Resource:
    payload = yaml.safe_load(data)
    top = _strict_mapping(
        payload, {"specVersion", "kind", "metadata", "spec"}, "resource"
    )
    version, kind = top.get("specVersion"), top.get("kind")
    if version != "0.1":
        raise ValueError(f"unsupported specVersion {version!r}")
    if kind not in KINDS:
        raise ValueError(f"unsupported kind {kind!r}")
    metadata = _strict_mapping(
        top.get("metadata"), {"id", "name", "description", "labels"}, "metadata"
    )
    spec = _strict_mapping(top.get("spec"), ALLOWED[kind], "spec")
    return Resource(version, kind, metadata, spec)


def parse_state(data: str | bytes) -> dict[str, Any]:
    value = _strict_mapping(
        yaml.safe_load(data) or {},
        {"metrics", "stages", "approvals", "documentation", "reports"},
        "state",
    )
    return {
        "metrics": value.get("metrics") or {},
        "stages": value.get("stages") or {},
        "approvals": value.get("approvals") or {},
        "documentation": value.get("documentation") or {},
        "reports": value.get("reports") or {},
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
    if not spec.get("requirements"):
        add("Project.spec.requirements must not be empty")
    for key, kind, source in [
        ("requirements", "Requirement", bundle.requirements),
        ("gates", "Gate", bundle.gates),
        ("metrics", "Metric", bundle.metrics),
        ("roles", "Role", bundle.roles),
        ("approvalPolicies", "ApprovalPolicy", bundle.approval_policies),
    ]:
        refs(spec.get(key, []), kind, source)
    artifact_refs(spec.get("documentation", []), "documentation")
    artifact_refs(spec.get("reports", []), "report")
    for resource_id, workflow in bundle.workflows.items():
        if not workflow.spec.get("stages"):
            add(f"Workflow {resource_id!r} has no stages")
        refs(workflow.spec.get("stages", []), "Stage", bundle.stages)
    for resource_id, stage in bundle.stages.items():
        s = stage.spec
        stage_type = s.get("type")
        if stage_type not in STAGE_TYPES:
            add(
                f"Stage {resource_id!r} has invalid type {stage_type!r}; "
                f"expected one of {', '.join(sorted(STAGE_TYPES))}"
            )
        invalid_activities = set(s.get("activities", [])) - STAGE_ACTIVITIES.get(
            stage_type, set()
        )
        if invalid_activities:
            add(
                f"Stage {resource_id!r} has unsupported activities for "
                f"{stage_type!r}: {', '.join(sorted(invalid_activities))}"
            )
        if stage_type == "refinement":
            if not s.get("owners"):
                add(f"Stage {resource_id!r} requires at least one owner")
            if not s.get("documentation"):
                add(
                    f"Stage {resource_id!r} requires at least one documentation reference"
                )
        if stage_type == "deploy" and not s.get("environment"):
            add(f"Stage {resource_id!r} of type 'deploy' requires environment")
        if stage_type == "review" and not s.get("reviewScope"):
            add(f"Stage {resource_id!r} of type 'review' requires reviewScope")
        if stage_type == "review" and not s.get("approvalPolicy"):
            add(f"Stage {resource_id!r} of type 'review' requires approvalPolicy")
        refs(s.get("dependsOn", []), "Stage", bundle.stages)
        refs(s.get("gates", []), "Gate", bundle.gates)
        artifact_refs(s.get("documentation", []), "documentation")
        artifact_refs(s.get("reports", []), "report")
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
        refs(
            [s.get("qualityCharacteristic", "")],
            "QualityCharacteristic",
            bundle.quality_characteristics,
        )
        refs(
            [s.get("qualitySubcharacteristic", "")],
            "QualitySubcharacteristic",
            bundle.quality_subcharacteristics,
        )
        sub = bundle.quality_subcharacteristics.get(
            s.get("qualitySubcharacteristic", "")
        )
        if sub and sub.spec.get("characteristic") != s.get("qualityCharacteristic"):
            add(
                f"Requirement {resource_id!r} characteristic does not match its subcharacteristic"
            )
        if s.get("target"):
            refs([s["target"].get("metric", "")], "Metric", bundle.metrics)
        if s.get("owner"):
            refs([s["owner"]], "Role", bundle.roles)
        artifact_refs(s.get("documentation", []), "documentation")
        artifact_refs(s.get("reports", []), "report")
    valid_operators = {
        "equals",
        "notEquals",
        "greaterThan",
        "greaterThanOrEqual",
        "lessThan",
        "lessThanOrEqual",
        "exists",
        "approved",
    }
    for resource_id, gate in bundle.gates.items():
        if not gate.spec.get("rules"):
            add(f"Gate {resource_id!r} has no rules")
        if gate.spec.get("failure", {}).get("action") not in {"block", "warn"}:
            add(
                f"Gate {resource_id!r} has invalid failure action {gate.spec.get('failure', {}).get('action', '')!r}"
            )
        for rule in gate.spec.get("rules", []):
            refs([rule.get("metric", "")], "Metric", bundle.metrics)
            if rule.get("operator") not in valid_operators:
                add(
                    f"Gate {resource_id!r} uses invalid operator {rule.get('operator', '')!r}"
                )
    for resource_id, policy in bundle.approval_policies.items():
        s = policy.spec
        refs(s.get("approvers", []), "Role", bundle.roles)
        if s.get("strategy") not in {"all", "any", "minimum"}:
            add(
                f"ApprovalPolicy {resource_id!r} has invalid strategy {s.get('strategy', '')!r}"
            )
        if s.get("strategy") == "minimum" and not (
            1 <= s.get("minimum", 0) <= len(s.get("approvers", []))
        ):
            add(f"ApprovalPolicy {resource_id!r} has unsatisfiable minimum")
    for resource_id, metric in bundle.metrics.items():
        if metric.spec.get("type") not in {
            "integer",
            "number",
            "percentage",
            "boolean",
            "duration",
            "string",
        }:
            add(
                f"Metric {resource_id!r} has invalid type {metric.spec.get('type', '')!r}"
            )
    for resource_id, artifact in bundle.artifacts.items():
        if artifact.spec.get("category") not in {"documentation", "report"}:
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
    for resource_id in bundle.project.spec.get("requirements", []):
        requirement = bundle.requirements[resource_id]
        check = Check(resource_id, requirement.name, True)
        target = requirement.spec.get("target")
        if target:
            check.passed, check.reason = _compare(
                state["metrics"],
                target.get("metric"),
                target.get("operator"),
                target.get("value"),
            )
        for field, label in (("documentation", "documentation"), ("reports", "report")):
            for evidence_id in requirement.spec.get(field, []):
                if state[field].get(evidence_id):
                    continue
                check.passed = False
                check.reason = "; ".join(
                    filter(None, [check.reason, f"missing {label} {evidence_id}"])
                )
        report.requirements.append(check)
        report.ready &= check.passed
    gate_cache: dict[str, Check] = {}
    for stage_id in workflow.spec.get("stages", []):
        stage = bundle.stages[stage_id]
        status = state["stages"].get(stage_id, "pending") or "pending"
        result = StageResult(stage_id, stage.name, status)
        if status in {"running", "blocked"}:
            active_stages.append(stage.name)
        elif status == "pending":
            pending_stages.append(stage.name)
        for gate_id in stage.spec.get("gates", []):
            if gate_id not in gate_cache:
                gate = bundle.gates[gate_id]
                failures = []
                warning = gate.spec.get("failure", {}).get("action") == "warn"
                for rule in gate.spec.get("rules", []):
                    ok, reason = _compare(
                        state["metrics"],
                        rule.get("metric"),
                        rule.get("operator"),
                        rule.get("value"),
                    )
                    failures += [] if ok else [reason]
                gate_cache[gate_id] = Check(
                    gate_id, gate.name, not failures, warning, "; ".join(failures)
                )
                report.gates.append(gate_cache[gate_id])
            check = gate_cache[gate_id]
            result.gates.append(check)
            if not check.passed and not check.warning:
                report.ready = False
        for field, checks, label in (
            ("documentation", result.documentation, "documentation"),
            ("reports", result.reports, "report"),
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
