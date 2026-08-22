# GitHub example

This contract ensures a GitHub repository exists and grants collaborator access.
It does not create CI/CD workflows or repository rulesets.

```bash
oq validate examples/github
oq plan --target examples/github/project.yaml --provider-role sourceControl examples/github
```
