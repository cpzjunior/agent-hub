
import subprocess
from pathlib import Path

import pytest

from agent_hub.agents.git_agent.tools.git_cli import (
    GitCliInput,
    GitCliTool,
    GitOperation,
)


@pytest.fixture
def git_repository(tmp_path: Path) -> Path:
    repository = tmp_path / "repository"
    repository.mkdir()

    def git(*arguments: str) -> None:
        subprocess.run(
            ["git", *arguments],
            cwd=repository,
            check=True,
            capture_output=True,
            text=True,
        )

    git("init")
    git("config", "user.name", "Agent Hub Tests")
    git("config", "user.email", "tests@agent-hub.local")

    (repository / "README.md").write_text(
        "# Test repository\n",
        encoding="utf-8",
    )

    git("add", "README.md")
    git("commit", "-m", "Initial commit")

    return repository


@pytest.fixture
def tool() -> GitCliTool:
    return GitCliTool()


@pytest.mark.asyncio
async def test_status_returns_repository_status(
    tool: GitCliTool,
    git_repository: Path,
) -> None:
    result = await tool.execute(
        GitCliInput(
            root_path=git_repository,
            operation=GitOperation.STATUS,
        )
    )

    assert result.success
    assert "##" in result.stdout


@pytest.mark.asyncio
async def test_branch_list_returns_local_branches(
    tool: GitCliTool,
    git_repository: Path,
) -> None:
    result = await tool.execute(
        GitCliInput(
            root_path=git_repository,
            operation=GitOperation.BRANCH_LIST,
        )
    )

    assert result.success
    assert result.stdout.strip()


@pytest.mark.asyncio
async def test_branch_create_creates_branch(
    tool: GitCliTool,
    git_repository: Path,
) -> None:
    result = await tool.execute(
        GitCliInput(
            root_path=git_repository,
            operation=GitOperation.BRANCH_CREATE,
            branch_name="feature/test",
        )
    )

    assert result.success

    branches = subprocess.run(
        ["git", "branch", "--list"],
        cwd=git_repository,
        check=True,
        capture_output=True,
        text=True,
    )

    assert "feature/test" in branches.stdout


@pytest.mark.asyncio
async def test_branch_switch_changes_current_branch(
    tool: GitCliTool,
    git_repository: Path,
) -> None:
    subprocess.run(
        ["git", "branch", "feature/test"],
        cwd=git_repository,
        check=True,
        capture_output=True,
        text=True,
    )

    result = await tool.execute(
        GitCliInput(
            root_path=git_repository,
            operation=GitOperation.BRANCH_SWITCH,
            branch_name="feature/test",
        )
    )

    assert result.success

    current_branch = subprocess.run(
        ["git", "branch", "--show-current"],
        cwd=git_repository,
        check=True,
        capture_output=True,
        text=True,
    )

    assert current_branch.stdout.strip() == "feature/test"


@pytest.mark.asyncio
async def test_branch_create_rejects_invalid_name(
    tool: GitCliTool,
    git_repository: Path,
) -> None:
    result = await tool.execute(
        GitCliInput(
            root_path=git_repository,
            operation=GitOperation.BRANCH_CREATE,
            branch_name="invalid branch name",
        )
    )

    assert not result.success
    assert result.stderr == "Invalid branch name."


@pytest.mark.asyncio
async def test_diff_returns_working_tree_changes(
    tool: GitCliTool,
    git_repository: Path,
) -> None:
    (git_repository / "README.md").write_text(
        "# Modified repository\n",
        encoding="utf-8",
    )

    result = await tool.execute(
        GitCliInput(
            root_path=git_repository,
            operation=GitOperation.DIFF,
        )
    )

    assert result.success
    assert "Modified repository" in result.stdout


@pytest.mark.asyncio
async def test_log_returns_recent_commits(
    tool: GitCliTool,
    git_repository: Path,
) -> None:
    result = await tool.execute(
        GitCliInput(
            root_path=git_repository,
            operation=GitOperation.LOG,
            limit=5,
        )
    )

    assert result.success
    assert "Initial commit" in result.stdout


