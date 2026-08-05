from __future__ import annotations

from .model import Bundle, Check, Report


def mermaid(bundle: Bundle) -> str:
    assert bundle.project
    workflow = bundle.workflows[bundle.project.spec["workflow"]]
    lines = ["flowchart LR"]
    for stage_id in workflow.spec["stages"]:
        stage = bundle.stages[stage_id]
        lines.append(
            f'    n_{stage_id.replace("-", "_")}["{stage.name.replace(chr(34), r"\"")}"]'
        )
        lines.extend(
            f"    n_{dependency.replace('-', '_')} --> n_{stage_id.replace('-', '_')}"
            for dependency in stage.spec.get("dependsOn", [])
        )
    return "\n".join(lines) + "\n"


def ascii(bundle: Bundle) -> str:
    assert bundle.project
    stages = bundle.workflows[bundle.project.spec["workflow"]].spec["stages"]
    lines: list[str] = []
    for index, stage_id in enumerate(stages):
        stage = bundle.stages[stage_id]
        depends = stage.spec.get("dependsOn", [])
        lines.append(
            f"[{stage.name}]" + (f" (after {', '.join(depends)})" if depends else "")
        )
        if index < len(stages) - 1:
            lines.extend(["   │", "   ▼"])
    return "\n".join(lines) + "\n"


def _check(check: Check) -> str:
    icon = "✓" if check.passed else "!" if check.warning else "✗"
    return (
        f"{icon} {check.name}" + (f" — {check.reason}" if check.reason else "") + "\n"
    )


def _status_icon(status: str) -> str:
    return {"completed": "✓", "running": "▶", "blocked": "✗"}.get(status, "○")


def evaluation(report: Report) -> str:
    lines = [
        f"Quality evaluation: {report.project}",
        f"Workflow: {report.workflow}",
        "",
        "Requirements",
    ]
    lines.extend(_check(item).rstrip("\n") for item in report.requirements)
    lines.extend(["", "Stages"])
    for stage in report.stages:
        lines.append(
            f"{_status_icon(stage.status)} {stage.status.upper():<12} {stage.name}"
        )
        lines.extend("    gate: " + _check(item).rstrip("\n") for item in stage.gates)
        if stage.approval:
            lines.append("    approval: " + _check(stage.approval).rstrip("\n"))
        lines.extend(
            "    documentation: " + _check(item).rstrip("\n")
            for item in stage.documentation
        )
        lines.extend(
            "    report: " + _check(item).rstrip("\n") for item in stage.reports
        )
    lines.extend(["", "Overall: " + ("READY" if report.ready else "NOT READY")])
    return "\n".join(lines) + "\n"


def status(report: Report) -> str:
    lines = [
        f"Project: {report.project}",
        f"Workflow: {report.workflow}",
        f"Current stage: {report.current_stage}",
        "",
    ]
    for state in ("completed", "running", "blocked", "pending"):
        names = sorted(item.name for item in report.stages if item.status == state)
        if names:
            lines.append(f"{_status_icon(state)} {state.title()}")
            lines.extend(f"  - {name}" for name in names)
    return "\n".join(lines) + "\n"
