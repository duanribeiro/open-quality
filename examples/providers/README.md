# Provider targets

These targets demonstrate the supported provider adapters. They are not Quality
Contract resources; use each one with the reusable contract in
[`../minimal`](../minimal/README.md).

| Provider | Target | What `oq apply` manages |
| --- | --- | --- |
| OpenProject | `openproject.target.yaml` | Project, Kanban board, members, requirements, stages, and reviewers |
| Jira Cloud | `jira-cloud.target.yaml` | Project, Kanban board, members, requirements, and stages |
| GitHub | `github.target.yaml` | Repository and collaborators |
| GitLab | `gitlab.target.yaml` | Collaborators of an existing project |

Replace the placeholder organization, project, and user identifiers with your
own values. First inspect the operations without making external changes:

```bash
oq plan --target examples/providers/openproject.target.yaml examples/minimal
oq plan --target examples/providers/jira-cloud.target.yaml examples/minimal
oq plan --target examples/providers/github.target.yaml examples/minimal
oq plan --target examples/providers/gitlab.target.yaml examples/minimal
```

To execute a plan, replace `plan` with `apply`. The provider adapter obtains
its credentials from the environment; see [the provider reference](../../docs/providers.md)
for the required credentials and provider behavior.

Files ending in `.target.yaml` are intentionally ignored by `oq validate`,
because they configure an external adapter rather than declare a contract
resource.
