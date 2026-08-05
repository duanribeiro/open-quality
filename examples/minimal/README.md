# Minimal payment API contract

This example models a small release workflow:

```text
Design review → CI validation → Release approval
```

It declares one availability requirement, one technical-design document, one automated-test report, a gate, roles, and an approval policy. It is intentionally compact while exercising every core resource kind.

The `Project` in `project.yaml` is the entry point. Resource references use `metadata.id`, regardless of file name.
