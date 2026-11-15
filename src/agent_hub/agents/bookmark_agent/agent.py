import asyncio
from html.parser import HTMLParser
from pathlib import Path
from typing import Any, Literal
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import Request, urlopen

from pydantic import BaseModel, Field, field_validator

from agent_hub.core import (
    Agent,
    InterpretationRequest,
    Interpreter,
    Skill,
    SkillLoader,
)

BookmarkOperation = Literal["create", "extract", "describe", "classify"]


class BookmarkAgentRequest(BaseModel):
    url: str | None = None
    operation: BookmarkOperation = "create"
    content: str | None = None
    title: str | None = None

    @field_validator("url")
    @classmethod
    def validate_url(cls, value: str | None) -> str | None:
        if value is None:
            return None

        value = value.strip()
        parsed = urlparse(value)

        if parsed.scheme not in {"http", "https"} or not parsed.netloc:
            raise ValueError("A valid HTTP or HTTPS URL is required.")

        return value

    @field_validator("content", "title")
    @classmethod
    def normalize_text(cls, value: str | None) -> str | None:
        if value is None:
            return None

        value = value.strip()
        return value or None


class BookmarkAgentOutput(BaseModel):
    status: Literal["completed", "needs_input", "unsupported", "failed"]
    message: str
    url: str | None = None
    title: str | None = None
    content: str | None = None
    description_pt_br: str | None = None
    description_en: str | None = None
    category: str | None = None
    subcategory: str | None = None
    new_category_suggestion: str | None = None
    new_subcategory_suggestion: str | None = None
    reasoning: str | None = None
    required_input: str | None = None
    validation_notes: list[str] = Field(default_factory=list)


class _PageParser(HTMLParser):
    _IGNORED_TAGS = {
        "script",
        "style",
        "noscript",
        "svg",
        "nav",
        "footer",
        "header",
    }

    def __init__(self) -> None:
        super().__init__()
        self.title = ""
        self.description = ""
        self.content = ""

        self._inside_title = False
        self._ignored_depth = 0

    def handle_starttag(
        self,
        tag: str,
        attrs: list[tuple[str, str | None]],
    ) -> None:
        if tag in self._IGNORED_TAGS:
            self._ignored_depth += 1
            return

        if self._ignored_depth > 0:
            return

        if tag == "title":
            self._inside_title = True
            return

        if tag == "meta":
            attributes = dict(attrs)
            name = (
                attributes.get("name")
                or attributes.get("property")
                or ""
            ).lower()

            if name in {
                "description",
                "og:description",
                "twitter:description",
            }:
                value = attributes.get("content")
                if value and not self.description:
                    self.description = value.strip()

    def handle_endtag(self, tag: str) -> None:
        if tag in self._IGNORED_TAGS:
            if self._ignored_depth > 0:
                self._ignored_depth -= 1
            return

        if tag == "title":
            self._inside_title = False

    def handle_data(self, data: str) -> None:
        if self._ignored_depth > 0:
            return

        text = data.strip()
        if not text:
            return

        if self._inside_title:
            self.title = f"{self.title} {text}".strip()
        else:
            self.content = f"{self.content} {text}".strip()


