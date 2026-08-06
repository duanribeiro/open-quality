# Open Quality

Open Quality is an experimental, vendor-neutral specification for **Quality as Code**: the practice of representing software-quality expectations and governance as declarative, version-controlled artifacts.

The specification defines a **Quality Contract** that can describe:

- what quality means for a software system;
- which requirements and measurable targets apply;
- which workflow and stages a change must pass through;
- which quality gates block progression;
- who owns work and who must approve decisions;
- which refinement documentation and execution reports support a quality decision.

Open Quality is not a test framework, workflow engine, certification, AI product, or hosted platform. It is an open format that tools may author, validate, evaluate, visualize, or execute.

## Status

Version `0.1.0` is an experimental foundation intended to invite feedback. Names and structures may change before `1.0.0`.

## Repository map

```text
.
├── MANIFESTO.md
├── PRINCIPLES.md
├── SPECIFICATION.md
├── schema/v0.1/
├── examples/minimal/
└── docs/
```

## Start with the minimal contract

The example in [`examples/minimal`](examples/minimal/README.md) describes a small release process for a payment API. Each YAML document declares one resource using a common envelope:

```yaml
specVersion: "0.1"
kind: Requirement
metadata:
  id: api-availability
  name: API availability
spec:
  statement: The API must remain available to customers.
  priority: critical
  qualityLevel: external
```

Read [`SPECIFICATION.md`](SPECIFICATION.md) for the normative model and [`docs/syntax.md`](docs/syntax.md) for authoring conventions.

## Install

The optional command-line interface requires Python 3.10 or later. Clone the
repository, create an isolated environment, and install the local project:

```bash
git clone <repository-url>
cd open-quality
python3 -m venv .venv
source .venv/bin/activate
python -m pip install .
```

For local development, install the formatter as well:

```bash
python -m pip install -e ".[dev]"
```

## Quick start

Validate the minimal Quality Contract included with the repository:

```bash
oq validate examples/minimal
```

Explore a richer example and run the project's checks:

```bash
oq graph examples/payment-api/quality
oq evaluate examples/payment-api/quality examples/payment-api/state.yaml
make check
```

`oq validate` confirms the contract is structurally valid. `oq graph` renders
its workflow dependencies, and `oq evaluate` evaluates its gates against a
state file. Run `oq` without arguments to see the available commands.

Before opening a pull request, run `make format` to apply the project's Black
formatting standard and `make check` to verify formatting, compilation, and
tests.

## Core resources

| Resource | Purpose |
|---|---|
| `Project` | Entry point and scope of a Quality Contract |
| `Requirement` | A quality expectation and its acceptance target |
| `Workflow` | Ordered or dependent stages in a quality process |
| `Stage` | A reusable phase of work, verification, or decision |
| `Gate` | Objective conditions that must be satisfied |
| `Metric` | A typed measurement referenced by requirements or gates |
| `Artifact` | A refinement document or execution report required to support a quality decision |
| `Role` | A responsibility used for ownership or approval |
| `ApprovalPolicy` | Rules that determine who must approve and how |

## Contributing

Open an issue before proposing a new core resource. See
[`CONTRIBUTING.md`](CONTRIBUTING.md), [`GOVERNANCE.md`](GOVERNANCE.md),
[`CODE_OF_CONDUCT.md`](CODE_OF_CONDUCT.md), and [`SUPPORT.md`](SUPPORT.md).

## Compatibility and releases

Open Quality is currently at specification version `0.1.0` and is experimental.
The CLI supports Python 3.10 and later. Versioned schemas live under
[`schema/v0.1`](schema/v0.1); tools should select schemas by the contract's
`specVersion` rather than assuming future compatibility.

Until `1.0.0`, the project may make breaking changes. Each release will be
tagged, documented in [`CHANGELOG.md`](CHANGELOG.md), and identify its schema
compatibility and migration notes where needed. After `1.0.0`, releases will
follow semantic versioning: patch releases are backward-compatible fixes,
minor releases add backward-compatible functionality, and major releases may
contain breaking changes.

## License

Copyright © 2026 Duan Ribeiro.

Open Quality is licensed under the GNU General Public License v3.0. Any copy,
redistribution, or modified version must retain the applicable copyright and
license notices, state its changes, and be distributed under GPL-3.0. See
[`LICENSE`](LICENSE) and [`NOTICE`](NOTICE).
