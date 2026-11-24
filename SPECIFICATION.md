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
kind: <resource kind>
metadata:
  id: <contract-unique identifier>
  name: <human-readable name>
spec: {}
```

- `kind` MUST be one of the core resources defined below.
- `metadata.id` MUST be unique within a Quality Contract and use lowercase kebab-case.
- `metadata.name` is a human-readable label.
- `metadata.description` and `metadata.labels` MAY provide additional context.
- `spec` contains fields defined by the selected `kind`, except for
  `QualityContract`, whose `quality`, optional `docs`, `roles`, and
  `approvalPolicies` fields, and provider-role configurations are declared at
  the document root.

Unknown fields are invalid in version 0.1 unless they are placed under an explicitly supported extension field in a future version.

## 3. Quality Contract

A Quality Contract is one `QualityContract` and every resource transitively referenced by it. Resources MAY be stored in separate files. File names and directories are organizational and do not determine resource type.

References use resource IDs:

```yaml
workManagement:
  provider: github
  workflow: standard-release
  config:
    owner: your-user-or-organization
    project: Payment API Quality
```

An implementation MUST report unresolved references and duplicate IDs. It MUST NOT infer resources solely from file paths.

## 4. Core resources

### 4.1 QualityContract

`QualityContract` is the contract entry point. Its root-level `quality` field
declares quality scope; optional root-level `docs` and `approvalPolicies`
reference related resources. Team member role assignments are declared only
under `team[].roles`. The required
`workManagement.workflow` field selects the active workflow.

```yaml
kind: QualityContract
metadata:
  id: payment-api
  name: Payment API
docs:
  - technical-design
quality:
  characteristics: []
```

Required field: `quality`, an object containing `characteristics`. The
`characteristics` list holds fixed `characteristic`, optional
`subcharacteristics`, and `requirements` values. A characteristic MAY reference
requirements directly when it has no applicable subcharacteristics; otherwise,
each requirement appears under its subcharacteristic. Requirements reference
their `QualityMeasure` resources through `qualityMeasures` and carry the
acceptance targets for those measures.

Optional fields: `description`, `docs`, `roles`, and `approvalPolicies`.
Stages are declared only by the referenced `Workflow`.

Exactly one `QualityContract` MUST exist in a contract.

`QualityContract` MAY declare a top-level `team` list. Each member MUST contain
an `email` address and a non-empty `roles` list referencing existing `Role`
resource IDs. A person MAY hold multiple roles, and a role MAY be shared by
multiple people. Email addresses MUST be unique within the team, compared
case-insensitively, and role IDs MUST NOT repeat within a member's list.
Omitting `team` or declaring `team: []` is valid. This mapping records role
assignments; it does not grant provider permissions or change approval evaluation.

An implementation MAY support provider-role mappings at the QualityContract
root for provider-specific application configuration. Each provider role, such
as `workManagement` or `sourceControl`, declares `provider` and optional
`description` and `config` fields. Provider configuration does not alter the
portable quality-contract semantics.

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

`Stage.spec.description` MAY explain the stage's purpose. `Stage` has no fixed
type. Its behavior is otherwise expressed by optional fields: `approvalPolicy`
for a decision, `environment` for delivery context, and
`owners`/`documentation` for refinement work. Stage IDs, names, environments,
and review scopes are user-defined.

A stage is ready only when its referenced dependencies are complete in an executing implementation. Execution semantics are outside version 0.1; this rule establishes a shared conceptual meaning.

### 4.5 QualityMeasure

`QualityMeasure` defines the unit and calculation of a measurement.

Optional fields include `measurementFunction`, `unit`, `description`, and `sourceHint`.

`sourceHint` is descriptive only and MUST NOT create a dependency on a provider.

### 4.6 QualityMeasureElement

`QualityMeasureElement` stores the inputs to a measurement function. It MUST
declare `measurementMethod` and a non-empty `measurements` list. Each
measurement records a numeric `value` and its `measuredAt` timestamp in ISO 8601
date-time format. New measurements are appended to the list so that historical
values are retained. `measurementMethod: manual-entry` indicates that a person
records the value directly.

### 4.7 Documentation

`Documentation` describes documentation expected by a contract, requirement,
or stage. QualityContract references use root-level `docs`; requirements and
stages use `documentation`.

Required fields: `category`, `externalLink`. `category` is always `documentation` for inputs established during discovery or technical refinement (for example, PRD, BRD, or technical design). `externalLink` MUST be an absolute URL to the externally stored artifact. Optional fields include `required`, `retention`, and `contentType`.

### 4.8 Role

`Role` declares an accountable function used by ownership and approval references. It represents a role, not a named person.

Optional fields: `description`, `responsibilities`.

### 4.9 ApprovalPolicy

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

1. it contains exactly one QualityContract;
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

Contracts SHOULD reference secrets and identities rather than embedding sensitive values. Documentation definitions point to externally stored material, which may contain confidential data and require appropriate access controls outside this specification.

## 9. Versioning

Resource documents do not carry a version field. Implementations validate
documents using the schema shipped with that implementation. Breaking format
changes may require updating existing contracts; see [`docs/versioning.md`](docs/versioning.md).

## 10. Non-goals for 0.1

- executing tests or deployments;
- provisioning repository or CI settings;
- synchronizing measurements with external integrations;
- persisting approvals or documentation;
- defining exceptions and waivers;
- encoding complete ISO/IEC standards;
- defining a scoring model;
- making any specific platform central.
