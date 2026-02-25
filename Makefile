#################################################################################
# GLOBALS                                                                       #
#################################################################################

PROJECT_NAME = semantic-patterns
PYTHON_VERSION = 3.9
PYTHON_INTERPRETER = python
VENV_DIR = .venv
VENV_PYTHON = $(VENV_DIR)/bin/python
VENV_PIP = $(VENV_PYTHON) -m pip

#################################################################################
# COMMANDS                                                                      #
#################################################################################


## Install Python dependencies
.PHONY: requirements
requirements:
	conda env update --name $(PROJECT_NAME) --file environment.yml --prune


## Bootstrap local .venv with project + dev dependencies
.PHONY: bootstrap
bootstrap:
	@if [ ! -x "$(VENV_PYTHON)" ]; then \
		echo ">>> creating $(VENV_DIR) with python3.9"; \
		python3.9 -m venv $(VENV_DIR); \
	fi
	$(VENV_PIP) install --upgrade pip setuptools wheel
	$(VENV_PIP) install -e ".[dev]"
	$(VENV_PIP) install --upgrade "numexpr>=2.8.4" "bottleneck>=1.3.6"


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
	@if $(VENV_PYTHON) -c "import semantic_ai_washing" >/dev/null 2>&1; then \
		echo "[OK] semantic_ai_washing import works in $(VENV_DIR)"; \
	else \
		echo "[ERROR] cannot import semantic_ai_washing from $(VENV_DIR)"; \
		exit 1; \
	fi
	@$(VENV_PYTHON) -m ruff --version
	@$(VENV_PYTHON) -m pytest --version
	@echo "[OK] doctor complete"
	



## Delete all compiled Python files
.PHONY: clean
clean:
	find . -type f -name "*.py[co]" -delete
	find . -type d -name "__pycache__" -delete


## Lint using ruff (use `make format` to do formatting)
.PHONY: lint
lint:
	ruff format --check
	ruff check

## Format source code with ruff
.PHONY: format
format:
	ruff check --fix
	ruff format





## Set up Python interpreter environment
.PHONY: create_environment
create_environment:
	conda env create --name $(PROJECT_NAME) -f environment.yml
	
	@echo ">>> conda env created. Activate with:\nconda activate $(PROJECT_NAME)"
	



#################################################################################
# PROJECT RULES                                                                 #
#################################################################################


## Make dataset
.PHONY: data
data: requirements
	$(PYTHON_INTERPRETER) src/dataset.py


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
