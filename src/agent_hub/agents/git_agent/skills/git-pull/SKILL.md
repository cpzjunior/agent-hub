---
name: git-pull
description: Pull updates from all Git repositories under a configured root directory.
---

# Git Pull

## Input
- `root_path`: Absolute path containing Git repositories.

## Process
1. Invoke the `git-pull` tool with `root_path`.
2. Review the result for each repository.
3. Report successful, skipped and failed operations.

## Output
A summary containing:
- Total repositories discovered.
- Successful pulls.
- Skipped repositories.
- Failed repositories and their errors.

## Constraints
- Never modify or discard uncommitted changes.
- Report individual failures without stopping the operation.