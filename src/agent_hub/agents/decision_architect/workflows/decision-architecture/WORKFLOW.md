---
name: decision-architecture
description: >
  Coordinates the iterative analysis and evolution of a decision using
  the six foundations of Decision Architecture. Selects and combines
  specialized skills according to the current needs of the decision.
---

# Decision Architecture Workflow

## Purpose

Guide the iterative construction, analysis, and evolution of a
Decision Model.

The workflow coordinates the six decision dimensions:

1. Domain.
2. Initial context.
3. Objectives.
4. Risks and uncertainties.
5. Consequences.
6. Evolution.

These dimensions are interdependent. They do not represent mandatory
sequential stages.

The workflow must adapt to the current understanding of the decision
and the user's needs.

## Core principles

### 1. The Decision Model is the central state

The Decision Model represents the current understanding of a single
decision.

It must remain independent of:

- Conversation history.
- Generated documents.
- Presentation formats.
- External persistence mechanisms.

The workflow operates on the current Decision Model and updates it
when relevant information becomes available.

### 2. The process is iterative

Every interaction may change the understanding of the decision.

New information may require:

- Updating an existing dimension.
- Revisiting previous conclusions.
- Reconsidering alternatives.
- Reassessing risks.
- Revising objectives.
- Reinterpreting the original problem.

Never assume that previously established conclusions are permanently
valid.

### 3. Skills are selected according to need

Use only the skills relevant to the current interaction.

Available skills:

| Skill | Responsibility |
|---|---|
| decision-domain | Understand the decision domain and its boundaries |
| initial-context | Investigate the current situation |
| decision-objectives | Define and evaluate desired outcomes |
| risks-and-uncertainties | Identify and assess uncertainty and risks |
| decision-consequences | Analyze potential consequences and trade-offs |
| decision-evolution | Reassess decisions and incorporate learning |

Multiple skills may be used in the same interaction.

A skill may be executed repeatedly when new information justifies it.

Do not execute all skills simply because they exist.

## Interaction cycle

### 1. Understand the user's input

Interpret the user's message in the context of the current session.

Determine whether the user is:

- Introducing a new decision.
- Providing additional information.
- Answering a previous question.
- Challenging an existing assumption.
- Changing an objective.
- Introducing a new alternative.
- Requesting an evaluation.
- Requesting a review of the decision.
- Requesting a representation or document.

Do not treat every message as a new independent decision.

### 2. Assess the current Decision Model

Review the available model before performing new analysis.

Identify:

- What is already understood.
- What remains unknown.
- Which conclusions depend on assumptions.
- Which dimensions are incomplete.
- Which conclusions may have become outdated.
- Which relationships between dimensions require reassessment.

Avoid asking the user to repeat information already available.

### 3. Identify the next useful activity

Determine what would most improve the current decision analysis.

Examples:

- An unclear problem may require initial-context.
- An overly broad problem may require decision-domain.
- A proposed solution without clear outcomes may require decision-objectives.
- A critical unverified assumption may require risks-and-uncertainties.
- Competing alternatives may require decision-consequences.
- New evidence affecting a previous decision may require decision-evolution.

Select one or more relevant skills.

Do not impose a fixed sequence.

### 4. Conduct the analysis

Execute the selected skills using the current Decision Model
and relevant conversation context.

The analysis must:

- Preserve established information.
- Distinguish facts, hypotheses, assumptions, and unknowns.
- Identify contradictions.
- Make relevant inferences explicit.
- Avoid fabricating missing information.
- Consider dependencies between decision dimensions.

When information is insufficient, ask focused questions.

Prefer one meaningful question at a time when possible.

Do not turn the interaction into a rigid questionnaire.

### 5. Update the Decision Model

Incorporate relevant information into the model.

Update only the dimensions affected by the interaction.

Possible updates include:

- Domain boundaries and relevant elements.
- Current context and stakeholders.
- Objectives and priorities.
- Evidence and assumptions.
- Risks and uncertainties.
- Alternatives.
- Expected consequences.
- Evolution notes and status.

Preserve the distinction between information provided by the user,
external evidence, and agent inferences.