class BookmarkAgent(Agent):
    _MAX_PAGE_SIZE = 2 * 1024 * 1024
    _MAX_PAGE_TEXT = 15000
    _MAX_TAXONOMY_SIZE = 30000
    _PAGE_TIMEOUT = 15

    name = "bookmark-agent"

    description = (
        "Creates bookmark proposals by extracting page content, "
        "generating bilingual descriptions and classifying bookmarks "
        "using a local taxonomy."
    )

    def __init__(
        self,
        interpreter: Interpreter | None = None,
        bookmarks_path: Path | str | None = None,
    ) -> None:
        self._interpreter = interpreter
        self._bookmarks_path = (
            Path(bookmarks_path).expanduser().resolve()
            if bookmarks_path is not None
            else None
        )

        skills_directory = Path(__file__).parent / "skills"
        loaded_skills = SkillLoader(skills_directory).load_all()
        self._skills = {skill.name: skill for skill in loaded_skills}

    @property
    def input_schema(self) -> type[BaseModel]:
        return BookmarkAgentRequest

    @property
    def output_schema(self) -> type[BaseModel]:
        return BookmarkAgentOutput

    @property
    def skills(self) -> tuple[Skill, ...]:
        return tuple(self._skills.values())

    async def run(
        self,
        input: BaseModel | dict[str, Any],
    ) -> BookmarkAgentOutput:
        try:
            request = BookmarkAgentRequest.model_validate(input)

            if self._interpreter is None:
                return self._needs_input("interpreter")

            title = request.title
            content = request.content
            url = request.url

            descriptions: dict[str, Any] = {}
            classification: dict[str, Any] = {}

            if request.operation in {"create", "extract"}:
                if not url:
                    return self._needs_input("url")

                page = await self._extract_page(url)

                if page.status != "completed":
                    page.url = url
                    return page

                title = title or page.title
                content = content or page.content

                skill_result = await self._run_skill(
                    "bookmark-extract",
                    {
                        "url": url,
                        "title": title,
                        "description": page.message,
                        "content": content,
                    },
                )

                if isinstance(skill_result, BookmarkAgentOutput):
                    skill_result.url = url
                    return skill_result

                title = self._required_string(skill_result, "title") or title
                content = self._required_string(skill_result, "content")

                if not content:
                    return BookmarkAgentOutput(
                        status="needs_input",
                        message="The page content could not be extracted.",
                        url=url,
                        required_input="content",
                    )

                if request.operation == "extract":
                    return BookmarkAgentOutput(
                        status="completed",
                        message="Page content extracted successfully.",
                        url=url,
                        title=title,
                        content=content,
                    )

            if request.operation in {"describe", "classify"}:
                if not content:
                    return self._needs_input("content")

            if request.operation in {"create", "describe"}:
                skill_result = await self._run_skill(
                    "bookmark-describe",
                    {
                        "url": url,
                        "title": title,
                        "content": content,
                    },
                )

                if isinstance(skill_result, BookmarkAgentOutput):
                    skill_result.url = url
                    return skill_result

                descriptions = skill_result

                description_pt_br = self._required_string(
                    descriptions,
                    "description_pt_br",
                )
                description_en = self._required_string(
                    descriptions,
                    "description_en",
                )

                if not description_pt_br or not description_en:
                    return BookmarkAgentOutput(
                        status="failed",
                        message=(
                            "The description skill returned incomplete "
                            "descriptions."
                        ),
                        url=url,
                        title=title,
                        content=content,
                    )

                if request.operation == "describe":
                    return BookmarkAgentOutput(
                        status="completed",
                        message="Descriptions generated successfully.",
                        url=url,
                        title=title,
                        content=content,
                        description_pt_br=description_pt_br,
                        description_en=description_en,
                    )

            if request.operation in {"create", "classify"}:
                if self._bookmarks_path is None:
                    return self._needs_input("bookmarks_path")

                taxonomy = await asyncio.to_thread(self._read_taxonomy)

                skill_result = await self._run_skill(
                    "bookmark-classify",
                    {
                        "url": url,
                        "title": title,
                        "content": content,
                        "description_pt_br": descriptions.get(
                            "description_pt_br"
                        ),
                        "description_en": descriptions.get("description_en"),
                        "taxonomy": taxonomy,
                    },
                )

                if isinstance(skill_result, BookmarkAgentOutput):
                    skill_result.url = url
                    return skill_result

                classification = skill_result

                category = self._required_string(
                    classification,
                    "category",
                )
                subcategory = self._required_string(
                    classification,
                    "subcategory",
                )

                if not category:
                    return BookmarkAgentOutput(
                        status="failed",
                        message=(
                            "The classification skill did not return "
                            "a category."
                        ),
                        url=url,
                        title=title,
                        content=content,
                    )

                if request.operation == "classify":
                    return BookmarkAgentOutput(
                        status="completed",
                        message="Bookmark classified successfully.",
                        url=url,
                        title=title,
                        content=content,
                        category=category,
                        subcategory=subcategory,
                        new_category_suggestion=self._optional_string(
                            classification,
                            "new_category_suggestion",
                        ),
                        new_subcategory_suggestion=self._optional_string(
                            classification,
                            "new_subcategory_suggestion",
                        ),
                        reasoning=self._optional_string(
                            classification,
                            "reasoning",
                        ),
                    )

            return BookmarkAgentOutput(
                status="completed",
                message="Bookmark proposal generated successfully.",
                url=url,
                title=title,
                content=content,
                description_pt_br=self._optional_string(
                    descriptions,
                    "description_pt_br",
                ),
                description_en=self._optional_string(
                    descriptions,
                    "description_en",
                ),
                category=self._optional_string(
                    classification,
                    "category",
                ),
                subcategory=self._optional_string(
                    classification,
                    "subcategory",
                ),
                new_category_suggestion=self._optional_string(
                    classification,
                    "new_category_suggestion",
                ),
                new_subcategory_suggestion=self._optional_string(
                    classification,
                    "new_subcategory_suggestion",
                ),
                reasoning=self._optional_string(
                    classification,
                    "reasoning",
                ),
            )

        except (HTTPError, URLError, TimeoutError, OSError) as exc:
            return BookmarkAgentOutput(
                status="failed",
                message=f"Unable to access the requested resource: {exc}",
            )
        except ValueError as exc:
            return BookmarkAgentOutput(
                status="failed",
                message=str(exc),
            )
        except Exception as exc:
            return BookmarkAgentOutput(
                status="failed",
                message=f"Bookmark processing failed: {exc}",
            )

    async def _run_skill(
        self,
        skill_name: str,
        context: dict[str, Any],
    ) -> dict[str, Any] | BookmarkAgentOutput:
        skill = self._skills.get(skill_name)

        if skill is None:
            return BookmarkAgentOutput(
                status="failed",
                message=f"Skill '{skill_name}' was not found.",
            )

        interpreter = self._interpreter

        if interpreter is None:
            return self._needs_input("interpreter")

        instruction = (
            f"Execute the skill '{skill_name}' using the following context:\n"
            f"{context!r}"
        )

        result = await interpreter.interpret(
            InterpretationRequest(
                instruction=instruction,
                skills=[skill],
            )
        )

        if result.missing_inputs:
            return BookmarkAgentOutput(
                status="needs_input",
                message=result.message or "Additional input is required.",
                required_input=", ".join(result.missing_inputs),
            )

        if result.skill_name != skill_name:
            return BookmarkAgentOutput(
                status="unsupported",
                message=(
                    f"The interpreter did not execute the expected skill "
                    f"'{skill_name}'."
                ),
            )

        return result.parameters

    async def _extract_page(self, url: str) -> BookmarkAgentOutput:
        page = await asyncio.to_thread(self._read_page, url)

        return BookmarkAgentOutput(
            status="completed",
            message=page["description"],
            url=url,
            title=page["title"],
            content=page["content"],
        )

    def _read_page(self, url: str) -> dict[str, str]:
        request = Request(
            url,
            headers={
                "User-Agent": "AgentHub-BookmarkAgent/1.0",
                "Accept": "text/html,application/xhtml+xml",
            },
        )

        with urlopen(request, timeout=self._PAGE_TIMEOUT) as response:
            content_type = response.headers.get_content_type()

            if content_type not in {"text/html", "application/xhtml+xml"}:
                raise ValueError(
                    f"Unsupported page content type: {content_type}"
                )

            raw_content = response.read(self._MAX_PAGE_SIZE + 1)

            if len(raw_content) > self._MAX_PAGE_SIZE:
                raise ValueError("The page exceeds the maximum allowed size.")

            charset = response.headers.get_content_charset() or "utf-8"

        html = raw_content.decode(charset, errors="replace")

        parser = _PageParser()
        parser.feed(html)

        return {
            "title": parser.title.strip(),
            "description": parser.description.strip(),
            "content": parser.content[: self._MAX_PAGE_TEXT],
        }

    def _read_taxonomy(self) -> str:
        if self._bookmarks_path is None:
            raise ValueError("The bookmarks repository path is not configured.")

        if not self._bookmarks_path.is_dir():
            raise ValueError(
                f"Bookmarks repository not found: {self._bookmarks_path}"
            )

        excluded_directories = {
            ".git",
            ".venv",
            "__pycache__",
            "node_modules",
        }

        markdown_files = sorted(
            path
            for path in self._bookmarks_path.rglob("*.md")
            if not any(
                part in excluded_directories
                for part in path.relative_to(self._bookmarks_path).parts
            )
        )

        if not markdown_files:
            raise ValueError(
                "No Markdown files were found in the bookmarks repository."
            )

        sections: list[str] = []
        total_size = 0

        for path in markdown_files:
            relative_path = path.relative_to(self._bookmarks_path)
            content = path.read_text(encoding="utf-8")

            section = f"\n## {relative_path}\n{content}"
            remaining = self._MAX_TAXONOMY_SIZE - total_size

            if remaining <= 0:
                break

            sections.append(section[:remaining])
            total_size += min(len(section), remaining)

        return "\n".join(sections)

    @staticmethod
    def _required_string(
        parameters: dict[str, Any],
        key: str,
    ) -> str | None:
        value = parameters.get(key)

        if not isinstance(value, str):
            return None

        value = value.strip()
        return value or None

    @classmethod
    def _optional_string(
        cls,
        parameters: dict[str, Any],
        key: str,
    ) -> str | None:
        return cls._required_string(parameters, key)

    @staticmethod
    def _needs_input(field: str) -> BookmarkAgentOutput:
        return BookmarkAgentOutput(
            status="needs_input",
            message=f"The following input is required: {field}.",
            required_input=field,
        )
