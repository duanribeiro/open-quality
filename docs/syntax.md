# Syntax

## Format

YAML is the recommended authoring format. JSON is equivalent because YAML resource documents map to the JSON data model used by the schemas.

```yaml
specVersion: "0.1"
kind: Metric
metadata:
  id: regression-pass-rate
  name: Regression pass rate
  labels:
    area: testing
spec:
  type: percentage
  unit: percent
```

## Naming

- Field names use `camelCase`.
- Resource IDs use lowercase kebab-case and are unique within a contract.
- Human-readable names may contain spaces.
- References contain only the target resource ID.
- Percentages use numeric values from 0 through 100.
- Durations use ISO 8601 strings where a schema explicitly permits duration values.

## Documents and files

One resource per file is recommended for reviewable diffs. A parser must determine resource type from `kind`, not from the file name or directory.

## Operators

Version 0.1 uses named operators rather than free-form expressions:

`equals`, `notEquals`, `greaterThan`, `greaterThanOrEqual`, `lessThan`, `lessThanOrEqual`, `exists`, `approved`.

Free-form script expressions are excluded because they are difficult to validate portably and can introduce security risks.

## Unknown fields

The experimental schemas reject unknown fields. This catches spelling mistakes and keeps implementations aligned. Extension semantics will be designed through future public proposals.
