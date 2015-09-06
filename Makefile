# System variables
ENV_DIR=$(CURDIR)/.env
PYTHON=$(ENV_DIR)/bin/python
NOSE=$(ENV_DIR)/bin/nosetests
COVERAGE=$(ENV_DIR)/bin/coverage
PROJECT_NAME=pgclient
CODE_DIR=$(CURDIR)/$(PROJECT_NAME)


help:
# target: help - Display callable targets
	@grep -e "^# target:" [Mm]akefile | sed -e 's/^# target: //g'

.PHONY: env
env:
# target: env - create virtualenv and install packages
	@virtualenv $(ENV_DIR)
	@$(ENV_DIR)/bin/pip install -r $(CURDIR)/requirements.txt

.PHONY: pypi_upload
pypi_upload:
# target: pypi_upload - Upload package to pypi.python.org
	@$(PYTHON) setup.py sdist upload

.PHONY: test
test: env
	@$(NOSE) $(CODE_DIR)/tests.py

.PHONY: system_test
system_test: env
# target: test - Run system_test
	@$(NOSE) system_test.py
	

.PHONY: test_ci
test_ci: env
# target: test_ci - Run tests command adapt for CI systems
	@$(NOSE) $(CODE_DIR)/tests.py

.PHONY: test_coverage
# target: test_coverage - Run tests with coverage
test_coverage: env
	@$(COVERAGE) run --source=$(PROJECT_NAME) $(NOSE) $(CODE_DIR)/tests.py
