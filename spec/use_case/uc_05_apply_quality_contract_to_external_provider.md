# Command Use Case: Apply a Quality Contract to an External Provider

[toc]

## 1. Overview

| Field | Value |
|-------|-------|
| **Use Case ID** | `uc_05` |
| **Actor(s)** | project manager, developer, CI |
| **Goal** | Materialize the contract in OpenProject, GitHub, GitLab or Jira Cloud |
| **Primary Entry** | `oq apply` |
| **Out of Scope** | Deleting remote resources; rollback |
| **Risk / Criticality** | Credential-sensitive remote write |

---

## 2. Coverage Trace

| Entry ID | Entry Type | Entry Name | Trigger | Actor Intent | Covered By This UC | Notes |
|----------|------------|------------|---------|--------------|--------------------|-------|
| E06 | CLI | `oq apply` | `oq apply --target T ... <dir>` | Provision tracking tools and members | yes | Writes provider state JSON for OpenProject and Jira Cloud |

---

## 3. Preconditions & Postconditions

| Kind | Description |
|------|-------------|
| Preconditions | Valid contract and target; provider credentials in env (`OPENPROJECT_TOKEN`, `GITHUB_TOKEN`, `GITLAB_TOKEN`, `JIRA_EMAIL`+`JIRA_API_TOKEN`); network reachability |
| Trigger Context | Same arguments as `oq plan` |
| Postconditions (success) | Remote resources created/updated; state saved to `--state` or `<target>[.<role>].state.json` (OpenProject/Jira); prints `Applied ...` |
| Postconditions (failure) | Partial remote changes possible; state saved incrementally via callback for OpenProject and Jira |

---

## 4. Main Flow

| Step | Actor / Component | Action | Input / Output | State Change |
|------|-------------------|--------|----------------|--------------|
| 1 | operator | Run `oq apply` | `argv` | none |
| 2 | cli.cli._provider | Same parsing as plan | `target` | none |
| 3 | provider handler | Print plan, then call provider `apply` | `operations` | none |
| 4 | Provider client | Issue REST calls (see `spec/api/consumed_http.md`) | `HTTP requests` | remote state changed |
| 5 | cli.cli | Persist state and print applied count | `state JSON` | exit 0 |

---

## 5. Rules & Validation

| ID | Rule Type | Rule / Constraint | Failure Behavior |
|----|-----------|-------------------|------------------|
| BR-1 | Permission | Token env var must be non-empty or `ValueError` is raised | exit 1 before remote writes |
| BR-2 | Idempotency | GitHub ensures repository exists; GitLab requires an existing project; state hashes skip unchanged OpenProject/Jira resources | skip/no-op |
| BR-3 | Validation | 30 s timeout per request; HTTP errors surface as `<Provider> returned <code>` | exit 1 |

---

## 6. Failure Handling

| Scenario | Detection | User-visible Result | Recovery |
|----------|-----------|---------------------|----------|
| Missing credential | empty env var | error message | export credential |
| HTTP error | `HTTPError` | `... returned <code>: <body>` | fix permissions or input; rerun using saved state |
| Unknown GitLab user | empty user lookup | `GitLab user not found: <name>` | fix username |

---

## 7. Acceptance Criteria

| ID | Criteria | Verification | Verification Target |
|----|----------|--------------|---------------------|
| AC-1 | Missing GitHub repository is created as private | unit | `tests/test_github_provider.py#test_missing_repository_is_created_as_private` |
| AC-2 | GitLab apply only provisions members | unit | `tests/test_gitlab_provider.py#test_apply_only_provisions_members` |
| AC-3 | GitHub apply never writes workflow or ruleset | unit | `tests/test_github_provider.py#test_apply_never_writes_a_workflow_or_ruleset` |

---

## 8. Observability & Test Coverage

| Kind | Name / Location | Covers | Status | Notes |
|------|-----------------|--------|--------|-------|
| Log / Trace / Metric | `stdout/stderr` | success and failure messages | implemented | No structured logging or metrics |
| Test | `tests/test_github_provider.py`, `tests/test_gitlab_provider.py` | GitHub and GitLab apply | partial | No Jira or OpenProject apply test located; no live-provider tests |

---

## 9. Entry Points

| Entry | Handler |
|-------|---------|
| `cli/cli.py#_provider` with `is_apply=True` | see section 2 |

---

## 10. Business Rules & Validation

| Scope | Summary |
|-------|---------|
| Enforcement | Credentials required; each request has a 30 s timeout; OpenProject and Jira state saved through a callback after resource creation |

---

## 11. Alternate / Exception Flows

| Flow | Description |
|------|-------------|
| Variants | Alternate: re-run after partial failure reuses saved state; exceptional: missing credential, HTTP error, unknown user |

---

## 12. Module & Data Touchpoints

| Touchpoint | Detail |
|------------|--------|
| Modules and data | `GitHubClient`, `GitLabClient`, `JiraClient`, `OpenProjectClient`; `ProviderState`/`JiraState`; writes provider state JSON and remote systems |

---

## 13. Error Handling

| Aspect | Behavior |
|--------|----------|
| Reporting | HTTP failures raise `ValueError` (`<Provider> returned <code>: <body>`); `main` exits 1 and already-saved state allows a re-run. |

---

<!-- Template: skill-spec-base/templates/command/use_case/uc.md -->

## Reference

> **(Maintained manually; AI must not modify existing content in this section.)**
