# OpenProject example

This contract provisions a project, Kanban board, members, one quality
requirement, and the workflow stages in OpenProject.

```bash
oq validate examples/openproject
oq plan --target examples/openproject/project.yaml --provider-role workManagement examples/openproject
```
