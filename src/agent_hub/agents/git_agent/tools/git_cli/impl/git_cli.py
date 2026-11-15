
import asyncio
import os
import re
from pathlib import Path

from agent_hub.agents.git_agent.tools.git_cli.models import (
    GitCliInput,
    GitCliOutput,
    GitOperation,
)


class GitCliTool:
    _CONFIRMATION_REQUIRED = {
        GitOperation.PULL,
        GitOperation.COMMIT,
        GitOperation.PUSH,
        GitOperation.MERGE,
    }

    def __init__(self, timeout: float = 30.0) -> None:
        if timeout <= 0:
            raise ValueError("Timeout must be greater than zero.")

        self._timeout = timeout

    async def execute(self, request: GitCliInput) -> GitCliOutput:
        operation = request.operation

        if (
            operation in self._CONFIRMATION_REQUIRED
            and not request.confirmed
        ):
            raise ValueError(
                f"Operation '{operation.value}' requires confirmation."
            )

        root_path = request.root_path.resolve()

        if not root_path.is_dir():
            raise ValueError(f"Directory does not exist: {root_path}")

        repository_check = await self._run(
            root_path,
            ["rev-parse", "--is-inside-work-tree"],
            operation,
        )

        if not repository_check.success:
            raise ValueError(
                f"Directory is not a Git repository: {root_path}"
            )

        validation_error = await self._validate_request(
            root_path,
            request,
        )

        if validation_error is not None:
            return validation_error

        return await self._run(
            root_path,
            self._build_command(request),
            operation,
        )

    async def _validate_request(
        self,
        root_path: Path,
        request: GitCliInput,
    ) -> GitCliOutput | None:
        operation = request.operation

        if operation in {
            GitOperation.BRANCH_CREATE,
            GitOperation.BRANCH_SWITCH,
            GitOperation.MERGE,
        }:
            if not request.branch_name:
                raise ValueError(
                    f"Operation '{operation.value}' requires branch_name."
                )

            result = await self._run(
                root_path,
                ["check-ref-format", "--branch", request.branch_name],
                operation,
            )

            if not result.success:
                return GitCliOutput(
                    operation=operation,
                    return_code=result.return_code,
                    stderr="Invalid branch name.",
                )

        if operation == GitOperation.COMMIT:
            if (
                not request.commit_message
                or not request.commit_message.strip()
            ):
                raise ValueError(
                    "Operation 'commit' requires commit_message."
                )

        if operation in {GitOperation.PULL, GitOperation.PUSH}:
            if not re.fullmatch(
                r"[A-Za-z0-9][A-Za-z0-9._/-]*",
                request.remote,
            ):
                raise ValueError("Invalid remote name.")

            result = await self._run(
                root_path,
                ["remote"],
                operation,
            )

            if not result.success:
                return result

            remotes = result.stdout.splitlines()

            if request.remote not in remotes:
                return GitCliOutput(
                    operation=operation,
                    return_code=1,
                    stderr=f"Remote '{request.remote}' does not exist.",
                )

        return None

    @staticmethod
    def _build_command(request: GitCliInput) -> list[str]:
        operation = request.operation

        if operation == GitOperation.STATUS:
            return ["status", "--short", "--branch"]

        if operation == GitOperation.BRANCH_LIST:
            return ["branch", "--list"]

        if operation == GitOperation.BRANCH_CREATE:
            return ["branch", request.branch_name or ""]

        if operation == GitOperation.BRANCH_SWITCH:
            return ["switch", request.branch_name or ""]

        if operation == GitOperation.DIFF:
            return ["diff", "--"]

        if operation == GitOperation.LOG:
            return [
                "log",
                "--oneline",
                "--decorate",
                "-n",
                str(request.limit),
            ]

        if operation == GitOperation.PULL:
            return ["pull", request.remote]

        if operation == GitOperation.COMMIT:
            return ["commit", "-m", request.commit_message or ""]

        if operation == GitOperation.PUSH:
            return ["push", request.remote]

        if operation == GitOperation.MERGE:
            return [
                "merge",
                "--no-edit",
                request.branch_name or "",
            ]

        raise ValueError(f"Unsupported Git operation: {operation}")

    async def _run(
        self,
        root_path: Path,
        arguments: list[str],
        operation: GitOperation,
    ) -> GitCliOutput:
        environment = os.environ.copy()
        environment["GIT_TERMINAL_PROMPT"] = "0"

        try:
            process = await asyncio.create_subprocess_exec(
                "git",
                *arguments,
                cwd=root_path,
                env=environment,
                stdin=asyncio.subprocess.DEVNULL,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )

            stdout, stderr = await asyncio.wait_for(
                process.communicate(),
                timeout=self._timeout,
            )

            return GitCliOutput(
                operation=operation,
                return_code=(
                    process.returncode
                    if process.returncode is not None
                    else 1
                ),
                stdout=stdout.decode("utf-8", errors="replace"),
                stderr=stderr.decode("utf-8", errors="replace"),
            )

        except FileNotFoundError:
            return GitCliOutput(
                operation=operation,
                return_code=127,
                stderr="Git executable was not found.",
            )

        except TimeoutError:
            if "process" in locals() and process.returncode is None:
                process.kill()
                await process.communicate()

            return GitCliOutput(
                operation=operation,
                return_code=124,
                stderr=(
                    f"Git command timed out after "
                    f"{self._timeout} seconds."
                ),
            )
