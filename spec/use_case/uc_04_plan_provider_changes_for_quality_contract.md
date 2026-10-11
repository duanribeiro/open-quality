# Command Use Case: Plan Provider Changes for a Quality Contract

[toc]

## 1. Overview

| Field | Value |
|-------|-------|
| **Use Case ID** | `uc_04` |
| **Actor(s)** | developer, project manager |
| **Goal** | Preview what `oq apply` would create or update in the target provider without remote writes |
| **Primary Entry** | `oq plan` |
| **Out of Scope** | Executing any remote change |
| **Risk / Criticality** | Ordinary read (reads target, members and state files) |

---

## 2. Coverage Trace

| Entry ID | Entry Type | Entry Name | Trigger | Actor Intent | Covered By This UC | Notes |
|----------|------------|------------|---------|--------------|--------------------|-------|
| E05 | CLI | `oq plan` | `oq plan [--target T] [--provider-role R] [--state S] [--members M] [<dir>]` | Dry-run provisioning | yes | Target defaults to `.quality/quality-contract.yaml`; directory defaults to the target file's parent; handler chosen by `provider` field |

---

## 3. Preconditions & Postconditions

| Kind | Description |
|------|-------------|
| Preconditions | Valid contract; target YAML with `provider` and `config` |
| Trigger Context | Target defaults to `.quality/quality-contract.yaml`; directory defaults to the target file's parent directory |
| Postconditions (success) | Header `Open Quality provider plan`, one line per operation, summary `Plan: X to create, Y to update, Z unchanged`; exit 0 |
| Postconditions (failure) | `error:` exit 1; no remote call and no state write |

---

## 4. Main Flow

| Step | Actor / Component | Action | Input / Output | State Change |
|------|-------------------|--------|----------------|--------------|
| 1 | developer | Run `oq plan` | `argv` | none |
| 2 | cli.cli._parse_provider_args | Parse flags; default target to `.quality/quality-contract.yaml` and directory to the target file's parent | `Namespace` | usage error if target file cannot be loaded |
| 3 | cli.cli._provider | Load target YAML; select the requested role or all configured roles in YAML order; choose each handler (GitHub, GitLab, Jira Cloud, or OpenProject) | `target document` | none |
| 4 | provider handler | Validate contract, load members and state, compute operations | `operations` | none |
| 5 | cli.cli | Print operations grouped (OpenProject: Provisionamento/Workflow/Revisão) and summary | `stdout` | exit 0 |

---

## 5. Rules & Validation

| ID | Rule Type | Rule / Constraint | Failure Behavior |
|----|-----------|-------------------|------------------|
| BR-1 | Validation | Target must contain only known keys; when `providers` is present, omission of `--provider-role` selects every role in YAML order and a supplied role selects only that role; `--provider-role` is invalid without `providers` | ValueError |
| BR-2 | Validation | Contract must validate before planning | exit 1 |
| BR-3 | Idempotency | Existing state hashes turn unchanged resources into no-op | none |

---

## 6. Failure Handling

| Scenario | Detection | User-visible Result | Recovery |
|----------|-----------|---------------------|----------|
| Unknown provider role | role not in `providers` | `provider role 'x' was not found` | fix role |
| Missing config key | loader ValueError | `target <path>: ...` | fix target |

---

## 7. Acceptance Criteria

| ID | Criteria | Verification | Verification Target |
|----|----------|--------------|---------------------|
| AC-1 | A supplied provider role selects one target | unit | `tests/test_cli.py#test_plan_selects_provider_role_from_project_file` |
| AC-2 | Omission of the provider role selects every target in YAML order | unit | No test currently covers this case |
| AC-3 | OpenProject plan provisions team and code reviewers | unit | `tests/test_provider.py#test_development_provisions_project_team_and_code_reviewers` |

---

## 8. Observability & Test Coverage

| Kind | Name / Location | Covers | Status | Notes |
|------|-----------------|--------|--------|-------|
| Log / Trace / Metric | `stdout/stderr` | success and failure messages | implemented | No structured logging or metrics |
| Test | `tests/test_cli.py`, `tests/test_provider.py` | explicit role selection and OpenProject plan | partial | All-role selection and Jira, GitHub or GitLab plan-output tests are not covered |

---

## 9. Entry Points

| Entry | Handler |
|-------|---------|
| `cli/cli.py#_provider` with `is_apply=False`; handlers `_github_provider`, `_gitlab_provider`, `_jira_provider`, `_openproject_provider` | see section 2 |

---

## 10. Business Rules & Validation

| Scope | Summary |
|-------|---------|
| Enforcement | Contract validated; target keys strictly checked; members taken inline unless `--members` overrides |

---

## 11. Alternate / Exception Flows

| Flow | Description |
|------|-------------|
| Variants | Alternate: project file with `providers` mapping runs every role unless `--provider-role` selects one; exceptional: unknown role, bad target, missing arguments |

---

## 12. Module & Data Touchpoints

| Touchpoint | Detail |
|------------|--------|
| Modules and data | `cli/providers/*/__init__.py` (`load_config`, `plan`), `cli/providers/openproject` (`ProviderState`, `Operation`), provider state JSON (read); no writes |

---

## 13. Error Handling

| Aspect | Behavior |
|--------|----------|
| Reporting | Target, role and config problems raise `ValueError` with the target path; `main` prints `error: ...` and exits 1; nothing is written remotely. |

---

<!-- Template: skill-spec-base/templates/command/use_case/uc.md -->

## Reference

> **(Maintained manually; AI must not modify existing content in this section.)**
