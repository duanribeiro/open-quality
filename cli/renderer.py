from __future__ import annotations

from .model import Bundle, Check, Report


def mermaid(bundle: Bundle) -> str:
    """Render the workflow's stage dependency graph as a Mermaid flowchart."""
    assert bundle.project
    workflow = bundle.workflows[bundle.project.spec["workflow"]]
    lines = ["flowchart LR"]
    for stage_id in workflow.spec["stages"]:
        stage = bundle.stages[stage_id]
        escaped_name = stage.name.replace('"', '\\"')
        lines.append(f'    n_{stage_id.replace("-", "_")}["{escaped_name}"]')
        lines.extend(
            f"    n_{dependency.replace('-', '_')} --> n_{stage_id.replace('-', '_')}"
            for dependency in stage.spec.get("dependsOn", [])
        )
    return "\n".join(lines) + "\n"


def ascii(bundle: Bundle) -> str:
    """Render the workflow's stages as a plain-text dependency list."""
    assert bundle.project
    stages = bundle.workflows[bundle.project.spec["workflow"]].spec["stages"]
    lines = ["Stage dependency graph (list order does not define execution order)"]
    for stage_id in stages:
        stage = bundle.stages[stage_id]
        depends = stage.spec.get("dependsOn", [])
        lines.append(
            f"[{stage.name}]" + (f" (after {', '.join(depends)})" if depends else "")
        )
    return "\n".join(lines) + "\n"


def _check(check: Check) -> str:
    """Render one Check as an icon, name, and optional failure reason."""
    icon = "✓" if check.passed else "!" if check.warning else "✗"
    return (
        f"{icon} {check.name}" + (f" — {check.reason}" if check.reason else "") + "\n"
    )


def _status_icon(status: str) -> str:
    """Return the icon for a stage status, defaulting to "○" for pending."""
    return {"completed": "✓", "running": "▶", "blocked": "✗"}.get(status, "○")


def evaluation(report: Report) -> str:
    """Render a full evaluation report: requirement and stage-by-stage checks."""
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
        if stage.approval:
            lines.append("    approval: " + _check(stage.approval).rstrip("\n"))
        lines.extend(
            "    documentation: " + _check(item).rstrip("\n")
            for item in stage.documentation
        )
    lines.extend(["", "Overall: " + ("READY" if report.ready else "NOT READY")])
    return "\n".join(lines) + "\n"


def status(report: Report) -> str:
    """Render a compact status summary grouped by stage status."""
    lines = [
        f"QualityContract: {report.project}",
        f"Workflow: {report.workflow}",
        f"Current / active stages: {report.current_stage}",
        "",
    ]
    for state in ("completed", "running", "blocked", "pending"):
        names = sorted(item.name for item in report.stages if item.status == state)
        if names:
            lines.append(f"{_status_icon(state)} {state.title()}")
            lines.extend(f"  - {name}" for name in names)
    return "\n".join(lines) + "\n"
