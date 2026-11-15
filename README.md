# Agent Hub

A modular workspace for building, organizing and orchestrating AI agents, with encapsulated skills, tools and shared capabilities.

## Project goals

- Organize agents as independent modules.
- Encapsulate agent-specific skills and tools.
- Share common capabilities when needed.
- Support simple agents and workflow-based agents.
- Evolve incrementally without unnecessary complexity.

## Requirements

- Python 3.12+
- Git

## Environment setup

Create a virtual environment:

```powershell
python -m venv .venv
```

Activate the virtual environment:

```powershell
.\.venv\Scripts\Activate.ps1
```

If PowerShell blocks script execution, run:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

## Installation

Install the project and development dependencies:

```powershell
python -m pip install -e ".[dev]"
```

## Validation

Run the following commands from the project root directory.

### Tests

Execute the automated test suite:

```powershell
pytest -v
```

### Lint

Check code quality and formatting rules:

```powershell
ruff check src tests
```

### Type checking

Run static type checking:

```powershell
mypy src tests
```

All three checks should pass before committing changes.

## Development workflow

1. Activate the virtual environment.
2. Implement the changes.
3. Run tests, lint and type checking.
4. Commit only after all checks pass.