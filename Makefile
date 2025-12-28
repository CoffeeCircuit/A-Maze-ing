.PHONY: install uninstall run debug clean lint lint-strict

PYTHON := $(shell command -v python3 2>/dev/null)
UV := $(shell command -v uv 2>/dev/null)
ARGS := $(wordlist 2, 999, $(MAKECMDGOALS))

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

	@echo " - Checking for python"
	@if [ -z "$(PYTHON)" ]; then \
		uv python install 3.11; \
	else \
		echo "\tpython3 found at $(PYTHON)"; \
		uv sync --python 3.11; \
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

run:
	@echo "Running with args: $(ARGS)"
	@if [ ! -d "./.venv" ]; then \
		uv venv; \
	fi; \
	. ./.venv/bin/activate; \
	echo "Python used: $$(which python)"; \
	uv run python a_maze_ing.py $(ARGS)

%:
	@:

debug:
	uv run python -m pdb a_maze_ing.py $(ARGS)

clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type d -name .mypy_cache -exec rm -rf {} +
	find . -name .pytest_cache -exec rm -rf {} +
	find . -name "*.pyc" -delete
	find . -name "*.pyo" -delete
	rm -f output_maze.txt
	rm -rf .venv

lint:
	uv run flake8 *.py
	uv run mypy . \
		--warn-return-any \
		--warn-unused-ignores \
		--ignore-missing-imports \
		--disallow-untyped-defs \
		--check-untyped-defs \
		--exclude '(^\.venv/|^test/|^subject/)'

lint-strict:
	uv run flake8 *.py
	uv run mypy . \
		--strict \
		--exclude '(^\.venv/|^test/|^subject/)'
