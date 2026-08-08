# Providers

The Quality Contract is provider-neutral. `Project`, `Stage`, `Gate`, and the
other core resources never contain OpenProject, Jira, or other vendor fields.

`oq plan` and `oq apply` use a separate provider target. The `provider` field
selects an implementation adapter; OpenProject is the first registered adapter.

```yaml
provider: openproject
name: local-openproject
config:
  baseURL: http://localhost:8080
  tokenEnv: OPENPROJECT_TOKEN
  workPackageTypeHref: /api/v3/types/1
```

A future Jira adapter uses the same commands with `provider: jira` and its own
connection configuration.
