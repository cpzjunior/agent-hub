---
name: services
description: Create service or productized-solution proposals describing the offering, operation, target users and possible applications. Use when the idea proposes a service, platform, tool or business-oriented solution.
---

# Services

## Objective

Describe a service-oriented solution, platform or offering, explaining its purpose, operation, capabilities and potential applications.

## Reference Document

The application supplies this repository example:

`services/institutional-onboarding-and-enterprise-architecture-training-agent/README.pt-BR.md`

Use it as a structural reference. Do not copy its subject matter or wording.

## Required Structure

Follow the reference's section structure:

- `# Title`
- `## Descrição`
- `## Funcionamento`
- `## Aplicações`
- `## Referências`

The reference may contain subsections, tables, lists and detailed usage examples. Include these elements when they help explain the proposed service.

## Writing Rules

- Write in Brazilian Portuguese.
- Explain the problem, target audience and value proposition.
- Describe how the service works and its main capabilities.
- Include a concrete usage example when it clarifies the proposal.
- In `Aplicações`, identify relevant users, organizations, contexts and possible delivery or business models when appropriate.
- Distinguish existing capabilities from future possibilities.
- Include references only when known; do not invent products, companies or sources.
- Preserve the Markdown conventions of the reference document.

## Output

Return:

- `title`: document title.
- `content_pt_br`: complete Markdown document in Brazilian Portuguese.

Do not translate the document. The application invokes the shared `text-translate` skill separately.
