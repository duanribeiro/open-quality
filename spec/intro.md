# Command Spec Intro

[toc]

## 1. Project Overview

| Field | Value |
|-------|-------|
| **Project Name** | open-quality (PyPI `open-quality-cli`, command `oq`) |
| **Primary Users** | Developers, QA engineers, CI jobs, project managers provisioning tracking tools |
| **One-line Summary** | Command-line reference implementation of the Open Quality 0.1 specification: validates, visualizes and evaluates a YAML quality contract and provisions it in OpenProject, GitHub, GitLab or Jira Cloud. |
| **Scope Boundary** | Owns contract parsing/validation (`cli/core.py`), rendering (`cli/renderer.py`), provider adapters (`cli/providers/`), JSON Schemas (`schema/v0.1`), docs and the static site (`web/`). Does not own the external provider systems or the quality evidence that feeds `state.yaml`. |

---

## 2. Stack Overview

| Layer | Technology / Module | Responsibility | Evidence |
|-------|---------------------|----------------|----------|
| Runtime | Python >= 3.10, PyYAML, jsonschema | Parse YAML, validate against JSON Schema | `pyproject.toml` |
| Command Entry | Console script `oq` -> `cli.cli:main`; `python -m cli.cli` | Dispatch subcommands | `pyproject.toml`, `cli/cli.py` |
| Script Entry | `Makefile`, GitHub Actions workflows | Build, format, test, demo, publish, deploy | `Makefile`, `.github/workflows/*.yml` |
| Integration | OpenProject, GitHub, GitLab, Jira Cloud REST APIs via `urllib` | Provision projects, members, work items | `cli/providers/*/__init__.py` |
| Static Site | Plain HTML/CSS/JS | Documentation site published to GitHub Pages | `web/` |

---

## 3. Capability Map

| Capability | Description | Primary Entry | Related Spec |
|------------|-------------|---------------|--------------|
| Validate contract | Schema and cross-reference validation of a quality directory | `oq validate` | `spec/use_case/uc_01_validate_quality_contract.md` |
| Render workflow graph | ASCII and Mermaid graph | `oq graph` | `spec/use_case/uc_02_render_quality_workflow_graph.md` |
| Evaluate readiness | Compare contract with runtime `state.yaml` | `oq evaluate`, `oq status` | `spec/use_case/uc_03_evaluate_quality_readiness_and_status.md` |
| Plan provider changes | Dry-run of provider operations | `oq plan` | `spec/use_case/uc_04_plan_provider_changes_for_quality_contract.md` |
| Apply to provider | Remote writes and state file | `oq apply` | `spec/use_case/uc_05_apply_quality_contract_to_external_provider.md` |
| Check, publish, deploy | Local checks, PyPI release, Pages deploy | `make check`, workflows | `spec/use_case/uc_06_check_publish_and_deploy_project.md` |

---

## 4. Spec Index

| Index | Location | Notes |
|-------|----------|-------|
| Architecture | `spec/arch/` | Repo layout, configuration/environment, dependencies |
| Use Cases | `spec/use_case/` | Six command and automation workflows |
| API | `spec/api/consumed_http.md` | Provider REST calls made by `oq apply`; the CLI provides no API |
| Commands | `spec/command/command.md` | Subcommand surface, options, exit codes |
| Scripts | `spec/script/scripts.md` | Makefile targets and GitHub workflows |

---

## 5. Source Evidence

| Source | Evidence | Notes |
|--------|----------|-------|
| `pyproject.toml` | `[project.scripts] oq = "cli.cli:main"` | Defines the console entry |
| `cli/cli.py` | `run()`, `_provider()` | Subcommand dispatch |
| `cli/core.py` | `load_contract`, `validate`, `evaluate` | Core domain logic |
| `cli/providers/` | `GitHubClient`, `GitLabClient`, `JiraClient`, `OpenProjectClient` | External integrations |

---

<!-- Template: skill-spec-base/templates/command/intro.md -->

## Reference

> **(Maintained manually; AI must not modify existing content in this section.)**

