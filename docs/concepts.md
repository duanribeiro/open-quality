# Concepts

This page explains the ideas behind Open Quality before going into YAML
details. Start with [Quick start](quick-start.md) if you want to run the
example first.

## Quality as Code

Quality as Code is a methodology: quality expectations and governance are
expressed as declarative, reviewable, version-controlled artifacts.

The important shift is from “quality is checked somewhere in a pipeline” to
“quality expectations are explicit inputs to the delivery process”. A contract
can therefore be reviewed alongside the code and changed through the same
version-control workflow.

## Open Quality

Open Quality is the open specification in this repository. It defines interoperable resource shapes and semantics without requiring a particular platform.

## Quality Contract

A Quality Contract is the complete set of resources that describes quality for one project. Its `QualityContract` entry point organizes quality as characteristic → subcharacteristic → requirement, and references the workflow, stages, metrics, documentation, roles, and approval policies.

```text
QualityContract
├── Requirement ── Metric / Documentation
├── Workflow ── Stage
└── Role ── ApprovalPolicy
```

The contract is desired governance, not an execution log. QualityMeasureElement
resources retain timestamped measurement values; other runtime state,
documentation files, and approval events belong to implementations.

## Declaration versus execution

Open Quality defines what a team expects and how those expectations relate.
An implementation decides how to execute a stage, collect a metric, store an
approval, or connect a person to a role.

This boundary keeps the contract portable:

```text
Open Quality contract  ->  implementation  ->  runtime state
requirements, stages       CI, provider,       observations,
and policies               dashboard, CLI      approvals, status
```

The reference CLI adds a local state snapshot only to make evaluation
repeatable. That snapshot is an implementation detail, not an extension to the
portable resource model.

## Resource and reference

A resource is one YAML or JSON document with `specVersion`, `kind`, `metadata`, and `spec`. Resources refer to each other by contract-unique `metadata.id`; directory layout has no semantic effect.

## Structural and semantic validation

Structural validation checks document shape with JSON Schema. Semantic validation checks relationships across documents, such as missing roles, incompatible metrics, duplicate IDs, or cyclic stage dependencies.

Both layers matter. A document can have valid YAML and still be invalid as a
contract when a reference is missing or a workflow contains a cycle.

## What is intentionally excluded

Version `0.1` does not define test execution, deployment execution, provider
provisioning, dashboards, persistence, certification, waivers, or a scoring
model. These boundaries are intentional while the portable vocabulary is
being tested.
