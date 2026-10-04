# Architecture: Repository & Module Layout

[toc]

## 1. Overview

| Field | Value |
|-------|-------|
| **Project** | open-quality |
| **Stack** | python (command) |
| **Monorepo** | no |
| **Root** | `.` |

---

## 2. Top-level Tree

```text
.
├── cli/                         # Python package behind the `oq` command
│   ├── __init__.py              # package marker
│   ├── cli.py                   # subcommand dispatch (run/main) and provider handlers
│   ├── core.py                  # contract loading, schema + reference validation, readiness evaluation
│   ├── model.py                 # dataclasses: Resource, Bundle, Check, StageResult, Report
│   ├── renderer.py              # ASCII/Mermaid graph and evaluation/status text rendering
│   └── providers/               # external-system adapters
│       ├── __init__.py          # package marker
│       ├── interfaces.py        # ProviderAdapter / TargetLoader protocols
│       ├── github/              # GitHub repository + collaborator provisioning
│       │   └── __init__.py          # GitHubClient, loaders and apply
│       ├── gitlab/              # GitLab project member provisioning
│       │   └── __init__.py          # GitLabClient, loaders and apply
│       ├── jira_cloud/          # Jira Cloud project, board, issue hierarchy
│       │   └── __init__.py          # JiraClient, state, plan and apply
│       └── openproject/         # OpenProject projects, work packages, Kanban, members
│           └── __init__.py          # OpenProjectClient, state, plan and apply
├── schema/v0.1/                 # JSON Schemas for each resource kind (11 files)
├── examples/                    # minimal sample contract and state.yaml
├── docs/                        # Markdown documentation for the specification and CLI
├── tests/                       # unittest suites for CLI, core and providers
├── web/                         # static documentation site (index.html, app.js, styles.css)
├── pyproject.toml               # package metadata, dependencies, console script
├── Makefile                     # build/format/test/demo targets
├── dist/                        # build output (generated; not expanded)
├── open_quality_cli.egg-info/   # setuptools metadata (generated; not expanded)
├── _skynet/                     # tooling workspace, not part of the product
└── *.md                         # README, SPECIFICATION, MANIFESTO, GOVERNANCE, CHANGELOG and community files
```

---

## 3. Packages（monorepo）

| Package | Path | Stack | Role |
|---------|------|-------|------|
| `cli` | `cli/` | python | command |

---

## 4. Source Conventions

| Convention | Path |
|------------|------|
| Subcommand dispatch | `cli/cli.py` |
| Domain logic | `cli/core.py`, `cli/model.py`, `cli/renderer.py` |
| One package per provider | `cli/providers/{github,gitlab,jira_cloud,openproject}/__init__.py` |
| Tests mirror modules | `tests/test_*.py` |

---

## 5. Build & Tooling

| Tool | Config File |
|------|-------------|
| setuptools build, console script | `pyproject.toml` |
| black (line length 88, py310) | `pyproject.toml` |
| make targets | `Makefile` |
| GitHub Actions | `.github/workflows/ci.yml`, `pages.yml`, `publish-pypi.yml` |

---

<!-- Template: skill-spec-base/templates/arch/files.md -->

## Reference

> **(Maintained manually; AI must not modify existing content in this section.)**

