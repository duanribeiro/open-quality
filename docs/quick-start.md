# Quick start

This guide takes a small Quality Contract from disk to a readiness report.

## Prerequisites

- Python 3.10 or newer

Install the published [Open Quality CLI package from PyPI](https://pypi.org/project/open-quality-cli/) with `pipx`:

```bash
pipx install open-quality-cli
```

`pipx` keeps the CLI in an isolated environment. To install with `pip`, first activate a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install open-quality-cli
```

## Validate the example

Clone the repository to use its complete example contract for a payment API:

```bash
git clone https://github.com/duanribeiro/open-quality.git
cd open-quality
oq validate examples/minimal
```

The command checks the resource schemas and the relationships between
resources. A successful result looks like:

```text
PASS Payment API
```

Validation does not execute tests or call an external provider.

## Render the workflow

Print the workflow as terminal text and Mermaid:

```bash
oq graph --format both examples/minimal
```

Use `--format ascii` for terminal output only, or `--format mermaid` when the
result will be embedded in Markdown.

## Evaluate readiness

The example contains a local state snapshot at `examples/state.yaml`. Evaluate
the contract against it:

```bash
oq evaluate examples/minimal
```

For a concise operational summary:

```bash
oq status examples/minimal
```

The evaluator checks requirement targets, required documentation, stage
completion, and approval policies. `oq evaluate` returns exit code `2` when
the contract is valid but the state is not ready.

## Create your own contract

To start from a guided scaffold in the default `.quality` directory, run:

```bash
oq init
```

You can pass a different destination, such as `oq init my-contract`.

The CLI asks about project details, separately configures at most one
work-management provider and one source-control provider, and creates the
workflow and its stages. Quality characteristics are optional. Add one only if
you want to track specific quality requirements; otherwise, validate directly.

```bash
oq validate
```

Without a directory argument, `oq validate` checks `.quality` in the current
working directory. Pass a custom directory when needed, such as
`oq validate my-contract`.

To add a characteristic before validating, run:

```bash
oq add characteristic
oq validate
```

You can also add documentation and metrics when needed:

```bash
oq add documentation
oq add metrics
```

Review generated requirement statements and targets, then validate the
contract. See the [`oq init` reference](cli.md#oq-init) and the `oq add`
references for [characteristics](cli.md#oq-add-characteristic),
[documentation](cli.md#oq-add-documentation), [metrics](cli.md#oq-add-metrics),
and [workflows](cli.md#oq-add-workflow).

You can also copy and adapt the example manually. Keep one resource per YAML
file:

```text
my-contract/
├── quality-contract.yaml
├── workflows/
├── stages/
├── quality-requirements/
├── quality-measures/
├── quality-measure-elements/
├── artifacts/
├── roles/
└── approval-policies/
```

The directory names are for organization only. Open Quality identifies a
resource by its `kind`, and references use `metadata.id`.

Start with a quality contract and a workflow:

```yaml
specVersion: "0.1"
kind: QualityContract
metadata:
  id: checkout-api
  name: Checkout API
spec:
  workflow: release
  quality:
    - characteristic: reliability
      subcharacteristics:
        - subcharacteristic: availability
          requirements:
            - api-availability
```

Then add the referenced resources described in
[Resources](resources.md), and validate the directory:

```bash
oq validate my-contract
```

## Run the project checks

For changes to the CLI or its tests:

```bash
make check
```
