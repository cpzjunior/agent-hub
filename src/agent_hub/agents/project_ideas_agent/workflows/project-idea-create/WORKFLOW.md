---
name: project-idea-create
description: Create a project idea document by selecting its category, following a repository example, writing in Brazilian Portuguese and translating the complete document into English.
---

# Project Idea Creation Workflow

Coordinate the category-specific skill and the shared translation skill to produce a bilingual project idea proposal.

## Input

Required:

- `instruction`: user's description of the idea.

Optional:

- `template_variant`: `beginner` or `advanced`, required when the selected category is `game-concepts`.

## Execution

### Step 1: Select Category

Use the user's instruction to select exactly one category skill:

- `game-concepts`: a complete game concept.
- `game-mechanics`: a gameplay mechanic or reusable game system.
- `legislative`: a legislative proposal, draft law concept or initiative to create, amend or repeal legal provisions.
- `non-profit`: a social, humanitarian, environmental or public-interest initiative.
- `services`: a service, platform or business-oriented solution.

Do not generate content during category selection.

If the request does not fit any category, report that it is unsupported.

### Step 2: Resolve Game Concept Variant

When the selected category is `game-concepts`, require either `beginner` or `advanced`.

If the variant is missing or ambiguous, stop and ask the user. Do not guess.

Other categories do not use a variant.

### Step 3: Load Reference Document

The application reads the corresponding existing `README.pt-BR.md` from the local project-ideas repository and supplies its path and content to the selected skill.

Use this document as a structural and depth reference, not as content to copy.

For the `legislative` category, use an existing document under the `legislative/` directory as the reference.

### Step 4: Generate Portuguese Document

Execute the selected category skill with:

- User instruction.
- Category.
- Variant, when applicable.
- Reference document path and content.

Expected output:

- `title`.
- `content_pt_br`: complete Markdown document in Brazilian Portuguese.

Category-specific requirements:

- **legislative:** Assume Brazil as the default jurisdiction unless the user specifies otherwise. Evaluate the legislative competence and constitutional context, relevant legislation, expected positive and negative impacts, implementation feasibility, enforcement challenges and open questions. Distinguish verified legal facts from assumptions and policy recommendations. Use reliable, verifiable references whenever legal or factual claims require support. Never invent laws, bills, court decisions, statistics, sources or URLs. If current legal research is unavailable, explicitly identify the points requiring verification.

If essential information is missing, stop and request it rather than inventing details.

### Step 5: Translate Complete Document

Execute the shared `text-translate` skill with the entire `content_pt_br` document.

Source language: Brazilian Portuguese.
Target language: English.

Preserve the Markdown structure, section order, lists, tables, links, code and meaning. Do not summarize or adapt the content.

### Step 6: Validate and Return

Ensure both documents are present and non-empty.

Return:

- Category.
- Variant, if applicable.
- Title.
- Complete Portuguese Markdown document.
- Complete English Markdown document.
- Reference document path.

## Repository Restrictions

This workflow is read-only.

Do not create, update, delete or commit files in the project-ideas repository. Present the generated documents for user review.