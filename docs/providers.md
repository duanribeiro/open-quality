# Providers

The Quality Contract is provider-neutral. `QualityContract.spec`, `Stage`, and
the other core resources never contain OpenProject, Jira, or other vendor fields.

`QualityContract` MAY declare provider configurations at the document root, beside
`spec`. The `provider` field selects an implementation adapter. This keeps the
quality contract separate from provider configuration while allowing both to
live in one project file.

The minimal example includes provider configurations in its `quality-contract.yaml`.
By default, planning or applying runs every configured role in YAML order:

```bash
oq plan \
  --target examples/minimal/quality-contract.yaml \
  examples/minimal
```

Pass `--provider-role sourceControl` (or another role key) to run only that
role. If several roles run with an explicit `--state`, each role gets a
role-suffixed state filename.

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
  members:
    - role: software-engineer
      emails: [engineer@example.com]
      openProjectRole: Member
  kanban:
    columns: [New, In progress, Closed]
```

OpenProject selects an available work package type from the target project
automatically. Existing provider files may set `workPackageTypeHref` to prefer
a specific type; if that type is not enabled for the project, an available
project type is selected instead.

The provider creates the OpenProject project, a Basic board named after the
Open Quality project, and memberships from `config.members`. Workflow stage IDs
become freely named columns in
workflow order. The provider does not create work packages for stages or cards
in those columns. Missing member email addresses are created as OpenProject
invitations (requiring an administrator token). Each target may declare a
different set of members.

Jira Cloud uses the same commands with `provider: jira-cloud`. It creates or
reuses the configured Jira project, a Kanban board, project members, and
requirement issues. Kanban column names come from the workflow stage IDs, in
workflow order. The provider does not create issues for workflow stages.
When the existing board has a different number of columns, the CLI keeps
status order, redistributes the non-terminal statuses across all but the last
requested column, and keeps the existing last-column statuses at the end. Jira
treats the rightmost column as completed. Jira's public Agile API does not
provide a write operation for board columns, so the CLI currently uses the
same internal endpoint as Jira's board settings UI to rename them.
The `config.projectKey` must contain at least two characters, start with an
uppercase ASCII letter, and contain only uppercase ASCII letters and digits.
The CLI validates this before contacting Jira.

## GitHub Projects work management

Use `provider: github` with `config.owner` and `config.project` to select a
GitHub Projects board as the `workManagement` provider. `ownerType` defaults
to `organization`; set it to `user` for a personal project. The GitHub Project
represents the QualityContract. `oq plan` previews the project and workflow
board. `oq apply` creates or reuses the project, adds an `Open Quality Stage`
single-select field with the workflow stage IDs as its options, and creates a
Board view grouped into columns by that field. It does not add draft issues or
other project items. The provider stores the project ID and number in local
state for later applies.

```yaml
providers:
  workManagement:
    provider: github
    config:
      owner: your-organization
      project: Payment API Quality
      ownerType: organization
```

`GITHUB_TOKEN` needs permission to read the owner and create Projects v2
projects, fields, and views. The provider uses GraphQL for projects and fields,
and REST for the board view.

## GitHub repository provider

GitHub is a repository provider: run `oq apply` with a GitHub provider against
the same contract used by a project provider. It ensures the configured
repository exists and grants the configured collaborators access. It never
creates CI/CD workflows, repository rulesets, or pipeline configuration.
Set `ownerType` to `user` or `organization`; this selects the repository
creation endpoint. Personal repositories can only be created for the
authenticated GitHub account, whose login must match `owner`.

```yaml
provider: github
config:
  owner: your-organization
  ownerType: organization
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
  ownerType: organization
  repository: payment-api
  members:
    - role: software-engineer
      usernames: [octocat]
      permission: push
```

Do not include the repository owner in `config.members`; the owner already has
access and does not need a collaborator invitation.

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
