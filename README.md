# Open Quality

[![CI](https://github.com/duanribeiro/open-quality/actions/workflows/ci.yml/badge.svg)](https://github.com/duanribeiro/open-quality/actions/workflows/ci.yml)
[![PyPI version](https://img.shields.io/pypi/v/open-quality-cli.svg)](https://pypi.org/project/open-quality-cli/)
[![Python versions](https://img.shields.io/pypi/pyversions/open-quality-cli.svg)](https://pypi.org/project/open-quality-cli/)
[![License: GPL-3.0](https://img.shields.io/badge/license-GPL--3.0-blue.svg)](LICENSE)

**Quality as Code**: describe software-quality expectations as version-controlled YAML, then validate, visualize, and check them from the command line.

![`oq check` running on the minimal example](docs/assets/oq-check.png)

## The problem

Quality expectations usually live in wiki pages, slide decks, and tickets. They
are vague, nobody owns the number, and nothing checks them when a release ships.

Open Quality keeps them in the repository, next to the code, in a format that a
tool can read, validate, and evaluate.

## Before and after

**Before**: a sentence that no tool can check.

> The payment API must stay highly available.

**After**: a requirement with a measurable target. `oq check` evaluates it
against the measurements in the contract.

```yaml
kind: QualityRequirement
metadata:
  id: api-availability
  name: API availability
spec:
  statement: The payment API must achieve at least 99.95% monthly availability.
  priority: critical
  qualityMeasures:
    - qualityMeasure: availability
      target:
        operator: greaterThanOrEqual
        value: 99.95
        unit: percent
```

## Install

Install the `oq` command from PyPI with one command. It requires Python 3.10 or later:

```bash
pipx install open-quality-cli
```

Prefer `pip` in a virtual environment? See the [quick start guide](docs/quick-start.md).

## Quick start

The repository includes a complete example contract for a payment API. Clone it
and run these four commands:

```bash
git clone https://github.com/duanribeiro/open-quality.git
cd open-quality
oq validate examples/minimal
oq graph examples/minimal
oq check examples/minimal
oq evaluate examples/minimal
```

What you should see:

- `oq validate` prints `PASS Payment API` when the contract is structurally valid.
- `oq graph` prints the release workflow as stages and their dependencies.
- `oq check` prints `Requirements: PASS`, because the measured availability and test coverage meet their targets.
- `oq evaluate` prints `Overall: NOT READY` and exits with code `2`. The sample state has stages still pending, so this result is expected.

Ready to model your own system? Run `oq init` and follow
[creating your own contract](docs/quick-start.md#create-your-own-contract).

## Documentation

- [Documentation hub](docs/README.md): concepts, quick start, resource model, CLI, evaluation, and provider guides.
- [CLI reference](docs/cli.md): every `oq` command and its exit codes.
- [Normative specification](SPECIFICATION.md): the complete `0.1` model.
- [Hosted site and blog](https://duanribeiro.github.io/open-quality/).

## Core resources

| Resource | Purpose |
|---|---|
| `QualityContract` | Entry point and scope of a Quality Contract |
| `QualityRequirement` | A quality expectation and its acceptance target |
| `QualityMeasure` | A calculated measure that requirements reference |
| `QualityMeasureElement` | A measured input that a quality measure is calculated from |
| `Workflow` | Ordered or dependent stages in a quality process |
| `Stage` | A reusable phase of work, verification, or decision |
| `Documentation` | A refinement document required to support a quality decision |
| `Role` | A responsibility used for ownership or approval |
| `ApprovalPolicy` | Rules that determine who must approve and how |

Open Quality is not a test framework, workflow engine, certification, AI product,
or hosted platform. It is an open format that tools may author, validate,
evaluate, visualize, or execute.

## Status

Open Quality is experimental. The `0.1` specification invites feedback, and
names and structures may change before `1.0.0`. The reference CLI is published
as [`open-quality-cli` on PyPI](https://pypi.org/project/open-quality-cli/);
see the [changelog](CHANGELOG.md) for what changed in each release.

## Repository map

```text
.
├── SPECIFICATION.md   normative model (0.1)
├── MANIFESTO.md       why Quality as Code
├── PRINCIPLES.md      design principles
├── schema/v0.1/       JSON Schemas used for validation
├── cli/               reference `oq` command-line interface
├── examples/minimal/  payment API quality contract
├── docs/              user documentation
└── tests/             CLI and provider tests
```

## Contributing

First contributions are welcome: a typo fix, a clearer example, a bug report, or
feedback about a workflow that the format cannot yet express are all useful.

1. Read the [Code of Conduct](CODE_OF_CONDUCT.md).
2. Pick a [`good first issue`](https://github.com/duanribeiro/open-quality/labels/good%20first%20issue)
   or check the [open issues](https://github.com/duanribeiro/open-quality/issues)
   and discuss your change.
3. Follow the setup and pull-request guide in [CONTRIBUTING.md](CONTRIBUTING.md).

For help using the project, see [SUPPORT.md](SUPPORT.md). Changes to the core
format follow the lightweight decision process in [GOVERNANCE.md](GOVERNANCE.md).

## Releases

Releases are tagged `vMAJOR.MINOR.PATCH` and published to PyPI. Versions follow
[Semantic Versioning](https://semver.org/). While the project is below `1.0.0`,
a minor release may contain breaking format changes; each one is listed in
[`CHANGELOG.md`](CHANGELOG.md) with the update it requires. Schemas ship with the
CLI under [`schema/v0.1`](schema/v0.1), and resource documents carry no separate
version field.

## License

Copyright © 2026 Duan Ribeiro.

Open Quality is licensed under the GNU General Public License v3.0. Any copy,
redistribution, or modified version must retain the applicable copyright and
license notices, state its changes, and be distributed under GPL-3.0. See
[`LICENSE`](LICENSE) and [`NOTICE`](NOTICE).
