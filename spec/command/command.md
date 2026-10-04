# Command Contract

[toc]

## 1. Overview

| Field | Value |
|-------|-------|
| **Tool Name** | `oq` (also `python -m cli.cli`) |
| **Invocation Modes** | manual, CI, Makefile demo |
| **Primary Working Directory** | any; contract directories are passed as arguments |
| **Required Permissions** | read of contract/state files; write of provider state files; network and credentials for `apply` |

---

## 2. Command Catalog

| Command | Source | Handler | Arguments / Options | Exit Codes | Related Use Case |
|---------|--------|---------|---------------------|------------|------------------|
| `oq validate` | `cli/cli.py` | `cli/cli.py#run` | `<quality-directory>` | `0`, `1` | `spec/use_case/uc_01_validate_quality_contract.md` |
| `oq graph` | `cli/cli.py` | `cli/cli.py#run`, `cli/renderer.py#ascii`/`mermaid` | `--format ascii\|mermaid\|both` (default `both`), `<quality-directory>` | `0`, `1` | `spec/use_case/uc_02_render_quality_workflow_graph.md` |
| `oq evaluate` | `cli/cli.py` | `cli/cli.py#run`, `cli/core.py#evaluate` | `<quality-directory> [state.yaml]` | `0` ready, `2` not ready, `1` error | `spec/use_case/uc_03_evaluate_quality_readiness_and_status.md` |
| `oq status` | `cli/cli.py` | same as evaluate with `renderer.status` | `<quality-directory> [state.yaml]` | `0`, `1` | `spec/use_case/uc_03_evaluate_quality_readiness_and_status.md` |
| `oq plan` | `cli/cli.py` | `cli/cli.py#_provider` | `--target <file>`, `--provider-role`, `--state`, `--members`, `<quality-directory>` | `0`, `1` | `spec/use_case/uc_04_plan_provider_changes_for_quality_contract.md` |
| `oq apply` | `cli/cli.py` | `cli/cli.py#_provider` | same as plan | `0`, `1` | `spec/use_case/uc_05_apply_quality_contract_to_external_provider.md` |
| `oq` (no args / unknown) | `cli/cli.py` | `cli/cli.py#run` | N/A | `1` with usage text | `spec/use_case/uc_01_validate_quality_contract.md` |
| console script | `pyproject.toml` | `cli.cli:main` | N/A | exit code of `run` | `spec/use_case/uc_06_check_publish_and_deploy_project.md` |

---

## 3. Inputs, Outputs & Side Effects

| Entry | Inputs | Outputs | Side Effects | Idempotency / Safety |
|-------|--------|---------|--------------|----------------------|
| `oq validate` | YAML files under the directory | `PASS <project>` and resource counts; errors on stderr | none | read-only |
| `oq graph` | contract directory | ASCII and/or Mermaid text | none | read-only |
| `oq evaluate` / `status` | contract directory, state YAML | evaluation or status report | none | read-only |
| `oq plan` | target YAML, contract, state/members files | operation list and create/update/unchanged counts | none (offline; reads state file) | no remote calls |
| `oq apply` | as plan plus credentials env | plan output and "Applied ..." summary | remote create/update/invite calls; writes state JSON (OpenProject, Jira) | state hashes skip unchanged resources; no confirmation prompt |

---

## 4. Execution & Failure Handling

| Entry | Flow Summary | Failure Signal | User-visible Result | Recovery |
|-------|--------------|----------------|---------------------|----------|
| all commands | `main` runs `run(sys.argv[1:])` | any exception | `error: <message>` on stderr, exit 1 | fix input and rerun |
| `oq validate` / others | `_valid` loads, validates, prints each error as "- <error>" | `ValueError` "contract has N validation error(s)" | exit 1 | correct the YAML |
| `oq evaluate` | load contract, load state, `evaluate` | `report.ready` false | report text, exit 2 | satisfy stages/metrics/approvals |
| `oq plan`/`apply` | parse args, load target, select provider role, dispatch handler | missing `--target`/directory, unknown role, HTTP errors (`<Provider> returned <code>`) | usage or error text, exit 1 | fix target; rerun apply (state-based resume) |

---

<!-- Template: skill-spec-base/templates/command/command.md -->

## Reference

> **(Maintained manually; AI must not modify existing content in this section.)**

