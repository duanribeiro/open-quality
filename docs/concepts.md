# Concepts

## Quality as Code

Quality as Code is a methodology: quality expectations and governance are expressed as declarative, reviewable, version-controlled artifacts.

## Open Quality

Open Quality is the open specification in this repository. It defines interoperable resource shapes and semantics without requiring a particular platform.

## Quality Contract

A Quality Contract is the complete set of resources that describes quality for one project. Its `Project` entry point organizes quality as characteristic → subcharacteristic → requirement, and references the workflow, stages, metrics, documentation, roles, and approval policies.

```text
Project
├── Requirement ── Metric / Documentation
├── Workflow ── Stage
└── Role ── ApprovalPolicy
```

The contract is desired governance, not an execution log. Runtime state, measurements, documentation files, and approval events belong to implementations.

## Resource and reference

A resource is one YAML or JSON document with `specVersion`, `kind`, `metadata`, and `spec`. Resources refer to each other by contract-unique `metadata.id`; directory layout has no semantic effect.

## Structural and semantic validation

Structural validation checks document shape with JSON Schema. Semantic validation checks relationships across documents, such as missing roles, incompatible metrics, duplicate IDs, or cyclic stage dependencies.
