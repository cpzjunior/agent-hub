# Git Pull Tool

## Identity

- **Name:** `git-pull`
- **Description:** Pull updates from all Git repositories under a root directory.
- **Agent:** `git-agent`

## Purpose

Discover Git repositories under a configured root directory and execute `git pull` on each repository.

Each repository is processed independently. A failure in one repository must not prevent processing the others.

## Input

| Field | Type | Required | Description |
|---|---|---|---|
| `root_path` | `Path` | Yes | Root directory containing Git repositories. |

The root directory must exist and be a directory.

## Output

Returns a list of `RepositoryResult` objects.

| Field | Type | Description |
|---|---|---|
| `repository_path` | `str` | Absolute path of the repository. |
| `status` | `str` | Operation result: `success`, `skipped` or `failed`. |
| `message` | `str` | Operation details or error description. |

## Execution Flow

1. Expand the root path and resolve its absolute location.
2. Validate that the root directory exists.
3. Recursively discover Git repositories.
4. Sort discovered repository paths.
5. For each repository:
   - Check its working tree using `git status --porcelain`.
   - Skip the repository if uncommitted changes exist.
   - Execute `git pull` if the working tree is clean.
   - Record the operation result.
6. Return all repository results.

## Discovery Rules

- A directory containing a `.git` file or directory is considered a Git repository.
- Once a repository is discovered, its subdirectories are not traversed.
- Nested repositories inside another discovered repository are not processed separately.
- Repository discovery must be deterministic.

## Configuration

| Parameter | Default | Description |
|---|---|---|
| `timeout` | `120` seconds | Maximum execution time for each Git command. |

The timeout must be greater than zero.

## Error Handling

- Invalid root directories raise `ValueError`.
- Git execution errors are recorded as `failed`.
- Git command timeouts are recorded as `failed`.
- A failed repository must not interrupt processing of subsequent repositories.
- Every discovered repository must have a corresponding result.

## Constraints

- Never discard or overwrite uncommitted changes.
- Never execute `git reset`, `git clean` or equivalent destructive commands.
- Do not stop processing because of an individual repository failure.
- Disable interactive Git prompts.
- Do not modify repository configuration.

## Dependencies

- Git executable available in the system PATH.
- Python standard library.
- Pydantic.
