# Versioning

Open Quality versions the specification and contract history separately.

## Specification version

Every resource declares its interpretation family:

```yaml
specVersion: "0.1"
```

Specification releases use Semantic Versioning. During experimentation:

- patch releases clarify or fix the current schema without intended breaking changes;
- minor releases may introduce breaking changes and use a new `specVersion` family;
- `1.0.0` establishes the first stable compatibility commitment.

## Contract version

Contract evolution is normally tracked by source control. A user-defined contract release label may be stored outside the core metadata until a concrete interoperability need is established.

## Deprecation

Before 1.0, breaking changes must include release notes and updated examples. Stable-version deprecation policy, migration documents, and converters will be specified before 1.0.
