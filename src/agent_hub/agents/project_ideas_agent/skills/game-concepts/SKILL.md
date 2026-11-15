---
name: game-concepts
description: Create game concept documents using the beginner or advanced format in the project-ideas repository. Use when the user proposes a game, game world, game genre or complete game experience.
---

# Game Concepts

## Objective

Create a complete game concept document in Brazilian Portuguese, following the structure and depth of the selected repository example.

## Required Variant

The user or application must specify one of these variants:

- `beginner`: use a concise concept format suitable for an initial game idea.
- `advanced`: use a more developed concept format, with richer explanations and more detailed mechanics.

Never infer the variant when it has not been provided. Request clarification.

## Reference Documents

The application supplies one existing document from the repository:

- Beginner: `game-concepts/beginner/air-hockey-pro-the-path-to-glory/README.pt-BR.md`
- Advanced: `game-concepts/advanced/exoskeleton-sports-beyond-human-limits/README.pt-BR.md`

Use the supplied document as a structural and depth reference. Do not copy its idea, characters, setting or wording.

## Beginner Format

Follow the reference's section structure:

- `# Title`
- `## Conceito`
- `## Objetivo`
- `## Mecânicas principais`
- `## Referências`

Describe the central premise clearly, state the player's main objective, and list the core mechanics. Keep the proposal focused and avoid expanding it into a full design specification.

## Advanced Format

Follow the reference's section structure:

- `# Title`
- `## Conceito`
- `## Objetivo`
- `## Mecânicas principais`
- `## Referências`

Provide a more developed concept, explaining the experience, gameplay pillars, progression and relevant systems. Detail the mechanics sufficiently to communicate how the game works, without turning the document into a technical implementation plan.

## Writing Rules

- Write in Brazilian Portuguese.
- Keep the proposal coherent and internally consistent.
- Distinguish the game's concept from its mechanics and objective.
- Include references only when relevant; do not invent existing products or works.
- Do not add unsupported claims or pretend that design decisions have already been validated.
- Preserve the Markdown conventions of the reference document.

## Output

Return:

- `title`: document title.
- `content_pt_br`: complete Markdown document in Brazilian Portuguese.

Do not translate the document. The application invokes the shared `text-translate` skill separately.
