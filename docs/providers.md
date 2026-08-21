# Providers

The Quality Contract is provider-neutral. `Project.spec`, `Stage`, and
the other core resources never contain OpenProject, Jira, or other vendor fields.

`Project` MAY declare provider configurations at the document root, beside
`spec`. The `provider` field selects an implementation adapter. This keeps the
quality contract separate from provider configuration while allowing both to
live in one project file.

[`examples/project.yaml`](../examples/project.yaml) is a combined project and
target example. Select one target by name when planning or applying:

```bash
oq plan --target examples/project.yaml --provider-role workManagement examples
oq plan --target examples/project.yaml --provider-role sourceControl examples
```

The former standalone provider-file format remains supported. It is useful when
provider credentials or environment-specific configuration should not be
committed alongside the contract.

Credentials are never declared in provider YAML. `oq apply` reads
`OPENPROJECT_TOKEN`, `GITHUB_TOKEN`, `GITLAB_TOKEN`, or (for Jira Cloud)
`JIRA_EMAIL` and `JIRA_API_TOKEN`, according to the selected provider.

```yaml
provider: openproject
config:
  baseURL: http://localhost:8080
  workPackageTypeHref: /api/v3/types/1
  members:
    - role: software-engineer
      emails: [engineer@example.com]
      openProjectRole: Member
  kanban:
    columns: [New, In progress, Closed]
```

When a workflow contains a `development` stage, the provider creates the
OpenProject project, a status-based Kanban board named after the Open Quality
project, and memberships from `config.members`. Missing member email addresses are
created as OpenProject invitations (requiring an administrator token). A
`code-review` stage adds members
whose `role` appears in its approval policy as watchers of the review
work package (the OpenProject API's multi-user review mechanism). Each target
may therefore declare a different set of people.

Jira Cloud uses the same commands with `provider: jira-cloud`. It creates or
reuses the configured Jira project, a Kanban board, project members, and the
requirement and stage issues.

## GitHub repository provider

GitHub is a repository provider: run `oq apply` with a GitHub provider against
the same contract used by a project provider. It ensures the configured
repository exists and grants the configured collaborators access. It never
creates CI/CD workflows, repository rulesets, or pipeline configuration.

```yaml
provider: github
config:
  owner: your-organization
  repository: payment-api
  visibility: private
  members:
    - role: software-engineer
      usernames: [octocat]
      permission: push
```

`GITHUB_TOKEN` must have repository administration and collaborator-management
permissions. If the configured repository does not exist, `oq apply` creates
it; the default visibility is `private` and can be changed to `public` in the
target.

`config.members` invites GitHub usernames as collaborators during apply:

```yaml
provider: github
config:
  owner: your-organization
  repository: payment-api
  members:
    - role: software-engineer
      usernames: [octocat]
      permission: push
```

## GitLab repository provider

GitLab providers add the target's members to an existing project. They never
create or replace `.gitlab-ci.yml`, merge policies, or other CI/CD settings.

```yaml
provider: gitlab
config:
  baseURL: https://gitlab.com/api/v4
  project: group/payment-api
  members:
    - role: software-engineer
      usernames: [octocat]
      accessLevel: developer
```
