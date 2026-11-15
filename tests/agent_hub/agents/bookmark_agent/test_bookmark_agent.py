from pathlib import Path
from typing import Any
from unittest.mock import AsyncMock

import pytest
from pydantic import ValidationError

from agent_hub.agents.bookmark_agent.agent import (
    BookmarkAgent,
    BookmarkAgentOutput,
    BookmarkAgentRequest,
    _PageParser,
)
from agent_hub.core import InterpretationResult, Interpreter


@pytest.fixture
def interpreter() -> AsyncMock:
    return AsyncMock(spec=Interpreter)


@pytest.fixture
def bookmarks_path(tmp_path: Path) -> Path:
    repository = tmp_path / "bookmarks"
    repository.mkdir()

    (repository / "README.md").write_text(
        "# Bookmarks\n\n"
        "## Categories\n\n"
        "- technology\n"
        "  - artificial-intelligence\n"
        "- github\n",
        encoding="utf-8",
    )

    return repository


@pytest.fixture
def agent(
    interpreter: AsyncMock,
    bookmarks_path: Path,
) -> BookmarkAgent:
    return BookmarkAgent(
        interpreter=interpreter,
        bookmarks_path=bookmarks_path,
    )


def make_interpretation_result(
    skill_name: str,
    parameters: dict[str, Any] | None = None,
    missing_inputs: list[str] | None = None,
) -> InterpretationResult:
    return InterpretationResult(
        skill_name=skill_name,
        parameters=parameters or {},
        missing_inputs=missing_inputs or [],
    )


def configure_interpreter(
    interpreter: AsyncMock,
    responses: dict[str, dict[str, Any]],
) -> None:
    async def interpret(request: Any) -> InterpretationResult:
        skill_name = request.skills[0].name

        return make_interpretation_result(
            skill_name=skill_name,
            parameters=responses.get(skill_name, {}),
        )

    interpreter.interpret.side_effect = interpret


