# Artifacts

An `Artifact` represents documentation used to support a quality decision,
such as a PRD, BRD, or technical design. It is referenced through the
`documentation` field of a QualityContract, QualityRequirement, or Stage.

```yaml
kind: Artifact
metadata:
  id: technical-design
  name: Technical design
spec:
  category: documentation
  externalLink: https://docs.example.com/technical-design
```
