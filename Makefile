.PHONY: build format format-check test check demo provider-plan \
	package-tools clean-package package publish-test publish

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
	# evaluate exits 2 when the sample state is not ready; that is expected here.
	-python3 -m cli.cli evaluate examples/minimal examples/state.yaml
	python3 -m cli.cli status examples/minimal examples/state.yaml

provider-plan: build
	python3 -m cli.cli plan --target examples/minimal/quality-contract.yaml --provider-role workManagement examples/minimal

# Build and publish the Python package to TestPyPI or PyPI.
# Twine prompts for credentials unless TWINE_USERNAME / TWINE_PASSWORD are set.
# `make publish` also asks for a higher stable MAJOR.MINOR.PATCH version.
package-tools:
	python3 -m pip install --upgrade build twine

clean-package:
	rm -rf build dist *.egg-info

package: package-tools clean-package
	python3 -m build
	python3 -m twine check dist/*

publish-test: package
	python3 -m twine upload --repository testpypi dist/*

publish:
	python3 scripts/prompt_version.py
	$(MAKE) package
	python3 -m twine upload dist/*
