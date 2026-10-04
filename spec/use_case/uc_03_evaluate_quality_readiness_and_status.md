# Command Use Case: Evaluate Quality Readiness and Status

[toc]

## 1. Overview

| Field | Value |
|-------|-------|
| **Use Case ID** | `uc_03` |
| **Actor(s)** | developer, CI, release manager |
| **Goal** | Decide whether runtime evidence satisfies the contract |
| **Primary Entry** | `oq evaluate / oq status` |
| **Out of Scope** | Collecting the evidence in state.yaml |
| **Risk / Criticality** | Ordinary read; exit code gates CI |

---

## 2. Coverage Trace

| Entry ID | Entry Type | Entry Name | Trigger | Actor Intent | Covered By This UC | Notes |
|----------|------------|------------|---------|--------------|--------------------|-------|
| E03 | CLI | `oq evaluate` | `oq evaluate <dir> [state.yaml]` | Gate readiness (exit 2 if not ready) | yes | Detailed report |
| E04 | CLI | `oq status` | `oq status <dir> [state.yaml]` | Read-only summary (always exit 0 on success) | yes | Same evaluation, different renderer |

---

## 3. Preconditions & Postconditions

| Kind | Description |
|------|-------------|
| Preconditions | Valid contract; state YAML with `metrics`, `stages`, `approvals`, `documentation` mappings |
| Trigger Context | 1–2 arguments; default state path `<dir parent>/state.yaml` |
| Postconditions (success) | Report printed; evaluate exits 0 if ready, 2 if not; status exits 0 |
| Postconditions (failure) | `error:` and exit 1 |

---

## 4. Main Flow

| Step | Actor / Component | Action | Input / Output | State Change |
|------|-------------------|--------|----------------|--------------|
| 1 | developer/CI | Run `oq evaluate` or `oq status` | `argv` | none |
| 2 | cli.cli.run | Check 1–2 args and resolve state path | `paths` | none |
| 3 | cli.core.load_state | Parse the state file | `dict` | error if invalid |
| 4 | cli.core.evaluate | Compare metrics, stage statuses, approvals and documentation against requirements | `Report` | ready flag |
| 5 | cli.renderer | `evaluation` or `status` text | `stdout` | exit code from readiness |

---

## 5. Rules & Validation

| ID | Rule Type | Rule / Constraint | Failure Behavior |
|----|-----------|-------------------|------------------|
| BR-1 | Validation | State has only the four known keys (`parse_state`) | exit 1 |
| BR-2 | Gate | Not ready returns 2 for `evaluate` only | CI fails |

---

## 6. Failure Handling

| Scenario | Detection | User-visible Result | Recovery |
|----------|-----------|---------------------|----------|
| Unreadable or invalid state file | exception in `load_state` | `error: <path>: ...` | fix state |
| Bad argument count | `not 1 <= len(rest) <= 2` | usage message | fix call |

---

## 7. Acceptance Criteria

| ID | Criteria | Verification | Verification Target |
|----|----------|--------------|---------------------|
| AC-1 | Complete state yields ready and exit 0 | integration | `tests/test_cli.py#test_validate_and_evaluate_cli` |
| AC-2 | Parallel active stages and fixture evaluation are reported | unit | `tests/test_core.py#test_evaluation_reports_parallel_active_stages`, `#test_fixture_contract_validates_and_evaluates` |

---

## 8. Observability & Test Coverage

| Kind | Name / Location | Covers | Status | Notes |
|------|-----------------|--------|--------|-------|
| Log / Trace / Metric | `stdout/stderr` | success and failure messages | implemented | No structured logging or metrics |
| Test | `tests/test_cli.py, tests/test_core.py` | ready and not-ready | present | No dedicated test for `status` or the exit-2 path located |

---

## 9. Entry Points

| Entry | Handler |
|-------|---------|
| `cli/cli.py#run` (commands `evaluate`, `status`) | see section 2 |

---

## 10. Business Rules & Validation

| Scope | Summary |
|-------|---------|
| Enforcement | Contract must validate; state keys limited to metrics, stages, approvals, documentation; only `evaluate` converts not-ready into exit 2 |

---

## 11. Alternate / Exception Flows

| Flow | Description |
|------|-------------|
| Variants | Alternate: `status` never fails on readiness; exceptional: invalid state file, wrong argument count |

---

## 12. Module & Data Touchpoints

| Touchpoint | Detail |
|------------|--------|
| Modules and data | `cli/core.py#load_state`, `#evaluate`, `#_compare`; `cli/renderer.py#evaluation`, `#status`; `cli/model.py#Report`; read-only |

---

## 13. Error Handling

| Aspect | Behavior |
|--------|----------|
| Reporting | Invalid state or contract raises `ValueError` (exit 1); a not-ready `evaluate` returns exit code 2 without an error message. |

---

<!-- Template: skill-spec-base/templates/command/use_case/uc.md -->

## Reference

> **(Maintained manually; AI must not modify existing content in this section.)**
