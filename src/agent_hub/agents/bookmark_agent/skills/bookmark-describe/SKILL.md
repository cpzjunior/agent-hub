---
name: bookmark-describe
description: Generate concise and accurate bookmark descriptions in Brazilian Portuguese and English.
---

# Bookmark Description

Generate descriptions for a bookmark in Brazilian Portuguese and English.

## Responsibilities

Produce two descriptions based on the supplied resource information.

### Brazilian Portuguese

- Use natural Brazilian Portuguese.
- Prefer clear and objective language.
- Explain what the resource offers and why it is useful.
- Preserve technical terms when appropriate.
- Avoid literal translations from English.

### English

- Use natural, fluent English.
- Preserve the original meaning of the Portuguese description.
- Use appropriate technical terminology.
- Avoid unnecessary promotional language.

## Quality Guidelines

- Be concise and informative.
- Focus on the resource's actual purpose.
- Do not repeat the title unnecessarily.
- Avoid generic descriptions.
- Do not invent features, capabilities, or content.
- Do not make claims that are unsupported by the extracted information.
- Prefer one or two sentences per language.

## Output Requirements

Return:

- `description_pt_br`: description in Brazilian Portuguese.
- `description_en`: description in English.

Both descriptions must communicate the same essential information.

## Restrictions

- Do not classify the bookmark.
- Do not suggest categories or subcategories.
- Do not add personal opinions.
- Do not fabricate information.
