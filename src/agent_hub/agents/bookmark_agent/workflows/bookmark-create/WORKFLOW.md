
---
name: bookmark-create
description: Create a complete bookmark from a URL by extracting its information, generating bilingual descriptions, and classifying it.
---

# Bookmark Creation Workflow

Execute the three bookmark skills in sequence to produce a complete bookmark proposal.

## Input

Required:

- `url`: resource URL.

## Execution

### Step 1: Extract

Execute `bookmark-extract`.

Provide:

- URL.
- Page title.
- Page metadata.
- Extracted page content.

Expected output:

- Resource title.
- Resource summary.

If extraction fails or the available information is insufficient, stop the workflow and request additional information.

### Step 2: Describe

Execute `bookmark-describe`.

Provide:

- Resource title.
- Extracted content.

Expected output:

- Description in Brazilian Portuguese.
- Description in English.

Both descriptions must represent the same resource accurately.

### Step 3: Classify

Execute `bookmark-classify`.

Provide:

- Resource title.
- Extracted content.
- Both descriptions.
- Current repository taxonomy.

Expected output:

- Recommended category.
- Recommended subcategory.
- Optional new category suggestion.
- Optional new subcategory suggestion.
- Classification rationale.

## Final Result

Combine the outputs into a single bookmark proposal.

Return:

- URL.
- Title.
- Brazilian Portuguese description.
- English description.
- Recommended category.
- Recommended subcategory.
- Optional taxonomy suggestions.
- Classification rationale.

## Error Handling

- Stop if extraction cannot provide sufficient information.
- Do not invent page content.
- Do not generate descriptions from unsupported assumptions.
- Do not classify without access to the current taxonomy.
- Preserve successful intermediate results when a later stage fails.

## Repository Restrictions

This workflow is read-only.

Never modify the bookmarks repository automatically.

New categories and subcategories are suggestions and require user review.
