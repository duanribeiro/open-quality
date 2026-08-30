# CLI reference

The reference command-line interface is installed as `oq`.

```bash
oq <command> ...
```

Run `oq` without arguments to see the command list.

## `oq validate`

Validate the complete contract in a directory:

```bash
oq validate <quality-directory>
```

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
  --target <target.yaml> \
  [--provider-role <role>] \
  [--state <state.json>] \
  <quality-directory>
```

`plan` validates the contract before calculating provider operations. It does
not require credentials for a dry run and does not write to the external
system.

## `oq apply`

Apply provider changes:

```bash
oq apply \
  --target <target.yaml> \
  [--provider-role <role>] \
  [--state <state.json>] \
  <quality-directory>
```

Credentials are read from environment variables by the selected provider.
Provider state is stored separately from the portable Quality Contract.

Supported provider names in this repository include `openproject`,
`jira-cloud`, `github`, and `gitlab`. See [Providers](providers.md) for
configuration examples and scope.