Do not overwrite relevant previous understanding without
preserving its historical significance.

### 6. Record relevant events

Register meaningful changes in Decision History.

Use Decision Events to record:

- Decision creation.
- Relevant information added.
- Changes to existing dimensions.
- New alternatives.
- Alternative selection or rejection.
- Status changes.
- Significant reviews.

Each event should contain:

- Event type.
- Affected element.
- Description.
- Rationale, when available.
- Information source.
- Timestamp.

Do not create unnecessary events for trivial wording changes
or internal analysis that does not change the model.

### 7. Reassess dependencies

After updating the model, consider whether the changes affect
other dimensions.

Examples:

- A domain change may require context reassessment.
- New context may invalidate assumptions.
- Invalid assumptions may affect objectives.
- Revised objectives may change alternative evaluation.
- New alternatives may introduce different risks.
- New consequences may justify revisiting objectives.
- Actual outcomes may require revising the original decision.

Revisit only the dimensions materially affected.

### 8. Communicate the result

Respond with the most useful information for the current interaction.

Depending on the situation:

- Explain the current understanding.
- Present relevant findings.
- Identify unresolved questions.
- Explain contradictions or trade-offs.
- Compare alternatives.
- Recommend further investigation.
- Present an updated decision status.

Do not expose the entire Decision Model in every response.

Provide a complete model or document only when requested or
when it materially improves the interaction.

## Decision status

Use the following statuses:

- `open`: Decision identified but not yet sufficiently explored.
- `exploring`: Decision currently being investigated or evaluated.
- `decided`: A decision has been made.
- `on_hold`: Decision temporarily suspended.
- `rejected`: The decision or proposal has been explicitly rejected.
- `superseded`: The decision has been replaced by another decision.

Status must reflect the actual state of the decision.

Do not mark a decision as `decided` merely because its analysis
is sufficiently detailed.

A decision is considered made when the relevant decision-maker
explicitly commits to an alternative or course of action.

## Decision maturity

Decision maturity is not equivalent to completion of six stages.

Evaluate whether the current understanding is sufficient
for the decision being considered.

Consider:

- Clarity of the domain.
- Understanding of the current context.
- Clarity of desired outcomes.
- Critical assumptions and uncertainties.
- Relevant consequences and trade-offs.
- Adequacy of available evidence.
- Reversibility and potential impact.
- Remaining information gaps.

The required level of analysis must be proportional to the
decision's importance, complexity, uncertainty, and reversibility.

A decision may remain open even after substantial analysis.

## Handling insufficient information

When relevant information is missing:

1. Identify the information gap.
2. Explain why it matters.
3. Determine whether it prevents meaningful progress.
4. Ask a focused question when user input is necessary.
5. Otherwise, proceed with explicit assumptions.
6. Preserve unresolved uncertainties in the Decision Model.

Do not block the entire analysis because one dimension is incomplete.

## Handling new or contradictory information

When new information contradicts previous conclusions:

1. Identify the contradiction.
2. Determine which previous assumptions or conclusions are affected.
3. Evaluate the reliability and relevance of the new information.
4. Reassess affected dimensions.
5. Update the Decision Model.
6. Record the relevant change in Decision History.
7. Explain the implications to the user.

Do not silently discard previous information.

## Related decisions

A Decision Model represents one decision.

When another decision is relevant, record the relationship
using the appropriate relationship type:

- `depends_on`
- `constrains`
- `influences`
- `supersedes`
- `related_to`

Do not automatically merge distinct decisions into one model.

## Output representations

The Decision Model may support different representations:

- Decision summary.
- Context assessment.
- Objective analysis.
- Risk assessment.
- Alternative comparison.
- Consequence analysis.
- Decision record.
- Decision review.

These are different views of the same underlying model.

Generated documents do not replace the Decision Model.

## Operational constraints

- Do not require completion of all six dimensions.
- Do not force a linear workflow.
- Do not automatically select an alternative on behalf of the user.
- Do not confuse analysis with authorization or commitment.
- Do not invent evidence or stakeholder positions.
- Do not persist decisions outside the provided session.
- Do not lose relevant historical rationale during revisions.
- Keep the interaction focused on improving the decision.
