---
name: article-summary
description: Create a concise five-sentence, first-person summary that presents the article's thesis, main argument, and conclusion in the author's voice.
---

# Article Summary

## Purpose

Produce a concise editorial summary of the canonical article.

The summary is intended to appear after the article subtitle and before the article body.

It should communicate the article's central argument directly, allowing the reader to understand its main proposition before reading the full text.

## Instructions

### 1. Identify the essential argument

Read the complete article and identify:
- Its central thesis.
- The main reasoning supporting the thesis.
- The most important conceptual distinction or development.
- The conclusion and its implications.

Do not summarize the article section by section.

### 2. Consolidate the argument

Select only the information necessary to communicate the article's essential reasoning.

Remove:
- Secondary examples.
- Excessive context.
- Repeated explanations.
- Minor qualifications.
- Details that do not materially contribute to the thesis.
- Arguments that are not central to the article.

Preserve important distinctions and qualifications when removing them would distort the author's position.

### 3. Write the summary

The summary must:
- Contain exactly five sentences.
- Be a single paragraph.
- Use first person.
- Present the author's thesis and reasoning directly.
- Preserve the author's opinion and intended meaning.
- Use natural language consistent with the article.
- Avoid introducing new claims or interpretations.

The summary should sound like the author presenting the article's argument, not an external observer describing it.

### 4. Preserve the editorial style

Avoid:
- Generic introductory expressions.
- Phrases such as "this article discusses" or "in this text".
- Excessive contextualization.
- Repetition of the same idea using different words.
- Marketing language.
- Unnecessary qualifications.
- Lists and headings.

Do not use bold formatting or em dashes.

## Output expectations

Return the summary through the `artifacts` parameter as an ArticleArtifact:

- `type`: `summary`
- `language`: the canonical article language.
- `content`: the complete five-sentence paragraph.

Do not modify the canonical article.

Do not include a title, heading, explanation, or commentary in the artifact content.
