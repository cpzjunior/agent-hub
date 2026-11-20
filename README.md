

🇺🇸 [English](README.md) | 🇧🇷 [Português](README.pt-BR.md)

# Agent Hub

A modular workspace for creating, organizing, and orchestrating AI agents, with encapsulated shared skills, tools, and resources.

## Objectives

- Organize agents as independent modules.
- Encapsulate each agent's specific skills and tools.
- Share common resources through the core.
- Support simple agents and workflow-based agents.
- Make agents available through an MCP server.

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

- Git Agent — performs Git operations on local repositories.
- Agent Builder — assists in creating and improving agents, skills, and tools.
- Archmage Scribe — develops fantasy world concepts, maintains consistency with a local canon repository, and writes texts set in those worlds.
- Bookmark Agent — creates, extracts, describes, and classifies bookmarks.
- Decision Architect — supports decision analysis through an iterative process covering context, objectives, uncertainties, consequences, and evolution.
- Project Ideas Agent — generates structured project idea documents.
- Writing Assistant — explores ideas, writes, reviews, summarizes, and translates articles while preserving the author's editorial voice.

Each agent has its own instructions, workflows, and tools, where applicable. LLM interpretation is provided through interchangeable implementations of the main `Interpreter` interface, currently supporting OpenAI and Anthropic.

## MCP Server

The MCP server exposes registered agents as tools through the standard input/output (`stdio`) transport.

Each agent is exposed as an MCP tool:

| Agent | MCP Tool |
|---|---|
| Git Agent | `git_agent` |
| Agent Builder | `agent_builder` |
| Archmage Scribe | `archmage_scribe` |
| Bookmark Agent | `bookmark_agent` |
| Decision Architect | `decision_architect` |
| Project Ideas Agent | `project_ideas_agent` |
| Writing Assistant | `writing_assistant` |

The server is started with:

```powershell
python -m agent_hub.mcp
```

The current entry point configures OpenAI interpreters for all agents. Set `OPENAI_API_KEY` before starting the server.

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

Adjust `command` to point to the Python executable in the project's virtual environment, if necessary.

### Provider selection per agent

It is also possible to use Anthropic or combine different providers across agents. The selection is made individually in the `interpreters` dictionary, defined in the [`src/agent_hub/mcp/__main__.py`](https://github.com/cpzjunior/agent-hub/blob/main/src/agent_hub/mcp/__main__.py) file.

To use Anthropic for an agent, import `AnthropicInterpreter` and replace the corresponding implementation:

```python
from agent_hub.integrations.langchain.anthropic import AnthropicInterpreter
from agent_hub.integrations.langchain.openai import OpenAIInterpreter

interpreters = {
    "git-agent": OpenAIInterpreter(),
    "agent-builder": AnthropicInterpreter(),
    "archmage-scribe": OpenAIInterpreter(),
    # Remaining agents...
}
```

Set `ANTHROPIC_API_KEY` in the MCP server environment for agents that use Anthropic. The default model is `claude-sonnet-4-5` and can be changed using the `ANTHROPIC_MODEL` variable.

This allows each agent to use OpenAI or Anthropic independently of the others. If both providers are used, configure the respective API keys in the server environment.

## Validation

Run the automated checks from the project root:

```powershell
pytest -v
ruff check src tests
mypy src tests
```

All checks must pass before committing changes.

## Development Workflow

1. Activate the virtual environment.
2. Implement the changes.
3. Run the tests, lint checks, and type checks.
4. Commit only after all checks pass.

## Contributing

Contributions are welcome!

If you would like to contribute to this project:

1. Fork the repository.
2. Create a branch for your changes.
3. Make your changes and ensure that the project builds successfully.
4. Run the existing tests and add new tests where applicable.
5. Submit a Pull Request describing your changes.

To report bugs, request features, or ask questions, open an issue.

By contributing, you agree that your contributions will be licensed under the same license as this project.

## License

This project is licensed under the [MIT License](LICENSE).

