# Command Use Case: Check, Publish and Deploy the Project

[toc]

## 1. Overview

| Field | Value |
|-------|-------|
| **Use Case ID** | `uc_06` |
| **Actor(s)** | maintainer, CI |
| **Goal** | Verify code quality, release the package to PyPI and publish the documentation site |
| **Primary Entry** | `make check / GitHub workflows` |
| **Out of Scope** | Runtime use of the oq command |
| **Risk / Criticality** | Release and publication side effects |

---

## 2. Coverage Trace

| Entry ID | Entry Type | Entry Name | Trigger | Actor Intent | Covered By This UC | Notes |
|----------|------------|------------|---------|--------------|--------------------|-------|
| E07 | script | `make targets` | `make <target>` | Local build/format/test/demo | yes | Makefile |
| E08 | script | `CI workflow` | `pull_request, push main` | Run `make check` on Python 3.10–3.13 | yes | ci.yml |
| E09 | script | `Deploy documentation site` | `push main on web/**, manual` | Publish `web/` to Pages | yes | pages.yml |
| E10 | script | `Publish to PyPI` | `release published` | Build and upload distributions | yes | publish-pypi.yml |
| E11 | console_script | `oq / python -m cli.cli` | `pip install` | Expose the command after install | yes | pyproject.toml `[project.scripts]` |

---

## 3. Preconditions & Postconditions

| Kind | Description |
|------|-------------|
| Preconditions | GitHub repository with Pages and `pypi` environment configured; release tag `v<version>` matching `pyproject.toml` |
| Trigger Context | Make invocation, PR/push, release, workflow_dispatch |
| Postconditions (success) | Checks pass; distribution on PyPI; Pages site updated |
| Postconditions (failure) | Workflow fails; nothing published when the tag/version check fails |

---

## 4. Main Flow

| Step | Actor / Component | Action | Input / Output | State Change |
|------|-------------------|--------|----------------|--------------|
| 1 | maintainer | Open PR or push | `git event` | CI runs |
| 2 | ci.yml | Install `.[dev]` and run `make check` | `matrix 3.10–3.13` | pass/fail |
| 3 | maintainer | Publish a GitHub release | `tag` | trigger publish |
| 4 | publish-pypi.yml | Verify tag equals version, `python -m build`, upload artifact, publish via OIDC | `dist/` | package released |
| 5 | pages.yml | Upload `web/` and deploy to Pages | `site artifact` | site updated |

---

## 5. Rules & Validation

| ID | Rule Type | Rule / Constraint | Failure Behavior |
|----|-----------|-------------------|------------------|
| BR-1 | Idempotency | Pages deploys share concurrency group `pages` with cancel-in-progress | older run cancelled |
| BR-2 | Validation | Release tag must equal `v<project.version>` | job fails |
| BR-3 | Permission | PyPI publish uses `id-token: write` in the `pypi` environment | job fails without trust |

---

## 6. Failure Handling

| Scenario | Detection | User-visible Result | Recovery |
|----------|-----------|---------------------|----------|
| Format or test failure | make exit code | failed CI check | fix and push |
| Tag/version mismatch | `test` command in workflow | failed build job | retag or bump version |

---

## 7. Acceptance Criteria

| ID | Criteria | Verification | Verification Target |
|----|----------|--------------|---------------------|
| AC-1 | `make check` passes locally | integration | `Makefile#check` |
| AC-2 | Release blocked on mismatched tag | manual | `publish-pypi.yml` |

---

## 8. Observability & Test Coverage

| Kind | Name / Location | Covers | Status | Notes |
|------|-----------------|--------|--------|-------|
| Log / Trace / Metric | `GitHub Actions logs` | all workflow steps | implemented | No metrics |
| Test | `tests/` | all python tests run by `make test` | present | Workflows themselves are untested |

---

## 9. Entry Points

| Entry | Handler |
|-------|---------|
| `Makefile` targets; `.github/workflows/ci.yml`, `pages.yml`, `publish-pypi.yml`; console script `oq` | see section 2 |

---

## 10. Business Rules & Validation

| Scope | Summary |
|-------|---------|
| Enforcement | Release tag must equal `v<project.version>`; Pages path limited to `web/`; CI matrix Python 3.10–3.13 |

---

## 11. Alternate / Exception Flows

| Flow | Description |
|------|-------------|
| Variants | Alternate: manual `workflow_dispatch` for Pages; exceptional: format/test failure, tag mismatch |

---

## 12. Module & Data Touchpoints

| Touchpoint | Detail |
|------------|--------|
| Modules and data | `pyproject.toml`, `Makefile`, `web/`, `dist/`; writes GitHub Pages and PyPI |

---

## 13. Error Handling

| Aspect | Behavior |
|--------|----------|
| Reporting | A failing make target or workflow step fails the job; the PyPI job does not run when the tag/version check fails. |

---

<!-- Template: skill-spec-base/templates/command/use_case/uc.md -->

## Reference

> **(Maintained manually; AI must not modify existing content in this section.)**
