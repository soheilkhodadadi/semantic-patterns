#################################################################################
# GLOBALS                                                                       #
#################################################################################

PROJECT_NAME = semantic-patterns
PYTHON_VERSION = 3.11
VENV_DIR = .venv
VENV_PYTHON = $(VENV_DIR)/bin/python
VENV_PIP = $(VENV_PYTHON) -m pip
REPO_PYTHONPATH = $(CURDIR)/src:$(CURDIR)/packages/labcore/src:$(CURDIR)/packages/director/src
REPO_PYTHON = PYTHONPATH="$(REPO_PYTHONPATH)" $(VENV_PYTHON)
BOOTSTRAP_PYTHON ?= python3.11
PYTHON_INTERPRETER = $(VENV_PYTHON)
ITER ?= 1
PHASE ?= label-expansion

#################################################################################
# COMMANDS                                                                      #
#################################################################################


## Install Python dependencies into the canonical repo-local .venv
.PHONY: requirements
requirements: bootstrap
	@echo "[OK] dependencies managed through $(VENV_DIR)"


## Bootstrap local .venv with project + dev dependencies
.PHONY: bootstrap
bootstrap:
	@if [ ! -x "$(VENV_PYTHON)" ]; then \
		if ! command -v "$(BOOTSTRAP_PYTHON)" >/dev/null 2>&1; then \
			echo "[ERROR] $(BOOTSTRAP_PYTHON) not found. Install native Python $(PYTHON_VERSION) first."; \
			exit 1; \
		fi; \
		echo ">>> creating $(VENV_DIR) with $$($(BOOTSTRAP_PYTHON) -c 'import os,sys; print(os.path.realpath(sys.executable))')"; \
		$(BOOTSTRAP_PYTHON) -m venv --copies $(VENV_DIR); \
	fi
	$(VENV_PIP) install --upgrade pip setuptools wheel
	$(VENV_PIP) install -e ".[dev]"
	@if [ -f "packages/labcore/pyproject.toml" ]; then \
		$(VENV_PIP) install -e "./packages/labcore"; \
	fi
	@if [ -f "packages/director/pyproject.toml" ]; then \
		$(VENV_PIP) install -e "./packages/director"; \
	fi
	$(VENV_PIP) install --upgrade "pyarrow>=16.1.0" "wrds>=3.3.0" "psycopg2-binary>=2.9.0" "numexpr>=2.8.4" "bottleneck>=1.3.6"


## Rebuild the canonical .venv from the configured Python bootstrap interpreter
.PHONY: rebuild-venv
rebuild-venv:
	rm -rf $(VENV_DIR)
	$(MAKE) bootstrap


