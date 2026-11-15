---
name: tool-manage
description: Create and improve executable tools for agents within the Agent Hub project.
---

# Tool Management

Manage the creation and improvement of executable tools used by agents in the Agent Hub project.

Determine whether the user wants to create a new tool or improve an existing one.

## Responsibilities

### Create

When creating a tool:

- Identify the agent responsible for the tool.
- Keep agent-specific tools inside their owning agent module.
- Define clear input and output contracts using Pydantic when appropriate.
- Separate models from implementation when this matches project conventions.
- Implement a focused and well-defined responsibility.
- Handle expected errors explicitly.
- Consider timeouts and resource management for external operations.
- Document behavior, inputs, outputs, and limitations.
- Follow the existing project conventions.

A tool should perform an executable operation.

Do not confuse tools with skills:

- Skills describe procedures and instructions.
- Tools implement executable capabilities.
- Agents coordinate skills and tools.

### Improve

When improving an existing tool:

- Preserve its public contract unless a change is explicitly required.
- Identify the actual problem before proposing changes.
- Preserve existing behavior where possible.
- Improve error handling when necessary.
- Consider security implications.
- Avoid unnecessary abstractions.
- Update documentation when relevant.

## Project Context

Use only project information provided by the user.

Never claim to have inspected existing implementations unless their contents were provided.

When important context is missing:

- Request the relevant source files.
- Request existing models and tests when necessary.
- Do not invent existing APIs or conventions.
- Prefer consistency with the owning agent.

## Security Guidelines

- Never allow an LLM to execute arbitrary shell commands.
- Validate external inputs.
- Restrict filesystem access to explicitly authorized locations.
- Avoid exposing credentials or secrets.
- Use safe execution mechanisms.
- Require explicit confirmation for destructive or consequential operations when appropriate.

## Testing Guidelines

Tests should be generated or updated when relevant.

Consider tests when the tool contains:

- Business rules.
- Input validation.
- Conditional execution.
- Filesystem operations.
- External integrations.
- Side effects.
- Error handling.

Do not create tests merely to increase coverage.

Do not duplicate existing tests.

When changing existing behavior, evaluate whether current tests need updates.

If tests are not relevant, explain why.

If tests are relevant, provide complete test files or the necessary changes.

## Output Requirements

Return structured artifacts using the following format:

- `artifacts`: list of generated files.
- `path`: relative project path.
- `content`: complete file content.
- `action`: `create` or `update`.
- `tests_relevant`: whether tests are relevant.
- `tests_rationale`: explanation of the testing decision.
- `validation_notes`: relevant validation instructions or limitations.

Always provide complete file contents.

Never claim that files were created or modified in the repository unless the application actually performed those operations.

## Restrictions

- Do not introduce generic Tool abstractions into `core`.
- Do not generate arbitrary shell commands.
- Do not create unnecessary architectural layers.
- Do not modify unrelated components.
