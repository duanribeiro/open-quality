.PHONY: build format format-check test check demo provider-plan

build:
	python3 -m compileall -q cli

format:
	python3 -m black cli tests

format-check:
	python3 -m black --check cli tests

test:
	python3 -m unittest discover -s tests -v

check: build format-check test

demo: build
	python3 -m cli.cli validate examples/minimal
	python3 -m cli.cli graph --format both examples/minimal
	python3 -m cli.cli evaluate examples/minimal examples/state.yaml
	python3 -m cli.cli status examples/minimal examples/state.yaml

provider-plan: build
	python3 -m cli.cli plan --target examples/minimal/project.yaml --provider-role workManagement examples/minimal
