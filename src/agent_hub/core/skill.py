import re
from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel


class Skill(BaseModel):
    name: str
    description: str
    instructions: str
    path: Path


class SkillLoader:
    """Discover and load Agent Skills from a directory."""

    def __init__(self, skills_dir: Path) -> None:
        self.skills_dir = skills_dir

    def load_all(self) -> list[Skill]:
        if not self.skills_dir.is_dir():
            raise FileNotFoundError(
                f"Skills directory not found: {self.skills_dir}"
            )

        skill_files = sorted(self.skills_dir.glob("*/SKILL.md"))

        return [self._load_skill(path) for path in skill_files]

    def load(self, name: str) -> Skill:
        skill_path = self.skills_dir / name / "SKILL.md"

        if not skill_path.is_file():
            raise FileNotFoundError(f"Skill not found: {name}")

        return self._load_skill(skill_path)

    @staticmethod
    def _load_skill(path: Path) -> Skill:
        content = path.read_text(encoding="utf-8")
        lines = content.splitlines()

        if not lines or lines[0].strip() != "---":
            raise ValueError(f"Missing YAML frontmatter: {path}")

        try:
            closing_index = next(
                index
                for index, line in enumerate(lines[1:], start=1)
                if line.strip() == "---"
            )
        except StopIteration as error:
            raise ValueError(
                f"Unclosed YAML frontmatter: {path}"
            ) from error

        metadata_content = "\n".join(lines[1:closing_index])
        instructions = "\n".join(lines[closing_index + 1 :]).strip()

        try:
            metadata: Any = yaml.safe_load(metadata_content)
        except yaml.YAMLError as error:
            raise ValueError(
                f"Invalid YAML frontmatter in {path}: {error}"
            ) from error

        if not isinstance(metadata, dict):
            raise ValueError(f"Invalid skill metadata: {path}")

        name = metadata.get("name")
        description = metadata.get("description")

        if not isinstance(name, str) or not name.strip():
            raise ValueError(f"Skill name is missing or invalid: {path}")

        if not isinstance(description, str) or not description.strip():
            raise ValueError(
                f"Skill description is missing or invalid: {path}"
            )

        if len(name) > 64 or not re.fullmatch(
            r"[a-z0-9]+(?:-[a-z0-9]+)*",
            name,
        ):
            raise ValueError(f"Invalid skill name: {name}")

        if path.parent.name != name:
            raise ValueError(
                f"Skill name '{name}' must match directory '{path.parent.name}'."
            )

        if not instructions:
            raise ValueError(f"Skill instructions are empty: {path}")

        return Skill(
            name=name,
            description=description,
            instructions=instructions,
            path=path,
        )