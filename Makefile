SHELL := /bin/bash

VENV := .venv
PYTHON := $(VENV)/bin/python
PIP := $(VENV)/bin/pip

.PHONY: help setup test run

help:
	@printf "Targets:\n"
	@printf "  make setup  - create venv, install deps, create .env if missing\n"
	@printf "  make test   - run test suite\n"
	@printf "  make run    - start bot with env from .env\n"

setup:
	python3 -m venv $(VENV)
	$(PYTHON) -m pip install -U pip
	$(PIP) install -e ".[dev]"
	@if [ ! -f .env ]; then cp .env.example .env; fi
	@printf "Setup complete. Edit .env with BOT_TOKEN and OWNER_CHAT_ID before running.\n"

test:
	$(PYTHON) -m pytest -q

run:
	@if [ ! -f .env ]; then printf "Missing .env. Run 'make setup' first.\n"; exit 1; fi
	@set -a; source .env; set +a; $(PYTHON) -m hourbot.main
