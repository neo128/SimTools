.PHONY: test cli-list cli-compare cli-doctor

test:
	PYTHONPATH=src pytest

cli-list:
	PYTHONPATH=src python -m simtools list

cli-compare:
	PYTHONPATH=src python -m simtools compare

cli-doctor:
	PYTHONPATH=src python -m simtools doctor
