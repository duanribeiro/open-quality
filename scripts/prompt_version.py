"""Prompt for and update the next stable package version in pyproject.toml."""

from __future__ import annotations

import re
import sys
from pathlib import Path


PROJECT_FILE = Path(__file__).parents[1] / "pyproject.toml"
VERSION_LINE = re.compile(r'(?m)^version\s*=\s*"([^"]+)"\s*$')
STABLE_VERSION = re.compile(
    r"^(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)$"
)


def main() -> int:
    content = PROJECT_FILE.read_text()
    match = VERSION_LINE.search(content)
    if not match:
        print("Could not find project version in pyproject.toml.", file=sys.stderr)
        return 1

    current = match.group(1)
    current_parts = STABLE_VERSION.fullmatch(current)
    if not current_parts:
        print(
            f"Current version {current!r} is not a stable MAJOR.MINOR.PATCH version.",
            file=sys.stderr,
        )
        return 1

    print(f"Current version: {current}")
    proposed = input("Enter the next version (MAJOR.MINOR.PATCH): ").strip()
    proposed_parts = STABLE_VERSION.fullmatch(proposed)
    if not proposed_parts:
        print(
            "Version must use MAJOR.MINOR.PATCH, for example 0.2.1.",
            file=sys.stderr,
        )
        return 1

    if tuple(map(int, proposed_parts.groups())) <= tuple(
        map(int, current_parts.groups())
    ):
        print(f"Next version must be greater than {current}.", file=sys.stderr)
        return 1

    updated = VERSION_LINE.sub(f'version = "{proposed}"', content, count=1)
    PROJECT_FILE.write_text(updated)
    print(f"Updated pyproject.toml to version {proposed}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
