# Architecture: Dependency

[toc]

## 1. Overview

| Field | Value |
|-------|-------|
| **Scope** | package |
| **Stack** | python |

---

## 2. Dependency Manifest Files

| Path | File Role | Scope | Notes |
|------|-----------|-------|-------|
| `pyproject.toml` | manifest | runtime/build | runtime: `PyYAML>=6.0`, `jsonschema>=4.18`; dev: `black>=24,<26`; build: `setuptools>=68`; `requires-python >=3.10` |
| `Makefile` | build descriptor | build | `python3 -m compileall`, `black`, `unittest` |
| `.github/workflows/*.yml` | CI descriptor | build/release | Actions: checkout, setup-python, configure/upload/deploy-pages, upload/download-artifact, pypa/gh-action-pypi-publish |

---

## 3. External Service Dependencies

| Service | Protocol | Client / Integration Point | Base URL / Target | Auth | Consumed API Specs | Use Case |
|---------|----------|----------------------------|-------------------|------|--------------------|----------|
| OpenProject | http | `cli/providers/openproject/__init__.py#OpenProjectClient` | `config.baseURL` | HTTP Basic with `OPENPROJECT_TOKEN` | `spec/api/consumed_http.md` | `spec/use_case/uc_05_apply_quality_contract_to_external_provider.md` |
| GitHub | http | `cli/providers/github/__init__.py#GitHubClient` | `https://api.github.com` or `config.baseURL` | Bearer `GITHUB_TOKEN` | `spec/api/consumed_http.md` | `spec/use_case/uc_05_apply_quality_contract_to_external_provider.md` |
| GitLab | http | `cli/providers/gitlab/__init__.py#GitLabClient` | `config.baseURL` | `GITLAB_TOKEN` | `spec/api/consumed_http.md` | `spec/use_case/uc_05_apply_quality_contract_to_external_provider.md` |
| Jira Cloud | http | `cli/providers/jira_cloud/__init__.py#JiraClient` | `config.baseURL` | Basic `JIRA_EMAIL`:`JIRA_API_TOKEN` | `spec/api/consumed_http.md` | `spec/use_case/uc_05_apply_quality_contract_to_external_provider.md` |
| PyPI | package | `.github/workflows/publish-pypi.yml` | pypi.org/p/open-quality-cli | OIDC trusted publishing | N/A | `spec/use_case/uc_06_check_publish_and_deploy_project.md` |
| GitHub Pages | package | `.github/workflows/pages.yml` | repository Pages site | OIDC `id-token` | N/A | `spec/use_case/uc_06_check_publish_and_deploy_project.md` |

---

<!-- Template: skill-spec-base/templates/arch/dependency.md -->

## Reference

> **(Maintained manually; AI must not modify existing content in this section.)**

