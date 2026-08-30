# Evaluation

The `0.1` specification describes the desired quality model. It does not
define runtime storage or execution. The reference CLI demonstrates readiness
with an implementation-specific `state.yaml` snapshot stored next to the
contract directory.

## State shape

```yaml
metrics:
  unit-test-coverage: 85
stages:
  continuous-integration: completed
approvals:
  production-release-approval:
    - quality-lead
    - engineering-manager
documentation:
  technical-design: true
```

The snapshot has four sections:

- `metrics`: observed values used by requirement targets;
- `stages`: stage status such as `pending`, `running`, `blocked`, or
  `completed`;
- `approvals`: roles that approved each policy;
- `documentation`: whether an artifact is available.

## Requirement checks

A `QualityRequirement` passes when each referenced `QualityMeasure` target is
satisfied and each required artifact is present in state.

Available target operators are:

```text
equals
notEquals
greaterThan
greaterThanOrEqual
lessThan
lessThanOrEqual
exists
approved
```

For example, this target passes when the state contains a numeric metric of at
least `80`:

```yaml
qualityMeasures:
  - qualityMeasure: unit-test-coverage
    target:
      operator: greaterThanOrEqual
      value: 80
      unit: percent
```

## Stage checks

A stage is ready for evaluation when its state is `completed`, its required
documentation is present, and its approval policy is satisfied when one is
declared. The CLI reports dependencies in the graph, while the state snapshot
records the current status.

The specification intentionally does not define how stages start, retry,
timeout, or persist runtime events. An external implementation may provide
those behaviors and produce an equivalent state snapshot.

## Measurement history

`QualityMeasureElement` stores timestamped observations:

```yaml
kind: QualityMeasureElement
metadata:
  id: unit-test-covered-lines
  name: Unit-test-covered lines
spec:
  unit: lines
  measurementMethod: manual-entry
  measurements:
    - value: 850
      measuredAt: "2026-08-01T00:00:00Z"
```

Keeping observations in the contract preserves measurement history. The
implementation that collects them may be CI, telemetry, a database, or a
manual process.
