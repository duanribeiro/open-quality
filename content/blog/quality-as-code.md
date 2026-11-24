---
title: "Quality as Code: A Practical Guide for Software Teams"
description: "Learn how to define software quality expectations as version-controlled contracts, connect requirements to measures, and validate them with Open Quality."
date: 2026-11-24
author: "Open Quality"
slug: "quality-as-code-practical-guide"
tags:
  - quality as code
  - software quality
  - quality requirements
---

Software teams often describe quality in tickets, test plans, spreadsheets, and
release checklists. Those documents can be useful, but expectations become hard
to review when each tool stores a different version of the rules.

**Quality as Code** puts those expectations in version-controlled files beside
the software. A team can review changes, validate references, and connect the
contract to its workflow without making quality requirements depend on a single
project-management tool.

## What goes into a quality contract?

An Open Quality contract starts with a project entry point. It groups
requirements under quality characteristics, associates each requirement with
measurable targets, and can describe team roles, evidence, approvals, and
provider settings.

```yaml
kind: QualityContract
metadata:
  id: payment-api
  name: Payment API
quality:
  characteristics:
    - characteristic: reliability
      subcharacteristics:
        - subcharacteristic: availability
          requirements:
            - api-availability
```

The requirement itself lives in a separate resource. It states the expected
result and refers to a measure and target:

```yaml
kind: QualityRequirement
metadata:
  id: api-availability
  name: API availability
spec:
  statement: The API must achieve at least 99.9% availability.
  priority: high
  qualityMeasures:
    - qualityMeasure: availability
      target:
        operator: greaterThanOrEqual
        value: 99.9
        unit: percent
```

This separation makes the acceptance threshold visible during review. A
`QualityMeasure` describes the quantity being measured, while a
`QualityMeasureElement` can record timestamped observations used by a
measurement process.

## Keep quality expectations connected

A contract can also reference a `Workflow` whose stages describe the delivery
process. Stages can declare dependencies, owners, required documentation, and
approval policies. Those references let a team inspect how requirements and
release decisions relate to one another.

The reference CLI checks schemas and cross-resource references. For example,
run `oq validate examples/minimal` to validate the bundled contract, or
`oq graph --format both examples/minimal` to inspect its stage dependencies.

The CLI does not run a project's tests or collect telemetry on its own. The
measurement process supplies runtime values, and `oq evaluate` compares those
values with the contract's targets and workflow state.

## Try Open Quality

The source code, schemas, examples, and command-line implementation are in the
[Open Quality GitHub repository](https://github.com/duanribeiro/open-quality).
Start with the repository's quick-start guide to install the CLI and create a
contract for your own project.
