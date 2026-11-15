---
name: non-profit
description: Create proposals for non-profit initiatives, social projects and public-interest solutions. Use when the idea prioritizes social, environmental, humanitarian or community impact.
---

# Non-Profit Projects

## Objective

Describe a non-profit initiative or public-interest project, explaining the problem it addresses, how the initiative works and who can benefit from it.

## Reference Document

The application supplies this repository example:

`non-profit/integration-and-adaptation-platform-for-immigrants-and-refugees/README.pt-BR.md`

Use it as a structural reference. Do not copy its subject matter or wording.

## Required Structure

Follow the reference's section structure:

- `# Title`
- `## Descrição`
- `## Funcionamento`
- `## Aplicações`
- `## Referências`

The reference may contain subsections, lists and additional paragraphs within these sections. Use that level of detail when appropriate to the idea.

## Writing Rules

- Write in Brazilian Portuguese.
- Explain the social or public-interest problem and the intended beneficiaries.
- Describe the initiative's operating model, activities, services or capabilities.
- Explain potential applications and relevant stakeholders.
- Do not assume a commercial business model. If funding, partnerships or sustainability are relevant, describe them as possibilities rather than established facts.
- Avoid unsupported impact metrics or claims.
- Include references only when known; do not invent organizations, programs or sources.
- Preserve the Markdown conventions of the reference document.

## Output

Return:

- `title`: document title.
- `content_pt_br`: complete Markdown document in Brazilian Portuguese.

Do not translate the document. The application invokes the shared `text-translate` skill separately.
