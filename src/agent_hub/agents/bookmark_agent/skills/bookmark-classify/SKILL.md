---
name: bookmark-classify
description: Classify bookmarks using the existing local taxonomy and suggest new categories or subcategories when necessary.
---

# Bookmark Classification

Classify bookmarks using the taxonomy supplied by the application.

## Responsibilities

- Understand the resource's primary subject.
- Analyze the available categories and subcategories.
- Select the most appropriate existing category.
- Select the most appropriate existing subcategory.
- Suggest new taxonomy entries only when existing options are inadequate.

## Classification Guidelines

### Existing Categories

Always prioritize existing categories.

Choose the category that best represents the resource's primary purpose.

Do not create a new category merely because the resource covers multiple subjects.

### Existing Subcategories

Choose the most specific existing subcategory that accurately represents the resource.

Avoid classifications that are excessively broad or overly specific.

### New Categories

Suggest a new category only when:

- The resource does not fit any existing category.
- The subject represents a meaningful and sufficiently distinct group of resources.
- The proposed category could reasonably accommodate additional bookmarks.

### New Subcategories

Suggest a new subcategory only when:

- An existing category is appropriate.
- None of its existing subcategories adequately represents the resource.
- The proposed subcategory adds meaningful organization.

Do not suggest both a new category and a new subcategory unless there is a clear justification.

## Taxonomy Consistency

- Respect the existing naming conventions.
- Preserve the language and formatting conventions used by the repository.
- Avoid duplicate or synonymous categories.
- Do not assume that a category exists unless it appears in the supplied taxonomy.
- Treat the supplied local repository contents as the source of truth.

## Output Requirements

Return:

- `category`: recommended existing category, or null if a new category is proposed.
- `subcategory`: recommended existing subcategory, or null if a new subcategory is proposed.
- `new_category_suggestion`: proposed category, if necessary.
- `new_subcategory_suggestion`: proposed subcategory, if necessary.
- `reasoning`: concise explanation of the classification.

If the existing taxonomy is sufficient, both new suggestion fields must be null.

## Restrictions

- Do not modify the repository.
- Do not create taxonomy files.
- Do not invent existing categories.
- Do not suggest new categories without justification.
