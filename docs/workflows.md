# Workflows and Stages

A `Workflow` names the stages that form a quality process. A `Stage` defines its dependencies and attached controls.

```yaml
kind: Workflow
spec:
  stages:
    - design-review
    - continuous-integration
    - release-approval
```

```yaml
kind: Stage
metadata:
  id: continuous-integration
spec:
  dependsOn:
    - design-review
  owner: software-engineer
  gates:
    - ci-gate
```

Dependencies form a directed acyclic graph. This allows sequential and parallel phases without embedding an execution language. A semantic validator must reject cycles and references to stages outside the contract.

Version 0.1 describes the process but does not define how a stage starts, completes, retries, times out, or stores runtime state. Those execution semantics remain implementation concerns until interoperability requirements are understood.
