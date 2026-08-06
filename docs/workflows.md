# Workflows and Stages

A `Workflow` names the stages that form a quality process. A `Stage` defines its dependencies and attached controls.

```yaml
kind: Workflow
spec:
  stages:
    - technical-refinement
    - continuous-integration
    - security-review
    - release-approval
```

```yaml
kind: Stage
metadata:
  id: continuous-integration
spec:
  type: continuous-integration
  activities: [linter, build, unit-tests, integration-tests, static-analysis]
  dependsOn:
    - technical-refinement
  owner: software-engineer
  gates:
    - ci-gate
```

Dependencies form a directed acyclic graph. This allows sequential and parallel phases without embedding an execution language. A semantic validator must reject cycles and references to stages outside the contract.

## Fixed stage types

Stage IDs and names identify a project-specific instance, but `spec.type` is
mandatory and comes from a fixed catalog. This gives integrations a stable
contract: a tool can implement `review`, for example, regardless of a
team's chosen stage ID or display name.

Business refinement → Technical refinement → `development` → `review` →
`continuous-integration` → `review` → `deploy` → `review` → `deploy`

The catalog does not force every workflow to use every type. Dependencies
continue to define the actual workflow order and possible parallelism.

`refinement` is accountable to one or more roles through `owners` and must
attach at least one `documentation` resource. Its ID and name are free, so a
contract can define Business refinement, Technical refinement, or any other
refinement instance. A `deploy` stage requires a free-form `environment`, a
`review` stage requires a free-form `reviewScope` and an `approvalPolicy`; none
of these fields has a fixed catalog. The review policy lists one or more reviewer roles
and uses `any`, `all`, or `minimum` to define the required approvals. Other
stage types may use the optional singular `owner` field.

Only the following types accept `activities`:

- `continuous-integration`: `linter`, `build`, `unit-tests`,
  `integration-tests`, `static-analysis`, `vulnerability-scan`,
  `secrets-scan`, `artifact-generation`.
For example, deployments to `staging`, `uat`, and `production` are all
instances of `deploy`; a team may instead use any labels such as `test-lab` or
`prod-br`.

Likewise, `code`, `business`, and `architecture` may all be values of
`reviewScope` for instances of `review`.

```yaml
kind: Stage
metadata:
  id: architecture-review
spec:
  type: review
  reviewScope: architecture
  approvalPolicy: architecture-review-approval
```

For example, both `continuous-integration` and `security-review` can depend on
the `technical-refinement` instance, with `release-approval` depending on both. After the
technical refinement completes, an executing implementation may run the CI and security
stages concurrently; it must wait for both before the release approval is
ready. The order in `Workflow.spec.stages` is only a declaration order and
does not make stages run sequentially.

```yaml
# continuous-integration
spec:
  type: continuous-integration
  dependsOn: [technical-refinement]

# security-review (stage ID)
spec:
  type: review
  reviewScope: security
  approvalPolicy: security-review-approval
  dependsOn: [technical-refinement]

# release-approval (stage ID)
spec:
  type: review
  reviewScope: release
  approvalPolicy: production-release-approval
  dependsOn: [continuous-integration, security-review]
```

Version 0.1 describes the process but does not define how a stage starts, completes, retries, times out, or stores runtime state. Those execution semantics remain implementation concerns until interoperability requirements are understood.
