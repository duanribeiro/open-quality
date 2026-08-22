# Contributing to Open Quality

Thank you for helping make Quality as Code practical and interoperable. You do
not need to be a specification expert to contribute: documentation fixes, small
examples, bug reports, tests, and feedback from real delivery work are all
valuable.

Please read the [Code of Conduct](CODE_OF_CONDUCT.md) before participating.

## Choose a contribution path

| You want to... | Best first step |
|---|---|
| Fix wording, links, or an example | Open a focused pull request. |
| Report a defect | Use the [bug report](.github/ISSUE_TEMPLATE/bug_report.md) template with a minimal reproduction. |
| Suggest a capability or schema change | Open a [feature proposal](.github/ISSUE_TEMPLATE/feature_request.md) before coding. |
| Ask how to use the CLI or format | Start with [SUPPORT.md](SUPPORT.md); then open a question issue if needed. |
| Report a security problem | Follow [SECURITY.md](SECURITY.md), never a public issue. |

For a new core resource or any change that affects interoperability, start with
a public proposal. This avoids spending time on an implementation before the
community agrees on the problem and direction.

## Set up your development environment

You need Python 3.10 or later and Git.

```bash
git clone https://github.com/duanribeiro/open-quality.git
cd open-quality
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev]"
make check
```

Useful commands:

```bash
make format          # format Python code
make check           # compile, format-check, and run tests
oq validate examples # validate the included example contract
oq graph examples    # inspect its stage dependencies
```

## Make a change

1. Search existing issues and pull requests to avoid duplicate work.
2. Create a focused branch from `main`.
3. Explain the real quality-management use case, not only the desired YAML
   shape.
4. Prefer the smallest change that solves the use case without adding
   provider-specific fields to the core format.
5. Add or update tests, examples, and documentation with the code.
6. Run `make check` before opening a pull request.

## What to include in a pull request

Use a clear title and explain the problem, the change, and how you validated it.
Keep unrelated cleanup in a separate pull request.

For specification changes, update the applicable items:

- `SPECIFICATION.md` and the versioned JSON Schemas;
- valid and invalid test fixtures;
- at least one example and its documentation;
- `CHANGELOG.md`;
- migration notes when a change is breaking.

## How changes are reviewed

Maintainers review changes for clarity, portability, minimality, composability,
implementability, and alignment with the project principles. Provider-specific
behavior belongs in adapters or extensions rather than the core.

Editorial corrections and small bug fixes can usually be reviewed directly.
Material semantic changes follow the public proposal process described in
[GOVERNANCE.md](GOVERNANCE.md). Be prepared to refine a proposal based on
feedback; that conversation is part of building an interoperable format.

## License

By contributing, you agree that your contribution is licensed under the
repository's [GPL-3.0 license](LICENSE).
