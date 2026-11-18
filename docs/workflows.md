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
  description: Run automated checks on the refined changes.
  dependsOn:
    - technical-refinement
  owner: software-engineer
```

Dependencies form a directed acyclic graph. This allows sequential and parallel phases without embedding an execution language. A semantic validator must reject cycles and references to stages outside the contract.

## Stage capabilities

Stage descriptions are optional and can explain the stage's purpose. Stage IDs
and names are entirely project-defined. A stage declares its
`approvalPolicy` for a decision, `environment` for delivery context, and
`owners` with `documentation` for refinement work.
Dependencies still define execution order and possible parallelism.

For example, deployments may use any `environment` such as `staging`, `uat`,
`production`, or `prod-br`. Likewise, `reviewScope` can be `code`, `business`,
or `architecture` when that context helps readers.

```yaml
kind: Stage
metadata:
  id: architecture-review
spec:
  description: Review the design for architectural risks.
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
  description: Run automated checks on the changes.
  dependsOn: [technical-refinement]

# security-review (stage ID)
spec:
  description: Review the changes for security risks.
  reviewScope: security
  approvalPolicy: security-review-approval
  dependsOn: [technical-refinement]

# release-approval (stage ID)
spec:
  description: Confirm the release is ready to proceed.
  reviewScope: release
  approvalPolicy: production-release-approval
  dependsOn: [continuous-integration, security-review]
```

Version 0.1 describes the process but does not define how a stage starts, completes, retries, times out, or stores runtime state. Those execution semantics remain implementation concerns until interoperability requirements are understood.
