# Evidence

Evidence is a declared artifact expected to support a requirement, stage, gate, approval, or decision. An `Evidence` resource declares the expectation, not the stored artifact.

Evidence is separated into two categories:

- `documentation` is an input produced during business or technical refinement, such as a PRD, BRD, architecture decision, or technical design.
- `report` is an output produced by execution or verification, such as an automated test report, security scan report, or coverage report.

Contracts reference the first category through `documentation` and the second through `reports`. A reference must match the category declared by the `Evidence` resource.

```yaml
kind: Evidence
metadata:
  id: e2e-test-report
spec:
  category: report
  type: test-report
  required: true
  contentType: application/json
  retention: P180D
```

For example, a design-review stage can require `documentation: [prd, brd, technical-design]`; a later continuous-integration stage can require `reports: [automated-test-report, coverage-report]`.

Implementations are responsible for collection, integrity, access control, retention enforcement, and linking an actual artifact to its definition. Contracts should not embed secrets or confidential artifact payloads.
