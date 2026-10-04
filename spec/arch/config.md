# Architecture: Config

[toc]

## 1. Overview

| Field | Value |
|-------|-------|
| **Stack** | python |
| **Config Source** | env, provider target YAML (`quality-contract.yaml`/project file), members file, state files |
| **Last Updated** | 2026-10-04 |

---

## 2. Config Catalog

| Key | Type | Required | Default | Owner | Used By | Validation & Defaults | Secret Handling |
|-----|------|----------|---------|-------|---------|-----------------------|-----------------|
| `OPENPROJECT_TOKEN` | string (env) | yes for `apply` on OpenProject | N/A | operator | `cli/providers/openproject` | `ValueError` "environment variable OPENPROJECT_TOKEN is empty" | API key used in HTTP Basic auth; never printed |
| `GITHUB_TOKEN` | string (env) | yes for `apply` on GitHub | N/A | operator | `cli/providers/github` | `ValueError` when empty | Bearer token; never printed |
| `GITLAB_TOKEN` | string (env) | yes for `apply` on GitLab | N/A | operator | `cli/providers/gitlab` | `ValueError` when empty | Access token; never printed |
| `JIRA_EMAIL`, `JIRA_API_TOKEN` | string (env) | yes for `apply` on Jira Cloud | N/A | operator | `cli/providers/jira_cloud` | `ValueError` unless both set | Basic auth header from email:token |
| `provider` | string | yes | N/A | contract author | `cli/cli.py#_provider` | `github`, `gitlab`, `jira-cloud`; any other value falls through to the OpenProject handler | N/A |
| `providers` / `--provider-role` | mapping / string | when file has `providers` | N/A | contract author | `cli/cli.py#_select_provider_role` | role must exist; `--provider-role` invalid without `providers` | N/A |
| `config.baseURL` | string | GitLab, Jira: yes; GitHub: no; OpenProject: validated by loader | GitHub `https://api.github.com` | contract author | all providers | Unknown config keys are rejected | N/A |
| `config.project` / `projectKey` / `owner` / `repository` | string | per provider | N/A | contract author | provider loaders | Missing required keys raise `ValueError` | N/A |
| `config.members` / `membersFile` / `--members` | list / path | no | none | contract author | `cli/cli.py#_load_members` | inline members win unless `--members` is given; relative path resolved against the target file | N/A |
| `config.typeHref` | string | OpenProject | N/A | contract author | `openproject.TargetConfig` | must start with `/api/v3/types/` | N/A |
| `config.notify` | bool | no | `false` | contract author | OpenProject work-package creation | passed as `notify` query | N/A |
| `--state` | path | no | `<target>[.<role>].state.json` | operator | OpenProject, Jira `plan`/`apply` | state file persisted after apply | local file, contains remote ids only |
| `state.yaml` (positional) | path | no | `<contract-dir>/../state.yaml` | operator | `oq evaluate`/`status` | parsed with `core.parse_state`; keys metrics, stages, approvals, documentation | N/A |

---

<!-- Template: skill-spec-base/templates/arch/config.md -->

## Reference

> **(Maintained manually; AI must not modify existing content in this section.)**

