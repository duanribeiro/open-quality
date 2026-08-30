# Resources

Resources are the building blocks of a Quality Contract. Every resource uses
the same envelope:

```yaml
specVersion: "0.1"
kind: QualityRequirement
metadata:
  id: api-availability
  name: API availability
spec:
  statement: The API must remain available to customers.
  priority: critical
  qualityMeasures:
    - qualityMeasure: availability
      target:
        operator: greaterThanOrEqual
        value: 99.9
        unit: percent
```

## The contract entry point

`QualityContract` is the only required entry point. It names the active `Workflow` and
organizes `QualityRequirement` resources under quality characteristics and
optional subcharacteristics.

```text
QualityContract
├── quality ── QualityRequirement ── QualityMeasure
│                              └── Artifact
├── workflow ── Workflow ── Stage
│                         ├── Role
│                         └── ApprovalPolicy
└── roles, documentation, metrics
```

## Core resources

| Resource | Describes |
|---|---|
| `QualityContract` | The scope and entry point of a contract. |
| `QualityRequirement` | A quality expectation and its acceptance target. |
| `Workflow` | The stages that form a quality process. |
| `Stage` | A phase of work, verification, or decision. |
| `QualityMeasure` | The meaning, unit, and calculation of a measurement. |
| `QualityMeasureElement` | A timestamped input observation. |
| `Artifact` | A document used as quality evidence. |
| `Role` | An accountable function used by ownership and approval. |
| `ApprovalPolicy` | The rule for deciding whether approval is sufficient. |

## References

References contain only the target resource ID:

```yaml
spec:
  workflow: standard-release
  metrics:
    - unit-test-coverage
  roles:
    - software-engineer
```

IDs must be unique within the contract and use lowercase kebab-case. File names
and directory layout have no semantic meaning.

## Portable by default

The core resources do not contain vendor-specific fields. Implementations may
add provider configuration alongside a `QualityContract`, but provider configuration
must not change the meaning of the portable resources.

See [Providers](providers.md) for the supported adapter behavior in this
repository.

