---
name: git-operations
description: Execute operações Git em um repositório local, incluindo consulta de status, branches, diff, histórico, pull, commit, push e merge.
---

# Git Operations

Interpret the user's natural language instruction and select the appropriate Git operation.

Return structured parameters for the GitCliInput contract.

## Supported operations

- `status`: inspect repository status.
- `branch_list`: list local branches.
- `branch_create`: create a local branch. Requires `branch_name`.
- `branch_switch`: switch to an existing branch. Requires `branch_name`.
- `diff`: inspect working tree changes.
- `log`: inspect recent commits. Accepts optional `limit`.
- `pull`: pull changes from a remote. Accepts optional `remote`.
- `commit`: create a commit. Requires `commit_message`.
- `push`: push changes to a remote. Accepts optional `remote`.
- `merge`: merge another branch into the current branch. Requires `branch_name`.

## Parameter rules

- Always identify the requested operation.
- Do not invent a repository path. If it was not provided, report `root_path` as a missing input.
- Do not invent branch names or commit messages.
- Use `origin` as the default remote when the user does not specify one.
- Use `10` as the default log limit.
- Only return parameters relevant to the selected operation.
- Never return `confirmed`. Confirmation is controlled by the application, not by the language model.
- Do not generate shell commands or arbitrary Git arguments.

## Operation selection

Choose exactly one operation for each request.

If the instruction does not clearly correspond to a supported operation, do not force a match. Explain that the requested operation is unsupported.