@pytest.mark.asyncio
async def test_commit_requires_confirmation(
    tool: GitCliTool,
    git_repository: Path,
) -> None:
    with pytest.raises(ValueError, match="requires confirmation"):
        await tool.execute(
            GitCliInput(
                root_path=git_repository,
                operation=GitOperation.COMMIT,
                commit_message="Test commit",
            )
        )


@pytest.mark.asyncio
async def test_commit_creates_commit_when_confirmed(
    tool: GitCliTool,
    git_repository: Path,
) -> None:
    (git_repository / "README.md").write_text(
        "# Updated repository\n",
        encoding="utf-8",
    )

    subprocess.run(
        ["git", "add", "README.md"],
        cwd=git_repository,
        check=True,
        capture_output=True,
        text=True,
    )

    result = await tool.execute(
        GitCliInput(
            root_path=git_repository,
            operation=GitOperation.COMMIT,
            commit_message="Update README",
            confirmed=True,
        )
    )

    assert result.success, (
        f"return_code={result.return_code}\n"
        f"stdout={result.stdout}\n"
        f"stderr={result.stderr}"
    )

    commit_message = subprocess.run(
        ["git", "log", "-1", "--format=%s"],
        cwd=git_repository,
        check=True,
        capture_output=True,
        text=True,
    )

    assert commit_message.stdout.strip() == "Update README"


@pytest.mark.asyncio
async def test_pull_requires_confirmation(
    tool: GitCliTool,
    git_repository: Path,
) -> None:
    with pytest.raises(ValueError, match="requires confirmation"):
        await tool.execute(
            GitCliInput(
                root_path=git_repository,
                operation=GitOperation.PULL,
            )
        )


@pytest.mark.asyncio
async def test_push_requires_confirmation(
    tool: GitCliTool,
    git_repository: Path,
) -> None:
    with pytest.raises(ValueError, match="requires confirmation"):
        await tool.execute(
            GitCliInput(
                root_path=git_repository,
                operation=GitOperation.PUSH,
            )
        )


@pytest.mark.asyncio
async def test_merge_requires_confirmation(
    tool: GitCliTool,
    git_repository: Path,
) -> None:
    with pytest.raises(ValueError, match="requires confirmation"):
        await tool.execute(
            GitCliInput(
                root_path=git_repository,
                operation=GitOperation.MERGE,
                branch_name="main",
            )
        )


@pytest.mark.asyncio
async def test_merge_merges_existing_branch(
    tool: GitCliTool,
    git_repository: Path,
) -> None:
    subprocess.run(
        ["git", "branch", "feature/test"],
        cwd=git_repository,
        check=True,
        capture_output=True,
        text=True,
    )

    result = await tool.execute(
        GitCliInput(
            root_path=git_repository,
            operation=GitOperation.MERGE,
            branch_name="feature/test",
            confirmed=True,
        )
    )

    assert result.success


@pytest.mark.asyncio
async def test_operation_rejects_nonexistent_directory(
    tool: GitCliTool,
    tmp_path: Path,
) -> None:
    with pytest.raises(ValueError, match="Directory does not exist"):
        await tool.execute(
            GitCliInput(
                root_path=tmp_path / "missing",
                operation=GitOperation.STATUS,
            )
        )


@pytest.mark.asyncio
async def test_operation_rejects_non_git_directory(
    tool: GitCliTool,
    tmp_path: Path,
) -> None:
    with pytest.raises(ValueError, match="not a Git repository"):
        await tool.execute(
            GitCliInput(
                root_path=tmp_path,
                operation=GitOperation.STATUS,
            )
        )


def test_timeout_must_be_positive() -> None:
    with pytest.raises(ValueError, match="Timeout must be greater than zero"):
        GitCliTool(timeout=0)
