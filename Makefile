PYTHON = python3
UV = uv
SRC = fly_in.py
MAP ?=

run:
	@if [ -f "$(MAP)" ]; then \
		uv run $(SRC) $(MAP); \
	else \
		echo "⚠️  Fichier $(MAP) introuvable"; \
		uv run $(SRC); \
	fi

install:
	uv sync

debug:
	@uv run python -m pdb $(SRC)

clean:
	@find . -type d -name "__pycache__" -exec rm -rf {} +
	@find . -name "*.pyc" -delete
	@rm -rf $(VENV)
	@rm -rf 
	@echo "all is clear"

lint:
	@uv run $(PYTHON) -m flake8 . --extend-exclude .venv
	@uv run $(PYTHON) -m mypy . --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs


lint-strict:
	@uv run $(PYTHON) -m flake8 . --extend-exclude .venv
	@uv run $(PYTHON) -m mypy . --strict

.PHONY: run install debug clean lint lint-strict