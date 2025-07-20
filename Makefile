# Makefile for AtPack Parser development

.PHONY: help install install-dev test lint format clean build publish

help: ## Show this help message
	@echo "AtPack Parser Development Commands"
	@echo "=================================="
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Install package in development mode
	pip install -e .

install-dev: ## Install package with development dependencies
	pip install -e ".[dev]"

test: ## Run tests
	pytest tests/ -v

test-coverage: ## Run tests with coverage
	pytest tests/ --cov=src/atpack_parser --cov-report=html --cov-report=term

lint: ## Run linting (ruff and mypy)
	ruff check src/atpack_parser/
	mypy src/atpack_parser/

format: ## Format code with black
	black src/atpack_parser/ tests/ examples/

format-check: ## Check code formatting
	black --check src/atpack_parser/ tests/ examples/

clean: ## Clean build artifacts
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf .pytest_cache/
	rm -rf .coverage
	rm -rf htmlcov/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

build: ## Build distribution packages
	python -m build

publish: ## Publish to PyPI (requires build first)
	python -m twine upload dist/*

setup: ## Run development setup script
	python setup_dev.py

example: ## Run example script (requires ATPACK_FILE environment variable)
	@if [ -z "$(ATPACK_FILE)" ]; then \
		echo "Please set ATPACK_FILE environment variable"; \
		echo "Example: make example ATPACK_FILE=../public/atpacks/Atmel.ATmega_DFP.2.2.509_dir_atpack"; \
	else \
		python examples/example_usage.py "$(ATPACK_FILE)"; \
	fi

# CLI testing targets
cli-help: ## Test CLI help
	atpack --help

cli-scan: ## Scan for AtPack files (requires ATPACK_DIR)
	@if [ -z "$(ATPACK_DIR)" ]; then \
		echo "Please set ATPACK_DIR environment variable"; \
		echo "Example: make cli-scan ATPACK_DIR=../public/atpacks"; \
	else \
		atpack scan "$(ATPACK_DIR)"; \
	fi

cli-devices: ## List devices (requires ATPACK_FILE)
	@if [ -z "$(ATPACK_FILE)" ]; then \
		echo "Please set ATPACK_FILE environment variable"; \
		echo "Example: make cli-devices ATPACK_FILE=../public/atpacks/Atmel.ATmega_DFP.2.2.509_dir_atpack"; \
	else \
		atpack devices list "$(ATPACK_FILE)"; \
	fi

cli-info: ## Show device info (requires ATPACK_FILE and DEVICE)
	@if [ -z "$(ATPACK_FILE)" ] || [ -z "$(DEVICE)" ]; then \
		echo "Please set ATPACK_FILE and DEVICE environment variables"; \
		echo "Example: make cli-info ATPACK_FILE=../public/atpacks/Atmel.ATmega_DFP.2.2.509_dir_atpack DEVICE=ATmega16"; \
	else \
		atpack devices info "$(DEVICE)" "$(ATPACK_FILE)"; \
	fi
