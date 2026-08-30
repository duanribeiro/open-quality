from __future__ import annotations

import argparse
import sys
from pathlib import Path

from . import renderer
from .core import evaluate, load_contract, load_state, validate
from .provider import (
    ExternalResource,
    OpenProjectClient,
    OpenProjectProvider,
    apply,
    load_config,
    load_members,
    load_state as load_provider_state,
    plan,
    save_state,
)
from .providers import github, gitlab, jira_cloud
import yaml


def _valid(path: str):
    bundle = load_contract(path)
    errors = validate(bundle)
    if errors:
        for error in errors:
            print("-", error, file=sys.stderr)
        raise ValueError(f"contract has {len(errors)} validation error(s)")
    return bundle


def _provider(args: list[str], is_apply: bool) -> int:
    parser = argparse.ArgumentParser(
        prog=f"oq {'apply' if is_apply else 'plan'}", add_help=False
    )
    parser.add_argument("--target")
    parser.add_argument("--provider-role")
    parser.add_argument("--state")
    parser.add_argument("--members")
    parser.add_argument("directory", nargs="?")
    values = parser.parse_args(args)
    if not values.target or not values.directory:
        raise ValueError(
            f"usage: oq {'apply' if is_apply else 'plan'} --target <target.yaml> [--state <state.json>] <quality-directory>"
        )
    target_document = yaml.safe_load(Path(values.target).read_text()) or {}
    provider_role = values.provider_role
    if "providers" in target_document:
        providers = target_document["providers"]
        if not isinstance(providers, dict):
            raise ValueError("providers must be a mapping")
        if not provider_role:
            raise ValueError("--provider-role is required when project file contains providers")
        target_document = providers.get(provider_role)
        if not isinstance(target_document, dict):
            raise ValueError(f"provider role {provider_role!r} was not found")
    elif provider_role:
        raise ValueError("--provider-role is only valid for a project file with providers")
    target_provider = target_document.get("provider")
    if target_provider == "jira-cloud":
        return _jira_provider(values, is_apply, target_document, provider_role)
    if target_provider == "github":
        config = github.load_config(target_document, provider_role)
        bundle = _valid(values.directory)
        provider_config = target_document.get("config") or {}
        members_path = values.members or config.members_file
        if "members" in provider_config and not values.members:
            members = github.load_members({"provider": "github", "members": provider_config["members"]})
        elif members_path and not Path(members_path).is_absolute():
            members_path = str(Path(values.target).parent / members_path)
            members = github.load_members(members_path)
        else:
            members = github.load_members(members_path) if members_path else []
        print(f"Open Quality provider plan\n\nProvider: github\nRole: {config.name}\n")
        print(f"  ENSURE  GitHubRepository   {config.owner}/{config.repository}")
        for member in members:
            print(f"  INVITE  GitHubCollaborator {member.username} ({member.permission})")
        if is_apply:
            print(f"\nApplied GitHub provisioning for {github.apply(config, members)} repository/repositories.")
        return 0
    if target_provider == "gitlab":
        config = gitlab.load_config(target_document, provider_role)
        bundle = _valid(values.directory)
        members = gitlab.load_members((target_document.get("config") or {}))
        print(f"Open Quality provider plan\n\nProvider: gitlab\nRole: {config.name}\n")
        print(f"  ENSURE  GitLabProject      {config.project}")
        for member in members: print(f"  INVITE  GitLabMember       {member.username} ({member.access_level})")
        if is_apply: print(f"\nApplied GitLab provisioning for {gitlab.apply(config, members)} project(s).")
        return 0
    config = load_config(target_document, provider_role)
    provider_config = target_document.get("config") or {}
    members_path = values.members or config.members_file
    if "members" in provider_config and not values.members:
        members = load_members({"provider": "openproject", "members": provider_config["members"]})
    elif members_path and not Path(members_path).is_absolute():
        members_path = str(Path(values.target).parent / members_path)
        members = load_members(members_path)
    else:
        members = load_members(members_path) if members_path else []
    state_path = values.state or values.target + (f".{provider_role}" if provider_role else "") + ".state.json"
    state = load_provider_state(state_path, config.name)
    bundle = _valid(values.directory)
    existing_project = None
    provider = None
    client = None
    if is_apply:
        provider = OpenProjectProvider(config, config.token())
        client = provider.client
        if bundle.project and bundle.project.id not in state.resources:
            existing_project = client.find_project(bundle.project.id)
    operations = provider.plan(bundle, state, members) if provider else plan(bundle, state, config, members)
    if existing_project and bundle.project:
        project = next(item for item in operations if item.resource_id == bundle.project.id)
        project.action = "no-op"
        state.resources[bundle.project.id] = ExternalResource(
            bundle.project.id, "QualityContract", existing_project[0], existing_project[1], project.hash, ""
        )
    print(
        "Open Quality provider plan\n\nProvider: "
        + config.provider
        + "\nRole: "
        + config.name
        + "\n"
    )
    groups = (
        ("Provisionamento", {"QualityContract", "KanbanBoard", "ProjectMember"}),
        ("Workflow", {"QualityRequirement", "Stage"}),
        ("Revisão", {"CodeReviewer"}),
    )
    displayed: set[str] = set()
    for title, kinds in groups:
        selected = [item for item in operations if item.kind in kinds]
        if not selected:
            continue
        print(f"\n{title}")
        for item in selected:
            displayed.add(item.resource_id)
            print(f"  {item.action.upper():<7} {item.kind:<18} {item.subject}")
    for item in operations:
        if item.resource_id not in displayed:
            print(f"  {item.action.upper():<7} {item.kind:<18} {item.subject}")
    print(
        f"\nPlan: {sum(item.action == 'create' for item in operations)} to create, {sum(item.action == 'update' for item in operations)} to update, {sum(item.action == 'no-op' for item in operations)} unchanged"
    )
    if is_apply:
        assert client is not None
        provider.apply(operations, state, lambda current: save_state(state_path, current))
        print(
            f"\nApplied {sum(item.action != 'no-op' for item in operations)} resource(s); state saved to {state_path}"
        )
    return 0


