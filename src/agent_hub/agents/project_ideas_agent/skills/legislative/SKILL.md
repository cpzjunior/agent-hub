---
name: legislative
description: Create legislative proposals, public policy initiatives and regulatory reform ideas. Use when the user proposes creating, modifying or evaluating laws, regulations or government policies.
---

# Legislative Proposals

## Objective

Create a structured legislative proposal in Brazilian Portuguese, describing a legal or regulatory intervention intended to address a specific public problem, improve existing legislation or establish new rights, obligations, mechanisms or government policies.

The proposal must be sufficiently detailed to communicate its purpose, rationale, expected effects, implementation challenges and legal context.

## Jurisdiction

- Default jurisdiction: Brazil.
- Consider the Brazilian Federal Constitution, applicable legislation, regulatory frameworks and the distribution of legislative and administrative competencies among the Union, states, Federal District and municipalities.
- When the proposal concerns a specific jurisdiction or government level, respect its constitutional and legal competencies.
- Consider whether the proposed initiative requires a federal law, complementary law, constitutional amendment, state law, municipal law, regulation or another legal instrument.
- Do not assume that every public problem requires the creation of a new law. Consider whether modifying existing legislation or improving its enforcement would be more appropriate.

## Reference Documents

The application supplies an existing legislative proposal from the project-ideas repository:

`legislative/anti-overpricing-act/README.pt-BR.md`

Use it as a structural and level-of-detail reference.

Other legislative proposals may also be considered to understand the repository's writing conventions and expectations.

Do not copy their subject matter, mechanisms or wording.

## Required Structure

Follow this section structure:

- `# Title`
- `## 1. Ideia`
- `## 2. Motivação`
- `## 3. Benefícios esperados`
- `## 4. Impactos potenciais`
- `## 5. Viabilidade e desafios`
- `## 6. Pontos em aberto`
- `## 7. Referências`

### 1. Ideia

Describe the proposed legislative initiative clearly.

Explain:

- The legal or regulatory intervention being proposed.
- The main mechanisms, rules, obligations, rights or prohibitions.
- Who will be affected by the proposal.
- Which government institutions or regulatory authorities will be responsible for implementation and oversight, when applicable.
- The intended scope of application.

Describe the proposed mechanisms in sufficient detail to make their practical operation understandable.

Use numbered lists and subsections when the proposal contains multiple independent mechanisms.

### 2. Motivação

Explain the problem that justifies the legislative initiative.

Address:

- The current situation and existing problems.
- Limitations or gaps in the current legal and regulatory framework.
- Why existing mechanisms may be insufficient.
- The reasons why legislative intervention may be appropriate.
- The potential consequences of maintaining the current situation.

Distinguish documented facts from assumptions and hypotheses.

### 3. Benefícios esperados

Describe the expected benefits of the proposal.

Consider:

- Public interest and social benefits.
- Economic and financial effects.
- Improvements in transparency and accountability.
- Administrative efficiency.
- Legal certainty and predictability.
- Protection of citizens, consumers, businesses or other affected groups.

Use objective and specific benefits rather than generic statements.

Do not present speculative outcomes as guaranteed results.

### 4. Impactos potenciais

Evaluate both positive and negative impacts.

Consider relevant stakeholders, including:

- Citizens and society.
- Public administration.
- Businesses and economic sectors.
- Regulatory and oversight authorities.
- Government employees and public officials.
- Other directly affected groups.

Identify potential unintended consequences, implementation costs, economic distortions, compliance burdens and risks of abuse.

When appropriate, organize the impacts into positive and negative subsections.

### 5. Viabilidade e desafios

Evaluate the legal, institutional, administrative, technical and economic feasibility of the proposal.

Address:

- Constitutional compatibility.
- Legislative and administrative competencies.
- Compatibility with existing legislation.
- Potential conflicts or overlaps with existing legal provisions.
- Responsible institutions and enforcement mechanisms.
- Administrative and operational requirements.
- Implementation costs and funding.
- Oversight, accountability and enforcement.
- Due process and protection of fundamental rights.
- Potential judicial challenges.

Identify the legal instrument most appropriate for implementing the proposal.

When relevant, explain whether the initiative requires changes to existing legislation or the creation of new legal provisions.

### 6. Pontos em aberto

List questions and decisions that still require further investigation or definition.

Consider:

- Specific legal provisions and wording.
- Scope and applicability.
- Exceptions and special circumstances.
- Definitions and objective criteria.
- Responsibilities and institutional arrangements.
- Enforcement procedures.
- Penalties and sanctions.
- Transitional rules and implementation deadlines.
- Monitoring and evaluation mechanisms.

Do not artificially resolve every uncertainty. Preserve legitimate open questions for future development.

### 7. Referências

Include relevant and verifiable sources supporting the proposal.

Prioritize:

1. Brazilian Federal Constitution.
2. Existing federal, state and municipal legislation, as applicable.
3. Official government publications and regulatory documents.
4. Official legislative databases and legislative proposals.
5. Decisions and precedents from relevant courts.
6. Publications from regulatory and oversight authorities.
7. Academic research and other reputable sources.

Whenever possible, include direct links to official sources.

Do not invent laws, legislative proposals, court decisions, regulatory provisions, institutions or URLs.

Distinguish existing legislation from proposed changes and recommendations.

If a reference cannot be verified, do not present it as an established source.

## Research and Legal Analysis

Before developing the proposal:

- Identify the existing legislation governing the subject.
- Investigate whether similar legislative initiatives already exist.
- Identify relevant legislative proposals currently under consideration, when information is available.
- Examine potential conflicts with constitutional provisions and existing laws.
- Identify the institutions responsible for the subject.
- Consider whether the problem can be addressed through existing legislation or administrative measures.
- Evaluate alternative regulatory approaches.

Prefer primary and official sources over secondary interpretations.

Never fabricate legal references or claim that a proposal is legally viable without sufficient analysis.

When current information cannot be verified, explicitly identify the relevant uncertainty.

## Writing Rules

- Write in Brazilian Portuguese.
- Use clear, objective and technically precise language.
- Adopt a legislative and institutional perspective.
- Describe proposals as proposals, not as existing law.
- Distinguish legal facts, assumptions, recommendations and unresolved questions.
- Avoid ideological or partisan language.
- Do not favor or oppose political parties, candidates or specific political groups.
- Consider constitutional rights, proportionality, legal certainty and due process.
- Avoid unnecessary complexity and excessive legal terminology.
- Ensure consistency between the proposed mechanisms, rationale, expected benefits and implementation requirements.
- Do not invent statistics, legal precedents or factual claims.
- Preserve the Markdown conventions of the reference documents.

## Output

Return:

- `title`: document title.
- `content_pt_br`: complete Markdown document in Brazilian Portuguese.

Do not translate the document. The application invokes the shared `text-translate` skill separately.