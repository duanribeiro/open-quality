# Changelog

All notable changes to Open Quality are documented here.

## Unreleased

## [0.2.0] - 2026-10-11

### Fixed

- `oq validate` now defaults to `.quality` when the contract directory is omitted.
- GitHub Projects personal board creation uses the owner's login in the REST route and recognizes existing GraphQL board layouts.

### Added

- Interactive `oq init` scaffolds a contract, while `oq add role` and `oq add team`
  create roles and associate people with them.
- GitHub Projects can be used as a work-management provider, with a board view
  grouped by workflow stages.
- Optional top-level `QualityContract.team` entries associate email addresses with existing roles, with validation for duplicate emails and unresolved role references.

### Changed

- Renamed the `Project` resource kind to `QualityContract` (schema file, examples, and CLI output updated accordingly).
- Quality requirements now declare their acceptance targets through quality measures.
- Gates and SQuaRE `qualityLevel` were removed from the 0.1 model.
- The CLI package is published to PyPI as `open-quality-cli`.

## [0.1.0] - 2026-08-03

### Added

- Initial Quality as Code manifesto and principles.
- Quality Contract concept and common resource envelope.
- Core resources: Project, QualityRequirement, Workflow, Stage, QualityMeasure, QualityMeasureElement, Artifact, Role, and ApprovalPolicy.
- Experimental JSON Schemas for structural validation.
- Minimal payment API example.
- Initial governance and contribution process.
