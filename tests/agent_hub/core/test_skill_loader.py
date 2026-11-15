from pathlib import Path

import pytest

from agent_hub.core import SkillLoader


def create_skill(
    skills_dir: Path,
    name: str = "example-skill",
) -> Path:
    skill_dir = skills_dir / name
    skill_dir.mkdir(parents=True)

    skill_file = skill_dir / "SKILL.md"
    skill_file.write_text(
        f"""---
name: {name}
description: Example skill for testing.
---

# Example Skill

These are the skill instructions.
""",
        encoding="utf-8",
    )

    return skill_file


def test_load_skill(tmp_path: Path) -> None:
    create_skill(tmp_path)

    skill = SkillLoader(tmp_path).load("example-skill")

    assert skill.name == "example-skill"
    assert skill.description == "Example skill for testing."
    assert "# Example Skill" in skill.instructions


def test_load_all_skills(tmp_path: Path) -> None:
    create_skill(tmp_path, "skill-one")
    create_skill(tmp_path, "skill-two")

    skills = SkillLoader(tmp_path).load_all()

    assert len(skills) == 2
    assert [skill.name for skill in skills] == [
        "skill-one",
        "skill-two",
    ]


def test_load_missing_skill_raises_error(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError):
        SkillLoader(tmp_path).load("missing-skill")


def test_missing_frontmatter_raises_error(tmp_path: Path) -> None:
    skill_dir = tmp_path / "invalid-skill"
    skill_dir.mkdir()

    (skill_dir / "SKILL.md").write_text(
        "# Invalid Skill",
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="Missing YAML frontmatter"):
        SkillLoader(tmp_path).load_all()


def test_skill_name_must_match_directory(tmp_path: Path) -> None:
    skill_dir = tmp_path / "directory-name"
    skill_dir.mkdir()

    (skill_dir / "SKILL.md").write_text(
        """---
name: different-name
description: Example skill.
---

Instructions.
""",
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="must match directory"):
        SkillLoader(tmp_path).load_all()