# Minimal payment API contract

This example models the standard release workflow:

```text
Business refinement → Technical refinement → Development → Code review → CI → Security review →
Deploy to staging → Release approval
→ Deploy to production → Post-release monitoring
```

It declares one availability requirement, one technical-design document, one automated-test report, a gate, roles, and approval policies. It exercises every fixed stage type. Deployments use the generic `deploy` type with free-form environments.

Resources are grouped in directories by `kind` (for example,
`projects/project.yaml`, `stages/`, and `metrics/`). The `Project` in
`projects/project.yaml` is the entry point. Resource references use
`metadata.id`, regardless of file name.
