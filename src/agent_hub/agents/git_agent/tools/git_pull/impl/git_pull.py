import asyncio
import os
from pathlib import Path
from typing import Literal

from pydantic import BaseModel


class GitPullInput(BaseModel):
    root_path: Path


class RepositoryResult(BaseModel):
    repository_path: str
    status: Literal["success", "skipped", "failed"]
    message: str


class GitPullTool:
    name = "git-pull"
    description = "Pull updates from all Git repositories under a root directory."
    input_schema = GitPullInput

    def __init__(self, timeout: int = 120) -> None:
        if timeout <= 0:
            raise ValueError("Timeout must be greater than zero.")

        self.timeout = timeout

    async def execute(
        self,
        input: GitPullInput,
    ) -> list[RepositoryResult]:
        root = input.root_path.expanduser().resolve()

        if not root.exists() or not root.is_dir():
            raise ValueError(f"Invalid repository root: {root}")

        repositories = self._discover_repositories(root)
        results: list[RepositoryResult] = []

        for repository in repositories:
            result = await self._pull_repository(repository)
            results.append(result)

        return results

    @staticmethod
    def _discover_repositories(root: Path) -> list[Path]:
        repositories: list[Path] = []

        for current, directories, _ in os.walk(root):
            current_path = Path(current)
            directories.sort()

            if (current_path / ".git").exists():
                repositories.append(current_path)
                directories.clear()

        return sorted(repositories)

    async def _run_git(
        self,
        repository: Path,
        *args: str,
    ) -> tuple[int, str, str]:
        try:
            process = await asyncio.create_subprocess_exec(
                "git",
                *args,
                cwd=repository,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                env={**os.environ, "GIT_TERMINAL_PROMPT": "0"},
            )
        except OSError as error:
            return -1, "", f"Unable to execute Git: {error}"

        try:
            stdout, stderr = await asyncio.wait_for(
                process.communicate(),
                timeout=self.timeout,
            )
        except TimeoutError:
            try:
                process.kill()
            except ProcessLookupError:
                pass

            await process.communicate()
            return -1, "", "Git command timed out."

        returncode = process.returncode

        if returncode is None:
            return -1, "", "Git process terminated without an exit code."

        return (
            returncode,
            stdout.decode(errors="replace").strip(),
            stderr.decode(errors="replace").strip(),
        )

    async def _pull_repository(
        self,
        repository: Path,
    ) -> RepositoryResult:
        code, stdout, stderr = await self._run_git(
            repository,
            "status",
            "--porcelain",
        )

        if code != 0:
            return RepositoryResult(
                repository_path=str(repository),
                status="failed",
                message=stderr or stdout or "Unable to check repository status.",
            )

        if stdout:
            return RepositoryResult(
                repository_path=str(repository),
                status="skipped",
                message="Repository has uncommitted changes.",
            )

        code, stdout, stderr = await self._run_git(
            repository,
            "pull",
        )

        return RepositoryResult(
            repository_path=str(repository),
            status="success" if code == 0 else "failed",
            message=stdout or stderr or (
                "Git pull completed." if code == 0 else "Git pull failed."
            ),
        )