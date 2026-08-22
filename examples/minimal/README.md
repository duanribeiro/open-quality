# Minimal payment API contract

This example models the standard release workflow:

```text
Business refinement → Technical refinement → Development → Code review → CI → Security review →
Deploy to staging → Release approval
→ Deploy to production → Post-release monitoring
```

It declares one availability requirement, one technical-design document, roles, and approval policies. Stages express their capabilities directly, such as documentation, approvals, and environments.

Resources are grouped in directories by `kind` (for example, `stages/`,
`quality-requirements/`, and `quality-measures/`). The `Project` in
`project.yaml` is the entry point. Resource references use
`metadata.id`, regardless of file name.

See the sibling provider examples in [`..`](..) for standalone contracts.
