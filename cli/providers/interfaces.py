"""Provider contracts shared by every external-system adapter."""

from __future__ import annotations

from pathlib import Path
from typing import Protocol, Sequence

from ..model import Bundle


class ProviderAdapter(Protocol):
    """Plans and materializes a quality bundle in an external provider."""

    name: str

    def plan(self, bundle: Bundle, state: object) -> Sequence[object]:
        """Compute the operations needed to bring the provider in line with `bundle`."""
        ...

    def apply(self, operations: Sequence[object], state: object) -> object:
        """Execute `operations` against the provider and return the updated state."""
        ...


class TargetLoader(Protocol):
    """Loads provider-specific target configuration from a YAML document."""

    def load(self, path: str | Path) -> object:
        """Load and validate a provider target document from `path`."""
        ...
