---
name: skill-manage
description: Create and improve Agent Skills following the Agent Skills specification and Agent Hub conventions.
---

# Skill Management

Manage the creation and improvement of skills used by agents in the Agent Hub project.

Determine whether the user wants to create a new skill or improve an existing one.

Follow the Agent Skills specification:

https://agentskills.io/

## Responsibilities

### Create

When creating a skill:

- Choose a concise, descriptive, lowercase name.
- Use hyphens to separate words.
- Create a `SKILL.md` file.
- Include valid YAML frontmatter.
- Define the required `name` and `description` metadata.
- Describe the skill's purpose and responsibilities.
- Provide clear instructions for the agent.
- Define constraints and expected behavior.
- Include examples when they materially improve understanding.

The frontmatter must start at the first character of the file.

Example:

---
name: example-skill
description: A concise description of the skill.
---

### Improve

When improving an existing skill:

- Preserve its original purpose.
- Identify ambiguous, duplicated, or conflicting instructions.
- Improve clarity and precision.
- Remove unnecessary instructions.
- Keep the skill focused on a specific capability.
- Preserve valid metadata.
- Avoid unnecessary complexity.

## Project Context

Use only project information provided by the user.

Never claim to have inspected existing skills unless their contents were provided.

When modifying a skill, request its current contents if necessary.

Follow the project's existing skill directory conventions.

## Testing and Validation

Automated tests are generally not necessary for skill creation or improvement.

Instead, validate:

- YAML frontmatter structure.
- Required metadata.
- Skill naming conventions.
- Description clarity.
- Instruction consistency.
- Absence of contradictory rules.
- Whether the skill has a clear and limited responsibility.

Generate automated tests only when the skill introduces behavior that can meaningfully be tested by the project's existing test infrastructure.

Do not create tests merely to increase coverage.

## Output Requirements

Return structured artifacts using the following format:

- `artifacts`: list of generated files.
- `path`: relative project path.
- `content`: complete file content.
- `action`: `create` or `update`.
- `tests_relevant`: whether tests are relevant.
- `tests_rationale`: explanation of the testing decision.
- `validation_notes`: relevant validation instructions or limitations.

Always provide the complete `SKILL.md` content.

Never claim that files were created or modified in the repository unless the application actually performed those operations.

## Restrictions

- Do not create unnecessary supporting files.
- Do not duplicate existing skills.
- Do not introduce instructions unrelated to the skill's purpose.
- Do not invent project conventions.
