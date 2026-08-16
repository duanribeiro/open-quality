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
oq plan --target examples/project.yaml --provider-role workManagement examples/minimal
oq plan --target examples/project.yaml --provider-role sourceControl examples/minimal
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

A future Jira adapter uses the same commands with `provider: jira` and its own
connection configuration.

## GitHub development provider

GitHub is a source-control provider: run `oq apply` with a GitHub provider
against the same contract used by a project provider. Its `developmentPolicy`
writes a managed workflow under `.github/workflows/`
and creates or updates an `Open Quality: <stage-id>` repository ruleset on the
configured default branch. The ruleset requires pull requests and enforces the
commit-message pattern; the workflow validates branch names, commits, linked
issues, and a non-empty pull-request description.

```yaml
provider: github
config:
  owner: your-organization
  repository: payment-api
  defaultBranch: main
  visibility: private
  members:
    - role: software-engineer
      usernames: [octocat]
      permission: push
```

`GITHUB_TOKEN` must have repository `Contents`, `Workflows`, and
`Administration` write permissions. The ruleset makes the generated
`Open Quality development policy` check required before merge; that workflow
enforces the branch and commit patterns declared in the provider configuration.
If the configured repository does not exist, `oq apply` creates it; the default
visibility is `private` and can be changed to `public` in the target.

`config.members` invites GitHub usernames as collaborators during apply:

```yaml
provider: github
members:
  - role: software-engineer
    usernames: [octocat]
    permission: push
```

## GitLab development provider

GitLab providers generate `.gitlab-ci.yml` from `developmentPolicy`, require a
successful pipeline before merge, and add the target's members.

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
