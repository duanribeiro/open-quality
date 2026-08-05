# Quality Gates

A `Gate` groups objective rules that decide whether progression is allowed.

```yaml
kind: Gate
metadata:
  id: ci-gate
spec:
  rules:
    - metric: test-pass-rate
      operator: equals
      value: 100
    - metric: code-coverage
      operator: greaterThanOrEqual
      value: 80
  failure:
    action: block
```

Every rule references a separately declared `Metric`. The contract defines the threshold independently from the tool that supplies a measurement.

All rules use AND semantics in version 0.1. A gate failure may `block` or `warn`. Boolean groups, conditional rules, time windows, and automated rollback are intentionally deferred.
