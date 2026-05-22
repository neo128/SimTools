.PHONY: test validate cli-list cli-status cli-compare cli-doctor cli-validate

test:
	PYTHONPATH=src pytest

validate:
	./scripts/validate_project.sh

cli-list:
	PYTHONPATH=src python -m simtools list

cli-status:
	PYTHONPATH=src python -m simtools status

cli-compare:
	PYTHONPATH=src python -m simtools compare

cli-doctor:
	PYTHONPATH=src python -m simtools doctor

cli-validate:
	PYTHONPATH=src python -m simtools validate
