# Artifacts

An `Artifact` is a declared external resource expected to support a requirement, stage, gate, approval, or decision. It points to its stored content through the required `externalLink`.

Artifacts are separated into two categories:

- `documentation` is an input produced during business or technical refinement, such as a PRD, BRD, architecture decision, or technical design.
- `report` is an output produced by execution or verification, such as an automated test report, security scan report, or coverage report.

Contracts reference the first category through `documentation` and the second through `reports`. A reference must match the category declared by the `Artifact` resource.

```yaml
kind: Artifact
metadata:
  id: e2e-test-report
spec:
  category: report
  externalLink: https://quality.example.com/reports/e2e-test-report
  required: true
  contentType: application/json
  retention: P180D
```

For example, a technical refinement stage with `type: refinement` can require `documentation: [prd, brd, technical-design]`; a later continuous-integration stage can require `reports: [automated-test-report, coverage-report]`.

Implementations are responsible for collection, integrity, access control, and retention enforcement. Contracts should not embed secrets or confidential artifact payloads.
