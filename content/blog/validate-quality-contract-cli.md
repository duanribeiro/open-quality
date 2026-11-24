---
title: "Validate a Software Quality Contract with the Open Quality CLI"
description: "A hands-on guide to validating resources, viewing workflow dependencies, and evaluating software quality targets with the Open Quality CLI."
date: 2026-11-24
author: "Open Quality"
slug: "validate-quality-contract-open-quality-cli"
category: "CLI guides"
tags:
  - Open Quality CLI
  - quality as code
  - software quality validation
---

A quality contract is most useful when teams can check it as part of normal
development. The Open Quality CLI validates contract resources and provides
commands to inspect a workflow or compare a runtime snapshot with its targets.

## Install and validate

Install the package with `pipx`:

```bash
pipx install open-quality-cli
```

From the repository root, validate the included example:

```bash
oq validate examples/minimal
```

Validation checks resource schemas, unique IDs, references to roles and
requirements, workflow dependencies, and other cross-resource rules. A
successful validation confirms the contract is structurally and semantically
consistent; it does not run application tests.

## Inspect a workflow

Stages can depend on one another, and the CLI can render those dependencies as
terminal text and Mermaid:

```bash
oq graph --format both examples/minimal
```

Dependencies define which stages can proceed; a list of stages alone does not
make them sequential. Use the graph output to review the process represented
by a `Workflow` and its `Stage` resources.

## Evaluate a runtime snapshot

Evaluation compares a contract with values supplied by an implementation:

```bash
oq evaluate examples/minimal examples/state.yaml
```

The snapshot can provide measured values, completed stages, present
documentation, and approvals. The CLI checks those inputs against the
contract's targets and policies. It does not collect telemetry, execute
measurement expressions, or run tests on your behalf.

## Connect a provider when needed

Provider configuration is optional. The repository documents supported
work-management and source-control integrations; provider credentials remain
in environment variables rather than the contract. Start with the
[Open Quality source repository](https://github.com/duanribeiro/open-quality)
to see the schemas, examples, and CLI implementation.
