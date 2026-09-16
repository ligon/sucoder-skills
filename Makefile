.PHONY: lint lint-skills lint-residue check

lint: lint-skills lint-residue

lint-skills:
	python3 scripts/lint_skills.py

lint-residue:
	python3 scripts/lint_residue.py

check: lint
