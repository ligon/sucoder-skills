.PHONY: lint lint-skills lint-residue check

# lint_skills.py needs PyYAML; override when the default python3 lacks it:
#   make check PYTHON=/path/to/python
PYTHON ?= python3

lint: lint-skills lint-residue

lint-skills:
	$(PYTHON) scripts/lint_skills.py

lint-residue:
	$(PYTHON) scripts/lint_residue.py

check: lint
