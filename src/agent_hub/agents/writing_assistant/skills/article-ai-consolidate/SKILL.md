---
name: article-ai-consolidate
description: Produce a compact English consolidation of an article, preserving its thesis and substantive arguments for consumption by AI agents.
---

# Article AI Consolidation

## Purpose

Create a compact English representation of the article for use as contextual material by other AI agents.

The consolidation is intended to preserve the article's conceptual content while reducing its length and removing reader-oriented editorial elements.

It is not a translation intended for publication and must not replace the canonical article.

## Instructions

### 1. Understand the complete article

Read the full source article.

Identify:
- The central thesis.
- The main arguments.
- Important conceptual distinctions.
- Relevant causal relationships.
- Essential qualifications and limitations.
- The conclusions and implications.

Do not rely exclusively on the title, subtitle, or summary.

### 2. Consolidate by topic

Organize the content by its substantive topics.

Each topic should capture a meaningful part of the article's reasoning.

Preserve the relationship between arguments when that relationship is necessary to understand the thesis.

The consolidation should represent the article's conceptual structure rather than reproduce its original section structure.

### 3. Remove editorial elements

Remove:
- Title and subtitle.
- Markdown heading markers.
- Decorative formatting.
- Repeated ideas.
- Redundant explanations.
- Secondary examples.
- Unnecessary narrative context.
- Reader-oriented transitions.
- Editorial language that does not contribute to the argument.

Do not remove qualifications or distinctions that materially affect the meaning.

### 4. Write in English

Produce the consolidation in clear, concise English.

Translate concepts according to their meaning rather than their literal wording.

Use consistent terminology.

Preserve domain-specific terms when translating them would introduce ambiguity.

### 5. Preserve intellectual integrity

Do not:
- Introduce new arguments.
- Add external interpretations.
- Strengthen or weaken the author's claims.
- Turn hypotheses into facts.
- Remove relevant limitations.
- Attribute conclusions to the author that are not present in the article.
- Fabricate references or evidence.

The consolidation must remain faithful to the source even when substantially shorter.

### 6. Optimize for AI consumption

The intended audience is another AI agent.

Prioritize:
- Explicit concepts.
- Clear relationships between ideas.
- Precise terminology.
- Concise explanations.
- Preservation of relevant context.
- Unambiguous statements of the author's position.

Avoid unnecessary prose intended only to engage a human reader.

Do not add instructions to the receiving agent or speculate about how it should use the content.

## Output expectations

Return the consolidation through the `artifacts` parameter as an ArticleArtifact:

- `type`: `ai-consolidation`
- `language`: `en`
- `content`: the complete consolidated article.

Do not modify the canonical article.

Do not include a title, introductory explanation, or commentary in the artifact content.

