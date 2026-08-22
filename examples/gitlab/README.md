# GitLab example

This contract grants member access to an existing GitLab project. It does not
create or modify CI/CD configuration or merge policies.

```bash
oq validate examples/gitlab
oq plan --target examples/gitlab/project.yaml --provider-role sourceControl examples/gitlab
```
