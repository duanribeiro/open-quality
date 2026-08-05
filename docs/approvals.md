# Roles and Approvals

Ownership and approval are distinct. A `Stage.owner` identifies the accountable role for the phase. An `ApprovalPolicy` defines which roles must approve a decision.

```yaml
kind: ApprovalPolicy
metadata:
  id: production-release
spec:
  strategy: all
  approvers:
    - quality-lead
    - engineering-manager
```

Policies should reference roles rather than named people so contracts remain stable through staffing changes. Implementations map roles to identities and store approval events.

Strategies:

- `all`: all roles approve;
- `any`: at least one role approves;
- `minimum`: a declared minimum approves.

Version 0.1 does not define ordered approvals, delegation, separation of duties, expiry, or waivers.
