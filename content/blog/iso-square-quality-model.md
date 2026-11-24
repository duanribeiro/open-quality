---
title: "How to Model Software Quality with ISO SQuaRE"
description: "Connect ISO SQuaRE quality characteristics to software requirements, quality measures, and timestamped observations using Open Quality."
date: 2026-11-24
author: "Open Quality"
slug: "model-software-quality-iso-square"
tags:
  - ISO SQuaRE
  - software quality model
  - quality measurement
---

Teams need a shared vocabulary for quality before they can agree on what to
measure. ISO/IEC SQuaRE provides models for organizing software product quality,
quality in use, and measurement concepts. Open Quality uses those ideas to
structure quality requirements in a version-controlled contract.

## From a characteristic to a requirement

A **characteristic** names a broad quality concern, such as reliability or
maintainability. A **subcharacteristic** narrows it: availability is one aspect
of reliability, while testability is one aspect of maintainability.

The contract classifies a requirement under the relevant characteristic:

```yaml
quality:
  characteristics:
    - characteristic: reliability
      subcharacteristics:
        - subcharacteristic: availability
          requirements: [api-availability]
```

The characteristic IDs come from the supported schema vocabulary. They are
classification values, not project-defined resources. This gives teams a
consistent way to browse and compare requirements across services.

## Make the expectation measurable

A quality requirement contains the acceptance criterion. It references a
quality measure and records the target for that requirement:

```yaml
kind: QualityRequirement
metadata:
  id: api-availability
  name: API availability
spec:
  statement: The API must achieve at least 99.95% monthly availability.
  priority: critical
  qualityMeasures:
    - qualityMeasure: availability
      target:
        operator: greaterThanOrEqual
        value: 99.95
        unit: percent
```

The measure describes the quantity and may define a calculation. Its inputs can
be `QualityMeasureElement` resources containing values and timestamps. Keeping
the target on the requirement allows two requirements to use the same measure
with different acceptance thresholds.

## Separate the model from collection

The contract can describe a measure and its inputs, but it does not prescribe
how a monitoring system, test runner, or team collects the data. Likewise, the
reference CLI does not execute a measurement expression or gather telemetry;
it evaluates values provided in a runtime snapshot.

That boundary keeps the quality model portable. A team can keep its measurement
system while making requirements, targets, and workflow checks reviewable in
Git.

For the formal models, see
[ISO/IEC 25010](https://www.iso.org/standard/78176.html) for product quality
and [ISO/IEC 25019](https://www.iso.org/standard/78177.html) for quality in
use. Open Quality provides a contract format that draws on these concepts; a
valid contract is not, by itself, a claim of ISO conformity.

Explore the implementation and schemas in the
[Open Quality repository](https://github.com/duanribeiro/open-quality).
