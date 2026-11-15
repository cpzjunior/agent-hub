---
name: agent-manage
description: Create and improve AI agents within the Agent Hub project, following its architecture and conventions.
---

# Agent Management

Manage the creation and improvement of AI agents within the Agent Hub project.

Determine whether the user wants to create a new agent or improve an existing one.

## Responsibilities

### Create

When creating an agent:

- Follow the existing Agent Hub architecture.
- Use the `core.Agent` abstraction.
- Define appropriate input and output contracts using Pydantic.
- Use the `core.Interpreter` abstraction when natural language interpretation is required.
- Keep agent-specific skills and tools inside the agent module.
- Avoid introducing unnecessary dependencies.
- Follow the project's existing naming and directory conventions.

### Improve

When improving an existing agent:

- Preserve its existing responsibilities and public contracts unless a change is explicitly required.
- Identify the actual problem before proposing changes.
- Reuse existing abstractions and implementations.
- Avoid unnecessary refactoring.
- Consider backward compatibility.
- Update documentation when relevant.

## Project Context

Use only project information provided by the user.

Never claim to have inspected files, directories, or implementations that were not provided.

When important context is missing:

- Request the relevant files or project structure.
- Do not invent existing classes, methods, APIs, or conventions.
- Prefer solutions consistent with the architecture already established.

## Testing Guidelines

Tests should be generated or updated only when relevant.

Consider tests when the agent contains:

- Execution logic.
- Interpretation or orchestration behavior.
- Input validation.
- Conditional behavior.
- Interactions with other components.

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
- Do not create unnecessary architectural layers.
- Do not generate arbitrary shell commands.
- Do not invent project conventions.
- Do not modify unrelated components.
