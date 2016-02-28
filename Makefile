# System variables
ENV_DIR=$(CURDIR)/.env
PYTHON=$(ENV_DIR)/bin/python
NOSE=$(ENV_DIR)/bin/nosetests
PROJECT_NAME=pgclient
CODE_DIR=$(CURDIR)/$(PROJECT_NAME)


help:
# target: help - Display callable targets
	@grep -e "^# target:" [Mm]akefile | sed -e 's/^# target: //g'

env:
# target: env - create virtualenv and install packages
	@virtualenv $(ENV_DIR)
	@$(ENV_DIR)/bin/pip install -r $(CURDIR)/requirements.txt

pypi_upload: clean
# target: pypi_upload - Upload package to pypi.python.org
	@$(ENV_DIR)/bin/pip install wheel
	@$(PYTHON) setup.py bdist_wheel upload -r pypi

test: env
	@$(NOSE) $(CODE_DIR)/tests.py

system_test: env
# target: test - Run system_test
	@$(NOSE) --with-coverage $(CODE_DIR)/system_test/system_test.py
	
clean:
# target: clean - cleanup build stuff
	@echo "Clean .pyc" && find . -name "*.pyc" | xargs rm -f
	@echo "Clean tmp folders and files" && rm -rf dist .coverage MANIFEST


.PHONY: system_test test pypi_upload env help clean




