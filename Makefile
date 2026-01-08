.PHONY: install uninstall build run debug clean lint lint-strict

PYTHON := $(shell command -v python3.11 2>/dev/null)
UV := $(shell command -v uv 2>/dev/null)
ARGS := $(wordlist 2, 999, $(MAKECMDGOALS))
OUTPUT_FILE := $(shell grep -i output_file config.txt | cut -d= -f2 | xargs)
WHEEL := dist/*.whl

install:
	@echo "Checking for dependencies..."

	@echo " - Checking for uv"
	@if [ -z "$(UV)" ]; then \
		echo "\tuv not found, installing..."; \
		curl -LsSf https://astral.sh/uv/install.sh | sh; \
		export PATH=$$PATH:$$HOME/.local/bin/uv; \
		UV=$$(command -v uv 2>/dev/null); \
		echo " uv installed at $$UV"; \
	else \
		echo "\tuv found at $(UV)"; \
	fi

	@echo " - Checking for python dependencies"
	@if [ ! -f mazegen*.whl ]; then \
		echo "Missing mazegen wheel file..."; \
		echo "Run make build"; \
		exit 1; \
	fi

	@echo " - Checking for python"
	@if [ -z "$(PYTHON)" ]; then \
		uv python install 3.11; \
	else \
		echo "\tpython3 found at $(PYTHON)"; \
	fi

	@echo "Configuring venv"
	@if [ ! -d "./.venv" ]; then \
		uv venv; \
	fi; \
	. ./.venv/bin/activate; \
	uv pip install mazegen*.whl; \
	uv pip install flake8; \
	uv pip install mypy

uninstall:
	uv cache clean
	rm -rf $(shell uv python dir)
	rm -rf $(shell uv tool dir)
	rm -rf ~/.local/bin/uv ~/.local/bin/uvx

build:
	@if [ ! -f pyproject.toml ]; then \
		touch pyproject.toml; \
		echo "[project]" >> pyproject.toml; \
		echo 'name = "mazegen"' >> pyproject.toml; \
		echo 'version = "1.0.0"' >> pyproject.toml; \
		echo 'description = "Maze generation library"' >> pyproject.toml; \
		echo 'readme = "mazegen/README.md"' >> pyproject.toml; \
		echo 'requires-python = ">=3.11"' >> pyproject.toml; \
		echo 'dependencies = []' >> pyproject.toml; \
		echo >> pyproject.toml; \
		echo "[tool.setuptools]" >> pyproject.toml; \
		echo 'packages = ["mazegen"]' >> pyproject.toml; \
		echo "[tool.setuptools.package-data]" >> pyproject.toml; \
		echo 'mazegen = ["README.md"]' >> pyproject.toml; \
	fi
	uv build
	mv $(WHEEL) .
	rm -rf dist
	$(MAKE) clean

config:
	@tmp=$$(mktemp); \
	base=$$(mktemp); \
	if [ -f config.txt ]; then \
		cp config.txt $$tmp; \
		cp config.txt $$base; \
	else \
		echo "# This file is read by a_maze_ing.py" > $$tmp; \
		echo "WIDTH=25"        >> $$tmp; \
		echo "HEIGHT=25"       >> $$tmp; \
		echo "ENTRY=0,0"       >> $$tmp; \
		echo "EXIT=19,14"      >> $$tmp; \
		echo "OUTPUT_FILE=out.txt" >> $$tmp; \
		echo "PERFECT=True"    >> $$tmp; \
		echo >> $$tmp; \
		echo "# The flags below are optional" >> $$tmp; \
		echo "# SEED=42"       >> $$tmp; \
		echo "# ALGORITHM=dfs" >> $$tmp; \
	fi; \
	$${EDITOR:-nano} $$tmp; \
	if cmp -s $$tmp $$base; then \
		echo "No changes detected. Configuration not updated."; \
	else \
		cp $$tmp config.txt; \
		echo "Configuration updated and saved to config.txt"; \
	fi; \
	rm $$tmp

run:
	@if [ ! -d .venv ]; then \
		echo "Run make install first..."; \
		exit 1; \
	fi
	@echo "Running with args: $(ARGS)"
	@sh -c '\
		mv mazegen mazegen.bak; \
		trap "mv mazegen.bak mazegen" EXIT; \
		. ./.venv/bin/activate; \
		echo "Python used: $$(which python)"; \
		uv run python a_maze_ing.py $(ARGS); \
	'

debug:
	uv run python -m pdb a_maze_ing.py $(ARGS)

clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type d -name .mypy_cache -exec rm -rf {} +
	find . -type d -name *.egg-info -exec rm -rf {} +
	find . -name .pytest_cache -exec rm -rf {} +
	find . -name "*.pyc" -delete
	find . -name "*.pyo" -delete
	rm -rf dist
	@if [ -f config.txt ]; then \
		echo rm -f "$(OUTPUT_FILE)"; \
		rm -f "$(OUTPUT_FILE)"; \
	fi
	rm -f pyproject.toml

fclean: clean
	rm -rf .venv
	rm -f mazegen*.whl

lint:
	@if [ ! -d .venv ]; then \
		echo "Run 'make build install' first..."; \
		exit 1; \
	fi
	uv run flake8 **/*.py
	uv run mypy . \
		--warn-return-any \
		--warn-unused-ignores \
		--ignore-missing-imports \
		--disallow-untyped-defs \
		--check-untyped-defs \
		--exclude '(^\.venv/|^test/|^subject/)'

lint-strict:
	@if [ ! -d .venv ]; then \
		echo "Run 'make build install' first..."; \
		exit 1; \
	fi
	uv run flake8 **/*.py
	uv run mypy . \
		--strict \
		--exclude '(^\.venv/|^test/|^subject/)'


help:
	@echo "Available targets:"
	@echo "  install        Install dependencies and set up the virtual environment"
	@echo "  uninstall      Removes all Python versions and dependencies newly installed"
	@echo "  build          Compiles the wheel file"
	@echo "  config         Set a config.txt file for the maze generation"
	@echo "  run            Run the application"
	@echo "                 $$ make run ARGS=config.txt"
	@echo "  lint           Run flake8 and mypy"
	@echo "  lint-strict    Run strict mypy checks"
	@echo "  clean          Remove caches and temporary files"
	@echo "  fclean         Removes wheel file"
	@echo "  debug          Run the debugger"
