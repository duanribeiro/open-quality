# Contributing

Open Quality welcomes discussion, examples, documentation fixes, schema improvements, and implementation feedback.

## Before proposing a change

1. Read the manifesto, principles, and current specification.
2. Search existing issues and proposals.
3. Explain the real quality-management use case, not only the desired YAML shape.
4. Show whether the proposal can be modeled by composing existing resources.

## Change types

- Editorial corrections may be submitted directly.
- Compatible schema clarifications should include valid and invalid fixtures.
- New fields or semantics that affect interoperability require a public proposal.
- New core resources require a public proposal and evidence from more than one domain.

## Pull request expectations

A specification change should update, as applicable:

- `SPECIFICATION.md`;
- the versioned JSON Schemas;
- at least one example;
- documentation;
- `CHANGELOG.md`;
- migration notes for breaking changes.

Use clear commits and avoid mixing unrelated changes. Contributions must be compatible with the repository license.

## Design criteria

Proposals are evaluated for clarity, portability, minimality, composability, implementability, and alignment with the principles. Provider-specific behavior belongs in adapters or extensions rather than the core.
