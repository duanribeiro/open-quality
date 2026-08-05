# Open Quality reference implementation

`open-quality-cli` is the command-line implementation of the experimental [Open Quality 0.1 specification](../open-quality). It proves that a Quality as Code contract can be parsed, validated, visualized, and evaluated without a platform, database, AI service, or vendor integration.

It is deliberately **not QualityOS**. The engine consumes portable Open Quality resources and a local state snapshot.

## Capabilities

- strict YAML parsing for all nine Open Quality 0.1 resource kinds;
- structural checks and semantic validation of IDs, references, graph cycles, operators, roles, and approval policies;
- Mermaid and terminal workflow rendering;
- evaluation of requirement targets, gates, metrics, required documentation, reports, stages, and approvals;
- concise workflow status output.
- provider plans and idempotent materialization in OpenProject Community through API v3.

## Build and run

Python 3.10 or newer is required.

```bash
make check
make demo
```

Or run commands individually:

```bash
python -m pip install -e ".[dev]"
oq validate examples/payment-api/quality
oq graph --format both examples/payment-api/quality
oq evaluate examples/payment-api/quality examples/payment-api/state.yaml
oq status examples/payment-api/quality examples/payment-api/state.yaml
oq plan --target examples/payment-api/openproject-target.yaml examples/payment-api/quality
```

`evaluate` exits with status `2` when the contract is valid but the supplied state is not ready. Validation and operational errors exit with status `1`.

## State snapshot

Open Quality 0.1 defines representation and validation, not runtime state. This reference implementation adds a small, explicitly implementation-specific `state.yaml` input so the executable semantics can be demonstrated:

```yaml
metrics:
  test-pass-rate: 100
stages:
  continuous-integration: completed
approvals:
  production-release-approval: [quality-lead, engineering-manager]
documentation:
  technical-design: true
reports:
  automated-test-report: true
```

The state file does not extend or modify the Open Quality specification. A future adapter could produce the same state from CI, test, observability, or approval systems.

## OpenProject Community provider

The OpenProject provider keeps the Open Quality contract vendor-neutral. Provider details live in a separate target file:

```yaml
provider: openproject
name: community-openproject
baseURL: http://localhost:8080
tokenEnv: OPENPROJECT_API_TOKEN
project: payments
workPackageTypeHref: /api/v3/types/1
notify: false
```

`project` is the identifier of an existing OpenProject project. The authenticated user needs permission to create and edit work packages there. `workPackageTypeHref` selects a work package type enabled for that project; obtain the correct href from the installation's API documentation at `/api/docs` or API v3 responses.

Generate a dry-run plan without credentials or external writes:

```bash
oq plan \
  --target examples/payment-api/openproject-target.yaml \
  --state .oq/openproject-state.json \
  examples/payment-api/quality
```

Apply it with an API token generated in OpenProject account settings:

```bash
export OPENPROJECT_API_TOKEN='replace-me'

oq apply \
  --target examples/payment-api/openproject-target.yaml \
  --state .oq/openproject-state.json \
  examples/payment-api/quality
```

The provider maps resources as follows:

| Open Quality | OpenProject Community |
|---|---|
| `Project` | Root work package inside the configured OpenProject project |
| `Requirement` | Child work package of the root |
| `Stage` | Child work package of the root |
| `Gate` | Child work package of its first referencing stage |

Provider state records OpenProject IDs, HATEOAS links and content hashes. Reapplying an unchanged contract is a no-op; changed resources are updated with OpenProject optimistic locking. Multiple Open Quality projects can share one OpenProject project because each contract receives its own root work package.

This first provider does not create OpenProject projects, configure work package types, delete removed resources, or synchronize OpenProject statuses back into `state.yaml`. Those operations require additional administrative policy and are intentionally outside the initial safe apply behavior.

## Architecture

```text
cli/cli.py      command-line adapter
cli/core.py     filesystem loading, strict YAML parsing, validation and evaluation
cli/provider.py provider state and OpenProject API v3 adapter
cli/renderer.py terminal and Mermaid views
cli/model.py    shared contract and result model
```

The core evaluation path is independent of the CLI:

```text
Quality Contract -> Loader -> Parser -> Validator -> Evaluator -> Renderer
                                      + state.yaml ---^
```

## Example

The `examples/payment-api` contract models a release workflow with design review, CI, staging, and production approval. Copy it and change a metric, stage status, documentation or report value, or approval to see readiness change.

## Scope

This MVP does not execute tests, call external providers, persist state, or provision CI policies. Its purpose is to be readable, testable evidence that the Open Quality specification has coherent machine-executable semantics.
