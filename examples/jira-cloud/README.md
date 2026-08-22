# Jira Cloud example

This contract provisions a Jira software project, Kanban board, members, one
quality requirement, and the workflow stages.

```bash
oq validate examples/jira-cloud
oq plan --target examples/jira-cloud/project.yaml --provider-role workManagement examples/jira-cloud
```
