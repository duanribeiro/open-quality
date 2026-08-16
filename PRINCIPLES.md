# Principles

## 1. Quality is contextual and explicit

Every system should declare what quality means in its domain, risk profile, users, and operating environment.

## 2. Quality evolves with software

The Quality Contract is versioned and reviewed alongside the software it governs. A material change to the system may require a change to its contract.

## 3. Requirements are measurable or verifiable

A requirement should identify an objective target, required documentation, or an accountable human decision. Vague aspirations are not enforceable contracts.

## 4. Decisions are traceable

Requirements connect to quality measures, documentation, workflow stages, roles, and approvals so that a decision can be reconstructed.

## 5. Process is declarative

The contract describes desired quality governance without prescribing a particular CI system, test runner, repository host, or dashboard.

## 6. Automation is optional; accountability is not

Tools may automate measurement and evaluation, but the contract must preserve ownership and make human approvals explicit where judgment is required.

## 7. Exceptions are visible and bounded

Future versions should represent exceptions with a reason, owner, scope, expiry, and audit history. Silent bypasses violate the methodology.

## 8. The specification is open and portable

The same contract should be consumable by independent implementations. Core semantics must not depend on a proprietary provider.

## 9. The core remains small

New concepts enter the core only when they cannot be expressed through composition or extensions and have demonstrated use across multiple domains.
