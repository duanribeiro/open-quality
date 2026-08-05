from __future__ import annotations

import argparse
import sys
from pathlib import Path

from . import renderer
from .core import evaluate, load_contract, load_state, validate
from .provider import (
    OpenProjectClient,
    apply,
    load_config,
    load_state as load_provider_state,
    plan,
    save_state,
)


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
    parser.add_argument("--state")
    parser.add_argument("directory", nargs="?")
    values = parser.parse_args(args)
    if not values.target or not values.directory:
        raise ValueError(
            f"usage: oq {'apply' if is_apply else 'plan'} --target <target.yaml> [--state <state.json>] <quality-directory>"
        )
    config = load_config(values.target)
    state_path = values.state or values.target + ".state.json"
    state = load_provider_state(state_path, config.name)
    operations = plan(_valid(values.directory), state, config)
    print(
        "Open Quality provider plan\n\nProvider: openproject\nTarget: "
        + config.name
        + "\n"
    )
    for item in operations:
        print(
            ("=" if item.action == "no-op" else "+")
            + f" {item.action:<7} {item.kind:<12} {item.subject}"
        )
    print(
        f"\nPlan: {sum(item.action == 'create' for item in operations)} to create, {sum(item.action == 'update' for item in operations)} to update, {sum(item.action == 'no-op' for item in operations)} unchanged"
    )
    if is_apply:
        apply(operations, state, OpenProjectClient(config, config.token()))
        save_state(state_path, state)
        print(
            f"\nApplied {sum(item.action != 'no-op' for item in operations)} resource(s); state saved to {state_path}"
        )
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
            for item in bundle.evidence.values()
        )
        report_count = sum(
            item.spec.get("category") == "report" for item in bundle.evidence.values()
        )
        print(
            f"PASS {bundle.project.name}\n\n1 Project\n{len(bundle.workflows)} Workflow(s)\n{len(bundle.requirements)} Requirement(s)\n{len(bundle.stages)} Stage(s)\n{len(bundle.gates)} Gate(s)\n{len(bundle.metrics)} Metric(s)\n{documentation_count} Documentation definition(s)\n{report_count} Report definition(s)\n{len(bundle.roles)} Role(s)\n{len(bundle.approval_policies)} Approval policy(s)"
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
