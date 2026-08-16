"""Backward-compatible provider facade.

Provider implementations live in :mod:`cli.providers`. New code should import
the concrete adapter from ``cli.providers.openproject`` or program against the
contracts in ``cli.providers.interfaces``.
"""

from .providers.openproject import (
    ExternalResource,
    OpenProjectClient,
    OpenProjectProvider,
    Operation,
    ProjectMember,
    ProviderState,
    TargetConfig,
    apply,
    load_config,
    load_members,
    load_state,
    new_state,
    plan,
    save_state,
)

__all__ = [
    "ExternalResource",
    "OpenProjectClient",
    "OpenProjectProvider",
    "Operation",
    "ProjectMember",
    "ProviderState",
    "TargetConfig",
    "apply",
    "load_config",
    "load_members",
    "load_state",
    "new_state",
    "plan",
    "save_state",
]
