# Command Use Case: Render the Quality Workflow Graph

[toc]

## 1. Overview

| Field | Value |
|-------|-------|
| **Use Case ID** | `uc_02` |
| **Actor(s)** | developer, documentation author |
| **Goal** | Visualize stages, dependencies and requirements as ASCII or Mermaid |
| **Primary Entry** | `oq graph` |
| **Out of Scope** | Evaluation against runtime state |
| **Risk / Criticality** | Ordinary read |

---

## 2. Coverage Trace

| Entry ID | Entry Type | Entry Name | Trigger | Actor Intent | Covered By This UC | Notes |
|----------|------------|------------|---------|--------------|--------------------|-------|
| E02 | CLI | `oq graph` | `oq graph [--format F] <dir>` | See the workflow | yes | Format `both` emits ASCII plus a fenced mermaid block |

---

## 3. Preconditions & Postconditions

| Kind | Description |
|------|-------------|
| Preconditions | Valid contract directory |
| Trigger Context | `--format ascii|mermaid|both` (default both) |
| Postconditions (success) | Graph printed to stdout; exit 0 |
| Postconditions (failure) | `error:` on stderr; exit 1 |

---

## 4. Main Flow

| Step | Actor / Component | Action | Input / Output | State Change |
|------|-------------------|--------|----------------|--------------|
| 1 | developer | Run `oq graph` | `argv` | none |
| 2 | cli.cli.run | Parse `--format` and directory | `argparse Namespace` | directory required |
| 3 | cli.cli._valid | Load and validate bundle | `Bundle` | stops on errors |
| 4 | cli.renderer | `ascii(bundle)` and/or `mermaid(bundle)` | `text` | none |
| 5 | cli.cli.run | Print result | `stdout` | exit 0 |

---

## 5. Rules & Validation

| ID | Rule Type | Rule / Constraint | Failure Behavior |
|----|-----------|-------------------|------------------|
| BR-1 | Validation | Unknown format raises `unknown graph format` | exit 1 |
| BR-2 | Validation | ASCII output states that list order does not define execution order and uses no sequential arrows | N/A |

---

## 6. Failure Handling

| Scenario | Detection | User-visible Result | Recovery |
|----------|-----------|---------------------|----------|
| Missing directory | `not values.directory` | usage message | provide directory |
| Invalid contract | `_valid` errors | validation errors | fix contract |

---

## 7. Acceptance Criteria

| ID | Criteria | Verification | Verification Target |
|----|----------|--------------|---------------------|
| AC-1 | ASCII graph does not imply sequential order | unit | `tests/test_cli.py#test_ascii_graph_does_not_imply_sequential_stage_order` |

---

## 8. Observability & Test Coverage

| Kind | Name / Location | Covers | Status | Notes |
|------|-----------------|--------|--------|-------|
| Log / Trace / Metric | `stdout/stderr` | success and failure messages | implemented | No structured logging or metrics |
| Test | `tests/test_cli.py` | ascii rendering | present | Mermaid output not asserted |

---

## 9. Entry Points

| Entry | Handler |
|-------|---------|
| `cli/cli.py#run` (command `graph`) | see section 2 |

---

## 10. Business Rules & Validation

| Scope | Summary |
|-------|---------|
| Enforcement | `--format` limited to ascii, mermaid, both; contract must validate |

---

## 11. Alternate / Exception Flows

| Flow | Description |
|------|-------------|
| Variants | Alternate: format `ascii` or `mermaid` prints one block; exceptional: unknown format, missing directory, invalid contract |

---

## 12. Module & Data Touchpoints

| Touchpoint | Detail |
|------------|--------|
| Modules and data | `cli/renderer.py#ascii`, `#mermaid`; `cli/model.py#Bundle`; read-only |

---

## 13. Error Handling

| Aspect | Behavior |
|--------|----------|
| Reporting | Unknown format or invalid contract raises `ValueError`; `main` prints `error: ...` and exits 1. |

---

<!-- Template: skill-spec-base/templates/command/use_case/uc.md -->

## Reference

> **(Maintained manually; AI must not modify existing content in this section.)**
