"""`oq` command-line entry point.

Parses subcommands (validate/graph/evaluate/status/plan/apply) and dispatches
`plan`/`apply` to the target's provider adapter (OpenProject, GitHub, GitLab,
or Jira Cloud, under `cli.providers`).
"""

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
    """Load and validate a contract directory, printing errors before raising."""
    bundle = load_contract(path)
    errors = validate(bundle)
    if errors:
        for error in errors:
            print("-", error, file=sys.stderr)
        raise ValueError(f"contract has {len(errors)} validation error(s)")
    return bundle


def _parse_provider_args(args: list[str], is_apply: bool) -> argparse.Namespace:
    """Parse the shared plan/apply CLI arguments (--target, --state, ...)."""
    command = "apply" if is_apply else "plan"
    parser = argparse.ArgumentParser(prog=f"oq {command}", add_help=False)
    parser.add_argument("--target")
    parser.add_argument("--provider-role")
    parser.add_argument("--state")
    parser.add_argument("--members")
    parser.add_argument("directory", nargs="?")
    values = parser.parse_args(args)
    if not values.target or not values.directory:
        raise ValueError(
            f"usage: oq {command} --target <target.yaml> [--state <state.json>] <quality-directory>"
        )
    return values


def _select_provider_role(target_document: dict, provider_role: str) -> dict:
    """Resolve a project file to a single provider target.

    A project file either *is* a provider target directly, or declares a
    `providers` mapping of role name -> provider target, in which case
    `--provider-role` selects which one to use.
    """
    if "providers" not in target_document:
        if provider_role:
            raise ValueError(
                "--provider-role is only valid for a project file with providers"
            )
        return target_document
    providers = target_document["providers"]
    if not isinstance(providers, dict):
        raise ValueError("providers must be a mapping")
    if not provider_role:
        raise ValueError(
            "--provider-role is required when project file contains providers"
        )
    selected = providers.get(provider_role)
    if not isinstance(selected, dict):
        raise ValueError(f"provider role {provider_role!r} was not found")
    return selected


def _load_members(
    load_members_fn, provider_name: str, target_document: dict, config, values
):
    """Load provider members, either inline in the target or from a file.

    Shared by the providers whose target schema supports both an inline
    `config.members` list and an external `--members`/`membersFile` path
    (OpenProject, GitHub, Jira Cloud). GitLab only supports inline members.
    """
    provider_config = target_document.get("config") or {}
    members_path = values.members or config.members_file
    if "members" in provider_config and not values.members:
        return load_members_fn(
            {"provider": provider_name, "members": provider_config["members"]}
        )
    if members_path and not Path(members_path).is_absolute():
        members_path = str(Path(values.target).parent / members_path)
    return load_members_fn(members_path) if members_path else []


def _state_path(values: argparse.Namespace, provider_role: str) -> str:
    """Compute the default state-file path for a target, namespaced by role."""
    role_suffix = f".{provider_role}" if provider_role else ""
    return values.state or values.target + role_suffix + ".state.json"


def _print_plan_header(provider_name: str, role: str) -> None:
    """Print the "Provider: ... / Role: ..." header shared by plan and apply."""
    print(f"Open Quality provider plan\n\nProvider: {provider_name}\nRole: {role}\n")


def _print_operation(operation) -> None:
    """Print one planned operation as an "ACTION  KIND  SUBJECT" line."""
    print(f"  {operation.action.upper():<7} {operation.kind:<18} {operation.subject}")


def _print_plan_summary(operations) -> None:
    """Print the create/update/no-op counts for a list of operations."""
    print(
        f"\nPlan: {sum(item.action == 'create' for item in operations)} to create, "
        f"{sum(item.action == 'update' for item in operations)} to update, "
        f"{sum(item.action == 'no-op' for item in operations)} unchanged"
    )


def _github_provider(
    target_document: dict,
    provider_role: str,
    values: argparse.Namespace,
    is_apply: bool,
) -> int:
    """Plan or apply GitHub repository and collaborator provisioning."""
    config = github.load_config(target_document, provider_role)
    _valid(values.directory)
    members = _load_members(
        github.load_members, "github", target_document, config, values
    )
    _print_plan_header("github", config.name)
    print(f"  ENSURE  GitHubRepository   {config.owner}/{config.repository}")
    for member in members:
        print(f"  INVITE  GitHubCollaborator {member.username} ({member.permission})")
    if is_apply:
        print(
            f"\nApplied GitHub provisioning for {github.apply(config, members)} repository/repositories."
        )
    return 0


