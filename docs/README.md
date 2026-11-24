# Open Quality documentation

Open Quality is a vendor-neutral format for describing software-quality
expectations as version-controlled, declarative resources.

Use this documentation to learn the model, author a Quality Contract, validate
it with the reference CLI, and understand the boundaries of the `0.1`
specification.

## Get started

- [Quick start](quick-start.md): install the CLI and run the minimal contract.

## Model

| Kind | Related documentation |
|---|---|
| `QualityContract` | [Concepts](concepts.md), [Resources](resources.md), [Syntax](syntax.md), [Versioning](versioning.md) |
| `Workflow` | [Workflows and stages](workflows.md) |
| `QualityRequirement` | [Quality measures](metrics.md), [Evaluation](evaluation.md) |
| `Stage` | [Workflows and stages](workflows.md), [Evaluation](evaluation.md) |
| `QualityMeasure` | [Quality measures](metrics.md) |
| `QualityMeasureElement` | [Quality measures](metrics.md) |
| `Documentation` | [Documentation resources](artifacts.md) |
| `Role` | [Roles and approvals](approvals.md) |
| `ApprovalPolicy` | [Roles and approvals](approvals.md) |

## Reference

- [CLI reference](cli.md): validate, render, evaluate, plan, and apply.
- [Providers](providers.md): connect a contract to external systems without
  coupling the core model to a vendor.

## Project documents

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
