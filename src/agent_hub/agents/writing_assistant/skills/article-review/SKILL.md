---
name: article-review
description: Critically evaluate an article's thesis, reasoning, evidence, structure, clarity, originality, and readiness for publication.
---

# Article Review

## Purpose

Evaluate the article critically and determine whether its argument is defensible and whether the text is ready for publication.

The review should prioritize substantive quality over superficial stylistic preferences.

A review is an analytical activity. It does not automatically rewrite or modify the article.

## Instructions

### 1. Evaluate the thesis

Determine:
- Whether the central thesis is clear.
- Whether it is sufficiently specific.
- Whether the article actually develops the thesis it proposes.
- Whether the thesis is defensible.
- Whether its scope is appropriate.

Identify ambiguity, hidden assumptions, and unsupported generalizations.

### 2. Evaluate the argument

Examine the logical progression.

Consider:
- Whether each major argument supports the thesis.
- Whether conclusions follow from the premises.
- Whether important reasoning steps are missing.
- Whether the article confuses correlation, causation, and interpretation.
- Whether concepts are used consistently.
- Whether examples genuinely support the argument.

Identify contradictions and logical gaps.

Explain why they matter.

### 3. Evaluate counterarguments

Determine whether the article considers relevant opposing perspectives.

Identify:
- Strong objections that have been omitted.
- Alternative explanations.
- Important limitations.
- Conditions under which the thesis may not apply.
- Potential unintended consequences.

Distinguish between objections that undermine the thesis and those that require a qualification.

Do not demand artificial neutrality when the article is explicitly argumentative.

### 4. Evaluate factual accuracy and evidence

Identify claims that:
- Require external verification.
- Are presented too confidently.
- Lack adequate support.
- Depend on ambiguous or outdated concepts.
- Could be interpreted as established facts despite being opinions or hypotheses.

Do not claim that a statement is false without sufficient evidence.

When external research is unavailable, identify the verification requirement rather than inventing a conclusion.

### 5. Evaluate structure and progression

Examine:
- Whether the introduction establishes the central problem.
- Whether sections build on one another.
- Whether transitions are natural.
- Whether the argument develops progressively.
- Whether the conclusion adds a meaningful synthesis.
- Whether any section is unnecessary or misplaced.

Do not impose a standard article template.

### 6. Evaluate writing quality

Identify:
- Repetitive ideas or expressions.
- Clichés and generic formulations.
- Unnecessary jargon.
- Overly long or fragmented passages.
- Ambiguous sentences.
- Excessive qualifications.
- Explanations that repeat what the reader already understands.

Distinguish genuine problems from subjective stylistic preferences.

Respect the author's preference for dense, continuous prose and natural language.

### 7. Evaluate originality and editorial value

Consider:
- Whether the article offers a meaningful perspective.
- Whether it goes beyond an obvious interpretation.
- Whether its conceptual distinctions add value.
- Whether connections with other subjects are relevant.
- Whether it contributes something distinct to the author's body of work.

Do not equate originality with novelty of subject. A familiar subject can produce an original argument.

### 8. Assess publication readiness

Provide a clear assessment.

Use one of the following statuses:
- `ready`: defensible and suitable for publication.
- `ready_with_minor_changes`: publishable after limited adjustments.
- `needs_revision`: substantive issues should be addressed first.
- `not_ready`: fundamental problems prevent publication in its current form.

Explain the most important reasons behind the assessment.

Prioritize findings by significance.

## Output expectations

Return the structured review through the `review` parameter.

The review must contain:
- `status`
- `strengths`
- `substantive_issues`
- `missing_arguments`
- `editorial_issues`
- `recommendations`

Use one of the supported status values:
- `ready`
- `ready_with_minor_changes`
- `needs_revision`
- `not_ready`

The latest review is stored in `WritingSession.last_review`.

The review may also be explained in the assistant response.

Do not modify `article_updates` unless the user explicitly requests a revision.

Do not create a new article revision merely because a review was performed.

