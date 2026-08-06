# Quality measures

A `QualityMeasure` gives a stable name and type to a measurement used by requirements and gates.

```yaml
kind: QualityMeasure
metadata:
  id: latency-p95
spec:
  type: duration
  unit: milliseconds
  sourceHint: Application telemetry p95
```

The specification separates meaning from collection. `sourceHint` may help an adapter locate data, but it is not an executable provider configuration.

Supported types are integer, number, percentage, boolean, duration, and string. Implementations should reject comparisons that are incompatible with a metric type. Units should be explicit whenever ambiguity is possible.
