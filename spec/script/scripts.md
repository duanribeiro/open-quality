# Command Scripts

[toc]

## 1. Script & Hook Catalog

| Script / Hook | Source | Trigger | Runtime | Responsibility | Related Use Case |
|---------------|--------|---------|---------|----------------|------------------|
| `make build` | `Makefile` | manual / CI | python3 | `compileall -q cli` | `spec/use_case/uc_06_check_publish_and_deploy_project.md` |
| `make format` / `format-check` | `Makefile` | manual / CI | black | format or check `cli tests` | `spec/use_case/uc_06_check_publish_and_deploy_project.md` |
| `make test` | `Makefile` | manual / CI | unittest | `discover -s tests -v` | `spec/use_case/uc_06_check_publish_and_deploy_project.md` |
| `make check` | `Makefile` | CI | make | build + format-check + test | `spec/use_case/uc_06_check_publish_and_deploy_project.md` |
| `make demo` | `Makefile` | manual | python3 | run validate/graph/evaluate/status on `examples/minimal` | `spec/use_case/uc_06_check_publish_and_deploy_project.md` |
| `make provider-plan` | `Makefile` | manual | python3 | `oq plan` against the example `workManagement` role | `spec/use_case/uc_06_check_publish_and_deploy_project.md` |
| CI workflow | `.github/workflows/ci.yml` | PR, push to main | GitHub Actions | `make check` on Python 3.10–3.13 | `spec/use_case/uc_06_check_publish_and_deploy_project.md` |
| Deploy documentation site | `.github/workflows/pages.yml` | push to main touching `web/**` or the workflow; manual | GitHub Actions | publish `web/` to GitHub Pages | `spec/use_case/uc_06_check_publish_and_deploy_project.md` |
| Publish to PyPI | `.github/workflows/publish-pypi.yml` | release published | GitHub Actions | verify tag `v<version>`, build, publish | `spec/use_case/uc_06_check_publish_and_deploy_project.md` |

---

## 2. Automation Flow

| Flow | Step | Script / Hook | Input | Output |
|------|------|---------------|-------|--------|
| Quality gate | 1 | `make build` | `cli/` | byte-compiled check |
| Quality gate | 2 | `make format-check` | `cli`, `tests` | pass/fail |
| Quality gate | 3 | `make test` | `tests/` | test results |
| Release | 1 | version check | release tag, `pyproject.toml` | pass/fail |
| Release | 2 | `python -m build` | source | `dist/` artifact |
| Release | 3 | pypa publish | `dist/` | package on PyPI |
| Pages | 1 | configure/upload/deploy pages | `web/` | published site |

---

## 3. Safety & Side Effects

| Entry | Side Effect | Guard / Confirmation | Rollback / Recovery |
|-------|-------------|----------------------|---------------------|
| `make format` | rewrites `cli` and `tests` | manual invocation | git revert |
| Publish to PyPI | uploads a distribution | tag/version equality check; `pypi` environment; OIDC | publish a new version |
| Deploy documentation site | replaces the Pages site | concurrency group `pages`, cancel in progress | redeploy previous commit |

---

<!-- Template: skill-spec-base/templates/command/script/scripts.md -->

## Reference

> **(Maintained manually; AI must not modify existing content in this section.)**

