
# Git CLI Tool

## Purpose

Execute supported Git operations against a local repository.

## Input

- root_path: Local repository path.
- operation: Supported Git operation.
- branch_name: Branch used by branch and merge operations.
- commit_message: Message used by commit.
- remote: Remote repository name. Defaults to origin.
- limit: Maximum number of commits returned by log.
- confirmed: Explicit confirmation for operations requiring approval.

## Supported operations

- status
- branch_list
- branch_create
- branch_switch
- diff
- log
- pull
- commit
- push
- merge

## Safety

- Only predefined Git operations are supported.
- Arbitrary shell commands are not accepted.
- Commands execute without shell=True.
- Repository path must exist and be a Git working tree.
- Branch names are validated by Git.
- Remote names are validated against configured remotes.
- Pull, commit, push and merge require explicit confirmation.
- Commands have a configurable timeout.
- Interactive terminal prompts are disabled.

## Output

- operation: Executed operation.
- return_code: Git process exit code.
- stdout: Standard output.
- stderr: Standard error.
- success: Whether the operation succeeded.
