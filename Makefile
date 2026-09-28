UV ?= uv
PYTHON := .venv/bin/python
.PHONY: help setup test smoke reproduce info
help:
	@echo 'make setup | test | smoke | reproduce | info'
setup:
	$(UV) sync --locked --python 3.12.9 --no-python-downloads
test:
	$(PYTHON) scripts/run.py test
smoke:
	$(PYTHON) scripts/run.py smoke
reproduce:
	$(PYTHON) scripts/run.py reproduce
info:
	$(PYTHON) scripts/run.py info
