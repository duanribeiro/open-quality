# Quick start

This guide takes a small Quality Contract from disk to a readiness report.

## Prerequisites

- Python 3.10 or newer
- a checkout of this repository

Create an isolated environment and install the CLI:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev]"
```

## Validate the example

The repository includes a complete contract for a payment API:

```bash
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

Copy the example and keep one resource per YAML file:

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
