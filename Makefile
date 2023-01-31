MAKEFLAGS = --no-print-directory --no-builtin-rules
PACKAGE = fortifyapi
WORKDIR?=.
VENVDIR?=$(WORKDIR)/venv
VENV=$(VENVDIR)/bin

_PY_AUTODETECT_MSG=Detected Python interpreter: $(PY). Use PY environment variable to override

ifndef PY
_PY_OPTION:=$(VENVDIR)/bin/python
ifeq (ok,$(shell $(_PY_OPTION) -c "print('ok')" $(NULL_STDERR)))
PY=$(_PY_OPTION)
$(info $(_PY_AUTODETECT_MSG))
endif
endif

SYSTEM_PYTHON  = $(or $(shell which python3), $(shell which python))
PYTHON         = $(or $(wildcard venv/bin/python), $(SYSTEM_PYTHON))

.PHONY: all
all: install

.PHONY: clean
clean:
	@echo "🚀 Cleaning $(PACKAGE)"
	@rm -rf $(VENVDIR) && rm -rf $(WORKDIR)/dist
	@find . -type f -name '*.pyc' -delete

.PHONY: dependency-install
dependency-install:
	@echo "🚀 Installing dependencies for $(PACKAGE)"
	$(SYSTEM_PYTHON) -m venv $(VENVDIR)
	$(VENV)/python3 -m pip install --upgrade pip
	$(VENV)/python3 -m pip install poetry build wheel twine deptry isort black

# Run code quality tools.
.PHONY: check
check: dependency-install
	@echo "🚀 Checking Poetry lock file consistency with 'pyproject.toml': Running poetry lock --check"
	@$(VENV)/poetry lock --check
	@echo "🚀 Checking configuration: Running check"
	@$(VENV)/poetry check
	@echo "🚀 Checking for obsolete dependencies: Running deptry"
	@$(VENV)/deptry $(WORKDIR)
	#TODO: reformat files
	#@echo "🚀 Running black"
	#@$(VENV)/poetry run black --check $(WORKDIR)/$(PACKAGE)
	@echo "🚀 Running isort"
	@$(VENV)/isort --atomic $(WORKDIR)/$(PACKAGE)

.PHONY: build
build: clean check
	@echo "🚀 Building $(PACKAGE)"
	@$(VENV)/poetry build

.PHONY: install
install: build
	@echo "🚀 Installing $(PACKAGE)"
	$(VENV)/poetry install

# debug if needed
.PHONY: debug
debug:
	@$(VENV)/python -c "import sys; print('Python ' + sys.version.replace('\n',''))"
	@$(VENV)/pip --version

# publish a release to pypi.
.PHONY: publish
publish: build
	@echo "🚀 Publishing to PyPi"
	@poetry publish -vvv --build -n -r ${PYPI_REPOSITORY}
	@echo venv: $(VENVDIR)

.DEFAULT_GOAL := all
