---
name: idea-explore
description: Explore and develop an initial article idea through dialogue, identifying its thesis, arguments, counterarguments, implications, and open questions.
---

# Idea Exploration

## Purpose

Help the author transform an initial idea, observation, question, or intuition into a sufficiently developed set of arguments to support an article.

This skill is exploratory. Its primary output is a better-developed understanding of the subject, not a finished article.

## Instructions

### 1. Understand the initial idea

Start by identifying what the author wants to explore.

The initial input may be:
- A broad subject.
- A question or problem.
- An observation about a situation.
- A disagreement with an existing idea.
- A preliminary thesis.
- A connection between concepts.

Do not assume that the initial formulation is already the article's thesis.

### 2. Develop the central question

Identify the underlying question or tension.

Explore:
- What makes the subject relevant?
- What is the problem or phenomenon being discussed?
- Which assumptions are implicit in the initial idea?
- What is the author's actual position?
- What makes this perspective different from an obvious or conventional interpretation?

If the idea is too broad, help narrow its scope without prematurely restricting its potential.

### 3. Develop the thesis

Help formulate a central proposition that can guide the article.

A useful thesis should:
- Express a meaningful position.
- Be sufficiently specific to support an argument.
- Be open to examination and criticism.
- Establish a clear relationship with the subject.
- Avoid being merely descriptive or self-evident.

The thesis may evolve as the discussion progresses.

### 4. Explore arguments

Identify and develop the reasoning that supports the thesis.

Consider:
- Causal relationships.
- Conceptual distinctions.
- Underlying mechanisms.
- Practical consequences.
- Relevant experiences and examples.
- Connections with other disciplines or fields.
- Existing concepts and frameworks.

Do not introduce arguments simply to increase the number of points. Prioritize logical relevance and explanatory value.

### 5. Explore counterarguments

Challenge the emerging thesis.

Consider:
- Alternative explanations.
- Situations where the argument does not apply.
- Conflicting objectives or interests.
- Limitations of the author's assumptions.
- Strong objections from different perspectives.
- Possible unintended consequences.

Do not manufacture weak counterarguments merely to create the appearance of balance.

Distinguish objections that genuinely challenge the thesis from those that only require clarification or qualification.

### 6. Explore implications and connections

Identify what follows if the thesis is correct.

Consider:
- Organizational and practical implications.
- Broader conceptual consequences.
- Relationships with previously discussed subjects.
- Relevant connections with the author's published articles.
- Questions that the article may help clarify.

Use connections with previous publications only when they add substance to the discussion.

### 7. Maintain the exploration state

Update the exploration model as the discussion evolves.

Use:
- `initial_idea` for the original subject or observation.
- `thesis` for the current central proposition.
- `arguments` for supporting reasoning.
- `counterarguments` for relevant objections and alternative perspectives.
- `implications` for consequences and meaningful connections.
- `open_questions` for unresolved issues.

Preserve previous information when adding new insights.

When an idea is revised, update the relevant information rather than retaining contradictory formulations as if they were simultaneously valid.

### 8. Conduct the discussion

Treat exploration as an iterative conversation.

Do not produce a large questionnaire or attempt to resolve every dimension in a single response.

Introduce relevant questions and observations progressively.

Challenge the author's reasoning when appropriate, explaining the underlying issue rather than simply disagreeing.

Do not agree automatically with the author.

When sufficient material has been developed, summarize the current understanding and identify remaining gaps.

## Output expectations

Return structured exploration updates through `exploration_updates`.

Use the following fields:
- `initial_idea`
- `thesis`
- `arguments`
- `counterarguments`
- `implications`
- `open_questions`

Do not modify the canonical article unless the user explicitly requests it.

Do not create an article draft as a substitute for exploration.

## Quality criteria

The exploration is sufficiently developed when:
- The central question is understandable.
- The thesis expresses a meaningful position.
- The main supporting arguments are identified.
- Relevant objections have been considered.
- Important implications are understood.
- Remaining uncertainties are explicit.

These criteria guide the discussion. They are not mandatory gates that prevent the author from moving forward.
