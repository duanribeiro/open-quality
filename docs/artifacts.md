# Documentation resources

A `Documentation` resource represents material used to support a quality
decision, such as a PRD, BRD, or technical design. A QualityContract references
it through `docs`; a QualityRequirement or Stage uses `documentation`.

```yaml
kind: Documentation
metadata:
  id: technical-design
  name: Technical design
spec:
  category: documentation
  externalLink: https://docs.example.com/technical-design
```
