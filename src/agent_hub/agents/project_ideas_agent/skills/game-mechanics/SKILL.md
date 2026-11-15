---
name: game-mechanics
description: Create game mechanic proposals describing a reusable gameplay system, its behavior, applications and references. Use when the request focuses on a mechanic rather than a complete game concept.
---

# Game Mechanics

## Objective

Describe a game mechanic as a system that can be understood and potentially reused in different games.

## Reference Document

The application supplies this repository example:

`game-mechanics/dynamic-rival/README.pt-BR.md`

Use it as a structural reference. Do not copy its subject matter or wording.

## Required Structure

Follow the reference's section structure:

- `# Title`
- `## Descrição`
- `## Funcionamento`
- `## Aplicações`
- `## Referências`

## Writing Rules

- Write in Brazilian Portuguese.
- Explain what the mechanic is and what player or world experience it enables.
- In `Funcionamento`, describe the rules, triggers, state changes, feedback and relevant interactions.
- In `Aplicações`, identify suitable game genres or contexts.
- Include relevant references only when known; do not fabricate games, systems or sources.
- Focus on the mechanic itself, not on a complete game pitch.
- Preserve the Markdown conventions of the reference document.

## Output

Return:

- `title`: document title.
- `content_pt_br`: complete Markdown document in Brazilian Portuguese.

Do not translate the document. The application invokes the shared `text-translate` skill separately.
