# Open Quality documentation

Open Quality is a vendor-neutral format for describing software-quality
expectations as version-controlled, declarative resources.

Use this documentation to learn the model, author a Quality Contract, validate
it with the reference CLI, and understand the boundaries of the `0.1`
specification.

## Start here

- [Quick start](quick-start.md): install the CLI and run the minimal contract.
- [Concepts](concepts.md): understand Quality as Code, contracts, resources,
  references, and validation.
- [Resources](resources.md): learn the core resources and how they connect.
- [CLI reference](cli.md): validate, render, evaluate, plan, and apply.

## Build a contract

1. [Syntax](syntax.md): authoring rules for YAML and JSON resources.
2. [Workflows and stages](workflows.md): model the quality process.
3. [Quality measures](metrics.md): define targets and observations.
4. [Artifacts](artifacts.md): connect requirements to refinement documents.
5. [Roles and approvals](approvals.md): express ownership and decisions.
6. [Providers](providers.md): connect a contract to external systems without
   coupling the core model to a vendor.

## Operate and extend

- [Evaluation](evaluation.md): understand state snapshots and readiness.
- [Versioning](versioning.md): manage specification and contract evolution.
- [Reference implementation](../IMPLEMENTATION.md): see the CLI architecture
  and provider behavior.
- [Normative specification](../SPECIFICATION.md): read the complete `0.1`
  contract.

## What Open Quality is

Open Quality defines the portable description of quality. It does not prescribe
how a team runs tests, stores approvals, provisions projects, or collects
telemetry. Those behaviors belong to implementations that consume the
contract.

```text
Quality Contract
├── quality requirements ── quality measures ── observations
├── workflow ── stages ── dependencies
├── artifacts ── refinement evidence
└── roles ── approval policies
```
