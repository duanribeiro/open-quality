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
	python3 -m cli.cli validate examples/payment-api/quality
	python3 -m cli.cli graph --format both examples/payment-api/quality
	python3 -m cli.cli evaluate examples/payment-api/quality examples/payment-api/state.yaml
	python3 -m cli.cli status examples/payment-api/quality examples/payment-api/state.yaml

provider-plan: build
	python3 -m cli.cli plan --target examples/payment-api/openproject-target.yaml examples/payment-api/quality
