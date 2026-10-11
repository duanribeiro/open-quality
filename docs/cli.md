# CLI reference

The reference command-line interface is installed as `oq`.

```bash
oq <command> ...
```

Run `oq` without arguments to see the command list.

## `oq init`

Create a starter contract through an interactive prompt:

```bash
oq init [quality-directory]
```

When omitted, the destination defaults to `.quality`. The wizard asks for
project details, an optional provider for each role (work management and source
control), and the workflow name and stages. It writes `quality-contract.yaml`
plus the workflow and stage YAML resources. The destination must be new or
empty; existing files are never overwritten. Add a quality characteristic
only if you want to track specific quality requirements; an empty `quality`
list is valid.

Provider credentials are not requested or saved. The generated provider
configuration contains connection details only; `oq apply` reads credentials
from the environment as described in [Providers](providers.md).
When configuring Jira Cloud, the project key must start with an uppercase
letter and contain only uppercase letters and digits, with at least two
characters.

## `oq add characteristic`

Optionally add quality characteristics and their requirement and measure
resources:

```bash
oq add characteristic [quality-directory]
```

When omitted, the directory defaults to `.quality`. The command asks which
characteristics to add and prompts for a requirement statement, priority,
measurement unit, target operator, and target value for each one. It creates
the linked YAML resources and updates `quality-contract.yaml`. Starter
statements and targets should be reviewed; the default `exists` target only
checks that a measurement is present.

## `oq add documentation`

Add a documentation artifact and reference it from the contract:

```bash
oq add documentation [quality-directory]
```

The command prompts for an ID, name, absolute URL, whether the artifact is
required, and its content type.

## `oq add metrics`

Add a quality measure and reference it from the contract:

```bash
oq add metrics [quality-directory]
```

The command prompts for the measure ID, name, unit, description, and data
source.

## `oq add workflow`

Add a workflow and its stages, then select it as the contract's active workflow:

```bash
oq add workflow [quality-directory]
```

Stage IDs are entered as a comma-separated list. The command links each stage
to the previous one in that list. All `oq add` commands default to `.quality`
when the directory is omitted.

## `oq add role`

Create a role and reference it in `QualityContract.spec.roles`:

```bash
oq add role [quality-directory]
```

The command prompts for an ID, name, optional description, and optional
responsibilities separated by semicolons. It creates `roles/<id>.yaml` and
refuses to overwrite existing resource files. IDs already used by any resource
must be replaced with a new ID.

## `oq add team`

Add people to the top-level `team` list in the contract:

```bash
oq add team [quality-directory]
```

Create roles with `oq add role` first. For each person, the command asks for an
email and one or more existing roles, selected by number or ID separated by
commas. It then offers to add another person. Existing members are preserved;
duplicate emails are rejected ignoring case. Both commands default to `.quality`.
These assignments record contract roles and do not grant provider permissions.

## `oq validate`

Validate the complete contract in a directory:

```bash
oq validate [quality-directory]
```

When the directory is omitted, the command validates `.quality` in the current
working directory, matching the default used by `oq init` and `oq add`.
Pass a directory explicitly to validate a different contract, for example
`oq validate examples/minimal`.

The command performs structural validation with the versioned JSON Schemas and
semantic validation for IDs, references, workflow stages, dependency cycles,
quality targets, roles, artifacts, and approval policies.

Exit codes:

- `0`: the contract is valid;
- `1`: the command or contract could not be processed.

## `oq graph`

Render the workflow:

```bash
oq graph [--format ascii|mermaid|both] <quality-directory>
```

The default format is `both`. Stage order comes from `dependsOn`, not from the
order in `Workflow.spec.stages`.

## `oq evaluate`

Evaluate requirements and workflow state:

```bash
oq evaluate <quality-directory> [state.yaml]
```

When the state path is omitted, the CLI looks for `state.yaml` next to the
contract directory. The command reports requirement checks, stage status,
required documentation, and approvals.

Exit codes:

- `0`: the contract is ready;
- `1`: an operational or input error occurred;
- `2`: the contract is valid but the supplied state is not ready.

## `oq status`

Print a concise readiness summary:

```bash
oq status <quality-directory> [state.yaml]
```

Unlike `evaluate`, `status` returns `0` for a valid report even when the
contract is not ready.

## `oq plan`

Preview provider changes:

```bash
oq plan \
  [--target <target.yaml>] \
  [--provider-role <role>] \
  [--state <state.json>] \
  [<quality-directory>]
```

When `--target` is omitted, `plan` uses `.quality/quality-contract.yaml`.
`plan` validates the contract before calculating provider operations. It does
not require credentials for a dry run and does not write to the external
system. If the target file contains a `providers` mapping, omitting
`--provider-role` plans every configured role in YAML order. Pass
`--provider-role <role>` to plan only one role. When `<quality-directory>` is
omitted, the CLI uses the directory containing `<target.yaml>`.

## `oq apply`

Apply provider changes:

```bash
oq apply \
  [--target <target.yaml>] \
  [--provider-role <role>] \
  [--state <state.json>] \
  [<quality-directory>]
```

When `--target` is omitted, `apply` uses `.quality/quality-contract.yaml`.
Credentials are read from environment variables by the selected provider.
Provider state is stored separately from the portable Quality Contract.
`apply` uses the same directory default as `plan`: the parent directory of
`<target.yaml>`.
When several provider roles run and `--state` is supplied, the CLI adds each
role to the state filename so the roles keep separate state.

Supported provider names in this repository include `openproject`,
`jira-cloud`, `github`, and `gitlab`. See [Providers](providers.md) for
configuration examples and scope.
