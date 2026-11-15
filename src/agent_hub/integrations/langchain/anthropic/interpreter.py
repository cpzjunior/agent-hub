
from typing import Any, cast

from langchain_anthropic import ChatAnthropic
from langchain_core.prompts import ChatPromptTemplate

from agent_hub.core.interpreter import (
    InterpretationRequest,
    InterpretationResult,
    Interpreter,
)

from .settings import AnthropicSettings


class AnthropicInterpreter(Interpreter):
    def __init__(
        self,
        settings: AnthropicSettings | None = None,
        *,
        chain: Any | None = None,
    ) -> None:
        self._settings = settings or AnthropicSettings()

        if chain is not None:
            self._chain = chain
            return

        if self._settings.api_key is None:
            raise ValueError(
                "Anthropic API key is required when no chain is provided."
            )

        model_config: dict[str, Any] = {
            "model_name": self._settings.model,
            "api_key": self._settings.api_key,
            "temperature": self._settings.temperature,
            "timeout": None,
            "stop": None,
        }

        model = ChatAnthropic(**model_config)

        self._chain = self._build_prompt() | model.with_structured_output(
            InterpretationResult,
            method="json_schema",
        )

    @staticmethod
    def _build_prompt() -> ChatPromptTemplate:
        return ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    """
You are an interpreter for an AI agent.

Your task is to translate the user's natural language instruction
into a structured interpretation.

Available skills:
{skills}

Rules:
- Select only a skill that exists in the available skills.
- Extract the parameters required by the selected skill.
- Never invent missing information.
- If required information is missing, report it in missing_inputs.
- If no skill matches the instruction, return a null skill_name.
- Provide a concise message explaining the interpretation or what
  information is missing.
""",
                ),
                ("human", "{instruction}"),
            ]
        )

    async def interpret(
        self,
        request: InterpretationRequest,
    ) -> InterpretationResult:
        skills_description = "\n\n".join(
            f"Name: {skill.name}\nDescription: {skill.description}"
            for skill in request.skills
        )

        result = await self._chain.ainvoke(
            {
                "instruction": request.instruction,
                "skills": skills_description or "No skills available.",
            }
        )

        return cast(InterpretationResult, result)
