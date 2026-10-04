# Command Use Case: Validate a Quality Contract

[toc]

## 1. Overview

| Field | Value |
|-------|-------|
| **Use Case ID** | `uc_01` |
| **Actor(s)** | developer, CI |
| **Goal** | Confirm that a quality directory is a valid Open Quality contract |
| **Primary Entry** | `oq validate` |
| **Out of Scope** | Provider provisioning and readiness evaluation |
| **Risk / Criticality** | Ordinary read |

---

## 2. Coverage Trace

| Entry ID | Entry Type | Entry Name | Trigger | Actor Intent | Covered By This UC | Notes |
|----------|------------|------------|---------|--------------|--------------------|-------|
| E01 | CLI | `oq validate` | `oq validate <dir>` | Check a contract before using it | yes | Also the validation gate reused by graph, evaluate, status, plan and apply (`_valid`) |

---

## 3. Preconditions & Postconditions

| Kind | Description |
|------|-------------|
| Preconditions | Directory contains YAML resources with `specVersion`, `kind`, `metadata.id` |
| Trigger Context | CLI args: exactly one directory |
| Postconditions (success) | Prints `PASS <project>` and counts of QualityContract, Workflow, Requirement, Stage, QualityMeasure, Documentation definition, Role, Approval policy; exit 0 |
| Postconditions (failure) | Each error printed as `- <error>` on stderr, then `error: contract has N validation error(s)`; exit 1 |

---

## 4. Main Flow

| Step | Actor / Component | Action | Input / Output | State Change |
|------|-------------------|--------|----------------|--------------|
| 1 | developer | Run `oq validate <dir>` | `argv` | none |
| 2 | cli.cli.run | Require exactly one argument | `argv` | usage error otherwise |
| 3 | cli.core.load_contract | Parse every `.yaml`/`.yml` file, validate each against the JSON Schema, index by kind and id | `Bundle` | duplicate id or second QualityContract rejected |
| 4 | cli.core.validate | Check ids, workflow reference, requirement hierarchy, stages (incl. cycles), approvals, artifacts | `error list` | none |
| 5 | cli.cli.run | Print summary | `stdout` | exit 0 |

---

## 5. Rules & Validation

| ID | Rule Type | Rule / Constraint | Failure Behavior |
|----|-----------|-------------------|------------------|
| BR-1 | Validation | Unknown fields, bad kinds and schema violations are rejected (`core._validate_schema`, `_strict_mapping`) | exit 1 with message |
| BR-2 | Validation | Stage dependency cycles are errors (`_find_cycle`) | listed as validation error |
| BR-3 | Validation | Resource ids must be unique across the directory | `duplicate id` error |

---

## 6. Failure Handling

| Scenario | Detection | User-visible Result | Recovery |
|----------|-----------|---------------------|----------|
| Invalid YAML or schema | exception in `load_contract` | `error: <path>: <reason>` | fix file |
| Wrong argument count | `len(rest) != 1` | `usage: oq validate <quality-directory>` | pass one directory |

---

## 7. Acceptance Criteria

| ID | Criteria | Verification | Verification Target |
|----|----------|--------------|---------------------|
| AC-1 | Valid example contract prints PASS and exit 0 | integration | `tests/test_cli.py#test_validate_and_evaluate_cli` |
| AC-2 | Unknown fields and dependency cycles are rejected | unit | `tests/test_core.py#test_parser_rejects_unknown_field`, `#test_validator_detects_cycle` |

---

## 8. Observability & Test Coverage

| Kind | Name / Location | Covers | Status | Notes |
|------|-----------------|--------|--------|-------|
| Log / Trace / Metric | `stdout/stderr` | success and failure messages | implemented | No structured logging or metrics |
| Test | `tests/test_cli.py, tests/test_core.py` | success and failure | present | Unknown-field, cycle and artifact-link rules covered in test_core |

---

## 9. Entry Points

| Entry | Handler |
|-------|---------|
| `cli/cli.py#run` (command `validate`), `_valid()` shared by every other command | see section 2 |

---

## 10. Business Rules & Validation

| Scope | Summary |
|-------|---------|
| Enforcement | Rules are enforced in `cli/core.py#validate` (see section 5); unknown keys and schema violations are fatal |

---

## 11. Alternate / Exception Flows

| Flow | Description |
|------|-------------|
| Variants | Alternate: any other subcommand reuses `_valid`; exceptional: schema error, duplicate id, cycle, wrong argument count (see section 6) |

---

## 12. Module & Data Touchpoints

| Touchpoint | Detail |
|------------|--------|
| Modules and data | `cli/core.py` (load_contract, validate, _validate_*), `schema/v0.1/*.json`, `cli/model.py` (Bundle, Resource); reads only YAML files, no writes |

---

## 13. Error Handling

| Aspect | Behavior |
|--------|----------|
| Reporting | Errors are collected, printed as `- <error>` lines and raised as one `ValueError`; `main` prints `error: ...` and exits 1. |

---

<!-- Template: skill-spec-base/templates/command/use_case/uc.md -->

## Reference

> **(Maintained manually; AI must not modify existing content in this section.)**