def _jira_provider(values, is_apply: bool, target_document=None, provider_role="") -> int:
    config = jira_cloud.load_config(target_document or values.target, provider_role)
    provider_config = (target_document or {}).get("config") or {}
    members_path = values.members or config.members_file
    if "members" in provider_config and not values.members:
        members = jira_cloud.load_members({"provider": "jira-cloud", "members": provider_config["members"]})
    else:
        if members_path and not Path(members_path).is_absolute(): members_path = str(Path(values.target).parent / members_path)
        members = jira_cloud.load_members(members_path) if members_path else []
    state_path = values.state or values.target + (f".{provider_role}" if provider_role else "") + ".state.json"
    state = jira_cloud.load_state(state_path, config.name)
    bundle = _valid(values.directory)
    ops = jira_cloud.plan(bundle, state, config, members)
    print(f"Open Quality provider plan\n\nProvider: jira-cloud\nRole: {config.name}\n")
    for op in ops: print(f"  {op.action.upper():<7} {op.kind:<18} {op.subject}")
    print(f"\nPlan: {sum(x.action=='create' for x in ops)} to create, {sum(x.action=='update' for x in ops)} to update, {sum(x.action=='no-op' for x in ops)} unchanged")
    if is_apply:
        email, token = config.credentials(); jira_cloud.apply(ops, state, jira_cloud.JiraClient(config,email,token), config, lambda current: jira_cloud.save_state(state_path,current))
        print(f"\nApplied {sum(x.action != 'no-op' for x in ops)} resource(s); state saved to {state_path}")
    return 0


def run(args: list[str]) -> int:
    if not args:
        raise ValueError("usage: oq <validate|graph|evaluate|status|plan|apply> ...")
    command, rest = args[0], args[1:]
    if command in {"plan", "apply"}:
        return _provider(rest, command == "apply")
    if command == "validate":
        if len(rest) != 1:
            raise ValueError("usage: oq validate <quality-directory>")
        bundle = _valid(rest[0])
        documentation_count = sum(
            item.spec.get("category") == "documentation"
            for item in bundle.artifacts.values()
        )
        print(
            f"PASS {bundle.project.name}\n\n1 QualityContract\n{len(bundle.workflows)} Workflow(s)\n{len(bundle.requirements)} Requirement(s)\n{len(bundle.stages)} Stage(s)\n{len(bundle.metrics)} QualityMeasure(s)\n{documentation_count} Documentation definition(s)\n{len(bundle.roles)} Role(s)\n{len(bundle.approval_policies)} Approval policy(s)"
        )
        return 0
    if command == "graph":
        parser = argparse.ArgumentParser(prog="oq graph", add_help=False)
        parser.add_argument("--format", default="both")
        parser.add_argument("directory", nargs="?")
        values = parser.parse_args(rest)
        if not values.directory:
            raise ValueError(
                "usage: oq graph [--format ascii|mermaid|both] <quality-directory>"
            )
        bundle = _valid(values.directory)
        if values.format == "ascii":
            print(renderer.ascii(bundle), end="")
        elif values.format == "mermaid":
            print(renderer.mermaid(bundle), end="")
        elif values.format == "both":
            print(
                renderer.ascii(bundle)
                + "\n```mermaid\n"
                + renderer.mermaid(bundle)
                + "```"
            )
        else:
            raise ValueError(f"unknown graph format {values.format!r}")
        return 0
    if command in {"evaluate", "status"}:
        if not 1 <= len(rest) <= 2:
            raise ValueError(f"usage: oq {command} <quality-directory> [state.yaml]")
        state_path = (
            rest[1] if len(rest) == 2 else str(Path(rest[0]).parent / "state.yaml")
        )
        report = evaluate(_valid(rest[0]), load_state(state_path))
        print(
            (
                renderer.evaluation(report)
                if command == "evaluate"
                else renderer.status(report)
            ),
            end="",
        )
        return 0 if command == "status" or report.ready else 2
    raise ValueError("usage: oq <validate|graph|evaluate|status|plan|apply> ...")


def main() -> None:
    try:
        sys.exit(run(sys.argv[1:]))
    except Exception as error:
        print("error:", error, file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