class TestBookmarkAgent:

    @pytest.mark.asyncio
    async def test_create_bookmark(
        self,
        agent: BookmarkAgent,
        interpreter: AsyncMock,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        configure_interpreter(
            interpreter,
            {
                "bookmark-extract": {
                    "title": "Example Page",
                    "content": (
                        "An example page about artificial intelligence."
                    ),
                },
                "bookmark-describe": {
                    "description_pt_br": (
                        "Uma página sobre inteligência artificial."
                    ),
                },
                "text-translate": {
                    "translated_text": (
                        "A page about artificial intelligence."
                    ),
                },
                "bookmark-classify": {
                    "category": "technology",
                    "subcategory": "artificial-intelligence",
                    "reasoning": (
                        "The content discusses artificial intelligence."
                    ),
                },
            },
        )

        async def extract_page(url: str) -> BookmarkAgentOutput:
            return BookmarkAgentOutput(
                status="completed",
                message="Example description",
                url=url,
                title="Example Page",
                content=(
                    "An example page about artificial intelligence."
                ),
            )

        monkeypatch.setattr(agent, "_extract_page", extract_page)

        result = await agent.run(
            BookmarkAgentRequest(
                url="https://example.com",
                operation="create",
            )
        )

        assert result.status == "completed"
        assert result.url == "https://example.com"
        assert result.title == "Example Page"
        assert result.category == "technology"
        assert result.subcategory == "artificial-intelligence"
        assert result.description_pt_br is not None
        assert result.description_en is not None

        assert interpreter.interpret.await_count == 4

    @pytest.mark.asyncio
    async def test_extract_bookmark(
        self,
        agent: BookmarkAgent,
        interpreter: AsyncMock,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        configure_interpreter(
            interpreter,
            {
                "bookmark-extract": {
                    "title": "Example Page",
                    "content": "Extracted page content.",
                },
            },
        )

        async def extract_page(url: str) -> BookmarkAgentOutput:
            return BookmarkAgentOutput(
                status="completed",
                message="Page description",
                url=url,
                title="Example Page",
                content="Page content.",
            )

        monkeypatch.setattr(agent, "_extract_page", extract_page)

        result = await agent.run(
            BookmarkAgentRequest(
                url="https://example.com",
                operation="extract",
            )
        )

        assert result.status == "completed"
        assert result.title == "Example Page"
        assert result.content == "Extracted page content."
        assert interpreter.interpret.await_count == 1

    @pytest.mark.asyncio
    async def test_describe_bookmark(
        self,
        agent: BookmarkAgent,
        interpreter: AsyncMock,
    ) -> None:
        configure_interpreter(
            interpreter,
            {
                "bookmark-describe": {
                    "description_pt_br": "Descrição em português.",
                },
                "text-translate": {
                    "translated_text": "Description in English.",
                },
            },
        )

        result = await agent.run(
            BookmarkAgentRequest(
                operation="describe",
                title="Example",
                content="Example content.",
            )
        )

        assert result.status == "completed"
        assert result.description_pt_br == "Descrição em português."
        assert result.description_en == "Description in English."
        assert interpreter.interpret.await_count == 2

    @pytest.mark.asyncio
    async def test_classify_bookmark(
        self,
        agent: BookmarkAgent,
        interpreter: AsyncMock,
    ) -> None:
        configure_interpreter(
            interpreter,
            {
                "bookmark-classify": {
                    "category": "technology",
                    "subcategory": "artificial-intelligence",
                    "reasoning": "Classification reasoning.",
                },
            },
        )

        result = await agent.run(
            BookmarkAgentRequest(
                operation="classify",
                title="Example",
                content="Example content.",
            )
        )

        assert result.status == "completed"
        assert result.category == "technology"
        assert result.subcategory == "artificial-intelligence"
        assert result.reasoning == "Classification reasoning."
        assert interpreter.interpret.await_count == 1

    @pytest.mark.asyncio
    async def test_missing_interpreter(
        self,
        bookmarks_path: Path,
    ) -> None:
        agent = BookmarkAgent(bookmarks_path=bookmarks_path)

        result = await agent.run(
            BookmarkAgentRequest(
                operation="describe",
                content="Example content.",
            )
        )

        assert result.status == "needs_input"
        assert result.required_input == "interpreter"

    @pytest.mark.asyncio
    async def test_missing_url(
        self,
        agent: BookmarkAgent,
    ) -> None:
        result = await agent.run(
            BookmarkAgentRequest(operation="create")
        )

        assert result.status == "needs_input"
        assert result.required_input == "url"

    @pytest.mark.asyncio
    async def test_missing_content_for_describe(
        self,
        agent: BookmarkAgent,
    ) -> None:
        result = await agent.run(
            BookmarkAgentRequest(operation="describe")
        )

        assert result.status == "needs_input"
        assert result.required_input == "content"

    @pytest.mark.asyncio
    async def test_missing_content_for_classify(
        self,
        agent: BookmarkAgent,
    ) -> None:
        result = await agent.run(
            BookmarkAgentRequest(operation="classify")
        )

        assert result.status == "needs_input"
        assert result.required_input == "content"

    @pytest.mark.asyncio
    async def test_missing_bookmarks_path(
        self,
        interpreter: AsyncMock,
    ) -> None:
        agent = BookmarkAgent(interpreter=interpreter)

        configure_interpreter(
            interpreter,
            {
                "bookmark-classify": {
                    "category": "technology",
                },
            },
        )

        result = await agent.run(
            BookmarkAgentRequest(
                operation="classify",
                content="Example content.",
            )
        )

        assert result.status == "needs_input"
        assert result.required_input == "bookmarks_path"
        assert interpreter.interpret.await_count == 0

    @pytest.mark.asyncio
    async def test_missing_description_parameters(
        self,
        agent: BookmarkAgent,
        interpreter: AsyncMock,
    ) -> None:
        configure_interpreter(
            interpreter,
            {
                "bookmark-describe": {
                    "description_pt_br": "Descrição em português.",
                },
            },
        )

        result = await agent.run(
            BookmarkAgentRequest(
                operation="describe",
                content="Example content.",
            )
        )

        assert result.status == "failed"
        assert "incomplete" in result.message.lower()

    @pytest.mark.asyncio
    async def test_missing_category_parameter(
        self,
        agent: BookmarkAgent,
        interpreter: AsyncMock,
    ) -> None:
        configure_interpreter(
            interpreter,
            {
                "bookmark-classify": {
                    "subcategory": "artificial-intelligence",
                },
            },
        )

        result = await agent.run(
            BookmarkAgentRequest(
                operation="classify",
                content="Example content.",
            )
        )

        assert result.status == "failed"
        assert "category" in result.message.lower()

    @pytest.mark.asyncio
    async def test_interpreter_missing_inputs(
        self,
        agent: BookmarkAgent,
        interpreter: AsyncMock,
    ) -> None:
        async def interpret(request: Any) -> InterpretationResult:
            return InterpretationResult(
                skill_name=request.skills[0].name,
                missing_inputs=["page content"],
            )

        interpreter.interpret.side_effect = interpret

        result = await agent.run(
            BookmarkAgentRequest(
                operation="describe",
                content="Example content.",
            )
        )

        assert result.status == "needs_input"
        assert result.required_input == "page content"

    @pytest.mark.asyncio
    async def test_interpreter_returns_wrong_skill(
        self,
        agent: BookmarkAgent,
        interpreter: AsyncMock,
    ) -> None:
        interpreter.interpret.return_value = InterpretationResult(
            skill_name="another-skill",
            parameters={},
        )

        result = await agent.run(
            BookmarkAgentRequest(
                operation="describe",
                content="Example content.",
            )
        )

        assert result.status == "unsupported"

    @pytest.mark.asyncio
    async def test_missing_skill(
        self,
        agent: BookmarkAgent,
    ) -> None:
        agent._skills.pop("bookmark-describe")

        result = await agent.run(
            BookmarkAgentRequest(
                operation="describe",
                content="Example content.",
            )
        )

        assert result.status == "failed"
        assert "not found" in result.message.lower()

    @pytest.mark.asyncio
    async def test_page_extraction_failure(
        self,
        agent: BookmarkAgent,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        async def extract_page(url: str) -> BookmarkAgentOutput:
            return BookmarkAgentOutput(
                status="failed",
                message="Unable to access page.",
            )

        monkeypatch.setattr(agent, "_extract_page", extract_page)

        result = await agent.run(
            BookmarkAgentRequest(
                url="https://example.com",
                operation="create",
            )
        )

        assert result.status == "failed"
        assert result.url == "https://example.com"

    def test_invalid_url(self) -> None:
        with pytest.raises(ValidationError):
            BookmarkAgentRequest(
                url="file:///etc/passwd",
                operation="extract",
            )

    def test_read_taxonomy(
        self,
        agent: BookmarkAgent,
    ) -> None:
        taxonomy = agent._read_taxonomy()

        assert "technology" in taxonomy
        assert "artificial-intelligence" in taxonomy
        assert "README.md" in taxonomy

    def test_taxonomy_excludes_ignored_directories(
        self,
        agent: BookmarkAgent,
        bookmarks_path: Path,
    ) -> None:
        excluded = bookmarks_path / ".venv"
        excluded.mkdir()

        (excluded / "ignored.md").write_text(
            "# Should not be included",
            encoding="utf-8",
        )

        taxonomy = agent._read_taxonomy()

        assert "README.md" in taxonomy
        assert "ignored.md" not in taxonomy

    def test_taxonomy_repository_not_found(
        self,
        interpreter: AsyncMock,
        tmp_path: Path,
    ) -> None:
        agent = BookmarkAgent(
            interpreter=interpreter,
            bookmarks_path=tmp_path / "does-not-exist",
        )

        with pytest.raises(ValueError, match="not found"):
            agent._read_taxonomy()


class TestPageParser:

    def test_extract_title(self) -> None:
        parser = _PageParser()
        parser.feed(
            "<html><head><title>Example Page</title></head></html>"
        )

        assert parser.title == "Example Page"

    def test_extract_meta_description(self) -> None:
        parser = _PageParser()
        parser.feed(
            '<html><head>'
            '<meta name="description" content="Page description.">'
            "</head></html>"
        )

        assert parser.description == "Page description."

    def test_extract_open_graph_description(self) -> None:
        parser = _PageParser()
        parser.feed(
            '<meta property="og:description" '
            'content="Open Graph description.">'
        )

        assert parser.description == "Open Graph description."

    def test_extract_visible_content(self) -> None:
        parser = _PageParser()
        parser.feed(
            "<html><body>"
            "<main><p>Visible content.</p></main>"
            "<script>Hidden script.</script>"
            "<style>Hidden style.</style>"
            "</body></html>"
        )

        assert "Visible content." in parser.content
        assert "Hidden script." not in parser.content
        assert "Hidden style." not in parser.content

    def test_extract_title_and_content(self) -> None:
        parser = _PageParser()
        parser.feed(
            "<html><head><title>Example</title></head>"
            "<body><p>Page content.</p></body></html>"
        )

        assert parser.title == "Example"
        assert "Page content." in parser.content