def _gitlab_provider(
    target_document: dict,
    provider_role: str,
    values: argparse.Namespace,
    is_apply: bool,
) -> int:
    """Plan or apply GitLab project and member provisioning."""
    config = gitlab.load_config(target_document, provider_role)
    _valid(values.directory)
    members = gitlab.load_members(target_document.get("config") or {})
    _print_plan_header("gitlab", config.name)
    print(f"  ENSURE  GitLabProject      {config.project}")
    for member in members:
        print(f"  INVITE  GitLabMember       {member.username} ({member.access_level})")
    if is_apply:
        print(
            f"\nApplied GitLab provisioning for {gitlab.apply(config, members)} project(s)."
        )
    return 0


def _openproject_provider(
    target_document: dict,
    provider_role: str,
    values: argparse.Namespace,
    is_apply: bool,
) -> int:
    """Plan or apply the full OpenProject work-package hierarchy for a contract."""
    config = load_config(target_document, provider_role)
    members = _load_members(
        load_members, "openproject", target_document, config, values
    )
    state_path = _state_path(values, provider_role)
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
    operations = (
        provider.plan(bundle, state, members)
        if provider
        else plan(bundle, state, config, members)
    )
    if existing_project and bundle.project:
        project = next(
            item for item in operations if item.resource_id == bundle.project.id
        )
        project.action = "no-op"
        state.resources[bundle.project.id] = ExternalResource(
            bundle.project.id,
            "QualityContract",
            existing_project[0],
            existing_project[1],
            project.hash,
            "",
        )
    _print_plan_header(config.provider, config.name)
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
            _print_operation(item)
    for item in operations:
        if item.resource_id not in displayed:
            _print_operation(item)
    _print_plan_summary(operations)
    if is_apply:
        assert client is not None
        provider.apply(
            operations, state, lambda current: save_state(state_path, current)
        )
        print(
            f"\nApplied {sum(item.action != 'no-op' for item in operations)} resource(s); state saved to {state_path}"
        )
    return 0


def _jira_provider(
    target_document: dict,
    provider_role: str,
    values: argparse.Namespace,
    is_apply: bool,
) -> int:
    """Plan or apply the Jira Cloud project and issue hierarchy for a contract."""
    config = jira_cloud.load_config(target_document, provider_role)
    members = _load_members(
        jira_cloud.load_members, "jira-cloud", target_document, config, values
    )
    state_path = _state_path(values, provider_role)
    state = jira_cloud.load_state(state_path, config.name)
    bundle = _valid(values.directory)
    operations = jira_cloud.plan(bundle, state, config, members)
    _print_plan_header("jira-cloud", config.name)
    for operation in operations:
        _print_operation(operation)
    _print_plan_summary(operations)
    if is_apply:
        email, token = config.credentials()
        jira_cloud.apply(
            operations,
            state,
            jira_cloud.JiraClient(config, email, token),
            config,
            lambda current: jira_cloud.save_state(state_path, current),
        )
        print(
            f"\nApplied {sum(item.action != 'no-op' for item in operations)} resource(s); state saved to {state_path}"
        )
    return 0


_PROVIDER_HANDLERS = {
    "github": _github_provider,
    "gitlab": _gitlab_provider,
    "jira-cloud": _jira_provider,
}


def _provider(args: list[str], is_apply: bool) -> int:
    """Parse plan/apply arguments and dispatch to the target's provider handler."""
    values = _parse_provider_args(args, is_apply)
    target_document = yaml.safe_load(Path(values.target).read_text()) or {}
    target_document = _select_provider_role(target_document, values.provider_role)
    handler = _PROVIDER_HANDLERS.get(
        target_document.get("provider"), _openproject_provider
    )
    return handler(target_document, values.provider_role, values, is_apply)


def run(args: list[str]) -> int:
    """Execute one `oq` subcommand and return its process exit code."""
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
    """CLI entry point: run `oq` with `sys.argv` and exit with its status code."""
    try:
        sys.exit(run(sys.argv[1:]))
    except Exception as error:
        print("error:", error, file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
