.PHONY: lint check

lint:
	python3 scripts/lint_skills.py

check: lint