## Diagnose interpreter/tooling setup for reliable local runs
.PHONY: doctor
doctor:
	@echo ">>> shell python: $$(command -v python || echo missing)"
	@echo ">>> shell pip:    $$(command -v pip || echo missing)"
	@python --version || true
	@pip --version || true
	@if python -m pip --version >/dev/null 2>&1; then \
		echo "[OK] shell python -m pip is available"; \
	else \
		echo "[ERROR] shell python cannot run -m pip"; \
		exit 1; \
	fi
	@if [ "$$CONDA_DEFAULT_ENV" = "base" ] && [ -z "$$VIRTUAL_ENV" ]; then \
		echo "[WARN] conda base is active and $(VENV_DIR) is not activated."; \
		echo "       prefer: source $(VENV_DIR)/bin/activate"; \
	fi
	@if [ ! -x "$(VENV_PYTHON)" ]; then \
		echo "[ERROR] $(VENV_PYTHON) not found. Run 'make bootstrap' first."; \
		exit 1; \
	fi
	@echo ">>> venv python: $(VENV_PYTHON)"
	@$(VENV_PYTHON) --version
	@if $(VENV_PYTHON) -m pip --version >/dev/null 2>&1; then \
		echo "[OK] venv python -m pip is available"; \
	else \
		echo "[ERROR] venv python cannot run -m pip"; \
		exit 1; \
	fi
	@if $(VENV_PYTHON) -c "import platform, sys; assert sys.version_info >= (3, 11), 'Python 3.11+ required'; host='$(shell uname -m)'; assert not (sys.platform == 'darwin' and host == 'arm64' and platform.machine() != 'arm64'), 'arm64 host requires arm64 .venv'; print('[OK] venv interpreter version/arch compatible')" >/dev/null 2>&1; then \
		echo "[OK] venv interpreter version/arch compatible"; \
	else \
		echo "[ERROR] incompatible venv interpreter version or architecture"; \
		exit 1; \
	fi
	@if $(REPO_PYTHON) -c "import semantic_ai_washing" >/dev/null 2>&1; then \
		echo "[OK] semantic_ai_washing import works in $(VENV_DIR)"; \
	else \
		echo "[ERROR] cannot import semantic_ai_washing from $(VENV_DIR)"; \
		exit 1; \
	fi
	@if $(REPO_PYTHON) -c "import semantic_labcore" >/dev/null 2>&1; then \
		echo "[OK] semantic_labcore import works in $(VENV_DIR)"; \
	else \
		echo "[ERROR] cannot import semantic_labcore from $(VENV_DIR)"; \
		exit 1; \
	fi
	@if $(REPO_PYTHON) -c "import semantic_director" >/dev/null 2>&1; then \
		echo "[OK] semantic_director import works in $(VENV_DIR)"; \
	else \
		echo "[ERROR] cannot import semantic_director from $(VENV_DIR)"; \
		exit 1; \
	fi
	@if $(VENV_PYTHON) -c "import pyarrow" >/dev/null 2>&1; then \
		echo "[OK] pyarrow import works in $(VENV_DIR)"; \
	else \
		echo "[ERROR] cannot import pyarrow from $(VENV_DIR)"; \
		exit 1; \
	fi
	@if $(VENV_PYTHON) -c "import wrds, psycopg2" >/dev/null 2>&1; then \
		echo "[OK] wrds + psycopg2 imports work in $(VENV_DIR)"; \
	else \
		echo "[ERROR] cannot import wrds and psycopg2 from $(VENV_DIR)"; \
		exit 1; \
	fi
	@$(VENV_PYTHON) -m ruff --version
	@$(VENV_PYTHON) -m pytest --version
	@echo "[OK] doctor complete"


## Run director health checks
.PHONY: director-doctor
director-doctor:
	@$(REPO_PYTHON) -m semantic_ai_washing.director.cli doctor --strict-secrets --json


## Generate director plan artifacts for an iteration/phase
.PHONY: director-plan
director-plan:
	@$(REPO_PYTHON) -m semantic_ai_washing.director.cli plan --iteration $(ITER) --phase $(PHASE)


## Show director status snapshot
.PHONY: director-status
director-status:
	@$(REPO_PYTHON) -m semantic_ai_washing.director.cli status
	
## Refresh generated paper snippets/tables from current artifacts
.PHONY: paper-refresh
paper-refresh:
	@$(REPO_PYTHON) -m semantic_ai_washing.analysis.generate_paper_assets


## Build the repo-native paper draft into markdown and docx
.PHONY: paper-build
paper-build:
	@$(REPO_PYTHON) -m semantic_ai_washing.analysis.generate_paper_assets
	@$(REPO_PYTHON) scripts/build_paper.py



## Delete all compiled Python files
.PHONY: clean
clean:
	find . -type f -name "*.py[co]" -delete
	find . -type d -name "__pycache__" -delete


## Lint using ruff (use `make format` to do formatting)
.PHONY: lint
lint:
	$(VENV_PYTHON) -m ruff format --check
	$(VENV_PYTHON) -m ruff check

## Format source code with ruff
.PHONY: format
format:
	$(VENV_PYTHON) -m ruff check --fix
	$(VENV_PYTHON) -m ruff format





## Set up Python interpreter environment
.PHONY: create_environment
create_environment: bootstrap
	@echo ">>> canonical environment ready at $(VENV_DIR). Activate with:\nsource $(VENV_DIR)/bin/activate"
	



#################################################################################
# PROJECT RULES                                                                 #
#################################################################################


## Make dataset
.PHONY: data
data: requirements
	$(REPO_PYTHON) src/dataset.py


#################################################################################
# Self Documenting Commands                                                     #
#################################################################################

.DEFAULT_GOAL := help

define PRINT_HELP_PYSCRIPT
import re, sys; \
lines = '\n'.join([line for line in sys.stdin]); \
matches = re.findall(r'\n## (.*)\n[\s\S]+?\n([a-zA-Z_-]+):', lines); \
print('Available rules:\n'); \
print('\n'.join(['{:25}{}'.format(*reversed(match)) for match in matches]))
endef
export PRINT_HELP_PYSCRIPT

help:
	@$(PYTHON_INTERPRETER) -c "${PRINT_HELP_PYSCRIPT}" < $(MAKEFILE_LIST)
