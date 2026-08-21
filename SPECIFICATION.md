# Open Quality Specification 0.1

Status: **Experimental**  
Specification version: **0.1.0**

The key words **MUST**, **MUST NOT**, **SHOULD**, **SHOULD NOT**, and **MAY** indicate requirement levels for conforming documents and implementations.

## 1. Scope

Open Quality defines a vendor-neutral document model for Quality as Code. A set of conforming resource documents forms a **Quality Contract**.

A Quality Contract can define quality requirements, process stages, measurements, documentation, roles, and approval rules. Version 0.1 defines representation and validation semantics only. It does not define workflow execution, integrations, persistent state, dashboards, or certification.

## 2. Resource envelope

Every resource document MUST contain:

```yaml
specVersion: "0.1"
kind: <resource kind>
metadata:
  id: <contract-unique identifier>
  name: <human-readable name>
spec: {}
```

- `specVersion` selects the specification family used to interpret the document.
- `kind` MUST be one of the core resources defined below.
- `metadata.id` MUST be unique within a Quality Contract and use lowercase kebab-case.
- `metadata.name` is a human-readable label.
- `metadata.description` and `metadata.labels` MAY provide additional context.
- `spec` contains fields defined by the selected `kind`.

Unknown fields are invalid in version 0.1 unless they are placed under an explicitly supported extension field in a future version.

## 3. Quality Contract

A Quality Contract is one `Project` and every resource transitively referenced by it. Resources MAY be stored in separate files. File names and directories are organizational and do not determine resource type.

References use resource IDs:

```yaml
workflow: standard-release
requirements:
  - api-availability
```

An implementation MUST report unresolved references and duplicate IDs. It MUST NOT infer resources solely from file paths.

## 4. Core resources

### 4.1 Project

`Project` is the contract entry point. Its `spec` declares scope and references the active workflow and related resources.

Required fields: `workflow`, `quality`. `quality` is a non-empty hierarchy of
fixed `characteristic`, optional `subcharacteristics`, and `requirements`
values. A characteristic MAY reference requirements directly when it has no
applicable subcharacteristics; otherwise, each requirement appears under its
subcharacteristic. This makes the quality aspect, its desired level, and its
measurement traceable from the Project entry point.

Optional fields: `description`, `metrics`, `documentation`, `roles`, `approvalPolicies`. Stages are declared only by the referenced `Workflow`.

Exactly one `Project` MUST exist in a contract.

An implementation MAY support a top-level `Project.providers` mapping for
provider-specific application configuration. Each provider role declares
`provider` and optional `description` and `config` fields. `providers` is outside
`Project.spec`; it does not alter the portable quality-contract semantics.

### 4.2 QualityRequirement

`QualityRequirement` declares a quality expectation.

Required fields: `statement`, `priority`, `qualityMeasures`. Each
`qualityMeasures` entry references one `QualityMeasure`, its
acceptance `target` with an operator and expected value. A QualityMeasure owns
its `QualityMeasureElement` inputs through its measurement function.
Optional fields: `documentation`.

Version 0.1 target operators are `equals`, `notEquals`, `greaterThan`,
`greaterThanOrEqual`, `lessThan`, `lessThanOrEqual`, `exists`, and `approved`.

### 4.3 Workflow

`Workflow` identifies the stages that compose a quality process.

Required field: `stages`, a non-empty list of `Stage` IDs.

A Workflow does not imply list order as dependency order. Dependencies are declared by each `Stage.dependsOn`. Stages with the same satisfied dependencies have no ordering constraint and MAY be executed in parallel by an executing implementation. The resulting graph MUST be acyclic.

### 4.4 Stage

`Stage` is a reusable phase of work, verification, or decision.

`Stage` has no fixed type. Its behavior is expressed by optional fields:
`approvalPolicy` for a decision, `environment` for delivery context, and
`owners`/`documentation` for refinement work. Stage IDs, names, environments,
and review scopes are user-defined.

A stage is ready only when its referenced dependencies are complete in an executing implementation. Execution semantics are outside version 0.1; this rule establishes a shared conceptual meaning.

### 4.5 QualityMeasure

`QualityMeasure` defines the unit and calculation of a measurement.

Optional fields include `measurementFunction`, `unit`, `description`, and `sourceHint`.

`sourceHint` is descriptive only and MUST NOT create a dependency on a provider.

### 4.6 Artifact

`Artifact` describes documentation expected by a requirement or stage. References use `documentation`.

Required fields: `category`, `externalLink`. `category` is always `documentation` for inputs established during discovery or technical refinement (for example, PRD, BRD, or technical design). `externalLink` MUST be an absolute URL to the externally stored artifact. Optional fields include `required`, `retention`, and `contentType`.

### 4.7 Role

`Role` declares an accountable function used by ownership and approval references. It represents a role, not a named person.

Optional fields: `description`, `responsibilities`.

### 4.8 ApprovalPolicy

`ApprovalPolicy` declares how approval is obtained.

Required fields: `strategy`, `approvers`. Strategies are:

- `all`: every listed role approves;
- `any`: one listed role approves;
- `minimum`: at least `minimum` approvals from listed roles.

When strategy is `minimum`, the `minimum` field MUST be present and MUST NOT exceed the number of approvers.

## 5. Structural conformance

A resource is structurally conforming when it validates against its versioned JSON Schema. The schemas in `schema/v0.1` are the machine-readable source for structural constraints.

## 6. Semantic conformance

A Quality Contract is semantically conforming when:

1. it contains exactly one Project;
2. all IDs are unique;
3. all references resolve to the expected resource kind;
4. stage dependencies are acyclic;
5. workflow stages are declared and reachable;
6. approval policies reference declared roles;
7. `minimum` approval constraints are satisfiable.

JSON Schema alone cannot enforce every semantic rule. Implementations SHOULD provide a semantic validator.

## 7. Portability

A conforming implementation MUST interpret core resources according to this specification and MUST NOT require provider-specific fields for basic validation. Implementations MAY add capabilities outside the core, but such capabilities must not silently change core semantics.

## 8. Security and privacy

Contracts SHOULD reference secrets and identities rather than embedding sensitive values. Artifact definitions point to external artifacts, which may contain confidential data and require appropriate access controls outside this specification.

## 9. Compatibility

Documents use `specVersion: "0.1"`. Patch releases clarify or correct the 0.1 schema without intentional breaking changes. Breaking changes require a new minor experimental family or, after stabilization, a new major version. See [`docs/versioning.md`](docs/versioning.md).

## 10. Non-goals for 0.1

- executing tests or deployments;
- provisioning repository or CI settings;
- evaluating live metrics;
- persisting approvals or documentation;
- defining exceptions and waivers;
- encoding complete ISO/IEC standards;
- defining a scoring model;
- making any specific platform central.
