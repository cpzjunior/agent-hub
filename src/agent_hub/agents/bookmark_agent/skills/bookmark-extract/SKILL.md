---
name: bookmark-extract
description: Extract relevant and verifiable information from a web page to prepare a bookmark.
---

# Bookmark Extraction

Extract information from a web page using the content provided by the application.

## Responsibilities

- Identify the resource represented by the URL.
- Determine its actual title.
- Extract its main subject and purpose.
- Identify the type of resource, such as repository, article, documentation, video, channel, or website.
- Remove irrelevant navigation and boilerplate information.
- Preserve relevant technical names and terminology.

## Information Sources

Use the supplied page title, metadata, URL, and extracted page content.

Do not assume that the URL alone provides sufficient information.

Never invent information that cannot be verified from the supplied content.

If the page content is insufficient, report the missing information.

## Output Requirements

Return:

- `title`: resource title.
- `content`: concise factual summary of the resource.

The content must be sufficient for the description and classification stages.

## Restrictions

- Do not generate bookmark descriptions.
- Do not select categories.
- Do not invent missing information.
- Do not treat advertisements or navigation elements as the main content.
