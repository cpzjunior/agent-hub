
from enum import StrEnum
from pathlib import Path

from pydantic import BaseModel, Field


class GitOperation(StrEnum):
    STATUS = "status"
    BRANCH_LIST = "branch_list"
    BRANCH_CREATE = "branch_create"
    BRANCH_SWITCH = "branch_switch"
    DIFF = "diff"
    LOG = "log"
    PULL = "pull"
    COMMIT = "commit"
    PUSH = "push"
    MERGE = "merge"


class GitCliInput(BaseModel):
    root_path: Path
    operation: GitOperation

    branch_name: str | None = None
    commit_message: str | None = None

    remote: str = "origin"
    limit: int = Field(default=10, ge=1, le=100)

    confirmed: bool = False


class GitCliOutput(BaseModel):
    operation: GitOperation
    return_code: int
    stdout: str = ""
    stderr: str = ""

    @property
    def success(self) -> bool:
        return self.return_code == 0
