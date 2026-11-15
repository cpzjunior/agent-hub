---
name: bookmark-describe
description: Generate concise bookmark descriptions in Brazilian Portuguese and English. Use when creating or improving bookmark descriptions.
---

# Bookmark Describe

## Objective

Generate two equivalent descriptions for a bookmarked resource: one in Brazilian Portuguese and another in English.

## Instructions

1. Analyze the provided URL, title and extracted content.
2. Identify the resource's main subject, purpose and relevant characteristics.
3. Write a clear and informative description in Brazilian Portuguese.
4. Keep the description concise, preferably one or two sentences.
5. Use the shared `text-translate` skill to translate the Portuguese description into English.
6. Preserve exactly the meaning, context, tone and information of the original description during translation.
7. Do not introduce information that is not supported by the extracted content.
8. Preserve technical terminology, product names and proper nouns when appropriate.
9. Avoid generic introductions and unnecessary expressions.
10. Do not include category or subcategory recommendations.
11. Do not summarize or expand the description during translation.

## Output

Return both descriptions using the following fields:

- `description_pt_br`: Description in Brazilian Portuguese.
- `description_en`: Equivalent description in English.

Both descriptions must convey the same information and meaning.