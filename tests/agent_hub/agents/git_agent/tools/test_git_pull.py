import subprocess
from pathlib import Path

import pytest

from agent_hub.agents.git_agent.tools.git_pull.impl.git_pull import (
    GitPullInput,
    GitPullTool,
)


def run_git(*args: str, cwd: Path | None = None) -> None:
    subprocess.run(
        ["git", *args],
        cwd=cwd,
        check=True,
        capture_output=True,
    )


def create_repository(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)
    run_git("init", "--initial-branch=main", str(path))
    run_git("config", "user.name", "Test", cwd=path)
    run_git("config", "user.email", "test@example.com", cwd=path)


def create_remote_repository(
    tmp_path: Path,
    workspace: Path | None = None,
) -> tuple[Path, Path, Path]:
    remote = tmp_path / "remote.git"
    seed = tmp_path / "seed"
    workspace = workspace or (tmp_path / "workspace")
    repository = workspace / "repo"

    workspace.mkdir(parents=True, exist_ok=True)

    run_git("init", "--bare", "--initial-branch=main", str(remote))
    create_repository(seed)

    (seed / "README.md").write_text("Initial content", encoding="utf-8")
    run_git("add", ".", cwd=seed)
    run_git("commit", "-m", "Initial commit", cwd=seed)
    run_git("remote", "add", "origin", str(remote), cwd=seed)
    run_git("push", "-u", "origin", "main", cwd=seed)

    run_git("clone", str(remote), str(repository))

    return remote, seed, repository


def test_invalid_root_path_raises_error(tmp_path: Path) -> None:
    tool = GitPullTool()
    invalid_path = tmp_path / "nonexistent"

    with pytest.raises(ValueError):
        import asyncio

        asyncio.run(tool.execute(GitPullInput(root_path=invalid_path)))


def test_discover_repositories_returns_empty_list(tmp_path: Path) -> None:
    repositories = GitPullTool._discover_repositories(tmp_path)

    assert repositories == []


def test_discover_repositories_finds_git_repository(tmp_path: Path) -> None:
    repository = tmp_path / "repo"
    create_repository(repository)

    repositories = GitPullTool._discover_repositories(tmp_path)

    assert repositories == [repository]


async def test_execute_pulls_remote_changes(tmp_path: Path) -> None:
    _, seed, repository = create_remote_repository(tmp_path)

    (seed / "README.md").write_text("Updated content", encoding="utf-8")
    run_git("add", ".", cwd=seed)
    run_git("commit", "-m", "Update README", cwd=seed)
    run_git("push", cwd=seed)

    tool = GitPullTool()
    results = await tool.execute(
        GitPullInput(root_path=repository.parent)
    )

    assert len(results) == 1
    assert results[0].status == "success"
    assert (repository / "README.md").read_text(encoding="utf-8") == (
        "Updated content"
    )


async def test_execute_skips_repository_with_uncommitted_changes(
    tmp_path: Path,
) -> None:
    _, _, repository = create_remote_repository(tmp_path)

    (repository / "README.md").write_text("Local changes", encoding="utf-8")

    tool = GitPullTool()
    results = await tool.execute(
        GitPullInput(root_path=repository.parent)
    )

    assert len(results) == 1
    assert results[0].status == "skipped"
    assert "uncommitted changes" in results[0].message.lower()
    assert (repository / "README.md").read_text(encoding="utf-8") == (
        "Local changes"
    )


async def test_execute_continues_after_repository_failure(
    tmp_path: Path,
) -> None:
    workspace = tmp_path / "workspace"
    workspace.mkdir()

    invalid_repository = workspace / "invalid"
    create_repository(invalid_repository)

    _, seed, valid_repository = create_remote_repository(
        tmp_path,
        workspace=workspace,
    )

    # Rename the cloned repository to keep both repositories in the workspace.
    valid_repository.rename(workspace / "valid")
    valid_repository = workspace / "valid"

    (seed / "README.md").write_text("Updated content", encoding="utf-8")
    run_git("add", ".", cwd=seed)
    run_git("commit", "-m", "Update README", cwd=seed)
    run_git("push", cwd=seed)

    tool = GitPullTool()
    results = await tool.execute(GitPullInput(root_path=workspace))

    assert len(results) == 2
    assert results[0].status == "failed"
    assert results[1].status == "success"
    assert (valid_repository / "README.md").read_text(encoding="utf-8") == (
        "Updated content"
    )