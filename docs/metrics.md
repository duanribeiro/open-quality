# Quality measures

A `QualityMeasure` gives a stable name to a measurement used by requirements.

```yaml
kind: QualityMeasure
metadata:
  id: latency-p95
spec:
  unit: milliseconds
  sourceHint: Application telemetry p95
```

The specification separates meaning from collection. `sourceHint` may help an adapter locate data, but it is not an executable provider configuration.

Units should be explicit whenever ambiguity is possible. Implementations compare observed values with the requirement target.
