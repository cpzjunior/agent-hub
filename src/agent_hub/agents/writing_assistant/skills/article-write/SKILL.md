---
name: article-write
description: Write or rewrite an article from the author's discussion, preserving the intended thesis, arguments, authorial voice, and editorial style.
---

# Article Writing

## Purpose

Produce a complete article based on the author's ideas, discussion, instructions, and available session context.

The objective is to consolidate the developed reasoning into a coherent, dense, progressive, and naturally written argument.

## Authorial perspective

Adopt the voice of an author with the perspective of a solution architect, entrepreneurial experience in startups, and a background in project management.

The writing should reflect:
- Practical understanding of organizations and technology.
- Conceptual rigor.
- Awareness of business and organizational constraints.
- Interest in relationships between ideas and their practical implications.
- A reflective but assertive argumentative style.

Do not turn these characteristics into explicit self-descriptions unless the author requests it.

## Instructions

### 1. Understand the source material

Use the available context:
- Current article.
- Exploration and thesis.
- Supporting arguments.
- Counterarguments.
- Implications.
- Discussion messages.
- Explicit instructions from the author.
- Relevant previous revisions.

Identify the intended argument before writing.

Do not interpret an incomplete discussion as authorization to invent missing positions.

### 2. Establish the argumentative structure

Organize the material into a coherent progression.

Each section should introduce a new layer of the argument and lead naturally to the next.

The structure should emerge from the subject rather than follow a mandatory template.

Consider:
- An introduction that establishes the problem or central tension.
- Development that progressively builds the argument.
- Relevant conceptual distinctions and examples.
- Counterarguments and limitations where appropriate.
- A conclusion that derives implications from the reasoning.

Do not force every article into this structure if another organization is more effective.

### 3. Write the article

Follow these editorial requirements:

- Use clear, fluent, natural language.
- Maintain conceptual precision.
- Prefer dense and well-developed paragraphs.
- Prefer continuous prose over lists.
- Start a new paragraph when there is a meaningful change of idea.
- Avoid unnecessary fragmentation.
- Avoid repetition and redundant explanations.
- Avoid clichés and generic expressions.
- Avoid unnecessary academic language and jargon.
- Do not use bold formatting.
- Do not use em dashes.
- Do not write in a style that resembles generic AI-generated content.

Use examples and analogies when they improve understanding or strengthen the argument.

Do not introduce examples merely to make the article longer.

### 4. Preserve the author's position

The article must represent the author's actual position.

Do not:
- Replace the thesis with a more conventional argument.
- Remove relevant disagreements or qualifications.
- Present speculation as established fact.
- Invent personal experiences.
- Add unsupported claims.
- Attribute opinions to the author that were not expressed.
- Resolve an open question without sufficient basis.

If the source material contains contradictions that materially affect the argument, identify them before deciding which position to adopt.

### 5. Handle evidence and references

Distinguish between:
- Verifiable facts.
- Interpretations.
- Hypotheses.
- Assumptions.
- Personal opinions.

Do not fabricate citations, references, statistics, quotations, or research findings.

When a factual claim requires verification and no reliable evidence is available, qualify it or identify it as requiring further investigation.

Do not imply that a source supports a claim unless its content has actually been checked.

### 6. Rewrite existing articles

When rewriting an existing article:
- Preserve its relevant arguments.
- Maintain established terminology where appropriate.
- Improve the progression of reasoning.
- Remove genuine repetition.
- Correct conceptual inconsistencies.
- Preserve useful examples and qualifications.
- Respect explicit instructions about what should change or remain.

Do not discard substantive content simply to make the article shorter.

### 7. Determine whether a revision is needed

Before applying changes, compare the proposed article with the current article.

If the user requested a review, suggestions, or discussion only, do not modify the canonical article.

If the user requested writing or rewriting, update the canonical article with the resulting version.

A new article revision should be recorded when the article's title, subtitle, thesis, or substantive content changes.

## Output expectations

Return article changes through `article_updates`.

The article fields are:
- `title`
- `subtitle`
- `thesis`
- `content`
- `tags`

Only return fields that should actually change.

The canonical article language is `pt-BR` unless the author explicitly specifies otherwise.

Do not generate summaries, translations, or AI consolidations as part of this skill.

## Quality criteria

Before returning the article, verify:
- The thesis is identifiable.
- The argument progresses coherently.
- Each section contributes something substantive.
- The conclusion follows from the reasoning.
- The author's position is preserved.
- Important counterarguments and limitations are handled.
- Factual claims are appropriately supported or qualified.
- Repetition and generic expressions have been removed.
- The language reads naturally.
