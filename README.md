# Agent Hub

A modular workspace for building, organizing and orchestrating AI agents, with encapsulated skills, tools and shared capabilities.

## Goals

- Organize agents as independent modules.
- Encapsulate agent-specific skills and tools.
- Share common capabilities through the core.
- Support simple and workflow-based agents.
- Expose agents through an MCP server.

## Requirements

- Python 3.12+
- Git

## Setup

Run the following commands from the project root using PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev]"
```

If PowerShell blocks script execution:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

## Agents

The workspace currently includes:

- **Git Agent** — performs Git operations in local repositories.
- **Agent Builder** — assists with creating and improving agents, skills and tools.
- **Bookmark Agent** — creates, extracts, describes and classifies bookmarks.
- **Project Ideas Agent** — generates structured project idea documents.

Each agent has its own instructions, workflows and tools where applicable. LLM interpretation is provided through interchangeable implementations of the core `Interpreter` interface, currently supporting OpenAI and Anthropic.

## MCP Server

The MCP server exposes the registered agents as tools over the standard input/output (`stdio`) transport.

Each agent is exposed through one MCP tool:

| Agent | MCP tool |
|---|---|
| Git Agent | `git_agent` |
| Agent Builder | `agent_builder` |
| Bookmark Agent | `bookmark_agent` |
| Project Ideas Agent | `project_ideas_agent` |

The server is started with:

```powershell
python -m agent_hub.mcp
```

The current entry point configures OpenAI interpreters for all four agents. Set `OPENAI_API_KEY` before starting the server.

Example MCP client configuration:

```json
{
  "mcpServers": {
    "agent-hub": {
      "command": "python",
      "args": ["-m", "agent_hub.mcp"],
      "env": {
        "OPENAI_API_KEY": "your-api-key"
      }
    }
  }
}
```

Adjust `command` to point to the Python executable in the project's virtual environment when needed.

## Validation

Run the automated checks from the project root:

```powershell
pytest -v
ruff check src tests
mypy src tests
```

All checks should pass before committing changes.

## Development workflow

1. Activate the virtual environment.
2. Implement the changes.
3. Run tests, lint and type checking.
4. Commit only after all checks pass.

## Contributing

Contributions are welcome!

If you would like to contribute to this project:

1. Fork the repository.
2. Create a branch for your changes.
3. Make your changes and ensure the project builds successfully.
4. Run the existing tests and add new tests when applicable.
5. Submit a Pull Request describing your changes.

For bug reports, feature requests, or questions, please open an issue.

By contributing, you agree that your contributions will be licensed under the same license as this project.

## License

This project is licensed under the [MIT License](LICENSE).
